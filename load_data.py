# backend/load_data.py
import pandas as pd
from requests import session
from db import init_db, SessionLocal, User, Product, DistributionCenter, InventoryItem, Order, OrderItem
from datetime import datetime
import csv
from dateutil import parser
from requests import session

def load_users(csv_path):
    with open(csv_path, newline='') as csvfile:
        session = SessionLocal()  #
        reader = csv.DictReader(csvfile)
        for row in reader:
            user = User(
                user_id=int(row["id"]),
                first_name=row['first_name'],
                last_name=row['last_name'],
                email=row["email"],
                age=int(row["age"]),
                gender=row["gender"],
                state=row["state"],
                address=row["street_address"],
                postal_code=row["postal_code"],
                city=row["city"],
                country=row["country"],
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
                traffic_source=row["traffic_source"],
                created_at = datetime.strptime(row["created_at"].split("+")[0], "%Y-%m-%d %H:%M:%S.%f")
            )
            session.add(user)
        session.commit()
        session.close()



def load_products(csv_path):
    df = pd.read_csv(csv_path)
    session = SessionLocal()
    for _, row in df.iterrows():
        session.merge(Product(
            product_id=row['product_id'],
            name=row['name'],
            category=row['category'],
            price=row['price'],
            description=row['description']
        ))
    session.commit()
    session.close()

def load_distribution_centers(csv_path):
    df = pd.read_csv(csv_path)
    session = SessionLocal()
    for _, row in df.iterrows():
        session.merge(DistributionCenter(
            center_id=row['center_id'],
            name=row['name'],
            location=row['location']
        ))
    session.commit()
    session.close()

def load_inventory_items(csv_path):
    df = pd.read_csv(csv_path)
    session = SessionLocal()
    for _, row in df.iterrows():
        session.merge(InventoryItem(
            inventory_id=row['inventory_id'],
            product_id=row['product_id'],
            center_id=row['center_id'],
            stock=row['stock']
        ))
    session.commit()
    session.close()

def load_orders(csv_path):
    df = pd.read_csv(csv_path)
    session = SessionLocal()
    for _, row in df.iterrows():
        session.merge(Order(
            order_id=row['order_id'],
            user_id=row['user_id'],
            order_date=pd.to_datetime(row['order_date']).date(),
            status=row['status']
        ))
    session.commit()
    session.close()

def load_order_items(csv_path):
    df = pd.read_csv(csv_path)
    session = SessionLocal()
    for _, row in df.iterrows():
        session.merge(OrderItem(
            order_item_id=row['order_item_id'],
            order_id=row['order_id'],
            product_id=row['product_id'],
            quantity=row['quantity'],
            price=row['price']
        ))
    session.commit()
    session.close()

if __name__ == "__main__":
    init_db()
    load_users("backend/data/users.csv")
    load_products("backend/data/product.csv")
    load_distribution_centers("backend/data/distribution_centers.csv")
    load_inventory_items("backend/data/inventory_items.csv")
    load_orders("backend/data/orders.csv")
    load_order_items("backend/data/order_items.csv")
    print("✅ Data successfully loaded into the database!")
