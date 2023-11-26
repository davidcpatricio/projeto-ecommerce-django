from django.urls import path

from . import views

app_name = 'order'

url_patterns = [
    path('', views.Pay.as_view(), name='pay'),
    path('close_order/', views.CloseOrder.as_view(), name='close_order'),
    path('details/', views.Details.as_view(), name='details'),
]
