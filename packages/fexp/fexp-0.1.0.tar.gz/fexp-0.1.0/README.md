# fexp

A minimal CLI to serve a simple HTTP backend for browsing and uploading files.

## Install

You can install `fexp` via pip:

```bash
pip install fexp
```

## CLI

```bash
fexp [--host HOST] [--port PORT] [--root ROOT]  [--quiet] [--upload] [--cors]
```

- `--host` (default: 127.0.0.1)
- `--port` (default: 8765)
- `--root` root directory to expose (default: $PWD)
- `--quiet` disable logging output (default: false)
- `--upload` enable upload support (default: false)
- `--cors` enable CORS (default: false)

## Web UI

A minimal web UI is available at:

- `GET /path/to/dir` — opens a simple file manager page

Features:
- Navigate directories with breadcrumbs
- Click files to preview (text) or open in a new tab
- Upload files into the current directory (requires `--upload`)

## License

MIT
