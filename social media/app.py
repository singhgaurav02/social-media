# app.py
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import math
import os

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

# --- Example sample data (replace with real API data later) ---
SAMPLE_USERS = [
    {"username": "alice", "followers": 1200, "likes": 340, "comments": 80, "shares": 20},
    {"username": "bob", "followers": 900,  "likes": 220, "comments": 60, "shares": 15},
    {"username": "charlie", "followers": 1500,"likes": 500, "comments": 120,"shares": 30},
    {"username": "diana", "followers": 600,  "likes": 120, "comments": 30, "shares": 5},
]

# --- Metric calculations ---
def total_engagement(user: dict) -> int:
    return (user.get("likes",0) + user.get("comments",0) + user.get("shares",0))

def engagement_rate(user: dict) -> float:
    """Engagement rate as engagement per follower (as fraction)."""
    followers = user.get("followers") or 0
    eng = total_engagement(user)
    if followers <= 0:
        return 0.0
    return eng / followers

def compute_metrics(users: list) -> list:
    # compute engagement rate for each
    for u in users:
        u["total_engagement"] = total_engagement(u)
        u["engagement_rate"] = round(engagement_rate(u), 6)

    # compute average engagement rate across users
    rates = [u["engagement_rate"] for u in users]
    avg_rate = sum(rates) / len(rates) if rates else 0.0

    # relative score = engagement_rate / avg_rate
    for u in users:
        if avg_rate == 0:
            u["relative_score"] = None
        else:
            u["relative_score"] = round(u["engagement_rate"] / avg_rate, 3)

    # add ranking by relative_score
    sorted_users = sorted(users, key=lambda x: (x["relative_score"] if x["relative_score"] is not None else 0), reverse=True)
    for idx, u in enumerate(sorted_users, start=1):
        u["rank"] = idx

    # Return users sorted by rank for predictable display
    return sorted_users

# --- API endpoint ---
@app.route("/api/metrics")
def api_metrics():
    users_copy = [dict(u) for u in SAMPLE_USERS]  # shallow copy
    computed = compute_metrics(users_copy)
    return jsonify({"data": computed})

# --- Serve frontend ---
@app.route("/")
def index():
    return send_from_directory("static", "index.html")

# Serve static (JS/CSS) handled automatically by Flask's static_folder

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
