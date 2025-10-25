"""
Standalone Django project backup script

- Place this file in your Django project root.
- Run with: python standalone_django_backup.py
- Provides:
  1. List all files
  2. Download a single file
  3. Create a zip backup of the entire project
- Runs a small web server on localhost (default port 9000)
- Access via browser or curl
"""

import os
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote
import zipfile
import tempfile
import mimetypes

# --- CONFIG ---
SITE_ROOT = Path(__file__).parent.resolve()
PORT = 9000
EXCLUDE = ['.git', 'venv', '__pycache__', '.env', 'node_modules']
MAX_REASONABLE_BYTES = 500 * 1024 * 1024  # 500 MB
ALLOWED_IPS = ['127.0.0.1', '::1']

# --- HELPER FUNCTIONS ---
def should_exclude(path: Path):
    return any(part in EXCLUDE for part in path.parts)

def safe_path(requested: str):
    requested = unquote(requested).replace('..', '')
    full = (SITE_ROOT / requested).resolve()
    if SITE_ROOT not in full.parents and SITE_ROOT != full:
        return None
    return full

# --- HTTP HANDLER ---
class BackupHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, code=200):
        import json
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_GET(self):
        client_ip = self.client_address[0]
        if client_ip not in ALLOWED_IPS:
            self._send_json({'ok': False, 'error': f'Access denied from IP {client_ip}'}, code=403)
            return

        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        path = parsed.path.strip('/')

        if path == 'list_files':
            out = [str(f.relative_to(SITE_ROOT)) for f in SITE_ROOT.rglob('*') if f.is_file() and not should_exclude(f.relative_to(SITE_ROOT))]
            self._send_json({'ok': True, 'files': out})

        elif path == 'download_file':
            file_path = qs.get('file', [None])[0]
            if not file_path:
                self._send_json({'ok': False, 'error': 'No file specified'}, code=400)
                return
            full_path = safe_path(file_path)
            if not full_path or not full_path.is_file():
                self._send_json({'ok': False, 'error': 'File not found'}, code=404)
                return
            self.send_response(200)
            mime_type, _ = mimetypes.guess_type(str(full_path))
            self.send_header('Content-Type', mime_type or 'application/octet-stream')
            self.send_header('Content-Disposition', f'attachment; filename="{full_path.name}"')
            self.send_header('Content-Length', str(full_path.stat().st_size))
            self.end_headers()
            with open(full_path, 'rb') as f:
                self.wfile.write(f.read())

        elif path == 'create_backup':
            temp_dir = tempfile.gettempdir()
            backup_file = Path(temp_dir) / 'django_backup.zip'
            total_size = sum(f.stat().st_size for f in SITE_ROOT.rglob('*') if f.is_file() and not should_exclude(f.relative_to(SITE_ROOT)))
            warning = f'Warning: total size {total_size/1024/1024:.2f} MB' if total_size > MAX_REASONABLE_BYTES else None

            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for f in SITE_ROOT.rglob('*'):
                    if f.is_file() and not should_exclude(f.relative_to(SITE_ROOT)):
                        zipf.write(f, arcname=f.relative_to(SITE_ROOT))

            self.send_response(200)
            self.send_header('Content-Type', 'application/zip')
            self.send_header('Content-Disposition', f'attachment; filename="{backup_file.name}"')
            self.send_header('Content-Length', str(backup_file.stat().st_size))
            if warning:
                self.send_header('X-Warning', warning)
            self.end_headers()
            with open(backup_file, 'rb') as f:
                self.wfile.write(f.read())

        else:
            self._send_json({'ok': False, 'error': 'Unknown endpoint'}, code=404)

# --- RUN SERVER ---
if __name__ == '__main__':
    print(f'Serving backup server on http://127.0.0.1:{PORT}')
    httpd = HTTPServer(('127.0.0.1', PORT), BackupHandler)
    httpd.serve_forever()
