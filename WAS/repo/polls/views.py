from django.shortcuts import render
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

def res(req) :
    return render(req, 'res.html')