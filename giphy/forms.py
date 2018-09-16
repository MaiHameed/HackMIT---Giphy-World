from django import forms

class QueryForm(forms.Form):
    textarea = forms.CharField(label='Query', max_length=100)
