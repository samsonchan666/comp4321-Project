from django.shortcuts import render
from .forms import QueryForm
from search.scripts import utils

query_results = [
    ["1", "title1", "url1", "lastmod1", "size1", {"key1": 1, "key2":2}, ["p1", "p2"], ["c1", "c2"]],
    ["2", "title2", "url2", "lastmod2", "size2", {"key1": 1, "key2":2}, ["p1", "p2"], ["c1", "c2"]],
    ]

def index(request):
    return render(request, 'search/index.html')


def result(request):
    if request.method == 'GET':
        form = QueryForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            """"To do - double quotes phrases"""
            # queries = query.split()
            queries = utils.splitQuery(query)

            """ To do - Retrival function """
            url2pageID = utils.retriveWebPageInfo()
            # result = utils.retrive()
            # queries = utils.tokenizeAndClean(query)
            return render(request, 'search/result.html', {'query_results': query_results})
        else:
            return render(request, 'search/index.html')
  
    