from kmtest import km_test_suite
import numpy as np

# Create test data
np.random.seed(42)
y = np.cumsum(np.random.normal(0.5, 1, 200)) + 100

# Run test
result = km_test_suite(y)

# Print results
print(result)
print(f"\nRecommendation: {result.recommendation}")