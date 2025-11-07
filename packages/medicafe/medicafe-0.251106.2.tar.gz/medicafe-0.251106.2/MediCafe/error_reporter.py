import base64
import json
import os
import platform
import sys
import time
import zipfile

import requests
import traceback

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from MediCafe.MediLink_ConfigLoader import load_configuration, log as mc_log
from MediLink.MediLink_Gmail import get_access_token


def _safe_ascii(text):
	try:
		if text is None:
			return ''
		if isinstance(text, bytes):
			try:
				text = text.decode('ascii', 'ignore')
			except Exception:
				text = text.decode('utf-8', 'ignore')
		else:
			text = str(text)
		return text.encode('ascii', 'ignore').decode('ascii', 'ignore')
	except Exception:
		return ''


def _tail_file(path, max_lines):
	lines = []
	try:
		with open(path, 'r') as f:
			for line in f:
				lines.append(line)
				if len(lines) > max_lines:
					lines.pop(0)
		return ''.join(lines)
	except Exception:
		return ''


def _get_latest_log_path(local_storage_path):
	try:
		files = []
		for name in os.listdir(local_storage_path or '.'):
			if name.startswith('Log_') and name.endswith('.log'):
				files.append(os.path.join(local_storage_path, name))
		if not files:
			return None
		files.sort(key=lambda p: os.path.getmtime(p))
		return files[-1]
	except Exception:
		return None


def _redact(text):
    # Best-effort ASCII redaction: mask common secrets in logs and JSON
    try:
        text = _safe_ascii(text)
        import re
        patterns = [
            # SSN-like
            (r'\b(\d{3}-?\d{2}-?\d{4})\b', '***-**-****'),
            # 9-11 digit numeric IDs
            (r'\b(\d{9,11})\b', '*********'),
            # Authorization headers
            (r'Authorization:\s*Bearer\s+[A-Za-z0-9\-._~+/]+=*', 'Authorization: Bearer ***'),
            (r'Authorization:\s*[^\n\r]+', 'Authorization: ***'),
            # JSON token fields
            (r'("access_token"\s*:\s*")([^"]+)(")', r'\1***\3'),
            (r'("refresh_token"\s*:\s*")([^"]+)(")', r'\1***\3'),
            (r'("id_token"\s*:\s*")([^"]+)(")', r'\1***\3'),
            (r'("X-Auth-Token"\s*:\s*")([^"]+)(")', r'\1***\3'),
            # URL query params: token=..., access_token=..., auth=...
            (r'(token|access_token|auth|authorization)=([^&\s]+)', r'\1=***'),
            # Bearer fragments in JSON or text
            (r'Bearer\s+[A-Za-z0-9\-._~+/]+=*', 'Bearer ***'),
        ]
        for pat, rep in patterns:
            text = re.sub(pat, rep, text)
        return text
    except Exception:
        return text


def _ensure_dir(path):
	try:
		if not os.path.exists(path):
			os.makedirs(path)
		return True
	except Exception:
		return False


# Resolve a writable queue directory with fallback to ./reports_queue
def _resolve_queue_dir(medi_config):
    try:
        local_storage_path = medi_config.get('local_storage_path', '.') if isinstance(medi_config, dict) else '.'
    except Exception:
        local_storage_path = '.'
    primary = os.path.join(local_storage_path, 'reports_queue')
    if _ensure_dir(primary):
        return primary
    fallback = os.path.join('.', 'reports_queue')
    if _ensure_dir(fallback):
        try:
            mc_log("Queue directory fallback to ./reports_queue due to path/permission issue.", level="WARNING")
            print("Falling back to ./reports_queue for support bundles (check local_storage_path permissions).")
        except Exception:
            pass
        return fallback
    return primary


def _build_support_zip(zip_path, local_storage_path, max_log_lines, traceback_text, include_winscp, meta):
    latest_log = _get_latest_log_path(local_storage_path)
    log_tail = _tail_file(latest_log, max_log_lines) if latest_log else ''
    log_tail = _redact(log_tail)

    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
            z.writestr('meta.json', json.dumps(meta, ensure_ascii=True, indent=2))
            if latest_log and log_tail:
                z.writestr('log_tail.txt', log_tail)
            if traceback_text:
                z.writestr('traceback.txt', _redact(traceback_text))
            if include_winscp:
                upload_log = os.path.join(local_storage_path, 'winscp_upload.log')
                download_log = os.path.join(local_storage_path, 'winscp_download.log')
                winscp_logs = [(p, os.path.getmtime(p)) for p in [upload_log, download_log] if os.path.exists(p)]
                if winscp_logs:
                    latest_winscp = max(winscp_logs, key=lambda x: x[1])[0]
                    winscp_tail = _tail_file(latest_winscp, max_log_lines) if latest_winscp else ''
                    winscp_tail = _redact(winscp_tail)
                    if winscp_tail:
                        z.writestr('winscp_log_tail.txt', winscp_tail)
        return True
    except Exception as e:
        mc_log('Error creating support bundle at {}: {}'.format(zip_path, e), level='ERROR')
        return False

# Centralized self-healing helpers for email reporting
def _attempt_gmail_reauth_interactive(max_wait_seconds=120):
    """
    Delegate to MediLink.MediLink_Gmail.ensure_authenticated_for_gmail_send to
    reuse existing OAuth/server logic without duplicating implementations.
    """
    try:
        from MediLink.MediLink_Gmail import ensure_authenticated_for_gmail_send
        return bool(ensure_authenticated_for_gmail_send(max_wait_seconds=max_wait_seconds))
    except Exception as e:
        try:
            mc_log("Failed to initiate Gmail re-authorization: {0}".format(e), level="ERROR")
        except Exception:
            pass
        return False

# _compute_report_id removed (unused)


def collect_support_bundle(include_traceback=True, max_log_lines=500):
    config, _ = load_configuration()
    medi = config.get('MediLink_Config', {})
    local_storage_path = medi.get('local_storage_path', '.')
    queue_dir = _resolve_queue_dir(medi)

    stamp = time.strftime('%Y%m%d_%H%M%S')
    zip_path = os.path.join(queue_dir, 'support_report_{}.zip'.format(stamp))

    traceback_txt = ''
    if include_traceback:
        try:
            trace_path = os.path.join(local_storage_path, 'traceback.txt')
            if os.path.exists(trace_path):
                with open(trace_path, 'r') as tf:
                    traceback_txt = tf.read()
        except Exception:
            traceback_txt = ''

    meta = {
        'app_version': _safe_ascii(_get_version()),
        'python_version': _safe_ascii(sys.version.split(' ')[0]),
        'platform': _safe_ascii(platform.platform()),
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'error_summary': _safe_ascii(_first_line(traceback_txt)),
        'traceback_present': bool(traceback_txt),
        'config_flags': {
            'console_logging': bool(medi.get('logging', {}).get('console_output', False)),
            'test_mode': bool(medi.get('TestMode', False))
        }
    }

    ok = _build_support_zip(zip_path, local_storage_path, max_log_lines, traceback_txt, True, meta)
    return zip_path if ok else None


def collect_test_support_bundle(max_log_lines=500):
    """
    Build a support bundle using the latest available logs and a placeholder
    (fake) traceback to exercise the reporting pipeline without exposing
    real exception data.

    Returns absolute path to the created ZIP, or None on failure.
    """
    try:
        config, _ = load_configuration()
        medi = config.get('MediLink_Config', {})
        local_storage_path = medi.get('local_storage_path', '.')
        queue_dir = _resolve_queue_dir(medi)

        stamp = time.strftime('%Y%m%d_%H%M%S')
        zip_path = os.path.join(queue_dir, 'support_report_TEST_{}.zip'.format(stamp))

        # Build a placeholder traceback - ASCII-only, no real data
        fake_tb = (
            "Traceback (most recent call last):\n"
            "  File \"MediCafe/test_runner.py\", line 42, in <module>\n"
            "  File \"MediCafe/error_reporter.py\", line 123, in simulate_error\n"
            "Exception: This is a TEST placeholder traceback for pipeline verification only.\n"
            "-- No real patient or PHI data is included. --\n"
        )
        meta = {
            'app_version': _safe_ascii(_get_version()),
            'python_version': _safe_ascii(sys.version.split(' ')[0]),
            'platform': _safe_ascii(platform.platform()),
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'error_summary': 'TEST: Placeholder traceback',
            'traceback_present': True,
            'config_flags': {
                'console_logging': bool(medi.get('logging', {}).get('console_output', False)),
                'test_mode': True
            }
        }
        ok = _build_support_zip(zip_path, local_storage_path, max_log_lines, fake_tb, True, meta)
        return zip_path if ok else None
    except Exception as e:
        try:
            mc_log('Error creating TEST support bundle: {}'.format(e), level='ERROR')
        except Exception:
            pass
        return None


def _first_line(text):
	try:
		for line in (text or '').splitlines():
			line = line.strip()
			if line:
				return line[:200]
		return ''
	except Exception:
		return ''


def _get_version():
	try:
		from MediCafe import __version__
		return __version__
	except Exception:
		return 'unknown'


def capture_unhandled_traceback(exc_type, exc_value, exc_traceback):
	try:
		config, _ = load_configuration()
		medi = config.get('MediLink_Config', {})
		local_storage_path = medi.get('local_storage_path', '.')
		trace_path = os.path.join(local_storage_path, 'traceback.txt')
		text = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
		text = _redact(text)
		with open(trace_path, 'w') as f:
			f.write(text)
		print("An error occurred. A traceback was saved to {}".format(trace_path))
	except Exception:
		try:
			mc_log('Failed to capture traceback to file', level='WARNING')
		except Exception:
			pass

def submit_support_bundle_email(zip_path=None, include_traceback=True):
    if not zip_path:
        zip_path = collect_support_bundle(include_traceback)
        if not zip_path:
            mc_log("Failed to create bundle.", level="ERROR")
            try:
                print("Failed to create support bundle. Ensure 'MediLink_Config.local_storage_path' is writable and logs exist.")
            except Exception:
                pass
            return False
    bundle_size = os.path.getsize(zip_path)
    config, _ = load_configuration()
    email_config = config.get('MediLink_Config', {}).get('error_reporting', {}).get('email', {})
    # Determine max size from config with default 1.5MB
    try:
        max_bytes = int(email_config.get('max_bundle_bytes', 1572864))
    except Exception:
        max_bytes = 1572864
    if bundle_size > max_bytes:
        mc_log("Bundle too large ({} bytes > {} bytes) - leaving in queue.".format(bundle_size, max_bytes), level="WARNING")
        try:
            print("Bundle too large to email ({} KB > {} KB). Left in 'reports_queue'. Path: {}".format(int(bundle_size/1024), int(max_bytes/1024), zip_path))
            print("Attempting to create and send a smaller LITE bundle (reduced logs, no traceback).")
        except Exception:
            pass
        # Attempt a smaller bundle automatically
        lite_zip = collect_support_bundle_lite(max_log_lines=200)
        if lite_zip and os.path.exists(lite_zip):
            try:
                lite_size = os.path.getsize(lite_zip)
            except Exception:
                lite_size = -1
            if 0 < lite_size <= max_bytes:
                return submit_support_bundle_email(zip_path=lite_zip, include_traceback=False)
            else:
                try:
                    print("LITE bundle is still too large ({} KB).".format(int(max(lite_size, 0)/1024)))
                except Exception:
                    pass
        try:
            print("Tip: Reduce log size or increase 'MediLink_Config.error_reporting.email.max_bundle_bytes'.")
        except Exception:
            pass
        return False
    # Feature is always available; proceed if recipients and token are available
    # Normalize and validate recipients
    to_emails = _normalize_recipients(email_config.get('to', []))
    if not to_emails:
        mc_log("No valid recipients configured in error_reporting.email.to", level="ERROR")
        try:
            print("No recipients configured. Set 'MediLink_Config.error_reporting.email.to' to one or more email addresses.")
        except Exception:
            pass
        return False
    subject_prefix = email_config.get('subject_prefix', 'MediCafe Error Report')
    access_token = get_access_token()
    if not access_token:
        mc_log("No access token - attempting Gmail re-authorization.", level="ERROR")
        try:
            print("No Gmail token found. Starting re-authorization...")
        except Exception:
            pass
        if _attempt_gmail_reauth_interactive():
            access_token = get_access_token()
        if not access_token:
            try:
                print("Authentication incomplete. Please finish Gmail consent, then retry.")
            except Exception:
                pass
            return False
    mc_log("Building email...", level="INFO")
    msg = MIMEMultipart()
    msg['To'] = ', '.join(to_emails)
    msg['Subject'] = '{} - {}'.format(subject_prefix, time.strftime('%Y%m%d_%H%M%S'))
    with open(zip_path, 'rb') as f:
        attach = MIMEApplication(f.read(), _subtype='zip')
        attach.add_header('Content-Disposition', 'attachment', filename=os.path.basename(zip_path))
        msg.attach(attach)
    body = "Error report attached."
    msg.attach(MIMEText(body, 'plain'))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    mc_log("Sending report...", level="INFO")
    headers = {'Authorization': 'Bearer {}'.format(access_token), 'Content-Type': 'application/json'}
    data = {'raw': raw}
    try:
        resp = requests.post('https://gmail.googleapis.com/gmail/v1/users/me/messages/send', headers=headers, json=data)
    except Exception as e:
        mc_log("Network error during Gmail send: {0}".format(e), level="ERROR")
        try:
            print("Network error while sending report: {0}".format(e))
            print("Check internet connectivity or proxy settings and retry.")
        except Exception:
            pass
        return False
    if resp.status_code == 200:
        mc_log("Report sent successfully!", level="INFO")
        try:
            os.remove(zip_path)
        except Exception:
            pass
        return True
    else:
        # Handle auth errors by prompting re-consent using existing OAuth helpers, then retry once
        if resp.status_code in (401, 403):
            mc_log("Gmail send unauthorized ({}). Attempting re-authorization and retry.".format(resp.status_code), level="WARNING")
            try:
                print("Gmail permission issue detected ({}). Starting re-authorization...".format(resp.status_code))
            except Exception:
                pass
            if _attempt_gmail_reauth_interactive():
                new_token = get_access_token()
                if new_token:
                    headers['Authorization'] = 'Bearer {}'.format(new_token)
                    try:
                        resp = requests.post('https://gmail.googleapis.com/gmail/v1/users/me/messages/send', headers=headers, json=data)
                    except Exception as e:
                        mc_log("Network error on retry: {0}".format(e), level="ERROR")
                        try:
                            print("Network error on retry: {0}".format(e))
                        except Exception:
                            pass
                        return False
                    if resp.status_code == 200:
                        mc_log("Report sent successfully after re-authorization!", level="INFO")
                        try:
                            os.remove(zip_path)
                        except Exception:
                            pass
                        return True
        # Map common Gmail errors to actionable hints
        hint = ''
        try:
            body = resp.json()
            err = body.get('error', {}) if isinstance(body, dict) else {}
            status = (err.get('status') or '').upper()
            message = err.get('message') or ''
            reasons = ','.join([e.get('reason') for e in err.get('errors', []) if isinstance(e, dict) and e.get('reason')])
            if 'RATELIMIT' in status or 'rateLimitExceeded' in reasons:
                hint = 'Quota exceeded. Wait and retry later.'
            elif 'DAILY' in status or 'dailyLimitExceeded' in reasons:
                hint = 'Daily quota exceeded. Try again tomorrow.'
            elif status in ('PERMISSION_DENIED', 'FORBIDDEN'):
                hint = 'Permissions insufficient. Re-authorize Gmail with required scopes.'
            elif status == 'INVALID_ARGUMENT':
                hint = 'Invalid request. Check recipient emails and attachment size.'
            elif status == 'UNAUTHENTICATED':
                hint = 'Authentication required. Re-authorize and retry.'
        except Exception:
            pass
        mc_log("Failed to send: {} - {}".format(resp.status_code, _redact(resp.text)), level="ERROR")
        try:
            base_msg = "Failed to send report: HTTP {}.".format(resp.status_code)
            if hint:
                base_msg += " Hint: {}".format(hint)
            print(base_msg)
            print("The bundle remains in 'reports_queue'. See latest log for details.")
        except Exception:
            pass
        # Preserve bundle in queue for manual retry
        return False


def _normalize_recipients(to_field):
    try:
        # Flatten to a list of strings
        if isinstance(to_field, str):
            separators_normalized = to_field.replace(';', ',').replace('\n', ',').replace('\r', ',')
            candidates = [p.strip() for p in separators_normalized.split(',')]
        elif isinstance(to_field, list):
            candidates = [str(p).strip() for p in to_field]
        else:
            candidates = []
        # Basic email regex: local@domain.tld
        import re
        email_re = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
        valid = []
        for addr in candidates:
            if not addr:
                continue
            if email_re.match(addr):
                valid.append(addr)
            else:
                try:
                    mc_log("Invalid email recipient skipped: {}".format(addr), level="WARNING")
                except Exception:
                    pass
        return valid
    except Exception:
        return []


def collect_support_bundle_lite(max_log_lines=200):
    """Create a smaller 'lite' support bundle with reduced logs and no traceback/winscp logs."""
    try:
        config, _ = load_configuration()
        medi = config.get('MediLink_Config', {})
        local_storage_path = medi.get('local_storage_path', '.')
        queue_dir = _resolve_queue_dir(medi)
        stamp = time.strftime('%Y%m%d_%H%M%S')
        zip_path = os.path.join(queue_dir, 'support_report_LITE_{}.zip'.format(stamp))
        meta = {
            'app_version': _safe_ascii(_get_version()),
            'python_version': _safe_ascii(sys.version.split(' ')[0]),
            'platform': _safe_ascii(platform.platform()),
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'error_summary': 'LITE: No traceback included',
            'traceback_present': False,
            'config_flags': {
                'console_logging': bool(medi.get('logging', {}).get('console_output', False)),
                'test_mode': bool(medi.get('TestMode', False))
            }
        }
        ok = _build_support_zip(zip_path, local_storage_path, max_log_lines, None, False, meta)
        return zip_path if ok else None
    except Exception:
        return None


def list_queued_bundles():
    try:
        config, _ = load_configuration()
        medi = config.get('MediLink_Config', {})
        local_storage_path = medi.get('local_storage_path', '.')
        primary = os.path.join(local_storage_path, 'reports_queue')
        fallback = os.path.join('.', 'reports_queue')
        files = []
        for q in (primary, fallback):
            try:
                if os.path.isdir(q):
                    files.extend([os.path.join(q, f) for f in os.listdir(q) if f.endswith('.zip')])
            except Exception:
                pass
        files = sorted(set(files))
        return files
    except Exception:
        return []


def submit_all_queued_bundles():
    sent = 0
    failed = 0
    try:
        queued = list_queued_bundles()
        for z in queued:
            try:
                ok = submit_support_bundle_email(zip_path=z, include_traceback=False)
                if ok:
                    sent += 1
                else:
                    failed += 1
            except Exception:
                failed += 1
    except Exception:
        pass
    return sent, failed


def delete_all_queued_bundles():
    deleted = 0
    try:
        for z in list_queued_bundles():
            try:
                os.remove(z)
                deleted += 1
            except Exception:
                pass
    except Exception:
        pass
    return deleted

def email_error_report_flow():
    try:
        sent = submit_support_bundle_email(zip_path=None, include_traceback=True)
        return 0 if sent else 1
    except Exception as e:
        mc_log("[ERROR] Exception during email report flow: {0}".format(e), level="ERROR")
        try:
            print("Unexpected error while sending error report: {0}".format(e))
        except Exception:
            pass
        return 1

def email_test_error_report_flow():
    """
    Create and send a TEST error report bundle, containing a placeholder
    traceback and latest log tails. Intended for troubleshooting the
    submission pipeline only.
    """
    try:
        zip_path = collect_test_support_bundle()
        if not zip_path:
            try:
                print("Failed to create TEST support bundle. Ensure 'MediLink_Config.local_storage_path' is writable.")
            except Exception:
                pass
            return 1
        sent = submit_support_bundle_email(zip_path=zip_path, include_traceback=False)
        if not sent:
            try:
                print("TEST error report was not sent. See messages above for the reason. The ZIP remains queued if creation succeeded.")
            except Exception:
                pass
        return 0 if sent else 1
    except Exception as e:
        try:
            mc_log("[ERROR] Exception during test email report flow: {0}".format(e), level="ERROR")
        except Exception:
            pass
        try:
            print("Unexpected error during TEST report flow: {0}".format(e))
        except Exception:
            pass
        return 1

if __name__ == "__main__":
    raise SystemExit(email_error_report_flow())

