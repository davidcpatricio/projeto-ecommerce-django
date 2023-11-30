from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from profiles.models import Profile

from . import models


class ProductList(ListView):
    model = models.Product
    template_name = 'product/product_list.html'
    context_object_name = 'products'
    paginate_by = 10
    ordering = ['-id']


class Search(ProductList):
    def get_queryset(self, *args, **kwargs):
        term = self.request.GET.get('term') or self.request.session['term']
        qs = super().get_queryset(*args, **kwargs)

        if not term:
            return qs

        self.request.session['term'] = term

        qs = qs.filter(
            Q(name__icontains=term) |
            Q(short_description__icontains=term) |
            Q(long_description__icontains=term)
        )

        self.request.session.save()
        return qs


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
            # Variation exists in cart
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
            # Variation does not exist in cart
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
        http_referer = self.request.META.get(
            'HTTP_REFERER',
            reverse('product:product_list')
        )
        variation_id = self.request.GET.get('vid')

        if not variation_id:
            return redirect(http_referer)

        if not self.request.session.get('cart'):
            return redirect(http_referer)

        if variation_id not in self.request.session['cart']:
            return redirect(http_referer)

        cart = self.request.session['cart'][variation_id]

        messages.success(
            self.request,
            f'Product "{cart["product_name"]} {cart["variation_name"]}" '
            f'removed from your cart.'
        )

        del self.request.session['cart'][variation_id]
        self.request.session.save()
        return redirect(http_referer)


class Cart(View):
    def get(self, *args, **kwargs):
        context = {
            'cart': self.request.session.get('cart', {})
        }

        return render(self.request, 'product/cart.html', context)


class OrderSummary(View):
    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('profiles:profile')

        site_profile = Profile.objects.filter(
            site_user=self.request.user
        ).exists()

        if not site_profile:
            messages.error(
                self.request,
                'No profile set for this user.'
            )
            return redirect('profiles:profile')

        if not self.request.session.get('cart'):
            messages.error(
                self.request,
                'Your cart is empty.'
            )
            return redirect('product:product_list')

        context = {
            'site_user': self.request.user,
            'cart': self.request.session['cart'],
        }

        return render(self.request, 'product/order_summary.html', context)
