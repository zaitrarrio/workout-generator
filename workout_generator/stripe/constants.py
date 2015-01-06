import os

TEST_SECRET_KEY = os.environ['STRIPE_TEST_SECRET_KEY']
TEST_PUBLISHABLE_KEY = os.environ['STRIPE_TEST_PUBLISHABLE_KEY']

LIVE_SECRET_KEY = os.environ['STRIPE_LIVE_SECRET_KEY']
LIVE_PUBLISHABLE_KEY = os.environ['STRIPE_LIVE_PUBLISHABLE_KEY']

SUBSCRIPTION_ID = 'test_subscription'  # make sure to change this


def get_secret_key():
    return TEST_SECRET_KEY


def get_publishable_key():
    return TEST_PUBLISHABLE_KEY
