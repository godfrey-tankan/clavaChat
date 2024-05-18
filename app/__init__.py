from flask import Flask
from app.config import load_configurations, configure_logging
from .views import webhook_blueprint
from app.utils.model import *
from app.services.user_types import *
import os
from flask import Flask, render_template, request, jsonify
from werkzeug.security import generate_password_hash
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import check_password_hash
from datetime import timedelta
from sqlalchemy.exc import PendingRollbackError
from flask_cors import CORS

app = Flask(__name__,static_folder='static')
CORS(app)
CORS(app, origins=['http://localhost:8000','https://clava.onrender.com'])
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config['TEMPLATES_AUTO_RELOAD'] = True

app.config['SECRET_KEY'] = '112233445566'
app.config['JWT_EXPIRATION_DELTA'] = timedelta(days=2)

jwt = JWTManager(app)


# Load configurations and logging settings
load_configurations(app)
configure_logging()

app.register_blueprint(webhook_blueprint)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        data = request.get_json()
        username = data['username']
        password = data['password']
        if username.startswith('0'):
            username = username.replace('0', '263', 1)

        try:
            user = session.query(User).filter_by(username=username).first()
        except:
            user = None

        if not user:
            return jsonify(message='Wrong Login Credentials!')

        if check_password_hash(user.password, password):
            access_token = create_access_token(identity=user.id, additional_claims={
            'name': user.username,
            'password': user.password
            })
            return jsonify(message='success', access_token=access_token,user_name=user.username), 200
        else:
            return jsonify(message='Wrong Login Credentials.'), 401

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        data = request.get_json()
        username = data['username']
        password = data['password']
        if username.startswith('0'):
            username = username.replace('0', '263', 1)
        try:
            user = session.query(User).filter_by(username=username).first()
        except:
            user = None

        if user:
            return jsonify(message='User already exists')

        hashed_password = generate_password_hash(password)
        user_subscription = session.query(Subscription).filter_by(mobile_number=username).first()

        if not user_subscription:
            user_subscription = Subscription(mobile_number=username, subscription_status='welcome', user_name=username, user_status='new_user', user_type='new_user', user_activity='active')
            session.add(user_subscription)

        try:
            session.commit()
        except PendingRollbackError:
            return jsonify(message='An error occurred during registration. Please try again.'), 500

        user = User(username=username, password=hashed_password, subscription_id=user_subscription.id)
        session.add(user)

        try:
            session.commit()
        except PendingRollbackError:
            return jsonify(message='An error occurred during registration. Please try again.'), 500

        # Generate the access token
        access_token = create_access_token(identity=user.id, additional_claims={
            'name': user.username,
            'password': user.password
        })

        return jsonify(message='success', access_token=access_token,user_name=user.username), 200
