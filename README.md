# Joseph Urban Traffic Optimization Advisor

**Student:** Rozario Ralston Joseph · **Roll / PS:** 15 · **Course:** CE509 Agentic AI Laboratory

Analyze traffic observations, user-supplied weather and event scenarios, and illustrative signal timings and candidate corridor rankings. The prototype uses deterministic Python agents, not an LLM framework or live traffic controller.

## Easy setup

Install Python 3.10+ from https://www.python.org/downloads/ and select **Add Python to PATH** on Windows. Extract the full folder, double-click `start.bat`, keep the terminal open, and visit http://127.0.0.1:8003/. Click **Load demo**, then **Analyze traffic**. Stop with Ctrl+C. No packages, API keys, or internet are needed after installation. On macOS/Linux run `python3 app.py`.

## CSV inputs

Use `sample.csv` as a template. Columns: timestamp (ISO date/time), junction, approach, route, vehicles (integer count), duration_minutes (positive observation interval), lanes (positive integer), avg_speed_kmph (nonnegative). Timestamp marks interval start. Use comparable, complete, non-overlapping intervals in one timezone and consistent approach names. Overlap and complete junction coverage are not automatically validated. Limits: 10,000 rows and 4 MB requests. Duplicate junction/approach/timestamp rows are rejected. Route labels represent user-selected candidate corridors; only compare candidates serving the same origin and destination with comparable sampling.

## Agents and calculations

| Agent | Responsibility |
|---|---|
| TrafficDataAgent | Validate CSV fields and reject unusable readings |
| ContextAgent | Apply weather capacity and event-demand assumptions |
| CongestionAgent | Aggregate approach volumes, speeds, and load proxies |
| SignalAgent | Allocate illustrative green times with a minimum green |
| RouteAgent | Rank supplied corridor labels by average sampled load |

Flow per lane per hour = total vehicles × 60 / total lane-minutes. Scenario demand multiplies flow by (1 + event increase / 100). Load proxy = scenario demand / (900 × weather factor). Weather factors: clear 1.0, rain 0.85, heavy rain 0.70, fog 0.75. These are illustrative assumptions, not calibrated road capacities. Proxy thresholds: below 0.65 low, 0.65–0.999 moderate, 1.0 or higher high. These categories are heuristic screens, not measured congestion or true volume-to-capacity ratios.

Signal plans assume one phase per supplied approach, four seconds lost per phase, and a ten-second minimum green. Remaining green budget is allocated proportional to per-lane scenario demand. Rounding is corrected so greens plus assumed lost time equal the cycle. Cycles must be 40–180 seconds and sufficient for the supplied phase count. This is not a calibrated signal optimizer. Lane geometry, turns, conflicting phases, pedestrians, queues, and clearance requirements are not modeled. No control hardware is connected.

RouteAgent averages approach load proxies by supplied route label and sorts ascending. It does not build a connected route, account for travel distance, or estimate travel time. Speed is reported as a duration-weighted input average, not used to infer travel times. Uniform scenario factors may leave relative signal splits and route rankings unchanged.

## Tests and demo

Run `python -m unittest discover -s tests -v`. Tests cover sample totals, exact signal budget, scenario effects, invalid inputs, impossible cycles, and invalid event settings. Demo data is fictional: 630 observed vehicles at Central Square, four approaches, a 90-second signal cycle, and 16 seconds total assumed lost time.

## Files

`agents.py`: analysis; `app.py`: local HTTP server; `index.html`, `style.css`, `main.js`: interface; `sample.csv`: fictional observations; `start.bat`: launcher; `tests/`: verification; `Technology Stack.md`: technology details. Import and analysis stay in memory on localhost. Share the whole folder as a ZIP.
