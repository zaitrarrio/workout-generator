import stripe
from .constants import get_secret_key
from .constants import SUBSCRIPTION_ID


def charge_card(stripe_token, amount_in_cents, user_id, customer_email):
    stripe.api_key = get_secret_key()
    try:
        stripe.Charge.create(
            amount=amount_in_cents,
            currency="usd",
            card=stripe_token,
            description="Credits added for user %s: %s" % (user_id, customer_email)
        )
    except stripe.CardError as e:
        return False, e.message
    return True, ""


def create_subscription(stripe_token, customer_email):
    stripe.api_key = get_secret_key()

    customer = stripe.Customer.create(
        card=stripe_token,
        plan=SUBSCRIPTION_ID,
        email=customer_email
    )
    return customer.id
