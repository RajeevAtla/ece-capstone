import time
import psycopg2
from tabulate import tabulate

conn = psycopg2.connect(
    dbname="parking_db",
    user="postgres",
    password="abhiramvemuri123",
    host="localhost"
)

def fetch_parking_status():
    with conn.cursor() as cur:
        cur.execute("SELECT spot_id, status, last_updated FROM parking_spots ORDER BY spot_id;")
        rows = cur.fetchall()
        print("\033c", end="")  # Clear terminal screen
        print(tabulate(rows, headers=["Spot ID", "Status", "Last Updated"], tablefmt="fancy_grid"))

if __name__ == "__main__":
    try:
        while True:
            fetch_parking_status()
            time.sleep(2)  # Refresh every 2 seconds
    except KeyboardInterrupt:
        conn.close()
        print("\n⛔ Stopped live monitoring.")
