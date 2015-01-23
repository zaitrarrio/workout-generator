import os

from richenum import OrderedRichEnum
from richenum import OrderedRichEnumValue

TEST_SECRET_KEY = os.environ['STRIPE_TEST_SECRET_KEY']
TEST_PUBLISHABLE_KEY = os.environ['STRIPE_TEST_PUBLISHABLE_KEY']

LIVE_SECRET_KEY = os.environ['STRIPE_LIVE_SECRET_KEY']
LIVE_PUBLISHABLE_KEY = os.environ['STRIPE_LIVE_PUBLISHABLE_KEY']

SUBSCRIPTION_ID = 'basic_plan'
VALID_PLANS = [SUBSCRIPTION_ID]


def get_secret_key():
    return TEST_SECRET_KEY


def get_publishable_key():
    return TEST_PUBLISHABLE_KEY


class _SubscriptionState(OrderedRichEnumValue):
    def __init__(self, index, canonical_name, display_name):
        super(_SubscriptionState, self).__init__(index, canonical_name, display_name)


class SubscriptionState(OrderedRichEnum):
    DELINQUENT = _SubscriptionState(1, 'delinquent', 'Delinquent')
    INVALID = _SubscriptionState(2, 'invalid', 'Invalid')
    VALID = _SubscriptionState(3, 'valid', 'Valid')
