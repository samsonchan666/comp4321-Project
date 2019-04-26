import sys
from sqlitedict import SqliteDict
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from collections import deque
import collections

import porter
from string import punctuation
import nltk
from nltk import pos_tag, word_tokenize
from nltk.corpus import stopwords
nltk.download('stopwords')

url = "http://www.cse.ust.hk"

# Create queue
queue = deque()

# Url -> PageID
url2pageID = collections.OrderedDict()
# PageID -> [PageTitle, LastModified, Size, WordFreqDict, Children]
pageID2Meta = collections.OrderedDict()
# PageID -> [keywords]
forwardIndex = collections.OrderedDict()
# Word -> WordID
word2wordID = collections.OrderedDict()
# WordID -> [PageID]
invertedIndex = collections.OrderedDict()
# Title -> TitleID
title2TitleID = collections.OrderedDict()
# TitleID -> [PageID]
invertedIndexTitle = collections.OrderedDict()


def pushInvertedIndex(freqlist, pageID):
    for word, freq in freqlist.items():
        if word2wordID[word] not in invertedIndex:
            invertedIndex[word2wordID[word]] = [[pageID, freq]]
        else:
            invertedIndex[word2wordID[word]].append([pageID, freq])


def pushWord2wordID(freqlist):
    for word in freqlist.keys():
        if word not in word2wordID:
            currentWordID = len(word2wordID)
            word2wordID[word] = currentWordID


def indexTitle(title_tokens):
    for title_token in title_tokens:
        if title_token not in title2TitleID:
            current_title_id = len(title2TitleID)
            title2TitleID[title_token] = current_title_id


def pushTitleInverted(title_tokens, page_id):
    for title_token in title_tokens:
        token_id = title2TitleID[title_token]
        if token_id not in invertedIndexTitle:
            invertedIndexTitle[token_id] = [page_id]
        else:
            invertedIndexTitle[token_id].append(page_id)


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
    tokens = [porter.Porter(w) for w in tokens]
    return tokens


def bigrams(tokens):
    _tokens = tokens.copy()
    bi = list(nltk.bigrams(_tokens))
    bigram_str = [b[0] + " " + b[1] for b in bi]
    return bigram_str


def countWordFreq(tokens):
    _freqlist = {}
    for wd in tokens:
        if wd in _freqlist:
            _freqlist[wd] = _freqlist[wd] + 1
        else:
            _freqlist[wd] = 1
    return _freqlist


def saveHTML(pageID, html):
    html_file = open("./mysite/search/templates/search/html/" + str(pageID) + ".html", "w")
    html = str(html).replace('\n', '<br>')
    html_file.write(str(html.encode('ascii', 'ignore')))
    html_file.close()


def save2SqliteDict(_dict: collections.OrderedDict, _dir):
    sqliteDict = SqliteDict(_dir, autocommit=True)
    for key, value in _dict.items():
        sqliteDict[key] = value


def crawl(url, parent_IDs : list):
    if len(url2pageID) > 30:
        return
    try:
        print(url)
        urlf = requests.get(url)
        soup = BeautifulSoup(urlf.text, 'html.parser')
        if len(soup.text) > 500000:
            raise Exception('The page is too large')
        tokens = tokenizeAndClean(soup.text)

        page_title = soup.find("title").text
        # last_mod_day = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        last_mod_day = datetime.now().strftime("%Y-%m-%d")
        try:
            raw_date = soup.find('span', {"class": "pull-right"})
            pattern = re.compile("\d+-\d+-\d+")
            last_mod_day = re.findall(pattern, raw_date.text)[0]
        except AttributeError:
            pass

        currentPageID = len(url2pageID)
        if url in url2pageID.keys():
            print("Warning, visiting the same page twice")
        print(currentPageID)

        # Index the URL
        url2pageID[url] = currentPageID
        pageID2Meta[currentPageID] = [page_title,
                                      last_mod_day,
                                      len(str(soup.contents)),
                                      {}, []]
        # Append forward index
        forwardIndex[currentPageID] = tokens.copy()
        forwardIndex[currentPageID].extend(bigrams(tokens))
        # Append inverted index
        freqlist = countWordFreq(tokens)
        freqlist_bi = countWordFreq(bigrams(tokens))
        freqlist.update(freqlist_bi)
        pageID2Meta[currentPageID][3] = freqlist
        pushWord2wordID(freqlist)
        pushInvertedIndex(freqlist, currentPageID)

        # Index the title
        title_tokens = tokenizeAndClean(page_title)
        indexTitle(title_tokens)
        indexTitle(bigrams(title_tokens))
        # Inverted index of the title
        pushTitleInverted(title_tokens, currentPageID)
        pushTitleInverted(bigrams(title_tokens), currentPageID)

        # Assign parent-child relationship
        for parent_id in parent_IDs:
            if parent_id != -1:
                if currentPageID not in pageID2Meta[parent_id][4]:
                    pageID2Meta[parent_id][4].append(currentPageID)

        # saveHTML(currentPageID, soup)

        urls = soup.findAll("a", href=True)
        for i in urls:
            # Complete relative URLs and strip trailing slash
            complete_url = urljoin(url, i["href"]).rstrip('/')

            # Assign parent-child relationship for visited/indexed children
            if complete_url in url2pageID.keys():
                if url2pageID[complete_url] not in pageID2Meta[currentPageID][4]:
                    pageID2Meta[currentPageID][4].append(url2pageID[complete_url])

            # Pre-assign parent-child relationship for children in queue
            queue_0 = [q[0] for q in queue]
            if complete_url in queue_0:
                idx = queue_0.index(complete_url)
                if currentPageID not in queue[idx][1]:
                    queue[idx][1].append(currentPageID)

            # Check if the URL already exists in the queue or visited list
            if (complete_url in queue_0) or (complete_url in url2pageID.keys()):
                continue
            else:
                queue.append([complete_url, [currentPageID]])

    except Exception as e:
        print(e)

    # Pop one URL from the queue from the left side so that it can be crawled
    current = queue.popleft()
    # Recursive call to crawl until the queue is populated with 100 URLs
    crawl(current[0], current[1])


crawl(url, [-1])
# save2SqliteDict(url2pageID, './db/url2pageID.sqlite')
# save2SqliteDict(pageID2Meta, './db/pageID2Meta.sqlite')
# save2SqliteDict(forwardIndex, './db/forwardIndex.sqlite')
# save2SqliteDict(word2wordID, './db/word2wordID.sqlite')
# save2SqliteDict(invertedIndex, './db/invertedIndex.sqlite')
# save2SqliteDict(title2TitleID, './db/title2TitleID.sqlite')
# save2SqliteDict(invertedIndexTitle, './db/invertedIndexTitle.sqlite')

sys.exit()
