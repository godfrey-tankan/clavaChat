import logging
import time
from subprocess import Popen
from app import app
from flask_jwt_extended import JWTManager

@app.route('/about')
def hello():
    return "Welcome to clavaChat!"
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
   