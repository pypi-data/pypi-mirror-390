"""
Prometheus metrics for NeuroBUS observability.

Tracks key performance and operational metrics.
"""

import logging
from collections import defaultdict
from typing import Any

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Metrics collector for NeuroBUS.

    Tracks:
    - Event counts (published, dispatched)
    - Latency histograms
    - Handler durations
    - Queue depths
    - Subscription counts
    - Error rates

    Note: This is a simplified metrics collector. For production,
    integrate with prometheus_client library.

    Example:
        >>> metrics = MetricsCollector()
        >>>
        >>> # Record event published
        >>> metrics.record_event_published("user.login")
        >>>
        >>> # Record latency
        >>> start = time.time()
        >>> # ... do work ...
        >>> metrics.record_latency("dispatch", time.time() - start)
    """

    def __init__(self):
        """Initialize metrics collector."""
        self._counters = defaultdict(int)
        self._histograms = defaultdict(list)
        self._gauges = defaultdict(float)

        logger.info("MetricsCollector initialized")

    def record_event_published(self, topic: str) -> None:
        """
        Record event published.

        Args:
            topic: Event topic
        """
        self._counters["events_published_total"] += 1
        self._counters[f"events_published_topic_{topic}"] += 1

    def record_event_dispatched(self, topic: str) -> None:
        """
        Record event dispatched to handler.

        Args:
            topic: Event topic
        """
        self._counters["events_dispatched_total"] += 1
        self._counters[f"events_dispatched_topic_{topic}"] += 1

    def record_latency(self, operation: str, duration_seconds: float) -> None:
        """
        Record operation latency.

        Args:
            operation: Operation name (e.g., "dispatch", "semantic_match")
            duration_seconds: Duration in seconds
        """
        metric_name = f"{operation}_latency_seconds"
        self._histograms[metric_name].append(duration_seconds)

    def record_handler_duration(self, handler_name: str, duration_seconds: float) -> None:
        """
        Record handler execution duration.

        Args:
            handler_name: Handler function name
            duration_seconds: Duration in seconds
        """
        metric_name = f"handler_duration_seconds_{handler_name}"
        self._histograms[metric_name].append(duration_seconds)

    def set_queue_depth(self, depth: int) -> None:
        """
        Set current queue depth gauge.

        Args:
            depth: Queue depth
        """
        self._gauges["queue_depth"] = float(depth)

    def set_subscriptions_active(self, count: int) -> None:
        """
        Set active subscriptions gauge.

        Args:
            count: Number of active subscriptions
        """
        self._gauges["subscriptions_active"] = float(count)

    def record_semantic_match(self, similarity: float) -> None:
        """
        Record semantic match.

        Args:
            similarity: Similarity score
        """
        self._counters["semantic_matches_total"] += 1
        self._histograms["semantic_similarity"].append(similarity)

    def record_cache_hit(self) -> None:
        """Record cache hit."""
        self._counters["cache_hits_total"] += 1

    def record_cache_miss(self) -> None:
        """Record cache miss."""
        self._counters["cache_misses_total"] += 1

    def record_error(self, error_type: str) -> None:
        """
        Record error.

        Args:
            error_type: Type of error
        """
        self._counters["errors_total"] += 1
        self._counters[f"errors_{error_type}"] += 1

    def get_counter(self, name: str) -> int:
        """Get counter value."""
        return self._counters.get(name, 0)

    def get_histogram_stats(self, name: str) -> dict[str, float]:
        """
        Get histogram statistics.

        Returns:
            Dict with min, max, mean, p50, p95, p99
        """
        values = self._histograms.get(name, [])

        if not values:
            return {
                "count": 0,
                "min": 0.0,
                "max": 0.0,
                "mean": 0.0,
                "p50": 0.0,
                "p95": 0.0,
                "p99": 0.0,
            }

        sorted_values = sorted(values)
        count = len(sorted_values)

        return {
            "count": count,
            "min": sorted_values[0],
            "max": sorted_values[-1],
            "mean": sum(sorted_values) / count,
            "p50": sorted_values[int(count * 0.50)],
            "p95": sorted_values[int(count * 0.95)] if count > 1 else sorted_values[-1],
            "p99": sorted_values[int(count * 0.99)] if count > 1 else sorted_values[-1],
        }

    def get_gauge(self, name: str) -> float:
        """Get gauge value."""
        return self._gauges.get(name, 0.0)

    def get_all_metrics(self) -> dict[str, Any]:
        """
        Get all metrics.

        Returns:
            Dictionary with all counters, histograms, and gauges
        """
        metrics = {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histograms": {},
        }

        for name in self._histograms:
            metrics["histograms"][name] = self.get_histogram_stats(name)

        return metrics

    def reset(self) -> None:
        """Reset all metrics."""
        self._counters.clear()
        self._histograms.clear()
        self._gauges.clear()
        logger.info("Metrics reset")


# Global metrics instance
_metrics = MetricsCollector()


def get_metrics() -> MetricsCollector:
    """Get global metrics collector instance."""
    return _metrics
