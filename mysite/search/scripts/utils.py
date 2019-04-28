import re
import math
from search.scripts import porter
from string import punctuation
from nltk import pos_tag, word_tokenize
from nltk.corpus import stopwords

from sqlitedict import SqliteDict

# split should be list with length >= 2
def split2Str(split):
    result = split[0]
    for i in range(len(split)-1):
        result += " " + split[i+1]
    return result

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
    # Apply stemming to unigram and bigram
    for idx in range(len(tokens)):
        if len(tokens[idx].split()) == 1:
            tokens[idx] = porter.Porter(tokens[idx])
        else:
            stem_split = [porter.Porter(w) for w in tokens[idx].split()]
            print(stem_split)
            tokens[idx] = split2Str(stem_split)
    # tokens = [porter.Porter(w) for w in tokens]
    return tokens

def splitQuery(query):
    pattern = "\"(?:\w+(?: )?)+\"|\w+"
    p = re.compile(pattern)
    match = re.findall(p, query)     
    no_query = len(match)
    for i in range(no_query):
        if "\"" in match[i]:
            match[i] = match[i].replace("\"", "")
            unigram = match[i].split()
            match.extend(unigram)
    return match       
