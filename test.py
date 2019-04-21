from sqlitedict import SqliteDict

# Url -> PageID
url2pageID = SqliteDict('./url2pageID.sqlite', autocommit=True)
# PageID -> [PageTitle, LastModified, Size, WordFreqDict, Children]
pageID2Meta = SqliteDict('./pageID2Meta.sqlite', autocommit=True)

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



