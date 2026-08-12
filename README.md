# Smart Parking Lot Assist System

Rutgers ECE Capstone (SP25-02) — a computer-vision parking assist system that detects
vacant vs occupied spaces with YOLOv11 and shows live availability in a web UI.

**Team:** Rajeev Atla, Parshva Mehta, Aman Patel, Abhiram Vemuri  
**Advisor:** Kristin Dana

This repository covers the ML training/inference pipeline, PostgreSQL backend, and
Flask/FastAPI frontends used for the prototype. Intended deployment uses a Raspberry Pi 5
and camera; development often uses recorded video as a camera stand-in.

## What It Does

- Fine-tunes YOLOv11 to classify parking regions as `car` (occupied) or `empty`
- Lets you manually define parking-spot bounding boxes on a reference frame
- Runs inference on live camera or video and matches car detections to predefined spots (IoU)
- Writes spot statuses (`occupied` / `empty`) into a PostgreSQL `parking_spots` table
- Serves a Rutgers-branded web map that polls parking status in near real time
- Exposes a FastAPI backend for reading and updating spot status (and syncing `ml_output.json`)

## Architecture

```
Camera / video
      │
      ▼
YOLO (ML Model/best.pt)  +  predefined_spots.json
      │  (IoU: car boxes ↔ spot boxes)
      ▼
PostgreSQL (parking_spots)
      │
      ├── FastAPI server.py (:8000)
      └── Flask app.py (:5000) → templates/index.html
```

## Requirements

- Python 3.10+ recommended
- PostgreSQL with a database named `parking_db`
- Main packages used in this repo:
  - `ultralytics`, `opencv-python`, `torch`
  - `flask`, `fastapi`, `uvicorn`
  - `sqlalchemy`, `psycopg2-binary`, `pandas`, `pydantic`

Install (example):

```bash
pip install ultralytics opencv-python torch flask fastapi uvicorn sqlalchemy psycopg2-binary pandas pydantic
```

There is currently no locked `requirements.txt` in this repository.

## Database Setup

Create the database, then apply the schema:

```bash
createdb parking_db
psql -d parking_db -f database.sql
```

`database.sql` creates:

- `spot_id` (text, primary key)
- `status` (text, not null)
- `last_updated` (timestamp, not null)

Update the `DATABASE_URL` strings in `app.py`, `server.py`, and
`ML Model/video test/update_db.py` to match your local Postgres user/password before running.

## Usage

### 1. Define parking spots

Draw spot boxes on the first frame of a video (two clicks per spot):

```bash
python "ML Model/video test/define_spots.py"
```

Writes `predefined_spots.json` and `first_frame.jpg`.

### 2. Run video inference → database

Processes video with the trained weights, overlays spot status, and updates Postgres:

```bash
python "ML Model/video test/yolo_video_testv2.py"
```

Default inputs (editable in the script):

- Model: `ML Model/best.pt`
- Video: `ML Model/video test/testvid2.mp4`
- Spots: `predefined_spots.json`
- Annotated output: `test_predefined.avi`

### 3. Live webcam demo (no DB)

```bash
cd "ML Model"
python yolo_parking.py
```

### 4. FastAPI backend

```bash
uvicorn server:app --reload --port 8000
```

### 5. Flask parking map UI

```bash
python app.py
```

Open `http://127.0.0.1:5000`. The UI reads `/api/parking_status` from Postgres and maps
`spot_1`–`spot_60` to labeled regions (`A-*`, `BL-*`, `BR-*`, `CL-*`, `CR-*`, `D-*`).

An older alternate UI lives in `frontend.py` (campus accordion prototype that talks to FastAPI).

## API

### FastAPI (`server.py`, port 8000)

- `GET /get_parking` — all spots with `spot_id`, `status`, `last_updated`
- `POST /update_parking` — body: `{ "spot_id": "spot_1", "status": "occupied" | "empty" }`

Also updates `ml_output.json` for local ML/debug sync.

### Flask (`app.py`, port 5000)

- `GET /` — parking map UI (`templates/index.html`)
- `GET /api/parking_status` — mapped spot labels + status (`vacant` / `occupied`)

## Key Files

| Path | Role |
|------|------|
| `app.py` | Primary Flask UI + `/api/parking_status` |
| `server.py` | FastAPI read/update API + DB init |
| `database.sql` | Postgres schema |
| `predefined_spots.json` | Hand-drawn spot bounding boxes |
| `ml_output.json` | Debug dump of spot statuses |
| `ML Model/best.pt` | Deployed YOLO weights |
| `ML Model/data.yaml` | Dataset config (`car`, `empty`) |
| `ML Model/inference_export.py` | Dataset prep / training helper |
| `ML Model/yolo_parking.py` | Live webcam inference |
| `ML Model/video test/define_spots.py` | Interactive spot labeling |
| `ML Model/video test/yolo_video_testv2.py` | Video → IoU → DB pipeline |
| `ML Model/video test/update_db.py` | Postgres upsert helper |
| `templates/index.html` | Lot visualization frontend |

## Training Notes

Classes: `0 = car`, `1 = empty`. Training artifacts live under `ML Model/runs/` and
`ML Model/weights/`. The final report reports roughly:

- Precision ≈ 0.87
- Recall ≈ 0.80
- mAP50 ≈ 0.90
- mAP50-95 ≈ 0.72

Loss curves plateau around 750–800 epochs (~0.6).

## Current Limitations

- Full Raspberry Pi + fixed-camera field deployment was limited by hardware lead times and
  campus/state restrictions on drones / elevated mounts
- Phone/video capture was used as a stand-in for the intended Pi camera stream
- Distant spots are harder to detect with a single camera; multi-camera coverage is needed
  for large lots
- DB refresh was tuned toward ~30s (faster 5–10s updates caused locking/stability issues)
- Flask and FastAPI modules currently use different hardcoded DB credentials
- Automated API tests (`test_parking_api.py`) are out of date relative to the current schema
