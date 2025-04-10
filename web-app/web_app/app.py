"""Flask app for uploading and processing audio interview recordings."""

import os
from flask import Flask, request, redirect, url_for, render_template, flash
from werkzeug.utils import secure_filename
from pymongo import MongoClient

# Configurations
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"wav", "webm", "mp3"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SECRET_KEY"] = "supersecretkey"
app.config["TESTING"] = False  # will be overridden during testing

# Ensure upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    """Check if the file name has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_db_collection():
    """Return the MongoDB collection to store records."""
    mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    client = MongoClient(mongo_uri)
    database = client["web_app_db"]
    collection = database["records"]
    return collection


def transcribe_audio(file_path):
    """Dummy transcription function. Replace with real transcription service if needed."""
    filename = os.path.basename(file_path)
    return f"Simulated transcription from file: {filename}"


def analyze_transcription(transcription):
    """Dummy analysis function. Replace with real analysis logic if needed."""
    return f"Analysis result: {transcription}"


@app.route("/", methods=["GET"])
def index():
    """Render the index page with interview question and recent records."""
    questions = [
        "What is your greatest strength?",
        "Where do you see yourself in five years?",
    ]
    try:
        q_index = int(request.args.get("q", 0))
    except ValueError:
        q_index = 0
    if q_index < 0 or q_index >= len(questions):
        q_index = 0
    question = questions[q_index]

    # Retrieve non-empty records from the database
    collection = get_db_collection()
    records_cursor = collection.find()
    records = [record for record in records_cursor if record.get("transcript")]

    return render_template(
        "index.html",
        question=question,
        question_index=q_index,
        total_questions=len(questions),
        records=records,
    )


UPLOAD_FOLDER = "uploads"


@app.route("/submit_audio", methods=["POST"])
def submit_audio():
    """Handle audio file uploads and store file metadata in MongoDB."""
    if "audio_file" not in request.files or request.files["audio_file"].filename == "":
        flash("No audio file found")
        return redirect(url_for("index"))
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file = request.files["audio_file"]
    if file and allowed_file(file.filename):
        try:
            question_index = int(request.form.get("question_index", 0))
        except ValueError:
            question_index = 0

        collection = get_db_collection()
        attempt_count = collection.count_documents({"question_index": question_index})
        attempt_number = attempt_count + 1

        original_ext = file.filename.rsplit(".", 1)[1].lower()
        new_filename = (
            f"question{question_index}_attempt{attempt_number}.{original_ext}"
        )
        secure_name = secure_filename(new_filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], secure_name)
        file.save(file_path)

        # Save to DB with status "pending"
        record = {
            "file_path": file_path,
            "question_index": question_index,
            "status": "pending",
        }
        collection.insert_one(record)

        flash("Audio uploaded. Processing will begin shortly.")
        return redirect(url_for("index"))

    flash("Invalid audio file format")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
