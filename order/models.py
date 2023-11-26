from django.contrib.auth.models import User
from django.db import models


class Order(models.Model):
    site_user = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.FloatField()
    status = models.CharField(
        default="C",
        max_length=1,
        choices=(
            ('A', 'Approved'),
            ('C', 'Created'),
            ('U', 'Unapproved'),
            ('P', 'Pending'),
            ('S', 'Sent'),
            ('D', 'Done'),
        )
    )

    def __str__(self):
        return f'Order nr. {self.pk}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.CharField(max_length=255)
    product_id = models.PositiveIntegerField()
    variation = models.CharField(max_length=255)
    variation_id = models.PositiveIntegerField()
    price = models.FloatField()
    promo_price = models.FloatField(default=0)
    amount = models.PositiveIntegerField()
    image = models.CharField(max_length=2000)

    def __str__(self):
        return f'Item from {self.order}'
