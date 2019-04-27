from sqlitedict import SqliteDict
import math

# Url -> PageID
url2pageID = SqliteDict('./db/url2pageID.sqlite')
# PageID -> [PageTitle, LastModified, Size, WordFreqDict, Children]
pageID2Meta = SqliteDict('./db/pageID2Meta.sqlite')
# PageID -> [[WordID, frequency]]
forwardIndex = SqliteDict('./db/forwardIndex.sqlite')
# PageID -> doc_norm
docNorm = SqliteDict('./db/docNorm.sqlite')
# Word -> WordID
word2wordID = SqliteDict('./db/word2wordID.sqlite')
# WordID -> [[PageID, frequency]]
invertedIndex = SqliteDict('./db/invertedIndex.sqlite')
# Title -> TitleID
title2TitleID = SqliteDict('./db/title2TitleID.sqlite')
# TitleID -> [PageID]
invertedIndexTitle = SqliteDict('./db/invertedIndexTitle.sqlite')
queries = ["comput", "scienc"]


score_dict = {}
word_id = -1
total_doc_no = float(len(url2pageID))
for query in queries:
    if query in word2wordID.keys():
        word_id = word2wordID[query]
    else:
        print("Query word not indexed")
        continue
    posting_list = invertedIndex[word_id]
    df = float(len(posting_list))
    idf = math.log(total_doc_no / df, 2)
    tf_max = float(max([x[1] for x in posting_list]))
    for document in posting_list:
        doc_id = document[0]
        # Pre-computed tf-idf
        tf_idf = document[2]
        # Accumulate the inner product
        if doc_id not in score_dict:
            score_dict[doc_id] = [tf_idf * 1, 1]
        else:
            score_dict[doc_id][0] += tf_idf * 1
            score_dict[doc_id][1] += 1

cos_sim = score_dict.copy()
i = 0
for doc_id, score in score_dict.items():
    print(i, len(score_dict))
    i += 1
    word_list = [x[0] for x in forwardIndex[doc_id]]
    doc_norm = docNorm[doc_id]
    query_norm = math.sqrt(score_dict[doc_id][1])
    inner_prod = float(score_dict[doc_id][0])
    cos_sim[doc_id] = inner_prod / (doc_norm * query_norm)

cos_sim_list = list(cos_sim.items())
cos_sim_list = sorted(cos_sim_list, key=lambda x: x[1], reverse=True)
print(cos_sim_list)

url2pageID.close()
pageID2Meta.close()
forwardIndex.close()
docNorm.close()
word2wordID.close()
invertedIndex.close()
title2TitleID.close()
invertedIndexTitle.close()


"""
text_file = open("spider_result.txt", "w")


def findParent(pageID):
    _parents = []
    for id, meta in pageID2Meta.items():
        if pageID in meta[4]:
            _parents.append(id)
    return _parents


for url, pageID in url2pageID.items():
    text_file.write("%s\n" % pageID2Meta[pageID][0])
    text_file.write("%s\n" % url)
    text_file.write("%s %d\n" % (pageID2Meta[pageID][1],
                                 pageID2Meta[pageID][2]))
    for word, freq in pageID2Meta[pageID][3].items():
        text_file.write("%s %d; " % (word, freq))
    text_file.write("\n")
    parents = findParent(pageID)
    text_file.write("Parent links:\n")
    for parent in parents:
        parent_url = list(url2pageID.keys())[list(url2pageID.values()).index(int(parent))]
        text_file.write("%s\n" % parent_url)
    text_file.write("Children links:\n")
    for child in pageID2Meta[pageID][4]:
        child_url = list(url2pageID.keys())[list(url2pageID.values()).index(int(child))]
        text_file.write("%s\n" % child_url)
    text_file.write('-------------------------------------------------------------------------------------------\n')

text_file.close()
"""

"""
for url, pageID in url2pageID.items():
    print(pageID2Meta[pageID][0])
    print(url)
    print(pageID2Meta[pageID][1], pageID2Meta[pageID][2])
    for word, freq in pageID2Meta[pageID][3].items():
        print(word, freq, ';', end='')
    parents = findParent(pageID)
    print("")
    print("Parent links:")
    for parent in parents:
        print(list(url2pageID.keys())[list(url2pageID.values()).index(int(parent))])
    print("Children links:")
    for child in pageID2Meta[pageID][4]:
        print(list(url2pageID.keys())[list(url2pageID.values()).index(child)])
        # print(child)
    print('-------------------------------------------------------------------------------------------')

"""

