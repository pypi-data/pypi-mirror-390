"""Type definitions to support core"""

# pylint: disable=too-few-public-methods

from enum import Enum
from typing import Dict, List, Optional, cast, get_type_hints

from pydantic import BaseModel


class Proficiency(Enum):
    """Proficiency Enum"""

    ADVANCED = "Advanced"
    PROFICIENT = "Proficient"
    AVERAGE = "Average"
    LOW = "Low"


class Transcriber(str, Enum):
    """Enum for transcriber"""

    WHISPER = "OpenAI Whisper"
    DEEPGRAM = "Deepgram Voice Agent"


class Transcript(BaseModel):
    """Type definition for a transcript"""

    type: Transcriber
    raw: str
    clean: str = ""

    @property
    def word_count(self) -> int:
        """Word count of the clean transcript"""
        return len(self.clean.split())


class Case(BaseModel):
    """ "Type definition for a case"""

    code: str
    """ICD-10 code"""

    system: str
    """Body System"""

    name: str


class Metrics(BaseModel):
    """Type definition for metrics"""

    count: int
    """Actual amount of keywords used"""

    expected: int
    """Expected keyword count based on the keybank"""

    sequence: Dict[str, int]
    """Sequence of keywords used"""

    used: List[str]
    """List of keywords used"""

    @property
    def word_count(self) -> int:
        """Word count of keywords used, keywords may contain multiple words"""

        used = " ".join(self.used)
        return len(used.split())

    @property
    def percentage(self) -> float:
        """Percentage of keywords used"""

        return round((self.count / self.expected), 4) * 100


class Totals(BaseModel):
    """Type definition for totals"""

    count: int
    """Actual amount of keywords used"""

    expected: int
    """Expected keyword count based on the keybank"""

    word_count: int
    """Word count of keywords used, keywords may contain multiple words"""

    @property
    def percentage(self) -> float:
        """Percentage of keywords used"""

        return round((self.count / self.expected), 4) * 100


class TotalsRollupMixIn:
    """Mix-in class to calculate totals for all properties of type Metrics."""

    def calculate_totals(self) -> Totals:
        """Calculate totals for all properties of type Metrics."""
        total_count = 0
        total_expected = 0
        total_word_count = 0

        # Iterate over all attributes of the class
        for name, field_type in get_type_hints(type(self)).items():
            if field_type in (Optional[Metrics], Metrics):
                value = getattr(self, name)
                if value and value is not None:
                    metrics = cast(Metrics, value)
                    total_count += metrics.count
                    total_expected += metrics.expected
                    total_word_count += metrics.word_count

        return Totals(
            count=total_count,
            expected=total_expected,
            word_count=total_word_count,
        )


class Histories(BaseModel, TotalsRollupMixIn):
    """Type definition for histories"""

    cc: Optional[Metrics] = None
    """Cardinal Complaint"""
    hpi: Optional[Metrics] = None
    """History of Present Illness"""
    ros: Optional[Metrics] = None
    """Review of System"""
    meds: Optional[Metrics] = None
    """Medications"""

    @property
    def totals(self) -> Totals:
        """Totals for the histories"""
        return self.calculate_totals()


class Objectives(BaseModel, TotalsRollupMixIn):
    """Type definition for objectives"""

    vitals: Optional[Metrics] = None
    """Vital Signs"""
    gen: Optional[Metrics] = None
    """General Appearance"""
    pe: Optional[Metrics] = None
    """Physical Exam"""
    dl: Optional[Metrics] = None
    """Diagnostic Labs"""
    di: Optional[Metrics] = None
    """Diagnostic Imaging"""

    @property
    def totals(self) -> Totals:
        """Totals for the objectives"""
        return self.calculate_totals()


class Assessments(BaseModel, TotalsRollupMixIn):
    """ "Type definition for assessments"""

    dx: Optional[Metrics] = None
    """Diagnosis"""
    ddx: Optional[Metrics] = None
    """Differentials"""

    @property
    def totals(self) -> Totals:
        """Totals for the assessments"""
        return self.calculate_totals()


class Plans(BaseModel, TotalsRollupMixIn):
    """Type definition for plans"""

    tx: Optional[Metrics] = None
    """Treatment"""
    consults: Optional[Metrics] = None
    """Physician and Specialty Consultations"""
    interventions: Optional[Metrics] = None
    """Surgeries and Special Procedures"""

    @property
    def totals(self) -> Totals:
        """Totals for the plans"""
        return self.calculate_totals()


class Foundations(BaseModel, TotalsRollupMixIn):
    """Type definition for foundations"""

    root: Optional[Metrics] = None
    """Foundation"""

    @property
    def totals(self) -> Totals:
        """Totals for the foundations"""
        return self.calculate_totals()


class Soap(BaseModel):
    """Type definition for Subjective Objective Assessment Plan (SOAP)"""

    histories: Histories
    objectives: Objectives
    assessments: Assessments
    plans: Plans
    foundations: Foundations

    @property
    def totals(self) -> Totals:
        """Totals for the SOAP"""
        components_totals = [
            self.histories.totals,
            self.objectives.totals,
            self.assessments.totals,
            self.plans.totals,
            self.foundations.totals,
        ]

        total_count = sum(t.count for t in components_totals)
        total_expected = sum(t.expected for t in components_totals)
        total_word_count = sum(t.word_count for t in components_totals)

        return Totals(
            count=total_count, expected=total_expected, word_count=total_word_count
        )


class Score(BaseModel):
    """Type definition for a score"""

    lexical_density: float
    correct: Soap
    """Correct Medical Terminology"""
    wrong: Soap
    """Wrong Medical Terminology"""
