# """
# Developing...
# =============

# * module for static collection:
#     requests

# * module for dynamic collection:

# """

# from bs4 import BeautifulSoup
# import requests
# from selenium import webdriver

# # test
# # import example_google


# #basic2.rectangle_area()

# class ChineseNaver(object):
#     """This is class for Chinese character consisting of 1 letter on Naver. Busu : 1 ~ 17 strokes"""

#     def __init__(self,
#                  link: str = 'https://hanja.dict.naver.com/yp/busu/detail?',
#                  index: int = 0,
#                  order: int = 0,
#                  subindex: int = 0) -> None:
#         """Initialize link parameter to parse.

#         :param link: the link that not includes details,
#          defaults to <https://hanja.dict.naver.com/yp/busu/detail?> (order by Busu; root)
#         :type link: str, optional
#         :param index: the number of strokes of a root, defaults to 0
#         :type index: int, optional
#         :param order: one of the root in a particular index, defaults to 0
#         :type order: int, optional
#         :param subindex: the number of strokes of a chinese character, defaults to 0
#         :type subindex: int, optional
#         """

#         self.index = index
#         self.order = order
#         self.subindex = subindex
#         self.link = link + 'index=' + str(index) + '&order=' + str(
#             order) + '&subindex' + str(subindex)

#     def collect_dynamic(self) -> None:
#         """setting: chrome version: 79"""
#         index = 0
#         browser = webdriver.Chrome()
#         x = []
#         y = []

#         # real strokes = stroke value + 1   // for test range(0, 17) -> (0, 1)
#         for stroke in range(1):
#             order = 0
#             link = 'https://hanja.dict.naver.com/yp/busu/detail?index={}&order={}&subindex=0'.format(
#                 stroke, order)
#             browser.get(link)

#             elem = browser.find_elements_by_xpath(
#                 '/html/body/div[1]/div[3]/div[1]/div[2]/div')

#             x_temp = elem[0].text.split('\n')
#             length = len(x_temp)
#             x_temp[length-1] = x_temp[length-1].strip()

#             # x is Busu
#             x.append(x_temp)

#             for order in range(int(length/2)):
#                 chineseCharacter_temp = ChineseCharacter('test', 'test', '총 {}획, {}').format(stroke+1, x_temp[order*2])
                
#                 link='https://hanja.dict.naver.com/yp/busu/detail?index={}&order={}&subindex=0'.format(stroke, order)
#                 browser.get(link)

#                 elem=browser.find_elements_by_xpath(
#                     '/html/body/div[1]/div[3]/div[1]/div[3]/table/tbody')
#                 y_temp=elem[0].text.split('\n')
#                 y_temp.pop()

#                 iterator=iter(y_temp)
#                 retval=dict(zip(iterator, iterator)) 

#                 y.append([retval])
 
#         self.readChinese(x, y)

#     def readChinese(self, x: list, y: list) -> None:
#         for xx in x:
#             print(xx)

#         print('\n-------- Busu ----------\n\n\n')
#         for yy in y:
#             for yyy in yy:
#                 print(yyy)
#             print('\n------- Order -----------\n')

# # index = 0
# # browser = webdriver.Chrome()
# # x = []
# # y = []

# # order = 0
# # link = 'https://hanja.dict.naver.com/yp/busu/detail?index={}&order={}&subindex=0'.format(stroke, order)
# # browser.get(link)

# # elem = browser.find_elements_by_xpath(
# #     '/html/body/div[1]/div[3]/div[1]/div[3]/table/tbody')

# # /html/body/div[1]/div[3]/div[1]/div[3]/table/tbody/tr[1]/td[1]/a


# """python interpreter
# def collect_static(self) -> None:
#     ch = ChineseNaver()

#     req = requests.get(ch.link)
#     html = req.text()
#     status = req.status_code
#     print(status, req.ok)
#     # 200 is ok.

#     soup = BeautifulSoup(html, 'lxml')
#     print(soup.prettify())

# _temp ..만.. _ 붙이기?
# - 특정 획의 부수목록에 있는 글자의 훈음과 부수에 속하는 한자목록의 훈음이 다를 수 있음. 훈음이 아니라 글자로 판별할 것.
# - 자원은 없을수도 있으니, 해당 문자의 사전에서가 아닌 부록에서 정리할 것.
# dictionary로 만드는 것 필요한가? [한자로드(路)]에 더 잘나와있지만 없는 글자도 있고 이미지가 글에 포함되어 있어서 사용하기 껄그러움.
# - 부수에서 목록 데이터로 뽑기, 뽑고나서 각 글자링크에 접근하여 총 획수 및 형성문자 원리 및 설명 뽑기


#     iterator = iter(x_temp)
#     retval = dict(zip(iterator, iterator))

# /html/body/div[1]/div[2]/div[2]/div[6]/div[3]
# /html/body/div[1]/div[2]/div[2]/div[6]/div[4]

# index = []           # 1 ~ 17 획 (index[0] ~ index[16])
# index.append


# // python interpreter get history
# import readline
# for i in range(readline.get_current_history_length()):
#     print (readline.get_history_item(i + 1))
# """



# class ChineseCharacter(object):
#     """This is class for Chinese character object"""

#     def __init__(self,
#                  letter: str,
#                  read: str,
#                  busu: str,
#                  principle: str = "",
#                  descrption: str = "") -> None:
#         """Initialize link parameter to parse.

#         :param letter: the letter
#         :type letter: str
#         :param read: how to read this
#         :type read: str
#         :param busu: Busu
#         :type busu: str
#         :param principle: constituting principle, defaults to ""
#         :type principle: str, optional
#         :param descrption: constituting principle descrption, defaults to ""
#         :type descrption: str, optional
#         """

#         self.letter=letter
#         self.read=read
#         self.busu=busu
#         self.principle=principle
#         self.descrption=descrption

#     def write_principle(self,
#                        principle: str,
#                        descrption: str) -> None:
#         """[summary]

#         :param principle: [description]
#         :type principle: str
#         :param descrption: [description]
#         :type descrption: str
#         """
#         self.principle=principle
#         self.descrption=descrption


# def main():
#     chineseNaver=ChineseNaver()
#     chineseNaver.collect_dynamic()

# if __name__ == '__main__':
#     main()



# """
#     명세.


# """