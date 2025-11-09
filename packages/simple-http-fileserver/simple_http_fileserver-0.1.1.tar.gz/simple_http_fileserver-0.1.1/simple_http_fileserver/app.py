from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import threading
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import urllib.request

server = None
server_thread = None
is_running = False
log_widget = None

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
        log_to_gui(f"[POST] Saved file: {filename} ({length} bytes)")

    def do_GET(self):
        import urllib.parse
        parsed_path = urllib.parse.unquote(self.path)

        if parsed_path != '/' and os.path.isfile(parsed_path[1:]):
            filepath = parsed_path[1:]
            try:
                with open(filepath, 'rb') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-Disposition', f'attachment; filename="{os.path.basename(filepath)}"')
                self.send_header('Content-Type', 'application/octet-stream')
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                log_to_gui(f"[DOWNLOAD] Served file: {filepath}")
                return
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Error serving file: {e}".encode())
                log_to_gui(f"[ERROR] Failed to serve file {filepath}: {e}")
                return

        try:
            entries = os.listdir('.')
            file_links = []

            for entry in entries:
                if os.path.isfile(entry):
                    href = f"/{entry}"
                    file_links.append(f'<li><a href="{href}" download>{entry}</a></li>')
                elif os.path.isdir(entry):
                    file_links.append(f'<li><strong>[DIR]</strong> {entry}</li>')

            html = f"""
            <html>
            <head><title>File Server</title></head>
            <body>
                <h2>Directory Listing</h2>
                <ul>
                    {''.join(file_links)}
                </ul>
            </body>
            </html>
            """

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())

            log_to_gui("[GET] Served HTML file listing")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error: {e}\n".encode())
            log_to_gui(f"[ERROR] GET request failed: {e}")


def log_to_gui(message):
    if log_widget:
        log_widget.insert(tk.END, message + "\n")
        log_widget.see(tk.END)

def run_server(port):
    global server, is_running
    try:
        server = HTTPServer(('0.0.0.0', port), Handler)
        is_running = True
        log_to_gui(f"[INFO] Server started on port {port}")
        server.serve_forever()
    except Exception as e:
        log_to_gui(f"[ERROR] Server failed to start: {e}")

def start_gui():
    def start_server():
        global server_thread
        if not is_running:
            try:
                port = int(port_entry.get())
                if port < 1 or port > 65535:
                    raise ValueError("Invalid port number")
            except ValueError:
                log_to_gui("[ERROR] Invalid port number")
                return

            server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
            server_thread.start()
            status_label.config(text=f"Server is running on port {port}", fg="green")
            start_button.config(state=tk.DISABLED)
            stop_button.config(state=tk.NORMAL)

    def stop_server():
        global server, is_running

        if is_running and server:
            def shutdown_thread():
                global server, is_running
                try:
                    port = server.server_port
                    try:
                        urllib.request.urlopen(f"http://127.0.0.1:{port}/__shutdown__", timeout=1)
                    except:
                        pass 

                    server.shutdown()
                    server.server_close()
                    log_to_gui("[INFO] Server stopped")
                except Exception as e:
                    log_to_gui(f"[ERROR] Shutdown failed: {e}")
                finally:
                    window.after(0, lambda: (
                        status_label.config(text="Server stopped", fg="red"),
                        start_button.config(state=tk.NORMAL),
                        stop_button.config(state=tk.DISABLED)
                    ))
                    server = None
                    is_running = False

            threading.Thread(target=shutdown_thread, daemon=True).start()

    def show_help():
        help_text = r"""
    ++++Simple HTTP File Server++++

This Tool will run python based http GET and Post file server.

Usage:
1. The server will list (GET) the content of the current directory where the app located: Browse the IP of the machine with the selected port http://192.168.8.10:80 Or you can use one of the following in linux:
wget http://192.168.8.10:80/
Or: curl http://192.168.8.10:80/

2. The server will accept transferred files (POST) and save them to current directory where the app located. You can use one of the following: 
a) Using curl
curl.exe -X POST -H "X-Filename: nmap.exe" --data-binary "@C:\Users\kaled\Downloads\nmap-7.98-setup.exe" http://192.168.8.10:80/
you will get nmap.exe after the upload.
Where:
-X Use the HTTP POST method (send data in the request body).
-H "X-Filename: nmap.exe". Add a custom HTTP header named X-Filename with value nmap.exe (your server reads this to pick the filename to save).
--data-binary "@C:\Users\kaled\Downloads\nmap-7.98-setup.exe" Send the exact bytes of that local file as the HTTP request body. The @ tells curl to read the file contents.
http://192.168.8.10:80/ The destination URL (IP and port 80).

b) Using wget
wget --method=POST --header="X-Filename: test.txt" --header="Content-Type: application/octet-stream" --body-file="C:\Users\kaled\Downloads\somefile.txt" "http://192.168.8.10:80/"
Where: 
--method=POST sets the method to POST.
--header=... sends the custom X-Filename header.
test.txt the file name after transferring, it can be anything like key.pem.
--body-file=somefile.txt sends the file as raw binary.
somefile.txt the file name before transferring, it should be exact.

Created by Kaled Aljebur for learning purposes in teaching classes.
        """
        
        top = tk.Toplevel(window)
        top.title("Help")

        # help_label = tk.Label(top, text=help_text, justify=tk.LEFT, padx=10, pady=10)
        # help_label.pack(padx=10, pady=10)
        help_box = ScrolledText(top, wrap=tk.WORD, height=37, width=95)
        help_box.insert(tk.END, help_text)
        help_box.config(state=tk.DISABLED)  
        help_box.pack(padx=10, pady=10)

        close_button = tk.Button(top, text="Close", command=top.destroy)
        close_button.pack(pady=5)

    window = tk.Tk()
    window.title("Simple HTTP File Server")
    window.geometry("500x450")

    tk.Label(window, text="Get & Post fileServer").pack(pady=5)

    port_frame = tk.Frame(window)
    port_frame.pack(pady=5)
    tk.Label(port_frame, text="Port:").pack(side=tk.LEFT)
    port_entry = tk.Entry(port_frame, width=10)
    port_entry.insert(0, "80")
    port_entry.pack(side=tk.LEFT)

    status_label = tk.Label(window, text="Server not running", fg="red")
    status_label.pack()

    button_frame = tk.Frame(window)
    button_frame.pack(pady=5)

    start_button = tk.Button(button_frame, text="Start Server", command=start_server)
    start_button.pack(side=tk.LEFT, padx=10)

    stop_button = tk.Button(button_frame, text="Stop Server", command=stop_server, state=tk.DISABLED)
    stop_button.pack(side=tk.LEFT, padx=10)

    stop_help = tk.Button(button_frame, text="Help", command=show_help)
    stop_help.pack(side=tk.LEFT, padx=10)

    global log_widget
    log_widget = ScrolledText(window, height=20)
    log_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    window.mainloop()

def main():
    start_gui()
if __name__ == "__main__":
    main()
