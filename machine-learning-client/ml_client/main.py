"""
This module repeatedly inserts mock data into a MongoDB collection.
"""
from datetime import datetime
import os
import time
import sounddevice as sd
import soundfile as sf
import openai
from openai import OpenAI
from dotenv import load_dotenv
from pymongo import MongoClient


def record_audio(filename: str, duration: int = 10, fs: int = 44100):
    """
    Record audio from the microphone and save it to a file.
    
    Parameters:
      filename (str): The file path to save the recording.
      duration (int): Duration of the recording in seconds.
      fs (int): Sample rate.
    """
    print("Recording audio... Speak now!")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()  # Wait until recording is finished
    sf.write(filename, recording, fs)
    print(f"Recording complete. Audio saved as {filename}")


def transcribe_audio(filename: str, model: str = "gpt-4o-transcribe") -> str:
    """
    Send the audio file to OpenAI's transcription API and get back the transcript.

    Parameters:
      filename (str): The path to the audio file.
      model (str): The model to use for transcription (e.g. "gpt-4o-transcribe" or "whisper-1").

    Returns:
      str: The transcribed text.
    """
    load_dotenv()  # Load from .env
    openai.api_key = os.getenv("OPENAI_API_KEY")

    client = OpenAI()
    with open(filename, "rb") as audio_file:
        transcription_response = client.audio.transcriptions.create(
            model=model, file=audio_file,
        )
    return transcription_response.text


def get_feedback_from_gpt(text: str, model: str = "gpt-4o") -> str:
    """
    Send the transcript to the GPT API and return feedback.

    Parameters:
      transcript (str): The user's transcribed answer.
      model (str): GPT model to use (default is "gpt-4o").

    Returns:
      str: AI-generated feedback.
    """
    client = OpenAI()

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
    # Load environment variables if not already loaded
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    client = MongoClient(mongo_uri)
    db = client["ml_database"]
    collection = db["ml_collection"]

    # Build document to store metadata
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
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    client = MongoClient(mongo_uri)
    db = client["ml_database"]
    collection = db["ml_collection"]

    while True:
        mock = {"status": "ongoing", "message": "trial test, sending message"}
        collection.insert_one(mock)
        print("Inserted mock data once into MongoDB.")
        time.sleep(5)


if __name__ == "__main__":
    # Record user response
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    audio_filename = f"response_{timestamp}.wav"
    record_audio(audio_filename, duration=10)

    # Transcribe audio
    print("Transcribing audio...")
    transcript = transcribe_audio(audio_filename)
    print("Transcript:", transcript)

    # Get feedback from GPT
    feedback = get_feedback_from_gpt(transcript)
    print("\nAI Feedback:")
    print(feedback)

    # Save the metadata (recording info, transcript, and feedback) to MongoDB
    save_recording_to_mongodb(audio_filename, transcript, feedback, duration=10)

    # mock_data_insertion()
