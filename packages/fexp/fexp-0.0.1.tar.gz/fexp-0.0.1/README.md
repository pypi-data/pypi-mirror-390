# fexp

A minimal CLI that serves a simple HTTP backend for browsing files on your machine.

- No external dependencies
- Simple JSON APIs
- CORS enabled by default

## Install

You can install `fexp` via pip:

```bash
pip install fexp
```

## CLI

```bash
fexp [--host HOST] [--port PORT] [--root ROOT] [--cors] [--upload]
```

- `--host` (default: 127.0.0.1)
- `--port` (default: 8765)
- `--root` root directory to expose (default: $PWD)
- `--cors` enable CORS (default: false)
- `--upload` enable upload API (default: false)

## Web UI

A minimal web UI is available at:

- `GET /` — opens a simple file manager page

Features:
- Navigate directories with breadcrumbs
- Click files to preview (text) or open in a new tab
- Upload files into the current directory (requires `--upload`)

### Upload API

- Multipart form (recommended): send a `file` field with the file content and filename.

Example with curl:

```bash
curl -X POST \
	-F 'file=@./README.md' \
	'http://127.0.0.1:8765/path/to/upload'
```

- Raw bytes: set `filename` in query and send the body as the file content.

```bash
curl -X POST \
	--data-binary @./README.md \
	'http://127.0.0.1:8765/path/to/upload?filename=uploaded.md&overwrite=1'
```

Notes:
- All paths are sandboxed within the configured `--root`. Attempts to escape the root are rejected.
- Responses include basic metadata: name, path, type, size, mtime.
- Uploads are disabled by default. Enable with `--upload`.

## Example

```bash
curl 'http://127.0.0.1:8765/path/to/dir?json' | jq
```

## License

MIT
