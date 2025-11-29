#!/usr/bin/env python3
"""
Seed script for demo data to use with benchmarks.

Creates a test user and some sample ledger entries.
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from backend.chatbot_backend.db.session import get_db, engine, Base
from backend.chatbot_backend.db.models import User, Conversation
from backend.dashboard.models import LedgerEntry, Customer, Supplier


def seed_demo_data():
    """Seed demo data for benchmarking."""
    db = next(get_db())
    
    try:
        # Check if demo user exists
        demo_phone = "+919999999999"
        user = db.query(User).filter(User.phone_number == demo_phone).first()
        
        if not user:
            # Create demo user
            user = User(
                phone_number=demo_phone,
                name="Demo User",
                shop_name="Demo Shop",
                preferred_language="hi-IN",
                plan="free",
                state="menu"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created demo user: {user.id}")
        else:
            print(f"Demo user exists: {user.id}")
        
        # Create demo conversation
        conversation = db.query(Conversation).filter(Conversation.user_id == user.id).first()
        if not conversation:
            conversation = Conversation(
                user_id=user.id,
                last_message="Hi",
                context={}
            )
            db.add(conversation)
            db.commit()
            print(f"Created demo conversation")
        
        # Create some demo ledger entries
        existing_entries = db.query(LedgerEntry).filter(LedgerEntry.user_id == user.id).count()
        
        if existing_entries < 5:
            demo_entries = [
                LedgerEntry(
                    user_id=user.id,
                    type="sale",
                    amount=500,
                    description="Sold chips to Ramesh",
                    counterparty_name="Ramesh",
                    counterparty_type="customer"
                ),
                LedgerEntry(
                    user_id=user.id,
                    type="expense",
                    amount=200,
                    description="Fuel expense",
                    counterparty_name=None,
                    counterparty_type=None
                ),
                LedgerEntry(
                    user_id=user.id,
                    type="purchase",
                    amount=1000,
                    description="Bought stock from wholesale",
                    counterparty_name="Wholesale Market",
                    counterparty_type="supplier"
                ),
                LedgerEntry(
                    user_id=user.id,
                    type="udhaar",
                    amount=300,
                    description="Udhaar given to Mohan",
                    counterparty_name="Mohan",
                    counterparty_type="customer"
                ),
                LedgerEntry(
                    user_id=user.id,
                    type="payment",
                    amount=150,
                    description="Payment received from Suresh",
                    counterparty_name="Suresh",
                    counterparty_type="customer"
                ),
            ]
            
            for entry in demo_entries:
                db.add(entry)
            
            db.commit()
            print(f"Created {len(demo_entries)} demo ledger entries")
        else:
            print(f"Demo entries exist: {existing_entries}")
        
        # Create demo customers
        existing_customers = db.query(Customer).filter(Customer.user_id == user.id).count()
        
        if existing_customers < 3:
            demo_customers = [
                Customer(user_id=user.id, name="Ramesh", phone_number="+911111111111", outstanding_balance=0),
                Customer(user_id=user.id, name="Mohan", phone_number="+912222222222", outstanding_balance=300),
                Customer(user_id=user.id, name="Suresh", phone_number="+913333333333", outstanding_balance=0),
            ]
            
            for customer in demo_customers:
                db.add(customer)
            
            db.commit()
            print(f"Created {len(demo_customers)} demo customers")
        
        print("\n✅ Demo data seeded successfully!")
        print(f"Demo user ID: {user.id}")
        print(f"Demo phone: {demo_phone}")
        
        return user.id
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
