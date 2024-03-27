# from app.utils.whatsapp_utils import  generate_response,create_subscription

# def activate_subscription():

from paynow import Paynow
import time

paynow = Paynow(
    '17264', 
    '35848eb0-f1d7-446a-8978-e937926a8f77',
    'https://www.paynow.co.zw', 
    'http://google.com'
    )

payment = paynow.create_payment('Order', 'gtkandeya@gmail.com')

payment.add('Payment for stuff', 1)

response = paynow.send_mobile(payment, '0771111111', 'ecocash')


if(response.success):
    poll_url = response.poll_url

    print("Poll Url: ", poll_url)

    status = paynow.check_transaction_status(poll_url)

    time.sleep(1)

    print("Payment Status: ", status.status)
else:
    print("error something went wrong", response.error)