import re
import math
from search.scripts import porter
from string import punctuation
from nltk import pos_tag, word_tokenize
from nltk.corpus import stopwords

from sqlitedict import SqliteDict


def clean(tokens):
    # Change to lower case
    tokens = [word.lower() for word in tokens]
    # Remove punctuation
    table = str.maketrans('', '', punctuation)
    tokens = [w.translate(table) for w in tokens]
    tokens = [re.sub('[^A-Za-z0-9 ]+', '', w) for w in tokens]
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [w for w in tokens if w not in stop_words]
    tokens = [porter.Porter(w) for w in tokens]
    return tokens

def retriveWebPageInfo():
    url2pageID = SqliteDict('../db/url2pageID.sqlite', autocommit=True)
    return url2pageID

def splitQuery(query):
    pattern = "\"(?:\w+(?: )?)+\"|\w+"
    p = re.compile(pattern)
    match = re.findall(p, query)     
    for i in range(len(match)):
        match[i] = match[i].replace("\"", "") 
    return match       
