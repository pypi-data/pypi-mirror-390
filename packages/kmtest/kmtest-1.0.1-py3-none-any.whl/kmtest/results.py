"""
Result classes for Kobayashi-McAleer tests
"""

from dataclasses import dataclass
from typing import Dict, Optional, Union
import numpy as np


@dataclass
class KMTestResult:
    """
    Result from a single Kobayashi-McAleer test.
    
    Attributes:
        statistic: The test statistic value
        p_value: P-value (for V tests with drift) or None
        critical_values: Dictionary of critical values (for U tests) or None
        reject_null: Boolean or dict indicating rejection at various significance levels
        null_hypothesis: Description of the null hypothesis
        alternative: Description of the alternative hypothesis
        lag_order: Selected lag order
        drift_estimate: Estimated drift parameter
        variance_estimate: Estimated innovation variance
        test_type: Type of test ('V1', 'V2', 'U1', 'U2')
    """
    statistic: float
    p_value: Optional[float]
    critical_values: Optional[Dict[str, float]]
    reject_null: Union[bool, Dict[str, bool]]
    null_hypothesis: str
    alternative: str
    lag_order: int
    drift_estimate: Optional[float]
    variance_estimate: float
    test_type: str
    
    def __str__(self) -> str:
        """String representation of test results"""
        lines = [
            f"\nKobayashi-McAleer {self.test_type} Test",
            "=" * 50,
            f"Null Hypothesis: {self.null_hypothesis}",
            f"Alternative: {self.alternative}",
            f"\nTest Statistic: {self.statistic:.4f}",
        ]
        
        if self.p_value is not None:
            lines.append(f"P-value: {self.p_value:.4f}")
            lines.append(f"Reject null (α=0.05): {'Yes' if self.reject_null else 'No'}")
        else:
            lines.append("\nCritical Values:")
            if self.critical_values:
                for level, cv in self.critical_values.items():
                    reject_text = "Yes" if self.reject_null.get(level, False) else "No"
                    lines.append(f"  {level}: {cv:.3f} (Reject: {reject_text})")
        
        lines.extend([
            f"\nLag Order: {self.lag_order}",
            f"Variance Estimate: {self.variance_estimate:.6f}"
        ])
        
        if self.drift_estimate is not None:
            lines.append(f"Drift Estimate: {self.drift_estimate:.6f}")
        
        return "\n".join(lines)
    
    def summary(self) -> Dict:
        """Return summary as dictionary"""
        return {
            'test_type': self.test_type,
            'statistic': self.statistic,
            'p_value': self.p_value,
            'critical_values': self.critical_values,
            'reject_null': self.reject_null,
            'lag_order': self.lag_order,
            'null_hypothesis': self.null_hypothesis,
            'alternative': self.alternative
        }


@dataclass
class KMTestSuiteResult:
    """
    Result from running the full test suite.
    
    Attributes:
        recommendation: "LEVELS" or "LOGARITHMS"
        test1_result: First test result (V1 or U1)
        test2_result: Second test result (V2 or U2)
        has_drift: Whether drift was detected
        interpretation: Detailed interpretation text
    """
    recommendation: str
    test1_result: KMTestResult
    test2_result: KMTestResult
    has_drift: bool
    interpretation: str
    
    def __str__(self) -> str:
        """String representation of suite results"""
        lines = [
            "\n" + "=" * 60,
            "Kobayashi-McAleer Test Suite Results",
            "=" * 60,
            f"\n{'WITH' if self.has_drift else 'WITHOUT'} DRIFT DETECTED\n",
            f"RECOMMENDATION: Model data in {self.recommendation}",
            "\n" + "-" * 60,
            "\nTest 1 (Linear vs Logarithmic):",
            str(self.test1_result),
            "\n" + "-" * 60,
            "\nTest 2 (Logarithmic vs Linear):",
            str(self.test2_result),
            "\n" + "=" * 60,
            "\nInterpretation:",
            self.interpretation,
            "=" * 60
        ]
        return "\n".join(lines)
    
    def summary(self) -> Dict:
        """Return summary as dictionary"""
        return {
            'recommendation': self.recommendation,
            'has_drift': self.has_drift,
            'interpretation': self.interpretation,
            'test1': self.test1_result.summary(),
            'test2': self.test2_result.summary()
        }
