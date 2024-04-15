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
    print("current_directory:", current_directory)
    folder_path = current_directory + "/app/utils/documents"
    print("folder_path:", folder_path)
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
        try:
            requested_document_by_user = session.query(Document).filter(and_(Document.title == message, Document.file_path == requester)).first()
            if requested_document_by_user:
                # return send_file(document_path, mimetype='application/pdf')
                response = send_file(document_path, attachment_filename=message, as_attachment=True)
                print(response, "response", type(response))
                return response
            else:
                requested_document = Document(title=message, category="Library", file_path=requester,mimetype='application/pdf')
                session.add(requested_document)
                session.commit()
                response = send_file(document_path, attachment_filename=message, as_attachment=True)
                print(response, "response", type(response))
                return response

        except FileNotFoundError as e:
            # Handle the FileNotFoundError appropriately
            return f"error somewhere..{e}"
    else:
        return None