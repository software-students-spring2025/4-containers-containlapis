"""Module tests.test_app

This module contains unit tests for the Flask web application.
It tests endpoints and helper functions using multiple approaches.
"""

import io
import pytest
from web_app.app import (
    app,
    allowed_file,
    transcribe_audio,
    analyze_transcription,
)

# pylint: disable=redefined-outer-name


class DummyCollection:
    """A dummy collection to simulate database operations for testing.

    This class provides implementations for count_documents, insert_one,
    find, and get_number_of_records for test assertions.
    """

    def __init__(self):
        self.records = []

    def count_documents(self, query):
        """Return the count of records that match the given query."""
        return sum(
            1
            for record in self.records
            if all(record.get(k) == v for k, v in query.items())
        )

    def insert_one(self, record):
        """Simulate insertion of a record."""
        self.records.append(record)

        # pylint: disable=too-few-public-methods
        class DummyResult:
            """A dummy result object to simulate the result of a DB insertion."""

            inserted_id = "dummy_id"

        return DummyResult()

    def find(self):
        """Return all records."""
        return self.records

    def get_number_of_records(self):
        """Return the number of records in the dummy collection."""
        return len(self.records)


@pytest.fixture
def client_fixture(monkeypatch):
    """Fixture providing a test client and dummy database."""
    dummy_collection = DummyCollection()
    monkeypatch.setattr("web_app.app.get_db_collection", lambda: dummy_collection)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client, dummy_collection


def test_allowed_file_valid():
    """Test that allowed_file returns True for valid extensions."""
    assert allowed_file("audio.wav")
    assert allowed_file("sound.webm")
    assert allowed_file("record.mp3")


def test_allowed_file_invalid():
    """Test that allowed_file returns False for invalid extensions."""
    assert not allowed_file("audio.txt")
    assert not allowed_file("sound.mp4")


def test_transcribe_and_analyze():
    """Test dummy transcription and analysis functions."""
    fake_path = "uploads/test.wav"
    transcription = transcribe_audio(fake_path)
    analysis = analyze_transcription(transcription)
    assert "Simulated transcription" in transcription
    assert "Analysis result" in analysis


def test_index_page(client_fixture):
    """Test that the index page loads with expected content."""
    client, _ = client_fixture
    response = client.get("/")
    assert response.status_code == 200
    content = response.data.decode("utf-8")
    assert "Interview Question:" in content
    assert "Record and submit your answer:" in content


def test_submit_audio_invalid(client_fixture):
    """Test that submitting with no audio file displays an error message."""
    client, _ = client_fixture
    response = client.post("/submit_audio", data={}, follow_redirects=True)
    assert response.status_code == 200
    content = response.data.decode("utf-8")
    assert "No audio file found" in content or "error" in content


def test_submit_audio_valid(client_fixture):
    """
    Test that a valid audio submission works correctly and that the file is
    named following the pattern "question<index>_attempt<attempt>.<ext>".
    """
    client, dummy_collection = client_fixture
    dummy_audio = io.BytesIO(b"Dummy audio content")
    dummy_audio.name = "test.wav"
    data = {"audio_file": (dummy_audio, "test.wav"), "question_index": "1"}
    response = client.post(
        "/submit_audio",
        data=data,
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert response.status_code == 200
    content = response.data.decode("utf-8")
    # Check that the flash message is rendered in the HTML
    assert "Audio submitted successfully!" in content
    assert len(dummy_collection.records) == 1
    record = dummy_collection.records[0]
    assert "question1_attempt1" in record.get("file_path", "")
    assert "Simulated transcription" in record.get("transcript", "")
    assert "Analysis result" in record.get("analysis", "")


def test_submit_audio_multiple_attempts(client_fixture):
    """
    Test that multiple submissions for the same question increment the attempt
    number correctly.
    """
    client, dummy_collection = client_fixture
    # First submission for question index 0
    audio1 = io.BytesIO(b"Content 1")
    audio1.name = "first.wav"
    data1 = {"audio_file": (audio1, "first.wav"), "question_index": "0"}
    client.post(
        "/submit_audio",
        data=data1,
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    # Second submission for the same question index
    audio2 = io.BytesIO(b"Content 2")
    audio2.name = "second.wav"
    data2 = {"audio_file": (audio2, "second.wav"), "question_index": "0"}
    client.post(
        "/submit_audio",
        data=data2,
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert len(dummy_collection.records) == 2
    first_record = dummy_collection.records[0]
    second_record = dummy_collection.records[1]
    assert "question0_attempt1" in first_record.get("file_path", "")
    assert "question0_attempt2" in second_record.get("file_path", "")
