###This part is to calculate and rank the cosine similarity for a query and the collections of webpages###
###The result is stored in resultRank variable which has a sorted list with cosine similarity and each element is is dictionary type containing the information of webpage###

import math, sqlitedict

logBase=10	#This is for idf calculation but the value doesnt matter (but need to be greater than 1), since the idf value will be ranked
multiplier=3	#This is the multiplier for the title cosine similarity

# import os
# os.chdir("/Users/apple/Downloads/comp4321-Project-master")

url2pageID = sqlitedict.SqliteDict("./db/url2pageID.sqlite", autocommit=True)
pageID2Meta = sqlitedict.SqliteDict("./db/pageID2Meta.sqlite", autocommit=True)
forwardIndexTitle = sqlitedict.SqliteDict("./db/forwardIndexTitle.sqlite", autocommit=True)
title2TitleID = sqlitedict.SqliteDict("./db/title2TitleID.sqlite", autocommit=True)

#Calculate the TFIDF value for each word for each document, each element will be stored in a dictionary and result will be stored as a list
def calcTFIDF(termFreq, invDocFreq):
	tfidf=[]
	for documentTF in termFreq:
		tfidf.append({})
		for eachWord in documentTF:
			tfidf[-1][eachWord]=documentTF[eachWord]*invDocFreq[eachWord]
	return tfidf

#Convert a query to a dictionary with key=eachWord and value=numberOfOccurance
def convertQueryStringToDict(queryString):
	queryDict={}
	for i in queryString.split():
		if i in queryDict:
			queryDict[i]+=1
		else:
			queryDict[i]=1
	return queryDict

def convertQueryToDict(queryList):
	queryDict={}
	for i in queryList:
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
#Then transfer the format to a dictionary webpageIndex:correspondingWebpageInfo
def rankCosSimAndGiveWebLink(cosSimDict):
	#print(cosSimDict)
	rankPageIndex=[]
	sortedWebRankDict={}

	#Sort the cosSimDict dictionary to a list rankPageIndex
	for i in sorted(cosSimDict.items(), key=lambda kv:kv[1], reverse=True):
		rankPageIndex.append(i[0])
	#print(rankPageIndex)

	#Generate a dictionary with descending cosine similarity order with webpage index as key and its information as list
	for i in range(len(rankPageIndex)):
		for key,value in url2pageID.iteritems():
			if rankPageIndex[i]==value:
				#sortedWebRankDict[key]=cosSimDict[rankPageIndex[i]]
				sortedWebRankDict[value]=(cosSimDict[value],key)
				break

	return sortedWebRankDict

#Given termFreq variable, it will give each term inverse document frequency, which will be stored in a dictionary
#Note that it is assume that the termFreq variable keys are in small letter
def calcIDFFromTF(termFreq):
	invDocFreq={}
	for i in termFreq:
		for eachWord in i:
			try:
				invDocFreq[eachWord]+=1
			except:
				invDocFreq[eachWord]=1
		invDocFreq[eachWord]=math.log(len(termFreq)/invDocFreq[eachWord], logBase)
	return invDocFreq


#Given all documents sentences, it will give each term frequency of each document, which each element will be stored in a dictionary and result will be stored as a list
def countTFFromDocuments(documents):
	termFreq=[]
	for document in documents:
		termFreq.append({})
		for eachWord in document.split():
			if eachWord.lower() in termFreq[-1]:
				termFreq[-1][eachWord.lower()]+=1
			else:
				termFreq[-1][eachWord.lower()]=1
	return termFreq

def makeTitleList():
	titleList=[]
	for i in forwardIndexTitle:
		titleList.append([])
		for j in forwardIndexTitle[i]:
			for k in title2TitleID:
				if j==title2TitleID[k]:
					titleList[-1].append(k)
					break
	return titleList

def countTFFromLists(lists):
	termFreq=[]
	for eachList in lists:
		termFreq.append({})
		for eachWord in eachList:
			if eachWord.lower() in termFreq[-1]:
				termFreq[-1][eachWord.lower()]+=1
			else:
				termFreq[-1][eachWord.lower()]=1
	return termFreq

#Given all documents sentences, it will give each term inverse document frequency, which will be stored in a dictionary
def calcIDFFromDocuments(documents):
	invDocFreq={}
	#list(dict.fromkeys(" ".join(documents).split())) eqv to non-duplicate words in the whole doicument
	for eachWord in list(dict.fromkeys(" ".join(documents).lower().split())):
		count=0
		for document in documents:
			if eachWord in document.lower().split():
				count+=1
		invDocFreq[eachWord]=math.log(len(documents)/count, logBase)
	return invDocFreq

#Combine the two input-parameter generated by rankCosSimAndGiveWebLink() function and then sort the cosine similarity in reverse order
def combineToList(resultUsingTitle,resultUsingContent):
	combined=[]
	for i in resultUsingTitle:
		combined.append({})
		combined[-1]["index"]=i
		combined[-1]["link"]=resultUsingTitle[i][1]
		combined[-1]["titleSimilarity"]=resultUsingTitle[i][0]
		combined[-1]["contentSimilarity"]=resultUsingContent[i][0]
		combined[-1]["totalSimilarity"]=(resultUsingTitle[i][0]*multiplier+resultUsingContent[i][0])/(1+multiplier)
		combined[-1]["meta"]=pageID2Meta[i]
		#combined.sort(key=lambda x: (x["titleSimilarity"], x["contentSimilarity"]),reverse=True)
		combined.sort(key=lambda x: (x["totalSimilarity"]),reverse=True)
	return combined

def runQuery(query):
	##Given a query, we make it into smaller letter and convery it to a dictionary
	#queryString=query.strip()
	#queryString=" ".join(queryString.lower().split())
	#print(queryString)
	# query=query.split()
	queryDict=convertQueryToDict(query)

	#This part calculate the TFIDF value for the title for each document (which can be preloded)
	#tfidf variable is in format list where each element is a document dictionary key:value = word:tfidfValue
	titleList=makeTitleList()
	termFreq=countTFFromLists(titleList)
	invDocFreq=calcIDFFromTF(termFreq)
	tfidf=calcTFIDF(termFreq, invDocFreq)

	#This is calculate the cosine similarity between query and the title
	#The result resultUsingTitle variable is in format dictionary descending cos sim order with key:value = pageIndex:cosSimValue
	cosSimQueryTitleDict=queryCosSimAllDocs(tfidf,len(titleList),queryDict)
	resultUsingTitle=rankCosSimAndGiveWebLink(cosSimQueryTitleDict)

	#This part calculate the TFIDF value for the content (which can be preloded)
	termFreq=[]
	for i in range(len(pageID2Meta)):
		termFreq.append(pageID2Meta[i][3])
	invDocFreq=calcIDFFromTF(termFreq)
	tfidf=calcTFIDF(termFreq, invDocFreq)

	#This is calculate the cosine similarity between query and the content
	cosSimQueryContentDict=queryCosSimAllDocs(tfidf,len(termFreq),queryDict)
	resultUsingContent=rankCosSimAndGiveWebLink(cosSimQueryContentDict)

	#Combine two dictionary and sort the cosine similarity first by title then by content
	#The result variable resultRank is in format list and each element is a dictionary containing (0)document index (1)document url (2)title similarity (3)content similarity (4)Metadata
	resultRank=combineToList(resultUsingTitle,resultUsingContent)
	return resultRank
	# print(resultRank)

runQuery("HKUST is the best university in hong kong. CSE is the best department in HKUST! Python is the most beautiful language in the world.")

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
#termFreq=countTFFromDocuments(documents)
#invDocFreq=calcIDFFromDocuments(documents)
#tfidf=calcTFIDF(termFreq, invDocFreq)
'''

###Testing code to rank if the above full text document is given###
'''
#These 3 variables update upon a new query
#queryDict, cosSimDict, resultWebRank = {}, {}, {}

queryString="lawyer using paralegals"
queryDict=convertQueryStringToDict(queryString)
cosSimDict=queryCosSimAllDocs(tfidf,len(documents),queryDict)
print(rankCosSimAndGiveWebLink(cosSimDict))

queryString="lawyer using paralegal"
queryDict=convertQueryStringToDict(queryString)
cosSimDict=queryCosSimAllDocs(tfidf,len(documents),queryDict)
print(rankCosSimAndGiveWebLink(cosSimDict))

queryString="lawyer lawyer paralegal paralegal stairs experiment directly significantly better precision recall"
queryDict=convertQueryStringToDict(queryString)
cosSimDict=queryCosSimAllDocs(tfidf,len(documents),queryDict)
print(rankCosSimAndGiveWebLink(cosSimDict))

queryString="lawyer directly stairs experiment significantly better precision recall paralegal"
queryDict=convertQueryStringToDict(queryString)
cosSimDict=queryCosSimAllDocs(tfidf,len(documents),queryDict)
print(rankCosSimAndGiveWebLink(cosSimDict))

queryString="this is an apple and a orange"
queryDict=convertQueryStringToDict(queryString)
cosSimDict=queryCosSimAllDocs(tfidf,len(documents),queryDict)
print(rankCosSimAndGiveWebLink(cosSimDict))
'''