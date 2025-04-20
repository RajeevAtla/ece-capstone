from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Text, TIMESTAMP, func, text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.dialects.postgresql import insert
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import json

# ✅ DB setup
DATABASE_URL = "postgresql://parshvamehta:parshva123@localhost/parking_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# ✅ Updated DB model (matches your simplified table)
class ParkingSpot(Base):
    __tablename__ = "parking_spots"

    spot_id = Column(String, primary_key=True)
    status = Column(Text, nullable=False)
    last_updated = Column(TIMESTAMP, nullable=False)

# ✅ DB schema init (optional .sql execution)
def initialize_db():
    if os.path.exists("database.sql"):
        with engine.connect() as conn:
            with open("database.sql", "r") as file:
                sql_script = file.read()
            conn.execute(text(sql_script))
            conn.commit()
            print("✅ Executed database.sql")
    Base.metadata.create_all(bind=engine)

# ✅ FastAPI app
app = FastAPI()

# ✅ CORS config for frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Pydantic model for POST updates
class ParkingUpdate(BaseModel):
    spot_id: str
    status: str  # "occupied" or "empty"

# ✅ Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Helper to update local JSON file for ML/debugging
def update_json_file(spot_id: str, new_status: str):
    file_path = "ml_output.json"
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                ml_output = json.load(f)
        except json.JSONDecodeError:
            ml_output = []
    else:
        ml_output = []

    updated = False
    for spot in ml_output:
        if spot["spot_id"] == spot_id:
            spot["status"] = new_status
            updated = True
            break

    if not updated:
        ml_output.append({"spot_id": spot_id, "status": new_status})

    with open(file_path, "w") as f:
        json.dump(ml_output, f, indent=4)

# ✅ GET all parking spot statuses
@app.get("/get_parking")
def get_parking(db: Session = Depends(get_db)):
    spots = db.query(ParkingSpot).order_by(ParkingSpot.spot_id).all()
    return {
        "total_spots": len(spots),
        "spots": [
            {
                "spot_id": s.spot_id,
                "status": s.status,
                "last_updated": s.last_updated.isoformat()
            }
            for s in spots
        ]
    }

# ✅ POST to update a spot status
@app.post("/update_parking")
def update_parking(data: ParkingUpdate, db: Session = Depends(get_db)):
    if data.status not in ["occupied", "empty"]:
        raise HTTPException(status_code=400, detail="Invalid status value.")

    stmt = insert(ParkingSpot).values(
        spot_id=data.spot_id,
        status=data.status,
        last_updated=func.now()
    ).on_conflict_do_update(
        index_elements=["spot_id"],
        set_={
            "status": data.status,
            "last_updated": func.now()
        }
    )
    db.execute(stmt)
    db.commit()

    update_json_file(data.spot_id, data.status)
    return {"message": f"Spot {data.spot_id} updated successfully."}

# ✅ Call once
initialize_db()