from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
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
    subscription_referral = Column(String)
    user_type = Column(String)
    user_activity=Column(String)
    @classmethod
    def exists(cls, session, mobile_number):
        return session.query(cls).filter_by(mobile_number=mobile_number).first() is not None

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    message = Column(String)
    phone_number = Column(String)


class Landlord(Base):
    __tablename__ = 'landlords'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    phone_number = Column(String)
    rental_properties = relationship("RentalProperty", back_populates="landlord")
    subscription = relationship("Subscription", back_populates="landlord")


class RentalProperty(Base):
    __tablename__ = 'rental_properties'

    id = Column(Integer, primary_key=True)
    landlord_id = Column(Integer, ForeignKey('landlords.id'))
    house_info = Column(String)
    location = Column(String)
    price = Column(Integer)
    description = Column(String)
    picture = Column(String)
    landlord = relationship("Landlord", back_populates="rental_properties")
    


class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    category = Column(String)
    file_path = Column(String)

class Electronics(Base):
    __tablename__ = 'electronics'

    id = Column(Integer, primary_key=True)
    gadget_name = Column(String)
    condition = Column(String)
    price = Column(Integer)
    seller_id = Column(Integer, ForeignKey('sellers.id'))
    seller = relationship("Seller", back_populates="electronics")

class Clothes(Base):
    __tablename__ = 'clothes'

    id = Column(Integer, primary_key=True)
    garment_type = Column(String)
    seller_id = Column(Integer, ForeignKey('sellers.id'))

    seller = relationship("Seller", back_populates="clothes")

class Accessories(Base):
    __tablename__ = 'accessories'

    id = Column(Integer, primary_key=True)
    accessory_type = Column(String)
    seller_id = Column(Integer, ForeignKey('sellers.id'))
    seller = relationship("Seller", back_populates="accessories")

class Students(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    student_name = Column(String)
    student_id = Column(String)
    student_course = Column(String)
    student_year = Column(String)
    student_email = Column(String)
    student_phone = Column(String)
    student_address = Column(String)
    Subscription = relationship("Subscription", back_populates="students")
    document = relationship("Document", back_populates="students")


class Cars(Base):
    __tablename__ = 'cars'

    id = Column(Integer, primary_key=True)
    car_make = Column(String)
    car_model = Column(String)
    seller_id = Column(Integer, ForeignKey('sellers.id'))

    seller = relationship("Seller", back_populates="cars")

class Food(Base):
    __tablename__ = 'food'

    id = Column(Integer, primary_key=True)
    dish_name = Column(String)
    seller_id = Column(Integer, ForeignKey('sellers.id'))

    seller = relationship("Seller", back_populates="food")

class Seller(Base):
    __tablename__ = 'sellers'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    phone_number = Column(String)
    electronics = relationship("Electronics", back_populates="seller")
    clothes = relationship("Clothes", back_populates="seller")
    accessories = relationship("Accessories", back_populates="seller")
    cars = relationship("Cars", back_populates="seller")
    food = relationship("Food", back_populates="seller")
    subscription = relationship("Subscription", back_populates="seller")

engine = create_engine('sqlite:///subscriptions.db')
Base.metadata.create_all(engine)  # Create the tables if they don't exist

Session = sessionmaker(bind=engine)
session = Session()
today = datetime.now().date()