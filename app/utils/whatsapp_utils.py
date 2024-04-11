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
from sqlalchemy import and_
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from .model import *
from app.services.chat_responses import *
from app.services.user_types import *
from app.config import *
# import spacy

openai.api_key = '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'
conversation = []
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
            subscription_status=new_user,
            user_name=user_name,
            trial_start_date=today,
            trial_end_date=today + timedelta(days=7),
            user_status=welcome,
            user_type=chat_user,
            subscription_referral=None,
            user_activity="1"
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

def generate_response(response, wa_id, name):
    global conversation
    print("response",response,"wa_id",wa_id,"name",name)
    try:
        last_message = session.query(Message).filter_by(phone_number=wa_id[0]).order_by(Message.id.desc()).first().message
    except Exception as e:
        last_message = ""
    last_message = last_message.split()
    incoming = response.split()
    # if incoming[-1] != last_message[-1]:
    if response is not None:
        try:
            user_status = session.query(Subscription).filter_by(mobile_number=wa_id[0]).first()
            try:
                user_status.user_activity = response
                session.commit()
            except Exception as e:
                ...
            user_status_mode = user_status.user_status
            user_activity = user_status.user_activity
            expiry_date = user_status.trial_end_date
            subscription_status_ob =user_status.subscription_status
            print("user_status_mode",subscription_status_ob)
            print(",.,.,.,.",subscription_status_ob == new_user)
        except Exception as e:
            user_status_mode = ""
            subscription_status_ob =new_user
            user_activity = ""
            expiry_date = today
            # return f"sorry {e}"
        try:
            Subscription_status = create_subscription(wa_id[0], name, trial_mode)
        except Exception as e:
            Subscription_status = f"error!"
        conversation.append({"role": "user", "content": response})
        if user_activity == response and (response != "1" or "2" or "3"):
            return None
        if Subscription_status == "created":
            response = welcome_message
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
        elif user_status.subscription_status == new_user or user_status.user_status != welcome:
            print("calling function welcome page ....")

            response_ob = welcome_page(wa_id,response,subscription_status_ob,name,page_number=1)
            return response_ob
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
    response = generate_response(message_body, phone_number_id, profile_name)
    # OpenAI Integration
    # response = generate_response(message_body, wa_id, name)
    # response = process_text_for_whatsapp(response)

    data = get_text_message_input(current_app.config["RECIPIENT_WAID"], response)
    send_message(data)

def landlord_tenant_housing(mobile_number,message,name):
        try:
            active_subscription_status = session.query(Subscription).filter_by(mobile_number=mobile_number).first()
        except Exception as e:
            ...
        #=========================HOUSING USER BLOCK ===============
        if active_subscription_status.user_status == appartment_addition:
            response = add_property_response
            if message.lower() == "y":
                response = "House information captured successfully, you can add another property anytime."
                return response
            elif message.lower() == "n":
                try:
                    active_subscription_status.user_type = new_user
                    session.commit()
                    return welcome_message
                except Exception as e:
                    ...
                return "error adding property"
            elif message.lower() == "exit" :
                try:
                    active_subscription_status.user_status = welcome
                    active_subscription_status.user_type = new_user
                    session.commit()
                except Exception as e:
                    ...
                return welcome_message
            
            if len(message) > 7:
                analyze_messages(mobile_number,message)
                description,location, rentals = extract_house_details(message)
                print(description,"|",location,"|",rentals)
                if location and description and rentals:
                    house_details = f"- *Location:* {location}\n- *Description:* {description}\n- *Rentals*: ${rentals}"
                    response = apartment_added_successfully.format(house_details)
                    save_house_info(mobile_number, location.lower(), description.lower(), rentals)
                    return response
                return invalid_house_information
            return response
        
        #=========================LANDLORD USER BLOCK ===============
        if active_subscription_status.user_type == landlord_user:
            response = welcome_landlord_response
            if len(message) > 4 and len(message) < 10 and message != "exit" and message != "hello":
                    try:
                        landlord_prof = session.query(Landlord).filter_by(phone_number=mobile_number).first()
                        landlord_prof.name = message
                        session.commit()
                    except Exception as e:
                        ...
                    response = f"We will use *{message.upper()}* as your name."
            if message == "1":
                response = add_property_response
                try:
                    active_subscription_status.subscription_referral = message[:5]
                    active_subscription_status.user_status = appartment_addition
                    session.commit()
                except Exception as e:
                    ...
                return response
            elif message == "2":
                try:
                    landlord_profile = session.query(Landlord).filter_by(phone_number=mobile_number).first()
                except Exception as e:
                    landlord_profile = None
                if landlord_profile:
                    landlord_listings = session.query(RentalProperty).filter_by(landlord_id=landlord_profile.id).all()
                    if landlord_listings:
                        response = f"*Hi `{landlord_profile.name}` here is your rental property listings:*\n\n"
                        for i, listing in enumerate(landlord_listings, start=1):
                            response += f"{i} *House Information:* {listing.description}\n\t-*Location:* {listing.location}\n\t-*Rent:* ${listing.price}/month\n\n"
                        response += "\n1. To add  property or type *exit* to Exit."
                        return response
                    else:
                        return no_apartment_listings
                else:
                    return not_a_landlord_response
            elif message.lower() == "exit" :
                try:
                    active_subscription_status.user_status = welcome
                    active_subscription_status.user_type = new_user
                    session.commit()
                except Exception as e:
                    ...
                return welcome_message
            return response      
        #=========================TENANT USER BLOCK ===============              
        if active_subscription_status.user_type == tenant_user:
            if message == "1":
                return tenant_response
            elif message.lower() == "exit" :
                try:
                    active_subscription_status.user_status = welcome
                    active_subscription_status.user_type = new_user
                    session.commit()
                except Exception as e:
                    ...
                return welcome_message
            if len(message) > 7:
                house_info, location, budget = extract_house_details(message)
                if house_info and location and budget:
                    matching_properties = search_rental_properties(house_info.lower(), location.lower(), budget)
                    if matching_properties:
                        result = "Here are some houses you may like:\n\n"
                        for i,property in enumerate(matching_properties, start=1) :
                            result += f"*{i}* *House information* {property.house_info}\n\t*Rent*: {property.price}\n\t*Location*: {property.location}\n\n Call: *{property.landlord.name}* on {property.landlord.phone_number}"
                        analyze_messages(mobile_number,message)
                        return result
                    else:
                        return no_houses_found_response
                else:
                    return invalid_house_information
            return welcome_tenant_response

def buying_and_selling(wa_id,message,name,page_number):
    message_ob = message
    try:
        active_subscription_status = session.query(Subscription).filter_by(mobile_number=wa_id[0]).first()
    except Exception as e:
        ...
    else:
        if active_subscription_status.user_type == buyer_user:
                response =buyer_response
                if len(message) > 5:
                    analyze_messages(wa_id[0],message)
                    product_name, condition, price = extract_product_details(message)
                    if product_name and condition and price:
                        seller_products_list =search_products(product_name, condition, price,page_number, 5)
                        if seller_products_list:
                            result = "HERE IS WHAT WE FOUND:\n\n"
                            for i,product in enumerate(seller_products_list, start=1) :
                                result += f"*{i}* *Product Name* {product.gadget_name}\n\t*Condition*: {product.condition}\n\t*Price*: {product.price}\n\n Call: *{product.seller.name}* on {product.seller.phone_number}"
                            analyze_messages(wa_id[0],message)
                            return result
                        else:
                            return no_products_found_response
                    else:
                        return invalid_product_information

                elif message.lower() == "exit" :
                    try:
                        active_subscription_status.user_status = welcome
                        active_subscription_status.user_type = new_user
                        session.commit()
                    except Exception as e:
                        ...
                    return welcome_message
                return response
            #=========================SELLING USER BLOCK ===============
        if active_subscription_status.user_type == seller_user:
            response = seller_response
            if message == "1":
                response = seller_add_response
                return response
            elif message == "2" or message.lower()=="more":
                try:
                    seller_user_profile = session.query(Seller).filter_by(phone_number=wa_id[0]).first()
                except Exception as e:
                    seller_user_profile = None
                if seller_user_profile:
                    page_number = page_number
                    records_per_page = 10
                    if message.lower() =="more":
                        page_number+=1
                    offset = (page_number - 1) * records_per_page
                    seller_products = session.query(Electronics).filter_by(seller_id=seller_user_profile.id).\
                    limit(records_per_page).offset(offset).all()
                    if seller_products:
                        response = "Here is your listings:\n\n"
                        for i, product in enumerate(seller_products, start=1):
                            response += f"- {i} *Product Name:* {product.gadget_name}\n\t- *Condition:* {product.condition}\n\t- *Price:* ${product.price}\n\n"
                        response += "\nReply with *1* to Add a product, *more* to view more or *exit* to exit."
                        return response
                    else:
                        return no_listings_response
                else:
                    return not_a_seller_response
            elif len(message) > 7:
                analyze_messages(wa_id[0],message)
                if get_number_range(message):
                    number_range = get_number_range(message)
                    response = product_added_successfully.format(message, number_range.start, number_range.stop)
                    product_name, condition, price = extract_product_details(message)
                    if product_name and condition and price:
                        save_electronics_listing(wa_id[0], product_name.lower(), condition.lower(), price)
                        return response
                    else:
                        return invalid_sale_response
                return response
            if message_ob.lower() == "exit" :
                try:
                    active_subscription_status.user_status = welcome
                    active_subscription_status.user_type = new_user
                    session.commit()
                except Exception as e:
                    ...
                return welcome_message
            return response

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
    
def welcome_page(wa_id,message,user_status_ob,name,page_number):
    end_date = today + timedelta(days=7)
    trial_response_ob = trial_response.format(name,end_date)
    if user_status_ob == new_user:
        welcome_response = welcome_message
        try:
            session = Session()
            active_subscription_status = session.query(Subscription).filter_by(mobile_number=wa_id[0]).first()
            selling_mode_ob =active_subscription_status.user_status
        except Exception as e:
            user_type_ob = ""
            selling_mode_ob = ""
        else:
            #=========================BUYING & SELLING USER BLOCK ===============
            if active_subscription_status.user_type == buyer_user or active_subscription_status.user_type == seller_user:
                
                response = buying_and_selling(wa_id,message,name,page_number)
                return response
            
            if active_subscription_status.user_status == selling_mode:
                response = selling_response
                if message == "1":
                    response = seller_response
                    try:
                        active_subscription_status.user_type = seller_user
                        active_subscription_status.user_status = selling_mode
                        session.commit()
                        seller_info = Seller(phone_number=wa_id[0], name=name)
                        session.add(seller_info)
                        session.commit()
                    except Exception as e:
                        pass
                        # return e
                    return response
                
                elif message == "2":
                    response = buyer_response
                    try:
                        active_subscription_status.user_type = buyer_user
                        active_subscription_status.user_status = buyer_user
                        session.commit()
                    except Exception as e:
                        user_type_ob = ""
                        # return e
                    return response
                elif message.lower() == "exit" :
                    try:
                        active_subscription_status.user_status = welcome
                        active_subscription_status.user_type = new_user
                        session.commit()
                    except Exception as e:
                        ...
                    return welcome_message
                return response  
            
            if active_subscription_status.user_type == landlord_user or active_subscription_status.user_type == tenant_user:
                response =landlord_tenant_housing(wa_id[0],message,name)
                return response
            
            if active_subscription_status.user_status == housing_mode:
                response = welcome_response3
                

                if message == "1":
                    response = welcome_landlord_response
                    try:
                        response = landlord_name_response
                        active_subscription_status.user_type = landlord_user
                        active_subscription_status.user_status = landlord_user
                        session.commit()
                        landlord_info = Landlord(phone_number=wa_id[0], name=name) 
                        try:
                            landlord_ob = session.query(Landlord).filter_by(phone_number=wa_id[0]).first()
                        except Exception as e:
                            landlord_ob = ""
                        if landlord_ob:
                            pass
                        else:
                            session.add(landlord_info)
                            session.commit()
                            return response
                        return welcome_landlord_response
                    except Exception as e:
                        selling_mode_ob = ""
                        # return e
                    return response
                elif message == "2":
                    response = welcome_tenant_response
                    try:
                        active_subscription_status.user_type = tenant_user
                        active_subscription_status.user_status = tenant_user
                        session.commit()
                    except Exception as e:
                        user_type_ob = ""
                        response = "error listing property.."
                        # return e
                    return response
                elif message.lower() == "exit" :
                    try:
                        active_subscription_status.user_status = welcome
                        active_subscription_status.user_type = new_user
                        session.commit()
                    except Exception as e:
                        ...
                    return welcome_message
                return response
            if message == "1" or message=="1.":
                try:
                    active_subscription_status.user_status = chat_status
                    active_subscription_status.subscription_status = trial_mode
                    session.commit()
                except Exception as e:
                    return e
                return trial_response_ob
            
            if message == "2" or message=="2.":
                selling_response_ob =selling_response
                try:
                    active_subscription_status.user_status = selling_mode
                    session.commit() 
                except Exception as e:
                    selling_mode_ob = ""
                    # return e
                return selling_response_ob
            if message == "3":
                response = welcome_response3
                try:
                    active_subscription_status.user_status = housing_mode
                    session.commit() 
                except Exception as e:
                    selling_mode_ob = ""
                return response
            return welcome_response
    return "eeh"

# def summarize_message(message):
#     nlp = spacy.load("en_core_web_sm")
#     doc = nlp(message)
#     keywords = []
#     house_info = []
#     price_per_month = []
#     location = ""
#     for token in doc:
     
#         if token.pos_ in ["NOUN", "PROPN"]:
#             keywords.append(token.text)
#         if token.pos_ == "NUM":
#             house_info.append(token.text)

#         if token.ent_type_ == "MONEY":
#             price_per_month.append(token.text)
        
#         if token.ent_type_ == "GPE":
#             location = token.text

#     summary = f"Location: {location}\n" \
#               f"Rent: {', '.join(price_per_month)}\n" \
#               f"House info: {', '.join(house_info)}"

#     return summary

def get_number_range(string):
    match = re.search(r'\$(\d+)', string)
    if match:
        number = int(match.group(1))
        return range(number - 10, number + 11)
    else:
        return None

def extract_product_details(string):
    product_name, condition, price ="", "", ""
    match = re.search(r'^(.*?)\s*,\s*(.*?)\s+\$(\d+)$', string)
    if match:
        product_name = match.group(1)
        condition = match.group(2)
        price = int(match.group(3))
        return product_name, condition, price
    else:
        return product_name, condition, price

def save_electronics_listing(seller_id, product_name, condition, price):
    seller = session.query(Seller).filter_by(phone_number=seller_id).first()
    if seller:
        electronics = Electronics(gadget_name=product_name, condition=condition, price=price, seller=seller,seller_id=seller.id)
        session.add(electronics)
        session.commit()

def save_house_info(landlord_phone, location, description, price):
    try:
        landlord = session.query(Landlord).filter_by(phone_number=landlord_phone).first()
    except Exception as e:
        landlord = ""
    if landlord:
        rental_property = RentalProperty(landlord_id=landlord.id, location=location, description=description, price=price,house_info=description,)
        session.add(rental_property)
        session.commit()

def analyze_messages(sender,message):
    try:
        last_message = session.query(Message).filter_by(phone_number=sender).order_by(Message.id.desc()).first().message
    except Exception as e:
        last_message = False
    if last_message:
        try:
            message_ob = Message(message=message,phone_number=sender)
            session.add(message_ob)
            if last_message != message:
                session.commit()
                return True
            else:
                return False
        except Exception as e:
            ...
    else:
        try:
            message_ob = Message(message=message,phone_number=sender)
            session.add(message_ob)
            session.commit()
            return True
        except Exception as e:
            ...

def extract_house_details(string):
    pattern = r'^(.*?)\sin\s(.*?)\s*\$([\d,]+)$'
    match = re.search(pattern, string)
    house_info, location, budget = "", "", ""
    
    if match:
        house_info = match.group(1)
        location = match.group(2)
        budget = int(match.group(3).replace(',', ''))
    
    return house_info, location, budget

def search_rental_properties(house_info, location, budget):
    session = Session()
    try:
        properties = session.query(RentalProperty).\
            filter(RentalProperty.description.ilike('%{}%'.format(house_info))).\
            filter(RentalProperty.location.ilike('%{}%'.format(location))).\
            filter(RentalProperty.price.between(budget - 20, budget + 20)).\
            all()
    except Exception as e:
        properties = None
    return properties

def search_products(product_name, condition, budget, page_number, records_per_page):
    if condition == "boxed" or "new":
        condition = "boxed"
    else:
        condition = "pre-owned"
    try:
        offset = (page_number - 1) * records_per_page
        matching_products = session.query(Electronics).join(Electronics.seller).\
            filter(Electronics.gadget_name.ilike(f'%{product_name}%')).\
            filter(Electronics.condition.ilike(f'%{condition}%')).\
            filter(Electronics.price.between(budget - 20, budget + 20)).\
            offset(offset).limit(records_per_page).all()
    except Exception as e:
        matching_products = None
    return matching_products