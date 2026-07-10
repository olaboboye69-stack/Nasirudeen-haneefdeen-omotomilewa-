from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
import uuid
from datetime import datetime
from collections import Counter

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "incidents.json")

LOCATION_COORDS = {
    "Hostel": {"x": 25, "y": 65},
    "Lecture hall": {"x": 55, "y": 30},
    "Cafeteria": {"x": 70, "y": 55},
    "Car Park": {"x": 40, "y": 80},
    "Fence/Perimeter": {"x": 10, "y": 20},
    "Other": {"x": 50, "y": 50},
}


def load_incidents():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_incidents(records):
    with open(DATA_FILE, "w") as f:
        json.dump(records, f, indent=2)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/report", methods=["GET", "POST"])
def report():
    if request.method == "POST":
        location = request.form.get("location", "").strip()
        coords = LOCATION_COORDS.get(location, LOCATION_COORDS["Other"])

        record = {
            "id": str(uuid.uuid4())[:8],
            "full_name": request.form.get("full_name", "").strip(),
            "matric_no": request.form.get("matric_no", "").strip(),
            "department": request.form.get("department", "").strip(),
            "incident_type": request.form.get("incident_type", "").strip(),
            "incident_date": request.form.get("incident_date", "").strip(),
            "incident_time": request.form.get("incident_time", "").strip(),
            "location": location,
            "location_other": request.form.get("location_other", "").strip(),
            "description": request.form.get("description", "").strip(),
            "reported": request.form.get("reported", "").strip(),
            "evidence_url": "",
            "timestamp": datetime.now().strftime("%Y/%m/%d %I:%M:%S %p"),
            "map_x": coords["x"],
            "map_y": coords["y"],
        }

        records = load_incidents()
        records.append(record)
        save_incidents(records)
        return redirect(url_for("thanks"))

    return render_template("report.html")


@app.route("/thanks")
def thanks():
    return render_template("thanks.html")


@app.route("/dashboard")
def dashboard():
    records = load_incidents()

    total = len(records)
    type_counts = Counter(r["incident_type"] for r in records if r["incident_type"])
    location_counts = Counter(r["location"] for r in records if r["location"])
    reported_counts = Counter(r["reported"] for r in records if r["reported"])

    unreported = reported_counts.get("No", 0) + reported_counts.get("Not sure", 0)
    unreported_pct = round((unreported / total) * 100) if total else 0

    top_location = location_counts.most_common(1)[0][0] if location_counts else "N/A"
    top_type = type_counts.most_common(1)[0][0] if type_counts else "N/A"

    stats = {
        "total": total,
        "unreported_pct": unreported_pct,
        "top_location": top_location,
        "top_type": top_type,
        "type_counts": dict(type_counts),
        "location_counts": dict(location_counts),
        "reported_counts": dict(reported_counts),
    }

    return render_template("dashboard.html", stats=stats, records=records)


@app.route("/map")
def map_view():
    records = load_incidents()
    return render_template("map.html", records=records)


@app.route("/api/incidents")
def api_incidents():
    return jsonify(load_incidents())


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
