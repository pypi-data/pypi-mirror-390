"""Testing for keybank module"""

import numpy as np
import pandas as pd
import pytest
from pandas import DataFrame

from audio_case_grade import Case, get_keybank, get_keybank_csv


def test_keybank():
    """Test keybank function"""

    case = Case(
        code="I42.1",
        system="Cardiopulm",
        name="concentric left ventricular hypertrophy",
    )

    correct_keybank, wrong_keybank = get_keybank(case)

    assert correct_keybank is not None
    assert wrong_keybank is not None
    assert len(correct_keybank) == 15
    assert len(wrong_keybank) == 15


def test_get_keybank_for_abbreviations():
    """Test keybank for abbreviations"""

    case = Case(
        code="K80.00",
        system="GI",
        name="acute calculus cholecystitis",
    )

    correct_keybank, wrong_keybank = get_keybank(case)

    assert correct_keybank is not None
    assert wrong_keybank is not None
    assert correct_keybank.iloc[0] == ["abdominal pain"]
    assert "elevate alkaline phosphatase" in correct_keybank.iloc[7]
    assert wrong_keybank.iloc[0] == []


def test_get_keybank_for_contamination():
    """Test to ensure the wrong keybank doesn't contain the correct keywords"""

    case = Case(
        code="I25.2",
        system="Cardiopulm",
        name="ischemic cardiomyopathy",
    )

    correct_keybank, wrong_keybank = get_keybank(case)

    assert correct_keybank is not None
    assert wrong_keybank is not None
    assert sorted(correct_keybank.iloc[1]) == sorted(
        ["short breath", "six month", "physical activity"]
    )
    assert "nyha two" in wrong_keybank.iloc[9]
    assert "nyha four" not in wrong_keybank.iloc[9]
    assert "myocarditis dilate cardiomyopathy" in wrong_keybank.iloc[9]


def test_get_keybank_for_lemmatization():
    """Test to ensure the  keybank is Cleaned"""

    case = Case(
        code="I42.5",
        system="Cardiopulm",
        name="sarcoidosis r. cardiomyopathy",
    )

    correct_keybank, wrong_keybank = get_keybank(case)

    assert correct_keybank is not None
    assert wrong_keybank is not None
    assert sorted(correct_keybank.iloc[1]) == sorted(
        ["pre syncope", "physical activity", "palpitation", "short breath", "two month"]
    )
    assert "wheeze" in sorted(correct_keybank.iloc[2])


def test_get_keybank_csv():
    """Test getting keybank csv"""

    csv = get_keybank_csv()

    assert csv is not None
    assert isinstance(csv, DataFrame)


def test_dimensions():
    """Check Dimensions of Override DataFrames"""

    with pytest.raises(ValueError):
        case = Case(
            code="I42.1",
            system="Cardiopulm",
            name="concentric left ventricular hypertrophy",
        )
        num_rows = 1
        num_cols = 15

        data = {f"col{i}": ["chest pain"] * num_rows for i in range(1, num_cols + 1)}
        df = pd.DataFrame(data)
        get_keybank(case, keybank_override=df)


def test_empty_cell():
    """Check Empty Cell Remains Empty"""
    case = Case(
        code="I42.1",
        system="Cardiopulm",
        name="concentric left ventricular hypertrophy",
    )
    csv = get_keybank_csv().replace(r"^\s*$", np.nan, regex=True)
    correct_keybank, wrong_keybank = get_keybank(case, keybank_override=csv)

    assert correct_keybank.iloc[14] == []
    assert wrong_keybank.iloc[14] == []
