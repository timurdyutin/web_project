# -*- coding: utf-8 -*-
from sys import path
path.append("C:\\Users\\timur1001\\abzac\\")

from threading import Thread
from utils.rthread import rThread
from requests import get
from bs4 import BeautifulSoup as bs
import os 

data = {}
content = get(url="https://ilibrary.ru/author/chekhov/l.all/index.html")
content.encoding = "windows-1251"
soup = bs(content.text, "lxml")

def parseBooksAuthor(): 
    bookAuthor = soup.h1.text
    data[bookAuthor] = {}
    parseAuthorBooksUrls(bookAuthor)
    
def parseAuthorBooksUrls(bookAuthor):
    data[bookAuthor] = {tag.text: "https://ilibrary.ru" + tag["href"] for tag in 
              [tag for tag in soup.findAll("a") if "href" in tag.attrs and len(tag.attrs) == 1 and "text" in tag["href"]]}
    currentPath = os.path.split(os.path.abspath(__file__))[0]
    os.mkdir(os.path.join(currentPath, bookAuthor))
    pathToSave = os.path.join(currentPath, bookAuthor)
    print(pathToSave)
    parseAuthorBooksText(bookAuthor, pathToSave)
    
def parseAuthorBooksText(bookAuthor, pathToSave): 
    print(data)
    for name, url in data[bookAuthor].items(): 
        thread = rThread(target=parseAuthorBookText, args=(url, ))
        thread.start()
        text = thread.join()
        with open(os.path.join(pathToSave, name + ".txt"), "w", encoding="utf-8") as file:
            file.write(text)        

def parseAuthorBookText(url):  
    count = 1
    b = ""
    copiedUrl = url
    while True:
        try:
            url = url.replace("index.html", f"p.{count}/index.html")
            content = get(url=url)
            content.encoding = "windows-1251"
            soup = bs(content.text, "lxml")
            q = "".join([tag.text for tag in soup.findAll("span") if "class" in tag.attrs])
            b += q
            count += 1
            url = copiedUrl
        except:
            print(b)
            return b

parseBooksAuthor()