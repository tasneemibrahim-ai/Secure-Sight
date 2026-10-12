"""
SecureSight — Latency Monitor
===============================
Tracks end-to-end, inference, and frame acquisition latencies.
"""

import time
import collections


class LatencyMonitor:
    """Tracks multiple latency metrics with rolling window."""

    def __init__(self, window_size: int = 60):
        self._window = window_size
        self._inference_times = collections.deque(maxlen=window_size)
        self._acquisition_times = collections.deque(maxlen=window_size)
        self._e2e_times = collections.deque(maxlen=window_size)
        self._frame_count = 0

    def record_inference(self, latency_ms: float):
        self._inference_times.append(latency_ms)

    def record_acquisition(self, latency_ms: float):
        self._acquisition_times.append(latency_ms)

    def record_end_to_end(self, latency_ms: float):
        self._e2e_times.append(latency_ms)
        self._frame_count += 1

    def _stats(self, data) -> dict:
        if not data:
            return {"mean_ms": 0, "min_ms": 0, "max_ms": 0, "latest_ms": 0}
        d = list(data)
        return {
            "mean_ms": round(sum(d) / len(d), 2),
            "min_ms": round(min(d), 2),
            "max_ms": round(max(d), 2),
            "latest_ms": round(d[-1], 2),
        }

    @property
    def inference_stats(self) -> dict:
        return self._stats(self._inference_times)

    @property
    def acquisition_stats(self) -> dict:
        return self._stats(self._acquisition_times)

    @property
    def end_to_end_stats(self) -> dict:
        return self._stats(self._e2e_times)

    @property
    def avg_inference_ms(self) -> float:
        if not self._inference_times:
            return 0.0
        return sum(self._inference_times) / len(self._inference_times)

    @property
    def avg_e2e_ms(self) -> float:
        if not self._e2e_times:
            return 0.0
        return sum(self._e2e_times) / len(self._e2e_times)

    def get_stats(self) -> dict:
        return {
            "inference": self.inference_stats,
            "acquisition": self.acquisition_stats,
            "end_to_end": self.end_to_end_stats,
            "total_frames": self._frame_count,
        }

    def __repr__(self):
        return (f"<LatencyMonitor e2e={self.avg_e2e_ms:.1f}ms "
                f"inference={self.avg_inference_ms:.1f}ms frames={self._frame_count}>")
