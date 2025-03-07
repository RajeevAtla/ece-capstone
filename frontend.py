from flask import Flask, render_template_string

app = Flask(__name__)

html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rutgers Parking Updates</title>
    <style>
        body {
            background-color: #B31B1B;
            color: white;
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
        }
        header {
            background-color: #990000;
            padding: 1rem;
            text-align: center;
        }
        main {
            padding: 1rem;
        }
        .section {
            background-color: white;
            color: black;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        .accordion {
            margin-top: 1rem;
        }
        .accordion-item {
            margin-bottom: 1rem;
        }
        .accordion-title {
            font-size: 1.2rem;
            font-weight: bold;
            cursor: pointer;
        }
        .accordion-content {
            margin-left: 1rem;
            display: none;
        }
        .accordion-content.active {
            display: block;
        }
        .update-btn {
            background-color: #990000;
            color: white;
            border: none;
            padding: 5px 10px;
            margin-left: 10px;
            cursor: pointer;
            border-radius: 5px;
        }
        .update-btn:hover {
            background-color: #750000;
        }
        footer {
            background-color: #990000;
            padding: 1rem;
            text-align: center;
        }
    </style>
    <script>
        function toggleContent(id) {
            const content = document.getElementById(id);
            content.classList.toggle('active');
        }
        
        function updateParkingSpots() {
            fetch("http://127.0.0.1:8000/get_parking")  // FastAPI endpoint
            .then(response => response.json())
            .then(data => {
                // Loop through the returned parking spots and update the UI
                data.spots.forEach(spot => {
                    let spotElement = document.getElementById(`lot-${spot.spot_number}`);
                    if (spotElement) {
                        spotElement.textContent = spot.status;
                    }
                });

                // Update the total parking spots count
                document.getElementById("total-spots").textContent = `Total Spots: ${data.total_spots}`;
            })
            .catch(error => {
                console.error("Error fetching parking data:", error);
                alert("Failed to fetch parking data.");
            });
        }
        
    </script>
</head>
<body>
    <header>
        <h1>Rutgers Parking Updates</h1>
    </header>
    <main>
        <div class="section">
            <h2>Current Alerts</h2>
            <p>No parking alerts at the moment. Check back later for updates!</p>
        </div>

        <div class="section">
            <h2>Lot Availability</h2>
            <button class="update-btn" onclick="updateParkingSpots()">Update All</button>
            <p id="total-spots">Total Spots: --</p> <!-- Placeholder for total count -->
            <div class="accordion">
                <!-- Busch Campus -->
                <div class="accordion-item">
                    <div class="accordion-title" onclick="toggleContent('busch-content')">Busch Campus</div>
                    <div class="accordion-content" id="busch-content">
                        <p>Lot 59: <span id="lot-59">20</span> spaces available 
                            <button class="update-btn">Update</button>
                        </p>
                        <p>Lot 67: <span id="lot-67">10</span> spaces available 
                            <button class="update-btn">Update</button>
                        </p>
                    </div>
                </div>

                <!-- Livingston Campus -->
                <div class="accordion-item">
                    <div class="accordion-title" onclick="toggleContent('livingston-content')">Livingston Campus</div>
                    <div class="accordion-content" id="livingston-content">
                        <p>Lot 105: <span id="lot-105">15</span> spaces available 
                            <button class="update-btn">Update</button>
                        </p>
                        <p>Lot 112: <span id="lot-112">5</span> spaces available 
                            <button class="update-btn">Update</button>
                        </p>
                    </div>
                </div>

                <!-- College Avenue Campus -->
                <div class="accordion-item">
                    <div class="accordion-title" onclick="toggleContent('college-ave-content')">College Avenue Campus</div>
                    <div class="accordion-content" id="college-ave-content">
                        <p>Lot 30: <span id="lot-30">Full</span> 
                            <button class="update-btn">Update</button>
                        </p>
                        <p>Lot 26: <span id="lot-26">8</span> spaces available 
                            <button class="update-btn">Update</button>
                        </p>
                    </div>
                </div>

                <!-- Cook/Douglass Campus -->
                <div class="accordion-item">
                    <div class="accordion-title" onclick="toggleContent('cook-douglass-content')">Cook/Douglass Campus</div>
                    <div class="accordion-content" id="cook-douglass-content">
                        <p>Lot 70: <span id="lot-70">12</span> spaces available 
                            <button class="update-btn">Update</button>
                        </p>
                        <p>Lot 78: <span id="lot-78">Full</span> 
                            <button class="update-btn">Update</button>
                        </p>
                    </div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>Contact Parking Services</h2>
            <p>Rutgers Parking Services is here to help with any questions or concerns.</p>
            <p>Email: <a href="mailto:parking@rutgers.edu">parking@rutgers.edu</a></p>
            <p>Phone: <a href="tel:732-932-7744">732-932-7744</a></p>
        </div>
    </main>
    <footer>
        <p>&copy; {{ year }} Rutgers University. All Rights Reserved.</p>
    </footer>
</body>
</html>
"""

@app.route('/')
def home():
    from datetime import datetime
    return render_template_string(html_template, year=datetime.now().year)

if __name__ == "__main__":
    app.run(debug=True)
