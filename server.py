from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, TIMESTAMP, func
from sqlalchemy.orm import sessionmaker, declarative_base
import json

# Database URL (Modify for your setup)
DATABASE_URL = "postgresql://user:password@localhost/parking_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
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

# FastAPI App
app = FastAPI()

# Request Model for Updating Parking Spots
class ParkingUpdate(BaseModel):
    spot_number: str
    status: bool

# API to Fetch Available Parking Spots
@app.get("/get_parking")
def get_parking():
    session = SessionLocal()
    spots = session.query(ParkingSpot).all()
    session.close()
    return [{"spot_number": s.spot_number, "x": s.x, "y": s.y, "status": "vacant" if s.status else "occupied"} for s in spots]

# API to Update Parking Spot Status
@app.post("/update_parking")
def update_parking(data: ParkingUpdate):
    session = SessionLocal()
    spot = session.query(ParkingSpot).filter(ParkingSpot.spot_number == data.spot_number).first()
    
    if not spot:
        session.close()
        raise HTTPException(status_code=404, detail="Spot not found")
    
    spot.status = data.status
    spot.last_updated = func.now()
    session.commit()
    session.close()
    
    return {"message": f"Spot {data.spot_number} updated successfully"}

# Run the FastAPI server with:
# uvicorn main:app --reload --host 0.0.0.0 --port 8000