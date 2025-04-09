import os
import pytest
from unittest.mock import patch, MagicMock
from ml_client import main

@patch("ml_client.main.sd.rec")
@patch("ml_client.main.sd.wait")
@patch("ml_client.main.sf.write")
def test_record_audio(mock_write, mock_wait, mock_rec):
    main.record_audio("test.wav", duration=1)
    mock_rec.assert_called()
    mock_wait.assert_called()
    mock_write.assert_called()

@patch("ml_client.main.OpenAI")
@patch("builtins.open", create=True)
def test_transcribe_audio(mock_open, mock_openai):
    mock_file = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file
    client_instance = mock_openai.return_value
    client_instance.audio.transcriptions.create.return_value.text = "Test Transcript"
    result = main.transcribe_audio("fake.wav")
    assert result == "Test Transcript"

@patch("ml_client.main.OpenAI")
def test_get_feedback_from_gpt(mock_openai):
    mock_choice = MagicMock()
    mock_choice.message.content = "Feedback text"
    mock_openai.return_value.chat.completions.create.return_value.choices = [mock_choice]
    response = main.get_feedback_from_gpt("text")
    assert "Feedback" in response
