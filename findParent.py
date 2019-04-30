from sqlitedict import SqliteDict

# PageID -> [Parent1, Parent2 ,. ..]
pageID2Parent = SqliteDict('./db/pageID2Parent.sqlite', autocommit=True)
# PageID -> [PageTitle, LastModified, Size, WordFreqDict, Children]
pageID2Meta = SqliteDict('./db/pageID2Meta.sqlite')


def findParent(child_id):
    _parents = []
    for parent_id, meta in pageID2Meta.items():
        if int(child_id) in meta[4]:
            _parents.append(parent_id)
    return _parents


i = 0
for page_id in pageID2Meta.keys():
    print(str(i), len(pageID2Meta))
    i += 1
    parents = findParent(page_id)
    pageID2Parent[page_id] = parents

pageID2Parent.close()
pageID2Meta.close()
