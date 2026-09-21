# -*- coding: utf-8 -*-
"""로컬 미리보기: python serve.py  →  http://localhost:8791"""
import os
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PORT = 8791
SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")

if __name__ == "__main__":
    handler = partial(SimpleHTTPRequestHandler, directory=SITE)
    httpd = ThreadingHTTPServer(("0.0.0.0", PORT), handler)
    url = f"http://localhost:{PORT}/index.html"
    print(f"연결한의원 청주오창 미리보기: {url}  (종료: Ctrl+C)")
    webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
