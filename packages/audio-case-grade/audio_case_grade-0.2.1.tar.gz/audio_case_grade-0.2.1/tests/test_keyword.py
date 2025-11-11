"""Testing for keyword module"""

from audio_case_grade import (
    Case,
    Transcriber,
    Transcript,
    clean,
    count_keywords,
    get_keywords,
)


def test_count_keywords():
    """Test count keywords function"""

    metrics = count_keywords(
        "This is a banana and apple test", ["banana", "apple", "kiwi"]
    )

    assert metrics is not None
    assert metrics.count == 2
    assert metrics.expected == 3
    assert metrics.sequence == {"banana": 11, "apple": 22, "kiwi": -1}
    assert metrics.used == ["banana", "apple"]


def test_get_keywords():
    """Test get keywords function Correct Terminology Count"""

    text = "hello world chest pain two months fatigued ago"
    case = Case(
        code="I42.1",
        system="Cardiopulm",
        name="concentric left ventricular hypertrophy",
    )

    correct_soap, wrong_soap = get_keywords(text, case)

    assert correct_soap is not None
    assert correct_soap.totals.count == 3
    assert correct_soap.totals.expected == 52
    assert correct_soap.totals.word_count == 5

    assert wrong_soap is not None
    assert wrong_soap.totals.count == 0
    assert wrong_soap.totals.expected == 34
    assert wrong_soap.totals.word_count == 0


def test_get_keywords_wrong():
    """Test get keywords function Wrong Terminology Count"""

    text = "hello world chest pain two weeks palpitations pre syncope"
    case = Case(
        code="I42.1",
        system="Cardiopulm",
        name="concentric left ventricular hypertrophy",
    )

    correct_soap, wrong_soap = get_keywords(text, case)

    assert correct_soap is not None
    assert correct_soap.totals.count == 1
    assert correct_soap.totals.expected == 52
    assert correct_soap.totals.word_count == 2

    assert wrong_soap is not None
    assert wrong_soap.totals.count == 3
    assert wrong_soap.totals.expected == 34
    assert wrong_soap.totals.word_count == 5


def test_get_keywords_percentage():
    """Test get keywords percentage"""

    text = "hello world chest pain two weeks palpitations pre syncope"
    case = Case(
        code="I42.1",
        system="Cardiopulm",
        name="concentric left ventricular hypertrophy",
    )

    correct_soap, wrong_soap = get_keywords(text, case)

    assert correct_soap is not None
    assert correct_soap.totals.percentage == 1.92

    assert wrong_soap is not None
    assert wrong_soap.totals.percentage == 8.82


def test_get_keywords_usage():
    """Test get keywords usage"""

    stem_hpi = " last known well time two hours incontinence"
    stem_pe = " stoke severity moderate"
    stem_dx = " cerebral infarction aca"
    stem_tx = " asa seizure precautions dvt prophylaxis"
    stem_found = " acute ischemic stroke aca symptoms"
    text = stem_hpi + stem_pe + stem_dx + stem_tx + stem_found

    transcript = Transcript(
        type=Transcriber.DEEPGRAM, raw=text, word_count=len(text.split())
    )
    clean_txt = clean(transcript)
    case = Case(
        code="I63.43",
        system="Neruo",
        name="cerebral infarction aca < 3 hrs",
    )

    correct_soap, wrong_soap = get_keywords(clean_txt.clean, case)

    assert correct_soap is not None
    assert wrong_soap is not None
    assert sorted(correct_soap.histories.hpi.used) == sorted(
        ["last know well time", "two hour", "incontinence"]
    )
    assert correct_soap.objectives.pe.used == ["stoke severity moderate"]
    assert correct_soap.assessments.dx.used == ["cerebral infarction aca"]
    assert sorted(correct_soap.plans.tx.used) == sorted(
        ["asa", "seizure precaution", "deep venous thrombosis prophylaxis"]
    )
    assert sorted(correct_soap.foundations.root.used) == sorted(
        ["acute", "ischemic stroke", "aca", "symptom"]
    )


def test_get_keywords_sequence():
    """Test get keywords Sequence"""

    stem_hpi = " last known well time two hours incontinence"
    stem_pe = " stoke severity moderate"
    stem_dx = " cerebral infarction aca"
    stem_tx = " asa seizure precautions dvt prophylaxis"
    stem_found = " acute ischemic stroke aca symptoms"
    text = stem_hpi + stem_pe + stem_dx + stem_tx + stem_found

    transcript = Transcript(
        type=Transcriber.DEEPGRAM, raw=text, word_count=len(text.split())
    )
    clean_txt = clean(transcript)
    case = Case(
        code="I63.43",
        system="Neruo",
        name="cerebral infarction aca < 3 hrs",
    )

    correct_soap, wrong_soap = get_keywords(clean_txt.clean, case)

    assert correct_soap is not None
    assert wrong_soap is not None
    assert correct_soap.histories.hpi.sequence == dict(
        {"last know well time": 1, "two hour": 21, "incontinence": 30}
    )
    assert correct_soap.objectives.pe.sequence == dict({"stoke severity moderate": 43})
    assert correct_soap.assessments.dx.sequence == dict({"cerebral infarction aca": 67})
    assert correct_soap.plans.tx.sequence == dict(
        {
            "asa": 91,
            "seizure precaution": 95,
            "deep venous thrombosis prophylaxis": 114,
            "insulin slide scale": -1,
        }
    )

    assert correct_soap.foundations.root.sequence == dict(
        {"acute": 149, "ischemic stroke": 155, "aca": 87, "symptom": 175}
    )


def test_get_keywords_soap_count():
    """Test get keywords function for SOAP"""

    def create_case() -> str:
        stem_cc = "stroke alert"
        stem_hpi = " last known well time two hours incontinence"
        stem_gen = " severe sensory loss"
        stem_pe = " stoke severity moderate"
        stem_dl = " cbc with diff no occlusion"
        stem_di = " internal carotid"
        stem_dx = " cerebral infarction aca"
        stem_tx = " asa seizure precautions dvt prophylaxis"
        stem_consult = " intensivist neurologist"
        stem_inter = " iv tpa"
        stem_found = " acute ischemic stroke aca symptoms"
        text = (
            stem_cc
            + stem_hpi
            + stem_gen
            + stem_pe
            + stem_dl
            + stem_di
            + stem_dx
            + stem_tx
            + stem_consult
            + stem_inter
            + stem_found
        )
        return text

    text = create_case()
    transcript = Transcript(
        type=Transcriber.DEEPGRAM, raw=text, word_count=len(text.split())
    )
    clean_txt = clean(transcript)
    case = Case(
        code="I63.43",
        system="Neruo",
        name="cerebral infarction aca < 3 hrs",
    )

    correct_soap, wrong_soap = get_keywords(clean_txt.clean, case)

    assert correct_soap is not None

    assert correct_soap.histories.totals.count == 4
    assert correct_soap.objectives.totals.count == 5
    assert correct_soap.assessments.totals.count == 1
    assert correct_soap.plans.totals.count == 6
    assert correct_soap.foundations.totals.count == 4

    assert correct_soap.totals.count == 20
    assert correct_soap.totals.expected == 36
    assert correct_soap.totals.word_count == 42

    assert wrong_soap is not None
    assert wrong_soap.totals.count == 0
    assert wrong_soap.totals.expected == 5
    assert wrong_soap.totals.word_count == 0
