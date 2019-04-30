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
# from nltk.corpus import stopwords
# nltk.download('stopwords')

url = "http://www.cse.ust.hk"
max_page = 300
save_to_db = True
save_html = False

# Create queue
queue = deque()

# Url -> PageID
url2pageID = collections.OrderedDict()
# PageID -> Url
pageID2Url = collections.OrderedDict()
# PageID -> [PageTitle, LastModified, Size, WordFreqDict, Children]
pageID2Meta = collections.OrderedDict()
# PageID -> [[WordID, frequency]]
forwardIndex = collections.OrderedDict()
# Word -> WordID
word2wordID = collections.OrderedDict()
# WordID -> Word
wordID2word = collections.OrderedDict()
# WordID -> [[PageID, frequency, tf_idf]]
invertedIndex = collections.OrderedDict()
# Title Token -> TitleID
title2TitleID = collections.OrderedDict()
# TitleID -> Title Token
titleID2Title = collections.OrderedDict()
# PageID -> [TitleID]
forwardIndexTitle = collections.OrderedDict()
# TitleID -> [[PageID, tf_idf]]
invertedIndexTitle = collections.OrderedDict()

stopwords = set([line.rstrip('\n') for line in open('./stopwords.txt')])


def pushInvertedIndex(freqlist, pageID):
    for word, freq in freqlist.items():
        if word2wordID[word] not in invertedIndex:
            invertedIndex[word2wordID[word]] = [[pageID, freq, 0]]
        else:
            invertedIndex[word2wordID[word]].append([pageID, freq, 0])


def indexWord(freqlist):
    for word in freqlist.keys():
        if word not in word2wordID:
            currentWordID = len(word2wordID)
            word2wordID[word] = currentWordID
            wordID2word[currentWordID] = word


def indexTitle(title_tokens):
    for title_token in title_tokens:
        if title_token not in title2TitleID:
            current_title_id = len(title2TitleID)
            title2TitleID[title_token] = current_title_id
            titleID2Title[current_title_id] = title_token


def pushTitleInverted(title_tokens, page_id):
    for title_token in title_tokens:
        token_id = title2TitleID[title_token]
        if token_id not in invertedIndexTitle:
            invertedIndexTitle[token_id] = [[page_id, 0]]
        else:
            invertedIndexTitle[token_id].append([page_id, 0])


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
    # stop_words = set(stopwords.words('english'))
    stop_words = stopwords
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
    print("Saving database to" + _dir)
    for key, value in _dict.items():
        sqliteDict[key] = value
    sqliteDict.close()


def crawl(url, parent_IDs : list):
    if len(url2pageID) > max_page:
        return
    try:
        if ".pdf" in url:
            raise Exception('Ingore pdf page')
        print(url)
        urlf = requests.get(url)
        soup = BeautifulSoup(urlf.text, 'html.parser')
        if len(soup.text) > 500000:
            raise Exception('The page is too large')
        tokens = tokenizeAndClean(soup.text)

        page_title = soup.find("title").text
        # last_mod_day = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        last_mod_date = datetime.now().strftime("%Y-%m-%d")
        try:
            raw_date = soup.find('span', {"class": "pull-right"})
            pattern = re.compile("\d+-\d+-\d+")
            last_mod_date = re.findall(pattern, raw_date.text)[0]
        except AttributeError:
            pass

        currentPageID = len(url2pageID)
        # Check the page is being modified
        if url in url2pageID.keys():
            mod_date = pageID2Meta[url2pageID[url]][1]
            mod_date = datetime.strptime(mod_date, "%Y-%m-%d")
            if mod_date >= datetime.strptime(last_mod_date, "%Y-%m-%d"):
                raise Exception('The page is not modified')
            print("Warning, visiting the same page twice")
            # Use the existing page ID, otherwise serious bug will occur
            currentPageID = url2pageID[url]
        print(currentPageID)

        # Index the URL
        url2pageID[url] = currentPageID
        # Page ID -> Url
        pageID2Url[currentPageID] = url
        pageID2Meta[currentPageID] = [page_title,
                                      last_mod_date,
                                      len(str(soup.contents)),
                                      {}, []]

        freqlist = countWordFreq(tokens)
        freqlist_bi = countWordFreq(bigrams(tokens))
        freqlist.update(freqlist_bi)
        pageID2Meta[currentPageID][3] = freqlist
        indexWord(freqlist)

        # Append forward index
        freqlist_id = {}
        for word, freq in freqlist.items():
            freqlist_id[word2wordID[word]] = freq
        # freqlist_id = [{word2wordID[x[0]]: x[1]} for x in list(freqlist.items())]
        forwardIndex[currentPageID] = freqlist_id
        # Append inverted index
        pushInvertedIndex(freqlist, currentPageID)

        # Title to title id
        title_tokens = tokenizeAndClean(page_title)
        indexTitle(title_tokens)
        indexTitle(bigrams(title_tokens))
        # Title forward index
        all_title_tokens = title_tokens.copy()
        all_title_tokens.extend(bigrams(title_tokens))
        all_title_tokens = [title2TitleID[x] for x in all_title_tokens]
        forwardIndexTitle[currentPageID] = all_title_tokens
        # Inverted index of the title
        pushTitleInverted(title_tokens, currentPageID)
        pushTitleInverted(bigrams(title_tokens), currentPageID)

        # Assign parent-child relationship
        for parent_id in parent_IDs:
            if parent_id != -1:
                if currentPageID not in pageID2Meta[parent_id][4]:
                    pageID2Meta[parent_id][4].append(currentPageID)

        if save_html:
            saveHTML(currentPageID, soup)

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
if save_to_db:
    save2SqliteDict(url2pageID, './db/url2pageID.sqlite')
    save2SqliteDict(pageID2Url, './db/pageID2Url.sqlite')
    save2SqliteDict(pageID2Meta, './db/pageID2Meta.sqlite')
    save2SqliteDict(forwardIndex, './db/forwardIndex.sqlite')
    save2SqliteDict(word2wordID, './db/word2wordID.sqlite')
    save2SqliteDict(wordID2word, './db/wordID2word.sqlite')
    save2SqliteDict(invertedIndex, './db/invertedIndex.sqlite')
    save2SqliteDict(title2TitleID, './db/title2TitleID.sqlite')
    save2SqliteDict(titleID2Title, './db/titleID2Title.sqlite')
    save2SqliteDict(forwardIndexTitle, './db/forwardIndexTitle.sqlite')
    save2SqliteDict(invertedIndexTitle, './db/invertedIndexTitle.sqlite')

sys.exit()

# x = forwardIndex[29]
# z = [y[0] for y in x]
# for _z in z:
#     aa = invertedIndex[_z]
#     bb = [cc[0] for cc in aa]
#     if 29 not in bb:
#         print("error")
