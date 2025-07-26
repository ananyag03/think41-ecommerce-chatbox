from sqlalchemy import (
    Column, DateTime, Float, String, Integer, Numeric, Text,
    ForeignKey, Date, create_engine
)
from sqlalchemy.orm import relationship, sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# ---------- DATABASE CONNECTION ----------
DATABASE_URL = "postgresql://postgres:yourpassword@localhost:5432/ecommerce_ai"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ---------- MODELS ----------

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    age = Column(Integer)
    gender = Column(String)
    state = Column(String)
    address = Column(String)
    postal_code = Column(String)
    city = Column(String)
    country = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    traffic_source = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    product_id = Column(String, unique=True)
    name = Column(String)
    category = Column(String)
    price = Column(Numeric)
    description = Column(Text)

class DistributionCenter(Base):
    __tablename__ = 'distribution_centers'
    id = Column(Integer, primary_key=True)
    center_id = Column(String, unique=True)
    name = Column(String)
    location = Column(String)

class InventoryItem(Base):
    __tablename__ = 'inventory_items'
    id = Column(Integer, primary_key=True)
    inventory_id = Column(String, unique=True)
    product_id = Column(String, ForeignKey('product.product_id'))
    center_id = Column(String, ForeignKey('distribution_centers.center_id'))
    stock = Column(Integer)

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    order_id = Column(String, unique=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    order_date = Column(Date)
    status = Column(String)

class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True)
    order_item_id = Column(String, unique=True)
    order_id = Column(String, ForeignKey('orders.order_id'))
    product_id = Column(String, ForeignKey('product.product_id'))
    quantity = Column(Integer)
    price = Column(Numeric)

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String)  # 'user' or 'ai'
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")

# ---------- SESSION UTILS ----------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- UTILITY FUNCTIONS ----------

def get_all_users():
    db: Session = SessionLocal()
    try:
        users = db.query(User).all()
        return [u.__dict__ for u in users]
    finally:
        db.close()

def get_all_orders():
    db: Session = SessionLocal()
    try:
        orders = db.query(Order).all()
        return [o.__dict__ for o in orders]
    finally:
        db.close()

# ---------- INITIALIZE DB ----------

def init_db():
    Base.metadata.create_all(bind=engine)
