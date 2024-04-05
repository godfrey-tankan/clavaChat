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
from app.config import *




today = datetime.now().date()
def create_subscription(mobile_number,user_name, subscription_status):
    if Subscription.exists(session, mobile_number):
        sub_end = session.query(Subscription).filter_by(mobile_number=mobile_number).first()
        if sub_end.trial_end_date < today:
            message = "expired"
            if sub_end.subscription_status != "Free Trial" and sub_end.subscription_status != "Monthly Subscription":
                pass
            else:
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
    if response != "" or None:
        try:
            user_status = session.query(Subscription).filter_by(mobile_number=wa_id[0]).first()
            user_status_mode = user_status.user_status
            expiry_date = user_status.trial_end_date
            subscription_status_ob =user_status.subscription_status
        except Exception as e:
            user_status_mode = welcome
            expiry_date = today
            subscription_status_ob = "Free Trial"
        try:
            Subscription_status = create_subscription(wa_id[0], name, "Free Trial")
        except Exception as e:
            Subscription_status = "error"
        conversation.append({"role": "user", "content": response})
        if Subscription_status == "created":
            response = f" Hi {name}\nYour 7-Days Free trial `subscription` has been `created` . Your free trial will expire on `{today + timedelta(days=7)}`\n Enjoy a happy chat with `clavaChat` \nRegards,\n*clavaChat*."
            return response
        elif Subscription_status == "expired":
            if  user_status_mode == subs_status:
                response = activate_subscription(wa_id,user_status_mode,response,expiry_date,subscription_status_ob)
                return response
            elif user_status_mode == payment_status:
                response = activate_subscription(wa_id,user_status_mode,response,expiry_date,subscription_status_ob)
                return response
            
            response = subs_response_default
            return response
        if subscription_status_ob == chat_status:
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
            elif response.lower() in questions_list:
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

def activate_subscription(wa_id,status,message,expiry_date,subscription_status_ob):
    try:
        if status ==subs_status:
            try:
                response = subs_response_default
            except Exception as e:
                response = f"subscription - {error_response}"
                return response
            else:
                if message == "1" or message=="1.": 
                    response = subs_response1
                    return response
                if message == "2" or message=="2.":
                    response = f"{subs_response2.format(subscription_status_ob)} its expiry date is {expiry_date}\n{subs_response5}"
                    return response
                elif message == "3" or message=="3.":
                    response =subs_response_final4
                    return response
                elif message == "4" or message=="4.":
                    response = subs_response_final4
                    return response
                elif message == "5" or message=="5.":
                    response = subs_response5
                    return response
                if message.lower() == "y":
                    response = payment_response_default_response
                    try:
                        active_subscription_status = session.query(Subscription).filter_by(mobile_number=wa_id[0]).first()
                        active_subscription_status.user_status = payment_status
                        active_subscription_status.subscription_status = "Subscription Activation"
                        session.commit()
                    except Exception as e:
                        return e
                    return response
                if message.lower() == "n":
                    response = subs_payment_deny_response
                    return response
            return response
            
        if status == payment_status:
            try:
                response = payment_response_default_response
            except Exception as e:
                response = f"payment - {error_response}"
                return response
            else:
                if message == "1" or message=="1.":
                    response = subs_payment_agree_response
                    return response
                if message == "2" or message=="2.":
                    response = subs_cancel_response
                    return response
            if len(message) >5  and message[:1] == "0":
                pattern = r'^(077|078)\d{7}$'
                match = re.match(pattern, message)
                if match:
                    response = ecocash_number_valid_response
                    return response
                else:
                    response = ecocash_number_invalid_response
                    return response
            if "transfer confirmation" in message.lower():
                pattern = r"PP(.*?)\bNew wallet"
                match = re.search(pattern, message)
                if match:
                    transaction_message_input = match.group(1).strip()
                    if transaction_message_input == transaction_message.strip():
                        try:
                            Subscription_status = session.query(Subscription).filter_by(mobile_number=wa_id[0]).first()
                            Subscription_status.subscription_status = "Monthly Subscription"
                            Subscription_status.user_status = chat_status
                            Subscription_status.trial_start_date = today
                            Subscription_status.trial_end_date = today + timedelta(days=30)
                            session.commit()
                            response = eccocash_transaction_success_response
                            return response
                        except Exception as e:
                            response = f"transaction - {error_response}"
                            return response
                    else:
                        return reference_number_error_response
                else:
                    return pop_reference_number_error_response
            return response
        return response
    except Exception as e:
        response = subs_error_response
        return response