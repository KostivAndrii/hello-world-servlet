#!/usr/bin/env python3
from html.parser import HTMLParser

number_of_starttags = 0
number_of_endtags = 0

# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        global number_of_starttags
        number_of_starttags += 1

    def handle_endtag(self, tag):
        global number_of_endtags
        number_of_endtags += 1

# instantiate the parser and fed it some HTML
parser = MyHTMLParser()
parser.feed('<html><head><title>Test</title></head><body><h1>Parse me!</h1></body></html>')

print(number_of_starttags, number_of_endtags)