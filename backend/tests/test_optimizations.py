"""
Tests for rule-based classifier and entity extraction.

These tests verify that the optimized rule-based paths work correctly
and handle edge cases without needing LLM fallback.
"""
import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestRuleBasedClassifier:
    """Tests for the rule-based intent classifier."""
    
    def test_expense_intents(self):
        """Test expense intent classification."""
        from backend.agents.nodes.classify import rule_based_classifier
        
        test_cases = [
            ("Fuel 200", "add_expense"),
            ("Petrol bharwaya 500", "add_expense"),
            ("Rent paid 5000", "add_expense"),
            ("Electricity bill 1200", "add_expense"),
            ("Salary 10000", "add_expense"),
            ("Chai 50", "add_expense"),
            ("Auto fare 100", "add_expense"),
        ]
        
        for text, expected_intent in test_cases:
            intent, confidence = rule_based_classifier(text)
            assert intent == expected_intent, f"Failed for '{text}': got {intent}, expected {expected_intent}"
            assert confidence >= 0.85, f"Low confidence for '{text}': {confidence}"
    
    def test_sale_intents(self):
        """Test sale intent classification."""
        from backend.agents.nodes.classify import rule_based_classifier
        
        test_cases = [
            ("Sold 10 packets to Ramesh", "add_sale"),
            ("Becha 5 kg rice 300", "add_sale"),
            ("Invoice to Mohan 1500", "add_sale"),
            ("Sale 500 to customer", "add_sale"),
        ]
        
        for text, expected_intent in test_cases:
            intent, confidence = rule_based_classifier(text)
            assert intent == expected_intent, f"Failed for '{text}': got {intent}, expected {expected_intent}"
    
    def test_purchase_intents(self):
        """Test purchase intent classification."""
        from backend.agents.nodes.classify import rule_based_classifier
        
        test_cases = [
            ("Bought stock 2000", "add_purchase"),
            ("Kharida 50 packets 500", "add_purchase"),
            ("Purchase from wholesale 3000", "add_purchase"),
            ("Stock inventory 5000", "add_purchase"),
        ]
        
        for text, expected_intent in test_cases:
            intent, confidence = rule_based_classifier(text)
            assert intent == expected_intent, f"Failed for '{text}': got {intent}, expected {expected_intent}"
    
    def test_udhaar_intents(self):
        """Test udhaar/credit intent classification."""
        from backend.agents.nodes.classify import rule_based_classifier
        
        test_cases = [
            ("Aman ko udhaar 500 diya", "add_udhaar"),
            ("Ramesh se udhar liya 1000", "add_udhaar"),
            ("Credit to Suresh 300", "add_udhaar"),
            ("Loan given 2000", "add_udhaar"),
        ]
        
        for text, expected_intent in test_cases:
            intent, confidence = rule_based_classifier(text)
            assert intent == expected_intent, f"Failed for '{text}': got {intent}, expected {expected_intent}"
    
    def test_payment_intents(self):
        """Test payment intent classification."""
        from backend.agents.nodes.classify import rule_based_classifier
        
        test_cases = [
            ("Received 500 from Ramesh", "add_payment"),
            ("Paid back 200", "add_payment"),
            ("Payment received 1000", "add_payment"),
            ("Mila 300 Mohan se", "add_payment"),
        ]
        
        for text, expected_intent in test_cases:
            intent, confidence = rule_based_classifier(text)
            assert intent == expected_intent, f"Failed for '{text}': got {intent}, expected {expected_intent}"
    
    def test_query_intents(self):
        """Test query intent classification."""
        from backend.agents.nodes.classify import rule_based_classifier
        
        test_cases = [
            ("Show today's summary", "query_summary"),
            ("Show ledger", "query_ledger"),
            ("Who owes me?", "query_udhaar"),
            ("Total profit", "query_summary"),
        ]
        
        for text, expected_intent in test_cases:
            intent, confidence = rule_based_classifier(text)
            assert intent == expected_intent, f"Failed for '{text}': got {intent}, expected {expected_intent}"
    
    def test_greeting_intents(self):
        """Test greeting intent classification."""
        from backend.agents.nodes.classify import rule_based_classifier
        
        test_cases = [
            ("Hi", "greeting"),
            ("Hello", "greeting"),
            ("Namaste", "greeting"),
            ("Good morning", "greeting"),
        ]
        
        for text, expected_intent in test_cases:
            intent, confidence = rule_based_classifier(text)
            assert intent == expected_intent, f"Failed for '{text}': got {intent}, expected {expected_intent}"
    
    def test_unknown_returns_none(self):
        """Test that ambiguous text returns None or low confidence."""
        from backend.agents.nodes.classify import rule_based_classifier
        
        test_cases = [
            "xyz abc 123",
            "random text here",
            "just some words",
        ]
        
        for text in test_cases:
            intent, confidence = rule_based_classifier(text)
            # Should either be None or have low confidence
            if intent is not None:
                assert confidence < 0.85, f"High confidence for ambiguous '{text}'"


class TestEntityExtraction:
    """Tests for rule-based entity extraction."""
    
    def test_amount_extraction(self):
        """Test amount extraction from various formats."""
        from backend.agents.nodes.extract import extract_amount
        
        test_cases = [
            ("₹500", 500),
            ("Rs 500", 500),
            ("Rs.500", 500),
            ("500 rupees", 500),
            ("500rs", 500),
            ("1000 ka", 1000),
            ("2500", 2500),
            ("₹1,500", 1500),
        ]
        
        for text, expected in test_cases:
            result = extract_amount(text)
            assert result == expected, f"Failed for '{text}': got {result}, expected {expected}"
    
    def test_quantity_extraction(self):
        """Test quantity and unit extraction."""
        from backend.agents.nodes.extract import extract_quantity_and_unit
        
        test_cases = [
            ("10 kg", (10, "kg")),
            ("5 packets", (5, "packets")),
            ("2 dozen", (2, "dozen")),
            ("100 bottles", (100, "bottles")),
        ]
        
        for text, expected in test_cases:
            result = extract_quantity_and_unit(text)
            assert result == expected, f"Failed for '{text}': got {result}, expected {expected}"
    
    def test_name_extraction(self):
        """Test customer/supplier name extraction."""
        from backend.agents.nodes.extract import extract_name
        
        test_cases = [
            ("Sold to Ramesh", "Ramesh"),
            ("from Mohan", "Mohan"),
            ("Suresh ko diya", "Suresh"),
            ("customer Amit", "Amit"),
        ]
        
        for text, expected in test_cases:
            result = extract_name(text)
            assert result == expected, f"Failed for '{text}': got {result}, expected {expected}"
    
    def test_expense_category(self):
        """Test expense category detection."""
        from backend.agents.nodes.extract import extract_expense_category
        
        test_cases = [
            ("Petrol 500", "fuel"),
            ("Rent paid", "rent"),
            ("Salary 10000", "salary"),
            ("Auto fare", "transport"),
            ("Lunch 200", "food"),
        ]
        
        for text, expected in test_cases:
            result = extract_expense_category(text)
            assert result == expected, f"Failed for '{text}': got {result}, expected {expected}"


class TestLLMCache:
    """Tests for LLM response caching."""
    
    def test_cache_set_get(self):
        """Test basic cache operations."""
        from backend.llm.llm_cache import LRUCache
        
        cache = LRUCache(max_size=10, ttl_seconds=60)
        
        # Test set and get
        cache.set("test prompt", "test response", "test-model")
        result = cache.get("test prompt", "test-model")
        assert result == "test response"
    
    def test_cache_miss(self):
        """Test cache miss returns None."""
        from backend.llm.llm_cache import LRUCache
        
        cache = LRUCache(max_size=10, ttl_seconds=60)
        result = cache.get("nonexistent prompt", "model")
        assert result is None
    
    def test_cache_lru_eviction(self):
        """Test LRU eviction when cache is full."""
        from backend.llm.llm_cache import LRUCache
        
        cache = LRUCache(max_size=3, ttl_seconds=60)
        
        # Fill cache
        cache.set("prompt1", "response1", "model")
        cache.set("prompt2", "response2", "model")
        cache.set("prompt3", "response3", "model")
        
        # Access prompt1 to make it recent
        cache.get("prompt1", "model")
        
        # Add new item, should evict prompt2 (least recently used)
        cache.set("prompt4", "response4", "model")
        
        assert cache.get("prompt1", "model") == "response1"
        assert cache.get("prompt2", "model") is None  # Should be evicted
        assert cache.get("prompt3", "model") == "response3"
        assert cache.get("prompt4", "model") == "response4"
    
    def test_cache_stats(self):
        """Test cache statistics."""
        from backend.llm.llm_cache import LRUCache
        
        cache = LRUCache(max_size=10, ttl_seconds=60)
        
        cache.set("prompt1", "response1", "model")
        cache.get("prompt1", "model")  # Hit
        cache.get("nonexistent", "model")  # Miss
        
        stats = cache.stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["size"] == 1


class TestTimingDecorators:
    """Tests for timing decorators."""
    
    def test_time_node_decorator(self):
        """Test that time_node decorator captures timing."""
        from backend.decorators.timeit import time_node, get_timings, clear_timings
        import time
        
        clear_timings()
        
        @time_node
        def slow_function():
            time.sleep(0.1)
            return "result"
        
        result = slow_function()
        assert result == "result"
        
        timings = get_timings()
        assert "slow_function" in timings
        assert timings["slow_function"] >= 0.1
    
    def test_timed_context(self):
        """Test timed_context context manager."""
        from backend.decorators.timeit import timed_context, get_timings, clear_timings
        import time
        
        clear_timings()
        
        with timed_context("test_block"):
            time.sleep(0.05)
        
        timings = get_timings()
        assert "test_block" in timings
        assert timings["test_block"] >= 0.05


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
