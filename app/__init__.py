from flask import Flask
from app.config import load_configurations, configure_logging
from .views import webhook_blueprint
from app.utils.model import *
import os
from flask import Flask, render_template, request, jsonify


app = Flask(__name__,static_folder='static')
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config['TEMPLATES_AUTO_RELOAD'] = True
# Load configurations and logging settings
load_configurations(app)
configure_logging()

# Import and register blueprints, if any
app.register_blueprint(webhook_blueprint)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        data = request.get_json()
        username = data['username']
        password = data['password']

        if username == 'admin' and password == 'admin':
            return jsonify(message='success')
        else:
            return jsonify(message='Invalid credentials')
