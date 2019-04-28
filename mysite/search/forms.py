from django import forms

class QueryForm(forms.Form):
    query = forms.CharField(label='Query', max_length=100)

class ReQueryForm(forms.Form):
    docId = forms.CharField(label='Query', max_length=100)