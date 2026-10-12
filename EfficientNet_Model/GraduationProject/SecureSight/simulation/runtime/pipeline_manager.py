"""
SecureSight — Pipeline Manager
================================
Controls the entire runtime loop: frame capture, inference,
telemetry updates, alert generation, and statistics reporting.
"""

import time
import logging
import threading
from typing import Optional, Callable, List, Dict

logger = logging.getLogger("SecureSight.PipelineManager")

try:
    import queue
except ImportError:
    import Queue as queue


class Alert:
    """Represents a detected anomaly alert."""

    def __init__(self, class_name: str, confidence: float, frame_index: int,
                 drone_position: dict = None, gps: dict = None):
        self.timestamp = time.time()
        self.class_name = class_name
        self.confidence = confidence
        self.frame_index = frame_index
        self.drone_position = drone_position or {}
        self.gps = gps or {}
        self.acknowledged = False

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "class": self.class_name,
            "confidence": round(self.confidence, 4),
            "frame_index": self.frame_index,
            "drone_position": self.drone_position,
            "gps": self.gps,
            "acknowledged": self.acknowledged,
        }

    def __repr__(self):
        return f"<Alert {self.class_name} conf={self.confidence:.2f} frame={self.frame_index}>"


class PipelineManager:
    """
    Orchestrates the complete drone surveillance pipeline:
    1. Frame acquisition from FrameReceiver
    2. Inference via RealtimeInferenceEngine
    3. Telemetry recording
    4. Alert generation
    5. Statistics collection
    """

    def __init__(self, frame_receiver, inference_engine, drone_connector,
                 telemetry_recorder, fps_monitor, latency_monitor,
                 config: Optional[Dict] = None):
        self._frame_rx = frame_receiver
        self._inference = inference_engine
        self._drone = drone_connector
        self._telemetry = telemetry_recorder
        self._fps = fps_monitor
        self._latency = latency_monitor

        cfg = config or {}
        self._confidence_threshold = cfg.get("confidence_threshold", 0.5)
        self._alert_cooldown = cfg.get("alert_cooldown_seconds", 5.0)
        self._log_interval = cfg.get("log_interval_seconds", 2.0)
        self._max_runtime = cfg.get("max_runtime_seconds", 0)
        self._enable_alerts = cfg.get("enable_alerts", True)

        self._alerts: List[Alert] = []
        self._last_alert_time: Dict[str, float] = {}
        self._running = False
        self._frame_count = 0
        self._last_log_time = 0.0
        self._on_alert_callback: Optional[Callable] = None
        self._on_frame_callback: Optional[Callable] = None

    def set_alert_callback(self, callback: Callable):
        self._on_alert_callback = callback

    def set_frame_callback(self, callback: Callable):
        self._on_frame_callback = callback

    def run(self, max_frames: int = 0, duration_seconds: float = 0):
        """
        Main pipeline loop.
        Args:
            max_frames: Stop after N frames (0 = unlimited)
            duration_seconds: Stop after N seconds (0 = use config or unlimited)
        """
        self._running = True
        self._frame_count = 0
        self._fps.start()
        self._telemetry.start()
        start_time = time.time()

        max_dur = duration_seconds or self._max_runtime
        logger.info("[Pipeline] Starting main loop")
        print("[SecureSight] >> Pipeline running...")

        try:
            while self._running:
                e2e_start = time.perf_counter()

                # 1. Acquire frame
                frame_result = self._frame_rx.read_frame()
                if not frame_result.success:
                    logger.warning("[Pipeline] Frame acquisition failed")
                    time.sleep(0.01)
                    continue

                self._latency.record_acquisition(frame_result.metadata.acquisition_time_ms)

                # 2. Run inference
                inf_result = self._inference.predict_frame(frame_result.frame)
                self._latency.record_inference(inf_result.latency_ms)

                # 3. Get drone state
                drone_state = self._drone.get_state()

                # 4. Record end-to-end latency
                e2e_ms = (time.perf_counter() - e2e_start) * 1000
                self._latency.record_end_to_end(e2e_ms)

                # 5. FPS tick
                self._fps.tick()

                # 6. Build telemetry record
                telem = self._telemetry.build_record(
                    drone_state=drone_state,
                    inference_result=inf_result,
                    fps=self._fps.current_fps,
                    e2e_ms=e2e_ms,
                    frame_index=self._frame_count,
                )
                self._telemetry.record(telem)

                # 7. Check for alerts
                if self._enable_alerts and inf_result.is_alert:
                    self._handle_alert(inf_result, drone_state)

                # 8. Frame callback
                if self._on_frame_callback:
                    self._on_frame_callback(frame_result, inf_result, drone_state)

                # 9. Periodic logging
                now = time.time()
                if now - self._last_log_time >= self._log_interval:
                    self._print_status(inf_result, drone_state)
                    self._last_log_time = now

                self._frame_count += 1

                # Check stop conditions
                if max_frames > 0 and self._frame_count >= max_frames:
                    logger.info(f"[Pipeline] Reached {max_frames} frames -- stopping")
                    break
                if max_dur > 0 and (now - start_time) >= max_dur:
                    logger.info(f"[Pipeline] Reached {max_dur}s runtime -- stopping")
                    break

        except KeyboardInterrupt:
            print("\n[SecureSight] Pipeline stopped by user (Ctrl+C)")
        finally:
            self._running = False
            self._telemetry.stop()

        return self.get_session_summary()

    def stop(self):
        self._running = False

    def _handle_alert(self, inf_result, drone_state):
        cls = inf_result.class_name
        now = time.time()
        last = self._last_alert_time.get(cls, 0)
        if (now - last) < self._alert_cooldown:
            return

        pos = drone_state.position.to_dict() if hasattr(drone_state.position, 'to_dict') else {}
        gps = drone_state.gps.to_dict() if hasattr(drone_state.gps, 'to_dict') else {}
        alert = Alert(cls, inf_result.confidence, self._frame_count, pos, gps)
        self._alerts.append(alert)
        self._last_alert_time[cls] = now

        print(f"  [ALERT] {cls} (conf={inf_result.confidence:.2f}) "
              f"at frame #{self._frame_count}")

        if self._on_alert_callback:
            self._on_alert_callback(alert)

    def _print_status(self, inf_result, drone_state):
        fps_stats = self._fps.get_stats()
        lat_stats = self._latency.get_stats()
        print(f"  [{self._frame_count:>6}] "
              f"FPS={fps_stats['current_fps']:>5.1f} | "
              f"E2E={lat_stats['end_to_end']['latest_ms']:>6.1f}ms | "
              f"Pred={inf_result.class_name:<18s} "
              f"Conf={inf_result.confidence:.2f} | "
              f"Bat={drone_state.battery_percent:.0f}% | "
              f"Alt={drone_state.altitude_agl:.0f}m")

    def get_session_summary(self) -> dict:
        return {
            "total_frames": self._frame_count,
            "total_alerts": len(self._alerts),
            "fps_stats": self._fps.get_stats(),
            "latency_stats": self._latency.get_stats(),
            "telemetry_summary": self._telemetry.get_summary(),
            "alerts": [a.to_dict() for a in self._alerts[-50:]],
        }

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def frame_count(self) -> int:
        return self._frame_count

    @property
    def alert_count(self) -> int:
        return len(self._alerts)
