#!/usr/bin/env python3
import os
import datetime
import yaml
import sqlite3
import argparse
from html.parser import HTMLParser
from urllib.parse import urlparse
import urllib.request
from urllib import error
from sqlalchemy import Column, LargeBinary, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import pickle
from sqlalchemy.ext.serializer import loads, dumps

# number_of_starttags = 0
# number_of_endtags = 0
rezults_tag = []

Base = declarative_base()

class Urls(Base):
    __tablename__ = 'al_urls'
    site_name = Column(String(50), nullable=False, )
    url = Column(String(250), nullable=False, primary_key=True)
    DT = Column(String(50), nullable=False, primary_key=True)
    tags = Column(LargeBinary)

    def __init__(self, site_name, url, DT, tags):
        self.site_name = site_name
        self.url = url
        self.DT = DT
        self.tags = tags


# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
    def __init__(self):
        self.tags_list = []
        super(MyHTMLParser, self).__init__()

    def handle_starttag(self, tag, attrs):
        # global number_of_starttags
        print('<',tag, '>')
        self.tags_list.append(tag)
        # number_of_starttags += 1

    def handle_endtag(self, tag):
        # global number_of_endtags
        print('</',tag, '>')
        self.tags_list.append(tag)
        # number_of_endtags += 1


def downloadUrl(url:str) -> str:
    # load YAML synonims
    with open("synonims.yaml", 'r') as ymlfile:
        snnm = yaml.load(ymlfile)

    # download html for analizing
    try:
        # check url in synonims YAML
        if url in snnm['synonims'] :
            url = snnm['synonims'][url]
        # check if schema is present. else use http by default
        if urlparse(url).scheme == '':
            response = urllib.request.urlopen(str('http://'+url))
        else:
            response = urllib.request.urlopen(url)
    except error.URLError as e:
        if hasattr(e,'code') :
            print (e.code)
        if hasattr(e,'reason') :
            print (e.reason)
        exit(1)
    except error.HTTPError as e:
        if hasattr(e,'code'):
            print(e.code)
        if hasattr(e,'reason'):
            print(e.reason)
        exit(1)

    # webContent = response.read().decode("utf-8")
    return response.read().decode(response.headers.get_content_charset())


def logg_site_processing(url:str, DT:datetime.datetime):
    # currentDT = datetime.datetime.now()
    with open('tagcounter.log', "a") as f:
        print(DT.strftime("%Y-%m-%d %H:%M:%S"), url, file=f)


def process_tag_calculating(rezults_tag:[]) -> {}:
    # calculate each tags amounts
    print('')
    print(rezults_tag)
    print('Tegs total: ', len(rezults_tag))
    rezults_tag_list = list(dict.fromkeys(rezults_tag))
    print('uniq tags list: ', rezults_tag_list)
    rezults_tag_dict = {r_tag:rezults_tag.count(r_tag) for r_tag in rezults_tag_list}
    print('Tags frequency    : ', rezults_tag_dict)
    print('Tegs total final: ', sum(rezults_tag_dict.values()))
    return rezults_tag_dict


def store_sql3_pickle(site_name:str, url:str, DT:datetime.datetime, rezult_dict:{}):
    # Pickle + sqlite3
    p_dict = pickle.dumps(rezult_dict, protocol=pickle.HIGHEST_PROTOCOL)

    conn = sqlite3.connect('tagcounter.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS urls
                (site text, url text, date text, tags blob)''')
    c.execute("INSERT INTO urls (site, url, date, tags) VALUES ( ?, ?, ?, ?)", \
        ( site_name , url, DT, p_dict))
    conn.commit()
    conn.close()

def read_sql3_pickle(url:str):
    # Pickle + sqlite3
    # p_dict = pickle.dumps(rezult_dict, protocol=pickle.HIGHEST_PROTOCOL)
    conn = sqlite3.connect('tagcounter.db')
    c = conn.cursor()
    rrr = str("SELECT * FROM urls WHERE url = '" + url + "'")
    c.execute(str("SELECT * FROM urls WHERE url = '" + url + "'"))
    records = c.fetchall()

    for row in records:
        print("Site = ", row[0], )
        print("URL = ", row[1])
        print("Parsing date  = ", row[2])
        pickle_rezults_tag_dict = pickle.loads(row[3])
        print("Tags frequency: ", pickle_rezults_tag_dict)
        print('Tegs total final: ', sum(pickle_rezults_tag_dict.values()))

    conn.commit()
    conn.close()

def store_alchemy_pickle(site_name:str, url:str, DT:datetime.datetime, rezult_dict:{}):
    engine = create_engine('sqlite:///sqlalchemy_example.db')
    Base.metadata.create_all(engine)
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    # Insert an record in the table
    new_urls = Urls( site_name, url, DT, dumps(rezult_dict))
    session.add(new_urls)
    session.commit()

def read_alchemy_pickle(url:str):
    engine = create_engine('sqlite:///sqlalchemy_example.db')
    Base.metadata.create_all(engine)
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    session.query(Urls).all()
    ourSites = session.query(Urls).filter(Urls.url==url)

    for row in ourSites:
        print("Site = ", row.site_name )
        print("URL = ", row.url)
        print("Parsing date  = ", row.DT)
        pickle_rezults_tag_dict = loads(row.tags)
        print("Tags frequency: ", pickle_rezults_tag_dict)
        print('Tegs total final: ', sum(pickle_rezults_tag_dict.values()))


def main():
    # # procassing input parameters
    parser = argparse.ArgumentParser(description='Programm to work with AWS')
    parser.add_argument('--get', help='gathering info about this site')
    parser.add_argument('--view', help='displaying info about this site')
    args = parser.parse_args()

    if args.get == '' :
        print('you should pass an argument for --get. see next time. bye')
        exit(0)
    if args.view == '' :
        print('you should pass an argument for --view. see next time. bye')
        exit(0)

    # download url
    webContent = downloadUrl(args.get)
    # write operation into log file
    currentDT = datetime.datetime.now()
    logg_site_processing(args.get, currentDT)
    # with open('tagcounter.log', "a") as f:
    #     print(currentDT.strftime("%Y-%m-%d %H:%M:%S"), args.get, file=f)
    # print(type(currentDT))

    # instantiate the parser and fed it some HTML
    parser = MyHTMLParser()
    # parse HTML and collect tags info
    parser.feed(webContent)
    # rezults_tag = parser.tags_list

    # currentDT = datetime.datetime.now()
    # with open('tagcounter.log', "a") as f:
    #     print(currentDT.strftime("%Y-%m-%d %H:%M:%S"), args.get, file=f)

    # calculate each tags amounts
    rezult_dict = process_tag_calculating(parser.tags_list)
    # print('')
    # print(rezults_tag)
    # print('Tegs total: ', len(rezults_tag))
    # rezults_tag_list = list(dict.fromkeys(rezults_tag))
    # print('uniq tags list: ', rezults_tag_list)
    # rezults_tag_dict = {r_tag:rezults_tag.count(r_tag) for r_tag in rezults_tag_list}
    # print('Tags frequency    : ', rezults_tag_dict)
    # print('Tegs total final: ', sum(rezults_tag_dict.values()))


    # # Pickle
    # with open('filename.pickle', 'wb') as handle:
    #     pickle.dump(rezults_tag_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # with open('filename.pickle', 'rb') as handle:
    #     rezults_tag_dict_new = pickle.load(handle)
    # print('Tags frequency new: ', rezults_tag_dict_new)

    # store rezults into sqlite3 with pickle
    store_sql3_pickle(urlparse(args.get).hostname, args.get, currentDT.strftime("%Y-%m-%d %H:%M:%S"), rezult_dict)
    print('--------------------------------------------------------------------------------')
    read_sql3_pickle(args.get)
    print('--------------------------------------------------------------------------------')
    # Pickle + sqlite3
    # import pickle
    # p_dict = pickle.dumps(rezult_dict, protocol=pickle.HIGHEST_PROTOCOL)

    # conn = sqlite3.connect('tagcounter.db')
    # c = conn.cursor()
    # # site = urlparse(args.get).hostname
    # # dt = currentDT.strftime("%Y-%m-%d %H:%M:%S")

    # c.execute('''CREATE TABLE IF NOT EXISTS urls
    #             (site text, url text, date text, tags blob)''')
    # c.execute("INSERT INTO urls (site, url, date, tags) VALUES ( ?, ?, ?, ?)", \
    #     ( urlparse(args.get).hostname , args.get , currentDT.strftime("%Y-%m-%d %H:%M:%S") , p_dict))

    # c.execute("SELECT * FROM urls WHERE site = '12factor.net'")
    # records = c.fetchall()

    # for row in records:
    #     print("Site = ", row[0], )
    #     print("URL = ", row[1])
    #     print("Parsing date  = ", row[2])
    #     pickle_rezults_tag_dict = pickle.loads(row[3])
    #     print("Tags frequency: ", pickle_rezults_tag_dict)
    #     print('Tegs total final: ', sum(pickle_rezults_tag_dict.values()))

    # conn.commit()
    # conn.close()


    # # SQLAlchemy == START
    store_alchemy_pickle(urlparse(args.get).hostname, args.get, currentDT.strftime("%Y-%m-%d %H:%M:%S"), rezult_dict)
    print('--------------------------------------------------------------------------------')
    read_alchemy_pickle(args.get)
    print('--------------------------------------------------------------------------------')
    # engine = create_engine('sqlite:///sqlalchemy_example.db')

    # Base.metadata.create_all(engine)

    # DBSession = sessionmaker(bind=engine)
    # session = DBSession()

    # # Insert an record in the table
    # dpickle = dumps(rezult_dict)
    # new_urls = Urls( urlparse(args.get).hostname , args.get , currentDT.strftime("%Y-%m-%d %H:%M:%S") , \
    #     dumps(rezult_dict))
    # session.add(new_urls)
    # # new_urls.post_code
    # ## check reading pickle from database --view
    # session.commit()
    # session.query(Urls).all()
    # ourSites = session.query(Urls).filter(Urls.site_name=='12factor.net')

    # for row in ourSites:
    #     print("Site = ", row.site_name )
    #     print("URL = ", row.url)
    #     print("Parsing date  = ", row.DT)
    #     pickle_rezults_tag_dict = loads(row.tags)
    #     print("Tags frequency: ", pickle_rezults_tag_dict)
    #     print('Tegs total final: ', sum(pickle_rezults_tag_dict.values()))
    # # SQLAlchemy == END

    print(list(dict.fromkeys(rezults_tag)))
    # print(number_of_starttags, number_of_endtags)

# r0 = ['html', 'head', 'meta', 'title', 'title', 'meta', 'meta', 'meta', 'link', 'link', 'link', 'script', 'script', 'script', 'script', 'head', 'body', 'noscript', 'iframe', 'iframe', 'noscript', 'script', 'script', 'header', 'h1', 'a', 'a', 'h1', 'header', 'section', 'article', 'h2', 'h2', 'h3', 'h3', 'p', 'em', 'em', 'a', 'a', 'p', 'ul', 'li', 'a', 'a', 'li', 'li', 'li', 'li', 'li', 'ul', 'p', 'strong', 'strong', 'p', 'p', 'p', 'p', 'strong', 'strong', 'a', 'a', 'a', 'a', 'p', 'p', 'p', 'p', 'strong', 'em', 'em', 'strong', 'em', 'em', 'em', 'em', 'p', 'p', 'code', 'code', 'code', 'code', 'code', 'code', 'code', 'code', 'code', 'code', 'code', 'code', 'p', 'p', 'p', 'article', 'section', 'section', 'nav', 'div', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'span', 'span', 'div', 'div', 'a', 'a', 'div', 'div', 'a', 'a', 'div', 'nav', 'section', 'footer', 'div', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'span', 'span', 'div', 'div', 'div', 'div', 'div', 'div', 'a', 'a', 'div', 'div', 'a', 'a', 'div', 'div', 'a', 'a', 'div', 'footer', 'body', 'html']
# len(r0)
# r1 = list(dict.fromkeys(r0))
# r2 = {r_tag:rezult.count(r_tag) for r_tag in r1}
# print(r2)
# sum(r2.values())

# # Expression Serializer Extension
# from sqlalchemy.ext.serializer import loads, dumps
# metadata = MetaData(bind=some_engine)
# Session = scoped_session(sessionmaker())

# # ... define mappers

# query = Session.query(MyClass).
#     filter(MyClass.somedata=='foo').order_by(MyClass.sortkey)

# # pickle the query
# serialized = dumps(query)

# # unpickle.  Pass in metadata + scoped_session
# query2 = loads(serialized, metadata, Session)

# print query2.all()

# # using yaml configuration fie
# # https://martin-thoma.com/configuration-files-in-python/
# import yaml

# with open("config.yml", 'r') as ymlfile:
#     cfg = yaml.load(ymlfile)

# for section in cfg:
#     print(section)
# print(cfg['mysql'])
# print(cfg['other'])

if __name__ == "__main__":
    # execute only if run as a script
    main()
