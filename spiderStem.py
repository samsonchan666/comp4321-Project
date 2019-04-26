import sys
from sqlitedict import SqliteDict
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from collections import deque
import collections

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


def save2SqliteDict(_dict: collections.OrderedDict, _dir):
    sqliteDict = SqliteDict(_dir, autocommit=True)
    for key, value in _dict.items():
        sqliteDict[key] = value


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

def updateM(word):
    vowel = 'aeiou'
    structure = []
    structureLength = 0
    m = 0
    for x in word:
        if x in vowel:
            if (len(structure) == 0) or (structure[-1] == 'c'):
                structure.append('v')
        elif (len(structure) == 0) or (structure[-1] == 'v'):
            structure.append('c')
    structureLength = len(structure)
        
    m = structureLength/2
    if m > 0:
        if (structure[0] == 'c') and (structure[-1] == 'v'):
            m = m - 1
        elif (structure[0] == 'c') or (structure[-1] == 'v'):
            m = m - 0.5
    return [structure, structureLength, m]

def check_cvcwxy(word):
    vowel = 'aeiou'
    if (len(word) >= 3) and (word[-1] not in (vowel or 'wxy')) and (word[-2] in vowel) and (word[-3] not in vowel):
            return True
    else:
        return False

def Porter(word):
    if (word.isalpha() == False):
        return word
    else:
        vowel = 'aeiou'
        #structure = []
        #structureLength = 0
        #m = 0 
        
        update = updateM(word)
        
        #For 'fff' case
        if update[1] == 1:
            return word
        
        #Step 1a
        if word.endswith('sses'):
            word = word.replace('sses', 'ss')
        elif word.endswith('ies'):
            word = word.replace('ies', 'i')
        elif word.endswith('ss'):
            word = word
        elif word.endswith('s'):
            word = word.replace('s', '')
        
        #Step 1b
        nextStep = False
        temp = word
        if word.endswith('eed'):
            temp = word[0:-3]
            if updateM(temp)[2] > 0:
                word = word.replace('eed', 'ee')
        if 'v' in update[0][1:-1]:  
            if word.endswith('ed'):
                temp = word.replace('ed', '')
            elif word.endswith('ing'):
                temp = word.replace('ing', '')
            if temp != word:
                for x in temp:
                    if x in vowel:
                        word = temp
                        nextStep = True
        
        update = updateM(word)
        
        #Step 1b continued
        if nextStep == True:
            if word.endswith('at'):
                word = word.replace('at', 'ate')
            elif word.endswith('bl'):
                word = word.replace('bl', 'ble')
            elif word.endswith('iz'):
                word = word.replace('iz', 'ize')
            elif (word[-1] == word[-2]) and (word[-1] not in 'lsz'):
                word = word[0:-1]
            elif (check_cvcwxy(word) == True) and (update[2] == 1):
                word = word + 'e'
        
        #Step 1c
        vowelExist = False
        for x in word:
            if x in vowel:
                vowelExist = True
        if (vowelExist == True) and (word.endswith('y') == True):
            word = word.replace('y', 'i')
        
        #Step 2
        Step2Dict = {'ational': 'ate',
                    'tional': 'tion',
                    'enci': 'ence',
                    'anci': 'ance',
                    'izer': 'ize',
                    'abli': 'able',
                    'alli': 'al',
                    'entli': 'ent',
                    'eli': 'e',
                    'oucli': 'ous',
                    'ization': 'ize',
                    'ation': 'ate',
                    'ator': 'ate',
                    'alism': 'al',
                    'iveness': 'ive',
                    'fulness': 'ful',
                    'ousness': 'ous',
                    'aliti': 'al',
                    'iviti': 'ive',
                    'biliti': 'ble'}
        temp = word
        for x in Step2Dict:
            if temp.endswith(x):
                temp = word.replace(x, '')
                if updateM(temp)[2] > 0:
                    word = word.replace(x, Step2Dict[x])
                    
        #Step 3
        Step3Dict = {'icate': 'ic',
                    'ative': '',
                    'alize': 'al',
                    'iciti': 'ic',
                    'ical': 'ic',
                    'ful': '',
                    'ness': ''}
        temp = word
        for x in Step3Dict:
            if temp.endswith(x):
                temp = word.replace(x, '')
                if updateM(temp)[2] > 0:
                    word = word.replace(x, Step3Dict[x])
        
        #Step 4
        Step4List = ['al', 'ance', 'ence', 'er', 'ic', 'able', 'ible', 'ant', 'ement', 'ment', 'ent', 
                     'ion', 'ou', 'ism', 'ate', 'iti', 'ous', 'ive', 'ize']
        for x in Step4List:
            if word.endswith(x):
                temp = word.replace(x, '')
                if x == 'ion':
                    if (temp.endswith('s') == True) or (temp.endswith('t') == True):
                        if updateM(temp[0:-1])[2] > 1:
                            word = word.replace(x, '')
                else:
                    if updateM(temp)[2] > 1:
                        word = word.replace(x, '')
        
        #Step 5a
        temp = word
        if temp.endswith('e'):
            temp = word[0:-1]
            m = updateM(temp)[2]
            if m > 1:
                word = temp
            if (m == 1) and (check_cvcwxy(temp) == False):
                word = temp
        
        #Step 5b
        if (word[-1] == 'l') and (word[-2] == 'l') and (updateM(word)[2] > 1):
            word = word[0:-1]
            
        return word

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
    tokens = [Porter(w) for w in tokens]
    return tokens


def countWordFreq(tokens):
    freqlist = {}
    for wd in tokens:
        if wd in freqlist:
            freqlist[wd] = freqlist[wd] + 1
        else:
            freqlist[wd] = 1
    return freqlist


def saveHTML(pageID, html):
    html_file = open("./html/" + str(pageID) + ".html", "w")
    html = str(html).replace('\n', '<br>')
    html_file.write(str(html.encode('ascii', 'ignore')))
    html_file.close()


def crawl(url, parent_IDs : list):
    if len(url2pageID) > 30:
        return
    try:
        urlf = requests.get(url)
        soup = BeautifulSoup(urlf.text, 'html.parser')
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
        if currentPageID in url2pageID.values():
            print("Warning, same index")
        print(currentPageID)

        # Index the URL
        url2pageID[url] = currentPageID
        pageID2Meta[currentPageID] = [page_title,
                                      last_mod_day,
                                      len(str(soup.contents)),
                                      {}, []]
        # Append forward index
        forwardIndex[currentPageID] = tokens
        # Append inverted index
        freqlist = countWordFreq(tokens)
        pageID2Meta[currentPageID][3] = freqlist
        pushWord2wordID(freqlist)
        pushInvertedIndex(freqlist, currentPageID)

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
save2SqliteDict(url2pageID, './url2pageID.sqlite')
save2SqliteDict(pageID2Meta, './pageID2Meta.sqlite')
save2SqliteDict(forwardIndex, './forwardIndex.sqlite')
save2SqliteDict(word2wordID, './word2wordID.sqlite')
save2SqliteDict(invertedIndex, './invertedIndex.sqlite')

sys.exit()