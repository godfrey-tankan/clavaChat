import logging
import time
from subprocess import Popen
from app import create_app
app = create_app()

if __name__ == "__main__":
    logging.info("Flask app started")
    app.run(host="0.0.0.0", port=8000)
    while True:
        process = Popen(["python", "chatbot/run.py"])
        time.sleep(10)  # 120 seconds = 2 minutes
        process.terminate()