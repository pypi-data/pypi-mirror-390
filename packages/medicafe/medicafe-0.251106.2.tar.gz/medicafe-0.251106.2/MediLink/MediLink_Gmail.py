# MediLink_Gmail.py
import sys, os, subprocess, time, webbrowser, requests, json, ssl, signal

# Set up Python path to find MediCafe when running directly
def setup_python_path():
    """Set up Python path to find MediCafe package"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.dirname(current_dir)
    
    # Add workspace root to Python path if not already present
    if workspace_root not in sys.path:
        sys.path.insert(0, workspace_root)

# Set up paths before importing MediCafe
setup_python_path()

from MediCafe.core_utils import get_shared_config_loader, extract_medilink_config

# New helpers
from MediLink.gmail_oauth_utils import (
    get_authorization_url as oauth_get_authorization_url,
    exchange_code_for_token as oauth_exchange_code_for_token,
    refresh_access_token as oauth_refresh_access_token,
    is_valid_authorization_code as oauth_is_valid_authorization_code,
    clear_token_cache as oauth_clear_token_cache,
    get_access_token_with_refresh,
)
from MediLink.gmail_http_utils import (
    generate_self_signed_cert as http_generate_self_signed_cert,
    start_https_server as http_start_https_server,
    inspect_token as http_inspect_token,
    SSLRequestHandler,
)

# Get shared config loader
MediLink_ConfigLoader = get_shared_config_loader()
if MediLink_ConfigLoader:
    load_configuration = MediLink_ConfigLoader.load_configuration
    log = MediLink_ConfigLoader.log
else:
    # Fallback functions if config loader is not available
    def load_configuration():
        return {}, {}
    def log(message, level="INFO"):
        print("[{}] {}".format(level, message))
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread, Event
import platform
import ctypes

# Default configuration values
DEFAULT_SERVER_PORT = 8000
DEFAULT_CERT_DAYS = 365

# Path to token.json file
TOKEN_PATH = 'token.json'

def resolve_credentials_path(os_name, os_version):
    """Get platform-appropriate credentials path"""
    if os_name == 'Windows' and 'XP' in os_version:
        return 'F:\\Medibot\\json\\credentials.json'
    else:
        return 'json\\credentials.json'


def resolve_openssl_cnf(base_dir):
    """Find openssl.cnf file, searching local dir then fallback path. Returns best-effort path."""
    # Try relative path first
    openssl_cnf = 'openssl.cnf'
    if os.path.exists(openssl_cnf):
        log("Found openssl.cnf at: {}".format(os.path.abspath(openssl_cnf)))
        return openssl_cnf

    # Try base directory
    medilink_openssl = os.path.join(base_dir, 'openssl.cnf')
    log("Trying MediLink directory: {}".format(medilink_openssl))
    if os.path.exists(medilink_openssl):
        log("Found openssl.cnf at: {}".format(medilink_openssl))
        return medilink_openssl

    # Try fallback path (one directory up)
    parent_dir = os.path.dirname(base_dir)
    alternative_path = os.path.join(parent_dir, 'MediBot', 'openssl.cnf')
    log("Trying alternative path: {}".format(alternative_path))
    if os.path.exists(alternative_path):
        log("Found openssl.cnf at: {}".format(alternative_path))
        return alternative_path

    # Return relative path as fallback (may not exist)
    log("Could not find openssl.cnf at alternative path either")
    return openssl_cnf


config, _ = load_configuration()
medi = extract_medilink_config(config)
local_storage_path = medi.get('local_storage_path', '.')
downloaded_emails_file = os.path.join(local_storage_path, 'downloaded_emails.txt')

server_port = medi.get('gmail_server_port', DEFAULT_SERVER_PORT)
cert_file = 'server.cert'
key_file = 'server.key'
# Find openssl.cnf file
medilink_dir = os.path.dirname(os.path.abspath(__file__))
openssl_cnf = resolve_openssl_cnf(medilink_dir)

httpd = None  # Global variable for the HTTP server
shutdown_event = Event()  # Event to signal shutdown

# Safe-to-close flag and lightweight server status tracking
SAFE_TO_CLOSE = False
SERVER_STATUS = {
    'phase': 'idle',  # idle|processing|downloading|cleanup_triggered|cleanup_confirmed|done|error
    'linksReceived': 0,
    'filesDownloaded': 0,
    'filesToDelete': 0,
    'filesDeleted': 0,
    'lastError': None,
}

def set_safe_to_close(value):
    global SAFE_TO_CLOSE
    SAFE_TO_CLOSE = bool(value)

def set_phase(phase):
    try:
        SERVER_STATUS['phase'] = str(phase or '')
    except Exception:
        SERVER_STATUS['phase'] = 'error'

def set_counts(links_received=None, files_downloaded=None, files_to_delete=None, files_deleted=None):
    try:
        if links_received is not None:
            SERVER_STATUS['linksReceived'] = int(links_received)
        if files_downloaded is not None:
            SERVER_STATUS['filesDownloaded'] = int(files_downloaded)
        if files_to_delete is not None:
            SERVER_STATUS['filesToDelete'] = int(files_to_delete)
        if files_deleted is not None:
            SERVER_STATUS['filesDeleted'] = int(files_deleted)
    except Exception:
        pass

def set_error(msg):
    try:
        SERVER_STATUS['lastError'] = str(msg or '')
    except Exception:
        SERVER_STATUS['lastError'] = 'Unknown error'

def get_safe_status():
    try:
        return {
            'safeToClose': bool(SAFE_TO_CLOSE),
            'phase': SERVER_STATUS.get('phase', 'idle'),
            'counts': {
                'linksReceived': SERVER_STATUS.get('linksReceived', 0),
                'filesDownloaded': SERVER_STATUS.get('filesDownloaded', 0),
                'filesToDelete': SERVER_STATUS.get('filesToDelete', 0),
                'filesDeleted': SERVER_STATUS.get('filesDeleted', 0),
            },
            'lastError': SERVER_STATUS.get('lastError'),
        }
    except Exception:
        return {'safeToClose': False, 'phase': 'error'}

# Define the scopes for the Gmail API and other required APIs
SCOPES = ' '.join([
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/script.external_request',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/script.scriptapp',
    'https://www.googleapis.com/auth/drive'
])

# Determine the operating system and version
os_name = platform.system()
os_version = platform.release()

# Set the credentials path based on the OS and version
CREDENTIALS_PATH = resolve_credentials_path(os_name, os_version)

# Log the selected path for verification
log("Using CREDENTIALS_PATH: {}".format(CREDENTIALS_PATH), level="DEBUG")

REDIRECT_URI = 'https://127.0.0.1:8000'

def get_authorization_url():
    return oauth_get_authorization_url(CREDENTIALS_PATH, REDIRECT_URI, SCOPES, log)

def exchange_code_for_token(auth_code, retries=3):
    return oauth_exchange_code_for_token(auth_code, CREDENTIALS_PATH, REDIRECT_URI, log, retries=retries)

def _mask_token_value(value):
    try:
        s = str(value or '')
        if len(s) <= 8:
            return '***'
        return s[:4] + '...' + s[-4:]
    except Exception:
        return '***'




def get_access_token():
    return get_access_token_with_refresh(TOKEN_PATH, CREDENTIALS_PATH, log)

def refresh_access_token(refresh_token):
    return oauth_refresh_access_token(refresh_token, CREDENTIALS_PATH, log)

def bring_window_to_foreground():
    """Brings the current window to the foreground on Windows."""
    try:
        if platform.system() == 'Windows':
            pid = os.getpid()
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            current_pid = ctypes.c_ulong()
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(current_pid))
            if current_pid.value != pid:
                ctypes.windll.user32.SetForegroundWindow(hwnd)
                if ctypes.windll.user32.GetForegroundWindow() != hwnd:
                    ctypes.windll.user32.ShowWindow(hwnd, 9)
                    ctypes.windll.user32.SetForegroundWindow(hwnd)
    except Exception as e:
        log("Error bringing window to foreground: {}".format(e))

class RequestHandler(SSLRequestHandler):
    def _set_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-type', 'application/json')

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_headers()
        self.end_headers()
        try:
            origin = self.headers.get('Origin')
        except Exception:
            origin = None
        try:
            print("[CORS] Preflight {0} from {1}".format(self.path, origin))
        except Exception:
            pass

    def do_POST(self):
        if self.path == '/download':
            set_phase('processing')
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            links = data.get('links', [])
            log("Received links: {}".format(links), level="DEBUG")
            try:
                print("[Handshake] Received {0} link(s) from webapp".format(len(links)))
            except Exception:
                pass
            try:
                set_counts(links_received=len(links))
            except Exception:
                pass
            file_ids = [link.get('fileId', None) for link in links if link.get('fileId')]
            log("File IDs received from client: {}".format(file_ids), level="DEBUG")
            set_phase('downloading')
            try:
                download_docx_files(links)
            except Exception as e:
                set_phase('error')
                set_error(e)
            # Only delete files that actually downloaded successfully
            downloaded_names = load_downloaded_emails()
            successful_ids = []
            try:
                name_to_id = { (link.get('filename') or ''): link.get('fileId') for link in links if link.get('fileId') }
                for name in downloaded_names:
                    fid = name_to_id.get(name)
                    if fid:
                        successful_ids.append(fid)
            except Exception as e:
                log("Error computing successful file IDs for cleanup: {}".format(e))
                successful_ids = file_ids  # Fallback: attempt all provided IDs
            try:
                set_counts(files_to_delete=len(successful_ids))
            except Exception:
                pass
            # Trigger cleanup in Apps Script with auth
            try:
                cleanup_ok = False
                if successful_ids:
                    ok = send_delete_request_to_gas(successful_ids)
                    if ok:
                        set_phase('cleanup_confirmed')
                        try:
                            set_counts(files_deleted=len(successful_ids))
                        except Exception:
                            pass
                        cleanup_ok = True
                    else:
                        set_phase('cleanup_triggered')
                        set_error('Cleanup request not confirmed')
                else:
                    log("No successful file IDs to delete after download.")
                    set_phase('done')
                    cleanup_ok = True  # nothing to delete -> safe
            except Exception as e:
                log("Cleanup trigger failed: {}".format(e))
                set_phase('error')
                set_error(e)
                cleanup_ok = False
            self.send_response(200)
            self._set_headers()
            self.end_headers()
            try:
                set_safe_to_close(bool(cleanup_ok))
            except Exception:
                pass
            response = json.dumps({"status": "success", "message": "All files downloaded", "fileIds": successful_ids, "safeToClose": bool(cleanup_ok)})
            self.wfile.write(response.encode('utf-8'))
            try:
                print("[Handshake] Completed. Returning success for {0} fileId(s)".format(len(successful_ids)))
            except Exception:
                pass
            shutdown_event.set()
            bring_window_to_foreground()
        elif self.path == '/shutdown':
            log("Shutdown request received.")
            self.send_response(200)
            self._set_headers()
            self.end_headers()
            response = json.dumps({"status": "success", "message": "Server is shutting down."})
            self.wfile.write(response.encode('utf-8'))
            shutdown_event.set()
        elif self.path == '/delete-files':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            file_ids = data.get('fileIds', [])
            log("File IDs to delete received from client: {}".format(file_ids))
            if not isinstance(file_ids, list):
                self.send_response(400)
                self._set_headers()
                self.end_headers()
                response = json.dumps({"status": "error", "message": "Invalid fileIds parameter."})
                self.wfile.write(response.encode('utf-8'))
                return
            self.send_response(200)
            self._set_headers()
            self.end_headers()
            response = json.dumps({"status": "success", "message": "Files deleted successfully."})
            self.wfile.write(response.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        log("Full request path: {}".format(self.path), level="DEBUG")
        if self.path == '/_health':
            try:
                print("[Health] Probe OK")
            except Exception:
                pass
            self.send_response(200)
            self._set_headers()
            self.end_headers()
            try:
                self.wfile.write(json.dumps({"status": "ok"}).encode('ascii'))
            except Exception:
                self.wfile.write(b'{"status":"ok"}')
            return
        elif self.path == '/status':
            self.send_response(200)
            self._set_headers()
            self.end_headers()
            try:
                payload = json.dumps(get_safe_status())
            except Exception:
                payload = '{}'
            try:
                self.wfile.write(payload.encode('ascii'))
            except Exception:
                try:
                    self.wfile.write(payload.encode('utf-8'))
                except Exception:
                    self.wfile.write(b'{}')
            return
        if self.path.startswith("/?code="):
            auth_code = self.path.split('=')[1].split('&')[0]
            auth_code = requests.utils.unquote(auth_code)
            log("Received authorization code: {}".format(auth_code), level="DEBUG")
            if oauth_is_valid_authorization_code(auth_code, log):
                try:
                    token_response = exchange_code_for_token(auth_code)
                    if 'access_token' not in token_response:
                        if token_response.get("status") == "error":
                            self.send_response(400)
                            self.send_header('Content-type', 'text/html')
                            self.end_headers()
                            self.wfile.write(token_response["message"].encode())
                            return
                        raise ValueError("Access token not found in response.")
                except Exception as e:
                    log("Error during token exchange: {}".format(e))
                    self.send_response(500)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write("An error occurred during authentication. Please try again.".encode())
                else:
                    log("Token response: {}".format(token_response), level="DEBUG")
                    if 'access_token' in token_response:
                        from MediLink.gmail_oauth_utils import save_token_file
                        if save_token_file(TOKEN_PATH, token_response, log):
                            # Success - continue with response
                            self.send_response(200)
                            self.send_header('Content-type', 'text/html')
                            self.end_headers()
                            self.wfile.write("Authentication successful. You can close this window now.".encode())

                        # Only launch webapp if not in Gmail send-only mode
                        global httpd
                        if httpd is not None and not getattr(httpd, 'gmail_send_only_mode', False):
                            initiate_link_retrieval(config)
                        else:
                            # For Gmail send-only: just signal completion
                            log("Gmail send-only authentication complete. Server will shutdown after token poll.")
                            shutdown_event.set()
                    else:
                        log("Authentication failed with response: {}".format(token_response))
                        if 'error' in token_response:
                            error_description = token_response.get('error_description', 'No description provided.')
                            log("Error details: {}".format(error_description))
                        if token_response.get('error') == 'invalid_grant':
                            log("Invalid grant error encountered. Authorization code: {}, Response: {}".format(auth_code, token_response), level="DEBUG")
                            check_invalid_grant_causes(auth_code)
                            oauth_clear_token_cache(TOKEN_PATH, log)
                            user_message = "Authentication failed: Invalid or expired authorization code. Please try again."
                        else:
                            user_message = "Authentication failed. Please check the logs for more details."
                        self.send_response(400)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        self.wfile.write(user_message.encode())
                        shutdown_event.set()
            else:
                log("Invalid authorization code format: {}".format(auth_code), level="DEBUG")
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write("Invalid authorization code format. Please try again.".encode())
                shutdown_event.set()
        elif self.path == '/downloaded-emails':
            self.send_response(200)
            self._set_headers()
            self.end_headers()
            downloaded_emails = load_downloaded_emails()
            response = json.dumps({"downloadedEmails": list(downloaded_emails)})
            self.wfile.write(response.encode('utf-8'))
        else:
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'HTTPS server is running.')

def generate_self_signed_cert(cert_file, key_file):
    cert_days = medi.get('gmail_cert_days', DEFAULT_CERT_DAYS)
    http_generate_self_signed_cert(openssl_cnf, cert_file, key_file, log, subprocess, cert_days)

def run_server():
    global httpd
    try:
        log("Attempting to start server on port " + str(server_port))
        if not os.path.exists(cert_file):
            log("Error: Certificate file not found: " + cert_file)
        if not os.path.exists(key_file):
            log("Error: Key file not found: " + key_file)
        httpd = HTTPServer(('0.0.0.0', server_port), RequestHandler)
        httpd.gmail_send_only_mode = False  # Default: allow full webapp flow
        httpd.socket = ssl.wrap_socket(httpd.socket, certfile=cert_file, keyfile=key_file, server_side=True)
        log("Starting HTTPS server on port {}".format(server_port))
        try:
            print("[Server] HTTPS server ready at https://127.0.0.1:{0}".format(server_port))
        except Exception:
            pass
        httpd.serve_forever()
    except Exception as e:
        log("Error in serving: {}".format(e))
        stop_server()

def stop_server():
    global httpd
    if httpd:
        log("Stopping HTTPS server.")
        httpd.shutdown()
        httpd.server_close()
        log("HTTPS server stopped.")
    shutdown_event.set()
    bring_window_to_foreground()

def load_downloaded_emails():
    downloaded_emails = set()
    if os.path.exists(downloaded_emails_file):
        with open(downloaded_emails_file, 'r') as file:
            downloaded_emails = set(line.strip() for line in file)
    log("Loaded downloaded emails: {}".format(downloaded_emails), level="DEBUG")
    return downloaded_emails

def download_docx_files(links):
    downloaded_emails = load_downloaded_emails()
    downloads_count = 0
    for link in links:
        try:
            url = link.get('url', '')
            filename = link.get('filename', '')
            log("Processing link: url='{}', filename='{}'".format(url, filename), level="DEBUG")
            lower_name = (filename or '').lower()
            looks_like_csv = any(lower_name.endswith(ext) for ext in ['.csv', '.tsv', '.txt', '.dat'])
            if looks_like_csv:
                log("[CSV Routing Preview] Detected CSV-like filename: {}. Would route to CSV processing directory.".format(filename))
            if filename in downloaded_emails:
                log("Skipping already downloaded email: {}".format(filename))
                continue
            log("Downloading .docx file from URL: {}".format(url), level="DEBUG")
            response = requests.get(url, verify=False)
            if response.status_code == 200:
                file_path = os.path.join(local_storage_path, filename)
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                log("Downloaded .docx file: {}".format(filename))
                downloaded_emails.add(filename)
                with open(downloaded_emails_file, 'a') as file:
                    file.write(filename + '\n')
                downloads_count += 1
                try:
                    set_counts(files_downloaded=downloads_count)
                except Exception:
                    pass
            else:
                log("Failed to download .docx file from URL: {}. Status code: {}".format(url, response.status_code))
        except Exception as e:
            log("Error downloading .docx file from URL: {}. Error: {}".format(url, e))

def open_browser_with_executable(url, browser_path=None):
    try:
        if browser_path:
            log("Attempting to open URL with provided executable: {} {}".format(browser_path, url), level="DEBUG")
            process = subprocess.Popen([browser_path, url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                log("Browser opened with provided executable path using subprocess.Popen.")
            else:
                log("Browser failed to open using subprocess.Popen. Return code: {}. Stderr: {}".format(process.returncode, stderr))
        else:
            log("No browser path provided. Attempting to open URL with default browser: {}".format(url), level="DEBUG")
            webbrowser.open(url)
            log("Default browser opened.", level="DEBUG")
    except Exception as e:
        log("Failed to open browser: {}".format(e))

def initiate_link_retrieval(config):
    log("Initiating browser via implicit GET.")
    medi = extract_medilink_config(config)
    dep_id = (medi.get('webapp_deployment_id', '') or '').strip()
    if not dep_id:
        log("webapp_deployment_id is empty. Please set it in config before continuing.")
        shutdown_event.set()
        return
    url_get = "https://script.google.com/macros/s/{}/exec?action=get_link".format(dep_id)
    try:
        log("Opening GAS web app: {}".format(url_get), level="DEBUG")
    except Exception:
        pass
    # Preflight probe to surface HTTP status/redirects before opening the browser
    try:
        probe_url = "https://script.google.com/macros/s/{}/exec".format(dep_id)
        try:
            resp = requests.get(probe_url, allow_redirects=False, timeout=8)
            loc = resp.headers.get('Location')
            log("Preflight probe: status={} location={}".format(resp.status_code, loc), level="DEBUG")
        except Exception as probe_err:
            log("Preflight probe failed: {}".format(probe_err))
    except Exception:
        pass
    open_browser_with_executable(url_get)
    log("Preparing POST call.", level="DEBUG")
    url = "https://script.google.com/macros/s/{}/exec".format(dep_id)
    downloaded_emails = list(load_downloaded_emails())
    payload = {"downloadedEmails": downloaded_emails}
    access_token = get_access_token()
    if not access_token:
        log("Access token not found. Please authenticate first.")
        shutdown_event.set()
        return
    token_info = http_inspect_token(access_token, log, delete_token_file_fn=delete_token_file, stop_server_fn=stop_server)
    if token_info is None:
        log("Access token is invalid. Please re-authenticate.")
        shutdown_event.set()
        return
    headers = {'Authorization': 'Bearer {}'.format(access_token), 'Content-Type': 'application/json'}
    log("Request headers: {}".format(headers), level="DEBUG")
    log("Request payload: {}".format(payload), level="DEBUG")
    handle_post_response(url, payload, headers)

def handle_post_response(url, payload, headers):
    try:
        response = requests.post(url, json=payload, headers=headers)
        log("Response status code: {}".format(response.status_code), level="DEBUG")
        log("Response body: {}".format(response.text), level="DEBUG")
        if response.status_code == 200:
            response_data = response.json()
            log("Parsed response data: {}".format(response_data), level="DEBUG")
            if response_data.get("status") == "error":
                log("Error message from server: {}".format(response_data.get("message")))
                print("Error: {}".format(response_data.get("message")))
                shutdown_event.set()
            else:
                log("Link retrieval initiated successfully.")
        elif response.status_code == 401:
            # Automatic re-auth: clear token and prompt user to re-consent, keep server up
            log("Unauthorized (401). Clearing cached token and initiating re-authentication flow. Response body: {}".format(response.text))
            delete_token_file()
            auth_url = get_authorization_url()
            print("Your Google session needs to be refreshed to regain permissions. A browser window will open to re-authorize the app with the required scopes.")
            open_browser_with_executable(auth_url)
            # Wait for the OAuth redirect/flow to complete; the server remains running
            shutdown_event.wait()
        elif response.status_code == 403:
            # Treat 403 similarly; scopes may be missing/changed. Force a fresh consent.
            log("Forbidden (403). Clearing cached token and prompting for fresh consent. Response body: {}".format(response.text))
            delete_token_file()
            auth_url = get_authorization_url()
            print("Permissions appear insufficient (403). Opening browser to request the correct Google permissions.")
            open_browser_with_executable(auth_url)
            shutdown_event.wait()
        elif response.status_code == 404:
            log("Not Found. Verify the URL and ensure the Apps Script is deployed correctly. Response body: {}".format(response.text))
            shutdown_event.set()
        else:
            log("Failed to initiate link retrieval. Unexpected status code: {}. Response body: {}".format(response.status_code, response.text))
            shutdown_event.set()
    except requests.exceptions.RequestException as e:
        log("RequestException during link retrieval initiation: {}".format(e))
        shutdown_event.set()
    except Exception as e:
        log("Unexpected error during link retrieval initiation: {}".format(e))
        shutdown_event.set()

def send_delete_request_to_gas(file_ids):
    """Send a delete_files action to the Apps Script web app for the provided Drive file IDs.
    Relies on OAuth token previously obtained. Sends user notifications via GAS.
    """
    try:
        medi = extract_medilink_config(config)
        url = "https://script.google.com/macros/s/{}/exec".format(medi.get('webapp_deployment_id', ''))
        access_token = get_access_token()
        if not access_token:
            log("Access token not found. Skipping cleanup request to GAS.")
            return False
        headers = {'Authorization': 'Bearer {}'.format(access_token), 'Content-Type': 'application/json'}
        payload = {"action": "delete_files", "fileIds": list(file_ids)}
        log("Initiating cleanup request to GAS. Payload size: {} id(s)".format(len(file_ids)))
        resp = requests.post(url, json=payload, headers=headers)
        log("Cleanup response status: {}".format(resp.status_code))
        # Print a concise console message
        if resp.ok:
            try:
                body = resp.json()
                msg = body.get('message', 'Files deleted successfully') if isinstance(body, dict) else 'Files deleted successfully'
            except Exception:
                msg = 'Files deleted successfully'
            print("Cleanup complete: {} ({} file(s))".format(msg, len(file_ids)))
            return True
        else:
            print("Cleanup failed with status {}: {}".format(resp.status_code, resp.text))
            return False
    except Exception as e:
        log("Error sending delete request to GAS: {}".format(e))
        print("Cleanup request error: {}".format(e))
        return False

def inspect_token(access_token):
    return http_inspect_token(access_token, log, delete_token_file_fn=delete_token_file, stop_server_fn=stop_server)

def delete_token_file():
    try:
        if os.path.exists(TOKEN_PATH):
            os.remove(TOKEN_PATH)
            log("Deleted token.json successfully.")
        else:
            log("token.json does not exist.")
    except Exception as e:
        log("Error deleting token.json: {}".format(e))

def signal_handler(sig, frame):
    log("Signal received: {}. Initiating shutdown.".format(sig))
    stop_server()
    sys.exit(0)

def auth_and_retrieval():
    access_token = get_access_token()
    if not access_token:
        log("Access token not found or expired. Please authenticate first.")
        auth_url = get_authorization_url()
        open_browser_with_executable(auth_url)
        shutdown_event.wait()
    else:
        log("Access token found. Proceeding.")
        initiate_link_retrieval(config)
        shutdown_event.wait()

def is_valid_authorization_code(auth_code):
    return oauth_is_valid_authorization_code(auth_code, log)

def clear_token_cache():
    oauth_clear_token_cache(TOKEN_PATH, log)

def check_invalid_grant_causes(auth_code):
    log("FUTURE IMPLEMENTATION: Checking common causes for invalid_grant error with auth code: {}".format(auth_code))


def ensure_authenticated_for_gmail_send(max_wait_seconds=120):
    """Ensure a valid Gmail access token is available for sending.

    - Reuses existing OAuth helpers in this module.
    - Starts the local HTTPS server if needed, opens the browser for consent,
      and polls for a token for up to max_wait_seconds.
    - Returns True if a usable access token is available after the flow; otherwise False.
    """
    try:
        token = get_access_token()
    except Exception:
        token = None
    if token:
        return True

    # Prepare server and certificates
    try:
        generate_self_signed_cert(cert_file, key_file)
    except Exception as e:
        log("Warning: could not ensure self-signed certs: {}".format(e))

    server_started_here = False
    global httpd
    try:
        if httpd is None:
            log("Starting local HTTPS server for OAuth redirect handling.")
            server_thread = Thread(target=run_server)
            server_thread.daemon = True
            server_thread.start()
            server_started_here = True
            time.sleep(0.5)  # Wait for server to initialize
            # Set flag to prevent webapp launch
            if httpd is not None:
                httpd.gmail_send_only_mode = True
    except Exception as e:
        log("Failed to start OAuth local server: {}".format(e))

    try:
        auth_url = get_authorization_url()
        print("Opening browser to authorize Gmail permission for sending...")
        open_browser_with_executable(auth_url)
    except Exception as e:
        log("Failed to open authorization URL: {}".format(e))

    # Poll for token availability within timeout
    start_ts = time.time()
    token = None
    while time.time() - start_ts < max_wait_seconds:
        try:
            token = get_access_token()
        except Exception:
            token = None
        if token:
            break
        time.sleep(3)

    if server_started_here:
        try:
            # Reset flag before shutdown
            if httpd is not None:
                httpd.gmail_send_only_mode = False
            stop_server()
        except Exception:
            pass

    if not token:
        print("Gmail authorization not completed within timeout. Please finish consent and retry.")

    return bool(token)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    try:
        generate_self_signed_cert(cert_file, key_file)
        from threading import Thread
        log("Starting server thread.")
        server_thread = Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()
        auth_and_retrieval()
        log("Stopping HTTPS server.")
        stop_server()
        log("Waiting for server thread to finish.")
        server_thread.join()
    except KeyboardInterrupt:
        log("KeyboardInterrupt received, stopping server.")
        stop_server()
        sys.exit(0)
    except Exception as e:
        log("An error occurred: {}".format(e))
        stop_server()
        sys.exit(1)