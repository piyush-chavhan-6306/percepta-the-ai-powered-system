"""
PERCEPTA ONLINE CAMERA SOURCE ABSTRACTION
Provides a unified, extensible interface for all surveillance video inputs:
CameraSource
├── VideoFileSource (Local recordings / VIRAT demo source)
├── RTSPSource (Live edge H.264/H.265 network streams)
└── FutureCameraSource (IP cameras, WebRTC, secondary sensor payloads)
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import cv2
import numpy as np


class CameraType(str, Enum):
    RGB = "RGB"
    IR = "IR"
    THERMAL = "THERMAL"


class SourceProtocol(str, Enum):
    VIDEO_FILE = "video_file"
    RTSP = "rtsp"
    IP_CAMERA = "ip_camera"
    WEBRTC = "webrtc"


@dataclass
class SourceFrame:
    camera_id: str
    frame_number: int
    timestamp: datetime
    image: np.ndarray  # BGR numpy array
    width: int
    height: int
    fps: float
    source_type: SourceProtocol
    camera_type: CameraType = CameraType.RGB
    is_demo: bool = False


class CameraSource(ABC):
    """Abstract Base Class for all camera feed ingestion sources."""

    def __init__(
        self,
        camera_id: str,
        name: str,
        camera_type: CameraType = CameraType.RGB,
        location: str = "Sector 7 Perimeter",
        is_demo: bool = False,
    ):
        self.camera_id = camera_id
        self.name = name
        self.camera_type = camera_type
        self.location = location
        self.is_demo = is_demo
        self._is_active = False

    @property
    def is_active(self) -> bool:
        return self._is_active

    @abstractmethod
    async def open(self) -> bool:
        """Open connection or stream resource."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Release underlying hardware/network/file handle."""
        pass

    @abstractmethod
    async def read_frame(self) -> Optional[SourceFrame]:
        """Fetch next incoming frame."""
        pass

    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """Return operational telemetry and resolution metrics."""
        pass


class VideoFileSource(CameraSource):
    """Ingests video from local files (e.g. virat_cctv.mp4 demo source)."""

    def __init__(
        self,
        camera_id: str,
        name: str,
        file_path: str,
        camera_type: CameraType = CameraType.RGB,
        location: str = "Border Post Alpha (Optical CCTV)",
        is_demo: bool = False,
        loop: bool = True,
    ):
        super().__init__(camera_id=camera_id, name=name, camera_type=camera_type, location=location, is_demo=is_demo)
        self.file_path = str(file_path)
        self.loop = loop
        self._cap: Optional[cv2.VideoCapture] = None
        self._frame_count = 0
        self._fps = 25.0
        self._width = 640
        self._height = 480

    async def open(self) -> bool:
        p = Path(self.file_path)
        if not p.is_file():
            return False
        self._cap = cv2.VideoCapture(str(p))
        if not self._cap.isOpened():
            return False
        self._fps = float(self._cap.get(cv2.CAP_PROP_FPS) or 25.0)
        self._width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 640)
        self._height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480)
        self._is_active = True
        return True

    async def close(self) -> None:
        if self._cap:
            self._cap.release()
            self._cap = None
        self._is_active = False

    async def read_frame(self) -> Optional[SourceFrame]:
        if not self._cap or not self._cap.isOpened():
            return None
        ret, frame = self._cap.read()
        if not ret:
            if self.loop:
                self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self._cap.read()
            if not ret or frame is None:
                return None
        self._frame_count += 1
        return SourceFrame(
            camera_id=self.camera_id,
            frame_number=self._frame_count,
            timestamp=datetime.now(timezone.utc),
            image=frame,
            width=frame.shape[1],
            height=frame.shape[0],
            fps=self._fps,
            source_type=SourceProtocol.VIDEO_FILE,
            camera_type=self.camera_type,
            is_demo=self.is_demo,
        )

    def get_info(self) -> Dict[str, Any]:
        return {
            "camera_id": self.camera_id,
            "name": self.name,
            "source_type": SourceProtocol.VIDEO_FILE.value,
            "camera_type": self.camera_type.value,
            "location": self.location,
            "file_path": self.file_path,
            "is_demo": self.is_demo,
            "is_active": self._is_active,
            "width": self._width,
            "height": self._height,
            "fps": self._fps,
            "frame_count": self._frame_count,
        }


class RTSPSource(CameraSource):
    """Ingests live video over RTSP/TCP/UDP."""

    def __init__(
        self,
        camera_id: str,
        name: str,
        rtsp_url: str,
        camera_type: CameraType = CameraType.RGB,
        location: str = "Forward Surveillance Post",
    ):
        super().__init__(camera_id=camera_id, name=name, camera_type=camera_type, location=location, is_demo=False)
        self.rtsp_url = rtsp_url
        self._cap: Optional[cv2.VideoCapture] = None
        self._frame_count = 0

    async def open(self) -> bool:
        self._cap = cv2.VideoCapture(self.rtsp_url)
        self._is_active = self._cap.isOpened() if self._cap else False
        return self._is_active

    async def close(self) -> None:
        if self._cap:
            self._cap.release()
            self._cap = None
        self._is_active = False

    async def read_frame(self) -> Optional[SourceFrame]:
        if not self._cap or not self._cap.isOpened():
            return None
        ret, frame = self._cap.read()
        if not ret or frame is None:
            return None
        self._frame_count += 1
        return SourceFrame(
            camera_id=self.camera_id,
            frame_number=self._frame_count,
            timestamp=datetime.now(timezone.utc),
            image=frame,
            width=frame.shape[1],
            height=frame.shape[0],
            fps=25.0,
            source_type=SourceProtocol.RTSP,
            camera_type=self.camera_type,
            is_demo=False,
        )

    def get_info(self) -> Dict[str, Any]:
        return {
            "camera_id": self.camera_id,
            "name": self.name,
            "source_type": SourceProtocol.RTSP.value,
            "camera_type": self.camera_type.value,
            "location": self.location,
            "rtsp_url": self.rtsp_url,
            "is_demo": False,
            "is_active": self._is_active,
        }


class FutureCameraSource(CameraSource):
    """Stub/contract for future sensor streams (IP cameras, WebRTC, thermal payloads)."""

    def __init__(
        self,
        camera_id: str,
        name: str,
        stream_protocol: str = "webrtc",
        camera_type: CameraType = CameraType.RGB,
        location: str = "Unassigned Sector",
    ):
        super().__init__(camera_id=camera_id, name=name, camera_type=camera_type, location=location, is_demo=False)
        self.stream_protocol = stream_protocol

    async def open(self) -> bool:
        self._is_active = True
        return True

    async def close(self) -> None:
        self._is_active = False

    async def read_frame(self) -> Optional[SourceFrame]:
        return None

    def get_info(self) -> Dict[str, Any]:
        return {
            "camera_id": self.camera_id,
            "name": self.name,
            "source_type": self.stream_protocol,
            "camera_type": self.camera_type.value,
            "location": self.location,
            "status": "NOT_CONNECTED",
            "is_demo": False,
        }
