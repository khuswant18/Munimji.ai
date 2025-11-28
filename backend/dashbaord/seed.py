# backend/dashboard/seed.py
from ..chatbot_backend.db.session import SessionLocal
from ..chatbot_backend.db.models import User
from .models import LedgerEntry, Customer, Supplier

def seed_data():
    db = SessionLocal()
    try:
        # Seed user
        user = User(phone_number="9999999998", name="Test User", shop_name="Test Shop")
        db.add(user)
        db.commit()
        db.refresh(user)
        user_id = user.id

        # Seed customers
        customers = [
            Customer(user_id=user_id, name="Ramesh Kumar", phone="9876543210", outstanding_balance=500.0),
            Customer(user_id=user_id, name="Suresh Patel", phone="9876543211", outstanding_balance=200.0),
            Customer(user_id=user_id, name="Amit Singh", phone="9876543212", outstanding_balance=0.0),
        ]
        db.add_all(customers)

        # Seed suppliers
        suppliers = [
            Supplier(user_id=user_id, name="Supplier A", phone="9123456789", outstanding_balance=300.0),
            Supplier(user_id=user_id, name="Supplier B", phone="9123456790", outstanding_balance=150.0),
            Supplier(user_id=user_id, name="Supplier C", phone="9123456791", outstanding_balance=0.0),
        ]
        db.add_all(suppliers)

        # Seed ledger entries
        ledger_entries = [
            LedgerEntry(user_id=user_id, type="sale", amount=1000.0, description="Cash sale", counterparty_name="Ramesh Kumar", counterparty_type="customer"),
            LedgerEntry(user_id=user_id, type="purchase", amount=500.0, description="Bought goods", counterparty_name="Supplier A", counterparty_type="supplier"),
            LedgerEntry(user_id=user_id, type="udhaar", amount=200.0, description="Udhaar given", counterparty_name="Suresh Patel", counterparty_type="customer"),
            LedgerEntry(user_id=user_id, type="payment", amount=100.0, description="Payment received", counterparty_name="Ramesh Kumar", counterparty_type="customer"),
            LedgerEntry(user_id=user_id, type="expense", amount=50.0, description="Office supplies"),
            # Add more for 20 total
            LedgerEntry(user_id=user_id, type="sale", amount=800.0, description="Online sale"),
            LedgerEntry(user_id=user_id, type="purchase", amount=400.0, description="Raw materials", counterparty_name="Supplier B", counterparty_type="supplier"),
            LedgerEntry(user_id=user_id, type="udhaar", amount=150.0, description="Credit sale", counterparty_name="Amit Singh", counterparty_type="customer"),
            LedgerEntry(user_id=user_id, type="payment", amount=50.0, description="Partial payment", counterparty_name="Suresh Patel", counterparty_type="customer"),
            LedgerEntry(user_id=user_id, type="sale", amount=1200.0, description="Bulk sale"),
            LedgerEntry(user_id=user_id, type="purchase", amount=600.0, description="Equipment", counterparty_name="Supplier C", counterparty_type="supplier"),
            LedgerEntry(user_id=user_id, type="udhaar", amount=300.0, description="Loan given", counterparty_name="Ramesh Kumar", counterparty_type="customer"),
            LedgerEntry(user_id=user_id, type="expense", amount=75.0, description="Transport"),
            LedgerEntry(user_id=user_id, type="sale", amount=900.0, description="Wholesale"),
            LedgerEntry(user_id=user_id, type="purchase", amount=350.0, description="Packaging", counterparty_name="Supplier A", counterparty_type="supplier"),
            LedgerEntry(user_id=user_id, type="payment", amount=200.0, description="Full payment", counterparty_name="Amit Singh", counterparty_type="customer"),
            LedgerEntry(user_id=user_id, type="udhaar", amount=250.0, description="Advance", counterparty_name="Suresh Patel", counterparty_type="customer"),
            LedgerEntry(user_id=user_id, type="sale", amount=1100.0, description="Retail sale"),
            LedgerEntry(user_id=user_id, type="expense", amount=40.0, description="Miscellaneous"),
            LedgerEntry(user_id=user_id, type="purchase", amount=450.0, description="Supplies", counterparty_name="Supplier B", counterparty_type="supplier"),
        ]
        db.add_all(ledger_entries)

        db.commit()
        print("Sample data seeded successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()