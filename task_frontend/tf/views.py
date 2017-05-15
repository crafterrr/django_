from django.shortcuts import render
import requests
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django import forms


def send_request(url, datadict, req_type, session):
    url = 'http://127.0.0.1:8080/{}'.format(url)
    try:
        tkn = dict(Authorization='Token {}'.format(session['api_token']))
        if datadict:
            resp = req_type(url, datadict, headers=tkn)
        else:
            resp = req_type(url, headers=tkn)
    except KeyError:
        return JsonResponse({"detail": "You are not logged in"}, status=401)
    return resp


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


def list_share_view(request, pk):
    resp = send_request('todolists/{}/'.format(pk), {}, requests.get, request.session)
    if request.method == 'POST':
        form = ShareForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['user']
            data = {'name': resp.json()['name']}
            data['shared'] = resp.json()['shared']
            data['shared'].append(username)
            resp = send_request('todolists/{}/'.format(pk), data, requests.put, request.session)
            if resp.status_code == 403:
                return HttpResponse(resp.content, status=403)
            if resp.status_code == 401:
                return HttpResponseRedirect('http://127.0.0.1:8000/login/')
            return HttpResponseRedirect('http://127.0.0.1:8000/todolists/')
    else:
        form = ShareForm()
    return render(request, 'tf/list_edit.html', {'form': form})


def register(request):
    if 'api_token' in dict(request.session).keys():
        return HttpResponseRedirect('http://127.0.0.1:8000/todolists/')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['login']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            resp = requests.post('http://127.0.0.1:8080/register/',
                                 {'username': username, 'password': password, 'email': email})
            if resp.status_code == 403:
                return HttpResponse(resp.json()['detail'], status=403)
            return HttpResponse(resp.json()['detail'])
    else:
        form = RegisterForm()
    return render(request, 'tf/register.html', {'form': form})


def log_out(request):
    if 'api_token' in dict(request.session).keys():
        request.session.pop('api_token')
    return HttpResponseRedirect('http://127.0.0.1:8000/login/')

def login(request):
    if 'api_token' in dict(request.session).keys():
        return HttpResponseRedirect('http://127.0.0.1:8000/todolists/')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['login']
            password = form.cleaned_data['password']
            resp = requests.post('http://127.0.0.1:8080/token/',
                                 {'username': username, 'password': password})
            if resp.status_code == 403:
                return HttpResponse(resp.content, status=403)
            request.session['api_token'] = resp.json()['token']
            return HttpResponseRedirect('http://127.0.0.1:8000/todolists/')
            # return HttpResponse('Your access token is {}'.format(resp.json()['token']))
    else:
        form = LoginForm()
    return render(request, 'tf/login.html', {'form': form})


def lists_view(request):
    resp = send_request('todolists/', {}, requests.get, request.session)
    resp_sh = send_request('todolists/shared/', {}, requests.get, request.session)
    if resp.status_code == 401:
        return HttpResponseRedirect('http://127.0.0.1:8000/login/')
    return render(request, 'tf/lists.html', {'todo_lists': resp.json(), 'shared_lists': resp_sh.json()})


def list_details_view(request, list_id):
    resp = send_request('todolists/{}/tasks'.format(list_id), {}, requests.get, request.session)
    if resp.status_code == 401:
        return HttpResponseRedirect('http://127.0.0.1:8000/login/')
    return render(request, 'tf/list_details.html',
                  {'tasklist': resp.json()})


def list_shared_details_view(request, pk):
    resp = send_request('todolists/shared/{}/'.format(pk), {}, requests.get, request.session)
    if resp.status_code == 401:
        return HttpResponseRedirect('http://127.0.0.1:8000/login/')
    return render(request, 'tf/shlist_details.html',
                  {'tasklist': resp.json()})


def list_edit_view(request, pk):
    resp = send_request('todolists/{}/'.format(pk), {}, requests.get, request.session)
    if resp.status_code == 401:
        return HttpResponseRedirect('http://127.0.0.1:8000/login/')
    if request.method == 'POST':
        form = ListForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            resp = send_request('todolists/{}/'.format(pk), {'name': name}, requests.put, request.session)
            if resp.status_code == 403:
                return HttpResponse(resp.content, status=403)
            if resp.status_code == 401:
                return HttpResponseRedirect('http://127.0.0.1:8000/login/')
            return HttpResponseRedirect('http://127.0.0.1:8000/todolists/')
    else:
        form = ListForm(resp.json())
    return render(request, 'tf/list_edit.html', {'form': form})


def list_create_view(request):
    if request.method == 'POST':
        form = ListForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            resp = send_request('todolists/', {'name': name}, requests.post, request.session)
            if resp.status_code == 403:
                return HttpResponse(resp.content, status=403)
            if resp.status_code == 401:
                return HttpResponseRedirect('http://127.0.0.1:8000/login/')
            return HttpResponseRedirect('http://127.0.0.1:8000/todolists/')
    else:
        form = ListForm()
    return render(request, 'tf/list_edit.html', {'form': form})


def task_details_view(request, list_id, pk):
    url = 'todolists/{}/tasks/{}/'.format(list_id, pk)
    res = send_request(url, {}, requests.get, request.session)
    if res.status_code == 401:
        return HttpResponseRedirect('http://127.0.0.1:8000/login/')
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            tag = form.cleaned_data['tagname']
            resp = send_request('{}tags/'.format(url), {'name': tag}, requests.post, request.session)
            if resp.status_code == 403:
                return HttpResponse(resp.content, status=403)
            return HttpResponseRedirect('http://127.0.0.1:8000/{}'.format(url))
    else:
        form = TagForm()
    return render(request, 'tf/task_details.html', {'task': list(res.json().items()), 't': res.json(), 'form': form})


def task_edit_view(request, list_id, pk):
    resp = send_request('todolists/{}/tasks/{}/'.format(list_id, pk), {}, requests.get, request.session)
    if resp.status_code == 401:
        return HttpResponseRedirect('http://127.0.0.1:8000/login/')
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            resp = send_request('todolists/{}/tasks/{}/'.format(list_id, pk), form.cleaned_data, requests.put,
                                request.session)
            if resp.status_code == 403:
                return HttpResponse(resp.content, status=403)
            if resp.status_code == 401:
                return HttpResponseRedirect('http://127.0.0.1:8000/login/')
            return HttpResponseRedirect('http://127.0.0.1:8000/todolists/{}/tasks/'.format(list_id))
    else:
        form = TaskForm(resp.json())
    return render(request, 'tf/task_edit.html', {'form': form})


def task_create_view(request, list_id):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            resp = send_request('todolists/{}/tasks/'.format(list_id), form.cleaned_data, requests.post,
                                request.session)
            if resp.status_code == 403:
                return HttpResponse(resp.content, status=403)
            if resp.status_code == 401:
                return HttpResponseRedirect('http://127.0.0.1:8000/login/')
            return HttpResponseRedirect('http://127.0.0.1:8000/todolists/{}/tasks/'.format(list_id))
    else:
        form = TaskForm()
    return render(request, 'tf/task_edit.html', {'form': form})


def list_delete(request, pk):
    resp = send_request('todolists/{}/'.format(pk), None, requests.delete, request.session)
    if resp.status_code == 403:
        return HttpResponse(resp.content, status=403)
    if resp.status_code == 401:
        return HttpResponseRedirect('http://127.0.0.1:8000/login/')
    return HttpResponseRedirect('http://127.0.0.1:8000/todolists/')


def task_delete(request, list_id, pk):
    resp = send_request('todolists/{}/tasks/{}/'.format(list_id, pk), None, requests.delete, request.session)
    if resp.status_code == 403:
        return HttpResponse(resp.content, status=403)
    if resp.status_code == 401:
        return HttpResponseRedirect('http://127.0.0.1:8000/login/')
    return HttpResponseRedirect('http://127.0.0.1:8000/todolists/{}/tasks/'.format(list_id))
