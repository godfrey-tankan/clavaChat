import logging
import json
from flask import Flask, render_template,redirect, url_for
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from .decorators.security import signature_required
from .utils.whatsapp_utils import (
    process_whatsapp_message,
    is_valid_whatsapp_message,
    send_message_template,
)
from app.utils.model import *
webhook_blueprint = Blueprint("webhook", __name__)

def handle_message():
    body = request.get_json()
    if (
        body.get("entry", [{}])[0]
        .get("changes", [{}])[0]
        .get("value", {})
        .get("statuses")
    ):
        # logging.info("Received a WhatsApp status update.")
        return jsonify({"status": "ok"}), 200

    try:
        if is_valid_whatsapp_message(body):
            process_whatsapp_message(body)
            return jsonify({"status": "ok"}), 200
        
        else:
            send_message_template(body)
            return jsonify({"status": "ok"}), 200
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON")
        return jsonify({"status": "error", "message": "Invalid JSON provided"}), 400
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode and token:
        if mode == "subscribe" and token == current_app.config["VERIFY_TOKEN"]:
            logging.info("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            logging.info("VERIFICATION_FAILED")
            return jsonify({"status": "error", "message": "Verification failed"}), 403
    else:
        logging.info("MISSING_PARAMETER")
        return jsonify({"status": "error", "message": "Missing parameters"}), 400

@webhook_blueprint.route("/webhook", methods=["POST","GET"])
# @signature_required
def webhook():
    if request.method == "GET":
        return verify()
    elif request.method == "POST":
        return handle_message()

@webhook_blueprint.route("/home", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        data = request.get_json()  # Retrieve JSON data from the request body
        # Process the data as needed
    
    text = "hey man!"
    return render_template("index.html", text=text)

@webhook_blueprint.route("/subscriptions", methods=["POST", "GET"])
def subscriptions():
    if request.method == "POST":
        request_data = request.get_json()
        return render_template("subscriptions.html", data=request_data)

    elif request.method == "GET":
        args = request.args.to_dict(flat=False)
       
        if 'userName' in args:
            userName = args['userName'][0]
            userName = userName.replace("0", "263", 1)
            
            subscription_plan = session.query(Subscription).filter_by(mobile_number=userName).first()
            if subscription_plan:
                data = subscription_plan.subscription_status
                print("data", data)
                return jsonify(data)
        
    return render_template("subscriptions.html", data="No subs")

@webhook_blueprint.route("/subscription_plan", methods=["POST", "GET"])
def subscription_plan():
    if request.method == "POST":
        data = request.get_json()
        userName = data.get("user_name")
        if userName:
            userName = userName.replace("0", "263", 1)
        try:
            subscription_plan = session.query(Subscription).filter_by(mobile_number=userName).first()
        except Exception as e:
            ...
        if subscription_plan:
            data = {
                "subscription_status": subscription_plan.subscription_status,
                "expiry_date": subscription_plan.trial_end_date,
                "is_active": subscription_plan.is_active,
            }
            return jsonify(data)
        else:
            return jsonify({"error": "You have no active subscription plan"})

    elif request.method == "GET":
        args = request.args.to_dict(flat=False)
        if 'userName' in args:
            userName = args['userName'][0]
            userName = userName.replace("0", "263", 1)
            try:
                subscription_plan = session.query(Subscription).filter_by(mobile_number=userName).first()
            except Exception as e:
                ...
            if subscription_plan:
                data = {
                    "subscription_status": subscription_plan.subscription_status,
                }
                return jsonify(data)

    return jsonify({"error": "Invalid request"})