import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from server import app, SessionLocal, ParkingSpot
import json
import os

client = TestClient(app)

# Reset
@pytest.fixture(autouse=True)
def reset_database():
    db: Session = SessionLocal()
    db.query(ParkingSpot).delete()

    # Test Data
    test_spots = [
        ParkingSpot(spot_number="A1", x=10.5, y=20.3, status=True),
        ParkingSpot(spot_number="A2", x=15.2, y=25.1, status=False),
        ParkingSpot(spot_number="B1", x=12.8, y=22.7, status=True),
        ParkingSpot(spot_number="B2", x=18.4, y=30.2, status=False),
        ParkingSpot(spot_number="C1", x=14.6, y=28.9, status=True),
        ParkingSpot(spot_number="C2", x=19.1, y=35.5, status=False),
        ParkingSpot(spot_number="D1", x=11.3, y=24.6, status=True),
        ParkingSpot(spot_number="D2", x=16.7, y=27.4, status=False),
        ParkingSpot(spot_number="E1", x=13.9, y=26.8, status=True),
        ParkingSpot(spot_number="E2", x=20.0, y=32.1, status=False)
    ]

    db.add_all(test_spots)
    db.commit()
    db.close()

JSON_FILE = "ml_output.json"

def reset_json_file():
    initial_data = [
        {"spot_number": "A1", "status": True},
        {"spot_number": "A2", "status": False}
    ]
    with open(JSON_FILE, "w") as file:
        json.dump(initial_data, file, indent=4)

@pytest.fixture(autouse=True)
def setup():
    reset_json_file()

def read_json_file():
    if not os.path.exists(JSON_FILE):
        return []
    with open(JSON_FILE, "r") as file:
        return json.load(file)

# Test Case 1: GET Available Parking Spots
def test_get_parking():
    response = client.get("/get_parking")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    for spot in data:
        assert "spot_number" in spot
        assert "x" in spot
        assert "y" in spot
        assert "status" in spot
        assert spot["status"] in ["vacant", "occupied"]

# Test Case 2: POST Update Parking Spot to Occupied
def test_update_parking_to_occupied():
    response = client.post("/update_parking", json={"spot_number": "A2", "status": False})
    assert response.status_code == 200
    assert response.json() == {"message": "Spot A2 updated successfully"}

    json_data = read_json_file()
    spot = next((s for s in json_data if s["spot_number"] == "A2"), None)
    assert spot is not None
    assert spot["status"] is False

# Test Case 3: POST Update Parking Spot to Vacant
def test_update_parking_to_vacant():
    response = client.post("/update_parking", json={"spot_number": "A1", "status": True})
    assert response.status_code == 200
    assert response.json() == {"message": "Spot A1 updated successfully"}

    json_data = read_json_file()
    spot = next((s for s in json_data if s["spot_number"] == "A1"), None)
    assert spot is not None
    assert spot["status"] is True

# Test Case 4: POST Update Non-Existing Spot
def test_update_non_existing_spot():
    response = client.post("/update_parking", json={"spot_number": "Z99", "status": False})
    assert response.status_code == 404
    assert response.json() == {"detail": "Spot not found"}

    json_data = read_json_file()
    assert not any(s["spot_number"] == "Z99" for s in json_data)

def test_update_parking_missing_fields():
    response = client.post("/update_parking", json={})  
    assert response.status_code == 422
    
def test_update_parking_invalid_data():
    response = client.post("/update_parking", json={"spot_number": "A1", "status": "INVALID"})
    assert response.status_code == 422  

def test_rapid_consecutive_updates():
    for _ in range(10): 
        response = client.post("/update_parking", json={"spot_number": "A1", "status": False})
        assert response.status_code == 200