CREATE TABLE IF NOT EXISTS parking_spots (
    id SERIAL PRIMARY KEY,
    spot_number VARCHAR(10) UNIQUE NOT NULL,
    x FLOAT NOT NULL,
    y FLOAT NOT NULL,
    status BOOLEAN DEFAULT TRUE,  -- TRUE = Available, FALSE = Occupied
)