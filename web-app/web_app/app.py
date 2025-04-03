"""
This module defines a Flask app that connects to MongoDB and displays the latest record.
"""

import os
from flask import Flask, render_template
from pymongo import MongoClient

app = Flask(__name__)


@app.route("/")
def index():
    """
    Renders the index.html template with the latest record from the ml_database.
    """
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    client = MongoClient(mongo_uri)
    db = client["ml_database"]
    collection = db["ml_collection"]
    latest_record = collection.find_one(sort=[("_id", -1)])
    return render_template("index.html", data=latest_record)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
