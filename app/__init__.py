from flask import Flask
from app.config import load_configurations, configure_logging
from .views import webhook_blueprint

app = Flask(__name__)

# Load configurations and logging settings
load_configurations(app)
configure_logging()

# Import and register blueprints, if any
app.register_blueprint(webhook_blueprint)

if __name__ == '__main__':
    # Run the app on port 8000
    app.run(host='0.0.0.0', port=8000)