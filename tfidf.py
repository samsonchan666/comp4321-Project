from sqlitedict import SqliteDict
import math

# Url -> PageID
url2pageID = SqliteDict('./db/url2pageID.sqlite', autocommit=True)
# PageID -> {WordID: frequency, ... }
forwardIndex = SqliteDict('./db/forwardIndex.sqlite', autocommit=True)
# PageID -> doc_norm
docNorm = SqliteDict('./db/docNorm.sqlite', autocommit=True)
# WordID -> [[PageID, frequency, tf_idf]]
invertedIndex = SqliteDict('./db/invertedIndex.sqlite', autocommit=True)
# PageID -> [TitleID]
forwardIndexTitle = SqliteDict('./db/forwardIndexTitle.sqlite', autocommit=True)
# TitleID -> [PageID, tf_idf]
invertedIndexTitle = SqliteDict('./db/invertedIndexTitle.sqlite', autocommit=True)
# PageID -> title_norm
titleNorm = SqliteDict('./db/titleNorm.sqlite', autocommit=True)


def comp_tf_idf():
    total_doc_no = float(len(url2pageID))
    i = 0
    for word_id, posting_list in invertedIndex.items():
        print(i, len(invertedIndex))
        i += 1
        df = float(len(posting_list))
        idf = math.log(total_doc_no / df, 2)
        # tf_max = float(max([x[1] for x in posting_list]))
        for idx in range(len(posting_list)):
            page_id = posting_list[idx][0]
            tf_max = max(list(forwardIndex[page_id].values()))
            tf = float(posting_list[idx][1])
            tf_idf = tf / tf_max * idf
            posting_list[idx][2] = tf_idf
        invertedIndex[word_id] = posting_list


def comp_doc_norm():
    i = 0
    for doc_id, forward_dict in forwardIndex.items():
        print(i, len(forwardIndex))
        i += 1
        word_list = list(forward_dict.keys())
        doc_norm = 0
        for word_id in word_list:
            posting_list = invertedIndex[word_id]
            doc_list = [p_l[0] for p_l in posting_list]
            index = doc_list.index(int(doc_id))
            tf_idf = posting_list[index][2]
            doc_norm += tf_idf * tf_idf
        doc_norm = math.sqrt(doc_norm)
        docNorm[doc_id] = doc_norm


def comp_tf_idf_title():
    total_doc_no = float(len(url2pageID))
    i = 0
    for word_id, posting_list in invertedIndexTitle.items():
        print(i, len(invertedIndexTitle))
        i += 1
        df = float(len(posting_list))
        idf = math.log(total_doc_no / df, 2)
        # tf_max = float(max([x[1] for x in posting_list]))
        for idx in range(len(posting_list)):
            # tf = float(posting_list[idx][1])
            # tf_idf = tf / tf_max * idf
            tf_idf = 1 * idf
            posting_list[idx][1] = tf_idf
        invertedIndexTitle[word_id] = posting_list


def comp_doc_norm_title():
    i = 0
    for doc_id, forward_list in forwardIndexTitle.items():
        print(i, len(forwardIndexTitle))
        i += 1
        word_list = forward_list
        title_norm = 0
        for word_id in word_list:
            posting_list = invertedIndexTitle[word_id]
            doc_list = [p_l[0] for p_l in posting_list]
            index = doc_list.index(int(doc_id))
            tf_idf = posting_list[index][1]
            title_norm += tf_idf * tf_idf
        title_norm = math.sqrt(title_norm)
        titleNorm[doc_id] = title_norm


comp_tf_idf()
comp_doc_norm()
comp_tf_idf_title()
comp_doc_norm_title()
# print(invertedIndex)
# x = dict(invertedIndex.items())

url2pageID.close()
forwardIndex.close()
docNorm.close()
invertedIndex.close()
forwardIndexTitle.close()
invertedIndexTitle.close()
titleNorm.close()
