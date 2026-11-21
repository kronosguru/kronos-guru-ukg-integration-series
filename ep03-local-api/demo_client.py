"""Standard-library demonstration client for the fictional local WFM API."""
import argparse
import json
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import HTTPError

parser = argparse.ArgumentParser()
parser.add_argument("--period-end", default="2026-11-08")
parser.add_argument("--limit", type=int, default=3)
args = parser.parse_args()

base = "http://127.0.0.1:8765/api/v1/time-totals"
offset = 0
all_records = []
while True:
    url = base + "?" + urlencode({"period_end": args.period_end, "limit": args.limit, "offset": offset})
    try:
        with urlopen(url, timeout=5) as response:
            payload = json.load(response)
            print(f"HTTP {response.status} | {payload['count']} records | offset {offset}")
    except HTTPError as error:
        print(f"HTTP {error.code}: {error.read().decode()}")
        raise SystemExit(1)
    all_records.extend(payload["records"])
    if payload["next_offset"] is None:
        break
    offset = payload["next_offset"]

accepted = [record for record in all_records if record["approved"]]
print(f"Fetched: {len(all_records)} | eligible (DEMO only): {len(accepted)}")
print(f"Eligible hours: {sum(row['hours'] for row in accepted):.1f}")
print(f"Not eligible: {len(all_records) - len(accepted)}")
print("IMPORTANT: This local approved flag is not a UKG approval or sign-off contract.")
