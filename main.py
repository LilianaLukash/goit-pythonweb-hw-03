import mimetypes
import pathlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import json
from datetime import datetime


class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {
            key: value for key, value in [el.split("=") for el in data_parse.split("&")]
        }

        # Сохраняем сообщение в storage/data.json
        storage_path = pathlib.Path("storage")
        storage_path.mkdir(exist_ok=True)
        data_file = storage_path / "data.json"

        if data_file.exists():
            with open(data_file, "r", encoding="utf-8") as f:
                existing = json.load(f)
        else:
            existing = {}

        existing[str(datetime.now())] = data_dict

        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)

        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == "/":
            self.send_html_file("index.html")
        elif pr_url.path == "/message":
            self.send_html_file("message.html")
        elif pr_url.path == "/read":
            self.send_read_page()
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file("error.html", 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f".{self.path}", "rb") as file:
            self.wfile.write(file.read())

    def send_read_page(self):
        data_file = pathlib.Path("storage/data.json")
        if data_file.exists():
            with open(data_file, "r", encoding="utf-8") as f:
                messages = json.load(f)
        else:
            messages = {}

        html = """
                <html>
                    <head>
                    <meta charset="utf-8">
                    <title>Messages</title>
                    <link rel="stylesheet" href="/style.css">
                </head>
                <body>
                """
        html += "<h1>Все сообщения:</h1><a href='/'>⬅ Назад</a><hr>"
        for time, msg in messages.items():
            html += f"<p><strong>{msg['username']}</strong> ({time})<br>{msg['message']}</p><hr>"
        html += "</body></html>"

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ("", 8000)  # можно сменить на 3000, если нужно строго по заданию
    http = server_class(server_address, handler_class)
    try:
        print("Сервер запущен на http://localhost:8000")
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == "__main__":
    run()
