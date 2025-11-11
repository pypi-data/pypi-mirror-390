"""Tests for proficiency scale"""

from audio_case_grade import Proficiency, get_proficiency


def test_get_proficiency():
    """Test proficiency scale"""

    test_cases = [
        (100, Proficiency.ADVANCED),
        (76, Proficiency.ADVANCED),
        (75, Proficiency.ADVANCED),
        (51, Proficiency.PROFICIENT),
        (50, Proficiency.PROFICIENT),
        (49, Proficiency.AVERAGE),
        (25, Proficiency.AVERAGE),
        (0, Proficiency.LOW),
    ]

    for total_percentage, expected in test_cases:
        actual = get_proficiency(total_percentage)
        assert actual == expected, f"Failed for {total_percentage}"
