"""
SecureSight — FPS Monitor
==========================
Real-time frames-per-second tracking with rolling statistics.
"""

import time
import collections


class FPSMonitor:
    """Tracks real-time FPS with rolling window statistics."""

    def __init__(self, window_size: int = 60):
        self._window_size = window_size
        self._timestamps = collections.deque(maxlen=window_size)
        self._all_fps = []
        self._peak_fps = 0.0
        self._min_fps = float("inf")
        self._frame_count = 0
        self._start_time = None

    def start(self):
        self._start_time = time.perf_counter()
        self._timestamps.clear()
        self._all_fps.clear()
        self._peak_fps = 0.0
        self._min_fps = float("inf")
        self._frame_count = 0

    def tick(self):
        """Call once per frame to record timing."""
        now = time.perf_counter()
        self._timestamps.append(now)
        self._frame_count += 1

        fps = self.current_fps
        if fps > 0:
            self._all_fps.append(fps)
            if fps > self._peak_fps:
                self._peak_fps = fps
            if fps < self._min_fps:
                self._min_fps = fps

    @property
    def current_fps(self) -> float:
        if len(self._timestamps) < 2:
            return 0.0
        dt = self._timestamps[-1] - self._timestamps[0]
        if dt <= 0:
            return 0.0
        return (len(self._timestamps) - 1) / dt

    @property
    def rolling_average(self) -> float:
        return self.current_fps

    @property
    def peak_fps(self) -> float:
        return self._peak_fps

    @property
    def min_fps(self) -> float:
        return self._min_fps if self._min_fps != float("inf") else 0.0

    @property
    def overall_average(self) -> float:
        if not self._all_fps:
            return 0.0
        return sum(self._all_fps) / len(self._all_fps)

    @property
    def total_frames(self) -> int:
        return self._frame_count

    @property
    def elapsed_seconds(self) -> float:
        if self._start_time is None:
            return 0.0
        return time.perf_counter() - self._start_time

    def get_stats(self) -> dict:
        return {
            "current_fps": round(self.current_fps, 1),
            "rolling_avg_fps": round(self.rolling_average, 1),
            "peak_fps": round(self.peak_fps, 1),
            "min_fps": round(self.min_fps, 1),
            "overall_avg_fps": round(self.overall_average, 1),
            "total_frames": self.total_frames,
            "elapsed_seconds": round(self.elapsed_seconds, 1),
        }

    def __repr__(self):
        return f"<FPSMonitor fps={self.current_fps:.1f} peak={self.peak_fps:.1f} frames={self._frame_count}>"
