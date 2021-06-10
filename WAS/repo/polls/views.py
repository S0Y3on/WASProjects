from django.shortcuts import render
from django.http import Http404
from .mongoManager import *
import sys
sys.path.insert(0,'/root/WASProjects/')
from main import startApp
# Create your views here.

def error(req) :
    return Http404("Not Found")

def home(req) :
    return render(req, "index.html")

def input(req) :
    return render(req, 'input.html')

def check(req) :
    return render(req, 'check.html')
    
def idpw(req) :
    return render(req, 'idpw.html')

def res(req) :
    return render(req, 'res.html')

def getURL(req) :
    url = ''
    if req.method == "POST" :
        url = req.POST.get("url")
    return render(req, 'check.html', {'url' : url})

def selectTools(req) :
    idpw = True
    isEmpty = True
    user = {
        "id" : '',
        "password" : ''
    }
    if req.method == "POST" :
        tools = req.POST.getlist("tools")
        url = req.POST.get("url")
        if len(tools) >= 1 :
            isEmpty = False
        if not isEmpty and (tools[-1] == "XXE" or tools[-1] == "Injection") :
            idpw = False
    if not isEmpty :
        if idpw :
            return render(req, 'idpw.html', {'tools' : tools, 'url' : url})
        else :
            startApp(url, tools, user)
            data = mongoManage(url)
            return render(req, 'res.html', {'tools' : tools, 'data' : data})
    else :
        return render(req, 'check.html')

def getIDPW(req) :
    user = {
        "id" : '',
        "password" : ''
    }
    url = ''
    tools = []
    data = {None}
    if req.method == "POST":
        user["id"] = req.POST.get("id")
        user["password"] = req.POST.get("pw")
        url = req.POST.get("url")
        tools = req.POST.getlist("tools")
    print(1)
    if user["id"] != '' and user["password"] != '':
        startApp(url, tools, user)
        data = mongoManage(url)
        
        return render(req, 'res.html', {"tools" : tools, "data" : data})
    return render(req, 'idpw.html')

def mongoManage(url) :
    coll = mongoManager(url)
    #data = coll.searchDB()
    asdf = coll.testSample()
    print(4)
    data = {}
    return data