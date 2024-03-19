import logging
from flask import current_app, jsonify
import json
import requests
import openai
# from app.services.openai_service import generate_response
import re
from openai import ChatCompletion
# import random




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

def generate_response(response):
    global conversation

    conversation.append({"role": "user", "content": response})

    if "tecla" in response:
        response = "Hey Tecla, how can I help you today? Please be open to me and let me know if tankan is bothering you."
        return response
    elif response.lower().endswith("bypasslimit"):
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


#         )
#     if response.lower() == "who are you?" or response.lower() == "what is your name" or response.lower() == "where are you from" or response.lower() == "who made you?" or response.lower() == "who is tankan" or response.lower() == "tankan":
#         response = "I am tankan's assistant, I am here to help you with anything you need."
#         return response
#     # Call OpenAI API
#     else:
#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[{"role": "user", "content": response}],
#             max_tokens=200,
#             temperature=0.7,
#             n=1,
#             stop=None
#         )
#     return response.choices[0].message.content.strip()

# Example usage

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
        )  # 10 seconds timeout as an example
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
    # Remove brackets
    pattern = r"\【.*?\】"
    # Substitute the pattern with an empty string
    text = re.sub(pattern, "", text).strip()

    # Pattern to find double asterisks including the word(s) in between
    pattern = r"\*\*(.*?)\*\*"

    # Replacement pattern with single asterisks
    replacement = r"*\1*"

    # Substitute occurrences of the pattern with the replacement
    whatsapp_style_text = re.sub(pattern, replacement, text)

    return whatsapp_style_text


def process_whatsapp_message(body):
    wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]

    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    message_body = message["text"]["body"]

    # TODO: implement custom function here
    response = generate_response(message_body)

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