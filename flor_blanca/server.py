
from flask import redirect,Blueprint

import stripe
# This is your test secret API key.
stripe.api_key = 'sk_test_51LIRtEAEZk4zaxmwgkvrQLY710xrEQxpWy6wDfNbGB5dH7fnI8Z86XHp1d2Su0qFVV5D7YCMwao8J3UGSMinxJaM004g6MLmcl'



bp = Blueprint('checkout', __name__, url_prefix='/checkout')

YOUR_DOMAIN = 'http://localhost:5000'

@bp.route('/create-checkout-session', methods=['POST','GET'])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID of the product you want to sell
                    'price': 'price_1Na07qAEZk4zaxmwdQNDGBsk',
                    'quantity': 1,
                }
            ],
            mode='subscription',
            success_url=YOUR_DOMAIN + '/success.html',
            cancel_url=YOUR_DOMAIN + '/cancel.html',
        )
        return redirect(checkout_session.url, code=303)    
    except Exception as e:
        return str(e)




# YOUR_DOMAIN = 'http://localhost:4242'