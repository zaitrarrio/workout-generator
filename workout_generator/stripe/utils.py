import stripe
from .constants import get_secret_key
from .constants import SUBSCRIPTION_ID
from .constants import VALID_PLANS
from .constants import SubscriptionState


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

    try:
        customer = stripe.Customer.create(
            card=stripe_token,
            plan=SUBSCRIPTION_ID,
            email=customer_email
        )
    except stripe.CardError as e:
        return False, e.message
    return True, customer.id


def _get_stripe_customer(user):
    stripe.api_key = get_secret_key()
    customer = stripe.Customer.retrieve(user.stripe_customer_id)
    return customer


def validate_user_payment(user):
    if not user.stripe_customer_id:
        return SubscriptionState.INVALID

    customer = _get_stripe_customer(user)
    if customer.to_dict()["delinquent"]:
        return SubscriptionState.DELINQUENT

    for subscription in customer.to_dict()["subscriptions"]["data"]:
        subscription_plan = subscription["plan"]["id"]
        if subscription_plan in VALID_PLANS:
            return SubscriptionState.VALID
    return SubscriptionState.INVALID


def cancel_subscription(user):
    customer = _get_stripe_customer(user)
    customer.cancel_subscription(at_period_end=True)


def change_credit_card(user, new_token):
    customer = _get_stripe_customer(user)
    customer.update_subscription(plan=SUBSCRIPTION_ID, card=new_token)
