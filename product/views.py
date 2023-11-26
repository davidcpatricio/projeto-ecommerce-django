from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from . import models


class ProductList(ListView):
    model = models.Product
    template_name = 'product/product_list.html'
    context_object_name = 'products'
    paginate_by = 10


class ProductDetails(DetailView):
    model = models.Product
    template_name = 'product/details.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'


class AddToCart(View):
    def get(self, *args, **kwargs):
        http_referer = self.request.META.get(
            'HTTP_REFERER',
            reverse('product:product_list')
        )
        variation_id = self.request.GET.get('vid')

        if not variation_id:
            messages.error(
                self.request,
                'Product does not exist.'
            )
            return redirect(http_referer)

        variation = get_object_or_404(models.Variation, id=variation_id)
        variation_stock = variation.stock
        product = variation.product

        product_id = product.id
        product_name = product.name
        variation_name = variation.name or ''
        unit_price = variation.price
        unit_promo_price = variation.promo_price
        amount = 1
        slug = product.slug
        image = product.image

        image = image.name if image else ''

        if variation.stock < 1:
            messages.error(
                self.request,
                'Insufficient stock.'
            )
            return redirect(http_referer)

        if not self.request.session.get('cart'):
            self.request.session['cart'] = {}
            self.request.session.save()

        cart = self.request.session['cart']

        if variation_id in cart:
            # TODO : Variation exists in cart
            amount_cart = cart[variation_id]['amount']
            amount_cart += 1

            if variation_stock < amount_cart:
                messages.warning(
                    self.request,
                    f'Insufficent stock for {amount_cart} unit(s) of '
                    f'product "{product_name}". {variation_stock} unit(s) '
                    f'were added to your cart instead.'
                )
                amount_cart = variation_stock

            cart[variation_id]['amount'] = amount_cart
            cart[variation_id]['total_price'] = unit_price * \
                amount_cart
            cart[variation_id]['total_promo_price'] = unit_promo_price * \
                amount_cart
        else:
            # TODO : Variation does not exist in cart
            cart[variation_id] = {
                'product_id': product_id,
                'product_name': product_name,
                'variation_name': variation_name,
                'variation_id': variation_id,
                'unit_price': unit_price,
                'unit_promo_price': unit_promo_price,
                'total_price': unit_price,
                'total_promo_price': unit_promo_price,
                'amount': 1,
                'slug': slug,
                'image': image,
            }

        self.request.session.save()

        messages.success(
            self.request,
            f'Product "{product_name} {variation_name}" was added to your '
            f'cart ({cart[variation_id]["amount"]}x).'
        )

        return redirect(http_referer)


class RemoveFromCart(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Remove from cart')


class Cart(View):
    def get(self, *args, **kwargs):
        return render(self.request, 'product/cart.html')


class Checkout(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Checkout')
