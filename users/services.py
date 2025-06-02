import stripe
from forex_python.converter import CurrencyRates

from config.settings import STRIPE_API_KEY


stripe.api_key = STRIPE_API_KEY

def convert_currency(cur_from, cur_to, amount=1):
    c = CurrencyRates()
    rate = c.get_rate(cur_from, cur_to)
    return rate * amount


def create_stripe_price(amount: int) -> stripe.Price:
    data = {
        'currency': 'rub',
        'unit_amount': amount * 100,
        'product_data': {
            'name': 'subscription'
        }
    }
    return stripe.Price.create(**data)


def create_stripe_session(price: stripe.Price, success_url, cancel_url, **metadata) -> stripe.checkout.Session:
    data = {
        'success_url': success_url,
        'cancel_url': cancel_url,
        'line_items': [{
            'price': price.get('id'),
            'quantity': 1,
        }],
        'mode': 'payment',
        'metadata': metadata
    }
    session = stripe.checkout.Session.create(**data)
    return session
