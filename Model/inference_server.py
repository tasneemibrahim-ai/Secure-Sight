#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from inference import classify


class InferenceHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        if self.path != "/classify":
            self.send_error(404, "Not found")
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(content_length) or b"{}")
            args = argparse.Namespace(
                video=payload["video"],
                model=payload.get("model") or str(Path(__file__).with_name("best.pt")),
                timestamp=float(payload.get("timestamp", 0)),
                window_seconds=float(payload.get("windowSeconds", 5)),
                device=payload.get("device", "cpu"),
            )
            self._send_json(200, classify(args))
        except Exception as exc:  # noqa: BLE001
            self._send_json(500, {"error": str(exc)})

    def log_message(self, format: str, *args: object) -> None:
        return

    def _send_json(self, status: int, payload: dict[str, object]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    parser = argparse.ArgumentParser(description="SecureSight local model inference service.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5055)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), InferenceHandler)
    print(f"SecureSight model API running on http://{args.host}:{args.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
