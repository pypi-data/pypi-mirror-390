"""Testing for types module"""

from audio_case_grade import Metrics, Transcriber, Transcript


def test_transcript_word_count():
    """Test transcript type"""

    transcript = Transcript(
        type=Transcriber.DEEPGRAM,
        raw="This is the raw text",
        clean="clean text",
    )

    assert transcript.word_count == 2


def test_metrics_word_count():
    """Test metrics word count"""

    metrics = Metrics(
        count=2,
        expected=3,
        sequence={"test": 1, "test2": 2, "test3": -1},
        used=["test", "test2"],
    )

    assert metrics.word_count == 2


def test_metrics_percentage():
    """Test metrics percentage"""

    metrics = Metrics(
        count=2,
        expected=3,
        sequence={"test": 1, "test2": 2, "test3": -1},
        used=["test", "test2"],
    )

    assert metrics.percentage == 66.67
