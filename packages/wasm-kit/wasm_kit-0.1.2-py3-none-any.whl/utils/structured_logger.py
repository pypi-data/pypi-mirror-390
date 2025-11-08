# Production-grade structured logging

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class StructuredLogger:
    """Structured logger with JSON output for production monitoring."""

    def __init__(self, name: str, level: str = "INFO", log_file: Optional[Path] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        self.service_name = "wasm-kit"

        formatter = StructuredFormatter()

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def _log(self, level: str, message: str, **kwargs):
        extra = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            **kwargs,
        }
        getattr(self.logger, level)(message, extra={"structured": extra})

    def info(self, message: str, **kwargs):
        self._log("info", message, **kwargs)

    def error(self, message: str, **kwargs):
        self._log("error", message, **kwargs)

    def warning(self, message: str, **kwargs):
        self._log("warning", message, **kwargs)

    def debug(self, message: str, **kwargs):
        self._log("debug", message, **kwargs)


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logs."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "structured"):
            log_data.update(record.structured)

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class MetricsCollector:
    """Collect and export Prometheus-style metrics."""

    def __init__(self):
        self.metrics: Dict[str, Any] = {
            "builds_total": 0,
            "builds_successful": 0,
            "builds_failed": 0,
            "build_duration_seconds": [],
            "cache_hits": 0,
            "cache_misses": 0,
        }

    def record_build(self, success: bool, duration: float):
        self.metrics["builds_total"] += 1
        if success:
            self.metrics["builds_successful"] += 1
        else:
            self.metrics["builds_failed"] += 1
        self.metrics["build_duration_seconds"].append(duration)

    def record_cache_hit(self):
        self.metrics["cache_hits"] += 1

    def record_cache_miss(self):
        self.metrics["cache_misses"] += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Return metrics in Prometheus format."""
        avg_duration = (
            sum(self.metrics["build_duration_seconds"])
            / len(self.metrics["build_duration_seconds"])
            if self.metrics["build_duration_seconds"]
            else 0
        )

        return {
            **self.metrics,
            "build_duration_avg_seconds": avg_duration,
            "build_success_rate": (
                self.metrics["builds_successful"] / self.metrics["builds_total"]
                if self.metrics["builds_total"] > 0
                else 0
            ),
            "cache_hit_rate": (
                self.metrics["cache_hits"]
                / (self.metrics["cache_hits"] + self.metrics["cache_misses"])
                if (self.metrics["cache_hits"] + self.metrics["cache_misses"]) > 0
                else 0
            ),
        }


# Global instances
logger = StructuredLogger("wasm-kit")
metrics = MetricsCollector()
