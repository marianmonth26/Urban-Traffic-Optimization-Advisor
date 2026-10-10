# Urban Traffic Optimization Advisor

A local multi-agent application that analyzes traffic observations, explores weather and event scenarios, and generates illustrative signal-timing plans and candidate corridor rankings.

## Features

- Import traffic observations from CSV files.
- Analyze vehicle demand by junction and approach.
- Explore weather and event-demand scenarios.
- Classify approach load using transparent screening rules.
- Generate illustrative signal green-time allocations.
- Compare user-supplied candidate corridors.
- Export analysis reports as JSON.
- Run locally without API keys or additional Python packages.

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python standard-library HTTP server |
| Frontend | HTML, CSS, JavaScript |
| Data input | CSV |
| Report export | JSON |
| Testing | Python unittest |

## Agents

| Agent | Responsibility |
|---|---|
| TrafficDataAgent | Validates traffic observations and rejects invalid or duplicate entries |
| ContextAgent | Applies user-selected weather and event-demand assumptions |
| CongestionAgent | Aggregates traffic demand, average speeds, and load proxies |
| SignalAgent | Allocates illustrative green times within the selected signal cycle |
| RouteAgent | Ranks supplied corridor labels by average sampled load |

The agents are deterministic, rule-based Python components with structured data handoffs. This version does not use an LLM, trained machine-learning model, or frameworks such as LangChain or CrewAI.

## Requirements

- Python 3.10 or newer
- A modern web browser

No additional packages, API keys, or internet connection are required after Python installation.

## Installation and Setup

### Windows

1. Download this repository using **Code → Download ZIP**.
2. Extract the ZIP file.
3. Install Python and select **Add Python to PATH**.
4. Open the extracted project folder.
5. Double-click `start.bat`.
6. Open:

   http://127.0.0.1:8003/

Keep the terminal window open while using the application. Press **Ctrl+C** to stop the server.

### Terminal

Open a terminal inside the project folder:

```bash
python app.py
```

On macOS or Linux:

```bash
python3 app.py
```

## How to Use

1. Click **Load demo** or import a CSV file.
2. Select a weather scenario.
3. Enter the expected event-demand increase.
4. Select a signal cycle between **40 and 180 seconds**.
5. Click **Analyze traffic**.
6. Review approach loads, signal plans, and corridor rankings.
7. Click **Export JSON** to download the report.

The included demonstration observations are fictional.

## CSV Format

```csv
timestamp,junction,approach,route,vehicles,duration_minutes,lanes,avg_speed_kmph
2026-10-01T08:00:00,Central Square,North,Main corridor,240,15,2,18
2026-10-01T08:00:00,Central Square,South,Main corridor,180,15,2,24
2026-10-01T08:00:00,Central Square,East,Riverside corridor,90,15,2,35
2026-10-01T08:00:00,Central Square,West,Riverside corridor,120,15,2,30
```

| Field | Description |
|---|---|
| timestamp | Observation interval start in ISO date/time format |
| junction | Junction name |
| approach | Approach name or direction |
| route | User-supplied candidate corridor label |
| vehicles | Nonnegative integer vehicle count |
| duration_minutes | Positive observation duration |
| lanes | Positive integer lane count |
| avg_speed_kmph | Nonnegative observed average speed |

Use comparable, non-overlapping observation intervals in a consistent timezone. Include all approaches when preparing a junction scenario.

Limits: **10,000 rows** and requests under **4 MB**.

Duplicate junction, approach, and timestamp combinations are rejected. Overlapping intervals and complete junction coverage are not automatically checked.

## Analysis Method

### Traffic Demand

```text
Flow per lane per hour =
    total vehicles × 60 ÷ total lane-minutes

Scenario demand =
    flow per lane per hour × (1 + event increase ÷ 100)

Load proxy =
    scenario demand ÷ (900 × weather factor)
```

### Weather Assumptions

| Weather | Capacity factor |
|---|---|
| Clear | 1.00 |
| Rain | 0.85 |
| Heavy rain | 0.70 |
| Fog | 0.75 |

The weather factors and reference value of 900 vehicles per hour per lane are illustrative assumptions, not calibrated road capacities.

### Load Screening

| Load proxy | Category |
|---|---|
| Below 0.65 | Low |
| 0.65 to below 1.00 | Moderate |
| 1.00 or higher | High |

These categories are heuristic indicators. They do not represent measured congestion or a true volume-to-capacity ratio.

### Signal-Timing Scenarios

The signal agent assumes:

- One phase per supplied approach
- Four seconds of lost time per phase
- A minimum green time of ten seconds per phase

The remaining green-time budget is distributed proportionally to per-lane scenario demand. Rounding is adjusted so total green time plus assumed lost time equals the selected cycle.

A cycle is rejected if it cannot accommodate the assumed phases and minimum green times.

### Candidate Corridor Ranking

The route agent averages approach load proxies for each supplied corridor label and ranks them from lowest to highest.

Compare only candidates serving the same origin and destination with equivalent sampling coverage. This feature does not calculate connected navigation routes, travel distance, or travel time.

Uniform weather and event factors may change load values without changing relative signal splits or corridor rankings.

## Workflow

```text
CSV Traffic Observations
          ↓
TrafficDataAgent
          ↓
ContextAgent
          ↓
CongestionAgent
          ↓
SignalAgent and RouteAgent
          ↓
Dashboard and JSON Export
```

## Demonstration Output

With the included sample, clear weather, no event increase, and a 90-second cycle:

- Observed vehicles: **630**
- Assumed phases: **4**
- Total assumed lost time: **16 seconds**
- Available green time: **74 seconds**

| Approach | Green time |
|---|---|
| North | 22.95 seconds |
| South | 19.71 seconds |
| East | 14.86 seconds |
| West | 16.48 seconds |

These are illustrative allocations, not approved operational signal timings.

## Project Structure

```text
├── app.py
├── agents.py
├── index.html
├── style.css
├── main.js
├── sample.csv
├── start.bat
├── Technology Stack.md
├── README.md
└── tests/
    └── test_agents.py
```

## Running Tests

```bash
python -m unittest discover -s tests -v
```

Tests cover:

- Sample vehicle totals and corridor ordering
- Signal-cycle accounting and minimum green times
- Weather and event scenario effects
- Invalid traffic observations
- Insufficient signal-cycle duration
- Invalid event settings

## Privacy

- The server listens only on localhost.
- Imported observations are processed in memory.
- No traffic data is sent to external services.
- No signal controllers or road infrastructure are connected.

## Limitations

- Weather, event, and traffic inputs are manually supplied.
- No live traffic or weather feeds are used.
- Signal plans do not model pedestrian requirements, turning conflicts, queues, road geometry, or clearance rules.
- Load screening is not a calibrated traffic-engineering model.
- Corridor rankings do not establish the fastest or safest route.
- Observed speed is summarized but is not used to calculate travel time.
- Recommendations require professional assessment before operational use.

## Future Improvements

- Calibrate demand and capacity assumptions using real observations.
- Add interval-overlap and junction-coverage validation.
- Model pedestrian phases, turning movements, and queues.
- Support connected road networks and travel-time estimates.
- Evaluate recommendations against established traffic baselines.
