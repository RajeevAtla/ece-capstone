from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, TIMESTAMP, func, text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import json
import os

# Database Configuration
DATABASE_URL = "postgresql://parshvamehta:parshva123@localhost/parking_db"
engine = create_engine(DATABASE_URL)

# Function to initialize the database
def initialize_db():
    with engine.connect() as conn:
        with open("database.sql", "r") as file:
            sql_script = file.read()
        conn.execute(text(sql_script))
        conn.commit()

# Session Management
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# Database Model
class ParkingSpot(Base):
    __tablename__ = "parking_spots"

    id = Column(Integer, primary_key=True, index=True)
    spot_number = Column(String, unique=True, nullable=False)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    status = Column(Boolean, default=True)  # True = Available, False = Occupied
    last_updated = Column(TIMESTAMP, default=func.now())

# Create Tables
Base.metadata.create_all(bind=engine)

# Function to seed the database with initial data
def seed_database():
    session = SessionLocal()
    
    if session.query(ParkingSpot).count() == 0:
        spots = [
            ParkingSpot(spot_number="A1", x=10.5, y=20.3, status=True),
            ParkingSpot(spot_number="A2", x=15.2, y=25.1, status=False)
        ]
        session.add_all(spots)
        session.commit()
    
    session.close()

# Initialize DB and seed it with test data
initialize_db()
seed_database()

# FastAPI App
app = FastAPI()

# Pydantic Model for Updating Parking Spots
class ParkingUpdate(BaseModel):
    spot_number: str
    status: bool

# Function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to update the JSON file
def update_json_file(spot_number: str, new_status: bool):
    file_path = "ml_output.json"

    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            try:
                ml_output = json.load(file)
            except json.JSONDecodeError:
                ml_output = []
    else:
        ml_output = []

    spot_found = False
    for spot in ml_output:
        if spot["spot_number"] == spot_number:
            spot["status"] = new_status
            spot_found = True
            break
    
    if not spot_found:
        ml_output.append({"spot_number": spot_number, "status": new_status})

    with open(file_path, "w") as file:
        json.dump(ml_output, file, indent=4)

# API to Fetch Available Parking Spots
@app.get("/get_parking")
def get_parking(db: Session = Depends(get_db)):
    spots = db.query(ParkingSpot).all()
    return [{"spot_number": s.spot_number, "x": s.x, "y": s.y, "status": "vacant" if s.status else "occupied"} for s in spots]

# API to Update Parking Spot Status
@app.post("/update_parking")
def update_parking(data: ParkingUpdate, db: Session = Depends(get_db)):
    spot = db.query(ParkingSpot).filter(ParkingSpot.spot_number == data.spot_number).first()
    
    if not spot:
        raise HTTPException(status_code=404, detail="Spot not found")
    
    spot.status = data.status
    spot.last_updated = func.now()
    db.commit()

    update_json_file(data.spot_number, data.status)
    
    return {"message": f"Spot {data.spot_number} updated successfully"}

# uvicorn server:app --reload --host 0.0.0.0 --port 8000