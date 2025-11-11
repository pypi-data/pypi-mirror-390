"""
Enhanced Evaluation Framework for AutoTrain Advanced
=====================================================

Provides comprehensive evaluation capabilities for model training.
"""

from .evaluator import (
    Evaluator,
    EvaluationConfig,
    EvaluationResult,
    MetricType,
    evaluate_model,
    evaluate_generation,
)

from .metrics import (
    Metric,
    PerplexityMetric,
    BLEUMetric,
    ROUGEMetric,
    BERTScoreMetric,
    AccuracyMetric,
    F1Metric,
    ExactMatchMetric,
    METEORMetric,
    CustomMetric,
    MetricCollection,
)

from .callbacks import (
    EvaluationCallback,
    PeriodicEvalCallback,
    BestModelCallback,
    EarlyStoppingCallback,
    MetricsLoggerCallback,
)

from .benchmark import (
    Benchmark,
    BenchmarkConfig,
    BenchmarkResult,
    run_benchmark,
    compare_models,
)

__all__ = [
    # Core evaluator
    "Evaluator",
    "EvaluationConfig",
    "EvaluationResult",
    "MetricType",
    "evaluate_model",
    "evaluate_generation",
    # Metrics
    "Metric",
    "PerplexityMetric",
    "BLEUMetric",
    "ROUGEMetric",
    "BERTScoreMetric",
    "AccuracyMetric",
    "F1Metric",
    "ExactMatchMetric",
    "METEORMetric",
    "CustomMetric",
    "MetricCollection",
    # Callbacks
    "EvaluationCallback",
    "PeriodicEvalCallback",
    "BestModelCallback",
    "EarlyStoppingCallback",
    "MetricsLoggerCallback",
    # Benchmarking
    "Benchmark",
    "BenchmarkConfig",
    "BenchmarkResult",
    "run_benchmark",
    "compare_models",
]