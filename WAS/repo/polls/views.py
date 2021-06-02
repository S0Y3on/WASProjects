from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse
from django.http import Http404, HttpResponseNotFound
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

def selectTools(req) :
    nextpage = "/index/"
    idpw = False
    isEmpty = True
    if req.method == "POST" :
        tools = req.POST.getlist("tools")
        if len(tools) >= 1 :
            isEmpty = False
        if not isEmpty :
            if(tools[-1] == "Broken Access Control") :
                idpw = True
            elif(tools[-1] == "Broken Authentication") :
                idpw = True
    if not isEmpty :
        if idpw :
            return render(req, 'idpw.html', {'tools' : tools})
        else :
            return render(req, 'res.html', {'tools' : tools})
    else :
        return render(req, 'check.html')

def getIDPW(req) :
    if req.method == "POST":
        id = req.POST.get("id")
        pw = req.POST.get("pw")
        tools = req.POST.getlist("tools")
    if id != '' and pw != '':
        return render(req, 'res.html', {"tools" : tools})
    return render(req, 'idpw.html')
