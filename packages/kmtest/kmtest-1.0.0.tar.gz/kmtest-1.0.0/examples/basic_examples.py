"""
Basic examples of using kmtest package
"""

import numpy as np
from kmtest import km_test_suite, km_v1_test, km_v2_test

def example1_linear_process():
    """Example 1: Linear integrated process with drift"""
    print("\n" + "="*60)
    print("Example 1: Linear Integrated Process with Drift")
    print("="*60)
    
    # Simulate data
    np.random.seed(123)
    n = 200
    y = np.cumsum(np.random.normal(0.5, 1, n)) + 100
    
    # Run test suite
    result = km_test_suite(y, verbose=True)
    print(result)
    
    return result


def example2_logarithmic_process():
    """Example 2: Logarithmic integrated process with drift"""
    print("\n" + "="*60)
    print("Example 2: Logarithmic Integrated Process with Drift")
    print("="*60)
    
    # Simulate data
    np.random.seed(456)
    n = 200
    log_y = np.cumsum(np.random.normal(0.01, 0.05, n)) + np.log(100)
    y = np.exp(log_y)
    
    # Run test suite
    result = km_test_suite(y, verbose=True)
    print(result)
    
    return result


def example3_individual_tests():
    """Example 3: Running individual tests"""
    print("\n" + "="*60)
    print("Example 3: Individual Tests")
    print("="*60)
    
    # Simulate linear process
    np.random.seed(789)
    n = 200
    y = np.cumsum(np.random.normal(0.5, 1, n)) + 100
    
    print("\nRunning V1 test (Linear null vs Log alternative):")
    v1_result = km_v1_test(y)
    print(v1_result)
    
    print("\n" + "-"*60)
    print("\nRunning V2 test (Log null vs Linear alternative):")
    v2_result = km_v2_test(y)
    print(v2_result)
    
    return v1_result, v2_result


def example4_no_drift():
    """Example 4: Process without drift"""
    print("\n" + "="*60)
    print("Example 4: Random Walk Without Drift")
    print("="*60)
    
    # Simulate random walk
    np.random.seed(321)
    n = 200
    y = np.cumsum(np.random.normal(0, 1, n)) + 100
    
    # Run test suite (will automatically use U tests)
    result = km_test_suite(y, verbose=True)
    print(result)
    
    return result


def example5_comparison():
    """Example 5: Comparing multiple series"""
    print("\n" + "="*60)
    print("Example 5: Comparing Linear vs Logarithmic Series")
    print("="*60)
    
    np.random.seed(111)
    n = 200
    
    # Linear process
    y_linear = np.cumsum(np.random.normal(0.5, 1, n)) + 100
    
    # Logarithmic process
    log_y = np.cumsum(np.random.normal(0.01, 0.05, n)) + np.log(100)
    y_log = np.exp(log_y)
    
    print("\nTesting Linear Process:")
    print("-" * 40)
    result_linear = km_test_suite(y_linear, verbose=False)
    print(f"Recommendation: {result_linear.recommendation}")
    
    print("\nTesting Logarithmic Process:")
    print("-" * 40)
    result_log = km_test_suite(y_log, verbose=False)
    print(f"Recommendation: {result_log.recommendation}")
    
    return result_linear, result_log


if __name__ == "__main__":
    print("\n" + "="*60)
    print("kmtest Package Examples")
    print("="*60)
    
    # Run all examples
    example1_linear_process()
    example2_logarithmic_process()
    example3_individual_tests()
    example4_no_drift()
    example5_comparison()
    
    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60)
