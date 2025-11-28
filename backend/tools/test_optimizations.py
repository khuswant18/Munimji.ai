#!/usr/bin/env python3
"""
Quick test script to verify rule-based optimizations work correctly.
Run this without external dependencies to verify the core logic.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

def test_classifier():
    """Test the rule-based classifier."""
    from backend.agents.nodes.classify import rule_based_classifier, EDGE_TESTS
    
    print("=" * 60)
    print("TESTING RULE-BASED CLASSIFIER")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test in EDGE_TESTS:
        text = test["text"]
        expected = test["expect"]
        
        intent, confidence = rule_based_classifier(text)
        
        # For "unknown" cases, None is also acceptable
        if expected == "unknown" and intent is None:
            status = "✅ PASS"
            passed += 1
        elif intent == expected:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1
        
        print(f"{status} '{text}' => {intent} (expected: {expected}) conf: {confidence:.2f}")
    
    print(f"\nResults: {passed}/{passed + failed} passed")
    return failed == 0


def test_entity_extraction():
    """Test rule-based entity extraction."""
    from backend.agents.nodes.extract import (
        extract_amount, 
        extract_quantity_and_unit, 
        extract_name,
        extract_expense_category
    )
    
    print("\n" + "=" * 60)
    print("TESTING ENTITY EXTRACTION")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    # Amount tests
    amount_tests = [
        ("₹500", 500),
        ("Rs 500", 500),
        ("500 rupees", 500),
        ("2500", 2500),
    ]
    
    for text, expected in amount_tests:
        result = extract_amount(text)
        if result == expected:
            print(f"✅ PASS amount '{text}' => {result}")
            passed += 1
        else:
            print(f"❌ FAIL amount '{text}' => {result} (expected {expected})")
            failed += 1
    
    # Quantity tests
    qty_tests = [
        ("10 kg", (10, "kg")),
        ("5 packets", (5, "packet")),  # Normalized to singular
    ]
    
    for text, expected in qty_tests:
        result = extract_quantity_and_unit(text)
        if result == expected:
            print(f"✅ PASS quantity '{text}' => {result}")
            passed += 1
        else:
            print(f"❌ FAIL quantity '{text}' => {result} (expected {expected})")
            failed += 1
    
    # Name tests
    name_tests = [
        ("Sold to Ramesh", "Ramesh"),
        ("from Mohan", "Mohan"),
    ]
    
    for text, expected in name_tests:
        result = extract_name(text)
        if result == expected:
            print(f"✅ PASS name '{text}' => {result}")
            passed += 1
        else:
            print(f"❌ FAIL name '{text}' => {result} (expected {expected})")
            failed += 1
    
    # Category tests
    cat_tests = [
        ("Petrol 500", "fuel"),
        ("Rent paid", "rent"),
    ]
    
    for text, expected in cat_tests:
        result = extract_expense_category(text)
        if result == expected:
            print(f"✅ PASS category '{text}' => {result}")
            passed += 1
        else:
            print(f"❌ FAIL category '{text}' => {result} (expected {expected})")
            failed += 1
    
    print(f"\nResults: {passed}/{passed + failed} passed")
    return failed == 0


def test_cache():
    """Test LLM cache."""
    from backend.llm.llm_cache import LRUCache
    
    print("\n" + "=" * 60)
    print("TESTING LLM CACHE")
    print("=" * 60)
    
    cache = LRUCache(max_size=5, ttl_seconds=60)
    
    # Test set/get
    cache.set("prompt1", "response1", "model")
    result = cache.get("prompt1", "model")
    
    if result == "response1":
        print("✅ PASS cache set/get")
    else:
        print(f"❌ FAIL cache set/get: got {result}")
        return False
    
    # Test miss
    result = cache.get("nonexistent", "model")
    if result is None:
        print("✅ PASS cache miss returns None")
    else:
        print(f"❌ FAIL cache miss: got {result}")
        return False
    
    # Test stats
    stats = cache.stats()
    if stats["hits"] >= 1 and stats["misses"] >= 1:
        print(f"✅ PASS cache stats: {stats}")
    else:
        print(f"❌ FAIL cache stats: {stats}")
        return False
    
    return True


def test_timers():
    """Test timing decorators."""
    from backend.decorators.timeit import time_node, get_timings, clear_timings
    import time
    
    print("\n" + "=" * 60)
    print("TESTING TIMING DECORATORS")
    print("=" * 60)
    
    clear_timings()
    
    @time_node
    def slow_func():
        time.sleep(0.05)
        return "done"
    
    result = slow_func()
    timings = get_timings()
    
    if result == "done" and "slow_func" in timings and timings["slow_func"] >= 0.05:
        print(f"✅ PASS time_node decorator: {timings}")
        return True
    else:
        print(f"❌ FAIL time_node decorator: result={result}, timings={timings}")
        return False


def main():
    """Run all tests."""
    results = []
    
    results.append(("Classifier", test_classifier()))
    results.append(("Entity Extraction", test_entity_extraction()))
    results.append(("Cache", test_cache()))
    results.append(("Timers", test_timers()))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
