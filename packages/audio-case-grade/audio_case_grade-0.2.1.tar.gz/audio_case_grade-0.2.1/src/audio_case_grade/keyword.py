"""Keyword algorithm module"""

import re
from typing import Optional, Tuple

from pandas import DataFrame, Series

from .keybank import get_keybank
from .types import (
    Assessments,
    Case,
    Foundations,
    Histories,
    Metrics,
    Objectives,
    Plans,
    Soap,
)


def count_keywords(text: str, keybank: list[str]) -> Optional[Metrics]:
    """Get the keyword count and other metrics for a piece of text"""

    expected = len(keybank)

    if expected == 0:
        return None

    keyword_sequence: dict[str, int] = {}
    keywords_used: list[str] = []

    count = 0
    not_found = -1

    for keyword in keybank:
        if keyword in text:
            keywords_used.append(keyword)
            count += 1
            match = re.search(keyword, text)
            keyword_sequence[keyword] = match.start() + 1 if match else not_found
        else:
            keyword_sequence[keyword] = not_found

    return Metrics(
        count=count,
        expected=expected,
        sequence=keyword_sequence,
        used=keywords_used,
    )


def _histories(text: str, keybank: Series) -> Histories:
    """Get the history metrics for a transcript"""

    cc = count_keywords(text, keybank.iloc[0])
    hpi = count_keywords(text, keybank.iloc[1])
    ros = count_keywords(text, keybank.iloc[2])
    meds = count_keywords(text, keybank.iloc[3])

    return Histories(cc=cc, hpi=hpi, ros=ros, meds=meds)


def _objectives(text: str, keybank: Series) -> Objectives:
    """Get the objectives metrics for a transcript"""

    vitals = count_keywords(text, keybank.iloc[4])
    gen = count_keywords(text, keybank.iloc[5])
    pe = count_keywords(text, keybank.iloc[6])
    dl = count_keywords(text, keybank.iloc[7])
    di = count_keywords(text, keybank.iloc[8])

    return Objectives(vitals=vitals, gen=gen, pe=pe, dl=dl, di=di)


def _assessments(text: str, keybank: Series) -> Assessments:
    """Get the assessment metrics for a transcript"""

    dx = count_keywords(text, keybank.iloc[9])
    ddx = count_keywords(text, keybank.iloc[10])

    return Assessments(dx=dx, ddx=ddx)


def _plans(text: str, keybank: Series) -> Plans:
    """Get the plan metrics for a transcript"""

    tx = count_keywords(text, keybank.iloc[11])
    consults = count_keywords(text, keybank.iloc[12])
    interventions = count_keywords(text, keybank.iloc[13])

    return Plans(tx=tx, consults=consults, interventions=interventions)


def _foundations(text: str, keybank: Series) -> Foundations:
    """Get the assessment metrics for a transcript"""

    root = count_keywords(text, keybank.iloc[14])

    return Foundations(root=root)


def _soap(
    text: str, correct_keybank: Series, wrong_keybank: Series
) -> Tuple[Soap, Soap]:
    """calculate all metrics of the SOAP note flow and return the data frames for each section"""

    correct = Soap(
        histories=_histories(text, correct_keybank),
        objectives=_objectives(text, correct_keybank),
        assessments=_assessments(text, correct_keybank),
        plans=_plans(text, correct_keybank),
        foundations=_foundations(text, correct_keybank),
    )

    wrong = Soap(
        histories=_histories(text, wrong_keybank),
        objectives=_objectives(text, wrong_keybank),
        assessments=_assessments(text, wrong_keybank),
        plans=_plans(text, wrong_keybank),
        foundations=_foundations(text, wrong_keybank),
    )

    return correct, wrong


def get_keywords(
    text: str, case: Case, keybank_override: Optional[DataFrame] = None
) -> tuple[Soap, Soap]:
    """main function for keyword algorithm, applies above functions to all student transcripts"""

    (correct_keybank, wrong_keybank) = get_keybank(case, keybank_override)
    (correct_soap, wrong_soap) = _soap(
        text,
        correct_keybank,
        wrong_keybank,
    )

    return correct_soap, wrong_soap
