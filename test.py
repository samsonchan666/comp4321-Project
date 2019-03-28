import pickle

# Url -> [PageID, PageTitle, LastModified, Size, WordFreqDict, Children]
url2pageID = pickle.load(open('url2pageID.p', 'rb'))
forwardIndex = pickle.load(open('forwardIndex.p', 'rb'))
word2wordID = pickle.load(open('word2wordID.p', 'rb'))
invertedIndex = pickle.load(open('invertedIndex.p', 'rb'))

text_file = open("spider_result.txt", "w")
# for url, pageData in url2pageID.items():
#     print(pageData[1])
#     print(url)
#     print(pageData[2], pageData[3])
#     for word, freq in pageData[4].items():
#         print(word, freq, ';', end='')
#     for child in pageData[5]:
#         print(child)
#     print('-------------------------------------------------------------------------------------------')
for url, pageData in url2pageID.items():
    text_file.write("%s\n" % pageData[1])
    text_file.write("%s\n" % url)
    text_file.write("%s %d\n" % (pageData[2], pageData[3]))
    for word, freq in pageData[4].items():
        text_file.write("%s %d; " % (word, freq))
    text_file.write("\n")
    for child in pageData[5]:
        text_file.write("%s\n" % child)
    text_file.write('-------------------------------------------------------------------------------------------\n')

text_file.close()

