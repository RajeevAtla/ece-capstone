import pandas as pd
from sqlalchemy import create_engine, Column, String, Text, TIMESTAMP, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import insert

# ✅ DB connection
DATABASE_URL = "postgresql://postgres:parshva123@localhost/parking_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# ✅ ORM Model (Matches new table schema)
class ParkingSpot(Base):
    __tablename__ = "parking_spots"

    spot_id = Column(String, primary_key=True)
    status = Column(Text, nullable=False)
    last_updated = Column(TIMESTAMP, nullable=False)

# ✅ Schema execution
def initialize_db():
    with engine.connect() as conn:
        with open("database.sql", "r") as file:
            sql_script = file.read()
        conn.execute(text(sql_script))
        conn.commit()
        print("✅ Database schema initialized.")

# ✅ Status Updater from Annotations CSV
def update_status_from_annotations_csv(csv_path: str):
    session = SessionLocal()
    try:
        df = pd.read_csv(csv_path)
        df['last_updated'] = pd.to_datetime(df['last_updated'])

        # Keep only the latest record per spot_id
        latest_df = df.sort_values("last_updated").drop_duplicates("spot_id", keep="last")

        for _, row in latest_df.iterrows():
            spot_id = row["spot_id"]
            status = row["status"]
            timestamp = row["last_updated"]

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
        print("✅ Parking spot statuses inserted/updated from CSV!")

    except Exception as e:
        session.rollback()
        print(f"❌ Error during status update: {e}")
    finally:
        session.close()
# ✅ Run when executed
if __name__ == "__main__":
    initialize_db()
    update_status_from_annotations_csv("parking_spots.csv")