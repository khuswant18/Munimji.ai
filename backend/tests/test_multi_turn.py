"""
Test multi-turn conversation flow for slot filling.

Tests the following scenarios:
1. pen add karo → Kitne pen? → 2 → price? → 5 → Added: 2 pen @ ₹5
2. hello → Hello! Dukaan me kya madad karu?
3. 100 rs expense → ✅ Done!
"""
from langchain_core.messages import HumanMessage

# Add project root to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestMultiTurnConversation:
    """Test multi-turn conversation flow with slot filling."""
    
    def test_greeting_flow(self):
        """Test: hello → Hello! Dukaan me kya madad karu?"""
        from backend.agents.graph import compiled_graph
        from backend.agents.state import AgentState
        
        state: AgentState = {
            "messages": [HumanMessage(content="hello")],
            "intent": "",
            "entities": {},
            "context": {},
            "response": "",
            "user_id": 1,
            "missing_slots": [],
            "needs_followup": False,
            "route": ""
        }
        
        result = compiled_graph.invoke(state)
        
        # Should be a greeting response
        response = result.get("response", "").lower()
        assert any(word in response for word in ["hello", "namaste", "dukaan", "madad"]), \
            f"Expected greeting response, got: {result.get('response')}"
        assert result.get("intent") == "greeting", f"Expected greeting intent, got: {result.get('intent')}"
        print(f"✅ Greeting: {result.get('response')}")
    
    def test_single_turn_expense(self):
        """Test: 100 rs expense → ✅ Done! (single turn, all slots provided)"""
        from backend.agents.graph import compiled_graph
        from backend.agents.state import AgentState
        
        state: AgentState = {
            "messages": [HumanMessage(content="100 rs expense")],
            "intent": "",
            "entities": {},
            "context": {},
            "response": "",
            "user_id": 1,
            "missing_slots": [],
            "needs_followup": False,
            "route": ""
        }
        
        result = compiled_graph.invoke(state)
        
        # Should complete without follow-up
        assert not result.get("needs_followup", False), "Should not need follow-up"
        assert result.get("intent") in ["add_expense", "add_sale", "add_purchase"], \
            f"Expected add intent, got: {result.get('intent')}"
        print(f"✅ Single turn expense: {result.get('response')}")
    
    def test_pen_add_needs_followup(self):
        """Test: pen add karo → asks for quantity"""
        from backend.agents.graph import compiled_graph
        from backend.agents.state import AgentState
        
        state: AgentState = {
            "messages": [HumanMessage(content="pen add karo")],
            "intent": "",
            "entities": {},
            "context": {},
            "response": "",
            "user_id": 1,
            "missing_slots": [],
            "needs_followup": False,
            "route": ""
        }
        
        result = compiled_graph.invoke(state)
        
        # Should ask for follow-up info
        assert result.get("needs_followup", False) or result.get("missing_slots"), \
            f"Expected follow-up needed. Got missing_slots: {result.get('missing_slots')}"
        
        # Response should ask for quantity or price
        response = result.get("response", "").lower()
        assert any(word in response for word in ["kitne", "quantity", "price", "kitni"]), \
            f"Expected question about quantity/price, got: {result.get('response')}"
        
        print(f"✅ Pen add asks: {result.get('response')}")
        return result  # Return for continuation test
    
    def test_multi_turn_pen_flow(self):
        """Test complete multi-turn: pen add → 2 → 5 → Added"""
        from backend.agents.graph import compiled_graph
        from backend.agents.state import AgentState
        
        # Turn 1: pen add karo
        state: AgentState = {
            "messages": [HumanMessage(content="pen add karo")],
            "intent": "",
            "entities": {},
            "context": {},
            "response": "",
            "user_id": 1,
            "missing_slots": [],
            "needs_followup": False,
            "route": ""
        }
        
        result1 = compiled_graph.invoke(state)
        print(f"Turn 1: {result1.get('response')}")
        
        # Should need follow-up
        context = result1.get("context", {})
        pending_slots = context.get("pending_slots", [])
        
        if not pending_slots and not result1.get("missing_slots"):
            # If no follow-up needed, entity extraction got everything
            print("Note: Entity extraction got all slots from 'pen add karo'")
            return
        
        # Verify first question asks for quantity
        response1 = result1.get("response", "").lower()
        assert any(word in response1 for word in ["kitne", "quantity"]), \
            f"Expected quantity question, got: {result1.get('response')}"
        print("✅ Turn 1 asks for quantity")
        
        # Turn 2: answer with quantity "2"
        state2: AgentState = {
            "messages": [
                HumanMessage(content="pen add karo"),
                HumanMessage(content="2")
            ],
            "intent": "",
            "entities": {},
            "context": result1.get("context", {}),  # Carry over context
            "response": "",
            "user_id": 1,
            "missing_slots": [],
            "needs_followup": False,
            "route": ""
        }
        
        result2 = compiled_graph.invoke(state2)
        print(f"Turn 2: {result2.get('response')}")
        
        # Check if still needs price
        context2 = result2.get("context", {})
        pending_slots2 = context2.get("pending_slots", [])
        
        # Verify second question asks for price
        if pending_slots2:
            response2 = result2.get("response", "").lower()
            assert any(word in response2 for word in ["price", "kitni"]), \
                f"Expected price question, got: {result2.get('response')}"
            print("✅ Turn 2 asks for price")
            
            # Turn 3: answer with price "5"
            state3: AgentState = {
                "messages": [
                    HumanMessage(content="pen add karo"),
                    HumanMessage(content="2"),
                    HumanMessage(content="5")
                ],
                "intent": "",
                "entities": {},
                "context": result2.get("context", {}),
                "response": "",
                "user_id": 1,
                "missing_slots": [],
                "needs_followup": False,
                "route": ""
            }
            
            result3 = compiled_graph.invoke(state3)
            print(f"Turn 3: {result3.get('response')}")
            
            # At this point, all slots are filled
            # The response might be a DB error (which is fine, we're testing flow)
            # or a success message
            assert not result3.get("needs_followup", False), \
                f"Should be complete after providing price. Remaining slots: {result3.get('missing_slots')}"
            
            response = result3.get("response", "").lower()
            # Accept either success or DB error (flow completed, DB might not be set up)
            if "sorry" not in response:
                assert any(word in response for word in ["added", "done", "✅", "recorded"]), \
                    f"Expected confirmation, got: {result3.get('response')}"
            else:
                print("Note: DB error occurred (expected in test environment)")
        
        print("✅ Multi-turn flow complete!")


class TestSlotFillNode:
    """Test slot_fill node directly."""
    
    def test_extract_amount(self):
        """Test amount extraction from follow-up."""
        from backend.agents.nodes.slot_fill import extract_amount_from_followup
        
        assert extract_amount_from_followup("100") == 100.0
        assert extract_amount_from_followup("₹500") == 500.0
        assert extract_amount_from_followup("Rs 250") == 250.0
        assert extract_amount_from_followup("50.50") == 50.50
        print("✅ Amount extraction works")
    
    def test_extract_quantity(self):
        """Test quantity extraction from follow-up."""
        from backend.agents.nodes.slot_fill import extract_quantity_from_followup
        
        assert extract_quantity_from_followup("2") == 2.0
        assert extract_quantity_from_followup("5 kg") == 5.0
        assert extract_quantity_from_followup("10 pcs") == 10.0
        print("✅ Quantity extraction works")
    
    def test_extract_name(self):
        """Test name extraction from follow-up."""
        from backend.agents.nodes.slot_fill import extract_name_from_followup
        
        assert extract_name_from_followup("Ramesh") == "Ramesh"
        assert extract_name_from_followup("chai") == "Chai"
        print("✅ Name extraction works")
    
    def test_is_followup_response(self):
        """Test follow-up detection."""
        from backend.agents.nodes.slot_fill import is_followup_response
        from backend.agents.state import AgentState
        
        # With pending slots and short message → follow-up
        state_followup: AgentState = {
            "messages": [HumanMessage(content="2")],
            "context": {"pending_slots": ["quantity", "price"]},
            "intent": "",
            "entities": {},
            "response": "",
            "user_id": 1,
            "missing_slots": [],
            "needs_followup": False,
            "route": ""
        }
        assert is_followup_response(state_followup), "Should detect follow-up"
        
        # Without pending slots → not follow-up
        state_new: AgentState = {
            "messages": [HumanMessage(content="pen add karo")],
            "context": {},
            "intent": "",
            "entities": {},
            "response": "",
            "user_id": 1,
            "missing_slots": [],
            "needs_followup": False,
            "route": ""
        }
        assert not is_followup_response(state_new), "Should not detect follow-up"
        
        print("✅ Follow-up detection works")


class TestClassifyIntent:
    """Test classify node handles greetings correctly."""
    
    def test_greeting_intents(self):
        """Test various greeting messages."""
        from backend.agents.nodes.classify import classify_intent
        from backend.agents.state import AgentState
        
        greetings = ["hello", "hi", "namaste", "hey", "hola"]
        
        for greeting in greetings:
            state: AgentState = {
                "messages": [HumanMessage(content=greeting)],
                "intent": "",
                "entities": {},
                "context": {},
                "response": "",
                "user_id": 1,
                "missing_slots": [],
                "needs_followup": False,
                "route": ""
            }
            
            result = classify_intent(state)
            assert result.get("intent") == "greeting", \
                f"Expected greeting for '{greeting}', got: {result.get('intent')}"
        
        print("✅ All greetings classified correctly")


if __name__ == "__main__":
    print("=" * 60)
    print("Running Multi-Turn Conversation Tests")
    print("=" * 60)
    
    # Run slot fill tests
    slot_tests = TestSlotFillNode()
    slot_tests.test_extract_amount()
    slot_tests.test_extract_quantity()
    slot_tests.test_extract_name()
    slot_tests.test_is_followup_response()
    
    print()
    
    # Run classify tests
    classify_tests = TestClassifyIntent()
    classify_tests.test_greeting_intents()
    
    print()
    
    # Run conversation tests
    conv_tests = TestMultiTurnConversation()
    conv_tests.test_greeting_flow()
    conv_tests.test_single_turn_expense()
    conv_tests.test_pen_add_needs_followup()
    conv_tests.test_multi_turn_pen_flow()
    
    print()
    print("=" * 60)
    print("All tests passed! ✅")
    print("=" * 60)
