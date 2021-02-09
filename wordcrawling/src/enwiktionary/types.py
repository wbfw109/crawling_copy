"""Packages required to use source.enWiktionary.parsing
"""

from enum import Enum
from typing import Dict


class EnLanguagePOS:
    """English POS (Part of Speech) category and subcategory. only class variables exist.
        reference: https://en.wiktionary.org/wiki/Wiktionary:Entry_layout#Part_of_speech
    """

    category = (
        "PartOfSpeech",
        "Morphemes",
        "SymbolsAndCharacters",
        "Phrases",
        "HanCharacters",
        "Romanization",
    )
    subCategory = {}
    subCategory["PartOfSpeech"] = (
        "Adjective",
        "Adverb",
        "Ambiposition",
        "Article",
        "Circumposition",
        "Classifier",
        "Conjunction",
        "Contraction",
        "Counter",
        "Determiner",
        "Ideophone",
        "Interjection",
        "Noun",
        "Numeral",
        "Participle",
        "Particle",
        "Postposition",
        "Preposition",
        "Pronoun",
        "Proper noun",
        "Verb",
    )
    subCategory["Morphemes"] = (
        "Circumfix",
        "Combining form",
        "Infix",
        "Interfix",
        "Prefix",
        "Root",
        "Suffix",
    )
    subCategory["SymbolsAndCharacters"] = (
        "Diacritical mark",
        "Letter",
        "Ligature",
        "Number",
        "Punctuation mark",
        "Syllable",
        "Symbol",
    )
    subCategory["Phrases"] = ("Phrase", "Proverb", "Prepositional phrase")
    subCategory["HanCharacters"] = ("Han character", "Hanzi", "Kanji", "Hanja")
    subCategory["Romanization"] = "_none"


class EnLanguageType(Enum):
    """Enum. avaliable language: English = 1, #Latin = 2
    """

    def __str__(self):
        return self.name

    English = 1
    # Latin = 2


class EnLanguageForm:
    def __init__(self) -> None:
        self.paragraph: Dict[EnLanguageType, str] = {}
        self.isAtLeastOne: bool = False
        for i in EnLanguageType:
            self.paragraph[str(i)] = []
