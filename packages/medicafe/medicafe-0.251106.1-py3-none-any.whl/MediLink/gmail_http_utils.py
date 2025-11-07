import json
import os
import ssl
import subprocess
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer

# Try to import centralized logging
try:
    from MediCafe.core_utils import get_shared_config_loader
    _config_loader = get_shared_config_loader()
    if _config_loader:
        _central_log = _config_loader.log
    else:
        _central_log = None
except ImportError:
    _central_log = None


def generate_self_signed_cert(openssl_cnf_path, cert_file, key_file, log, subprocess_module, cert_days=365):
    log("Checking if certificate file exists: " + cert_file)
    log("Checking if key file exists: " + key_file)

    cert_needs_regeneration = True
    if os.path.exists(cert_file):
        try:
            check_cmd = ['openssl', 'x509', '-in', cert_file, '-checkend', '86400', '-noout']
            result = subprocess_module.call(check_cmd)
            if result == 0:
                log("Certificate is still valid")
                cert_needs_regeneration = False
            else:
                log("Certificate is expired or will expire soon")
                try:
                    if os.path.exists(cert_file):
                        os.remove(cert_file)
                        log("Deleted expired certificate file: {}".format(cert_file))
                    if os.path.exists(key_file):
                        os.remove(key_file)
                        log("Deleted expired key file: {}".format(key_file))
                except (IOError, OSError) as e:
                    log("Error deleting expired certificate files: {}".format(e))
        except (IOError, OSError, subprocess.CalledProcessError) as e:
            log("Error checking certificate expiration: {}".format(e))

    if cert_needs_regeneration:
        log("Generating self-signed SSL certificate...")
        cmd = [
            'openssl', 'req', '-config', openssl_cnf_path, '-nodes', '-new', '-x509',
            '-keyout', key_file,
            '-out', cert_file,
            '-days', str(cert_days),
            '-sha256'
        ]
        try:
            log("Running command: " + ' '.join(cmd))
            result = subprocess_module.call(cmd)
            log("Command finished with result: " + str(result))
            if result != 0:
                raise RuntimeError("Failed to generate self-signed certificate")
            verify_cmd = ['openssl', 'x509', '-in', cert_file, '-text', '-noout']
            verify_result = subprocess_module.call(verify_cmd)
            if verify_result != 0:
                raise RuntimeError("Generated certificate verification failed")
            log("Self-signed SSL certificate generated and verified successfully.")
        except (IOError, OSError, subprocess.CalledProcessError, RuntimeError) as e:
            log("Error generating self-signed certificate: {}".format(e))
            raise


def start_https_server(port, handler_cls, cert_file, key_file, log):
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, handler_cls)
    log("Attempting to wrap socket with SSL. cert_file=" + cert_file + ", key_file=" + key_file)
    httpd.socket = ssl.wrap_socket(httpd.socket, certfile=cert_file, keyfile=key_file, server_side=True)
    log("Starting HTTPS server on port {}".format(port))
    httpd.serve_forever()
    return httpd


def inspect_token(access_token, log, delete_token_file_fn=None, stop_server_fn=None):
    # Import the constant from oauth_utils
    try:
        from MediLink.gmail_oauth_utils import GOOGLE_TOKENINFO_URL
        info_url = GOOGLE_TOKENINFO_URL + "?access_token={}".format(access_token)
    except ImportError:
        # Fallback to hardcoded URL if import fails
        info_url = "https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}".format(access_token)
    try:
        response = requests.get(info_url)
        log("Token info: Status code {}, Body: {}".format(response.status_code, response.text))
        if response.status_code == 200:
            return response.json()
        else:
            log("Failed to inspect token. Status code: {}, Body: {}".format(response.status_code, response.text))
            if response.status_code == 400 and "invalid_token" in response.text:
                # Token is invalid (revoked/expired). Clear cache and let caller trigger re-auth.
                log("Access token is invalid. Clearing token cache and keeping server running for re-auth.")
                if delete_token_file_fn:
                    delete_token_file_fn()
                return None
            return None
    except (requests.exceptions.RequestException, ValueError) as e:
        log("Exception during token inspection: {}".format(e))
        return None


class SSLRequestHandler(BaseHTTPRequestHandler):
    """
    Enhanced RequestHandler that suppresses expected SSL certificate warnings.
    Python 3.4.4 compatible.
    """
    def handle_one_request(self):
        """Override to catch SSL errors and suppress expected certificate warnings"""
        try:
            super().handle_one_request()
        except ssl.SSLError as e:
            # SSL errors are expected with self-signed certs when client accepts warning
            error_str = str(e).lower()
            if "unknown ca" in error_str or "certificate" in error_str:
                # Expected SSL warning - client can accept and proceed
                # Don't log expected certificate warnings as they are normal behavior
                pass
            else:
                # Unexpected SSL error - log at WARNING level
                if _central_log:
                    _central_log("Unexpected SSL error in request handler: {}".format(e), level="WARNING")
        except Exception as e:
            # Re-raise non-SSL exceptions
            raise