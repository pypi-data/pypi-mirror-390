"""
Test cases for documented examples A, B, and C.
"""
import unittest
from math import sqrt, log

from bitads_v3_core.domain.models import MinerWindowStats, Percentiles
from bitads_v3_core.domain.math_ops import (
    base_score,
    final_score,
    normalize_revenue,
    normalize_sales,
    refund_rate,
)
from bitads_v3_core.app.scoring import ScoreCalculator
from tests.test_helpers import MockP95Provider


TOLERANCE = 1e-6


class TestExamples(unittest.TestCase):
    """Test cases from documentation examples."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Common P95 values for examples A and B
        self.p95_sales = 60.0
        self.p95_revenue = 4000.0
        self.percentiles = Percentiles(
            p95_sales=self.p95_sales,
            p95_revenue_usd=self.p95_revenue
        )
        self.p95_provider = MockP95Provider(self.percentiles)
        self.calculator = ScoreCalculator(self.p95_provider)
    
    def test_example_a(self):
        """
        Example A:
        Network: P95_sales=60, P95_rev=4000
        Miner: sales=48, rev=2300, refund_orders=6
        Expect score ≈ 0.802 (base ≈ 0.918, multiplier 0.875)
        """
        stats = MinerWindowStats(sales=48, revenue_usd=2300.0, refund_orders=6)
        result = self.calculator.score_one("miner_a", stats, "network")
        
        # Verify refund rate: 6/48 = 0.125
        expected_ref_rate = 6.0 / 48.0
        self.assertAlmostEqual(result.refund_multiplier, 1.0 - expected_ref_rate, delta=TOLERANCE)
        
        # Verify base score ≈ 0.918
        # sales_norm = sqrt(48) / sqrt(60) = sqrt(48/60) = sqrt(0.8) ≈ 0.8944
        # rev_norm = ln(1+2300) / ln(1+4000) ≈ ln(2301) / ln(4001) ≈ 7.740 / 8.294 ≈ 0.933
        # base = 0.40 * 0.8944 + 0.60 * 0.933 ≈ 0.3578 + 0.5598 ≈ 0.918
        self.assertAlmostEqual(result.base, 0.918, delta=0.01)
        
        # Verify final score ≈ 0.802
        # score = (1 - 0.125) * 0.918 = 0.875 * 0.918 ≈ 0.803
        self.assertAlmostEqual(result.score, 0.802, delta=0.01)
    
    def test_example_b(self):
        """
        Example B:
        Same P95s, Miner: sales=10, rev=3000, refund_orders=1
        Expect score ≈ 0.668 (base ≈ 0.742, multiplier 0.90)
        """
        stats = MinerWindowStats(sales=10, revenue_usd=3000.0, refund_orders=1)
        result = self.calculator.score_one("miner_b", stats, "network")
        
        # Verify refund rate: 1/10 = 0.10
        expected_ref_rate = 1.0 / 10.0
        self.assertAlmostEqual(result.refund_multiplier, 1.0 - expected_ref_rate, delta=TOLERANCE)
        
        # Verify base score ≈ 0.742
        # sales_norm = sqrt(10) / sqrt(60) = sqrt(10/60) = sqrt(0.1667) ≈ 0.408
        # rev_norm = ln(1+3000) / ln(1+4000) ≈ ln(3001) / ln(4001) ≈ 8.006 / 8.294 ≈ 0.965
        # base = 0.40 * 0.408 + 0.60 * 0.965 ≈ 0.163 + 0.579 ≈ 0.742
        self.assertAlmostEqual(result.base, 0.742, delta=0.01)
        
        # Verify final score ≈ 0.668
        # score = (1 - 0.10) * 0.742 = 0.90 * 0.742 ≈ 0.668
        self.assertAlmostEqual(result.score, 0.668, delta=0.01)
    
    def test_example_c(self):
        """
        Example C:
        sales=0, rev=0, refund_orders=0 → score = 0
        """
        stats = MinerWindowStats(sales=0, revenue_usd=0.0, refund_orders=0)
        result = self.calculator.score_one("miner_c", stats, "network")
        
        self.assertEqual(result.base, 0.0)
        self.assertEqual(result.refund_multiplier, 1.0)  # 1 - 0
        self.assertEqual(result.score, 0.0)
    
    def test_normalize_sales_calculation(self):
        """Test normalize_sales with example values."""
        # Example A: sales=48, p95_sales=60
        sales_norm = normalize_sales(48, 60)
        expected = sqrt(48) / sqrt(60)
        self.assertAlmostEqual(sales_norm, expected, delta=TOLERANCE)
        self.assertLessEqual(sales_norm, 1.0)
    
    def test_normalize_revenue_calculation(self):
        """Test normalize_revenue with example values."""
        # Example A: rev=2300, p95_rev=4000
        rev_norm = normalize_revenue(2300, 4000)
        expected = log(1 + 2300) / log(1 + 4000)
        self.assertAlmostEqual(rev_norm, expected, delta=TOLERANCE)
        self.assertLessEqual(rev_norm, 1.0)
    
    def test_base_score_calculation(self):
        """Test base_score with example values."""
        sales_norm = normalize_sales(48, 60)
        rev_norm = normalize_revenue(2300, 4000)
        base = base_score(sales_norm, rev_norm)
        expected = 0.40 * sales_norm + 0.60 * rev_norm
        self.assertAlmostEqual(base, expected, delta=TOLERANCE)


if __name__ == "__main__":
    unittest.main()


