import http.server
import urllib.request
import json
import os

PORT = 8080
TARGET_URL = "https://api.anthropic.com/v1/messages"

class CustomHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Serve local files (like HTML, CSS, JS)
        path = self.path.lstrip('/')
        if path == "" or path == "/":
            path = "inkscript_ai_claude.html"
            
        if os.path.exists(path) and os.path.isfile(path):
            try:
                with open(path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                if path.endswith(".html"):
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                elif path.endswith(".js"):
                    self.send_header("Content-Type", "application/javascript; charset=utf-8")
                elif path.endswith(".css"):
                    self.send_header("Content-Type", "text/css; charset=utf-8")
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self.send_error(500, str(e))
        else:
            self.send_error(404, "File not found")

    def do_POST(self):
        if self.path == "/api/chat":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            headers = {
                "content-type": "application/json",
                "x-api-key": self.headers.get("x-api-key", ""),
                "anthropic-version": self.headers.get("anthropic-version", "2023-06-01")
            }
            
            req = urllib.request.Request(TARGET_URL, data=body, headers=headers, method="POST")
            
            try:
                with urllib.request.urlopen(req) as response:
                    res_body = response.read()
                    self.send_response(response.status)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(res_body)
            except urllib.error.HTTPError as e:
                self.send_response(e.code)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(e.read())
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": {"message": str(e)}}).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    server_address = ("", PORT)
    httpd = http.server.HTTPServer(server_address, CustomHandler)
    print(f"Studio running at http://localhost:{PORT}/inkscript_ai_claude.html")
    httpd.serve_forever()