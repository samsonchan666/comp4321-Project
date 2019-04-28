import math
from sqlitedict import SqliteDict

def docID2UrlName(doc_id, db_ref):
    url2pageID = db_ref[0]
    return list(url2pageID.keys())[list(url2pageID.values()).index(int(doc_id))]

def findParent(pageID, metadb):
    _parents = []
    for id, meta in metadb.items():
        if pageID in meta[4]:
            _parents.append(id)
    return _parents

def format_result(cos_sim_list, db_ref):
    pageID2Meta = SqliteDict('../db/pageID2Meta.sqlite')
    query_results = []
    for doc in cos_sim_list:
        doc_id = doc[0]
        score  = doc[1]
        title = pageID2Meta[doc_id][0]
        last_mod = pageID2Meta[doc_id][1]
        url_name = docID2UrlName(doc_id, db_ref)
        size = pageID2Meta[doc_id][2]
        word_freq = pageID2Meta[doc_id][3]
        word_freq_list = sorted(list(word_freq.items()), key=lambda x: x[1], reverse=True)
        word_freq_list = word_freq_list[:5]
        parent = findParent(doc_id, pageID2Meta)
        parent = [docID2UrlName(p, db_ref) for p in parent]
        children = pageID2Meta[doc_id][4]
        children = [docID2UrlName(c, db_ref) for c in children]
        result = [score, title, url_name, doc_id,
                last_mod, size, word_freq_list, parent, 
                children]
        query_results.append(result)
    pageID2Meta.close()
    return query_results

""""To-do retrive function. Should return a dictionary with output like phase 1"""
def retrive(queries):
    # queries = ["comput", "scienc"]
    url2pageID = SqliteDict('../db/url2pageID.sqlite')
    forwardIndex = SqliteDict('../db/forwardIndex.sqlite')
    docNorm = SqliteDict('../db/docNorm.sqlite')
    word2wordID = SqliteDict('../db/word2wordID.sqlite')
    invertedIndex = SqliteDict('../db/invertedIndex.sqlite')
    title2TitleID = SqliteDict('../db/title2TitleID.sqlite')
    forwardIndexTitle = SqliteDict('../db/forwardIndexTitle.sqlite')
    invertedIndexTitle = SqliteDict('../db/invertedIndexTitle.sqlite')
    titleNorm = SqliteDict('../db/titleNorm.sqlite')
    # total_doc_no = float(len(url2pageID))

    #########################################################################
    title_score_dict = {}
    title_id = -1
    for query in queries:
        if query in title2TitleID.keys():
            title_id = title2TitleID[query]
        else:
            print("Title word not indexed:", query)
            continue
        posting_list = invertedIndexTitle[title_id]
        # print(posting_list)
        for document in posting_list:
            doc_id = document[0]
            # Pre-computed tf-idf
            tf_idf = document[1]
            # Accumulate the inner product
            if doc_id not in title_score_dict:
                title_score_dict[doc_id] = [tf_idf * 1, 1]
            else:
                title_score_dict[doc_id][0] += tf_idf * 1
                title_score_dict[doc_id][1] += 1

    cos_sim_title = title_score_dict.copy()
    for doc_id, score in title_score_dict.items():
        word_list = forwardIndexTitle[doc_id]
        title_norm = titleNorm[doc_id]
        query_norm = math.sqrt(title_score_dict[doc_id][1])
        inner_prod = float(title_score_dict[doc_id][0])
        cos_sim_title[doc_id] = inner_prod / (title_norm * query_norm)
    # print(cos_sim_title)
        
    #########################################################################
    score_dict = {}
    word_id = -1
    for query in queries:
        if query in word2wordID.keys():
            word_id = word2wordID[query]
        else:
            print("Query word not indexed:", query)
            continue
        posting_list = invertedIndex[word_id]
        # df = float(len(posting_list))
        # idf = math.log(total_doc_no / df, 2)
        # tf_max = float(max([x[1] for x in posting_list]))
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
    # i = 0
    for doc_id, score in score_dict.items():
        # print(i, len(score_dict))
        # i += 1
        word_list = [x[0] for x in forwardIndex[doc_id]]
        doc_norm = docNorm[doc_id]
        query_norm = math.sqrt(score_dict[doc_id][1])
        inner_prod = float(score_dict[doc_id][0])
        cos_sim[doc_id] = inner_prod / (doc_norm * query_norm)

    # print(cos_sim)
    #########################################################################
    cos_sim_combined = cos_sim.copy()
    for doc_id, score in cos_sim_title.items():
        if doc_id in cos_sim_combined:
            cos_sim_combined[doc_id] += score
        else:
            cos_sim_combined[doc_id] = score


    cos_sim_list = list(cos_sim_combined.items())
    cos_sim_list = sorted(cos_sim_list, key=lambda x: x[1], reverse=True)

    print(cos_sim_list)
    

    db_ref = [url2pageID, forwardIndex, docNorm, word2wordID, invertedIndex]
    
    result = format_result(cos_sim_list, db_ref)
    url2pageID.close()
    forwardIndex.close()
    docNorm.close()
    word2wordID.close()
    invertedIndex.close()

    return result