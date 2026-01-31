#!/usr/bin/env python3
"""
SG Playground Finder - Simple HTTP Server
Run with: python server.py [port]
Default port: 8082
"""
import http.server
import socketserver
import os
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8082
DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Enable CORS for development
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

if __name__ == "__main__":
    os.chdir(DIRECTORY)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🎠 SG Playground Finder")
        print(f"   Serving at: http://localhost:{PORT}")
        print(f"   Directory: {DIRECTORY}")
        print(f"   Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped")
