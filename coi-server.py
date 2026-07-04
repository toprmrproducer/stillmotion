#!/usr/bin/env python3
"""
Static file server that sets Cross-Origin-Opener-Policy / Cross-Origin-Embedder-Policy,
matching netlify.toml, so ffmpeg.wasm's SharedArrayBuffer-based core works locally
exactly as it does in production. Used only for local Playwright verification.
"""
import http.server
import sys


class COIRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        super().end_headers()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 4334
    directory = sys.argv[2] if len(sys.argv) > 2 else "dist"
    handler = lambda *args, **kwargs: COIRequestHandler(*args, directory=directory, **kwargs)
    http.server.ThreadingHTTPServer(("", port), handler).serve_forever()
