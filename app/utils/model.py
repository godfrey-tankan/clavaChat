from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    mobile_number = Column(String(20))
    subscription_status = Column(String(20))
    message = Column(String(255))
    trial_start_date = Column(Date)
    trial_end_date = Column(Date)

    @classmethod
    def exists(cls, session, mobile_number):
        return session.query(cls).filter_by(mobile_number=mobile_number).first() is not None
    