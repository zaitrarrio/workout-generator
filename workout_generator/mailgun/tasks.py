from celery.task import task
from .utils import send_test_email
from .utils import send_email_with_data
from .constants import ADMIN_EMAIL


def send_confirmation_email(email_address, order_id):
    text = "Thanks for your order! A bunch of scientists from down in the lab are now doing a bunch of "
    text += "sciency things to your video and making calculations.  When it's finished you'll be notified, "
    text += "but if there are any problems you can keep track of your order with:\n\n"
    text += "Order ID: %s" % order_id
    text += "\n\nThis might take over an hour, especially if a whole bunch of other meat heads are acting "
    text += "like nerds and uploading videos on the internets. In the meantime, I'll leave you with a quote:\n\n"
    text += "\"Education is important, but big arms are more important.\"\n-Abraham Lincoln"
    send_email_with_data(email_address,
                         "OneRepMaxCalculator.com Order Confirmation",
                         text)


def send_order_completion_email(email_address, final_url):
    text = "Hey your order finished!\n\n"
    text += "Final video URL: %s" % final_url
    send_email_with_data(email_address,
                         "OneRepMaxCalculator.com Digital Delivery",
                         text)


def notify_admin(exception, stack_trace):
    text = "Exception: %s\n\n" % exception
    text += stack_trace
    if hasattr(exception, "message"):
        text += "\n%s" % exception.message
    send_email_with_data(ADMIN_EMAIL, "OneRepMax Error!", text)


@task
def notify_admin_signup(facebook_service_id):
    text = "Someone signed up!\n"
    text += "Check out http://facebook.com/%s" % facebook_service_id
    send_email_with_data(ADMIN_EMAIL, "OneRepMax SignUp :) $", text)


@task
def test_send_email():
    send_test_email()
