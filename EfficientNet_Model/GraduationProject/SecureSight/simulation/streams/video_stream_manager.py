"""
SecureSight — Video Stream Manager
=====================================
Stream abstraction layer for future protocol support.
Manages: RTSP, AirSim camera, USB camera, recorded video.
"""

import logging
from typing import Optional, Dict

logger = logging.getLogger("SecureSight.StreamManager")


class StreamEndpoint:
    """Describes a stream source endpoint."""

    def __init__(self, name: str, protocol: str, uri: str,
                 width: int = 640, height: int = 480, fps: int = 30):
        self.name = name
        self.protocol = protocol  # synthetic | usb | rtsp | airsim | file
        self.uri = uri
        self.width = width
        self.height = height
        self.fps = fps
        self.active = False

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "protocol": self.protocol,
            "uri": self.uri,
            "resolution": f"{self.width}x{self.height}",
            "fps": self.fps,
            "active": self.active,
        }


class VideoStreamManager:
    """
    Manages multiple video stream endpoints.
    Future-ready for RTSP, AirSim, USB, and file-based streams.
    Currently delegates actual capture to FrameReceiver.
    """

    def __init__(self):
        self._endpoints: Dict[str, StreamEndpoint] = {}
        self._active_endpoint: Optional[str] = None

    def register_endpoint(self, endpoint: StreamEndpoint):
        self._endpoints[endpoint.name] = endpoint
        logger.info(f"[StreamManager] Registered: {endpoint.name} ({endpoint.protocol})")

    def register_synthetic(self, name: str = "synthetic_default",
                           width: int = 640, height: int = 480, fps: int = 30):
        ep = StreamEndpoint(name, "synthetic", "internal://synthetic", width, height, fps)
        self.register_endpoint(ep)
        return ep

    def register_webcam(self, name: str = "webcam_0", index: int = 0,
                        width: int = 640, height: int = 480):
        ep = StreamEndpoint(name, "usb", f"usb://{index}", width, height, 30)
        self.register_endpoint(ep)
        return ep

    def register_rtsp(self, name: str, url: str, width: int = 640, height: int = 480):
        ep = StreamEndpoint(name, "rtsp", url, width, height, 30)
        self.register_endpoint(ep)
        return ep

    def register_airsim(self, name: str = "airsim_front",
                        camera: str = "front_center",
                        width: int = 640, height: int = 480):
        ep = StreamEndpoint(name, "airsim", f"airsim://{camera}", width, height, 30)
        self.register_endpoint(ep)
        return ep

    def register_video_file(self, name: str, path: str):
        ep = StreamEndpoint(name, "file", path, 0, 0, 0)
        self.register_endpoint(ep)
        return ep

    def set_active(self, name: str) -> bool:
        if name not in self._endpoints:
            logger.error(f"[StreamManager] Unknown endpoint: {name}")
            return False
        if self._active_endpoint:
            self._endpoints[self._active_endpoint].active = False
        self._active_endpoint = name
        self._endpoints[name].active = True
        logger.info(f"[StreamManager] Active stream: {name}")
        return True

    def get_active(self) -> Optional[StreamEndpoint]:
        if self._active_endpoint:
            return self._endpoints.get(self._active_endpoint)
        return None

    def list_endpoints(self) -> list:
        return [ep.to_dict() for ep in self._endpoints.values()]

    @property
    def active_name(self) -> Optional[str]:
        return self._active_endpoint

    @property
    def endpoint_count(self) -> int:
        return len(self._endpoints)
