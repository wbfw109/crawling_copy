import parser
import json
import wiktextract

import requests

xml_fn = 'how-to-use-wiktextract'

print("Downloading XML dump to " + xml_fn)

response = requests.get('https://stackoverflow.com/questions/55217938/' + xml_fn, stream=True)

# Throw an error for bad status codes
response.raise_for_status()

with open(xml_fn, 'wb') as handle:
    for block in response.iter_content(4096):
        handle.write(block)

print("Downloaded XML dump, beginning processing...")

fh = open("output.json", "wb")
def word_cb(data):
    fh.write(json.dumps(data))

ctx = wiktextract.parse_wiktionary(
    r'how-to-use-wiktextract', word_cb,
    languages=["English", "Translingual"])

print("{} English entries processed.".format(ctx.language_counts["English"]))
print("{} bytes written to output.json".format(fh.tell()))

fh.close()




#import wiktextract
# path_output = "./output"

# ctx = wiktextract.parse_wiktionary(
#     path_output, word_cb=,
#     capture_cb=None,
#     languages=["English", "Translingual"],
#     translations=False,
#     pronunciations=False,
#     redirects=False)
## https://stackoverflow.com/questions/55217938/how-to-use-wiktextract


# import mwclient, json
# site = mwclient.Site('en.wikipedia.org')
# page = site.pages[u'Wikipedia:Sandbox']
# with open('mwtest.json', 'w', encoding="utf-8") as make_file:
#     json.dump(page.text(), make_file, ensure_ascii=False, indent=4)



# import pywikibot
# site = pywikibot.Site('en', 'wikipedia')  # The site we want to run our bot on
# page = pywikibot.Page(site, 'Wikipedia:Sandbox')
# page.text = page.text.replace('foo', 'bar')
# page.save('Replacing "foo" with "bar"')  # Saves the page

# import jsoncls
# from wiktionaryparser import WiktionaryParser
# parser = WiktionaryParser()
# parser.set_default_language('english')
# word_english = parser.fetch('test')
# word_korean = parser.fetch('test', 'korean')
# # parser.exclude_part_of_speech('noun')
# # parser.include_relation('alternative forms')


# json.dumps(['foo', {'bar': ('baz', None, 1.0, 2)}])

# with open('gfriend.json', 'w', encoding="utf-8") as make_file:
#     json.dump(word_english, make_file, ensure_ascii=False, indent=4)


 



'''
<!--
*********************************************************************
*        *** Attention ALL USERS (registered or not): ***           *
*              ****This is **NOT** a test page!****                 *
*    This is a disambiguation page for the term "test".             *
* ** DO NOT practice here. ** If you do, you may be blocked         *
* for disruptive editing or vandalism. If you want to practice,     *
* please use https://en.wikipedia.org/wiki/Wikipedia:Sandbox        *
*                                       Thanks...                   *
*********************************************************************
-->

'''