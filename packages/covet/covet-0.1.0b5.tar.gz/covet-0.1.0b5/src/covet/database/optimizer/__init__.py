"""
Database Query Optimizer Module

Enterprise-grade query optimization with:
- Query plan analysis
- Index recommendations
- Query rewriting
- Performance tracking

Example:
    from covet.database.optimizer import QueryOptimizer

    optimizer = QueryOptimizer(adapter)
    plan = await optimizer.analyze_query(query, params)
    recommendations = optimizer.recommend_indexes(plan)
"""

from .query_optimizer import IndexRecommendation, OptimizationSuggestion, QueryOptimizer, QueryPlan

__all__ = ["QueryOptimizer", "QueryPlan", "IndexRecommendation", "OptimizationSuggestion"]
