from django.urls import path

from . import views

app_name = 'product'

urlpatterns = [
    path('', views.ProductList.as_view(), name='product_list'),
    path('<slug>', views.ProductDetails.as_view(), name='details'),
    path('add_to_cart/', views.AddToCart.as_view(), name='add_to_cart'),
    path('remove_from_cart/', views.RemoveFromCart.as_view(),
         name='remove_from_cart'),
    path('cart/', views.Cart.as_view(), name='cart'),
    path('order_summary/', views.OrderSummary.as_view(), name='order_summary'),
    path('search/', views.Search.as_view(), name='search'),
]
