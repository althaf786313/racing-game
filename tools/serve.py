#!/usr/bin/env python3
"""Static server for ROAD RUSH.

Same idea as `python3 -m http.server`, but tuned for the sandbox preview pane:

  * sends `Cache-Control: no-store`, so a rebuilt index.html is never served
    stale to the preview iframe (a cached blank page is a classic "I can't see
    the preview" cause),
  * is threaded with daemon threads, so the preview proxy's keep-alive
    connection can't block the page fetch,
  * binds 0.0.0.0 so the proxy can reach it from outside the sandbox,
  * never sends X-Frame-Options/CSP, so the page may be embedded in the pane.

Usage:
    python3 tools/serve.py [port] [root]
Defaults: port 8000, root = the repository (parent of this file's folder).
"""
import functools
import http.server
import os
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
ROOT = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Handler(http.server.SimpleHTTPRequestHandler):
    server_version = "RoadRushPreview/1.0"
    # HTTP/1.1 so the preview proxy can keep pooled connections open; the base
    # class always sends Content-Length (and Connection: close on errors), so
    # there is no risk of a response with an undefined body length.
    protocol_version = "HTTP/1.1"

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Pragma", "no-cache")
        super().end_headers()

    def guess_type(self, path):
        # serve .mjs harness files as JS so they open instead of downloading
        if str(path).endswith(".mjs"):
            return "text/javascript"
        return super().guess_type(path)

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.address_string(), fmt % args))
        sys.stderr.flush()


class Server(http.server.ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def main():
    handler = functools.partial(Handler, directory=ROOT)
    try:
        httpd = Server(("0.0.0.0", PORT), handler)
    except OSError as exc:
        print(f"cannot bind 0.0.0.0:{PORT} -> {exc}", file=sys.stderr, flush=True)
        return 1
    print(f"ROAD RUSH serving {ROOT} at http://0.0.0.0:{PORT}/ (Ctrl-C to stop)", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("stopping", flush=True)
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
