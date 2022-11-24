from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse('Hello, World. You`re at the polls index.')


def base(request):
    return HttpResponse('this is the base page')


def top(request):
    return HttpResponse('3')
