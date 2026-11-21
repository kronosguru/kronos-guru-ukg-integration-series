"""Integration smoke test. No external network, credentials or dependencies."""
import json
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from pathlib import Path

folder = Path(__file__).parent
process = subprocess.Popen([sys.executable, str(folder / "mock_wfm_api.py")], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
base = "http://127.0.0.1:8765"
try:
    for _ in range(30):
        try:
            with urlopen(base + "/health", timeout=1) as reply:
                assert json.load(reply)["status"] == "ok"
            break
        except URLError:
            time.sleep(0.15)
    else:
        raise RuntimeError("Could not start local training server")

    def fetch(query):
        with urlopen(base + query, timeout=3) as res:
            return res.status, json.load(res)

    status, first = fetch("/api/v1/time-totals?period_end=2026-11-08&limit=3")
    assert status == 200 and first["count"] == 3 and first["total"] == 5 and first["next_offset"] == 3
    status, second = fetch("/api/v1/time-totals?period_end=2026-11-08&limit=3&offset=3")
    assert status == 200 and second["count"] == 2 and second["next_offset"] is None
    rows = first["records"] + second["records"]
    assert len(rows) == 5
    eligible = [row for row in rows if row["approved"]]
    assert len(eligible) == 4 and sum(row["hours"] for row in eligible) == 85.0
    for path, expected in [
        ("/api/v1/time-totals", 400),
        ("/api/v1/time-totals?period_end=bad", 400),
        ("/wrong-route", 404),
    ]:
        try:
            fetch(path)
            raise AssertionError("Expected HTTP error")
        except HTTPError as err:
            assert err.code == expected
    print("PASS: HTTP 200; 3+2 pagination; five rows; four eligible; 85.0 hours; 400/404 error handling")
finally:
    process.terminate()
    try:process.wait(timeout=5)
    except subprocess.TimeoutExpired:process.kill()
