import requests
from django import forms


class ShareForm(forms.Form):
    resp = requests.get('http://127.0.0.1:8080/users/',
                        headers=dict(Authorization='Token b567feab95d27420161875fb21abe1a9e1582a0d'))
    choice = [(i['id'], i['username']) for i in resp.json()]
    user = forms.ChoiceField(choices=choice)


class LoginForm(forms.Form):
    login = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)


class TagForm(forms.Form):
    tagname = forms.CharField(required=True)


class RegisterForm(forms.Form):
    email = forms.EmailField(required=True)
    login = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)


class TaskForm(forms.Form):
    name = forms.CharField(required=True)
    completed = forms.BooleanField(required=False)
    description = forms.CharField(required=False)
    priority = forms.ChoiceField(choices=(
        ('h', 'High'),
        ('m', 'Medium'),
        ('l', 'Low'),
        ('n', 'None')
    ))
    due_date = forms.DateField(widget=forms.SelectDateWidget(), required=False)


class ListForm(forms.Form):
    name = forms.CharField(required=True)
