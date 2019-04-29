from django.shortcuts import render
from .forms import QueryForm, ReQueryForm
from search.scripts import utils, retrivedb, cosineSimilarity
from django.template import Context, loader

query_results = [
    ["1", "title1", "urlname1", 0, "lastmod1", "size1", [("key1", 1), ("key2", 2)], ["p1", "p2"], ["c1", "c2"]],
    ["2", "title2", "urlname2", 1, "lastmod2", "size2", [("key1", 1), ("key2", 2)], ["p1", "p2"], ["c1", "c2"]],
    ]

def index(request):
    return render(request, 'search/index.html')


def result(request):
    if request.method == 'GET':
        form = QueryForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            print("Origin query: ", end='')
            print(query)

            # Split double quotes phrases
            queries = utils.splitQuery(query)
            # Clean, stem ...
            queries = utils.clean(queries)
            print("Processed query: ", end='')
            print(queries)
            
            print("Retriving pages ...")
            # query_results = retrivedb.retrive(queries)
            """Peter's retrive function"""
            peter_results = cosineSimilarity.runQuery(queries)
            query_results = retrivedb.reformatPeterResult(peter_results)
            print("No of related pages:" + str(len(query_results)))
            return render(request, 'search/result.html', {'query_results': query_results})
        else:
            return render(request, 'search/index.html')

def remote(request, page_id):
    template = "./search/html/" + str(page_id) + ".html"
    return render(request, template)

def similar(request):
    if request.method == 'GET':
        form = ReQueryForm(request.GET)
        if form.is_valid():
            doc_id = form.cleaned_data['docId']
            queries = retrivedb.getFreqWordAsQueryList(doc_id)
            print(queries)

            # query_results = retrivedb.retrive(queries)
            """Peter's retrive function"""
            peter_results = cosineSimilarity.runQuery(queries)
            query_results = retrivedb.reformatPeterResult(peter_results)
            return render(request, 'search/result.html', {'query_results': query_results})
        else:
            return render(request, 'search/index.html')
  
    