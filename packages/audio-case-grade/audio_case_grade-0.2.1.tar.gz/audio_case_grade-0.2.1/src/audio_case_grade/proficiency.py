"""Module to get a student's proficiency"""

from .types import Proficiency


def get_proficiency(total_percentage: float) -> Proficiency:
    """Grade a student's proficiency based on lexical density"""

    if total_percentage >= 75:
        return Proficiency.ADVANCED
    if 50 <= total_percentage < 75:
        return Proficiency.PROFICIENT
    if 25 <= total_percentage < 50:
        return Proficiency.AVERAGE

    return Proficiency.LOW
