import os
from .model import Document
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
import io
from flask import send_file




def search_document(document_name):
    current_directory = os.getcwd() 
    folder_path = current_directory + "/app/utils/documents"
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower() == document_name.lower():
                return os.path.join(root, file)
    return None


def library_contents_lookup(requester, message):
    message = message + ".pdf"
    document_path = search_document(message)
    if document_path:
        print("Document found at:", document_path)
        # try:
        requested_document_by_user = session.query(Document).filter_by(title = message, file_path =requester).first()
        if requested_document_by_user:
            pass
        else:
            requested_document = Document(title=message, category="Library", file_path=requester)
            session.add(requested_document)
            session.commit()
        return send_file(document_path, attachment_filename=message, as_attachment=True)

        # except FileNotFoundError as e:
        #     # Handle the FileNotFoundError appropriately
        #     return f"error somewhere..{e}"
    else:
        return "Document not found! Please check the document name and try again."