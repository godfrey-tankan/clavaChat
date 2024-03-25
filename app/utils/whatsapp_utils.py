import logging
from flask import current_app, jsonify
import json
import requests
import openai
# from app.services.openai_service import generate_response
import re
from openai import ChatCompletion
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.utils.model import Subscription
from datetime import timedelta
import datetime
# import random

engine = create_engine('sqlite:///subscriptions.db')
Session = sessionmaker(bind=engine)
session = Session()

def create_subscription(mobile_number,message, subscription_status):
    existing_subscription = session.query(Subscription).filter_by(wa_id=mobile_number).first()
    if existing_subscription:
        print("Subscription already exists")
    else:
        subscription = Subscription(
            mobile_number=mobile_number,
            subscription_status=subscription_status,
            message=message,
            trial_start_date=datetime.now(),
            trial_end_date=datetime.now() + timedelta(days=7),
        )
        session.add(subscription)
        session.commit()




def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")


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
    print(wa_id[0], name)
    conversation.append({"role": "user", "content": response})
    
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
            max_tokens=50,
            temperature=0.7,
            n=1,
            stop=None
        )
        conversation.append({"role": "assistant", "content": response.choices[0].message.content.strip()})

    return response.choices[0].message.content.strip()

# def generate_response(response):
#     # Return text in uppercase
#     if response.lower() == "hello":
#         response = "Hello, tankan"
#     return response.upper()


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
        logging.error("Timeout occurred while sending message")
        return jsonify({"status": "error", "message": "Request timed out"}), 408
    except (
        requests.RequestException
    ) as e:  # This will catch any general request exception
        logging.error(f"Request failed due to: {e}")
        return jsonify({"status": "error", "message": "Failed to send message"}), 500
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
