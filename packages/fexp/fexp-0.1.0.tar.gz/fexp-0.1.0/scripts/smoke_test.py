import json
import os
import sys
import time
from urllib.request import urlopen, Request
import uuid

# Ensure we can import the package from source when running from repo root
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(REPO_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from fexp.server import start_server, stop_server  # noqa: E402


def get(url: str):
    with urlopen(Request(url, method="GET")) as resp:
        data = resp.read()
        ctype = resp.headers.get("Content-Type", "")
        return resp.status, ctype, data


essential_tmp = os.path.join(REPO_ROOT, "tmp")


def main():
    host = "127.0.0.1"
    port = 9977
    root = REPO_ROOT

    httpd, thread = start_server(host=host, port=port, root=root, allow_cors=True, allow_upload=True)
    time.sleep(0.5)

    try:
        # UI page
        status, ctype, data = get(f"http://{host}:{port}/")
        assert status == 200 and ctype.startswith("text/html"), (status, ctype)
        print("/ OK")

        status, ctype, data = get(f"http://{host}:{port}/health")
        assert status == 200, status
        payload = json.loads(data)
        assert payload.get("status") == "ok", payload
        print("/health OK")

        status, ctype, data = get(f"http://{host}:{port}/api/ls?path=/")
        assert status == 200, status
        assert ctype.startswith("application/json"), ctype
        payload = json.loads(data)
        assert "items" in payload and isinstance(payload["items"], list), payload
        print("/api/ls OK (items=", len(payload["items"]), ")")

        # Stat this script (if present)
        status, ctype, data = get(f"http://{host}:{port}/api/stat?path=/README.md")
        assert status in (200, 404), status
        if status == 200:
            print("/api/stat OK")

        # Download README (if present)
        status, ctype, data = get(f"http://{host}:{port}/api/file?path=/README.md")
        if status == 200:
            print("/api/file OK (bytes=", len(data), ")")

        # Prepare upload target dir
        os.makedirs(essential_tmp, exist_ok=True)

        # Upload a small file via multipart
        content = b"hello upload\n"
        fname = f"upload_test_{uuid.uuid4().hex}.txt"
        boundary = f"----fexp{uuid.uuid4().hex}"
        multipart = []
        multipart.append(f"--{boundary}\r\n".encode())
        multipart.append(
            (
                f"Content-Disposition: form-data; name=\"file\"; filename=\"{fname}\"\r\n"
                "Content-Type: application/octet-stream\r\n\r\n"
            ).encode()
        )
        multipart.append(content)
        multipart.append(b"\r\n")
        multipart.append(f"--{boundary}--\r\n".encode())
        body = b"".join(multipart)
        req = Request(
            f"http://{host}:{port}/api/upload?path=/tmp&overwrite=1",
            method="POST",
            data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}", "Content-Length": str(len(body))},
        )
        with urlopen(req) as resp:
            assert resp.status in (200, 201), resp.status
            payload = json.loads(resp.read())
            assert payload.get("name") == fname
            print("/api/upload OK (multipart)")

        # Verify uploaded file via stat and file download
        status, ctype, data = get(f"http://{host}:{port}/api/stat?path=/tmp/{fname}")
        assert status == 200, status
        payload = json.loads(data)
        assert payload.get("type") == "file"
        status, ctype, data = get(f"http://{host}:{port}/api/file?path=/tmp/{fname}")
        assert status == 200, status
        assert data == content
        print("Uploaded file verified")

        print("Smoke test PASSED")
        return 0
    finally:
        stop_server(httpd)


if __name__ == "__main__":
    raise SystemExit(main())
