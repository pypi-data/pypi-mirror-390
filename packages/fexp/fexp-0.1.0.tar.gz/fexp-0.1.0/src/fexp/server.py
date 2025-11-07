import json
import mimetypes
import os
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from .template import html_template

def _within_root(root: Path, target: Path) -> bool:
    try:
        root_resolved = root.resolve()
        target_resolved = target.resolve()
        return str(target_resolved).startswith(str(root_resolved))
    except FileNotFoundError:
        # For non-existent paths, check the parent
        return str(target.resolve().parent).startswith(str(root.resolve()))


def _relpath(root: Path, target: Path) -> str:
    try:
        return "/" + target.resolve().relative_to(root.resolve()).as_posix()
    except Exception:
        return "/"


def _file_type(item: Path) -> str:
    is_dir = item.is_dir()
    is_file = item.is_file()
    return "dir" if is_dir else ("file" if is_file else "unknown")

def _file_stat(item: Path) -> os.stat_result:
    try:
        stat = item.stat()
        return {
            "name": item.name,
            "type": _file_type(item),
            "size": stat.st_size,
            "mtime": stat.st_mtime,
        }
    except FileNotFoundError:
        # Entry might have disappeared
        return {
            "name": item.name,
            "type": "unknown",
        }


class ApiHandler(BaseHTTPRequestHandler):
    root_dir: Path = Path.cwd()
    allow_cors: bool = False
    allow_upload: bool = False
    log_quiet: bool = False

    def log_message(self, format: str, *args):  # noqa: A003 - match BaseHTTPRequestHandler
        if self.log_quiet:
            return
        # Simple stdout log, can be customized
        return super().log_message(format, *args)

    def _send_cors(self):
        if self.allow_cors:
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

    def _send_json(self, status: int, obj: dict | list):
        data = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self._send_cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_html(self):
        self.send_response(200)
        self._send_cors()
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html_template)))
        self.end_headers()
        self.wfile.write(html_template.encode("utf-8"))

    def _bad_request(self, message: str):
        self._send_json(HTTPStatus.BAD_REQUEST, {"error": message})

    def _not_found(self, message: str):
        self._send_json(HTTPStatus.NOT_FOUND, {"error": message})

    def do_OPTIONS(self):  # noqa: N802 - match BaseHTTPRequestHandler
        # Preflight response
        self.send_response(HTTPStatus.NO_CONTENT)
        self._send_cors()
        self.end_headers()

    def do_GET(self):  # noqa: N802 - match BaseHTTPRequestHandler
        parsed = urlparse(self.path)
        target = self._get_target(parsed.path)
        qs = parse_qs(parsed.query, keep_blank_values=True)

        if target.is_dir():
            return self._handle_dir(target, qs)
        return self._handle_file(target, qs)

    def do_POST(self):  # noqa: N802 - match BaseHTTPRequestHandler
        parsed = urlparse(self.path)
        target = self._get_target(parsed.path)
        qs = parse_qs(parsed.query, keep_blank_values=True)
        return self._handle_upload(target, qs)

    def _get_target(self, raw_path: str) -> Path | None:
        # URL-decoding then treat as POSIX-like absolute within root
        rel = Path("." if raw_path in ("", "/") else unquote(raw_path).lstrip("/"))
        target = (self.root_dir / rel)
        if not _within_root(self.root_dir, target):
            return None
        return target

    def _handle_dir(self, target: Path, qs: dict):
        if target is None:
            return self._bad_request("Invalid path")
        if not target.exists():
            return self._not_found("Path does not exist")
        if not target.is_dir():
            return self._bad_request("Path is not a directory")

        # no json query then return HTML
        if qs.get("json", ["0"])[0] in ("0", "false", "False"):
            return self._send_html()

        try:
            items = []
            with os.scandir(target) as it:
                for entry in it:
                    items.append(_file_stat(Path(entry.path)))
            items.sort(key=lambda x: (x.get("type") != "dir", x.get("name", "").lower()))
            return self._send_json(200, {
                "path": _relpath(self.root_dir, target),
                "items": items,
            })
        except PermissionError:
            return self._bad_request("Permission denied")

    def _handle_file(self, target: Path, qs: dict):
        if target is None:
            return self._bad_request("Invalid path")
        if not target.exists():
            return self._not_found("File does not exist")
        if not target.is_file():
            return self._bad_request("Path is not a file")

        ctype, _ = mimetypes.guess_type(target.name)
        ctype = ctype or "application/octet-stream"
        try:
            self.send_response(200)
            self._send_cors()
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Disposition", f"inline; filename=\"{target.name}\"")
            self.send_header("Content-Length", str(target.stat().st_size))
            self.end_headers()
            with open(target, "rb") as f:
                while True:
                    chunk = f.read(64 * 1024)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
        except PermissionError:
            return self._bad_request("Permission denied")

    def _handle_upload(self, target: Path, qs: dict):
        if not self.allow_upload:
            return self._send_json(HTTPStatus.FORBIDDEN, {"error": "Upload disabled"})

        # Destination directory within root
        if target is None:
            return self._bad_request("Invalid destination path")
        if not target.exists():
            return self._not_found("Destination does not exist")
        if not target.is_dir():
            return self._bad_request("Destination is not a directory")

        overwrite = qs.get("overwrite", ["0"])[0] not in ("0", "false", "False")

        ctype = self.headers.get("Content-Type", "")
        clen = int(self.headers.get("Content-Length", "0") or 0)
        if not ctype:
            return self._bad_request("Missing Content-Type")

        # Helper to write stream to file in chunks
        def _write_to(dest_path: Path, src):
            with open(dest_path, "wb") as out:
                while True:
                    chunk = src.read(64 * 1024)
                    if not chunk:
                        break
                    out.write(chunk)

        # multipart/form-data
        if ctype.startswith("multipart/form-data"):
            import cgi  # stdlib; deprecated but fine for simple usage

            env = {
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": ctype,
                "CONTENT_LENGTH": str(clen),
            }
            fs = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ=env)
            if "file" not in fs:
                return self._bad_request("Missing file field")
            item = fs["file"]
            # item.file is a file-like object
            filename = item.filename or "upload.bin"
            # sanitize filename: basename only
            filename = os.path.basename(filename)
            if not filename:
                filename = "upload.bin"

            dest_path = target / filename
            if dest_path.exists() and not overwrite:
                return self._send_json(HTTPStatus.CONFLICT, {"error": "File exists", "path": _relpath(self.root_dir, dest_path)})
            try:
                _write_to(dest_path, item.file)
            except PermissionError:
                return self._bad_request("Permission denied")

            return self._send_json(HTTPStatus.CREATED, {
                "path": _relpath(self.root_dir, dest_path),
                "size": dest_path.stat().st_size,
            })

        # raw bytes with filename in query
        if ctype in ("application/octet-stream", "binary/octet-stream") or True:
            # Fallthrough also accepts other types as raw for simplicity
            filename = qs.get("filename", [""])[0]
            filename = os.path.basename(filename)
            if not filename:
                return self._bad_request("Missing filename query parameter for raw upload")
            dest_path = target / filename
            if dest_path.exists() and not overwrite:
                return self._send_json(HTTPStatus.CONFLICT, {"error": "File exists", "path": _relpath(self.root_dir, dest_path)})
            try:
                # Wrap rfile with a limited reader based on Content-Length if present
                remaining = clen
                class _Src:
                    def __init__(self, rfile, n):
                        self.rfile = rfile
                        self.remaining = n
                    def read(self, n):
                        if self.remaining == 0:
                            return b""
                        to_read = n if self.remaining < 0 else min(n, self.remaining)
                        data = self.rfile.read(to_read)
                        if self.remaining >= 0:
                            self.remaining -= len(data)
                        return data
                _write_to(dest_path, _Src(self.rfile, remaining))
            except PermissionError:
                return self._bad_request("Permission denied")
            return self._send_json(HTTPStatus.CREATED, {
                "path": _relpath(self.root_dir, dest_path),
                "size": dest_path.stat().st_size,
            })


def start_server(
    host: str = "127.0.0.1",
    port: int = 8765,
    root: str | os.PathLike = ".",
    log_quiet: bool = False,
    allow_upload: bool = False,
    allow_cors: bool = False,
):
    root_path = Path(root).resolve()

    class _Handler(ApiHandler):
        pass

    _Handler.root_dir = root_path
    _Handler.log_quiet = log_quiet
    _Handler.allow_upload = allow_upload
    _Handler.allow_cors = allow_cors

    httpd = ThreadingHTTPServer((host, port), _Handler)

    def _serve():
        try:
            httpd.serve_forever()
        finally:
            httpd.server_close()

    t = threading.Thread(target=_serve, name="fexp-server", daemon=True)
    t.start()
    print(f"fexp server listening on http://{host}:{port} (root={root_path})")
    return httpd, t


def stop_server(httpd: ThreadingHTTPServer):
    try:
        httpd.shutdown()
    except Exception:
        pass
