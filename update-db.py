import csv
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, TIMESTAMP, func, text
from sqlalchemy.orm import sessionmaker, declarative_base

# ✅ DB connection
DATABASE_URL = "postgresql://postgres:abhiramvemuri123@localhost/parking_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# ✅ ORM Model
class ParkingSpot(Base):
    __tablename__ = "parking_spots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    image_id = Column(String(50), nullable=False)
    spot_id = Column(Integer, nullable=False)
    x_min = Column(Float, nullable=False)
    y_min = Column(Float, nullable=False)
    width = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    status = Column(Boolean, default=True)
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        # Enforce uniqueness on image_id + spot_id
        {'sqlite_autoincrement': True},
    )

# ✅ Schema execution
def initialize_db():
    with engine.connect() as conn:
        with open("database.sql", "r") as file:
            sql_script = file.read()
        conn.execute(text(sql_script))
        conn.commit()
        print("✅ Database schema initialized.")

# ✅ CSV Importer
def import_parking_spots_from_csv(file_path: str):
    session = SessionLocal()
    try:
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                image_id = row["image_id"]
                spot_id = int(row["spot_id"])
                x_min = float(row["x_min"])
                y_min = float(row["y_min"])
                width = float(row["width"])
                height = float(row["height"])

                # Try to find existing record
                existing = session.query(ParkingSpot).filter_by(
                    image_id=image_id, spot_id=spot_id
                ).first()

                if existing:
                    # Update existing
                    existing.x_min = x_min
                    existing.y_min = y_min
                    existing.width = width
                    existing.height = height
                    existing.status = True  # or set from ML model later
                else:
                    # Insert new
                    new_spot = ParkingSpot(
                        image_id=image_id,
                        spot_id=spot_id,
                        x_min=x_min,
                        y_min=y_min,
                        width=width,
                        height=height
                    )
                    session.add(new_spot)

        session.commit()
        print("✅ Parking spots successfully inserted/updated from CSV!")

    except Exception as e:
        session.rollback()
        print(f"❌ Error during import: {e}")
    finally:
        session.close()

# ✅ Run when script is executed
if __name__ == "__main__":
    initialize_db()
    import_parking_spots_from_csv("C:/Users/abhir/ece-capstone/parking_spots.csv")
