import re
from string import punctuation
from nltk import pos_tag, word_tokenize
from nltk.corpus import stopwords

from sqlitedict import SqliteDict

def tokenizeAndClean(doc):
    tokens = word_tokenize(doc)
    # Change to lower case
    tokens = [word.lower() for word in tokens]
    # Remove punctuation
    table = str.maketrans('', '', punctuation)
    tokens = [w.translate(table) for w in tokens]
    tokens = [re.sub('[^A-Za-z0-9]+', '', w) for w in tokens]
    tokens = [w for w in tokens if w != '']
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [w for w in tokens if w not in stop_words]
    return tokens

""""To-do retrive function. Should return a dictionary with output like phase 1"""
def retrive():
    return

def retriveWebPageInfo():
    url2pageID = SqliteDict('../url2pageID.sqlite', autocommit=True)
    return url2pageID

def splitQuery(query):
    pattern = "\"(?:\w+(?: )?)+\"|\w+"
    p = re.compile(pattern)
    match = re.findall(p, query)     
    for i in range(len(match)):
        match[i] = match[i].replace("\"", "") 
    return match