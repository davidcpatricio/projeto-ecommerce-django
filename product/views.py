from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from . import models


class ProductList(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Product list')


class ProductDetails(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Product details')


class AddToCart(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Add to cart')


class RemoveFromCart(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Remove from cart')


class Cart(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Cart')


class Checkout(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Checkout')
