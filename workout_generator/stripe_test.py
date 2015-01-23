import stripe
stripe.api_key = ""
customer = stripe.Customer.retrieve("cus_5Sy5EGguaJ96vc")
customer.to_dict()["delinquent"]

for subscription in customer.to_dict()["subscriptions"]["data"]:
    subscription_plan = subscription["plan"]["id"]
    if subscription_plan == "whatever_my_plan_is":
        pass  # WE ARE GOOD

customer.cancel_subscription(at_period_end=True)


customer.update_subscription(card="tokenstr")
