"""
Scoring service for computing miner scores.

Pure application layer logic with no side effects.
"""
from typing import List, Tuple

from ..domain.math_ops import (
    apply_early_sales_soft_cap,
    base_score,
    final_score,
    normalize_revenue,
    normalize_sales,
    refund_rate,
)
from ..domain.models import MinerWindowStats, ScoreResult
from .ports import IP95Provider


class ScoreCalculator:
    """
    Calculator for miner scores.
    
    Pure service with no side effects. All computation is deterministic.
    """
    
    def __init__(
        self,
        p95_provider: IP95Provider,
        use_soft_cap: bool = False,
        use_flooring: bool = False
    ):
        """
        Initialize the score calculator.
        
        Args:
            p95_provider: Provider for P95 percentiles
            use_soft_cap: Whether to apply early-sales soft cap (default False)
            use_flooring: Whether to use normalization floors in auto mode (default False)
        """
        self.p95_provider = p95_provider
        self.use_soft_cap = use_soft_cap
        self.use_flooring = use_flooring
    
    def score_one(self, miner_id: str, stats: MinerWindowStats, scope: str) -> ScoreResult:
        """
        Compute score for a single miner.
        
        Algorithm:
        1. Compute refund rate
        2. If sales == 0, return zero score
        3. Get P95 percentiles for scope
        4. Normalize sales and revenue
        5. Compute base score
        6. Apply refund multiplier to get final score
        7. Optionally apply early-sales soft cap
        
        Args:
            miner_id: Opaque miner identifier
            stats: Miner window statistics
            scope: Opaque scope identifier
        
        Returns:
            ScoreResult with base, refund_multiplier, and final score
        """
        # Compute refund rate
        ref = refund_rate(stats)
        
        # Early return for zero sales
        if stats.sales == 0:
            return ScoreResult(
                miner_id=miner_id,
                base=0.0,
                refund_multiplier=(1.0 - ref),
                score=0.0
            )
        
        # Get P95 percentiles for scope
        p = self.p95_provider.get_effective_p95(scope)
        
        # Normalize sales and revenue
        sales_norm = normalize_sales(stats.sales, p.p95_sales)
        rev_norm = normalize_revenue(stats.revenue_usd, p.p95_revenue_usd)
        
        # Compute base score
        base = base_score(sales_norm, rev_norm)
        
        # Compute final score with refund multiplier
        score = final_score(base, ref)
        
        # Apply early-sales soft cap if enabled
        if self.use_soft_cap:
            score = apply_early_sales_soft_cap(score, stats.sales)
        
        return ScoreResult(
            miner_id=miner_id,
            base=base,
            refund_multiplier=(1.0 - ref),
            score=score
        )
        
    def score_many(
        self,
        entries: List[Tuple[str, MinerWindowStats]],
        scope: str
    ) -> List[ScoreResult]:
        """
        Compute scores for multiple miners.
        
        Args:
            entries: List of (miner_id, MinerWindowStats) tuples
            scope: Opaque scope identifier
        
        Returns:
            List of ScoreResult objects
        """
        return [self.score_one(miner_id, stats, scope) for miner_id, stats in entries]


