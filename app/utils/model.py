from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime


Base = declarative_base()

class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True)
    mobile_number = Column(String)
    subscription_status = Column(String)
    user_name = Column(String)
    user_status = Column(String)
    trial_start_date = Column(Date)
    trial_end_date = Column(Date)
    @classmethod
    def exists(cls, session, mobile_number):
        return session.query(cls).filter_by(mobile_number=mobile_number).first() is not None
    
engine = create_engine('sqlite:///subscriptions.db')
Base.metadata.create_all(engine)  # Create the table if it doesn't exist
Session = sessionmaker(bind=engine)
session = Session()
today = datetime.now().date()