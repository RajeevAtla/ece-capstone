from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Text, TIMESTAMP

Base = declarative_base()

class ParkingSpot(Base):
    __tablename__ = "parking_spots"

    spot_id = Column(String, primary_key=True)
    status = Column(Text, nullable=False)
    last_updated = Column(TIMESTAMP, nullable=False)
