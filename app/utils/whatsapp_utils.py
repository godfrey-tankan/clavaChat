import logging
from datetime import datetime
from datetime import timedelta
from flask import current_app, jsonify
import json
import requests
import openai
# from app.services.openai_service import generate_response
import re
from openai import ChatCompletion
from sqlalchemy.ext.declarative import declarative_base
from colorama import Fore, Style
from datetime import datetime
from .model import Subscription, session
from app.config import chat_status, subs_status, payment_status, welcome




today = datetime.now().date()
def create_subscription(mobile_number,user_name, subscription_status):
    if Subscription.exists(session, mobile_number):
        sub_end = session.query(Subscription).filter_by(mobile_number=mobile_number).first()
        if sub_end.trial_end_date < today:
            message = "expired"
            sub_end.user_status = subs_status
            session.commit()
            return message
        else:
            pass
            return subscription_status
    else:
        subscription = Subscription(
            mobile_number=mobile_number,
            subscription_status=subscription_status,
            user_name=user_name,
            trial_start_date=today,
            trial_end_date=today - timedelta(days=1),
            user_status=chat_status
        )
        session.add(subscription)
        session.commit()
    message = "created"
    return message

def log_http_response(response):
    pass
    # logging.info(f"Status: {response.status_code}")
    # logging.info(f"Content-type: {response.headers.get('content-type')}")
    # logging.info(f"Body: {response.text}")

def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )

openai.api_key = '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'
conversation = []

def generate_response(response, wa_id, name):
    global conversation
    try:
        user_status_mode = session.query(Subscription).filter_by(mobile_number=wa_id[0]).first().user_status
    except Exception as e:
        user_status_mode = welcome
    try:
        Subscription_status = create_subscription(wa_id[0], name, "Free Trial")
    except Exception as e:
        Subscription_status = "error"
    conversation.append({"role": "user", "content": response})
    if Subscription_status == "created":
        response = f" Hi {name}\nYour Free trial subscription has been created. You have a free trial for 7 days. expiring on {today + timedelta(days=7)} reply with word *help* to learn more!.\n Enjoy a happy chat with clava \n  Regards,\n *tnqn*."
        return response
    elif Subscription_status == "expired":
        if  user_status_mode == subs_status:
            response = activate_subscription(wa_id,user_status_mode,response)
            return response
        response = "*YOUR FREE TRIAL HAS `EXPIRED`*\nPlease Choose `Subscription` Option\n1. Monthly Subscription\n2. Check Subscription Status\n3. Help\n4. `Exit`\n\n *Please reply with the `number` of your choice*."
        return response
    else:
        if response.lower().endswith("bypasslimit"):
            response = ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": conversation[i]["content"]} for i in range(len(conversation))
                ],
                max_tokens=4000,
                temperature=0.7,
                n=1,
                stop=None
            )
            conversation.append({"role": "assistant", "content": response.choices[0].message.content.strip("bypasslimit")})
        elif response.lower() in ["who are you?", "what is your name", "where are you from", "who made you?", "who is tankan", "tankan"]:
            response = "I am tankan's assistant. I am here to help you with anything you need."
            return response

        else:
            response = ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": conversation[i]["content"]} for i in range(len(conversation))
                ],
                max_tokens=1000,
                temperature=0.7,
                n=1,
                stop=None
            )
            conversation.append({"role": "assistant", "content": response.choices[0].message.content.strip()})

        return response.choices[0].message.content.strip()

def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }
    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"
    try:
        response = requests.post(
            url, data=data, headers=headers, timeout=10
        )  
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.Timeout:
        pass
        # logging.error("Timeout occurred while sending message")
        # return jsonify({"status": "error", "message": "Request timed out"}), 408
    except (    
        requests.RequestException
    ) as e:  # This will catch any general request exception
        pass
        # logging.error(f"Request failed due to: {e}")
        # return jsonify({"status": "error", "message": "Failed to send message"}), 500
    else:
        # Process the response as normal
        log_http_response(response)
        return response

def process_text_for_whatsapp(text):
    pattern = r"\【.*?\】"
    text = re.sub(pattern, "", text).strip()
    pattern = r"\*\*(.*?)\*\*"

    replacement = r"*\1*"

    whatsapp_style_text = re.sub(pattern, replacement, text)

    return whatsapp_style_text

def process_whatsapp_message(body):
    data = body
    # phone_number_id = data['entry'][0]['changes'][0]['value']['metadata']['phone_number_id']
    phone_number_id =  [contact['wa_id'] for contact in data['entry'][0]['changes'][0]['value']['contacts']]

    # Extract messages text
    messages_text = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
    # Extract profile name
    profile_name = data['entry'][0]['changes'][0]['value']['contacts'][0]['profile']['name']

    wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]

    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    message_body = message["text"]["body"]

    # TODO: implementation of cutom function
    response = generate_response(message_body, phone_number_id, profile_name)
    # OpenAI Integration
    # response = generate_response(message_body, wa_id, name)
    # response = process_text_for_whatsapp(response)

    data = get_text_message_input(current_app.config["RECIPIENT_WAID"], response)
    send_message(data)

def is_valid_whatsapp_message(body):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )

def colorize_text(text, color):
    colored_text = f"{color}{text}{Style.RESET_ALL}"
    return colored_text

def activate_subscription(wa_id,status,message):
    expired_on = "YYYY-MM-DD"
    try:
        if status ==subs_status:
            try:
                response = "*YOUR FREE TRIAL HAS `EXPIRED`*\nPlease Choose `Subscription` Option\n1. Monthly Subscription\n2. Check Subscription Status\n3. Help\n4. `Exit`\n\n *Please reply with the `number` of your choice*."
                response1 = "Monthly Subscription Plan:\n\n*Features*\n1. Unlimited Access Message Requests\n2. 24/7 Customer Support\n3. Cancel Anytime - `guaranteed money back within first week` if you decided to change otherwise.\n\n*Pricing*\n$1/month\n\n To subscribe, please reply with, *Y* to proceed or *N* to abort."
            except Exception as e:
                response = "An error occured. Please try again later."
                return response
            else:
                if message == "1" or message=="1.": 
                    response = response1
                    return response
                if message == "2" or message=="2.":
                    response = "Your subscription has been cancelled. To reactivate, please reply with *1* to subscribe."
                    return response
                elif message == "3" or message=="3.":
                    response = f"Your subscription expiry date is {expired_on}. To add a subscription, please reply with *1* to subscribe."
                    return response
                elif message == "4" or message=="4.":
                    response = "Thank you for your interest in our subscription plans. We offer convenient options to help you split service costs efficiently.\n\n"
                    response += "Subscription Plans:\n"
                    response += "- Monthly Subscription Plan\n"
                    response += "- Cancel Subscription\n\n"
                    response += "By subscribing, you will gain unlimited access to all features and enjoy 24/7 customer support.\n\n"
                    response += "To proceed with the Monthly Subscription Plan, please reply with *1*. To cancel your subscription, please reply with *N*.\n\n"
                    response += "For any inquiries or assistance, please contact our support team.\n\n `263779586059` or send direct email to `solutions@tphub.com`\n\n"
                    response += "© 2023 TechProjectsHub. All rights reserved.\n"
                    return response
                elif message == "5" or message=="5.":
                    response = "Thank you for using our service. If you need any further assistance, please feel free to contact us. Have a great day!\n\n 🫰"
                    return response
                if message.lower() == "y":
                    response = "Your subscription is being created. You will be billed $1/month. To cancel your subscription, please reply with *2* or reply with your Ecocash mobile number in the form: `07XX` to proceed."
                    return response
                if message.lower() == "n":
                    response = "Your subscription Process has been terminated, To reactivate a subscription please reply with *1* ."
                    return response
            return response
            
        if status == payment_status:
            response = "Subscription Options:\n1. Monthly Subscription Plan\n2. Cancel Subscription\n3. Check Subscription Status\n4. Help\n5. Exit\n\nPlease reply with the number of your choice."
            return response

        if len(message) >5  and message[:1] == "0":
            pattern = r'^(077|078)\d{7}$'
            match = re.match(pattern, message)
            if match:
                response = "Please wait for the popup on your phone to confirm the payment. Your subscription will be activated once the payment is confirmed."
                return response
            else:
                response = "Invalid Ecocash number. Please reply with a valid Ecocash number to proceed."
                return response
        
    except Exception as e:
        response = "An error occured. Please try again later."
        return response
        