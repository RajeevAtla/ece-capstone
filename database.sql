CREATE TABLE IF NOT EXISTS parking_spots (
        spot_id VARCHAR PRIMARY KEY,
        status TEXT CHECK (status IN ('occupied', 'empty')),
        last_updated TIMESTAMP NOT NULL)
    ;