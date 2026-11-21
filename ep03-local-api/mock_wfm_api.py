"""Kronos Guru Ep 3: local, fictional WFM-like HTTP API.

NOT an official UKG API, UKG schema, or a production interface.
Runs on localhost using the Python standard library.
"""
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import json

HOST = "127.0.0.1"
PORT = 8765
DATA = json.loads(Path(__file__).with_name("sample_time_totals.json").read_text(encoding="utf-8"))


class WfmDemoHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def send_json(self, status, payload):
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            return self.send_json(200, {"status": "ok", "environment": "fictional-local-training"})
        if parsed.path != "/api/v1/time-totals":
            return self.send_json(404, {"error": "NOT_FOUND", "message": "Unknown route"})

        params = parse_qs(parsed.query)
        period = params.get("period_end", [None])[0]
        if not period:
            return self.send_json(400, {"error": "MISSING_PERIOD_END", "message": "Supply period_end=YYYY-MM-DD"})
        try:
            if date.fromisoformat(period).isoformat() != period:
                raise ValueError()
            limit = int(params.get("limit", [100])[0])
            offset = int(params.get("offset", [0])[0])
            if not (1 <= limit <= 100) or offset < 0:
                raise ValueError()
        except ValueError:
            return self.send_json(400, {"error": "INVALID_QUERY", "message": "Use ISO date, limit 1-100 and offset >= 0"})

        matches = [rec for rec in DATA if rec["period_end"] == period]
        page = matches[offset:offset + limit]
        next_offset = offset + limit if offset + limit < len(matches) else None
        return self.send_json(200, {
            "notice": "FICTIONAL TRAINING DATA — NOT AN OFFICIAL UKG API",
            "period_end": period,
            "total": len(matches),
            "count": len(page),
            "offset": offset,
            "next_offset": next_offset,
            "records": page,
        })


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), WfmDemoHandler)
    print(f"Local training API: http://{HOST}:{PORT}", flush=True)
    print("GET /api/v1/time-totals?period_end=2026-11-08", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
