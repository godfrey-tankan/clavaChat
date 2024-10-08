import logging
from datetime import datetime
from datetime import timedelta
from flask import current_app, jsonify
import json
import time
from sqlalchemy.exc import OperationalError
import requests
import openai
import time
from paynow import Paynow
# from app.services.openai_service import generate_response
import re
from openai import ChatCompletion
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import and_
from sqlalchemy import create_engine,func
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from .model import *
from app.services.chat_responses import *
from app.services.user_types import *
import random
from app.config import *

openai.api_key = "sk-proj-vdoincb6xa4NeNX04fknT3BlbkFJqbXL0EFJvL6192EQny3d"
conversation = []
today = datetime.now().date()

MAX_RETRIES = 3
RETRY_DELAY = 3 

def create_subscription(mobile_number,user_name, subscription_status):
    if Subscription.exists(session, mobile_number):
        sub_end = session.query(Subscription).filter_by(mobile_number=mobile_number).first()
        if sub_end.trial_end_date < today:
            # sub_end.trial_end_date = today + timedelta(days=100)
            # session.commit()
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
            trial_end_date=today + timedelta(days=130),
            user_status=welcome,
            user_type=new_user,
            subscription_referral=None,
            user_activity="1"
        )
        session.add(subscription)
        session.commit()
    message = "created"
    return message

def log_http_response(response):
    pass
    logging.info(f"Status: {response.status_code}")
    # logging.info(f"Content-type: {response.headers.get('content-type')}")
    # logging.info(f"Body: {response.text}")

def get_text_message_input(recipient, text,media,template=False):
    if media:
        return json.dumps(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient,
                "type": "document",
                # "type": "document",
                "document": {
                    "link": media,
                    "filename": text
                },
            }
        )
    if template:
        return json.dumps(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient,
                "type": "template",
                "template": {
                    "name": "clava_welcome",
                    "language": {"code": "en-GB"},
                },
            }
        )
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
    session.rollback()
    try:
        last_message = session.query(Subscription).filter_by(phone_number=wa_id[0]).first().user_activity
    except Exception as e:
        last_message = ""
    if last_message == response.strip() and (response != "1" and response !="2" and response !="3"):
        return None
    else:
        if response.lower() in questions_list:
            return "I am tankan's assistant. I am here to help you with anything you need."
        if response.lower().startswith("post") and wa_id[0] == "263779586059" or wa_id[0] == "263717852804":
            response_ob = publish_post(response)
            return response_ob
        if response.lower() == "help": 
            return buying_selling_help_help_final 
        try:
            user_status = session.query(Subscription).filter_by(mobile_number=wa_id[0]).first()
            try:
                user_status.user_activity = response
                session.commit()
            except Exception as e:
                ...

            user_status_mode = user_status.user_status
            expiry_date = user_status.trial_end_date
            subscription_status_ob =user_status.subscription_status
        except Exception as e:
            user_status_mode = ""
            subscription_status_ob =new_user
            expiry_date = today
            # return f"sorry {e}"
        try:
            user_name = name if name else "user"
            Subscription_status = create_subscription(wa_id[0], user_name, trial_mode)
        except Exception as e:
            Subscription_status = "error!"
            print('error subs check.. ',e)
            return None
        conversation.append({"role": "user", "content": response})
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
            user_status.user_status = subs_status
            session.commit()
            return response
        elif user_status.user_type != chat_user:
            print("calling function welcome page ....")
            response_ob = welcome_page(wa_id,response,subscription_status_ob,name,page_number=1)
            return response_ob
        else:
            if response.lower() == "exit" :
                    try:
                        user_status.user_status = welcome
                        user_status.user_type = new_user
                        user_status.subscription_status = new_user
                        session.commit()
                    except Exception as e:
                        ...
                    return welcome_message
            # return "Please *note* that the clavaChat AI Chatbot is currently under maintenance.\nRegards clavaTeam."      
            try:
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
            except Exception as e:
                return "Please *note* that the clavaChat AI Chatbot is currently under maintenance.\nRegards clavaTeam."      
    
def send_message(data,template=False):
    if template:
        headers = {
            "Content-type": "application/json",
            "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
        }
        url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"
        try:
            response = requests.post(
                url, data=data, headers=headers, timeout=30
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
    else:
        headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
        }
        url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"
        try:
            response = requests.post(
                url, data=data, headers=headers, timeout=30
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
    try:
        # phone_number_id = data['entry'][0]['changes'][0]['value']['metadata']['phone_number_id']
        phone_number_id =  [contact['wa_id'] for contact in data['entry'][0]['changes'][0]['value']['contacts']]
    except Exception as e:
        phone_number_id = ""

    try:
        profile_name = data['entry'][0]['changes'][0]['value']['contacts'][0]['profile']['name']
    except Exception as e:
        profile_name = "User"
    try:
        message = body["entry"][0]["changes"][0]["value"]["messages"][0]
        message_body = message["text"]["body"]
    except Exception as e:
        message_body = "hello there, how can i help you today?"
    try:
        response = generate_response(message_body, phone_number_id, profile_name)
        data = get_text_message_input(phone_number_id, response,None,False)
        send_message(data)
    except Exception as e:
        ...

def send_message_template(recepient):
    return json.dumps(
    {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": f"{recepient}",
        "type": "template",
        "template": {
            "namespace": "7a757027_47cc_4bb8_997e_e1fdb0600675",
            "name": "clava_home2",
            "language": {
                "code": "en",
            }
        }
    }
)

def landlord_tenant_housing(mobile_number,message,name,page_number):
        try:
            active_subscription_status = session.query(Subscription).filter_by(mobile_number=mobile_number).first()
        except Exception as e:
            ...
        #=========================HOUSING USER BLOCK ========================
        if active_subscription_status.user_status == appartment_addition:
            response = add_property_response
            if message.lower() == "y":
                response = "House information captured successfully, you can add another listing anytime."
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
            if "[" in message:
                landlord_details = message.split(']')[1].strip()
                try:
                    landlord = session.query(Landlord).filter_by(phone_number=landlord_details.split()[-1]).first()
                    if landlord:
                        pass
                    else:
                        landlord = Landlord(phone_number=landlord_details.split()[-1], name=landlord_details.split()[-2])
                        session.add(landlord)
                        session.commit()
                except Exception as e:
                    ...
                property_list = message.split("]")[0].strip() + "]"
                properties = eval(property_list)
                for single_property in properties:
                    description,location, rentals = extract_house_details(single_property)
                    try:
                        rental_property = RentalProperty(landlord_id=landlord.id, location=location, description=description, price=rentals,house_info=description,)
                        session.add(rental_property)
                        session.commit()
                    except Exception as e:
                        return "error adding property"
                    
                return "listings added successfully."
                
            
            if len(message) > 7:
                analyze_messages(mobile_number,message)
                description,location, rentals = extract_house_details(message)
                if location and description and rentals:
                    if int(rentals) ==100000:
                        return "Please provide a valid rental amount eg $80."
                    house_details = f"- *Location:* {location}\n- *Description:* {description}\n- *Rentals*: ${rentals}"
                    response = apartment_added_successfully.format(house_details)
                    save_house_info(mobile_number, location.lower(), description.lower(), rentals)
                    return response
                return invalid_house_information
            return response
        
        #=========================LANDLORD USER BLOCK ===============
        if active_subscription_status.user_type == landlord_user:
            if active_subscription_status.user_status == subscription_status:
                response = create_landlord_subscription(message, mobile_number)
                return response
            records_per_page =10
            response = welcome_landlord_response
            if message == "1":
                response = add_property_response
                try:
                    active_subscription_status.subscription_referral = message[:5]
                    active_subscription_status.user_status = appartment_addition
                    session.commit()
                except Exception as e:
                    ...
                return response
            elif message == "2" or "delete" in message.lower() or "edit" in message.lower() or message.lower() == "more":
                try:
                    landlord_profile = session.query(Landlord).filter_by(phone_number=mobile_number).first()
                except Exception as e:
                    landlord_profile = None
                if landlord_profile:
                    if "edit" in message.lower():
                        property_id = message.split(" ")[1]
                        match = re.search(r'\$(\d+)', message)
                        new_price = match.group(1) if match else None
                        response = edit_property(property_id, new_price,mobile_number)
                        return response
                    
                    if "delete" in message.lower():
                        property_id = message.split(" ")[1]
                        response = delete_property(property_id,mobile_number)
                        return response

                    if message.lower() =="more":
                        page_number+=1
                        offset = (page_number - 1) * records_per_page
                        landlord_listings = session.query(RentalProperty).filter_by(landlord_id=landlord_profile.id).\
                        limit(records_per_page).offset(offset).all()
                        if landlord_listings:
                            response = f"*HERE IS YOUR OTHER PROPERTY LISTINGS:*\n\n"
                            for i, listing in enumerate(landlord_listings, start=1):
                                response += f"{listing.id} *HOUSE INFORMATION:* {listing.description}\n- *LOCATION:* {listing.location}\n- *RENT:* ${listing.price}/month\n\n"
                            response += underline_response
                            response += after_property_listing_response
                            return response
                        else:
                            return "No more properties found."
                        
                    offset = (page_number - 1) * records_per_page
                    landlord_listings = session.query(RentalProperty).filter_by(landlord_id=landlord_profile.id).\
                    limit(records_per_page).offset(offset).all()
                    if landlord_listings:
                        response = f"*HI `{landlord_profile.name.upper()}` HERE IS YOUR PROPERTY LISTINGS:*\n\n"
                        for i, listing in enumerate(landlord_listings, start=1):
                            response += f"{listing.id} *HOUSE INFORMATION:* {listing.description}\n- *LOCATION:* {listing.location}\n- *RENT:* ${listing.price}/month\n\n"
                        response += underline_response
                        response += after_property_listing_response
                        return response
                    else:
                        return no_apartment_listings
                else:
                    return not_a_landlord_response
            if len(message) > 4 and len(message) < 10 and message != "exit" and message != "hello":
                    try:
                        landlord_prof = session.query(Landlord).filter_by(phone_number=mobile_number).first()
                        landlord_prof.name = message
                        session.commit()
                    except Exception as e:
                        ...
                    response = f"We will use *{message.upper()}* as your name.\n\nReply with *Y* to accept or *N* to deny."
                    return response
            if message == "3":
                response = landlord_subs_response
                try:
                    active_subscription_status.user_status = subscription_status
                    session.commit()
                except Exception as e:
                    ...
                return response
            if message.lower() == "exit" :
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
            if len(message) > 7 or message.lower() == "more":
                if message.lower() == "more":
                    return "No more properties found."
                house_info, location, budget = extract_house_details(message)
                if house_info and location and budget:
                    matching_properties = search_rental_properties(house_info.lower(), location.lower(), budget,page_number, 20)
                    if matching_properties:
                        result = "HERE ARE SOME PROPERTIES TO CONSIDER:\n\n"
                        for i,property in enumerate(matching_properties, start=1) :
                            result += f"*{i}* *House information :* {property.house_info}\n\t*Rent*: {property.price}\n\t*Location*: {property.location}\n Call: *{property.landlord.name}* on {property.landlord.phone_number}\n\n"
                            property_analysis(property.id,active_subscription_status.id,property.landlord.id)
                        # analyze_messages(mobile_number,message)
                        result += underline_response
                        result += after_tenant_listing_response
                        return result
                    else:
                        return no_houses_found_response
                else:
                    return invalid_house_information
            return tenant_response

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
                    if message.lower() == "more" :
                        return "No more products found."
                    product_name, condition, price = extract_product_details(message)
                    if product_name and condition and price:
                        seller_products_list =search_products(product_name, condition, price,page_number, 5)
                        if seller_products_list:
                            result = "*HERE IS WHAT YOU MAY LIKE:*\n\n"
                            for i,product in enumerate(seller_products_list, start=1) :
                                result += f"*{i}* *Product Name* {product.gadget_name}\n\t*Condition*: {product.condition}\n\t*Price*: ${product.price}\n\n Call: *{product.seller.name}* on {product.seller.phone_number}\n\n"
                                product_analysis(product.id,active_subscription_status.id,product.seller.id)
                            # analyze_messages(wa_id[0],message)
                            result += underline_response
                            result += after_buyer_listing_response
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
            page_number = page_number
            records_per_page = 10
            if "[" in message:
                seller_mobile = message.split(']')[1].strip()
                try:
                    seller = session.query(Seller).filter_by(phone_number=seller_mobile.split()[-1]).first()
                    if seller:
                        pass
                    else:
                        seller = Seller(phone_number=seller_mobile.split()[-1], name=seller_mobile.split()[-2])
                        session.add(seller)
                        session.commit()
                except Exception as e:
                    ...
                if "boxed" in message.lower():
                    condition = "boxed"
                else:
                    condition = "pre-owned"
                gadget_list_ob = message.split("]")[0].strip() + "]"
                gadget_list = eval(gadget_list_ob)
                for gadget in gadget_list:
                    product_info = gadget.split('$')
                    product_name = product_info[0].strip()
                    price = float(product_info[1].strip())
                    try:
                        electronics = Electronics(gadget_name=product_name, condition=condition, price=price, seller=seller,seller_id=seller.id)
                        session.add(electronics)
                        session.commit()
                    except Exception as e:
                        return "error adding gadget"
                    
                return "gadgets added successfully."
            
            if active_subscription_status.user_status == subscription_status:
                response = create_seller_subscription(message, wa_id[0])
                return response
                
            elif message == "1":
                response = seller_add_response
                return response
            elif message == "2" or message.lower()=="more" or "delete" in message.lower() or "edit" in message.lower():
                try:
                    seller_user_profile = session.query(Seller).filter_by(phone_number=wa_id[0]).first()
                except Exception as e:
                    seller_user_profile = None

                if seller_user_profile:

                    if "edit" in message.lower():
                        product_id = message.split(" ")[1]
                        match = re.search(r'\$(\d+)', message)
                        new_price = match.group(1) if match else None
                        response = edit_product(product_id, new_price,wa_id[0])
                        return response
                    
                    if "delete" in message.lower():
                        product_id = message.split(" ")[1]
                        response = delete_product(product_id,wa_id[0])
                        return response
                    
                    if message.lower() =="more":
                        page_number+=1
                        offset = (page_number - 1) * records_per_page
                        seller_products = session.query(Electronics).filter_by(seller_id=seller_user_profile.id).\
                        limit(records_per_page).offset(offset).all()
                        if seller_products:
                            response = "Here are your other listings:\n\n"
                            for i, product in enumerate(seller_products, start=1):
                                response += f"{product.id} *PRODUCT NAME:* {product.gadget_name}\n- *CONDITION:* {product.condition}\n- *PRICE:* ${product.price}\n"
                            response += underline_response
                            response += after_listing_response
                            return response
                        else:
                            return "No more listings found."
                        
                    offset = (page_number - 1) * records_per_page
                    seller_products = session.query(Electronics).filter_by(seller_id=seller_user_profile.id).\
                    limit(records_per_page).offset(offset).all()
                    if seller_products:
                        response = "Here are your listings:\n\n"
                        for i, product in enumerate(seller_products, start=1):
                            response += f"{product.id} *PRODUCT NAME:* {product.gadget_name}\n- *CONDITION:* {product.condition}\n- *PRICE:* ${product.price}\n"
                        response += underline_response
                        response += after_listing_response
                        return response
                    else:
                        return no_listings_response
                else:
                    return not_a_seller_response
            
            elif message.lower() == "3" :
                response = seller_subs_response
                try:
                    active_subscription_status.user_status = subscription_status
                    session.commit()
                except Exception as e:
                    ...
                return response

            elif len(message) > 4 and not 'delete' in message.lower() and not 'edit' in message.lower():
                analyze_messages(wa_id[0],message)
                if get_number_range(message):
                    number_range = get_number_range(message)
                    response = product_added_successfully.format(message, number_range.start, number_range.stop)
                    product_name, condition, price = extract_product_details(message)
                    if product_name and condition and price:
                        if price == 20000:
                            return 'Please provide a valid product price eg: $100.'
                        save_electronics_listing(wa_id[0], product_name.lower(), condition.lower(), price)
                        return response
                    else:
                        return invalid_sale_response
                return 'Please provide a valid product price eg: $100.'

            if message_ob.lower() == "exit" :
                try:
                    active_subscription_status.user_status = selling_mode
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

#=========================CHAT SERVICE SUBSCRIPTION BLOCK ========================
def activate_subscription(wa_id,status,message,expiry_date,subscription_status_ob):

    try:
        if message.lower() == "exit" :
            try:
                active_subscription_status = session.query(Subscription).filter_by(mobile_number=wa_id[0]).first()
                active_subscription_status.user_status = welcome
                active_subscription_status.user_type = new_user
                session.commit()
            except Exception as e:
                ...
            return welcome_message
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
                        return response
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
            if len(message) >5  and message[:1] == "0" or "ecocash" in message.lower() or "onemoney" in message.lower() or "bank" in message.lower():
                response = validate_payment(message,wa_id)
            return response
        return response
    except Exception as e:
        response = subs_error_response

#=====================THE HOME PAGE==========================
def welcome_page(wa_id,message,user_status_ob,name,page_number):
    end_date = today + timedelta(days=7)
    trial_response_ob = trial_response

    if user_status_ob == new_user or user_status_ob != trial_mode or user_status_ob != welcome:
        welcome_response = welcome_message
        if message == "template":
            data = send_message_template(wa_id[0])
            welcome_response = send_message(data,template=True)
            return welcome_response

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
            
            #=========================LIBRARY USER BLOCK ===============
            if active_subscription_status.user_type == library_user:
                if message.lower() == "exit":
                    try:
                        active_subscription_status.user_status = welcome
                        active_subscription_status.user_type = new_user
                        session.commit()
                        return welcome_message
                    except Exception as e:
                        ...
                response = library_contents_lookup(wa_id[0],message)
                return response
            
            if active_subscription_status.user_status == selling_mode:
                response = selling_response
                if message == "1":
                    response = seller_response
                    try:
                        active_subscription_status.user_type = seller_user
                        active_subscription_status.user_status = selling_mode
                        session.commit()
                        seller_info = Seller(phone_number=wa_id[0], name=name,subscription_id=active_subscription_status.id)
                        try:
                            seller_ob = session.query(Seller).filter_by(phone_number=wa_id[0]).first()
                        except Exception as e:
                            seller_ob = ""
                        if seller_ob:
                            pass
                        else:
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
            
            #=========================HOUSING USER BLOCK ========================
            if active_subscription_status.user_type == landlord_user or active_subscription_status.user_type == tenant_user:
                response =landlord_tenant_housing(wa_id[0],message,name,page_number)
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
                            active_subscription_status.landlord_id=landlord_info.id
                            session.commit()
                            return response
                        return welcome_landlord_response
                    except Exception as e:
                        selling_mode_ob = ""
                        # return e
                    return response
                elif message == "2":
                    response = tenant_response
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
            
            if '1' in message:
                try:
                    active_subscription_status.user_status = selling_mode
                    session.commit() 
                except Exception as e:
                    ...
                return selling_response
            
            if  "2" in message:
            
                try:
                    active_subscription_status.user_status = housing_mode
                    session.commit() 
                except Exception as e:
                    ...
                    # return e
                return welcome_response3
            if  '3' in message:
                response = library_response
                try:
                    active_subscription_status.user_status = library_user
                    active_subscription_status.user_type = library_user
                    session.commit()
                except Exception as e:
                    ...
                return response
            
            if "4" in message:
                return join_our_group_response
            
            if "5" in message:
                response = buying_selling_help_help_final
                return response
           
            return welcome_response
    return "eeh"

def get_number_range(string):
    match = re.search(r'\$(\d+)', string)
    if match:
        number = int(match.group(1))
        return range(number - 10, number + 11)
    else:
        return None

def extract_product_details(string):
    product_name, condition, price = "", "", ""
    if 'new' in string:
        condition = 'new'
    elif 'used' in string:
        condition = 'used'
    elif 'boxed' in string:
        condition = 'boxed'
    else:
        condition = 'pre-owned' 

    product_name = string.split(condition)[0].strip()

    price_match = re.findall(r'\$\d+', string)
    if price_match:
        price = float(price_match[0][1:]) 
    else:
        price = 20000 
    return product_name, condition, price

def save_electronics_listing(seller_id, product_name, condition, price):
    seller = session.query(Seller).filter_by(phone_number=seller_id).first()
    if condition == "boxed" or condition =="new":
        condition = "boxed"
    else:
        condition = "pre-owned"
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

def product_analysis(product_id,subscription_id,seller_id):
    try:
        old_product_ob = session.query(ProductsAnalysis).filter_by(product_id=int(product_id)).first()
    except Exception as e:
        old_product_ob = None
    try:
        product_ob = ProductsAnalysis(product_id=int(product_id),product_searcher=int(subscription_id),seller_id=int(seller_id))
        session.add(product_ob)
        if old_product_ob:
            pass
        else:
            session.commit()
    except Exception as e:
        ...

def property_analysis(property_id,subscription_id,landlord_id):
    try:
        old_property_ob = session.query(PropertiesAnalysis).filter_by(property_id=int(property_id)).first()
    except Exception as e:
        old_property_ob = None

    try:
        property_ob = PropertiesAnalysis(property_id=int(property_id),property_searcher=int(subscription_id),landlord_id=int(landlord_id))
        session.add(property_ob)
        if old_property_ob:
            pass
        else:
            session.commit()
    except Exception as e:
        ...

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
    pattern = r'^(.*?)\sin\s(.*?)(?:\s*\$([\d,]+))?$'
    match = re.search(pattern, string)
    house_info, location, budget = "", "", 0
    
    if match:
        house_info = match.group(1)
        location = match.group(2)
        try:
            budget = int(match.group(3).replace(',', '')) if match.group(3) else 100000
        except (IndexError, ValueError):
            budget = 100000
    return house_info, location, budget

def search_rental_properties(house_info, location, budget, page_number, records_per_page):
    session = Session()

    try:
        offset = (page_number - 1) * records_per_page
        properties = session.query(RentalProperty).join(RentalProperty.landlord).\
            filter(RentalProperty.location.ilike(f'%{location}%')).\
            filter(RentalProperty.price.between(0, budget + 100)).\
            offset(offset).limit(records_per_page).all()
        if properties:
            return properties
        else:
            new_location = location.split(" ")[0]
            properties = session.query(RentalProperty).join(RentalProperty.landlord).\
                filter(RentalProperty.location.ilike(f'%{new_location}%')).\
                filter(RentalProperty.price.between(0, budget + 100)).\
                offset(offset).limit(records_per_page).all()
    except Exception as e:
        properties = None
    return properties

def delete_product(product_id,mobile_number):

    try:
        product = session.query(Electronics).filter_by(id=product_id).first()
        if product:
            if f'{mobile_number}' == product.seller.phone_number:
                for products_analysis in product.products_analysis:
                    session.delete(products_analysis)
                product.seller.electronics.remove(product)
                session.delete(product)
                session.commit()
                return f"Product `{product_id}` has been deleted successfully."
            else:
                return "You are not the owner of this product. You can only delete your own products"
        else:
            return "Product not found. Please check the product ID and try again."
    except Exception as e:
        session.rollback()
        return f"Error deleting product"

def delete_property(property_id,mobile_number):
    try:
        property = session.query(RentalProperty).filter_by(id=property_id).first()
        if property:
            if f'{mobile_number}' == property.landlord.phone_number:
                for properties_analysis in property.properties_analysis:
                    session.delete(properties_analysis)
                property.landlord.rental_properties.remove(property)
                session.delete(property)
                session.commit()
                return f"Property `{property_id}` has been deleted successfully."
            else:
                return "You are not the owner of this property. You can only delete your own properties"
        else:
            return "Property not found. Please check the property ID and try again."
    except Exception as e:
        session.rollback()
        return f"Error deleting property"

def edit_product(product_id, new_price,mobile_number):
    if new_price:
        try:
            product = session.query(Electronics).filter_by(id=product_id).first()
        except Exception as e:
            ...
        try:
            if f'{mobile_number}' != product.seller.phone_number:
                return "You are not the owner of this product. You can only edit your own products"
            product.price = new_price
            session.commit()
            return f"Product `{product_id}` has been updated successfully."
        except Exception as e:
            return "wrong product id, please try again, make sure you're using correct the command e.g *edit 1 price = $200*."
    else:
        return f"Please provide a valid new price for the product `{product_id}`."

def edit_property(property_id, new_price,mobile_number):
    if new_price:
        try:
            property = session.query(RentalProperty).filter_by(id=property_id).first()
        except Exception as e:
            ...
        try:
            if f'{mobile_number}' != property.landlord.phone_number:
                return "You are not the owner of this property. You can only edit your own properties"
            property.price = new_price
            session.commit()
            return f"Property `{property_id}` has been updated successfully."
        except Exception as e:
            return "wrong property id, please try again, make sure you're using correct the command e.g *edit 1 price = $200*."
    else:
        return f"Please provide a valid new price for the property `{property_id}`."

def create_seller_subscription(message, mobile_number):
    response = seller_subs_response
    monthly_pricing,quarterly_pricing,half_yearly,yearly_pricing = 1, 2, 4,7
    monthly_sub,quarterly_sub,half_yearly_sub,yearly_sub = "Monthly","Quarterly ","Half Yearly","Yearly"
    try:
        subscription_status = session.query(Subscription).filter_by(mobile_number=mobile_number).first()
        landlord_subscription = session.query(Seller).filter_by(phone_number=mobile_number).first()
        landlord_subscription.subscription=subscription_status.id
        session.commit()
    except Exception as e:
        ...
    if message == "1":
        response = landlord_proceed_with_subs_response.format(monthly_sub,monthly_pricing)
        try:
            subscription_status.subscription_status =monthly_mode
            session.commit()
        except Exception as e:
            ...
            response = error_response
        return response
    elif message == "2":
        response = landlord_proceed_with_subs_response.format(quarterly_sub,quarterly_pricing)
        try:
            subscription_status.subscription_status =quarterly_mode
            session.commit()
        except Exception as e:
            ...
            response = error_response
        return response
    elif message == "3":
        response = landlord_proceed_with_subs_response.format(half_yearly_sub,half_yearly)
        try:
            subscription_status.subscription_status =half_yearly_mode
            session.commit()
        except Exception as e:
            ...
            response = error_response
        return response
    elif message == "4":
        
        response = landlord_proceed_with_subs_response.format(yearly_sub,yearly_pricing)
        try:
            subscription_status.subscription_status =yearly_mode
            session.commit()
        except Exception as e:
            ...
            response = error_response
        return response
    
    if message.lower() == "exit" :
        try:
            landlord_subs_cancelling = session.query(Subscription).filter_by(mobile_number=mobile_number).first()
            landlord_subs_cancelling.subscription_status = new_user
            landlord_subs_cancelling.user_status = seller_user
            session.commit()
        except Exception as e:
            ...
        return seller_response
    if len(message) > 5 and message[:1] == "0" or "ecocash" in message.lower():
        response =validate_payment(message, mobile_number)
        return response
    return response

def create_landlord_subscription(message, mobile_number):
    response = landlord_subs_response
    monthly_pricing,quarterly_pricing,half_yearly,yearly_pricing = 2, 3.80, 5,9
    monthly_sub,quarterly_sub,half_yearly_sub,yearly_sub = "Monthly ","Quarterly ","Half Yearly ","Yearly "
    try:
        subscription_status = session.query(Subscription).filter_by(mobile_number=mobile_number).first()
        landlord_subscription = session.query(Landlord).filter_by(phone_number=mobile_number).first()
        landlord_subscription.subscriptions=subscription_status.id
        session.commit()
    except Exception as e:
        ...
    if message == "1":
        response = landlord_proceed_with_subs_response.format(monthly_sub,monthly_pricing)
        try:
            subscription_status.subscription_status =monthly_mode
            session.commit()
        except Exception as e:
            ...
            response = error_response
        return response
    elif message == "2":
        response = landlord_proceed_with_subs_response.format(quarterly_sub,quarterly_pricing)
        try:
            subscription_status.subscription_status =quarterly_mode
            session.commit()
        except Exception as e:
            ...
            response = error_response
        return response
    elif message == "3":
        response = landlord_proceed_with_subs_response.format(half_yearly_sub,half_yearly)
        try:
            subscription_status.subscription_status =half_yearly_mode
            session.commit()
            return response
        except Exception as e:
            ...
            response = error_response
        return response
    elif message == "4":
        
        response = landlord_proceed_with_subs_response.format(yearly_sub,yearly_pricing)
        try:
            subscription_status.subscription_status =yearly_mode
            session.commit()
        except Exception as e:
            ...
            response = error_response
        return response
    
    if message.lower() == "exit" :
        try:
            landlord_subs_cancelling = session.query(Subscription).filter_by(mobile_number=mobile_number).first()
            landlord_subs_cancelling.subscription_status = new_user
            landlord_subs_cancelling.user_status = landlord_user
            session.commit()
        except Exception as e:
            ...
        return welcome_landlord_response
    if len(message) > 5 and message[:1] == "0" or "ecocash" in message.lower():
        response =validate_payment(message, mobile_number)
        return response
    return response

def create_payment_subscription(amount, mobile_number,subs_plan):
    paynow = Paynow(
        '17264',
        '35848eb0-f1d7-446a-8978-e937926a8f77',
        'http://google.com',
        'http://google.com'
        )
    try:
        payment = paynow.create_payment('Order', 'gtkandeya@gmail.com')
        payment.items=[]
        payment.add(f'Subscription for{subs_plan}', float(amount))

        response = paynow.send_mobile(payment, f'{mobile_number}', 'ecocash')


        if(response.success):
            poll_url = response.poll_url
            status = paynow.check_transaction_status(poll_url)
            return "Your subscription will be activated once you confirm your pin. Please check your phone."
        else:
            pass
    except Exception as e:
        pass

#PAYMENT CREATION
def validate_payment(message,phone_number):
    try:
        Subscription_status = session.query(Subscription).filter_by(mobile_number=phone_number).first()
    except Exception as e:
        ...
    response = "Payment validation..."
    if "transfer confirmation" in message.lower():
        pattern = r"PP(.*?)\bNew wallet"
        match = re.search(pattern, message)
        if match:
            transaction_message_input = match.group(1).strip()
            if transaction_message_input == transaction_message.strip():
                end_date = datetime.now().date() + timedelta(days=30)
                try:
                    if Subscription_status.subscription_status == monthly_mode:
                        end_date = datetime.now().date() + timedelta(days=30)
                    elif Subscription_status.subscription_status == quarterly_mode:
                        end_date = datetime.now().date() + timedelta(days=90)
                    elif Subscription_status.subscription_status == half_yearly_mode:
                        end_date = datetime.now().date() + timedelta(days=180)
                    elif Subscription_status.subscription_status == yearly_mode:
                        end_date = datetime.now().date() + timedelta(days=365)
                    Subscription_status.trial_start_date = datetime.now().date()
                    Subscription_status.trial_end_date = end_date
                    Subscription_status.is_active = True
                    Subscription_status.user_status = Subscription_status.user_type
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
        
    pattern = r'^(077|078)\d{7}$'
    match = re.match(pattern, message)
    if match:
        if Subscription_status.user_type == seller_user:

            if Subscription_status.subscription_status == monthly_mode:
                end_date = datetime.now().date() + timedelta(days=30)
                payment_amount = 1
                subs_period = "Monthly Subscription"
            elif Subscription_status.subscription_status == quarterly_mode:
                end_date = datetime.now().date() + timedelta(days=90)
                payment_amount = 2.30
                subs_period = "Quarterly Subscription"
            elif Subscription_status.subscription_status == half_yearly_mode:
                payment_amount = 4
                end_date = datetime.now().date() + timedelta(days=18)
                subs_period = "Half Yearly Subscription"
            elif Subscription_status.subscription_status == yearly_mode:
                payment_amount = 7
                end_date = datetime.now().date() + timedelta(days=365)
                subs_period = "Yearly Subscription"
        else:
            if Subscription_status.subscription_status == monthly_mode:
                end_date = datetime.now().date() + timedelta(days=30)
                payment_amount = 5.77
                subs_period = "Monthly Subscription"
            elif Subscription_status.subscription_status == quarterly_mode:
                end_date = datetime.now().date() + timedelta(days=90)
                payment_amount = 13.50
                subs_period = "Quarterly Subscription"
            elif Subscription_status.subscription_status == half_yearly_mode:
                payment_amount = 22.10
                end_date = datetime.now().date() + timedelta(days=180)
                subs_period = "Half Yearly Subscription"
            elif Subscription_status.subscription_status == yearly_mode:
                payment_amount = 39
                end_date = datetime.now().date() + timedelta(days=365)
                subs_period = "Yearly Subscription"
        response = create_payment_subscription(payment_amount, f'{message}',subs_period)
        if 'subscription' in response.lower():
            try:
                ...
                # Subscription_status.trial_end_date = end_date
                # Subscription_status.is_active = True
                # Subscription_status.user_status = "activated"
                # session.commit()
            except Exception as e:
                ...
            return response
        else:
            return "Payment failed. Please try again."
    else:
        response = ecocash_number_invalid_response
        return response
    return response

def search_products(product_name, condition, budget, page_number, records_per_page):
    if condition.lower() == "boxed" or condition.lower() == "new":
        condition = "boxed"
    else:
        condition = "pre-owned"
    try:
        offset = (page_number - 1) * records_per_page
        matching_products = session.query(Electronics).join(Electronics.seller).\
            filter(Electronics.gadget_name.ilike(f'{product_name}%')).\
            filter(Electronics.condition.ilike(f'%{condition}%')).\
            filter(Electronics.price.between(0, budget + 100)).\
            offset(offset).limit(records_per_page).all()
        if matching_products:
            return matching_products
        else:
            # matching_products = session.query(Electronics).filter(Electronics.gadget_name.ilike(f'%{product_name}%')).all()
            matching_products = session.query(Electronics).filter(Electronics.gadget_name.ilike(f'%{product_name}%')).\
            offset(offset).limit(records_per_page).all()
    except Exception as e:
        matching_products = None
    return matching_products

def search_document(document_name, requester,request_type):
    try:
        document_code = int(document_name)
        document = session.query(Document).filter_by(id=document_code).first()
        return document.title
    except Exception as e:
        ...

    if document_name.startswith("[") and requester == '263779586059':
        file_name_list = eval(document_name)

        last_document_id = session.query(func.max(Document.id)).scalar() or 0

        for file_name in file_name_list:
            document = session.query(Document).filter_by(title=file_name).first()

            if document:
                pass
            else:
                new_document_id = last_document_id + 1  # Start from the last ID
                document_add = Document(id=new_document_id, title=file_name, category="Library", file_path=requester)
                
                session.add(document_add)
                session.commit()
                last_document_id = new_document_id
        return "Documents added successfully."
    
    if document_name.startswith("add") and requester =='263779586059':
        new_name = document_name.strip("add")
        retries = 0
        while retries < MAX_RETRIES:
            try:
                document_ob = session.query(Document).filter_by(title=new_name).first()
                if document_ob:
                    return "Document already exists."
                document = Document(title=new_name, category="Library", file_path=requester)
                session.add(document)
                session.commit()
                return "Document added successfully."
            except OperationalError as e:
                if "SSL connection has been closed unexpectedly" in str(e):
                    retries += 1
                    print(f"Retrying database query ({retries}/{MAX_RETRIES})")
                    time.sleep(RETRY_DELAY)
                else:
                    raise e

    else:
        try:
            document = session.query(Document).filter(func.lower(Document.title).like(func.lower(f"%{document_name}%"))).first()
            if document:
                response = document.title
                return response
            else:
                try:
                    document_parts = modified_string.split("")
                    modified_string = "".join(document_parts[:3])
                    document = session.query(Document).filter(func.lower(Document.title).like(func.lower(f"%{modified_string}%"))).first()
                    if document:
                        response = document.title
                        return response
                except Exception as e:
                    ...

                modified_string = document_name.replace(" ", "_")
                try:
                    document_parts = modified_string.split("_")
                    modified_string = "_".join(document_parts[:3])
                    document = session.query(Document).filter(func.lower(Document.title).like(func.lower(f"%{modified_string}%"))).first()
                    if document:
                        response = document.title
                        return response
                    else:
                        document_parts = document_name.split("")
                        modified_string = " ".join(document_parts[:3])
                        document = session.query(Document).filter(func.lower(Document.title).like(func.lower(f"%{modified_string}%"))).first()
                        if document:
                            response = document.title
                            return response

                except Exception as e:
                    ...
                document = session.query(Document).filter(func.lower(Document.title).like(func.lower(f"%{modified_string}%"))).first()
                if document:
                    response = document.title
                    return response
                else:
                    modified_string = document_name.replace(" ", "-")
                    
                    document = session.query(Document).filter(func.lower(Document.title).like(func.lower(f"%{modified_string}%"))).first()
                    if document:
                        response = document.title
                        return response
                    else:
                        if '-' in modified_string:
                            modified_string = modified_string.split("-")[0]
                        elif '_' in modified_string:
                            modified_string = modified_string.split("_")[0]
                        else:
                            modified_string = modified_string.split(" ")[0]
                        documents_count = session.query(Document).count()
                        if request_type.lower().startswith("*here"):
                            all_documents = session.query(Document)\
                            .offset(random.randint(1, int(documents_count))).limit(10).all()
                            if all_documents:
                                response = f"{request_type}\n\n"
                                for i, document in enumerate(all_documents, start=random.randint(1, 10)):
                                    response += f"📚 *TITLE*: _{document.title}_\n- *code #️⃣:* {document.id}  \n\n"
                                response += underline_response
                                response += after_books_listing_response
                                data = get_text_message_input(requester, response, None)
                                response = send_message(data)
                                return response
                        else:
                            # all_documents = session.query(Document)\
                            # .offset(random.randint(1, int(documents_count))).limit(10).all()
                            all_documents = session.query(Document).filter(func.lower(Document.title).like(func.lower(f"%{modified_string}%"))).all()
                            if all_documents:
                                response = f"{request_type}\n\n"
                                for i, document in enumerate(all_documents, start=random.randint(1, 10)):
                                    response += f"📚 *TITLE*: _{document.title}_\n- *code #️⃣:* {document.id}  \n\n"
                                response += underline_response
                                response += after_books_listing_response
                                data = get_text_message_input(requester, response, None)
                                response = send_message(data)
                                return response
                    #returning matches with key words
        except Exception as e:
            ...
        return None
    return None

def publish_post(message):
   
    new_message = message.split()
    post_type = new_message[1]
    split_word = "message"
    words = message.split()
    second_word_index = words.index(split_word)
    message = " ".join(words[second_word_index+1:])

    if post_type.lower() == "library":
        user_type = library_user
    elif post_type.lower() == "landlord":
        user_type = landlord_user
    elif post_type.lower() == "tenant":
        user_type = tenant_user
    elif post_type.lower() == "buyer":
        user_type = buyer_user
    elif post_type.lower() == "seller":
        user_type = seller_user
    else:
        user_type = chat_user

    retries = 0
    while retries < MAX_RETRIES:
        try:
            all_users_related = session.query(Subscription).filter_by(user_type=user_type)
            break
        except OperationalError as e:
            if "SSL connection has been closed unexpectedly" in str(e):
                retries += 1
                print(f"Retrying database query ({retries}/{MAX_RETRIES})")
                time.sleep(RETRY_DELAY)
            else:
                raise e

    if all_users_related:
        for user in all_users_related:
            user_mobile = user.mobile_number
            try:
                data = get_text_message_input(user_mobile, message, None)
                response = send_message(data)
            except Exception as e:
                # Handle exception for send_message()
                response = "error sending messages"
        return response
    return 'No users found'

def library_contents_lookup(requester, message):
    if message.lower() in greetings_list:
        return "Hello! Please enter the title of what you are looking for."

    if message.lower() == "more":
        message = "vvvvbvb"
        request_type = '*here are some other random documents you might be interested in:*'
        document_path = search_document(message,requester,request_type)
        data = get_text_message_input(requester, document_path, None)
        response = send_message(data)
        return response
    else:
        custom_message = '*No exact match found!,here are some alternatives*'
        document_path = search_document(message,requester,custom_message)
        if document_path == "Document already exists.":
            return "Document already exists."
        elif document_path == "Document added successfully.":
            return "Document added successfully."
        if document_path:
            try:
                document = session.query(Document).filter_by(title=document_path).first()
                document_id = document.id
            except Exception as e:
                document_id = None
            if document_id and document_id > 1060:
                path=f"https://github.com/godfrey-tankan/My_projects/raw/main/{document_path.strip()}"
            else:
                path=f"https://github.com/godfrey-tankan/My_projects/raw/godfrey-tankan-patch-1/{document_path.strip()}"
        
            data = get_text_message_input(requester, document_path, path)
            response =send_message(data)
            return response
            # response = send_message("",media_files)
        
            # except FileNotFoundError as e:
            #     # Handle the FileNotFoundError appropriately
            #     return f"error somewhere..{e}"
        else:
            message = message.strip()
            if message[:1].isdigit() and message[-1].isalpha():
                return 'please use book code *number* only to get the book'
            return "No document found!\n `tip`: _try searching by the author instead_ ."