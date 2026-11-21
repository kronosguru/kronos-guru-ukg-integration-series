# Episode 3: Build a local training API

A small local HTTP API that serves the five fictional time records designed in Episode 2. It uses only the Python standard library, so there's nothing to install.

> **Not a UKG API.** The endpoint, field names and data are invented for training. Do not use them in a real connector.

## Requirements

Python 3.8 or later. Check with `python --version` (on some systems, `python3`).

## Files

| File | Purpose |
|---|---|
| `sample_time_totals.json` | The five fictional source records (period ending 2026-11-08) |
| `mock_wfm_api.py` | The local API server |
| `demo_client.py` | A client that requests every page and totals eligible hours |
| `smoke_test.py` | An automated test of the API |

## Run it

**Terminal 1** (start the API and leave it running):

```bash
python mock_wfm_api.py
```

**Terminal 2** (run the client):

```bash
python demo_client.py --period-end 2026-11-08 --limit 3
```

Expected output:

```
HTTP 200 | 3 records | offset 0
HTTP 200 | 2 records | offset 3
Fetched: 5 | eligible (DEMO only): 4
Eligible hours: 85.0
Not eligible: 1
```

You can also open these in a web browser while the server is running:

- http://127.0.0.1:8765/health
- http://127.0.0.1:8765/api/v1/time-totals?period_end=2026-11-08&limit=3

## Run the automated test

Stop the server in Terminal 1 first (**Ctrl+C**), because the test starts its own copy:

```bash
python smoke_test.py
```

## Experimenting

The server loads the JSON file once at startup. After editing `sample_time_totals.json`, stop the server with **Ctrl+C** and start it again.

## Notes

- The `approved` flag is a classroom rule. Real UKG payroll eligibility depends on the customer's timecard approval and sign-off process.
- Python's built-in `http.server` is for local learning only, not for production use.
