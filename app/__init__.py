from flask import Flask
from app.config import load_configurations, configure_logging
from .views import webhook_blueprint
from app.utils.model import *
import os


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config['TEMPLATES_AUTO_RELOAD'] = True
# Load configurations and logging settings
load_configurations(app)
configure_logging()

# Import and register blueprints, if any
app.register_blueprint(webhook_blueprint)

