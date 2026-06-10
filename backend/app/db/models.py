from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey

Base = declarative_base()

class State(Base):
    __tablename__ = "states"
    state_id = Column(Integer, primary_key=True)
    state_name = Column(String, nullable=False, unique=True)
    state_code = Column(String, nullable=True, unique=True)

class SKU(Base):
    __tablename__ = "skus"
    sku_id = Column(Integer, primary_key=True)
    sku_name = Column(String, nullable=False)
    category_id = Column(Integer, nullable=False)
    volume_ml = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

class Customer(Base):
    __tablename__ = "customers"
    customer_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    state_id = Column(Integer, ForeignKey("states.state_id"))

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")
