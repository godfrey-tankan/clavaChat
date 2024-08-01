from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean, DateTime
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
    user_activity = Column(String)
    is_active = Column(Boolean, default=True)
    landlord_id = Column(Integer, ForeignKey('landlords.id'))
    landlord = relationship("Landlord", back_populates="subscriptions")
    students = relationship("Student", backref="subscription")
    seller = relationship("Seller", back_populates="subscription")
    products_analysis = relationship("ProductsAnalysis", back_populates="subscription")
    property_analysis = relationship("PropertiesAnalysis", back_populates="subscription")

    @classmethod
    def exists(cls, session, mobile_number):
        return session.query(cls).filter_by(mobile_number=mobile_number).first() is not None

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    email = Column(String)
    phone_number = Column(String)
    is_active = Column(Boolean, default=True)
    user_type = Column(String)
    user_activity = Column(String)
    subscription_id = Column(Integer, ForeignKey('subscriptions.id'))  # Foreign key linking the tables

    @classmethod
    def exists(cls, session, username):
        return session.query(cls).filter_by(username=username).first() is not None

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
    subscriptions = relationship("Subscription", back_populates="landlord")
    property_analysis = relationship("PropertiesAnalysis", back_populates="landlord")

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
    properties_analysis = relationship("PropertiesAnalysis", back_populates="property")


class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    category = Column(String)
    file_path = Column(String)

class ProductsAnalysis(Base):
    __tablename__ = 'products_analysis'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('electronics.id'), nullable=False)
    product_searcher = Column(Integer, ForeignKey('subscriptions.id'))
    seller_id = Column(Integer, ForeignKey('sellers.id'))
    seller = relationship("Seller", back_populates="product_analysis")
    product = relationship("Electronics", back_populates="products_analysis")
    subscription = relationship("Subscription", back_populates="products_analysis")

class PropertiesAnalysis(Base):
    __tablename__ = 'properties_analysis'

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('rental_properties.id'), nullable=False)
    property_searcher = Column(Integer, ForeignKey('subscriptions.id'))
    landlord_id = Column(Integer, ForeignKey('landlords.id'))
    landlord = relationship("Landlord", back_populates="property_analysis")
    property = relationship("RentalProperty", back_populates="properties_analysis")
    subscription = relationship("Subscription", back_populates="property_analysis")

class Electronics(Base):
    __tablename__ = 'electronics'

    id = Column(Integer, primary_key=True)
    gadget_name = Column(String)
    condition = Column(String)
    price = Column(Integer)
    seller_id = Column(Integer, ForeignKey('sellers.id'))
    seller = relationship("Seller", back_populates="electronics")
    products_analysis = relationship("ProductsAnalysis", back_populates="product")

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

class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    student_name = Column(String)
    student_id = Column(String)
    student_course = Column(String)
    student_year = Column(String)
    student_email = Column(String)
    student_phone = Column(String)
    student_address = Column(String)
    subscription_id = Column(Integer, ForeignKey('subscriptions.id'))  # Foreign key linking the tables


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
    subscription_id = Column(Integer, ForeignKey('subscriptions.id'))
    subscription = relationship("Subscription", back_populates="seller")
    subscription = relationship("Subscription", back_populates="seller")
    product_analysis = relationship("ProductsAnalysis", back_populates="seller")

# Update the database connection URL for PostgreSQL
# engine = create_engine('postgresql://clavadb_owner:07dJHxYhXqMw@ep-white-firefly-a5yg5yyf.us-east-2.aws.neon.tech/clavadb?sslmode=require')
# engine = create_engine('postgresql://clavadb_owner:07dJHxYhXqMw@ep-white-firefly-a5yg5yyf-pooler.us-east-2.aws.neon.tech/clavadb?sslmode=require')


# engine = create_engine('sqlite:///clava_db.db')
engine = create_engine('postgresql://clava:dkdS5RlfUzgHOHkQy7rTfBAjRbpJ9qAK@dpg-cqig13ogph6c738oorig-a.oregon-postgres.render.com/clava')

Base.metadata.create_all(engine) # Create the tables if they don't exist
# Create a session
Session = sessionmaker(bind=engine)
session = Session()