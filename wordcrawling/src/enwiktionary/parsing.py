from enwiktionary.types import EnLanguageType, EnLanguageForm, EnLanguagePOS
from lxml import etree
from typing import List, Dict, Tuple, Any, AnyStr, Pattern
from word.character import Etymology, PartOfSpeech, Pronunciation
import io
import re


class EnWiktionary:
    def __init__(self) -> None:
        self._xmlFilePath: str = ""
        self._namespace: Dict[Any, str] = {}
        self._namespaceForm: Dict[Any, str] = {}
        self._xPathForm: Dict[Any, etree.XPath] = {}
        self._reForm: Dict[Any, Pattern[AnyStr]] = {}

    def initSetting(self) -> None:
        self._reForm = {}
        self.appendReForm(
            "Language",
            re.compile(r"^(==)([A-Za-z ]+)\1", re.DOTALL | re.MULTILINE)
        )
        self.appendReForm(
            "Etymology",
            re.compile(r"^(===)(Etymology|Etymology \d)\1(((?!===).)*)", re.DOTALL | re.MULTILINE),
        )
        self.appendReForm(
            "Pronunciation",
            re.compile(r"^(===)(Pronunciation)\1(((?!===).)*)", re.DOTALL | re.MULTILINE),
        )
        self.appendReForm(
            "PartsOfSpeechType1",
            re.compile(r"^(===)([A-Za-z]+)\1", re.DOTALL | re.MULTILINE),
        )
        self.appendReForm(
            "PartsOfSpeechType2",
            re.compile(r"^(====)([A-Za-z]+)\1", re.DOTALL | re.MULTILINE),
        )

    def getPage(self, content: etree.Element) -> Dict[EnLanguageType, str]:
        """Get page from source.enWiktionary.type.EnLanguageForm instance about parsing content.

        Args:
            content (Element): each content.

        Returns:
            Dict[EnLanguageType, str]: Key that consists of EnLanguageType and Text.
        """
        # get enLanguageForm by EnLanguageForm key.
        enLanguageForm = EnLanguageForm()
        matchObjectsLanguage = self._reForm["Language"].finditer(content.text)
        isFirst = False
        signalString = ""
        for matchObject in matchObjectsLanguage:
            if matchObject is not None:
                for i in EnLanguageType:
                    if isFirst:
                        enLanguageForm.paragraph[signalString].append(
                            matchObject.start() - 1
                        )
                        isFirst = False
                    if matchObject.group(2) == str(i):
                        enLanguageForm.paragraph[str(i)].append(matchObject.end())
                        enLanguageForm.isAtLeastOne = True
                        isFirst = True
                        signalString = str(i)
                        break
        # if it encounters EOF
        if signalString != "" and len(enLanguageForm.paragraph[signalString]) == 1:
            enLanguageForm.paragraph[signalString].append(len(content.text) - 1)

        # if the key have nothing value, delete key.
        for i in EnLanguageType:
            if enLanguageForm.paragraph[str(i)] == []:
                del enLanguageForm.paragraph[str(i)]
        # get page from enLanguageForm and content. if page is nothing, return {}
        page = {}
        if enLanguageForm.isAtLeastOne:
            for key, value in enLanguageForm.paragraph.items():
                page[key] = content.text[value[0] : value[1]]
        
        return page

    def getEtymology(
        self, page: Dict[EnLanguageType, str]
    ) -> Dict[EnLanguageType, List[Etymology]]:
        """If Etymology is none, a member of Etymology instance have default value; description is "", position is ().

        Args:
            page (Dict[EnLanguageType, str]): page (Key that consists of EnLanguageType and Text).

        Returns:
            Dict[EnLanguageType, List[Etymology]]: Key that consists of EnLanguageType and list that consist of Etymology instances.
        """
        etymology = {}
        for key in page.keys():
            etymology[key] = []
            matchObjectsEtymology = self._reForm["Etymology"].finditer(page[key])

            for matchObject in matchObjectsEtymology:
                if matchObject is not None:
                    etymology[key].append(
                        Etymology(matchObject.group(3).strip(), matchObject.span())
                    )

            # if Etymology is None
            if etymology[key] == []:
                etymology[key].append(Etymology())

        return etymology

    def setPronunciation(
        self,
        page: Dict[EnLanguageType, str],
        etymology: Dict[EnLanguageType, List[Etymology]],
    ) -> None:
        """If the etymology is all different and part-of-speech is different, it have separate pronunciation Match instance. ex) desert

        But if the pronunciation is the same according to part of speech, the pronunciation is not divided. ex) present

        Args:
            page (Dict[EnLanguageType, str]): page (Key that consists of EnLanguageType and Text).
            etymology (Dict[EnLanguageType, List[Etymology]]): return value from function getEtymology.
        """
        for key in page.keys():
            matchObjectsPronunciation = self._reForm["Pronunciation"].finditer(
                page[key]
            )
            pronunciations = []
            for matchObject in matchObjectsPronunciation:
                if matchObject is not None:
                    extractedText = []
                    buffer = io.StringIO(matchObject.group(3).strip())
                    for line in buffer.readlines():
                        if line.startswith(r"* {{audio"):
                            continue
                        else:
                            extractedText.append(line)
                    pronunciations.append(
                        Pronunciation("".join(extractedText), matchObject.span())
                    )

            # if etymology[key] >= 2 and it available 1:1 matching (not N:1), all etymology.position < pronunciation.position is True.
            # if all the pronunciation are None
            if pronunciations == []:
                for value in etymology[key]:
                    value.pronunciation = Pronunciation()
            # etymology[key] is at least 1, so simple equality comparison is possible.
            elif len(etymology[key]) == len(pronunciations):
                for value, pronunciation in zip(etymology[key], pronunciations):
                    value.pronunciation = pronunciation
            # if (len(etymology[key]) >= 2 and len(pronunciations) == 1) and (etymology[key][0].position > pronunciations[0].position)
            elif (len(pronunciations) == 1) and (
                etymology[key][0].position > pronunciations[0].position
            ):
                for value in etymology[key]:
                    value.pronunciation = pronunciations[0]
            # if 1. (len(etymology[key]) >= 2 and len(pronunciations) == 1) and (etymology[key][0].position < pronunciations[0].position)
            # if 2. (len(etymology[key]) >= 3 and len(pronunciations) >= 2
            else:
                a = 1
                b = 1
                while len(etymology[key]) >= a:
                    if len(pronunciations) < b:
                        etymology[key][
                            len(etymology[key]) - a
                        ].pronunciation = Pronunciation()
                        a += 1
                    elif (
                        etymology[key][len(etymology[key]) - a].position
                        < pronunciations[len(pronunciations) - b].position
                    ):
                        etymology[key][
                            len(etymology[key]) - a
                        ].pronunciation = pronunciations[len(pronunciations) - b]
                        a += 1
                        b += 1
                    else:
                        etymology[key][
                            len(etymology[key]) - a
                        ].pronunciation = Pronunciation()
                        a += 1

    def setPartOfSpeech(
        self,
        page: Dict[EnLanguageType, str],
        etymology: Dict[EnLanguageType, List[Etymology]],
    ) -> None:
        """Allocate Part Of Speech objects into Etymology objects.

        Args:
            page (Dict[EnLanguageType, str]): page (Key that consists of EnLanguageType and Text).
            etymology (Dict[EnLanguageType, List[Etymology]]): return value from function getEtymology.
        """
        for key in page.keys():
            if len(etymology[key]) < 2:
                POSlist = []
                matchObjectsPOS = self._reForm["PartsOfSpeechType1"].finditer(page[key])
                for matchObject in matchObjectsPOS:
                    if (
                        (matchObject is not None)
                        and (matchObject.group(2) != "Pronunciation")
                        and (matchObject.group(2) != "Etymology")
                    ):
                        temp = self._getPOScategory(matchObject.group(2))
                        if temp != ("", ""):
                            POSlist.append(PartOfSpeech(temp))
                # allocate value
                etymology[key][0].partOfSpeech = POSlist
            # len(etymology[key]) >= 2
            else:
                a = 1
                matchObjectsPOS = self._reForm["PartsOfSpeechType2"].finditer(page[key])
                POSlist = []
                for i in etymology[key]:
                    POSlist.append([])

                for matchObject in matchObjectsPOS:
                    if matchObject is not None:
                        if a >= len(etymology[key]):
                            temp = self._getPOScategory(matchObject.group(2))
                            if temp != ("", ""):
                                POSlist[len(etymology[key]) - 1].append(
                                    PartOfSpeech(temp)
                                )
                        else:
                            temp = self._getPOScategory(matchObject.group(2))
                            if temp != ("", ""):
                                if matchObject.span() >= etymology[key][a].position:
                                    a += 1
                                POSlist[a - 1].append(PartOfSpeech(temp))
                # allocate value
                for value, i in zip(etymology[key], range(len(POSlist))):
                    value.partOfSpeech = POSlist[i]

    def _getPOScategory(self, POS: str) -> Tuple[str, str]:
        for category in EnLanguagePOS.category:
            for subCategory in EnLanguagePOS.subCategory[category]:
                if POS == subCategory:
                    return (category, POS)
        # if it was not found
        return ("", "")

    @property
    def xmlFilePath(self) -> str:
        return self._xmlFilePath

    @xmlFilePath.setter
    def xmlFilePath(self, xmlFilePath: str) -> None:
        self._xmlFilePath = xmlFilePath

    @property
    def namespace(self) -> Dict[Any, str]:
        return self._namespace

    @namespace.setter
    def namespace(self, namespace: Dict[Any, str]) -> None:
        self._namespace = namespace

    def appendNamespace(self, key: Any, value: str) -> None:
        self._namespace[key] = value

    def deleteNamespace(self, key: Any) -> None:
        del self._namespace[key]

    @property
    def namespaceForm(self) -> Dict[Any, str]:
        return self._namespaceForm

    @namespaceForm.setter
    def namespaceForm(self, namespaceForm: Dict[Any, str]) -> None:
        self._namespaceForm = namespaceForm

    def appendNamespaceForm(self, key: Any, value: str) -> None:
        self._namespaceForm[key] = value

    def deleteNamespaceForm(self, key: Any) -> None:
        del self._namespaceForm[key]

    @property
    def xPathForm(self) -> Dict[Any, etree.XPath]:
        return self._xPathForm

    @xPathForm.setter
    def xPathForm(self, xPathForm: Dict[Any, etree.XPath]) -> None:
        self._xPathForm = xPathForm

    def appendXPathForm(self, key: Any, value: etree.XPath) -> None:
        self._xPathForm[key] = value

    def deleteXPathForm(self, key: Any) -> None:
        del self._xPathForm[key]

    @property
    def reForm(self) -> Dict[Any, Pattern[AnyStr]]:
        """Get regular expression in form of dictionary type.

        Returns:
            Dict[Any, Pattern[AnyStr]]: keys and regular expression objects.
        """
        return self._reForm

    @reForm.setter
    def reForm(self, reForm: Dict[Any, Pattern[AnyStr]]) -> None:
        """Set regular expression in form of dictionary type.

        Args:
            reForm (Dict[Any, Pattern[AnyStr]]): dictionary type (keys : regular expression objects).
        """
        self._reForm = reForm

    def appendReForm(self, key: Any, value: Pattern[AnyStr]) -> None:
        self._reForm[key] = value

    def deleteReForm(self, key: Any) -> None:
        del self._reForm[key]