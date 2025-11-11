"""Handle the KeyBank data"""

from importlib.resources import files
from typing import Mapping, Optional, Tuple, cast

import pandas as pd
from jiwer import (  # type: ignore
    Compose,
    RemoveMultipleSpaces,
    RemoveSpecificWords,
    Strip,
    SubstituteWords,
)
from pandas import DataFrame, Series

from .clean import _get_abbreviation_map, get_abbreviations_csv
from .language import lemmatize, load_lemmatizer, load_stop_words
from .types import Case

SEPERATOR = ","
CODE_COLUMN = "ICD10"
SYSTEM_COLUMN = "System"
CASE_COLUMNS = ["Case", CODE_COLUMN, SYSTEM_COLUMN]
EXPECTED_KEYBANK_COLS = 18
EXPECTED_ABBREV_COLS = 2


def get_keybank_csv() -> DataFrame:
    """Get the KeyBank from the csv file"""

    resources = "audio_case_grade.resources"
    keybank_file = "keybank.csv"

    csv_path = files(resources) / keybank_file

    with csv_path.open("r", encoding="utf-8") as csv_file:
        return pd.read_csv(
            csv_file,
            na_filter=False,
        )


def _check_for_dupes_keybank(
    keybank: DataFrame, ignore_error: Optional[bool] = False
) -> DataFrame:
    """Find all rows with duplicates"""

    def has_duplicates(row):
        seen = set()
        dupes = set()
        for col in keybank.columns:
            if col not in CASE_COLUMNS and isinstance(row[col], list):
                for item in row[col]:
                    if item in seen:
                        dupes.add(item)
                    else:
                        seen.add(item)
        has_dupes = len(dupes) > 0
        if has_dupes and not ignore_error:
            raise ValueError(
                f"Keybank case found with duplicate keywords: {row[CODE_COLUMN]} {dupes}"
            )
        return has_dupes

    return keybank[keybank.apply(has_duplicates, axis=1)]


def _check_for_dupes_wrong(keybank: Series) -> Series:
    """Check for Duplication in the Wrong Keybank"""
    seen = set()
    result = []

    for lst in keybank:
        new_lst = []
        for item in lst:
            if item not in seen:
                new_lst.append(item)
                seen.add(item)
        result.append(new_lst)

    return pd.Series(result, index=keybank.index)


def _clean_keybank(keybank: DataFrame, abbrev_map: Mapping[str, str]) -> DataFrame:
    stop = load_stop_words()
    lemma = load_lemmatizer()
    text_normalization = Compose(
        [
            RemoveSpecificWords(stop),
            SubstituteWords(abbrev_map),
            Strip(),
            RemoveMultipleSpaces(),
        ]
    )

    def clean_cell(cell):
        if pd.isna(cell):
            return []
        if isinstance(cell, str):
            cleaned = text_normalization(cell)
            cleaned_lemma = [
                " ".join(lemmatize(word, lemma) for word in key.split())
                for key in cleaned.split(SEPERATOR)
            ]
            return list({item.strip() for item in cleaned_lemma if item != ""})
        return []

    cleaned_keybank = keybank.copy()

    for column in cleaned_keybank.columns:
        if column not in CASE_COLUMNS:
            cleaned_keybank[column] = cleaned_keybank[column].apply(clean_cell)

    _check_for_dupes_keybank(cleaned_keybank)

    return cleaned_keybank


def _get_rows_by_code(keybank: DataFrame, case: Case) -> DataFrame:
    """Get the rows that match the case"""

    return keybank[keybank[CODE_COLUMN] == case.code]


def _get_rows_by_system(keybank: DataFrame, case: Case) -> DataFrame:
    """Get the rows that match the system but not case"""

    return keybank[keybank[SYSTEM_COLUMN] == case.system]


def _combine_rows(rows: DataFrame) -> Series:
    """Combine rows into a single row"""

    single_row_df = rows.apply(
        lambda col: list(
            {item.strip() for row in col for item in row if isinstance(row, list)}
        )
    )

    # Single row is already a series but has wrong type
    series = cast(Series, single_row_df)
    series.name = "Keywords"

    return series


def _subtract_series(s1: Series, s2: Series) -> Series:
    """Subtract the string arrays in df2 from df1."""

    return s1.combine(s2, lambda cell1, cell2: list(set(cell1) - set(cell2)))


def _check_csv_columns(csv: DataFrame, min_col) -> bool:
    if len(csv.columns) < min_col:
        raise ValueError(
            "DataFrame has incorrect dimensions. Expected Number of Columns: "
            + f"({min_col}, got {len(csv.columns)})"
        )

    return True


def get_keybank(
    case: Case,
    keybank_override: Optional[DataFrame] = None,
    abbreviations_override: Optional[DataFrame] = None,
) -> Tuple[Series, Series]:
    """Get the KeyBank"""

    keybank = get_keybank_csv() if keybank_override is None else keybank_override
    _check_csv_columns(keybank, EXPECTED_KEYBANK_COLS)
    abbrev = (
        get_abbreviations_csv()
        if abbreviations_override is None
        else abbreviations_override
    )
    _check_csv_columns(abbrev, EXPECTED_ABBREV_COLS)
    abbrev_map = _get_abbreviation_map(abbrev)

    cleaned_keybank = _clean_keybank(keybank, abbrev_map)

    correct_rows = _get_rows_by_code(cleaned_keybank, case).drop(CASE_COLUMNS, axis=1)
    correct_row = _combine_rows(correct_rows)

    wrong_rows = _get_rows_by_system(cleaned_keybank, case).drop(CASE_COLUMNS, axis=1)
    wrong_row = _combine_rows(wrong_rows)
    wrong_row_without_correct = _subtract_series(wrong_row, correct_row)
    wrong_row_without_dupes = _check_for_dupes_wrong(wrong_row_without_correct)
    return correct_row, wrong_row_without_dupes
