###This part is to calculate and rank the cosine similarity for a query (need to be amended in line 103) and the collections of webpages###
###The result is stored in rankCosSimAndGiveWebLink(cosSimDict) variable which has a dictionary type, with key:value = webpage:cosineSimilarityValue###

import math, sqlitedict

logBase=10	#This is for idf calculation but the value doesnt matter (but need to be greater than 1), since the idf value will be ranked

url2pageID = sqlitedict.SqliteDict('./db/url2pageID.sqlite', autocommit=True)
pageID2Meta = sqlitedict.SqliteDict('./db/pageID2Meta.sqlite', autocommit=True)

#Calculate the TFIDF value for each word for each document, each element will be stored in a dictionary and result will be stored as a list
def calcTFIDF(termFreq, invDocFreq):
	tfidf=[]
	for documentTF in termFreq:
		tfidf.append({})
		for eachWord in documentTF:
			tfidf[-1][eachWord]=documentTF[eachWord]*invDocFreq[eachWord]
	return tfidf

#Convert a query to a dictionary with key=eachWord and value=numberOfOccurance
def convertQueryToDict(queryString):
	queryDict={}
	for i in queryString.split():
		if i in queryDict:
			queryDict[i]+=1
		else:
			queryDict[i]=1
	return queryDict

#Calculate the cosine similarity of the query with the index-specify document
def queryCosSimEachDoc(tfidf,index,queryDict):

	#Calculate the dot product between the query and the document
	dotProduct=.0
	for eachWord in queryDict:
		#except occurs when the query word doesnt exist in the document
		try:
			dotProduct+=queryDict[eachWord]*tfidf[index][eachWord]
		except:
			pass

	#Calculate the length of the query
	lengthQueryDict=.0
	for eachWord in queryDict:
		lengthQueryDict+=queryDict[eachWord]**2
	lengthQueryDict**=.5

	#Calculate the length of the document
	lengthDocument=.0
	for eachWord in tfidf[index]:
		lengthDocument+=tfidf[index][eachWord]**2
	lengthDocument**=.5

	return dotProduct/(lengthQueryDict*lengthDocument)

#Return list of cosine similarity for query and all documents by calling queryCosSimEachDoc(tfidf,index,queryDict) function
#The return format will be dictionary with key:value -> indexOfDocument:cosineSimilarityToQuery
def queryCosSimAllDocs(tfidf,numberOfDocs,queryDict):
	cosSimDict={}
	for i in range(numberOfDocs):
		cosSimDict[i]=queryCosSimEachDoc(tfidf,i,queryDict)
	return cosSimDict

#Rank the cosSimDict according to the cosineSimilarityToQuery in descending order, with list format having indexOfDocument
#Then transfer the format to a dictionary webpageLinkOfDocument:correspondingCosineSimilarity
def rankCosSimAndGiveWebLink(cosSimDict):
	#print(cosSimDict)
	rankedCosSim=[]
	sortedWebRankDict={}

	#Sort the cosSimDict dictionary to another dictionary rankedCosSim
	for i in sorted(cosSimDict.items(), key=lambda kv:kv[1], reverse=True):
		rankedCosSim.append(i[0])
	#print(rankedCosSim)

	#Generate a dictionary with webpage as key and cosine similarity
	for i in range(len(rankedCosSim)):
		for key,value in url2pageID.iteritems():
			if rankedCosSim[i]==value:
				sortedWebRankDict[key]=cosSimDict[rankedCosSim[i]]
				break

	return sortedWebRankDict

def calcIDFFromTF(termFreq):
	invDocFreq={}
	for i in termFreq:
		#print(i)
		for eachWord in i:
			try:
				invDocFreq[eachWord]+=i[eachWord]
			except:
				invDocFreq[eachWord]=i[eachWord]
		#invDocFreq[eachWord]=math.log(len(termFreq)/invDocFreq[eachWord], logBase)
	return invDocFreq

termFreq=[]
for i in range(len(pageID2Meta)):
	termFreq.append(pageID2Meta[i][3])
invDocFreq=calcIDFFromTF(termFreq)
tfidf=calcTFIDF(termFreq, invDocFreq)

queryString="These i guess will be done by a django part".strip()
queryString=" ".join(queryString.split())
if queryString=="":
	print("Empty query!")
	exit()
queryDict=convertQueryToDict(queryString)
cosSimDict=queryCosSimAllDocs(tfidf,len(termFreq),queryDict)
print(rankCosSimAndGiveWebLink(cosSimDict))

###Unused functions, Testing code###
'''
#Given all documents sentences, it will give each term frequency of each document, which each element will be stored in a dictionary and result will be stored as a list
def countTF(documents):
	termFreq=[]
	for document in documents:
		termFreq.append({})
		for eachWord in document.split():
			if eachWord in termFreq[-1]:
				termFreq[-1][eachWord]+=1
			else:
				termFreq[-1][eachWord]=1
	return termFreq

#Given all documents sentences, it will give each term inverse document frequency, which will be stored in a dictionary
def calcIDFFromDocuments(documents):
	invDocFreq={}
	#list(dict.fromkeys(" ".join(documents).split())) eqv to non-duplicate words in the whole doicument
	for eachWord in list(dict.fromkeys(" ".join(documents).split())):
		count=0
		for document in documents:
			if eachWord in document.split():
				count+=1
		invDocFreq[eachWord]=math.log(len(documents)/count, logBase)
	return invDocFreq
'''

###Testing code for current directory###
'''
import os
os.chdir("/Users/apple/Downloads/comp4321-Project-master")
'''

###Testing code if full text document is given###
'''
documents=[]
documents.append("lawyer directly stairs paralegal experiment lawyer significantly better precision recall paralegal")
documents.append("this is a sample a")
documents.append("this is another example another example example")
'''

###Testing code if full text document is given###
'''
#These 3 variables can be preload
#termFreq, invDocFreq, tfidf = [], {}, []
#termFreq=countTF(documents)
#invDocFreq=calcIDFFromDocuments(documents)
#tfidf=calcTFIDF(termFreq, invDocFreq)
'''

###Testing code to rank if the above full text document is given###
'''
#These 3 variables update upon a new query
#queryDict, cosSimDict, resultWebRank = {}, {}, {}

queryString="lawyer using paralegals"
queryDict=convertQueryToDict(queryString)
cosSimDict=queryCosSimAllDocs(tfidf,len(documents),queryDict)
print(rankCosSimAndGiveWebLink(cosSimDict))

queryString="lawyer using paralegal"
queryDict=convertQueryToDict(queryString)
cosSimDict=queryCosSimAllDocs(tfidf,len(documents),queryDict)
print(rankCosSimAndGiveWebLink(cosSimDict))

queryString="lawyer lawyer paralegal paralegal stairs experiment directly significantly better precision recall"
queryDict=convertQueryToDict(queryString)
cosSimDict=queryCosSimAllDocs(tfidf,len(documents),queryDict)
print(rankCosSimAndGiveWebLink(cosSimDict))

queryString="lawyer directly stairs experiment significantly better precision recall paralegal"
queryDict=convertQueryToDict(queryString)
cosSimDict=queryCosSimAllDocs(tfidf,len(documents),queryDict)
print(rankCosSimAndGiveWebLink(cosSimDict))

queryString="this is an apple and a orange"
queryDict=convertQueryToDict(queryString)
cosSimDict=queryCosSimAllDocs(tfidf,len(documents),queryDict)
print(rankCosSimAndGiveWebLink(cosSimDict))
'''