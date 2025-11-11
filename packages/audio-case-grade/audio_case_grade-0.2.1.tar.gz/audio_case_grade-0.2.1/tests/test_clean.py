"""Tests for the clean module."""

from pandas import DataFrame

from audio_case_grade import Transcriber, Transcript, clean, get_abbreviations_csv


def test_stop_words():
    """Test clean function - Stop Words"""

    text = "This is the raw transcript"
    transcript = Transcript(type=Transcriber.DEEPGRAM, raw=text)
    expected_cleaned_text = "This raw transcript"

    cleaned_transcript = clean(transcript)

    assert cleaned_transcript.clean == expected_cleaned_text


def test_abbrev():
    """Test clean function - Abbreviations"""

    text = "wbc jvd bnp"
    transcript = Transcript(type=Transcriber.DEEPGRAM, raw=text)
    expected_cleaned_text = (
        "white blood cell jugular venous distention b-type natriuretic peptide"
    )

    cleaned_transcript = clean(transcript)

    assert cleaned_transcript.clean == expected_cleaned_text


def test_spaces():
    """Test clean function - Spacing Issues"""

    text = "  This is the   raw transcript "
    transcript = Transcript(type=Transcriber.DEEPGRAM, raw=text)
    expected_cleaned_text = "This raw transcript"

    cleaned_transcript = clean(transcript)

    assert cleaned_transcript.clean == expected_cleaned_text


def test_lemma():
    """Test Lemmatizer"""
    text = "the quick brown foxes are jumping over the lazy dogs"
    transcript = Transcript(type=Transcriber.DEEPGRAM, raw=text)
    expected_cleaned_text = "quick brown fox jump lazy dog"

    cleaned_transcript = clean(transcript)

    assert cleaned_transcript.clean == expected_cleaned_text


def test_whisper_type():
    """Test  Whisper type"""
    text = "the quick brown foxes are jumping over the lazy dogs"
    transcript = Transcript(type=Transcriber.WHISPER, raw=text)
    expected_cleaned_text = "quick brown fox jump lazy dog"

    cleaned_transcript = clean(transcript)

    assert cleaned_transcript.clean == expected_cleaned_text


def test_get_abbreviations_csv():
    """Test getting abbreviations csv"""

    csv = get_abbreviations_csv()

    assert csv is not None
    assert isinstance(csv, DataFrame)
