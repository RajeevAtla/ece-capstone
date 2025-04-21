from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime
from models import ParkingSpot  # Make sure this exists and matches DB schema

# ✅ Database connection
DATABASE_URL = "postgresql://postgres:abhiramvemuri123@localhost/parking_db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def update_parking_status_from_dict(spot_status: dict, timestamp: datetime):
    """
    Takes a dictionary of {spot_id: status} and updates the PostgreSQL DB.
    """
    session = Session()
    try:
        for spot_id, status in spot_status.items():
            stmt = insert(ParkingSpot).values(
                spot_id=spot_id,
                status=status,
                last_updated=timestamp
            ).on_conflict_do_update(
                index_elements=["spot_id"],
                set_={
                    "status": status,
                    "last_updated": timestamp
                }
            )
            session.execute(stmt)

        session.commit()
        print(f"✅ Updated DB with {len(spot_status)} parking spots")
    except Exception as e:
        session.rollback()
        print(f"❌ Error updating DB: {e}")
    finally:
        session.close()
