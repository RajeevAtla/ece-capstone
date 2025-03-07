from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, TIMESTAMP, func, text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import json
import os
from fastapi.middleware.cors import CORSMiddleware


DATABASE_URL = "postgresql://parshvamehta:parshva123@localhost/parking_db"
engine = create_engine(DATABASE_URL)

def initialize_db():
    with engine.connect() as conn:
        with open("database.sql", "r") as file:
            sql_script = file.read()
        conn.execute(text(sql_script))
        conn.commit()

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

Base.metadata.create_all(bind=engine)


# Call Init functions
initialize_db()


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5000"],  # Flask server address
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ParkingUpdate(BaseModel):
    spot_number: str
    status: bool

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    total_spots = len(spots)  # Get total number of spots

    return {
        "total_spots": total_spots,
        "spots": [
            {
                "spot_number": s.spot_number,
                "x": s.x,
                "y": s.y,
                "status": "vacant" if s.status else "occupied"
            } 
            for s in spots
        ]
    }

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

# uvicorn server:app --reload --host 127.0.0.1 --port 8000