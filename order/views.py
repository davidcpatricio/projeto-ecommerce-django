from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render, reverse
from django.views import View
from django.views.generic import DetailView, ListView

from product.models import Variation
from utils import utils

from .models import Order, OrderItem


class DispatchLoginRequiredMixin(View):
    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('profiles:profile')

        return super().dispatch(*args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        qs = qs.filter(site_user=self.request.user)
        return qs


class Pay(DispatchLoginRequiredMixin, DetailView):
    template_name = 'order/pay.html'
    model = Order
    pk_url_kwarg = 'pk'
    context_object_name = 'order'


class SaveOrder(View):
    template_name = 'order/pay.html'

    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            messages.error(
                self.request,
                'You have to be logged in to proceed with payment.'
            )
            return redirect('profiles:profile')

        if not self.request.session.get('cart'):
            messages.error(
                self.request,
                'Your cart is empty.'
            )
            return redirect('product:product_list')

        cart = self.request.session.get('cart')
        cart_variation_ids = [v for v in cart]
        db_variations = list(
            Variation.objects.select_related('product')
            .filter(id__in=cart_variation_ids)
        )

        for variation in db_variations:
            vid = str(variation.id)

            stock = variation.stock
            cart_amount = cart[vid]['amount']
            unit_price = cart[vid]['unit_price']
            unit_promo_price = cart[vid]['unit_promo_price']

            error_msg_stock = ''

            if stock < cart_amount:
                cart[vid]['amount'] = stock
                cart[vid]['total_price'] = stock * unit_price
                cart[vid]['total_promo_price'] = stock * \
                    unit_promo_price

                error_msg_stock = 'Insufficient stock for some '\
                    'products in your cart. '\
                    'The amount of those products was reduced. Please '\
                    'check which product(s) were affected down below.'

            if error_msg_stock:
                messages.error(
                    self.request,
                    error_msg_stock
                )
                self.request.session.save()
                return redirect('product:cart')

        total_amount_cart = utils.cart_total_amount(cart)
        total_value_cart = utils.cart_total_price(cart)

        order = Order(
            site_user=self.request.user,
            total_value=total_value_cart,
            total_amount=total_amount_cart,
            status='C'
        )

        order.save()

        OrderItem.objects.bulk_create(
            [
                OrderItem(
                    order=order,
                    product=v['product_name'],
                    product_id=v['product_id'],
                    variation=v['variation_name'],
                    variation_id=v['variation_id'],
                    price=v['total_price'],
                    promo_price=v['total_promo_price'],
                    amount=v['amount'],
                    image=v['image'],
                ) for v in cart.values()
            ]
        )

        del self.request.session['cart']

        return redirect(
            reverse(
                'order:pay',
                kwargs={
                    'pk': order.pk
                }
            )
        )


class Details(DispatchLoginRequiredMixin, DetailView):
    def get(self, *args, **kwargs):
        return HttpResponse('Details')


class OrderList(DispatchLoginRequiredMixin, ListView):
    def get(self, *args, **kwargs):
        return HttpResponse('Order list')
