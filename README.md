# Project Prism
An automated AI content agency managed via Google Antigravity.

## Running the Dashboard
The system telemetry is decoupled into a standalone zero-dependency web dashboard.

To view the Control Center, run a local python server from the `dashboard/` directory:

```bash
cd dashboard
python3 -m http.server 8000
```

Then open your browser to `http://localhost:8000`. The dashboard polls the central JSON state every 5 seconds.
