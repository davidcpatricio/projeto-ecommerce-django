from django.urls import path

from . import views

app_name = 'order'

urlpatterns = [
    path('pay/<int:pk>', views.Pay.as_view(), name='pay'),
    path('save/', views.SaveOrder.as_view(), name='save'),
    path('list/', views.OrderList.as_view(), name='list'),
    path('details/<int:pk>', views.Details.as_view(), name='details'),
]
