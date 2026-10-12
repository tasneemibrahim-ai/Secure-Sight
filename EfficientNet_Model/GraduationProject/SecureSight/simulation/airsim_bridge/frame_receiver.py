"""
SecureSight — Frame Receiver
=============================
Camera frame abstraction layer with multiple input sources.
Falls back to synthetic frames if no camera/video available.
"""

import time
import logging
from dataclasses import dataclass
from typing import Optional, Dict

logger = logging.getLogger("SecureSight.FrameReceiver")

NUMPY_AVAILABLE = False
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    pass

CV2_AVAILABLE = False
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    pass

AIRSIM_AVAILABLE = False
try:
    import airsim
    AIRSIM_AVAILABLE = True
except ImportError:
    pass


@dataclass
class FrameMetadata:
    source: str = "unknown"
    frame_index: int = 0
    timestamp: float = 0.0
    width: int = 0
    height: int = 0
    channels: int = 3
    acquisition_time_ms: float = 0.0


class FrameResult:
    def __init__(self, frame, metadata: FrameMetadata, success: bool = True):
        self.frame = frame
        self.metadata = metadata
        self.success = success

    def __bool__(self):
        return self.success


class SyntheticFrameSource:
    """Generates test frames with no external dependencies beyond numpy."""

    def __init__(self, width=640, height=480, fps=30):
        self._w, self._h, self._fps = width, height, fps
        self._idx = 0
        self._started = False

    def open(self):
        if not NUMPY_AVAILABLE:
            return False
        self._started = True
        self._idx = 0
        return True

    def read(self):
        if not self._started:
            return FrameResult(None, FrameMetadata(source="synthetic"), False)
        t0 = time.perf_counter()
        import math
        t = self._idx / max(self._fps, 1)
        frame = np.zeros((self._h, self._w, 3), dtype=np.uint8)
        shift = int(50 * math.sin(t * 0.5))
        for i in range(3):
            ramp = np.linspace(shift + i * 30, 255, self._w, dtype=np.uint8)
            frame[:, :, i] = np.tile(ramp, (self._h, 1))
        noise = np.random.randint(0, 20, frame.shape, dtype=np.uint8)
        frame = np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        acq = (time.perf_counter() - t0) * 1000
        meta = FrameMetadata("synthetic", self._idx, time.time(), self._w, self._h, 3, acq)
        self._idx += 1
        elapsed = time.perf_counter() - t0
        target = 1.0 / self._fps
        if elapsed < target:
            time.sleep(target - elapsed)
        return FrameResult(frame, meta, True)

    def close(self):
        self._started = False

    @property
    def is_open(self):
        return self._started


class WebcamFrameSource:
    """USB webcam via OpenCV."""

    def __init__(self, camera_index=0, width=640, height=480):
        self._idx_cam = camera_index
        self._w, self._h = width, height
        self._cap = None
        self._idx = 0

    def open(self):
        if not CV2_AVAILABLE:
            return False
        self._cap = cv2.VideoCapture(self._idx_cam)
        if not self._cap.isOpened():
            return False
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._w)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._h)
        self._idx = 0
        return True

    def read(self):
        if not self._cap or not self._cap.isOpened():
            return FrameResult(None, FrameMetadata(source="webcam"), False)
        t0 = time.perf_counter()
        ret, frame = self._cap.read()
        acq = (time.perf_counter() - t0) * 1000
        if not ret:
            return FrameResult(None, FrameMetadata(source="webcam"), False)
        h, w = frame.shape[:2]
        meta = FrameMetadata("webcam", self._idx, time.time(), w, h, 3, acq)
        self._idx += 1
        return FrameResult(frame, meta, True)

    def close(self):
        if self._cap:
            self._cap.release()
        self._cap = None

    @property
    def is_open(self):
        return self._cap is not None and self._cap.isOpened()


class VideoFileFrameSource:
    """Reads frames from a video file with optional looping."""

    def __init__(self, video_path: str, loop: bool = True):
        self._path = video_path
        self._loop = loop
        self._cap = None
        self._idx = 0

    def open(self):
        if not CV2_AVAILABLE:
            return False
        from pathlib import Path
        if not Path(self._path).exists():
            return False
        self._cap = cv2.VideoCapture(self._path)
        return self._cap.isOpened()

    def read(self):
        if not self._cap or not self._cap.isOpened():
            return FrameResult(None, FrameMetadata(source="video"), False)
        t0 = time.perf_counter()
        ret, frame = self._cap.read()
        if not ret and self._loop:
            self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self._cap.read()
        acq = (time.perf_counter() - t0) * 1000
        if not ret:
            return FrameResult(None, FrameMetadata(source="video"), False)
        h, w = frame.shape[:2]
        meta = FrameMetadata("video", self._idx, time.time(), w, h, 3, acq)
        self._idx += 1
        return FrameResult(frame, meta, True)

    def close(self):
        if self._cap:
            self._cap.release()
        self._cap = None

    @property
    def is_open(self):
        return self._cap is not None and self._cap.isOpened()


class AirSimFrameSource:
    """Captures frames from AirSim simulated camera."""

    def __init__(self, config: Optional[Dict] = None):
        if not AIRSIM_AVAILABLE:
            raise RuntimeError("AirSim not installed")
        cfg = config or {}
        self._ip = cfg.get("airsim_ip", "127.0.0.1")
        self._port = cfg.get("airsim_port", 41451)
        self._camera = cfg.get("camera_name", "front_center")
        self._vehicle = cfg.get("vehicle_name", "SecureSightDrone")
        self._client = None
        self._idx = 0

    def open(self):
        try:
            self._client = airsim.MultirotorClient(ip=self._ip, port=self._port)
            self._client.confirmConnection()
            return True
        except Exception:
            return False

    def read(self):
        if not self._client:
            return FrameResult(None, FrameMetadata(source="airsim"), False)
        try:
            t0 = time.perf_counter()
            resp = self._client.simGetImages([
                airsim.ImageRequest(self._camera, airsim.ImageType.Scene, False, False)
            ], vehicle_name=self._vehicle)
            if not resp or resp[0].width == 0:
                return FrameResult(None, FrameMetadata(source="airsim"), False)
            r = resp[0]
            img = np.frombuffer(r.image_data_uint8, dtype=np.uint8)
            frame = img.reshape(r.height, r.width, 3)
            acq = (time.perf_counter() - t0) * 1000
            meta = FrameMetadata("airsim", self._idx, time.time(), r.width, r.height, 3, acq)
            self._idx += 1
            return FrameResult(frame, meta, True)
        except Exception:
            return FrameResult(None, FrameMetadata(source="airsim"), False)

    def close(self):
        self._client = None

    @property
    def is_open(self):
        return self._client is not None


class FrameReceiver:
    """Factory that creates the right frame source with automatic fallback."""

    def __init__(self, config: Optional[Dict] = None):
        self._config = config or {}
        self._source = None
        self._source_type = "none"

    def initialize(self, preferred: str = "synthetic") -> bool:
        builders = {
            "airsim": self._try_airsim,
            "webcam": self._try_webcam,
            "video": self._try_video,
            "synthetic": self._try_synthetic,
        }
        if builders.get(preferred, self._try_synthetic)():
            return True
        if preferred != "synthetic":
            logger.warning(f"'{preferred}' unavailable -- falling back to synthetic")
            return self._try_synthetic()
        return False

    def _try_airsim(self):
        if not AIRSIM_AVAILABLE:
            return False
        try:
            s = AirSimFrameSource(self._config)
            if s.open():
                self._source, self._source_type = s, "airsim"
                return True
        except Exception:
            pass
        return False

    def _try_webcam(self):
        if not CV2_AVAILABLE:
            return False
        s = WebcamFrameSource(self._config.get("webcam_index", 0),
                              self._config.get("frame_width", 640),
                              self._config.get("frame_height", 480))
        if s.open():
            self._source, self._source_type = s, "webcam"
            return True
        return False

    def _try_video(self):
        if not CV2_AVAILABLE:
            return False
        p = self._config.get("video_path")
        if not p:
            return False
        s = VideoFileFrameSource(p)
        if s.open():
            self._source, self._source_type = s, "video"
            return True
        return False

    def _try_synthetic(self):
        if not NUMPY_AVAILABLE:
            return False
        s = SyntheticFrameSource(self._config.get("frame_width", 640),
                                  self._config.get("frame_height", 480),
                                  self._config.get("synthetic_fps", 30))
        if s.open():
            self._source, self._source_type = s, "synthetic"
            return True
        return False

    def read_frame(self):
        if not self._source:
            return FrameResult(None, FrameMetadata(), False)
        return self._source.read()

    def close(self):
        if self._source:
            self._source.close()
        self._source = None
        self._source_type = "none"

    @property
    def source_type(self):
        return self._source_type

    @property
    def is_open(self):
        return self._source is not None and self._source.is_open
