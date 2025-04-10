"""
This module repeatedly inserts mock data into a MongoDB collection.
"""

from datetime import datetime
import os
import time
import sounddevice as sd
import soundfile as sf
import openai
from dotenv import load_dotenv
import pymongo


def record_audio(filename: str, duration: int = 10, file_storage: int = 44100):
    """
    Record audio from the microphone and save it to a file.

    Parameters:
      filename (str): The file path to save the recording.
      duration (int): Duration of the recording in seconds.
      fs (int): Sample rate.
    """
    print("Recording audio... Speak now!")
    recording = sd.rec(
        int(duration * file_storage), samplerate=file_storage, channels=1
    )
    sd.wait()  # Wait until recording is finished
    sf.write(filename, recording, file_storage)
    print(f"Recording complete. Audio saved as {filename}")


def transcribe_audio(filename: str, model: str = "whisper-1") -> str:
    """
    Transcribe an audio file using OpenAI's transcription API.
    """
    load_dotenv()
    client = openai.OpenAI()  # Automatically reads from OPENAI_API_KEY

    with open(filename, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model=model,
            file=audio_file,
        )
    return response.text


def get_feedback_from_gpt(text: str, model: str = "gpt-4o") -> str:
    """
    Get constructive interview feedback from GPT based on provided text.

    Parameters:
      text (str): The input text (e.g., a candidate's answer to an interview question).
      model (str): The model identifier to be used (default is "gpt-4o").

    Returns:
      str: The GPT-generated feedback.
    """
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": """You are an interview coach.
                Give constructive feedback on the user's answer to a job interview question.
                Highlight strengths, suggest improvements, and be concise.""",
            },
            {"role": "user", "content": text},
        ],
        temperature=0.7,
    )

    return response.choices[0].message.content


def save_recording_to_mongodb(
    filename: str, text: str, gpt_feedback: str, duration: int = 10
):
    """
    Save metadata about the recording to MongoDB.

    Parameters:
      audio_filename (str): The filename or file path where the recording is stored.
      transcript (str): The transcript of the user's response.
      feedback (str): The feedback provided by the GPT model.
      duration (int): Duration of the recording in seconds.
    """
    load_dotenv()
    local_mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    client = pymongo.MongoClient(local_mongo_uri)
    local_database = client["web_app_db"]  # Renamed to avoid redefinition conflict
    collection = local_database["records"]

    document = {
        "timestamp": datetime.utcnow(),
        "filename": filename,
        "duration_sec": duration,
        "transcript": text,
        "feedback": gpt_feedback,
        "status": "processed",
        "model_used": {"transcription": "gpt-4o-transcribe", "feedback": "gpt-4o"},
    }

    collection.insert_one(document)
    print("Saved recording metadata to MongoDB.")


def mock_data_insertion():
    """
    Continuously insert mock data into MongoDB.
    """
    mock_mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    mock_client = pymongo.MongoClient(mock_mongo_uri)
    mock_database = mock_client["ml_database"]
    mock_collection = mock_database["ml_collection"]

    while True:
        mock = {"status": "ongoing", "message": "trial test, sending message"}
        mock_collection.insert_one(mock)
        print("Inserted mock data once into MongoDB.")
        time.sleep(5)


if __name__ == "__main__":
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    mongo_client = pymongo.MongoClient(mongo_uri)
    database = mongo_client["web_app_db"]
    records_collection = database["records"]

    while True:
        pending = records_collection.find_one({"status": "pending"})
        if pending:
            file_path = pending["file_path"]
            record_id = pending["_id"]

            print(f"Processing {file_path}...")

            try:
                transcript = transcribe_audio(file_path)
                feedback = get_feedback_from_gpt(transcript)

                records_collection.update_one(
                    {"_id": record_id},
                    {
                        "$set": {
                            "transcript": transcript,
                            "analysis": feedback,
                            "status": "processed",
                            "processed_at": datetime.utcnow(),
                        }
                    },
                )
                print("Processed and updated MongoDB.")
            except (openai.OpenAIError, pymongo.errors.PyMongoError) as e:
                print("Failed to process:", str(e))
                records_collection.update_one(
                    {"_id": record_id},
                    {"$set": {"status": "error", "error_message": str(e)}},
                )
        else:
            time.sleep(3)
