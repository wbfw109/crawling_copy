"""Character class and internal objects in Character class for Parsing word.

Structure

    1. Character class have "word", "language type", "etymology" property. "etymology" property is list that consists of Etymology instances.

    2. Etymology class have "description", "position", "pronunciation", "partOfSpeech" property. "pronunciation" property is str; Pronunciation instance. "partOfSpeech" property is list that consists of PartOfSpeech instances.

    3-1. Pronunciation class have "description", "position" property
    3-2. PartOfSpeech class have "categoryAndSubcategory" property. This type is tuple; (category, subcategory)

Default language of Character class is 'English'. There are characters class for different languages. These classes inherit from Character class.
"""
from typing import List, Tuple


class PartOfSpeech:
    """POS; Part Of Speech.
    """

    def __init__(self, categoryAndSubcategory: Tuple[str, str]) -> None:
        self._categoryAndSubcategory: Tuple[str, str] = categoryAndSubcategory

    @property
    def categoryAndSubcategory(self) -> Tuple[str, str]:
        """Get POS categoryAndSubcategory from enWiktionary.type.EnLanguagePOS class variable 'category' and 'subCategory'. refer to that package.

        Returns:
            tuple: (category, subCategory)
        """
        return self._categoryAndSubcategory

    @categoryAndSubcategory.setter
    def categoryAndSubcategory(self, categoryAndSubcategory: Tuple[str, str]) -> None:
        self._categoryAndSubcategory = categoryAndSubcategory


class Pronunciation:
    def __init__(self, description: str = "", position: Tuple[int, int] = ()) -> None:
        self._description: str = description
        self._position: Tuple[int, int] = position

    @property
    def description(self) -> str:
        """Get a Character pronunciation.

        Returns:
            str: ex) "어ː원", "ごげん", "/ˌɛt.ɪˈmɑl.ə.dʒi/"
        """
        return self._description

    @description.setter
    def description(self, description: str) -> None:
        self._description = description

    @property
    def position(self) -> Tuple[int, int]:
        return self._position

    @position.setter
    def position(self, position: Tuple[int, int]) -> None:
        self._position = position


class Etymology:
    def __init__(self, description: str = "", position: Tuple[int, int] = ()) -> None:
        self._description: str = description
        self._position: Tuple[int, int] = position
        self._pronunciation: Pronunciation = None
        self._partOfSpeech: List[PartOfSpeech] = []

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, description: str) -> None:
        self._description = description

    @property
    def position(self) -> Tuple[int, int]:
        return self._position

    @position.setter
    def position(self, position: Tuple[int, int]) -> None:
        self._position = position

    @property
    def pronunciation(self) -> Pronunciation:
        return self._pronunciation

    @pronunciation.setter
    def pronunciation(self, pronunciation: Pronunciation) -> None:
        self._pronunciation = pronunciation

    @property
    def partOfSpeech(self) -> List[PartOfSpeech]:
        return self._partOfSpeech

    @partOfSpeech.setter
    def partOfSpeech(self, partOfSpeech: List[PartOfSpeech]) -> None:
        self._partOfSpeech = partOfSpeech

    def appendPartOfSpeech(self, partOfSpeech: PartOfSpeech) -> None:
        self._partOfSpeech.append(partOfSpeech)

    def popPartOfSpeech(self, index: int) -> PartOfSpeech:
        return self._partOfSpeech.pop(index)


class Character:
    """Default language value is 'English'.
    """

    def __init__(self, word: str, language: str, etymology: List[Etymology]) -> None:
        self._word: str = word
        self._language: str = language
        self._etymology: List[Etymology] = etymology

    @property
    def word(self) -> str:
        """Get a Character word.

        Returns:
            str: ex) '각', '가감', 'hello', '氣', '添加'
        """
        return self._word

    @word.setter
    def word(self, word: str) -> None:
        self._word = word

    @property
    def language(self) -> str:
        """Get a Character language.
    
        Returns:
            str: ex) 'English', 'Latin'
        """
        return self._language

    @language.setter
    def language(self, language: str) -> None:
        self._language = language

    @property
    def etymology(self) -> List[Etymology]:
        """Get a Character etymology.

        Returns:
            List[Etymology]: Etymology instances
        """
        return self._etymology

    @etymology.setter
    def etymology(self, etymology: List[Etymology]) -> None:
        self._etymology = etymology

    def appendEtymology(self, etymology: Etymology) -> None:
        self._etymology.append(etymology)

    def popEtymology(self, index: int) -> Etymology:
        return self._etymology.pop(index)


class ChineseCharacter(Character):
    def __init__(self) -> None:
        super().__init__()
        self._hundok: list = ""
        self._umdok: list = ""

    @property
    def hundok(self) -> str:
        """Get Character hundok.

        Returns:
            hundok: list
        """
        return self._hundok

    @hundok.setter
    def hundok(self, hundok: list) -> None:
        """Set a Character hundok.

        Args:
            hundok (list): .
        """
        self._hundok = hundok

    def appendHundok(self, hundok: str) -> None:
        self._hundok.append(hundok)

    def popHundok(self) -> str:
        self._hundok.pop()

    @property
    def umdok(self) -> str:
        """Get Character umdok.

        Returns:
            umdok: list
        """
        return self._umdok

    @umdok.setter
    def umdok(self, umdok: list) -> None:
        """Set a Character umdok.

        Args:
            umdok (list): .
        """
        self._umdok = umdok

    def appendUmdok(self, umdok: str) -> None:
        self._umdok.append(umdok)

    def popUmdok(self) -> str:
        self._umdok.pop()
