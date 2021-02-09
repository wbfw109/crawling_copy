from bs4 import BeautifulSoup
from urllib.request import urlopen
import json
import requests
import re
import time
import itertools


import os
import unittest
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class PythonOrgSearch(unittest.TestCase):
    # https://bloons.fandom.com/wiki/Bloons_Tower_Defense_6
    def setUp(self):
        capabilities = DesiredCapabilities.CHROME.copy()
        capabilities["pageLoadStrategy"] = "normal"
        options = webdriver.ChromeOptions()
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        self.driver = webdriver.Chrome(
            "rsrc\chromedriver_win32_83.0.4103.39.exe",
            options=options,
            desired_capabilities=capabilities,
        )
        self.startLink = "https://bloons.fandom.com/wiki/Bloons_Tower_Defense_6"
        self.reHeroSubtype = re.compile(r"\(([A-Za-z ]+)\)")
        self.rePrice = re.compile(r"(\$[\d,]+) ?\(Hard\)")
        self.reMap = re.compile(r"(.*): (.*)", re.DOTALL)
        self.reValueFromPrice = re.compile(r"\$(\d+),?(\d*).*")
        self.xPathMonkeys = {
            "Primary": "/html/body/div[3]/section/div[2]/article/div/div[2]/div[2]/table[2]/tbody",
            "Military": "/html/body/div[3]/section/div[2]/article/div/div[2]/div[2]/table[3]/tbody",
            "Magic": "/html/body/div[3]/section/div[2]/article/div/div[2]/div[2]/table[4]/tbody",
            "Support": "/html/body/div[3]/section/div[2]/article/div/div[2]/div[2]/table[5]/tbody",
        }
        self.xPathHeroes = (
            "/html/body/div[3]/section/div[2]/article/div/div[2]/div[2]/ol"
        )
        self.xPathHeroPrice = "/html/body/div[3]/section/div[2]/article/div/div[1]/div[2]/aside/section[1]/div[3]/div"
        self.xPathMonkeysAppearances = "/html/body/div[3]/section/div[2]/article/div/div[1]/div[2]/aside/section/div[1]/div"
        self.xPathMonkeysNextBtd6 = "../following-sibling::div[@data-source='cost']/div"
        self.xPathMonkeysNextH3 = "../../../following-sibling::h3/following-sibling::*[self::div or self::table[@class='article-table']]"
        self.xPathMonkeysNextH3Rest = "following-sibling::h3/following-sibling::*[self::div or self::table[@class='article-table']]"
        self.xPathMonkeysInDiv = (
            "./div[@class='table-scrollable']/table[@class='article-table']/tbody"
        )
        self.xPathMonkeysInTable = "./tbody"
        self.xPathH2 = (
            "/html/body/div[3]/section/div[2]/article/div/div[2]/div[2]/h2/span[1]"
        )
        self.difficulty = ["Beginner", "Intermediate", "Advanced", "Expert"]
        self.statistics = [
            "Damage",
            "Pierce",
            "Attack Speed",
            "Range",
            "Status Effects",
            "Tower Boosts",
            "Income/Life Boosts",
            "Camo?",
        ]

    def _getPossiblePaths(self) -> set:
        sumListPaths = [
            [x for x in range(000, 600, 100)],
            [x for x in range(00, 60, 10)],
            [x for x in range(0, 6, 1)],
        ]
        possiblePathIndex = list(itertools.permutations([x for x in range(3)], 2))
        possiblePaths = set()
        for idx in possiblePathIndex:
            for a in sumListPaths[idx[0]]:
                for b in [x for x, _ in zip(sumListPaths[idx[1]], range(3))]:
                    possiblePaths.add(str(a + b).zfill(3))
        return possiblePaths

    def _getMonkeyPaths(self, element: WebElement, data: dict, jsonList: list):
        elemPathsTemp = [element.find_element_by_xpath(self.xPathMonkeysNextH3)]
        elemPaths = []
        for _ in range(2):
            elemPathsTemp.append(
                elemPathsTemp[len(elemPathsTemp) - 1].find_element_by_xpath(
                    self.xPathMonkeysNextH3Rest
                )
            )
        for elemPath in elemPathsTemp:
            if elemPath.tag_name == "div":
                elemPaths.append(elemPath.find_element_by_xpath(self.xPathMonkeysInDiv))
            else:
                # if elemPath.tag_name == "table":
                elemPaths.append(
                    elemPath.find_element_by_xpath(self.xPathMonkeysInTable)
                )

        for idx, elemPath in enumerate(elemPaths):
            elems = elemPath.find_elements_by_xpath("./tr/td[1]/p/b/a")
            elemsPrice = elemPath.find_elements_by_xpath("./tr/td[4]")
            for count, elem, elemPrice in zip(range(1, 6), elems, elemsPrice):
                jsonList.append(
                    {
                        "Type": "Monkey",
                        "SubType": data["SubType"],
                        "Name": data["Name"],
                        "UpgradedName": elem.get_attribute("title"),
                        "Path": str(10 ** (2 - idx) * count).zfill(3),
                        "Price (Hard)": elemPrice.text,
                        "Link": elem.get_attribute("href"),
                    }
                )

    def _getPriceHard(self, element: WebElement, data: dict):
        data["Price (Hard)"] = (
            self.rePrice.search(element.text.splitlines()[2]).group(1).replace(",", "")
        )

    def _getStatistics(self, element: WebElement, data: dict):
        elemAbility = element.find_element_by_xpath(
            "../following-sibling::div[@data-source='abilities']"
        )
        data[
            elemAbility.find_element_by_xpath("./h3").text
        ] = elemAbility.find_element_by_xpath("./div").text

        # add all key to mark not existing key
        for key in self.statistics:
            data[key] = ""

        elem = element.find_element_by_xpath(
            "/html/body/div[3]/section/div[2]/article/div/div[1]/div[2]/aside/section[2]"
        )
        elem.click()
        elemValues = elem.find_elements_by_xpath("./div")
        for elemValue in elemValues:
            data[
                elemValue.find_element_by_xpath("./h3").text
            ] = elemValue.find_element_by_xpath("./div").text

    def _getDecimalFromPrice(self, fromString: str) -> int:
        t = self.reValueFromPrice.search(fromString)
        return int(t.group(1) + t.group(2))

    def getMaps(self, chromeWebdriver: WebDriver):
        jsonMaps = []
        elemMaps = []
        elems = chromeWebdriver.find_elements_by_xpath(self.xPathH2)

        for elem in elems:
            if elem.text == "Maps":
                elemMaps.append(elem.find_element_by_xpath("../following-sibling::ul"))

                for _ in range(3):
                    elemMaps.append(
                        elemMaps[len(elemMaps) - 1].find_element_by_xpath(
                            "following-sibling::ul"
                        )
                    )

                for difficultyIndex, difficulty, elemMap in zip(
                    itertools.count(1), self.difficulty, elemMaps
                ):
                    mapFragments = elemMap.find_elements_by_xpath("./li")
                    for mapIndex, mapFragment in zip(
                        itertools.count(len(mapFragments), -1), mapFragments
                    ):
                        mapLink = mapFragment.find_element_by_xpath("./a")
                        mapText = self.reMap.search(mapFragment.text)
                        jsonMaps.append(
                            {
                                "Type": "Maps",
                                "Difficulty": str(difficultyIndex) + ": " + difficulty,
                                "MapIndex": str(mapIndex).zfill(2),
                                "Name": mapText.group(1),
                                "Description": mapText.group(2),
                                "Link": mapLink.get_attribute("href"),
                            }
                        )
                break

        with open("result/btd6Maps.json", "w+", encoding="utf-8") as fp:
            json.dump(jsonMaps, fp, indent=4, ensure_ascii=False)

    def getMonkey000(self, chromeWebdriver: WebDriver):
        jsonMonkeys = []
        jsonMonkeysPaths = []
        for key, value in self.xPathMonkeys.items():
            elem = chromeWebdriver.find_element_by_xpath(value)
            elemChildren = elem.find_elements_by_xpath("./tr/td/a[2]")
            for el in elemChildren:
                jsonMonkeys.append(
                    {
                        "Type": "Monkey",
                        "SubType": key,
                        "Name": el.get_attribute("title"),
                        "UpgradedName": el.get_attribute("title"),
                        "Path": "000",
                        "Price (Hard)": "",
                        "Link": el.get_attribute("href"),
                    }
                )

        for monkey in jsonMonkeys:
            chromeWebdriver.get(monkey["Link"])
            elems = chromeWebdriver.find_elements_by_xpath(self.xPathMonkeysAppearances)
            # to find BTD6 table
            elems.reverse()
            for elem in elems:
                elemBtd6 = elem.find_element_by_xpath(self.xPathMonkeysNextBtd6)
                self._getPriceHard(elemBtd6, monkey)
                self._getMonkeyPaths(elemBtd6, monkey, jsonMonkeysPaths)
                break

        with open("result/btd6Monkeys.json", "w+", encoding="utf-8") as fp:
            json.dump(jsonMonkeys, fp, indent=4, ensure_ascii=False)
        with open("result/btd6MonkeysPaths.json", "w+", encoding="utf-8") as fp:
            json.dump(jsonMonkeysPaths, fp, indent=4, ensure_ascii=False)

    def setUpdateMonkeysPathNotUpdated(self):
        with open("result/btd6MonkeysPaths.json", "r") as btd6MonkeysPaths:
            monkeyPaths = json.load(btd6MonkeysPaths)
            notUpdatedList = [
                ["Boomerang Monkey", "004", "$2,160"],
                ["Heli Pilot", "004", "$9,180"],
                ["Wizard Monkey", "400", "$11,770"],
                ["Monkey Sub", "030", "$1,510"],
                ["Monkey Sub", "500", "$34,560"],
                ["Engineer", "400", "$2,700"],
            ]
            for monkeyPath in monkeyPaths:
                if notUpdatedList:
                    for notUpdateMonkey in notUpdatedList:
                        if (
                            monkeyPath["Name"] == notUpdateMonkey[0]
                            and monkeyPath["Path"] == notUpdateMonkey[1]
                        ):
                            monkeyPath["Price (Hard)"] = notUpdateMonkey[2]
                            break
                else:
                    break

        with open("result/btd6MonkeysPaths.json", "w", encoding="utf-8") as fp:
            json.dump(monkeyPaths, fp, indent=4, ensure_ascii=False)

    def getMonkeySumPricefromResult(self):
        with open("result/btd6Monkeys.json", "r") as btd6Monkeys, open(
            "result/btd6MonkeysPaths.json"
        ) as btd6MonkeysPaths:
            monkey000 = json.load(btd6Monkeys)
            monkeyPaths = json.load(btd6MonkeysPaths)
            jsonMonkeysSumPrice = []
            # because itertools.islice is exhausted, so list(<  >) function is required.
            possiblePaths = list(itertools.islice(self._getPossiblePaths(), 0, None))
            print(possiblePaths)
            exit()
            _PathTypesMaxIndex = 2
            for defaultMonkey in monkey000:
                # add defaultMonkey to json with path of "000"
                defaultMonkeyPrice = self._getDecimalFromPrice(
                    defaultMonkey["Price (Hard)"]
                )

                oneMonkeysCache = {
                    x["Path"]: self._getDecimalFromPrice(x["Price (Hard)"])
                    for x in monkeyPaths
                    if x["Name"] == defaultMonkey["Name"]
                }

                # add other paths from defaultMonkey to json
                for path in possiblePaths:
                    # sum paths price
                    stepPaths = []
                    individualPaths = [
                        int(path[i]) * 10 ** (_PathTypesMaxIndex - i)
                        for i in range(_PathTypesMaxIndex + 1)
                    ]
                    for individualPath, index in zip(
                        individualPaths, itertools.count(2, -1)
                    ):
                        tempInt = individualPath
                        while individualPath > 0:
                            stepPaths.append(str(individualPath).zfill(3))
                            individualPath -= 10 ** index

                    jsonMonkeysSumPrice.append(
                        {
                            "Type": "Monkey",
                            "SubType": defaultMonkey["SubType"],
                            "Name": defaultMonkey["Name"],
                            "Path": path,
                            "Price (Hard)": defaultMonkeyPrice
                            + sum(
                                [oneMonkeysCache[stepPath] for stepPath in stepPaths]
                            ),
                        }
                    )

            with open("result/btd6MonkeysSumPrice.json", "w+", encoding="utf-8") as fp:
                json.dump(jsonMonkeysSumPrice, fp, indent=4, ensure_ascii=False)

    def getHeroes(self, chromeWebdriver: WebDriver):
        jsonHeroes = []
        elem = chromeWebdriver.find_element_by_xpath(self.xPathHeroes)
        elemChildren = elem.find_elements_by_xpath("./li")

        for el in elemChildren:
            e = el.find_element_by_xpath("./a")
            jsonHeroes.append(
                {
                    "Type": "Hero",
                    "SubType": self.reHeroSubtype.search(el.text.splitlines()[0]).group(
                        1
                    ),
                    "Name": e.get_attribute("title"),
                    "UpgradedName": "",
                    "Path": "",
                    "Price (Hard)": "",
                    "Link": e.get_attribute("href"),
                }
            )

        for hero in jsonHeroes:
            chromeWebdriver.get(hero["Link"])
            elem = chromeWebdriver.find_element_by_xpath(self.xPathHeroPrice)
            self._getPriceHard(elem, hero)
            self._getStatistics(elem, hero)

        with open("result/btd6Heroes.json", "w+", encoding="utf-8") as fp:
            json.dump(jsonHeroes, fp, indent=4, ensure_ascii=False)

    def test_search_in_python_org(self):
        # https://bloons.fandom.com/wiki/Druid#Bloons_Tower_Defense_6, https://bloons.fandom.com/wiki/Alchemist#Bloons_Tower_Defense_6
        # driver = self.driver
        # driver.implicitly_wait(10)
        # driver.get(self.startLink)

        # self.getMaps(driver)
        # self.getMonkey000(driver)
        # self.setUpdateMonkeysPathNotUpdated()
        # self.getHeroes(driver)
        self.getMonkeySumPricefromResult()

    def tearDown(self):
        self.driver.close()


if __name__ == "__main__":
    unittest.main()

"""

.. 표기형식이 랜덤.. 그냥 표에 있는 값을 추출하고, 업데이트 내역을 보고 바꾸자..
2019년 10월 24일꺼까지 반영됬음. 노멀에 1.08배가 하드 비용이고 끝자리는 버림?반올림?.
    Boomerang Monkey
        xx4 MOAB Press price increased from $1,800 -> $2,000      -> 2160
    Heli Pilot
        xx4 Comanche Defense price reduced from $10,000 -> $8,500    ->  9180
    Wizard Monkey
        4xx Arcane Spike price increased from $10,000 -> $10,900     -> 11770
    Monkey Sub
        x3x Ballistic Missile price reduced from $1,500 -> 1,400     -> 1510
    Monkey Sub 500 $32,000                                           -> 34560
    Engineer
        4xx Sentry Expert price reduced from $2800 to $2500          -> 2700

ToDo: bloons type 도 크롤링?, 엑셀 특정 문자만 색 변경? 매크로?
B.A.D.
    Parent of
        two Z.O.M.G.s and three D.D.T.s
Ceramic Bloon
    Parent of
        2 Rainbow Bloons
    Child of
        M.O.A.B. (which spawns 4 Ceramics)
        D.D.T. (which spawn 6 (BMC) or 4 (BTD6) Camo Regen Ceramics)
Rainbow Bloon
    Parent of
        Zebra Bloon x2 (BTD4-BTD6)
    Child of
        Ceramic Bloon (BTD3-BTD6)
Zebra Bloon
    Characteristics
        Immune to explosions and freezing
    Parent of
        1 Black Bloon and 1 White Bloon
    Child of
        Rainbow Bloon (which spawns 2 Zebra Bloons)
Black Bloon
    Characteristics
        Immune to explosions
    Parent of
        2 Pink Bloons (BTD 4-6)
    Child of
        Zebra Bloon (BTD 4-6)
        Lead Bloon (BTD 2-6)
White Bloon
    Characteristics
        Immune to freezing
    Parent of
        Pink Bloon x2 (BTD4-BTD6)
    Child of
        Zebra Bloon (BTD4-BTD6)

===== Special =====
Lead Bloon
    Characteristics
        Immune to sharp objects
    Parent of
        Black Bloon x2
    Child of
        None (BTD2 - BTD6)
Purple Bloon
    Characteristics
        Immune to Energy, Fire, and Plasma Attacks
    Parent of
        Pink Bloon x2
    Child of
        None


<Primary Towers>
    Boomerang Monkey
        Recommendation
            - 024*2?, 420*x??

    Ice monkey
        Recommendation
            - 002, 200  ->
                [203 ->  205, 
                320  ->  520
                    with {Primary Expertise
                    , Bloontonium Reactor
                    , fast firing towers
                        : Super Monkeys (Dark Knights, Dark Champions,the Legend of the Night), etc.
                    , multiple projectiles towers
                        : Triple Shot Dart Monkeys, Airburst Dart Monkey Subs, or Grape Shot Buccaneers with Double Shot, etc.
                    }
                ]
            ?and x3x* ?
            - x3x needs when to expand land on maps where there are bad land spots, particularly Peninsula and Spice Islands.
        - 300; Ice Shards
            *Comboing Ice Shards plus Bloontonium Reactor makes a great combo to maximize shard production.
            Ice Shards can only be sent out if the Frozen Bloons are popped by another tower other than itself, since its ice blasts are incapable of damaging Frozen Bloons on its own without Re-Freeze and attacks at a slower rate than the freeze duration
        - 400; Embrittlement
            *this upgrade allows the Ice Monkey to detect camo as well as strip off camo and regrow properties from bloons that are hit by its freeze attack.
            Embrittlement is not reliable enough camo detection against Round 47, with spaced Camo Pinks, because of its relatively slow attack speed and limited range.
        - 500; Super Brittle
            *M.O.A.B. Class Bloons are not frozen in place, but still take additional damage for up to 3 seconds and are permanently slowed down by 25% (via the Permafrost effect to MOAB-class)
            Due to the fact that it is still a 'Primary' tower, it can be buffed by Primary Training, Primary Mentoring and Primary Expertise to improve its small range.
            As its damage boost is additive rather than multiplicative, 
                fast firing towers benefit hugely. Super Monkeys especially, Dark Knights, Dark Champions and the Legend of the Night, can annihilate most tougher M.O.A.B-Class Bloons. Towers that fire multiple projectiles and also benefit, such as Triple Shot Dart Monkeys, Airburst Dart Monkey Subs, or Grape Shot Buccaneers with Double Shot.
        - 030; Arctic Wind
            Slows down bloons in range by 50%, does not affect frozen-immune.
        - 003; Cyro Cannon
            If using Cryo Cannon as purely a stalling tower, a 1-0-3 or 2-0-3 Cryo Cannon set on Strong may be the best option to go for, and can be useful for ensuring that all Ceramics that spawn on Round 63 become affected by Permafrost effect.
        - 004; Icicle
            The icicles that form on bloons are considered sharp, allowing the popping of White Bloons and Zebra Bloons but not Lead Bloons.
            As such, it is good to combo Icicles with a tower that deals a lot of MOAB damage but struggles against bloons, such as Arcane Spike or Dark Knight.
        - 005; Icicle Impale
            It's usually better to invest in 0-2-5 Ice Monkey over a 2-0-5 Ice Monkey, as although it can't directly damage lead bloons or detect camo bloons (both apply for DDTs) without support from other towers, it can provide a very valuable slowing effect on MOAB-class Bloons, especially in stages containing large numbers of MOAB-class bloons, meaning it's best to have a faster attack speed to catch fast MOAB-class bloons like DDTs than being able to directly damage Lead bloons and DDTs.

    Glue Gunner
        Recommendation
            - 013 (023)


<Magic Towers>
    Ninja Monkey
        Recommendation
            ?- {50x, x05} ?
            ?- 030 (131)*x  ->  x32*y?
                {50x, x05} 가 없으면 과도하게 설치하지 말자.


<Military Towers>
    Monkey Sniper
        Recommendation
            - 402, 024

    Monkey Sub
        Recommendation
            - 402, 
        - 400; Bloontonium Reactor
            A submerged Bloontonium Reactor can decamo an infinite amount of bloons per decamo pulse. However, the radioactive attack itself only has a base pierce of 70. This can be increased to 84 with the Barbed Darts upgrade.
            Submerging a Bloontonium Reactor has a very quick decamo pulse rate; it decamos bloons in range every 0.3 seconds, enough to decamo virtually any bloon passing by. When combined with Path 3 cross-pathing, not only will this increase the decamo pulse rate, it will also increase the radioactive attack with it.


            Submerge and Support
                When selected, it stops firing darts, however, it starts removing camo from Bloons in its range, including DDTs (both BMCM and BTD6). The decamo effect has infinite pierce, but only applies every 0.3 seconds. In BTD5 generation games, the target settings must be changed manually to use the "Submerge" option, though in BTD6 it automatically changes to "Submerge" targeting upon upgrading.
            Sub Commander is able to beat Round 63 on its own on most maps, provided it or other towers can pop Lead Bloons.


    Monkey Ace
        Recommendation
            - if camo detection does not required itself,
            ?    203  ->  204, 401?*2  ->  501?
              else,
            ?    , 023  ->  024, 420?*2  ->  520?

    Heli Pilot
        Recommendation 
            - if camo detection does not required itself,
                {[204 (104)
                    -> 205 with Hero: Pat or Gwendolin and Monkey: Super Brittle (if granted ice popping ability by Gwendolin or MIB), Glue Strike.
                    ]
                , [302  ->  402  ->  502
                    with {for destroying DDT: Monkey Intelligence Bureau, Bloon Sabotage, MOAB Glue and Overclock
                        , for destorying Super Ceramics: The Bloon Solver, Sun Avatar, The Biggest One
                        ?, Shattering Shells?
                    ],
                ?, 230*x??
                }
        - 400 Apache Dartship
            Apache Dartship is usually used as a stepping stone up to the extremely power Apache Prime. It usually will solo midgame but it is good to be wary since it begins to lose traction following Round 60. It is very important to manage support and costs so you can afford Apache Prime in time as the Dartship tends to grow weaker nearing the 80s.
        - 500; Apache Prime
            *Features
                - The plasma machine gun cannot pop purples, the rockets cannot pop blacks, but the laser attack can pop all bloons.
                - Its shortcomings are usually dampened by adding support towers. Its largest weakness on paper is in fact DDTs, which its rockets do not damage, along with the inability to fully use its decent pierce due to the tendency of DDTs to be spaced and fast. These issues are usually solved with the addition of support. Its largest weakness in practice is affording it, as Apache Dartship can struggle against many mid-late rounds on harder maps and without a properly planned strategy.
                    - Monkey Intelligence Bureau, Bloon Sabotage, MOAB Glue and Overclock all help the Apache Prime overcome this weakness. In addition, the latter three upgrades can also be useful to help on non-DDT rounds where the Apache Prime just does not have enough time to kill the bloons on certain tracks.
                    - The Bloon Solver, Sun Avatar, The Biggest One are great options for complementary towers as they all are specifically very good at destroying Super Ceramics.
                        Do be careful as their price may make them hard to afford.
                    - Cheap superceramic support options include Glue Hose and its upgrades, 0-1-2 Ice Monkeys, Downdraft, and The Big One.
                    - Shattering Shells makes fortified superceramics much easier to deal with.
        - 003; MOAB Shove
            The MOAB Shove will shove MOAB-class bloons in different ways, dependent on the bloon types along with the quantities of the MOAB-class bloons crammed near the Heli Pilot.
                - MOABs - Single MOABs will be pushed back substantially by a single MOAB Shove Heli Pilot. Single MOAB Shove Heli Pilots can only handle a certain number of MOABs before MOABs push through that Heli Pilot.
                - BFBs - Single BFBs will be stalled at the current spot if the Heli Pilot is locked in place. Single MOAB Shove Heli Pilots can only handle a certain number of BFBs before the BFBs push through that Heli Pilot.
                - ZOMGs - Single ZOMGs will be only slowed down.
                - DDTs - Cannot be pushed without camo detection. Massively slows it down otherwise.
            Having multiple MOAB Shoves will not change the amount of knockback inflicted on the same blimp. However, more blimps can be stalled at once if there is more than one MOAB Shove on screen.
            MOABs have a few seconds immunity to MOAB Shove after entering the map, and after coming out of their parents
        - 004; Comanche Defense
            The Comanche Defense is only powerful when the smaller Comanche helicopters are around
        - 005; Comanche Commander
            *Features
                - Transition from Tier 4 UpgradeEdit
                    In spite of Comanche Commander being close to $20k cheaper to afford, its Tier 4 upgrade (Comanche Defense) is highly underpowered for its price, even when backed up by its regular sets of incoming mini-Comanches. Conversely, Apache Dartship is able to solo up to the early 80s, which excluding Impoppable prices with no farming, allows Apache Prime to be easily afforded if planned properly.
                - Projectiles vs DamageEdit
                   Due to the nature of Comanche being inherently weak, it also heavily relies on a hero to buff itself. This is restricted to Pat or Gwendolin. On the other hand, Apache is much more flexible, being able to choose almost any hero depending on your strategy.
                - Comanche has become recognised as a borderline usable tower due to its synergy with Gwendolin or Pat Fusty. Also, the mini helis are directly benefited by Super Brittle (if granted ice popping ability by Gwendolin or MIB) and Glue Strike.
                - It is much more valuable in the long-run to give the Comanche Commander camo detection with a Radar Scanner and upgrade the Comanche Commander to 2/0/5 than it is to purchase simply 0/2/5, as the faster moving from Bigger Jets is not nearly as useful as the extra 2 darts fired by the mini-helicopters granted by Quad Darts.
                - The main helicopter is not much stronger than an x-x-2 helicopter in terms of damage, and as such the mini-helis form the majority of the tower's total damage output. As of update 12.0, the mini-helicopters can no longer inherit Alchemist or Overclock buffs of any form, including from Permanent Brew or Ultraboost.



520 - 420 = 10

============ 세트 =============
- Quincy, Gwendolin, Striker Jones, Obyn Greenfoot all have a levelling speed ratio of 1x (max 20 in CHIMPS). Captain Churchill and Adora have a 1.8x levelling speed ratio, meaning they take 1.8x as much XP to level up (max ?? in CHIMPS). Benjamin has a levelling speed of 1.5x, and Ezili (max ?? in CHIMPS), Pat Fusty and Admiral Brickell have a 1.425x levelling speed (max 17 in CHIMPS). 
- x; Benjamin, Ezili, Adora
<Quincy> // 일부 맵에서만 유용; Muddy Puddles, ???
<Obyn Greenfoot> 마법 타워 중
 {Wizard Monkey, Super Monkey, Ninja Monkey, Druid} 가 주 딜러라면
<Striker Jones> 1차 타워 중 {Bomb Shooter}, 군사 타워 중 {Mortar Monkey} 가 주 딜러라면
<Admiral Brickell> 군사 타워 중 해상 타워인 {Monkey Sub, Monkey Buccaneer} 가 주 딜러라면
<Gwendolin, Pat Fusty> 군사 타워 중 Heli Pilot 205
?팻 퍼스티? 그웬돌린
? <Captain Chur chill>: He is a very expensive hero, but he is useful against MOAB-class bloons later on in the game, especially with Armor Piercing Shells ability and the MOAB Barrage ability. Churchill cannot pop DDTs without abilities, so be wary if you use Churchill as your main defense against MOAB-class bloons. He is somewhat map specific as he is best used on maps with straight lines to shoot down so he can maximise the amount of explosions from each of his shots.                         ...// with Sniper Monkey, Monkey Ace, Heli Pilot ?


!나중에 쿨타임 사용하는 원숭이들 추가 비교..

*MOAB 대항용 몽키, Non-MOAB 대항용 몽키 나눠서 세트 만들기. 캐모 재생 강화 세라믹 100개 거리1 기준으로 1자지형에서 테스트.
[세트]
펫 퍼스티; 글루 024, 아이스 520, 아이스 024, 아이스 031, 연금술사 023, 스파이크 240*2, 원숭이 마을 502, 원숭이 마을 032

?닌자 402, 204 + (1)030 *x, 연금술사 402, 원숭이 마을 2개 ; -> 오빈
브릭켈 제독; 잠수함 400 -> 402 -> 502, 잠수함 205, 잠수함 024*4, 얼음 03x*6, 닌자 030 * 2
    20레벨 브릭켈 지뢰 한방에 BAD 터짐.. DDT와 다수의 풍선만 대비하면될듯.
; 플로토니움 402 *4, Ice 402*2, ice 032, 마을 402, 연금술사 402*2, 글루 사수 024*1


https://bloons.fandom.com/wiki/Rainbow_Bloon

https://stackoverflow.com/questions/46322165/dont-wait-for-a-page-to-load-using-selenium-in-python
???

https://stackoverflow.com/questions/59873157/opening-multiple-chrome-browser-and-multiple-tabs-in-single-browser-is-same
    Open Multiple Tabs in one browser will speed down your program, As webdriver will work only in one tab and then will move to the second tab. can't work simultaneously. its same as to reduce the number of URLs.
https://stackoverflow.com/questions/43429788/python-selenium-finds-h1-element-but-returns-empty-text-string/43430097
    text property allow you to get text from only visible elements while textContent attribute also allow to get text of hidden one

https://stackoverflow.com/questions/37883759/errorssl-client-socket-openssl-cc1158-handshake-failed-with-chromedriver-chr

selenium clear() 는 text 를 clear 하는 것.. 메모리가 아닌듯 ㅇ;

명시적으로 XPath 의 각 요소의 index 를 표시하지 않으면 전체를 찾는다.
??? unittest vs pytest

(wordcrawling) PS O:\repositories\crawling\wordcrawling> python -u "o:\repositories\crawling\wordcrawling\src\etc\btd6.py"   
o:\repositories\crawling\wordcrawling\src\etc\btd6.py:21: DeprecationWarning: use options instead of chrome_options
  self.driver = webdriver.Chrome("rsrc\chromedriver_win32_83.0.4103.39.exe", chrome_options=options)


개별 페이지는 업데이트가 거의 즉시 반영되지만 표에 넣어진 전체를 다루는 값은 갱신이 매우 느리다... 최소 2주..~ ?? 언제 되지

capabilities = DesiredCapabilities.CHROME.copy() 로 해결안됨..
https://selenium-python.readthedocs.io/waits.html

"""
