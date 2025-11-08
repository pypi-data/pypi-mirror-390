"""
Connection health monitoring utilities for WebSocket connections.
"""

import time
from enum import Enum
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field


class NetworkQuality(Enum):
    """Network quality assessment levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class ConnectionMetrics:
    """
    Metrics for tracking connection health and performance.
    
    Attributes:
        connected_since: Timestamp when connection was established
        last_ping_time: Timestamp of last ping sent
        last_pong_time: Timestamp of last pong received
        messages_sent: Count of messages sent
        messages_received: Count of messages received
        errors_count: Count of errors encountered
        reconnection_count: Number of reconnection attempts
        avg_latency: Average ping-pong latency in seconds
        latency_samples: Recent latency measurements
        uptime: Total connection uptime in seconds
    """
    connected_since: Optional[float] = None
    last_ping_time: Optional[float] = None
    last_pong_time: Optional[float] = None
    messages_sent: int = 0
    messages_received: int = 0
    errors_count: int = 0
    reconnection_count: int = 0
    avg_latency: float = 0.0
    latency_samples: List[float] = field(default_factory=list)
    max_latency_samples: int = 100
    
    def record_ping(self):
        """Record a ping being sent."""
        self.last_ping_time = time.time()
    
    def record_pong(self):
        """Record a pong being received and calculate latency."""
        self.last_pong_time = time.time()
        if self.last_ping_time:
            latency = self.last_pong_time - self.last_ping_time
            self.latency_samples.append(latency)
            
            # Keep only recent samples
            if len(self.latency_samples) > self.max_latency_samples:
                self.latency_samples.pop(0)
            
            # Update average latency
            self.avg_latency = sum(self.latency_samples) / len(self.latency_samples)
    
    def record_message_sent(self):
        """Record a message being sent."""
        self.messages_sent += 1
    
    def record_message_received(self):
        """Record a message being received."""
        self.messages_received += 1
    
    def record_error(self):
        """Record an error occurrence."""
        self.errors_count += 1
    
    def record_reconnection(self):
        """Record a reconnection attempt."""
        self.reconnection_count += 1
        self.connected_since = time.time()
    
    def get_uptime(self) -> float:
        """Calculate current uptime in seconds."""
        if self.connected_since:
            return time.time() - self.connected_since
        return 0.0
    
    def reset(self):
        """Reset all metrics."""
        self.connected_since = time.time()
        self.last_ping_time = None
        self.last_pong_time = None
        self.messages_sent = 0
        self.messages_received = 0
        self.errors_count = 0
        self.avg_latency = 0.0
        self.latency_samples.clear()
    
    def to_dict(self) -> Dict[str, Any]:
        """Export metrics as dictionary."""
        return {
            'uptime': self.get_uptime(),
            'messages_sent': self.messages_sent,
            'messages_received': self.messages_received,
            'errors_count': self.errors_count,
            'reconnection_count': self.reconnection_count,
            'avg_latency': self.avg_latency,
            'last_ping_time': self.last_ping_time,
            'last_pong_time': self.last_pong_time,
        }


class ConnectionHealth:
    """
    Connection health monitor for tracking and assessing connection quality.
    """
    
    def __init__(self):
        """Initialize connection health monitor."""
        self.metrics = ConnectionMetrics()
        self._quality = NetworkQuality.GOOD
        self._health_score = 100.0
        self._consecutive_errors = 0
        self._last_health_check = time.time()
    
    @property
    def quality(self) -> NetworkQuality:
        """Get current network quality assessment."""
        return self._quality
    
    @property
    def health_score(self) -> float:
        """Get current health score (0-100)."""
        return self._health_score
    
    @property
    def is_healthy(self) -> bool:
        """Check if connection is healthy."""
        return self._health_score >= 50 and self._quality not in [NetworkQuality.POOR, NetworkQuality.CRITICAL]
    
    def update_health(self):
        """Update health score and quality assessment."""
        self._health_score = calculate_health_score(self.metrics)
        self._quality = assess_connection_quality(self.metrics, self._health_score)
        self._last_health_check = time.time()
    
    def record_successful_operation(self):
        """Record a successful operation."""
        self._consecutive_errors = 0
    
    def record_error(self):
        """Record an error and update health."""
        self.metrics.record_error()
        self._consecutive_errors += 1
        self.update_health()
    
    def get_consecutive_errors(self) -> int:
        """Get count of consecutive errors."""
        return self._consecutive_errors
    
    def reset(self):
        """Reset health monitor."""
        self.metrics.reset()
        self._quality = NetworkQuality.GOOD
        self._health_score = 100.0
        self._consecutive_errors = 0
        self._last_health_check = time.time()
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive health status."""
        return {
            'quality': self._quality.value,
            'health_score': self._health_score,
            'is_healthy': self.is_healthy,
            'consecutive_errors': self._consecutive_errors,
            'metrics': self.metrics.to_dict(),
        }


def calculate_health_score(metrics: ConnectionMetrics) -> float:
    """
    Calculate connection health score based on metrics.
    
    Args:
        metrics: Connection metrics
        
    Returns:
        Health score from 0 to 100
    """
    score = 100.0
    
    # Deduct points for errors
    if metrics.errors_count > 0:
        error_penalty = min(30, metrics.errors_count * 3)
        score -= error_penalty
    
    # Deduct points for high latency
    if metrics.avg_latency > 1.0:  # More than 1 second average latency
        latency_penalty = min(20, (metrics.avg_latency - 1.0) * 10)
        score -= latency_penalty
    
    # Deduct points for reconnections
    if metrics.reconnection_count > 0:
        reconnect_penalty = min(25, metrics.reconnection_count * 5)
        score -= reconnect_penalty
    
    # Bonus for uptime
    uptime = metrics.get_uptime()
    if uptime > 3600:  # More than 1 hour
        score = min(100, score + 5)
    
    # Ensure score is between 0 and 100
    return max(0.0, min(100.0, score))


def assess_connection_quality(
    metrics: ConnectionMetrics,
    health_score: float
) -> NetworkQuality:
    """
    Assess network quality based on metrics and health score.
    
    Args:
        metrics: Connection metrics
        health_score: Current health score
        
    Returns:
        NetworkQuality assessment
    """
    # Critical: Very low health score or many recent errors
    if health_score < 20 or metrics.errors_count > 10:
        return NetworkQuality.CRITICAL
    
    # Poor: Low health score or high latency
    if health_score < 40 or metrics.avg_latency > 2.0:
        return NetworkQuality.POOR
    
    # Fair: Medium health score or moderate latency
    if health_score < 60 or metrics.avg_latency > 1.0:
        return NetworkQuality.FAIR
    
    # Good: Good health score
    if health_score < 80:
        return NetworkQuality.GOOD
    
    # Excellent: High health score and low latency
    return NetworkQuality.EXCELLENT


def get_recommended_ping_interval(quality: NetworkQuality) -> int:
    """
    Get recommended ping interval based on network quality.
    
    Args:
        quality: Current network quality
        
    Returns:
        Recommended ping interval in seconds
    """
    recommendations = {
        NetworkQuality.EXCELLENT: 30,
        NetworkQuality.GOOD: 30,
        NetworkQuality.FAIR: 45,
        NetworkQuality.POOR: 60,
        NetworkQuality.CRITICAL: 90,
    }
    return recommendations.get(quality, 30)


def diagnose_connection_issues(
    metrics: ConnectionMetrics,
    health: ConnectionHealth
) -> List[str]:
    """
    Diagnose potential connection issues and provide recommendations.
    
    Args:
        metrics: Connection metrics
        health: Connection health monitor
        
    Returns:
        List of diagnostic messages and recommendations
    """
    issues = []
    
    if metrics.errors_count > 5:
        issues.append(
            f"High error count ({metrics.errors_count}). "
            "Consider checking network stability or server availability."
        )
    
    if metrics.avg_latency > 2.0:
        issues.append(
            f"High average latency ({metrics.avg_latency:.2f}s). "
            "Connection may be slow or unstable."
        )
    
    if metrics.reconnection_count > 3:
        issues.append(
            f"Multiple reconnections ({metrics.reconnection_count}). "
            "Network may be experiencing interruptions."
        )
    
    if health.get_consecutive_errors() > 3:
        issues.append(
            f"Consecutive errors detected ({health.get_consecutive_errors()}). "
            "Connection may need to be reset."
        )
    
    uptime = metrics.get_uptime()
    if uptime < 60 and metrics.reconnection_count > 0:
        issues.append(
            "Connection is unstable (frequent disconnections). "
            "Consider using a more stable network or adjusting connection settings."
        )
    
    if not issues:
        issues.append("Connection health is good. No issues detected.")
    
    return issues

