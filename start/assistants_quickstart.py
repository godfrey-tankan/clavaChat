# from app.utils.whatsapp_utils import  generate_response,create_subscription

# def activate_subscription():

from paynow import Paynow
import time

from paynow import Paynow


paynow = Paynow(
	'17264',
	'35848eb0-f1d7-446a-8978-e937926a8f77',
	'http://google.com',
	'http://google.com'
	)

payment = paynow.create_payment('Order', 'gtkandeya@gmail.com')


payment.add('Payment for stuff', 1)

response = paynow.send_mobile(payment, '0779586059', 'ecocash')


if(response.success):
    poll_url = response.poll_url

    print("Poll Url: ", poll_url)

    status = paynow.check_transaction_status(poll_url)

    time.sleep(30)

    print("Payment Status: ", status.status)
else:
    print(response.error)
