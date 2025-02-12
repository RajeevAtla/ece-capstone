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
            <div class="accordion">
                <div class="accordion-item">
                    <div class="accordion-title" onclick="toggleContent('busch-content')">Busch Campus</div>
                    <div class="accordion-content" id="busch-content">
                        <p>Lot 59: 20 spaces available</p>
                        <p>Lot 67: 10 spaces available</p>
                    </div>
                </div>
                <div class="accordion-item">
                    <div class="accordion-title" onclick="toggleContent('livingston-content')">Livingston Campus</div>
                    <div class="accordion-content" id="livingston-content">
                        <p>Lot 105: 15 spaces available</p>
                        <p>Lot 112: 5 spaces available</p>
                    </div>
                </div>
                <div class="accordion-item">
                    <div class="accordion-title" onclick="toggleContent('college-ave-content')">College Avenue Campus</div>
                    <div class="accordion-content" id="college-ave-content">
                        <p>Lot 30: Full</p>
                        <p>Lot 26: 8 spaces available</p>
                    </div>
                </div>
                <div class="accordion-item">
                    <div class="accordion-title" onclick="toggleContent('cook-douglass-content')">Cook/Douglass Campus</div>
                    <div class="accordion-content" id="cook-douglass-content">
                        <p>Lot 70: 12 spaces available</p>
                        <p>Lot 78: Full</p>
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
