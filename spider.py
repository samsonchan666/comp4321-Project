import sys
import pickle
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from collections import deque
import collections

from string import punctuation
from nltk import pos_tag, word_tokenize
from nltk.corpus import wordnet, stopwords

url = "http://www.cse.ust.hk"

# Create queue
queue = deque()

# Maintains list of visited pages
visited_list = []

# Url -> [PageID, PageTitle, LastModified, Size, WordFreqDict, Children]
url2pageID = collections.OrderedDict()
forwardIndex = collections.OrderedDict()
word2wordID = collections.OrderedDict()
invertedIndex = collections.OrderedDict()


def pushInvertedIndex(freqlist, pageID):
    for word, freq in freqlist.items():
        if word not in invertedIndex:
            invertedIndex[word2wordID[word]] = [[pageID, freq]]
        else:
            invertedIndex[word2wordID[word]].append([pageID, freq])


def pushWord2wordID(freqlist):
    for word in freqlist.keys():
        if word not in word2wordID:
            currentWordID = len(word2wordID)
            word2wordID[word] = currentWordID


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


def countWordFreq(tokens):
    freqlist = {}
    for wd in tokens:
        if wd in freqlist:
            freqlist[wd] = freqlist[wd] + 1
        else:
            freqlist[wd] = 1
    return freqlist


def crawl(url):
    if len(visited_list) > 30:
        return
    try:
        urlf = requests.get(url)
        soup = BeautifulSoup(urlf.text, 'html.parser')
        tokens = tokenizeAndClean(soup.text)

        # Append URL to PageID scheme
        currentPageID = len(url2pageID)
        print(currentPageID)
        pageTitle = soup.find("title").text
        url2pageID[url] = [currentPageID, pageTitle, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), len(tokens), {}, []]
        # Append forward index
        forwardIndex[currentPageID] = tokens
        # Append inverted index
        freqlist = countWordFreq(tokens)
        url2pageID[url][4] = freqlist
        pushWord2wordID(freqlist)
        pushInvertedIndex(freqlist, currentPageID)

        visited_list.append(url)

        urls = soup.findAll("a", href=True)
        for i in urls:
            # Complete relative URLs and strip trailing slash
            complete_url = urljoin(url, i["href"]).rstrip('/')

            # Check if the URL already exists in the queue or visited list
            if (complete_url in queue) or (complete_url in visited_list):
                continue
            else:
                url2pageID[url][5].append(complete_url)
                queue.append(complete_url)

    except Exception as e:
        print(e)

    # Pop one URL from the queue from the left side so that it can be crawled
    current = queue.popleft()
    # Recursive call to crawl until the queue is populated with 100 URLs
    crawl(current)


crawl(url)
pickle.dump(url2pageID, open('url2pageID.p', 'wb'))
pickle.dump(forwardIndex, open('forwardIndex.p', 'wb'))
pickle.dump(word2wordID, open('word2wordID.p', 'wb'))
pickle.dump(invertedIndex, open('invertedIndex.p', 'wb'))

sys.exit()
