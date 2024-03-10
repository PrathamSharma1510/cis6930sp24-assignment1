import pytest
from censoror import censor_phone_numbers, censor_document, extract_and_censor_email_names, censor_addresses_with_google_nlp
import spacy
from unittest.mock import Mock
from google.cloud import language_v1 
import os

@pytest.fixture
def mock_spacy_nlp(monkeypatch):
    class MockedDoc:
        def __init__(self, ents):
            self.ents = ents

    class MockedEntity:
        def __init__(self, text, start_char, end_char, label_):
            self.text = text
            self.start_char = start_char
            self.end_char = end_char
            self.label_ = label_   

    monkeypatch.setattr(spacy, "load")

# Parametrized test for censoring phone numbers
@pytest.mark.parametrize("input_text,expected_output", [
    ("Call me at 555-123-4567.", "Call me at ████████████."),
    ("My number is (123) 456-7890.", "My number is ██████████████."),
])
def test_censor_phone_numbers(input_text, expected_output):
    stats = {"phones": 0}
    result, stats = censor_phone_numbers(input_text, stats)
    assert result == expected_output
    assert stats["phones"] > 0

def test_censor_addresses_with_mock():
    input_text = "She lives at 123 Fake St."
    stats = {"address": 0}
    censor_flags = ["--address"]
    censored_text, stats = censor_addresses_with_google_nlp(input_text,stats)
    expected_output = "She lives at ███████████."
    assert censored_text == expected_output
    assert stats["address"] == 1

def test_extract_and_censor_email_names():
    input_text = "Contact me via john.doe@example.com."
    stats = {"names": 0}
    censored_text, stats = extract_and_censor_email_names(input_text, stats)
    expected_output = "Contact me via ████████@example.com."
    assert censored_text == expected_output
    assert stats["names"] > 0
