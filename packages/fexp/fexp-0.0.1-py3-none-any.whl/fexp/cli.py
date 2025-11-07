import argparse
import signal
import sys
from pathlib import Path

from .server import start_server, stop_server


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="fexp",
        description="Start a minimal HTTP file explorer backend server.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8765, help="Port to listen on (default: 8765)")
    parser.add_argument(
        "--root",
        default=str(Path.cwd()),
        help="Root directory to expose (default: current working directory)",
    )
    parser.add_argument(
        "--cors",
        action="store_true",
        help="Disable CORS headers (enabled by default)",
    )
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Enable file upload API (default: disabled)",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    httpd, thread = start_server(
        host=args.host,
        port=args.port,
        root=args.root,
        allow_cors=args.cors,
        allow_upload=args.upload,
    )

    def _shutdown(*_):
        stop_server(httpd)

    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    try:
        # Block until server thread stops
        thread.join()
    except KeyboardInterrupt:
        pass
    finally:
        stop_server(httpd)


if __name__ == "__main__":
    sys.exit(main())
