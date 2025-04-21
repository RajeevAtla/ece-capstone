DROP TABLE IF EXISTS parking_spots;

CREATE TABLE parking_spots (
    spot_id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    last_updated TIMESTAMP NOT NULL
);
