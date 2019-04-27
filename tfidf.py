from sqlitedict import SqliteDict
import math

# Url -> PageID
url2pageID = SqliteDict('./db/url2pageID.sqlite', autocommit=True)
# PageID -> [[WordID, frequency]]
forwardIndex = SqliteDict('./db/forwardIndex.sqlite', autocommit=True)
# PageID -> doc_norm
docNorm = SqliteDict('./db/docNorm.sqlite', autocommit=True)
# WordID -> [[PageID, frequency, tf_idf]]
invertedIndex = SqliteDict('./db/invertedIndex.sqlite', autocommit=True)


def comp_tf_idf():
    total_doc_no = float(len(url2pageID))
    i = 0
    for word_id, posting_list in invertedIndex.items():
        print(i, len(invertedIndex))
        i += 1
        df = float(len(posting_list))
        idf = math.log(total_doc_no / df, 2)
        tf_max = float(max([x[1] for x in posting_list]))
        for idx in range(len(posting_list)):
            tf = float(posting_list[idx][1])
            tf_idf = tf / tf_max * idf
            posting_list[idx][2] = tf_idf
        invertedIndex[word_id] = posting_list


def comp_doc_norm():
    i = 0
    for doc_id, forward_list in forwardIndex.items():
        print(i, len(forwardIndex))
        i += 1
        word_list = [f_l[0] for f_l in forward_list]
        doc_norm = 0
        for word_id in word_list:
            posting_list = invertedIndex[word_id]
            doc_list = [p_l[0] for p_l in posting_list]
            index = doc_list.index(int(doc_id))
            tf_idf = posting_list[index][2]
            doc_norm += tf_idf * tf_idf
        doc_norm = math.sqrt(doc_norm)
        docNorm[doc_id] = doc_norm


comp_tf_idf()
comp_doc_norm()
print(invertedIndex)
x = dict(invertedIndex.items())

url2pageID.close()
forwardIndex.close()
docNorm.close()
invertedIndex.close()

