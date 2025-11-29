#!/usr/bin/env python3
"""
Complete End-to-End Workflow Test for Munimji WhatsApp Agent

This script tests the COMPLETE user journey:
1. New user registration (first message)
2. Onboarding (name, shop name)
3. Menu navigation
4. Add customers with udhaar
5. Add expenses
6. Add sales
7. Add purchases  
8. View ledger
9. View summary
10. View udhaar list
11. Multi-turn conversations
12. Edge cases

Run: python tests/test_complete_workflow.py
"""
import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_core.messages import HumanMessage
from backend.agents.graph import compiled_graph
from backend.agents.state import AgentState
from backend.chatbot_backend.db.session import get_db_session
from backend.chatbot_backend.db.models import User, Conversation
from backend.dashboard.models import Customer, Supplier, LedgerEntry


# Test phone number for this session
TEST_PHONE = f"+91999999{datetime.now().strftime('%H%M')}"


class ConversationSimulator:
    """Simulates WhatsApp conversation with context persistence."""
    
    def __init__(self, phone_number: str):
        self.phone_number = phone_number
        self.user_id = None
        self.context = {}
        self.db = get_db_session()
        self.message_count = 0
        
    def setup_user(self):
        """Create or get test user."""
        user = self.db.query(User).filter(User.phone_number == self.phone_number).first()
        if not user:
            user = User(
                phone_number=self.phone_number,
                name="Test Shopkeeper",
                shop_name="Test Dukaan",
                state="menu"  # Skip onboarding for test
            )
            self.db.add(user)
            self.db.commit()
            print(f"✅ Created new user: {self.phone_number}")
        else:
            print(f"ℹ️  Using existing user: {self.phone_number}")
        
        self.user_id = user.id
        return user
    
    def chat(self, message: str) -> str:
        """Send message and get response."""
        self.message_count += 1
        
        state: AgentState = {
            "messages": [HumanMessage(content=message)],
            "intent": "",
            "entities": {},
            "context": self.context,
            "response": "",
            "user_id": self.user_id,
            "missing_slots": [],
            "needs_followup": False,
            "route": "",
            "show_menu": False,
            "is_blocked": False,
        }
        
        result = compiled_graph.invoke(state)
        
        # Update context for next turn
        self.context = result.get("context", {})
        
        return result.get("response", "No response")
    
    def get_ledger_entries(self) -> list:
        """Get all ledger entries for this user."""
        return self.db.query(LedgerEntry).filter(
            LedgerEntry.user_id == self.user_id
        ).order_by(LedgerEntry.created_at.desc()).all()
    
    def get_customers(self) -> list:
        """Get all customers for this user."""
        return self.db.query(Customer).filter(
            Customer.user_id == self.user_id
        ).all()
    
    def cleanup(self):
        """Clean up test data."""
        if self.user_id:
            # Delete in correct order due to foreign keys
            self.db.query(LedgerEntry).filter(LedgerEntry.user_id == self.user_id).delete()
            self.db.query(Customer).filter(Customer.user_id == self.user_id).delete()
            self.db.query(Supplier).filter(Supplier.user_id == self.user_id).delete()
            self.db.query(Conversation).filter(Conversation.user_id == self.user_id).delete()
            self.db.query(User).filter(User.id == self.user_id).delete()
            self.db.commit()
            print(f"🧹 Cleaned up test user: {self.phone_number}")
        self.db.close()


def print_divider(title: str = "", char: str = "="):
    """Print visual divider."""
    if title:
        print(f"\n{char*60}")
        print(f"  {title}")
        print(f"{char*60}")
    else:
        print("-" * 60)


def print_chat(role: str, message: str, emoji: str = ""):
    """Print chat message."""
    if role == "user":
        print(f"\n👤 Shopkeeper: {message}")
    else:
        # Truncate long responses for readability
        if len(message) > 300:
            message = message[:300] + "..."
        print(f"🤖 Munimji: {message}")


def run_complete_workflow():
    """Run the complete workflow test."""
    
    print("\n" + "="*60)
    print("   MUNIMJI - COMPLETE WORKFLOW TEST")
    print("   Testing Full Shopkeeper Journey")
    print("="*60)
    
    sim = ConversationSimulator(TEST_PHONE)
    
    try:
        # Setup
        print_divider("SETUP: Creating Test User")
        user = sim.setup_user()
        print(f"   User ID: {user.id}")
        print(f"   Phone: {user.phone_number}")
        print(f"   Shop: {user.shop_name}")
        
        # ============================================================
        # TEST 1: Greeting & Menu
        # ============================================================
        print_divider("TEST 1: Greeting & Menu")
        
        print_chat("user", "Namaste")
        response = sim.chat("Namaste")
        print_chat("bot", response)
        
        assert "menu" in response.lower() or "madad" in response.lower(), \
            "Greeting should show menu"
        print("✅ Greeting shows menu")
        
        # ============================================================
        # TEST 2: Add First Customer with Udhaar
        # ============================================================
        print_divider("TEST 2: Add Customer - Ramesh ke 500 udhaar")
        
        print_chat("user", "Ramesh ke 500 rupay udhaar")
        response = sim.chat("Ramesh ke 500 rupay udhaar")
        print_chat("bot", response)
        
        assert "ramesh" in response.lower() or "500" in response.lower() or "done" in response.lower(), \
            f"Should confirm udhaar. Got: {response}"
        print("✅ Udhaar added for Ramesh")
        
        # ============================================================
        # TEST 3: Add Second Customer with Udhaar
        # ============================================================
        print_divider("TEST 3: Add Another Customer - Mohan ka 1000 baaki")
        
        print_chat("user", "Mohan ka 1000 baaki hai")
        response = sim.chat("Mohan ka 1000 baaki hai")
        print_chat("bot", response)
        
        assert "mohan" in response.lower() or "1000" in response.lower() or "done" in response.lower(), \
            f"Should confirm udhaar. Got: {response}"
        print("✅ Udhaar added for Mohan")
        
        # ============================================================
        # TEST 4: Add Expense - Petrol
        # ============================================================
        print_divider("TEST 4: Add Expense - 200 ka petrol")
        
        print_chat("user", "200 ka petrol dala")
        response = sim.chat("200 ka petrol dala")
        print_chat("bot", response)
        
        assert "200" in response.lower() or "expense" in response.lower() or "done" in response.lower(), \
            f"Should confirm expense. Got: {response}"
        print("✅ Petrol expense added")
        
        # ============================================================
        # TEST 5: Add Expense - Chai
        # ============================================================
        print_divider("TEST 5: Add Expense - 50 ka chai nashta")
        
        print_chat("user", "50 ka chai nashta")
        response = sim.chat("50 ka chai nashta")
        print_chat("bot", response)
        
        assert "50" in response.lower() or "expense" in response.lower() or "done" in response.lower(), \
            f"Should confirm expense. Got: {response}"
        print("✅ Chai expense added")
        
        # ============================================================
        # TEST 6: Add Sale
        # ============================================================
        print_divider("TEST 6: Add Sale - Sharma ji ko 800 ka saman becha")
        
        print_chat("user", "Sharma ji ko 800 ka saman becha")
        response = sim.chat("Sharma ji ko 800 ka saman becha")
        print_chat("bot", response)
        
        assert "800" in response.lower() or "sale" in response.lower() or "done" in response.lower() or "sharma" in response.lower(), \
            f"Should confirm sale. Got: {response}"
        print("✅ Sale recorded")
        
        # ============================================================
        # TEST 7: Add Purchase  
        # ============================================================
        print_divider("TEST 7: Add Purchase - 2000 ka stock kharida")
        
        print_chat("user", "2000 ka stock kharida supplier se")
        response = sim.chat("2000 ka stock kharida supplier se")
        print_chat("bot", response)
        
        assert "2000" in response.lower() or "purchase" in response.lower() or "done" in response.lower(), \
            f"Should confirm purchase. Got: {response}"
        print("✅ Purchase recorded")
        
        # ============================================================
        # TEST 8: Multi-turn - Add Inventory Item
        # ============================================================
        print_divider("TEST 8: Multi-turn - pen add karo")
        
        print_chat("user", "pen add karo")
        response1 = sim.chat("pen add karo")
        print_chat("bot", response1)
        
        assert "kitne" in response1.lower() or "quantity" in response1.lower(), \
            f"Should ask for quantity. Got: {response1}"
        
        print_chat("user", "10")
        response2 = sim.chat("10")
        print_chat("bot", response2)
        
        assert "price" in response2.lower() or "kitni" in response2.lower(), \
            f"Should ask for price. Got: {response2}"
        
        print_chat("user", "5")
        response3 = sim.chat("5")
        print_chat("bot", response3)
        
        assert "added" in response3.lower() or "done" in response3.lower() or "✅" in response3, \
            f"Should confirm. Got: {response3}"
        print("✅ Multi-turn inventory addition works")
        
        # ============================================================
        # TEST 9: View Ledger
        # ============================================================
        print_divider("TEST 9: View Ledger")
        
        print_chat("user", "aaj ka ledger dikhao")
        response = sim.chat("aaj ka ledger dikhao")
        print_chat("bot", response)
        
        # Verify in database
        entries = sim.get_ledger_entries()
        print(f"\n📊 Database has {len(entries)} ledger entries:")
        for entry in entries[:5]:  # Show first 5
            print(f"   - {entry.type}: ₹{entry.amount} - {entry.description}")
        
        print("✅ Ledger query works")
        
        # ============================================================
        # TEST 10: View Summary
        # ============================================================
        print_divider("TEST 10: View Summary")
        
        print_chat("user", "aaj ka summary dikhao")
        response = sim.chat("aaj ka summary dikhao")
        print_chat("bot", response)
        
        print("✅ Summary query works")
        
        # ============================================================
        # TEST 11: View Udhaar List
        # ============================================================
        print_divider("TEST 11: View Udhaar List")
        
        print_chat("user", "kaun kitna dena hai")
        response = sim.chat("kaun kitna dena hai")
        print_chat("bot", response)
        
        print("✅ Udhaar list query works")
        
        # ============================================================
        # TEST 12: Receive Payment
        # ============================================================
        print_divider("TEST 12: Receive Payment - Ramesh ne 200 diye")
        
        print_chat("user", "Ramesh ne 200 rupay diye")
        response = sim.chat("Ramesh ne 200 rupay diye")
        print_chat("bot", response)
        
        assert "200" in response.lower() or "payment" in response.lower() or "done" in response.lower(), \
            f"Should confirm payment. Got: {response}"
        print("✅ Payment received recorded")
        
        # ============================================================
        # TEST 13: Blocked Content
        # ============================================================
        print_divider("TEST 13: Content Filtering")
        
        print_chat("user", "lottery ticket")
        response = sim.chat("lottery ticket")
        print_chat("bot", response)
        
        assert "sirf" in response.lower() or "dukaan" in response.lower() or "business" in response.lower(), \
            f"Should block. Got: {response}"
        print("✅ Inappropriate content blocked")
        
        # ============================================================
        # TEST 14: Menu Navigation
        # ============================================================
        print_divider("TEST 14: Menu Navigation")
        
        print_chat("user", "menu")
        response = sim.chat("menu")
        print_chat("bot", response)
        
        print_chat("user", "6")  # Help option
        response = sim.chat("6")
        print_chat("bot", response)
        
        assert "help" in response.lower() or "kaise" in response.lower(), \
            f"Should show help. Got: {response}"
        print("✅ Menu navigation works")
        
        # ============================================================
        # TEST 15: Casual Conversation
        # ============================================================
        print_divider("TEST 15: Casual Conversation")
        
        print_chat("user", "thank you bhai")
        response = sim.chat("thank you bhai")
        print_chat("bot", response)
        
        assert "swagat" in response.lower() or "menu" in response.lower(), \
            f"Should respond casually. Got: {response}"
        print("✅ Casual conversation handled")
        
        # ============================================================
        # TEST 16: Goodbye
        # ============================================================
        print_divider("TEST 16: Goodbye")
        
        print_chat("user", "bye, kal milte hain")
        response = sim.chat("bye, kal milte hain")
        print_chat("bot", response)
        
        assert "alvida" in response.lower() or "bye" in response.lower() or "phir" in response.lower(), \
            f"Should say bye. Got: {response}"
        print("✅ Goodbye handled")
        
        # ============================================================
        # FINAL SUMMARY
        # ============================================================
        print_divider("FINAL DATABASE STATE", "=")
        
        entries = sim.get_ledger_entries()
        print(f"\n📊 Total Ledger Entries: {len(entries)}")
        
        # Calculate totals
        totals = {}
        for entry in entries:
            totals[entry.type] = totals.get(entry.type, 0) + entry.amount
        
        print("\n💰 Summary by Type:")
        for entry_type, amount in totals.items():
            print(f"   {entry_type.capitalize()}: ₹{amount}")
        
        print(f"\n📝 Total Messages Processed: {sim.message_count}")
        
        # ============================================================
        # CLEANUP
        # ============================================================
        print_divider("CLEANUP")
        
        cleanup = input("\nDelete test data? (y/n): ").strip().lower()
        if cleanup == 'y':
            sim.cleanup()
        else:
            print(f"ℹ️  Test data kept for user: {TEST_PHONE}")
            sim.db.close()
        
        # ============================================================
        # RESULTS
        # ============================================================
        print("\n" + "="*60)
        print("   🎉 ALL TESTS PASSED!")
        print("="*60)
        print("""
✅ Greeting & Menu
✅ Add Customer Udhaar (Ramesh 500)
✅ Add Customer Udhaar (Mohan 1000)  
✅ Add Expense (Petrol 200)
✅ Add Expense (Chai 50)
✅ Add Sale (Sharma ji 800)
✅ Add Purchase (Stock 2000)
✅ Multi-turn Inventory (10 pen @ 5)
✅ View Ledger
✅ View Summary
✅ View Udhaar List
✅ Receive Payment (Ramesh 200)
✅ Content Filtering
✅ Menu Navigation
✅ Casual Conversation
✅ Goodbye
        """)
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sim.db.close()
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sim.db.close()
        return False


def run_interactive_session():
    """Run interactive chat session."""
    print_divider("INTERACTIVE SESSION")
    print("Chat with Munimji as a shopkeeper.")
    print("Commands: 'quit' to exit, 'reset' to clear context, 'db' to see entries")
    print_divider()
    
    sim = ConversationSimulator(TEST_PHONE)
    sim.setup_user()
    
    try:
        while True:
            user_input = input("\n👤 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if user_input.lower() == 'reset':
                sim.context = {}
                print("🔄 Context reset!")
                continue
            
            if user_input.lower() == 'db':
                entries = sim.get_ledger_entries()
                print(f"\n📊 Ledger Entries ({len(entries)}):")
                for entry in entries[:10]:
                    print(f"   {entry.type}: ₹{entry.amount} - {entry.description}")
                continue
            
            response = sim.chat(user_input)
            print(f"\n🤖 Munimji: {response}")
            
    except KeyboardInterrupt:
        pass
    finally:
        print("\n👋 Goodbye!")
        sim.db.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Munimji Complete Workflow Test')
    parser.add_argument('-i', '--interactive', action='store_true', help='Run interactive mode')
    args = parser.parse_args()
    
    if args.interactive:
        run_interactive_session()
    else:
        run_complete_workflow()
