#!/usr/bin/env python3
"""
Newsletter API v4 Website Server
Serves the modern v4 web interface
"""
import http.server
import socketserver
import os
from pathlib import Path

PORT = 8082

class V4HTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=Path(__file__).parent, **kwargs)
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_GET(self):
        # Serve index.html as the main page
        if self.path == '/' or self.path == '/index.html':
            self.path = '/index.html'
        return super().do_GET()

def main():
    os.chdir(Path(__file__).parent)
    
    with socketserver.TCPServer(("", PORT), V4HTTPRequestHandler) as httpd:
        print(f"Urban Pulse v4 website running at http://localhost:{PORT}")
        print("Press Ctrl+C to stop the server")
        httpd.serve_forever()

if __name__ == "__main__":
    main()
