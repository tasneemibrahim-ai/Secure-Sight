"""
SecureSight — AirSim Drone Connector
======================================
Provides a unified drone control interface.
Falls back to a fully-functional mock drone if AirSim is not installed.

Usage:
    connector = DroneConnector()
    connector.connect()
    state = connector.get_state()
    connector.disconnect()
"""

import time
import math
import random
import logging
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any

# ── Safe AirSim import ──
AIRSIM_AVAILABLE = False
try:
    import airsim
    AIRSIM_AVAILABLE = True
except ImportError:
    pass

logger = logging.getLogger("SecureSight.DroneConnector")


# ============================================================
#  DATA STRUCTURES
# ============================================================

@dataclass
class DronePosition:
    """3D position in NED frame (meters)."""
    x: float = 0.0
    y: float = 0.0
    z: float = -30.0  # Negative = above ground in NED

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class DroneGPS:
    """GPS coordinates."""
    latitude: float = 24.7136
    longitude: float = 46.6753
    altitude: float = 642.0  # meters above sea level

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class DroneState:
    """Complete drone state snapshot."""
    connected: bool = False
    armed: bool = False
    mode: str = "MOCK"
    position: DronePosition = field(default_factory=DronePosition)
    gps: DroneGPS = field(default_factory=DroneGPS)
    altitude_agl: float = 30.0       # Above ground level (m)
    velocity_x: float = 0.0          # m/s
    velocity_y: float = 0.0
    velocity_z: float = 0.0
    speed: float = 0.0               # Total speed m/s
    heading_deg: float = 0.0         # 0-360
    battery_percent: float = 100.0
    battery_voltage: float = 14.8
    timestamp: float = 0.0

    def to_dict(self) -> dict:
        return {
            "connected": self.connected,
            "armed": self.armed,
            "mode": self.mode,
            "position": self.position.to_dict(),
            "gps": self.gps.to_dict(),
            "altitude_agl_m": self.altitude_agl,
            "velocity": {
                "x": self.velocity_x,
                "y": self.velocity_y,
                "z": self.velocity_z,
                "speed_ms": self.speed,
            },
            "heading_deg": self.heading_deg,
            "battery_percent": self.battery_percent,
            "battery_voltage": self.battery_voltage,
            "timestamp": self.timestamp,
        }


# ============================================================
#  MOCK DRONE (always available)
# ============================================================

class MockDrone:
    """
    Simulated drone that produces realistic telemetry.
    Used when AirSim is not installed or not running.
    """

    def __init__(self, config: Optional[Dict] = None):
        cfg = config or {}
        self._state = DroneState()
        self._state.mode = "MOCK"
        self._state.altitude_agl = cfg.get("default_altitude_m", 30.0)
        self._state.gps.latitude = cfg.get("gps_origin_lat", 24.7136)
        self._state.gps.longitude = cfg.get("gps_origin_lon", 46.6753)
        self._state.gps.altitude = cfg.get("gps_origin_alt", 612.0) + self._state.altitude_agl
        self._state.battery_voltage = cfg.get("battery_voltage", 14.8)
        self._discharge_rate = cfg.get("discharge_rate_per_second", 0.002)
        self._start_time = None
        self._patrol_angle = 0.0
        self._patrol_radius = 50.0  # meters
        self._connected = False

    def connect(self) -> bool:
        self._connected = True
        self._state.connected = True
        self._state.armed = True
        self._start_time = time.time()
        logger.info("[MockDrone] Connected (simulation mode)")
        return True

    def disconnect(self):
        self._connected = False
        self._state.connected = False
        self._state.armed = False
        logger.info("[MockDrone] Disconnected")

    def is_connected(self) -> bool:
        return self._connected

    def get_state(self) -> DroneState:
        """Generate a realistic evolving drone state."""
        if not self._connected:
            return self._state

        now = time.time()
        elapsed = now - self._start_time
        self._state.timestamp = now

        # Simulate circular patrol pattern
        self._patrol_angle += 0.01
        self._state.position.x = self._patrol_radius * math.cos(self._patrol_angle)
        self._state.position.y = self._patrol_radius * math.sin(self._patrol_angle)
        self._state.position.z = -(self._state.altitude_agl + random.uniform(-0.3, 0.3))

        # Velocity (tangential to circle)
        speed = 3.0 + random.uniform(-0.5, 0.5)
        self._state.velocity_x = -speed * math.sin(self._patrol_angle)
        self._state.velocity_y = speed * math.cos(self._patrol_angle)
        self._state.velocity_z = random.uniform(-0.1, 0.1)
        self._state.speed = math.sqrt(
            self._state.velocity_x ** 2 +
            self._state.velocity_y ** 2 +
            self._state.velocity_z ** 2
        )

        # Heading
        self._state.heading_deg = (math.degrees(self._patrol_angle) + 90) % 360

        # GPS drift
        self._state.gps.latitude += random.uniform(-0.000001, 0.000001)
        self._state.gps.longitude += random.uniform(-0.000001, 0.000001)
        self._state.gps.altitude = 612.0 + self._state.altitude_agl

        # Battery drain
        self._state.battery_percent = max(
            0.0,
            100.0 - (elapsed * self._discharge_rate * 100)
        )
        self._state.battery_voltage = 14.8 * (self._state.battery_percent / 100.0)

        return self._state


# ============================================================
#  AIRSIM DRONE (requires AirSim)
# ============================================================

class AirSimDrone:
    """
    Real AirSim drone connector.
    Only instantiated if the airsim package is available.
    """

    def __init__(self, config: Optional[Dict] = None):
        if not AIRSIM_AVAILABLE:
            raise RuntimeError("AirSim package is not installed. pip install airsim")

        cfg = config or {}
        self._ip = cfg.get("airsim_ip", "127.0.0.1")
        self._port = cfg.get("airsim_port", 41451)
        self._vehicle = cfg.get("vehicle_name", "SecureSightDrone")
        self._client = None
        self._state = DroneState(mode="AIRSIM")

    def connect(self) -> bool:
        try:
            self._client = airsim.MultirotorClient(ip=self._ip, port=self._port)
            self._client.confirmConnection()
            self._client.enableApiControl(True, vehicle_name=self._vehicle)
            self._client.armDisarm(True, vehicle_name=self._vehicle)
            self._state.connected = True
            self._state.armed = True
            logger.info(f"[AirSimDrone] Connected to {self._ip}:{self._port}")
            return True
        except Exception as e:
            logger.error(f"[AirSimDrone] Connection failed: {e}")
            self._state.connected = False
            return False

    def disconnect(self):
        if self._client:
            try:
                self._client.armDisarm(False, vehicle_name=self._vehicle)
                self._client.enableApiControl(False, vehicle_name=self._vehicle)
            except Exception:
                pass
        self._state.connected = False
        self._state.armed = False
        logger.info("[AirSimDrone] Disconnected")

    def is_connected(self) -> bool:
        return self._state.connected

    def get_state(self) -> DroneState:
        if not self._client or not self._state.connected:
            return self._state

        try:
            ks = self._client.getMultirotorState(vehicle_name=self._vehicle).kinematics_estimated
            pos = ks.position
            vel = ks.linear_velocity

            self._state.position = DronePosition(
                x=pos.x_val, y=pos.y_val, z=pos.z_val
            )
            self._state.altitude_agl = abs(pos.z_val)
            self._state.velocity_x = vel.x_val
            self._state.velocity_y = vel.y_val
            self._state.velocity_z = vel.z_val
            self._state.speed = math.sqrt(
                vel.x_val ** 2 + vel.y_val ** 2 + vel.z_val ** 2
            )

            gps = self._client.getGpsData(vehicle_name=self._vehicle)
            self._state.gps = DroneGPS(
                latitude=gps.gnss.geo_point.latitude,
                longitude=gps.gnss.geo_point.longitude,
                altitude=gps.gnss.geo_point.altitude,
            )

            self._state.timestamp = time.time()
        except Exception as e:
            logger.warning(f"[AirSimDrone] State read error: {e}")

        return self._state


# ============================================================
#  UNIFIED CONNECTOR (auto-selects backend)
# ============================================================

class DroneConnector:
    """
    Unified drone interface.
    Automatically selects AirSim if available and connectable,
    otherwise falls back to MockDrone.
    """

    def __init__(self, config: Optional[Dict] = None, force_mock: bool = False):
        self._config = config or {}
        self._force_mock = force_mock
        self._backend = None
        self._backend_name = "none"

    def connect(self) -> bool:
        # Try AirSim first (unless forced mock)
        if not self._force_mock and AIRSIM_AVAILABLE:
            logger.info("[DroneConnector] AirSim detected -- attempting connection...")
            try:
                backend = AirSimDrone(self._config)
                if backend.connect():
                    self._backend = backend
                    self._backend_name = "airsim"
                    print("[SecureSight] [OK] Connected to AirSim drone")
                    return True
            except Exception as e:
                logger.warning(f"[DroneConnector] AirSim connection failed: {e}")

        # Fallback to mock
        logger.info("[DroneConnector] Using MockDrone (simulation mode)")
        self._backend = MockDrone(self._config)
        self._backend.connect()
        self._backend_name = "mock"
        print("[SecureSight] [OK] MockDrone active (AirSim not available)")
        return True

    def disconnect(self):
        if self._backend:
            self._backend.disconnect()
        self._backend = None
        self._backend_name = "none"

    def is_connected(self) -> bool:
        return self._backend is not None and self._backend.is_connected()

    def get_state(self) -> DroneState:
        if self._backend:
            return self._backend.get_state()
        return DroneState()

    @property
    def backend_name(self) -> str:
        return self._backend_name

    @property
    def is_mock(self) -> bool:
        return self._backend_name == "mock"

    def __repr__(self):
        return f"<DroneConnector backend={self._backend_name} connected={self.is_connected()}>"
