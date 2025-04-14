CREATE TABLE IF NOT EXISTS parking_spots (
    id SERIAL PRIMARY KEY,
    image_id VARCHAR(50) NOT NULL,
    spot_id INTEGER NOT NULL,
    x_min FLOAT NOT NULL,
    y_min FLOAT NOT NULL,
    width FLOAT NOT NULL,
    height FLOAT NOT NULL,
    status BOOLEAN DEFAULT TRUE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (image_id, spot_id)
);
