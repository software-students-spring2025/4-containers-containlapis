"""
Unit tests for the ml_client.main module.
"""

from unittest.mock import patch, MagicMock

import pytest

from ml_client import main


@patch("ml_client.main.sf.write")
@patch("ml_client.main.sd.wait")
@patch("ml_client.main.sd.rec")
def test_record_audio(mock_rec, mock_wait, mock_write):
    """Test that record_audio calls the audio recording functions correctly."""
    filename = "dummy.wav"
    duration = 1  # seconds
    sample_rate = 22050  # alternative sample rate for testing

    main.record_audio(filename, duration=duration, file_storage=sample_rate)

    # Verify that the recording function is called with the correct parameters.
    mock_rec.assert_called_once_with(
        int(duration * sample_rate), samplerate=sample_rate, channels=1
    )
    mock_wait.assert_called_once()
    mock_write.assert_called_once_with(filename, mock_rec.return_value, sample_rate)


@patch("builtins.open", create=True)
@patch("openai.OpenAI")
def test_transcribe_audio(mock_openai, mock_file_open):
    """Test that transcribe_audio returns the expected transcript text."""
    mock_instance = MagicMock()
    mock_openai.return_value = mock_instance

    # Set up the file context management.
    mock_ctx = MagicMock()
    mock_file_open.return_value.__enter__.return_value = mock_ctx

    fake_response = MagicMock()
    fake_response.text = "Test Transcript"
    mock_instance.audio.transcriptions.create.return_value = fake_response

    transcript = main.transcribe_audio("dummy.wav")
    assert transcript == "Test Transcript"


@patch("openai.OpenAI")
def test_get_feedback_from_gpt(mock_openai):
    """Test that get_feedback_from_gpt returns the expected feedback text."""
    mock_instance = MagicMock()
    mock_openai.return_value = mock_instance

    # Create a fake choice with a message having a 'content' attribute.
    fake_choice = MagicMock()
    fake_choice.message = MagicMock(content="Feedback text")
    fake_response = MagicMock()
    fake_response.choices = [fake_choice]
    mock_instance.chat.completions.create.return_value = fake_response

    feedback = main.get_feedback_from_gpt("Some candidate answer")
    assert "Feedback text" in feedback


@patch("pymongo.MongoClient")
def test_save_recording_to_mongodb(mock_mongo_client):
    """Test that save_recording_to_mongodb constructs and inserts the document correctly."""
    fake_collection = MagicMock()
    # Create a fake database that returns the fake collection when "records" is looked up.
    fake_database = {"records": fake_collection}
    mock_client_instance = MagicMock()
    mock_client_instance.__getitem__.return_value = fake_database
    mock_mongo_client.return_value = mock_client_instance

    filename = "dummy.wav"
    transcript = "Dummy transcript"
    feedback = "Dummy feedback"
    duration = 5

    main.save_recording_to_mongodb(filename, transcript, feedback, duration)

    fake_collection.insert_one.assert_called_once()
    args, _ = fake_collection.insert_one.call_args
    inserted_doc = args[0]
    assert inserted_doc["filename"] == filename
    assert inserted_doc["transcript"] == transcript
    assert inserted_doc["feedback"] == feedback
    assert inserted_doc["duration_sec"] == duration
    assert "timestamp" in inserted_doc
    assert "status" in inserted_doc
    assert "model_used" in inserted_doc


@patch("time.sleep", side_effect=StopIteration)
@patch("pymongo.MongoClient")
def test_mock_data_insertion(mock_mongo_client, _mock_sleep):
    """Test that mock_data_insertion correctly inserts a document into MongoDB."""
    fake_collection = MagicMock()
    # Define a fake database for key "ml_database" that contains "ml_collection".
    fake_db = {"ml_collection": fake_collection}

    mock_client_instance = MagicMock()
    mock_client_instance.__getitem__.side_effect = lambda name: (
        fake_db if name == "ml_database" else None
    )
    mock_mongo_client.return_value = mock_client_instance

    with pytest.raises(StopIteration):
        main.mock_data_insertion()

    fake_collection.insert_one.assert_called_once()
