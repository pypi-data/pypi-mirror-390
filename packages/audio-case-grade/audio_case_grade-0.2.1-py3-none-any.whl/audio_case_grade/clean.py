"""Module for textual Cleaning/Standardization"""

import string
from importlib.resources import files
from typing import Mapping, Optional

import jiwer  # type: ignore
import pandas as pd
from pandas import DataFrame

from .language import lemmatize, load_lemmatizer, load_stop_words
from .types import Transcriber, Transcript

ABBREVIATION_COLUMN = "Abbreviation"
MEANING_COLUMN = "Meaning"

COMMON_SUBSTITUTIONS: Mapping[str, str] = {
    "1+": "one plus",
    "1 +": "one plus",
    "2 d": "2d",
    "o two": "oxygen saturation",
    "o2": "oxygen saturation",
    "mg": "milligrams",
    "x-ray": "xray",
    "x ray": "xray",
    "cr td": "crtd",
    "rails": "rales",
    "rail": "rale",
}
UNACCEPTABLE_ABBREV = ["s", "f", "b", "l", "r", "w"]


def get_abbreviations_csv() -> DataFrame:
    """Get the medical abbreviations & acronyms from the csv file"""

    resources = "audio_case_grade.resources"
    abbreviations_file = "abbreviations.csv"

    csv_path = files(resources) / abbreviations_file

    with csv_path.open("r", encoding="utf-8") as csv_file:
        return pd.read_csv(csv_file, header=0)


def _get_abbreviation_map(
    abbreviations_override: Optional[DataFrame] = None,
) -> Mapping[str, str]:
    """Convert medical abbreviation & acronyms to map"""

    acr_abb = (
        abbreviations_override
        if abbreviations_override is not None
        else get_abbreviations_csv()
    )
    abbrev_map = dict(
        zip(
            acr_abb[ABBREVIATION_COLUMN].str.lower(),
            acr_abb[MEANING_COLUMN].str.lower(),
        )
    )
    for key in UNACCEPTABLE_ABBREV:
        abbrev_map.pop(key, None)
    return abbrev_map


def _text_clean(text: str, abbrev_map: Mapping[str, str]) -> str:
    """textual cleaning and standardization"""

    translator = str.maketrans(string.punctuation, " " * len(string.punctuation))
    t = jiwer.ExpandCommonEnglishContractions()(text)
    t = jiwer.RemoveKaldiNonWords()(t)
    t = t.translate(translator)
    t = jiwer.SubstituteWords(abbrev_map)(t)
    t = jiwer.SubstituteWords(COMMON_SUBSTITUTIONS)(t)
    t = jiwer.Strip()(t)
    clean_text = jiwer.RemoveMultipleSpaces()(t)
    return clean_text


def _internal_clean(
    raw_transcript: str, abbreviations_override: Optional[DataFrame] = None
) -> str:
    """Removes stop words from presentations, applies above cleaning functions"""
    lemma = load_lemmatizer()
    stop = load_stop_words()
    abbrev_map = _get_abbreviation_map(abbreviations_override)
    cleaned_text = _text_clean(raw_transcript, abbrev_map)
    clean_list = cleaned_text.split()
    clean_stop = [word for word in clean_list if word not in stop]
    clean_lemma = [lemmatize(word, lemma) for word in clean_stop]
    return " ".join(clean_lemma)


def clean(
    transcript: Transcript, abbreviations_override: Optional[DataFrame] = None
) -> Transcript:
    """Clean up the transcript"""

    if transcript.type == Transcriber.DEEPGRAM:
        transcript.clean = _internal_clean(transcript.raw, abbreviations_override)
        return transcript

    if transcript.type == Transcriber.WHISPER:
        transcript.clean = _internal_clean(transcript.raw, abbreviations_override)
        return transcript

    return transcript
