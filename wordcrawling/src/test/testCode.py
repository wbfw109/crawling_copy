from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from lxml import etree
from multiprocessing import Pool, TimeoutError, Queue, Process
from enwiktionary.parsing import *
import os
import queue
import time
import json
from codecs import encode

def fast_iter(context, func):
    for event, elem in context:
        func(elem)
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
    del context

def serialize(elem):
    # Output a new tree like:
    # <SimplerRecord>
    #   <Title>This title</Title>
    #   <Copyright><Date>date</Date><Id>id</Id></Copyright>
    # </SimplerRecord>
     
    # Create a new root node
    r = etree.Element('SimplerRecord')
 
    # Create a new child
    t = etree.SubElement(r, 'Title')
 
    # Set this child's text attribute to the original text contents of <Title>
    t.text = elem.iterchildren(tag='Title').next().text
 
    return r



def extractPage():
    ns = 'http://www.mediawiki.org/xml/export-0.10/'
    nsKey = f'{{{ns}}}'
    nsMap = {'enWiktionary': ns}
    print('asdf')
    for _, elem in etree.iterparse('resource/enwiktionary_demo1.xml', tag=(nsKey+'page')):
        title = elem.iterchildren(tag=nsKey+'title').__next__()
        content = context(elem)
        print(title.text)
        if content:
            print(content[0].text[:1])

        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
    



if __name__ == '__main__':
    startTime = time.time()
    enWiktionary = EnWiktionary()
    enWiktionary.xmlFilePath = 'rsrc/enwiktionary_demo2.xml'
    enWiktionary.appendNamespace('enWiktionary', 'http://www.mediawiki.org/xml/export-0.10/')
    enWiktionary.appendNamespaceForm('page', f"{{{enWiktionary.namespace['enWiktionary']}}}page")
    enWiktionary.appendXPathForm('title', etree.XPath("enWiktionary:title", namespaces=enWiktionary.namespace))
    enWiktionary.appendXPathForm('text', etree.XPath("enWiktionary:revision/enWiktionary:text", namespaces=enWiktionary.namespace))
    enWiktionary.initSetting()

    characterList = []
    for _, elem in etree.iterparse(enWiktionary.xmlFilePath, tag=enWiktionary.namespaceForm['page']):
        title = enWiktionary.xPathForm['title'](elem)
        text = enWiktionary.xPathForm['text'](elem)
        page = enWiktionary.getPage(text[0])
        if page != {}:
            etymology = enWiktionary.getEtymology(page)
            enWiktionary.setPronunciation(page, etymology)
            enWiktionary.setPartOfSpeech(page, etymology)
            for key, etyList in etymology.items():
                for index, ety in enumerate(etyList):
                    characterList.append({
                        "title": title[0].text,
                        "language": key,
                        "etymologyIndex": index+1,
                        "pronunciation": ety.pronunciation.description,
                        "category": ", \n".join(["-".join(objects.categoryAndSubcategory) for objects in ety.partOfSpeech])
                    })
        # It's safe to call clear() here because no descendants will be accessed
        elem.clear()
        # Also eliminate now-empty references from the root node to <Title> 
        while elem.getprevious() is not None:
            del elem.getparent()[0]

    with open('result/enWiktionary.json', 'w+', encoding='utf-8') as fp:
        json.dump(characterList, fp, indent=2, ensure_ascii=False)


    print(time.time()-startTime)


# pro = Process(target=extractPage, args=(contents))
# pro.start()
# pro.join()


# What is intel compatible process? Intel-Compatible Processors (AMD and Cyrix) Several companies—mainly AMD and Cyrix—
"""
Python processes on multiple cores  brings the expected additional performance, but those do not share memory so you need inter proces communication (IPC) to have processes work together (you can use multiprocessing in a pool, they sync when the work is done but mostly useful for (not to) small tasks that are finite). Sharing memory is required I would assume as every task is working on the same big XML. LXML however has some way to work around the GIL but it only improves performance under certain conditions.
)
"""

###* serialize, write 함수를 나눈다.
## contains.. Xpath 3.1 에 없는데.. contains() function XPath 뭐로 바뀌었는지 찾아보기..?

# def extractPage(pageQueue: Queue, isEndQueue: Queue) -> bool:
#     print('asdf')
#     for _, element in etree.iterparse('resource/enwiktionary_demo2.xml', tag= (nsKey + 'page')):
#         pageQueue.put(element.tag)
#         isEndQueue.put(True)



"""
*A with statement does not create a scope

[multiprocessing] main count 만큼 읽어들이기, 하나의  프로세스에서  생성
    1. 파일을 분리해서 그냥 parser로 읽어들이기
        [장점]
        - 필요한 파일만 로드하여 메모리를 적게 먹음.
        [단점]
        - 파일이 새로 생성되며 매우 많아짐
    or
    2. 범위를 나눠서 처리하는 것이 우선인데 파일을  페이지 단위로 읽어서 동기 queueA 에 전달하여 쓰레드로 읽기 (((A)))
    2-1. 페이지 객체를 얻어서 전달 및 분석

    2-1. page 수가 countA 가 될 때까지 listA[str] 에 저장
        - listA[str] 의 수가 일정 값이 될 때마다 프로세스에 분배하고 시작.
            각 프로세스에서 listB 를 선언하고 이 곳에 값을 저장
        [장점] 1번보다 더 일반화되어있는 방식
        

(((A)))
    File operations are blocking. There is no non-blocking mode.
    But you can create a thread which reads the file in the background. In Python 3,
        https://stackoverflow.com/questions/39948588/non-blocking-file-read/39948796


Pool 을 사용할까 



Todo: MemorizationOfDegree 추가
////
Todo: 노래 가사 파싱 + 파일에 넣기. flag 로 뺄건 빼고.
Todo: 사운드 중 특정 사람의 목소리만 출력

Open the command palette with View > Command Palette... (or Shift+Cmd+P on OS X)
Type reload window and press enter


*[Learning in processing]
★ multiprocessing vs multithreading vs asyncio
    https://stackoverflow.com/questions/27435284/multiprocessing-vs-multithreading-vs-asyncio-in-python-3-4
    CPU Bound => Multi Processing
        Parsing text files is CPU bound
            https://lemire.me/blog/2008/12/08/parsing-text-files-is-cpu-bound/
            https://en.wikipedia.org/wiki/CPU-bound
    I/O Bound, Fast I/O, Limited Number of Connections => Multi Threading.
        Python have GIL (Global Interpreter Lock), so Multi Processing is to be preferred than Multi Threading.
    I/O Bound, Slow I/O, Many connections => Asyncio
★ Blocking-NonBlocking-Synchronous-Asynchronous
    https://homoefficio.github.io/2017/02/19/Blocking-NonBlocking-Synchronous-Asynchronous/
- parsing
    - Pattern.findall, Pattern.finditer 은 바로 아래의 자식태그만 찾을 수 있다.
    - Pattern.match, Pattern.search 는 발견된 첫번째 값만 찾는다 (?)
    - None 객체 반환하려하면 오류발생하니 처리할 것.
- multiprocessing
    - 프로세스 생성자 안에 있는 특정 함수의 인수에 객체는 맵핑할 수 없다.
        EOFError: Ran out of input inside a class
        TypeError: cannot pickle 'generator' object
    - what is join() in Multiprocess/Threading
        http://pertinency.blogspot.com/2019/10/join.html
    - exchanging-objects-between-processes
        https://docs.python.org/3/library/multiprocessing.html#exchanging-objects-between-processes
    //// https://zzaebok.github.io/python/python-multiprocessing/
        You would rather end up using Pool when there are relatively less number of task. vs Process
    //// https://docs.python.org/3/library/multiprocessing.html#pipes-and-queues
- 클래스 종류 알아내기
    <~>__class__


*[Code snippet]
- str is immutable object
    - 리스트를 첫 글자 대문자로 만들기
    ========================================
    from source.enWiktionary.types import *

    count = 0
    for i in enLanguagePartOfSpeechType:
        enLanguagePartOfSpeechType[count] = i[0].upper() + i[1:]
        count += 1

    print(enLanguagePartOfSpeechType)
    ========================================

* words

https://github.com/formulahendry/vscode-code-runner/issues/305
enWiktionary docs 추가.

VSC substring match : $<number>

컴파일러가 아니라 인터프리터이므로 위, 아래가 중요함..

https://stackoverflow.com/questions/3484019/python-list-to-store-class-instance

gitlab - 프로젝트 - Auto DevOps 기능?


https://docs.python.org/3/library/stdtypes.html?highlight=lower#text-sequence-type-str

===Etymology===
    {{<1>|<2>|<3>|<4>}}
        <1>: m (Wiktionary?), inh (Wikipedia?), der (Wikipedia?), cog (Cognate)
        <2>: word type
            https://en.wiktionary.org/wiki/Category:EnglishLanguage - Edit language data
            - la: Latin
            - en: English
            - sv: Swedish
            - de: German
        <3>: Ancestors.  Language code: <means>
            https://en.wiktionary.org/wiki/Category:EnglishLanguage
            1. ine-pro: Proto-Indo-European
            2. gem-pro: Proto-Germanic
            3. gmw-pro: Proto-West Germanic
            4. ang: Old English (Anglo-Saxon)
            5. enm: Middle English
        <4>: means by english
    *-----
    {{m|enm|bok}} = bok (in Wiktionary)
    {{m|la|pondus||weight}} = weight on Latin (in Wiktionary)
    {{inh|en|enm|book}}  =  Middle English book (in Wikipedia)
    {{inh|en|ang|bōc}}   =  Old English bōc (in Wikipedia)
        Old English language, also called Anglo-Saxon
    {{inh|en|gem-pro|*bōk}}  =  Proto-Germanic (in Wikipedia)
    {{der|en|gem-pro|*bakaną|t=to bake}}  =  Proto-Germanic *bakaną ‎(“to bake”‎).
    {{der|en|la|pondō||by weight}}  =  Latin pondō ‎(“by weight”‎)
        “der” is the third, feminine case ('dative case') for the definite article 'de' in Dutch (English: the)
    {{der|en|ine-pro|*pend-}}
    {{PIE root|en|(s)pend}}
        ???



def addInformation(enWiktionary: EnWiktionary, title: Element, content: Element, queue: Queue, count: int) -> None:
    tempList = []
    page = enWiktionary.getPage(content)
    if page != {}:
        etymology = enWiktionary.getEtymology(page)
        enWiktionary.setPronunciation(page, etymology)
        enWiktionary.setPartOfSpeech(page, etymology)
        
        for key, value in etymology.items():
            for index, v in enumerate(value):
                for pos in v.partOfSpeech:
                    tempList.append((title.text + ":", key, index+1, pos.categoryAndSubcategory))
    
    # [queue.put(item) for item in tempList]

    for item in tempList:
        # print("item", item)
        queue.put(item)
        # print(queue.get())
    


def doAddInformation(path, enQueue, count):
    enWiktionary = EnWiktionary()
    enWiktionary.xmlFilePath = path
    enWiktionary.namespace = {'enWiktionary': 'http://www.mediawiki.org/xml/export-0.10/'}
    enWiktionary.initSetting()
    
    print('a')

    for title, content in zip(enWiktionary.titles, enWiktionary.contents):
        if title.text != 'pie':
            addInformation(enWiktionary, title, content, enQueue, count, )
            count +=1

if __name__ == "__main__":    
    count = 0
    start = time.time()
    enQueue = Queue()
    processes = []
    for dirpath, dirnames, filenames in os.walk("resource/datas"):
        dirpath = dirpath.replace("\\", "/")
        for filename in filenames:
            path = f"{dirpath}/{filename}"
            print(f"parsing {path}")
            process = Process(target=doAddInformation, args=(path, enQueue, count))
            process.start()
            processes.append(process)

    
    [process.join() for process in processes]
    
    
    while not enQueue.empty():
        item = enQueue.get()
        # print(item)

    
    print(time.time()-start)

"""
