from http.server import BaseHTTPRequestHandler, HTTPServer
import os

def main():
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            filename = self.headers.get('X-Filename', 'default_uploaded_file')
            filename = os.path.basename(filename)
            length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(length)
            with open(filename, "wb") as f:
                f.write(post_data)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        def do_GET(self):
            try:
                entries = os.listdir('.')
                listing = "\n".join(entries).encode()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Directory listing:\n")
                self.wfile.write(listing)
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Error: {e}\n".encode())
                
    server = HTTPServer(('0.0.0.0', 80), Handler)
    print("Listening on port 80...")
    server.serve_forever()

if __name__ == "__main__":
    main()