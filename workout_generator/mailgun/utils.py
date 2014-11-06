import requests
from .constants import API_KEY


def send_email_with_data(customer_email, subject, text):
    domain = "onerepmaxcalculator.com"
    return requests.post(
        "https://api.mailgun.net/v2/%s/messages" % domain,
        auth=("api", API_KEY),
        data={"from": "One Rep Max Calculator<no-reply@OneRepMaxCalculator.com>",
              "to": customer_email,
              "subject": subject,
              "text": text})


def send_test_email():
    text = "This is totally in prod"
    title = "prod email"
    send_email_with_data("scott.lobdell@gmail.com", title, text)


def send_order_email(customer_email, order):
    url_str = "\n".join(order.get_final_image_urls())
    text = "Thanks for your business!  Your pictures can be downloaded for the next week at the following URLs:"
    text += "\n%s" % url_str
    send_email_with_data(customer_email, "Digital Picture Delivery!", text)


def send_order_confirmation_email(customer_email, order):
    text = "This email confirms your purchase from AirborneImaging.com.  "
    text += "Your credit card has been charged a total of $%s " % order.total_price
    text += "for %s pictures.  " % order.num_pictures
    text += "Your images are now being processed to the image quality specified in your order.  "
    text += "If there are any issues with your order, your order ID is %s" % order.id
    send_email_with_data(customer_email, "Order Confirmation", text)
