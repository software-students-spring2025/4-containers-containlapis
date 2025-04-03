import os
import time
from pymongo import MongoClient
def main():
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
