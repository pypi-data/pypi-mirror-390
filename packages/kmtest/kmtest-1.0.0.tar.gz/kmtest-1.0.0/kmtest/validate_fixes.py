#!/usr/bin/env python3
"""
Validation script for kmtest package fixes

This script performs comprehensive checks to verify that all numpy boolean
type issues have been properly fixed in the kmtest package.

Usage:
    python validate_fixes.py
"""

import sys
import numpy as np


def test_type_conversions():
    """Test that our type conversion approach works correctly"""
    print("Testing type conversion approach...")
    
    # Test numpy boolean conversion
    np_bool = np.array([1, 2]) > 1
    py_bool = bool(np_bool)
    
    assert isinstance(py_bool, bool), "bool() conversion failed"
    assert not isinstance(np_bool, bool), "numpy bool detected"
    
    # Test with different comparison operations
    tests = [
        np.array([1.0]) < 0.5,
        np.array([True]),
        np.True_,
        np.bool_(True)
    ]
    
    for test_val in tests:
        converted = bool(test_val)
        assert isinstance(converted, bool), f"Failed to convert {type(test_val)}"
    
    print("✓ Type conversion tests passed")


def test_kmtest_imports():
    """Test that kmtest package can be imported"""
    print("\nTesting kmtest imports...")
    
    try:
        from kmtest import km_v1_test, km_v2_test, km_u1_test, km_u2_test
        from kmtest import km_test_suite
        from kmtest.helpers import detect_drift
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_detect_drift_return_type():
    """Test that detect_drift returns proper Python bool"""
    print("\nTesting detect_drift return type...")
    
    from kmtest.helpers import detect_drift
    
    # Create test data with drift
    np.random.seed(123)
    y_drift = np.cumsum(np.random.normal(0.5, 1, 100)) + 100
    
    result = detect_drift(y_drift)
    
    assert isinstance(result, bool), f"Expected bool, got {type(result)}"
    assert result is True or result is False, "Result is not a proper boolean"
    
    print(f"✓ detect_drift returns: {type(result).__name__} (correct)")


def test_v1_return_type():
    """Test that V1 test returns proper Python bool for reject_null"""
    print("\nTesting V1 test return type...")
    
    from kmtest import km_v1_test
    
    np.random.seed(123)
    y = np.cumsum(np.random.normal(0.5, 1, 100)) + 100
    
    result = km_v1_test(y)
    
    assert isinstance(result.reject_null, bool), \
        f"Expected bool, got {type(result.reject_null)}"
    assert result.reject_null is True or result.reject_null is False, \
        "reject_null is not a proper boolean"
    
    print(f"✓ V1 test reject_null type: {type(result.reject_null).__name__} (correct)")


def test_v2_return_type():
    """Test that V2 test returns proper Python bool for reject_null"""
    print("\nTesting V2 test return type...")
    
    from kmtest import km_v2_test
    
    np.random.seed(456)
    log_y = np.cumsum(np.random.normal(0.01, 0.05, 100)) + np.log(100)
    y = np.exp(log_y)
    
    result = km_v2_test(y)
    
    assert isinstance(result.reject_null, bool), \
        f"Expected bool, got {type(result.reject_null)}"
    assert result.reject_null is True or result.reject_null is False, \
        "reject_null is not a proper boolean"
    
    print(f"✓ V2 test reject_null type: {type(result.reject_null).__name__} (correct)")


def test_u1_return_type():
    """Test that U1 test returns proper Python bools in reject_dict"""
    print("\nTesting U1 test return type...")
    
    from kmtest import km_u1_test
    
    np.random.seed(123)
    y = np.cumsum(np.random.normal(0, 1, 100)) + 100
    
    result = km_u1_test(y)
    
    for level, reject_val in result.reject_null.items():
        assert isinstance(reject_val, bool), \
            f"Expected bool for {level}, got {type(reject_val)}"
        assert reject_val is True or reject_val is False, \
            f"reject_null[{level}] is not a proper boolean"
    
    print(f"✓ U1 test reject_dict values: all {type(True).__name__} (correct)")


def test_u2_return_type():
    """Test that U2 test returns proper Python bools in reject_dict"""
    print("\nTesting U2 test return type...")
    
    from kmtest import km_u2_test
    
    np.random.seed(123)
    log_y = np.cumsum(np.random.normal(0, 0.05, 100)) + np.log(100)
    y = np.exp(log_y)
    
    result = km_u2_test(y)
    
    for level, reject_val in result.reject_null.items():
        assert isinstance(reject_val, bool), \
            f"Expected bool for {level}, got {type(reject_val)}"
        assert reject_val is True or reject_val is False, \
            f"reject_null[{level}] is not a proper boolean"
    
    print(f"✓ U2 test reject_dict values: all {type(True).__name__} (correct)")


def test_suite_return_type():
    """Test that test suite returns proper Python bool for has_drift"""
    print("\nTesting test suite return type...")
    
    from kmtest import km_test_suite
    
    np.random.seed(123)
    y = np.cumsum(np.random.normal(0.5, 1, 100)) + 100
    
    result = km_test_suite(y, verbose=False)
    
    assert isinstance(result.has_drift, bool), \
        f"Expected bool, got {type(result.has_drift)}"
    assert result.has_drift is True or result.has_drift is False, \
        "has_drift is not a proper boolean"
    
    print(f"✓ Test suite has_drift type: {type(result.has_drift).__name__} (correct)")


def test_suite_with_forced_drift():
    """Test that test suite properly handles user-provided has_drift parameter"""
    print("\nTesting test suite with forced drift parameter...")
    
    from kmtest import km_test_suite
    
    np.random.seed(123)
    y = np.cumsum(np.random.normal(0.5, 1, 100)) + 100
    
    # Test with explicit has_drift=True
    result1 = km_test_suite(y, has_drift=True, verbose=False)
    assert isinstance(result1.has_drift, bool), \
        f"Expected bool, got {type(result1.has_drift)}"
    
    # Test with explicit has_drift=False
    result2 = km_test_suite(y, has_drift=False, verbose=False)
    assert isinstance(result2.has_drift, bool), \
        f"Expected bool, got {type(result2.has_drift)}"
    
    # Test with numpy boolean (edge case)
    result3 = km_test_suite(y, has_drift=np.bool_(True), verbose=False)
    assert isinstance(result3.has_drift, bool), \
        f"Expected bool after numpy bool input, got {type(result3.has_drift)}"
    
    print("✓ Test suite properly handles forced drift parameter")


def run_all_tests():
    """Run all validation tests"""
    print("="*70)
    print("kmtest Package - Type Validation Tests")
    print("="*70)
    
    tests = [
        ("Type Conversions", test_type_conversions),
        ("Package Imports", test_kmtest_imports),
        ("detect_drift", test_detect_drift_return_type),
        ("V1 Test", test_v1_return_type),
        ("V2 Test", test_v2_return_type),
        ("U1 Test", test_u1_return_type),
        ("U2 Test", test_u2_return_type),
        ("Test Suite", test_suite_return_type),
        ("Forced Drift", test_suite_with_forced_drift),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            result = test_func()
            if result is False:
                failed += 1
                continue
            passed += 1
        except Exception as e:
            print(f"\n✗ {name} test failed with error:")
            print(f"  {type(e).__name__}: {e}")
            failed += 1
    
    print("\n" + "="*70)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*70)
    
    if failed == 0:
        print("\n✓ All validation tests passed! Your fixes are working correctly.")
        return 0
    else:
        print(f"\n✗ {failed} validation test(s) failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
