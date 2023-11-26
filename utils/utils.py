def format_price(val):
    return f'{val:.2f}€'.replace('.', ',')


def cart_total_amount(cart):
    return sum([item['amout'] for item in cart.values()])


def cart_totals(cart):
    return sum(
        [
            item.get('promo_total_price')
            if item.get('promo_total_price')
            else item.get('total_price')
            for item
            in cart.values()
        ]
    )
