#### concurent.futures
import urllib.request
import shutil
import os
from html.parser import HTMLParser

number_of_starttags = 0
number_of_endtags = 0
rezults_tag = []

# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        global number_of_starttags
        print(tag)
        rezults_tag.append(tag)
        number_of_starttags += 1

    def handle_endtag(self, tag):
        global number_of_endtags
        print(tag)
        rezults_tag.append(tag)
        number_of_endtags += 1

url = 'https://12factor.net/ru/config'
output_file = "12factor.html"
response = urllib.request.urlopen(url)
webContent = response.read()
print(webContent[0:3000])

f = open('foxnews.html', 'wb')
f.write(webContent)
f.close
print(os.getcwd())

# instantiate the parser and fed it some HTML
parser = MyHTMLParser()
parser.feed(webContent)
print(rezults_tag)
print(number_of_starttags, number_of_endtags)
