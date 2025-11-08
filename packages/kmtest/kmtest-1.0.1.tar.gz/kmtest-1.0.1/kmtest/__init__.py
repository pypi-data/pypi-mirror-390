"""
kmtest: Kobayashi-McAleer Tests for Linear and Logarithmic Transformations

This package implements the Kobayashi-McAleer (1999) tests for choosing between
linear and logarithmic transformations of integrated processes.

Main Functions:
    km_v1_test: Test linear (with drift) vs logarithmic process
    km_v2_test: Test logarithmic (with drift) vs linear process
    km_u1_test: Test linear (no drift) vs logarithmic process
    km_u2_test: Test logarithmic (no drift) vs linear process
    km_test_suite: Run appropriate tests and provide interpretation

Author: Dr. Merwan Roudane (merwanroudane920@gmail.com)
Based on: Kobayashi, M. and McAleer, M. (1999). Tests of Linear and Logarithmic
          Transformations for Integrated Processes. Journal of the American
          Statistical Association, 94(447), 860-868.
"""

__version__ = "1.0.0"
__author__ = "Dr. Merwan Roudane"
__email__ = "merwanroudane920@gmail.com"

from .km_tests import km_v1_test, km_v2_test, km_u1_test, km_u2_test
from .test_suite import km_test_suite
from .results import KMTestResult, KMTestSuiteResult

__all__ = [
    'km_v1_test',
    'km_v2_test', 
    'km_u1_test',
    'km_u2_test',
    'km_test_suite',
    'KMTestResult',
    'KMTestSuiteResult'
]
