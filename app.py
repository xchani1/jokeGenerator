"""Local web UI for the data analytics joke generator.

Usage: python app.py [--port 8000]   then open http://127.0.0.1:8000
The server holds the Vertex AI credentials; the browser only talks to /api/joke.
"""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from main import TOPICS, generate_joke, make_client

INDEX = Path(__file__).with_name("index.html")
client = make_client()


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, body, content_type="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/":
            self._send(200, INDEX.read_bytes(), "text/html; charset=utf-8")
        elif self.path == "/api/topics":
            self._send(200, TOPICS)
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/api/joke":
            return self._send(404, {"error": "not found"})
        try:
            length = int(self.headers.get("Content-Length", 0))
            topic = json.loads(self.rfile.read(length) or b"{}").get("topic", "")
            topic, joke = generate_joke(client, str(topic)[:100])
            self._send(200, {"topic": topic, "joke": joke})
        except Exception as e:
            self._send(500, {"error": str(e)})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    port = parser.parse_args().port
    print(f"Open http://127.0.0.1:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
