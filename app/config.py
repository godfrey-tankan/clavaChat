import sys
import os
from dotenv import load_dotenv
import logging


chat_status="CHATMODE"
subs_status="SUBMODE"
payment_status="PAYMENTMODE"
welcome="WELCOMEMODE"



def load_configurations(app):
    load_dotenv()
    app.config["ACCESS_TOKEN"] = os.getenv("ACCESS_TOKEN")
    app.config["YOUR_PHONE_NUMBER"] = os.getenv("YOUR_PHONE_NUMBER")
    app.config["APP_ID"] = os.getenv("APP_ID")
    app.config["APP_SECRET"] = os.getenv("APP_SECRET")
    app.config["RECIPIENT_WAID"] = os.getenv("RECIPIENT_WAID")
    app.config["VERSION"] = os.getenv("VERSION")
    app.config["PHONE_NUMBER_ID"] = os.getenv("PHONE_NUMBER_ID")
    app.config["VERIFY_TOKEN"] = os.getenv("VERIFY_TOKEN")


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )

subs_response_default = "*YOUR FREE TRIAL HAS `EXPIRED`*\nPlease Choose `Subscription` Option\n1. Monthly Subscription\n2. Check Subscription Status\n3. Help\n4. `Exit`\n\n *Please reply with the `number` of your choice*."
subs_response1 = "Monthly Subscription Plan:\n\n*Features*\n1. Unlimited Access Message Requests\n2. 24/7 Customer Support\n3. Cancel Anytime - `guaranteed money back within first week` if you decided to change otherwise.\n\n*Pricing*\n$1/month\n\n To subscribe, please reply with, *Y* to proceed or *N* to abort."
subs_response2 = "Your subscription has been cancelled. To reactivate, please reply with *1* to subscribe."
subs_response3 = f"Your subscription expiry date is. To add a subscription, please reply with *1* to subscribe."
subs_response4 = "Thank you for your interest in our subscription plans. We offer convenient options to help you split service costs efficiently.\n\n"
subs_response4 += "Subscription Plans:\n"
subs_response4 += "- Monthly Subscription Plan\n"
subs_response4 += "- Cancel Subscription\n\n"
subs_response4 += "By subscribing, you will gain unlimited access to all features and enjoy 24/7 customer support.\n\n"
subs_response4 += "To proceed with the Monthly Subscription Plan, please reply with *1*. To cancel your subscription, please reply with *N*.\n\n"
subs_response4 += "For any inquiries or assistance, please contact our support team.\n\n `263779586059` or send direct email to `solutions@tphub.com`\n\n"
subs_response4 += "© 2023 TechProjectsHub. All rights reserved.\n"
subs_response_final4=subs_response4
subs_response5 = "Thank you for using our service. If you need any further assistance, please feel free to contact us. Have a great day!\n\n 🫰"
subs_payment_agree_response = "Your subscription is being created. You will be billed $1/month. To cancel your subscription, please reply with *2* or reply with your Ecocash mobile number in the form: `07XX` to proceed."
subs_payment_deny_response = "Your subscription request has been cancelled. To subscribe, please reply with *1*."
subs_error_response = "An error occured. Please try again later."
subs_cancel_response = "Your subscription has been cancelled. To reactivate, please reply with *1* to subscribe."
payment_response_default_response = "Subscription Options:\n1. Monthly Subscription Plan\n2. Cancel Subscription\n3. Check Subscription Status\n4. Help\n5. Exit\n\nPlease reply with the number of your choice."
ecocash_number_valid_response = "Please wait for the popup on your phone to confirm the payment. Your subscription will be activated once the payment is confirmed."
ecocash_number_invalid_response = "Invalid Ecocash mobile number. Please reply with your Ecocash mobile number in the form: `07XX` to proceed."
error_response = "An error occured. Please try again later."
eccocash_transaction_success_response = "Your subscription has been successfully activated. Thank you for subscribing to our service. Enjoy!"
transaction_message = "240313.1849.F42721."