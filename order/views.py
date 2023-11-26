from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import DetailView, ListView


class Pay(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Pay')


class CloseOrder(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Close order')


class Details(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Details')
