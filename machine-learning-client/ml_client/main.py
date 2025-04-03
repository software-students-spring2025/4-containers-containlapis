"""
This module repeatedly inserts mock data into a MongoDB collection.
"""
import os
import time
from pymongo import MongoClient
def main():
    """
    Connects to MongoDB using MONGO_URI (from environment or default),
    then inserts a mock document every 5 seconds.
    """
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    client = MongoClient(mongo_uri)
    db = client["ml_database"]
    collection = db["ml_collection"]

    while True:
        mock = {
            "status": "ongoing",
            "message": "trial test, sending message"
        }
        collection.insert_one(mock)
        print("Inserted mock data once into MongoDB.")
        time.sleep(5)

if __name__ == "__main__":
    main()
