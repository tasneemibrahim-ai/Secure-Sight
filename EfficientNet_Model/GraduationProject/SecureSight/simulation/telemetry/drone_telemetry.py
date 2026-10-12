"""
SecureSight — Drone Telemetry
===============================
Simulated drone telemetry structure with JSON export.
"""

import time
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

logger = logging.getLogger("SecureSight.Telemetry")


class TelemetryRecord:
    """Single telemetry snapshot."""

    def __init__(self):
        self.timestamp = time.time()
        self.frame_index = 0
        # Drone state
        self.position = {"x": 0.0, "y": 0.0, "z": 0.0}
        self.gps = {"lat": 0.0, "lon": 0.0, "alt": 0.0}
        self.altitude_agl = 0.0
        self.speed_ms = 0.0
        self.heading_deg = 0.0
        self.battery_percent = 100.0
        # Inference result
        self.predicted_class = "Unknown"
        self.confidence = 0.0
        self.is_alert = False
        self.inference_latency_ms = 0.0
        # Pipeline stats
        self.fps = 0.0
        self.e2e_latency_ms = 0.0

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "frame_index": self.frame_index,
            "drone": {
                "position": self.position,
                "gps": self.gps,
                "altitude_agl_m": self.altitude_agl,
                "speed_ms": round(self.speed_ms, 2),
                "heading_deg": round(self.heading_deg, 1),
                "battery_percent": round(self.battery_percent, 1),
            },
            "inference": {
                "predicted_class": self.predicted_class,
                "confidence": round(self.confidence, 4),
                "is_alert": self.is_alert,
                "latency_ms": round(self.inference_latency_ms, 2),
            },
            "pipeline": {
                "fps": round(self.fps, 1),
                "e2e_latency_ms": round(self.e2e_latency_ms, 2),
            },
        }


class DroneTelemetry:
    """
    Manages telemetry recording, buffering, and export.
    """

    def __init__(self, max_records: int = 10000):
        self._records: List[TelemetryRecord] = []
        self._max = max_records
        self._alerts: List[TelemetryRecord] = []
        self._started = False
        self._start_time = 0.0

    def start(self):
        self._records.clear()
        self._alerts.clear()
        self._start_time = time.time()
        self._started = True
        logger.info("[Telemetry] Recording started")

    def stop(self):
        self._started = False
        logger.info(f"[Telemetry] Stopped -- {len(self._records)} records, {len(self._alerts)} alerts")

    def record(self, telemetry: TelemetryRecord):
        if not self._started:
            return
        if len(self._records) >= self._max:
            self._records.pop(0)
        self._records.append(telemetry)
        if telemetry.is_alert:
            self._alerts.append(telemetry)

    def build_record(self, drone_state=None, inference_result=None,
                     fps=0.0, e2e_ms=0.0, frame_index=0) -> TelemetryRecord:
        """Convenience builder from drone state + inference result."""
        rec = TelemetryRecord()
        rec.frame_index = frame_index
        rec.fps = fps
        rec.e2e_latency_ms = e2e_ms

        if drone_state is not None:
            rec.position = drone_state.position.to_dict() if hasattr(drone_state.position, 'to_dict') else {"x": 0, "y": 0, "z": 0}
            rec.gps = drone_state.gps.to_dict() if hasattr(drone_state.gps, 'to_dict') else {"lat": 0, "lon": 0, "alt": 0}
            rec.altitude_agl = drone_state.altitude_agl
            rec.speed_ms = drone_state.speed
            rec.heading_deg = drone_state.heading_deg
            rec.battery_percent = drone_state.battery_percent

        if inference_result is not None:
            rec.predicted_class = inference_result.class_name
            rec.confidence = inference_result.confidence
            rec.is_alert = inference_result.is_alert
            rec.inference_latency_ms = inference_result.latency_ms

        return rec

    def export_json(self, filepath: str):
        """Export all telemetry records to JSON."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        data = {
            "session_start": self._start_time,
            "session_duration_s": round(time.time() - self._start_time, 1) if self._started or self._records else 0,
            "total_records": len(self._records),
            "total_alerts": len(self._alerts),
            "records": [r.to_dict() for r in self._records[-500:]],  # Last 500
            "alerts": [a.to_dict() for a in self._alerts[-100:]],
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"[Telemetry] Exported to {filepath}")

    @property
    def record_count(self) -> int:
        return len(self._records)

    @property
    def alert_count(self) -> int:
        return len(self._alerts)

    @property
    def latest(self) -> Optional[TelemetryRecord]:
        return self._records[-1] if self._records else None

    def get_summary(self) -> dict:
        return {
            "total_records": len(self._records),
            "total_alerts": len(self._alerts),
            "duration_s": round(time.time() - self._start_time, 1) if self._start_time else 0,
            "alert_classes": list(set(a.predicted_class for a in self._alerts)),
        }
