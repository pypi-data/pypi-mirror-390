"""Testing for core module"""

import os

from audio_case_grade import Case, Transcriber, Transcript, clean, get_score, hello


def test_hello():
    """Test hello function"""

    result = hello()

    assert result == "Welcome to audio-case-grade!"


def test_score_no_density():
    """Test score function with no lexical density"""

    raw_text = "this is text"
    mock_clean_text = raw_text
    transcript = Transcript(
        type=Transcriber.DEEPGRAM, raw=raw_text, clean=mock_clean_text
    )

    case = Case(
        code="I42.1",
        system="Cardiopulm",
        name="concentric left ventricular hypertrophy",
    )
    expected_lexical_density = 0.0

    actual_score = get_score(transcript, case)

    assert actual_score.lexical_density == expected_lexical_density


def test_score_with_density():
    """Test score function with an easy to calculate lexical density"""

    raw_text = "hello world chest pain two months fatigued ago"
    mock_clean_text = raw_text
    transcript = Transcript(
        type=Transcriber.DEEPGRAM,
        raw=raw_text,
        clean=mock_clean_text,
    )
    case = Case(
        code="I42.1",
        system="Cardiopulm",
        name="concentric left ventricular hypertrophy",
    )
    expected_lexical_density = 62.5

    actual_score = get_score(transcript, case)

    assert actual_score.lexical_density == expected_lexical_density


def test_score_with_clean():
    """Test score function"""

    raw_text = "hello world chest pain two months fatigued ago"
    transcript = Transcript(type=Transcriber.DEEPGRAM, raw=raw_text)
    transcript = clean(transcript)
    case = Case(
        code="I42.1",
        system="Cardiopulm",
        name="concentric left ventricular hypertrophy",
    )
    expected_lexical_density = 62.5

    actual_score = get_score(transcript, case)

    assert actual_score.lexical_density == expected_lexical_density


def _get_transcript(trancript_type: str) -> str:
    current_directory = os.path.dirname(__file__)
    transcript_folder = os.path.join(current_directory, "sample_transcripts")

    transcript_name = trancript_type + " transcript.txt"
    transcript_path = os.path.join(transcript_folder, transcript_name)
    with open(transcript_path, "r", encoding="utf-8") as transcript_file:
        transcript = transcript_file.read()
    return transcript


def test_score_great_transcript():
    """Test score function for great transcript"""

    raw_text = _get_transcript("great")
    transcript = Transcript(type=Transcriber.DEEPGRAM, raw=raw_text)
    transcript = clean(transcript)
    case = Case(
        code="I42.1",
        system="Cardiopulm",
        name="concentric left ventricular hypertrophy",
    )
    expected_lexical_density = 47.74

    actual_score = get_score(transcript, case)

    assert actual_score.lexical_density == expected_lexical_density


def test_score_average_transcript():
    """Test score function for average transcript"""

    raw_text = _get_transcript("average")
    transcript = Transcript(type=Transcriber.DEEPGRAM, raw=raw_text)
    transcript = clean(transcript)
    case = Case(
        code="I42.1",
        system="Cardiopulm",
        name="concentric left ventricular hypertrophy",
    )
    expected_lexical_density = 38.41

    actual_score = get_score(transcript, case)

    assert actual_score.lexical_density == expected_lexical_density


def test_score_bad_transcript():
    """Test score function for bad transcript"""

    raw_text = _get_transcript("bad")
    transcript = Transcript(type=Transcriber.DEEPGRAM, raw=raw_text)
    transcript = clean(transcript)
    case = Case(
        code="I42.1",
        system="Cardiopulm",
        name="concentric left ventricular hypertrophy",
    )
    expected_lexical_density = 23.59

    actual_score = get_score(transcript, case)

    assert actual_score.lexical_density == expected_lexical_density

    assert actual_score.lexical_density == expected_lexical_density
