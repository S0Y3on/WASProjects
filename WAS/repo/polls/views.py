from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404, HttpResponseNotFound
# Create your views here.

def error(req) :
    return Http404("Not Found")

def home(req) :
    return render(req, "index.html")

def xss(req) :
    return HttpResponse("Hello, world. You're at the polls xss.")

def xxe(req) :
    return HttpResponse("Hello, world. You're at the polls xxe.")

def brokenAccess(req) :
    return HttpResponse("Hello, world. You're at the polls brokenAccess.")

def brokenAuth(req) :
    return HttpResponse("Hello, world. You're at the polls brokenAuth.")

def injection(req) :
    return HttpResponse("Hello, world. You're at the polls injection.")

def about(req) :
    return HttpResponse("Hello, world. You're at the polls about.")