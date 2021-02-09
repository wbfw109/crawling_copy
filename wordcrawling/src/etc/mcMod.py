from bs4 import BeautifulSoup
from urllib.request import urlopen
import json
import requests


import os
import unittest
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys


class PythonOrgSearch(unittest.TestCase):
    # https://www.curseforge.com/minecraft/mc-mods?filter-game-version=1738749986%3A68722&filter-sort=4
    def setUp(self):
        self.driver = webdriver.Chrome("rsrc\chromedriver_win32_83.0.4103.39.exe")
        self.startLink = "https://www.curseforge.com/minecraft/mc-mods?filter-game-version=1738749986:68722&filter-sort=3&page="
        self.startLinkPage = 46
        # 46 ~ 48 ?? SSL error
        self.xPathBackwardButton = "/html/body/div[3]/main/div[1]/div[2]/section/div[2]/div/div[1]/div/div[2]/div[2]/div/div[1]/a"
        self.xPathForwardButton = "/html/body/div[3]/main/div[1]/div[2]/section/div[2]/div/div[1]/div/div[2]/div[2]/div/div[2]/a"
        self.requiredXPath = [
            "/html/body/div[3]/main/div[1]/div[2]/section/div[2]/div/div[3]/div/div["
            + str(x)
            + "]/div/div[1]/div[2]/a[1]"
            for x in range(1, 21)
        ]

    def test_search_in_python_org(self):

        jsonList = []
        driver = self.driver
        driver.get(self.startLink + str(self.startLinkPage))
        # with open('result/mcModList.json', 'w+', encoding='utf-8') as fp:
        #     print("[", file=fp)

        # 중복해제..
        count = 0
        while True:
            if count == 4:
                break
            count += 1
            try:
                for item in self.requiredXPath:
                    elem = driver.find_element_by_xpath(item)
                    # ? 다중 클래스를 찾으려면 다른 구문이 필요한듯.. 바로 전달하는 것이 아니라..
                    elemChildren = elem.find_element_by_xpath("./h3")

                    jsonList.append(
                        {
                            "modName": elemChildren.text,
                            "Link": elem.get_attribute("href"),
                        }
                    )
                    # elem.clear()
                    # elemChildren.clear()

                # go to the next page
                nextElementPage = driver.find_element_by_xpath(self.xPathForwardButton)
                driver.get(nextElementPage.get_attribute("href"))
                # nextElementPage.clear()

            except NoSuchElementException:
                print(" ==== last page... exit. ==== ")
                break

        with open("result/mcModList.json", "w+", encoding="utf-8") as fp:
            json.dump(jsonList, fp, indent=4, ensure_ascii=False)

        # with open('result/mcModList.json', 'rb+') as fp:
        #     # last read byte is our truncation point, move back to it.
        #     fp.seek(-4, os.SEEK_END)
        #     fp.truncate()
        # with open('result/mcModList.json', 'a+', encoding='utf-8') as fp:
        #     print("\n]", file=fp)

        # driver.get("https://minecraft.gamepedia.com/Sweet_Berries")
        # self.assertIn("Python", driver.title)
        # assert "No results found." not in driver.page_source

    def tearDown(self):
        # You can also call quit method instead of close. The quit will exit the entire browser, whereas close will close a tab, but if it is the only tab opened, by default most browser will exit entirely.:
        self.driver.close()


if __name__ == "__main__":
    unittest.main()


"""
a = dict 형식, 중복된 키를 정의하면 이전의 키 값에 대응되는 값이 변경된다. 중복 오류가 발생하지 않음.


*json 의 Key 값을 통일해야 엑셀에서 정렬하여 불러올 수 있다.
*{Name, Total downloads, Date created, Last updated] 으로 정렬해보면 웹 페이지가 Popularity 보다 많은 것ㅇ르 알 수 있음..  전자 중 하나로 설정하고, 리스트 비교 문을 없애자..

- element clear 필요.. 속도..

#!DevTools listening on ws://127.0.0.1:8537/devtools/browser/c6d3ccdd-ecc6-4755-b4ee-955423272165
[24892:23656:0704/002311.187:ERROR:ssl_client_socket_impl.cc(959)] handshake failed; returned -1, SSL error code 1, net_error -107

The Selenium server is only required if you want to use the remote WebDriver.

The driver.get method will navigate to a page given by the URL. WebDriver will wait until the page has fully loaded (that is, the “onload” event has fired) before returning control to your test or script. It’s worth noting that if your page uses a lot of AJAX on load then WebDriver may not know when it has completely loaded.



=======================
https://www.postgresql.org/docs/current/ssl-tcp.html

PostgreSQL
F:\ProgramData\PostgreSQL\12\data\postgresql.conf


"""
