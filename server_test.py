import requests

API_URL = "http://localhost:8000/update_parking"

# Example data from ML Model
ml_output = [
    {"spot_number": "A1", "status": False},  # Occupied
    {"spot_number": "A2", "status": True},   # Vacant
]

for spot in ml_output:
    response = requests.post(API_URL, json=spot)
    print(response.json())