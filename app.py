from flask import Flask, render_template, jsonify
from sqlalchemy import create_engine
import pandas as pd

app = Flask(__name__)

DATABASE_URL = "postgresql://postgres:abhiramvemuri123@localhost/parking_db"
engine = create_engine(DATABASE_URL)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/parking_status')
def parking_status():
    with engine.connect() as conn:
        df = pd.read_sql("SELECT * FROM parking_spots", conn)

    # Map numeric IDs to visual spot names
    def map_id(row):
        sid = int(row['spot_id'].replace('spot_', ''))
        if 1 <= sid <= 10:
            return f"A-{sid}"
        elif 11 <= sid <= 20:
            return f"BL-{sid - 10}"
        elif 21 <= sid <= 30:
            return f"BR-{sid - 20}"
        elif 31 <= sid <= 40:
            return f"CL-{sid - 30}"
        elif 41 <= sid <= 50:
            return f"CR-{sid - 40}"
        elif 51 <= sid <= 60:
            return f"D-{sid - 50}"
        else:
            return f"Unknown-{sid}"

    df["mapped_id"] = df.apply(map_id, axis=1)
    df["status"] = df["status"].replace({"empty": "vacant"})

    return jsonify(df[["mapped_id", "status"]].rename(columns={"mapped_id": "spot_id"}).to_dict(orient="records"))

if __name__ == '__main__':
    app.run(debug=True)
