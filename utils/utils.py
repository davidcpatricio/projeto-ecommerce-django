def format_price(val):
    return f'{val:.2f}€'.replace('.', ',')


def cart_total_amount(cart):
    return sum([item['amount'] for item in cart.values()])


def cart_total_price(cart):
    return sum(
        [
            item.get('total_promo_price')
            if item.get('total_promo_price')
            else item.get('total_price')
            for item
            in cart.values()
        ]
    )
