"""Language processing utilities."""

from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

import nltk  # type: ignore
from nltk.corpus import stopwords  # type: ignore
from nltk.stem import WordNetLemmatizer  # type: ignore

STOP_WORDS_LANGUAGE = "english"
ACCEPTABLE_STOP_WORDS = ["no", "not", "most", "some", "out", "s", "t"]
NOUN = "n"
VERB = "v"


@dataclass
class NltkResource:
    """NLTK Resource"""

    name: str
    path: str


STOPWORDS = NltkResource("stopwords", "corpora/stopwords.zip")
WORDNET = NltkResource("wordnet", "corpora/wordnet.zip")


def _get_ntlk_download_dir() -> str:
    """Retrieve the path to the prepackaged NLTK data directory."""
    resources = "audio_case_grade.resources"
    nltk_path = "nltk"

    nltk_data_path = str(files(resources) / nltk_path)
    Path(nltk_data_path).mkdir(parents=True, exist_ok=True)
    nltk.data.path.append(nltk_data_path)
    return nltk_data_path


def _ensure_nltk_resources(resource: NltkResource) -> None:
    """Ensure NLTK resources are available."""
    download_dir = _get_ntlk_download_dir()

    try:
        nltk.data.find(resource.path)
    except LookupError:
        nltk.download(resource.name, download_dir=download_dir, quiet=False)


def load_stop_words() -> list[str]:
    """Load Stop Words"""

    _ensure_nltk_resources(STOPWORDS)
    stop = stopwords.words(STOP_WORDS_LANGUAGE)
    for word in ACCEPTABLE_STOP_WORDS:
        stop.remove(word)
    return stop


def load_lemmatizer() -> WordNetLemmatizer:
    """Load Lemmatizer"""

    _ensure_nltk_resources(WORDNET)
    lemma = WordNetLemmatizer()
    return lemma


def lemmatize(word: str, lemma: WordNetLemmatizer) -> str:
    """Lemmatize a word"""

    lemma_word = lemma.lemmatize(lemma.lemmatize(word, pos=VERB), pos=NOUN)
    return lemma_word
