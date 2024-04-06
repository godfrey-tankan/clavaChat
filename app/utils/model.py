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

    @classmethod
    def exists(cls, session, mobile_number):
        return session.query(cls).filter_by(mobile_number=mobile_number).first() is not None


class Landlord(Base):
    __tablename__ = 'landlords'

    id = Column(Integer, primary_key=True)
    phone_number = Column(String)
    rental_properties = relationship("RentalProperty", back_populates="landlord")


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
    seller_id = Column(Integer, ForeignKey('sellers.id'))

    seller = relationship("Seller", back_populates="gadgets")

class Clothes(Base):
    __tablename__ = 'clothes'

    id = Column(Integer, primary_key=True)
    garment_type = Column(String)
    seller_id = Column(Integer, ForeignKey('sellers.id'))

    seller = relationship("Seller", back_populates="gadgets")

class Accessories(Base):
    __tablename__ = 'accessories'

    id = Column(Integer, primary_key=True)
    accessory_type = Column(String)
    seller_id = Column(Integer, ForeignKey('sellers.id'))

    seller = relationship("Seller", back_populates="gadgets")

class Cars(Base):
    __tablename__ = 'cars'

    id = Column(Integer, primary_key=True)
    car_make = Column(String)
    car_model = Column(String)
    seller_id = Column(Integer, ForeignKey('sellers.id'))

    seller = relationship("Seller", back_populates="gadgets")

class Food(Base):
    __tablename__ = 'food'

    id = Column(Integer, primary_key=True)
    dish_name = Column(String)
    seller_id = Column(Integer, ForeignKey('sellers.id'))

    seller = relationship("Seller", back_populates="gadgets")

class Seller(Base):
    __tablename__ = 'sellers'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    phone_number = Column(String)
    gadgets = relationship("Gadget", back_populates="seller")

engine = create_engine('sqlite:///data.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
today = datetime.now().date()