from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, TIMESTAMP, func, text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import json
import os

DATABASE_URL = "postgresql://parshvamehta:parshva123@localhost/parking_db"
engine = create_engine(DATABASE_URL)

def initialize_db():
    """Initialize the database by executing the SQL script."""
    with engine.connect() as conn:
        with open("database.sql", "r") as file:
            sql_script = file.read()
        conn.execute(text(sql_script))
        conn.commit()

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class ParkingSpot(Base):
    """SQLAlchemy model for parking spots."""
    __tablename__ = "parking_spots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    spot_number = Column(String(10), unique=True, nullable=False)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    status = Column(Boolean, default=True)  # True = Vacant, False = Occupied
    last_updated = Column(TIMESTAMP, server_default=func.now())

def import_parking_spots_from_json(file_path: str):
    """Reads parking spots from a JSON file and inserts them into the database."""
    # Open a database session
    session = SessionLocal()

    try:
        # Read JSON data
        with open(file_path, "r") as file:
            parking_data = json.load(file)

        # Loop through JSON and add to DB
        for spot in parking_data:
            new_spot = ParkingSpot(
                spot_number=spot["spot_number"],
                x=spot["x"],
                y=spot["y"],
                status=spot["status"]
            )
            session.add(new_spot)

        # Commit changes to the database
        session.commit()
        print("✅ Parking spots successfully added from JSON file!")

    except Exception as e:
        session.rollback()
        print(f"❌ Error importing parking spots: {e}")

    finally:
        session.close()