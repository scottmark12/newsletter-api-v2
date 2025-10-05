#!/usr/bin/env python3
"""
Simple server for the working website
"""

import http.server
import socketserver
import os

PORT = 8082

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.path = '/index_working.html'
        return super().do_GET()

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"🚀 Server running at http://localhost:{PORT}")
        print(f"📱 Open http://localhost:{PORT} in your browser")
        print("🔧 Use the interface to initialize the database and run crawls")
        print("⏹️  Press Ctrl+C to stop")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped")

if __name__ == "__main__":
    main()
