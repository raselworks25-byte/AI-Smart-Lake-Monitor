from __future__ import annotations

import argparse
import importlib
import json
import os
import time
from datetime import datetime
from io import BytesIO
from typing import Any

import requests

serial = None
try:
    serial = importlib.import_module("serial")
except Exception:  # pragma: no cover - optional on non-Pi environments
    serial = None

cv2 = None
try:
    cv2 = importlib.import_module("cv2")
except Exception:  # pragma: no cover - optional on non-Pi environments
    cv2 = None

from water_quality_rules import classify_water_quality


BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000").rstrip("/")
INGEST_API_KEY = os.getenv("INGEST_API_KEY", "")
DEVICE_ID = os.getenv("DEVICE_ID", "pi-01")
CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", "0"))
FRAME_JPEG_QUALITY = int(os.getenv("FRAME_JPEG_QUALITY", "85"))
TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))
SERIAL_PORT = os.getenv("SERIAL_PORT", "")
SERIAL_BAUDRATE = int(os.getenv("SERIAL_BAUDRATE", "115200"))
SERIAL_TIMEOUT = float(os.getenv("SERIAL_TIMEOUT", "2"))

HEADERS = {"X-INGEST-TOKEN": INGEST_API_KEY} if INGEST_API_KEY else {}


def iso_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat()


def _parse_serial_payload(line: str) -> dict[str, Any]:
    text = line.strip()
    if not text:
        return {}

    try:
        payload = json.loads(text)
        if isinstance(payload, dict):
            return payload
    except json.JSONDecodeError:
        pass

    payload: dict[str, Any] = {}
    for part in text.split(";"):
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        payload[key.strip()] = value.strip()
    return payload


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def read_serial_sensor_sample() -> dict[str, Any] | None:
    if not SERIAL_PORT or serial is None:
        return None

    try:
        with serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT) as device:
            raw_line = device.readline().decode("utf-8", errors="ignore").strip()
    except Exception as exc:
        print(f"serial read failed: {exc}")
        return None

    payload = _parse_serial_payload(raw_line)
    if not payload:
        return None

    tds = _to_float(payload.get("tds") or payload.get("TDS") or payload.get("tds_ppm"), 0.0)
    turbidity = _to_float(payload.get("turbidity") or payload.get("NTU"), 0.0)
    temperature = _to_float(payload.get("temperature") or payload.get("temp"), 0.0)

    if not tds and not turbidity and not temperature:
        return None

    status = payload.get("status")
    if not status:
        status = classify_water_quality(tds, turbidity)

    sample = {
        "device_id": payload.get("device_id", DEVICE_ID),
        "timestamp": payload.get("timestamp", iso_now()),
        "tds": _to_int(tds),
        "turbidity": round(turbidity, 2),
        "temperature": round(temperature, 2),
        "status": status,
    }
    return sample


def read_water_sample() -> dict[str, Any]:
    serial_sample = read_serial_sensor_sample()
    if serial_sample is not None:
        return serial_sample

    tds = 182
    turbidity = 4.2
    temperature = 28.1
    status = classify_water_quality(tds, turbidity)
    return {
        "device_id": DEVICE_ID,
        "timestamp": iso_now(),
        "tds": tds,
        "turbidity": turbidity,
        "temperature": temperature,
        "status": status,
    }


def detect_objects_from_frame(_frame) -> dict[str, Any]:
    """Replace this stub with your local object-detection model output."""
    return {
        "class_id": 0,
        "class_name": "Plastic Bottle",
        "object_type": "Plastic Bottle",
        "bottle_count": 1,
        "debris_count": 0,
        "total_objects": 1,
        "confidence_score": 0.94,
    }


def capture_frame() -> bytes | None:
    if cv2 is None:
        return None

    camera = cv2.VideoCapture(CAMERA_INDEX)
    try:
        ok, frame = camera.read()
        if not ok:
            return None
        ok, encoded = cv2.imencode(
            ".jpg",
            frame,
            [int(cv2.IMWRITE_JPEG_QUALITY), FRAME_JPEG_QUALITY],
        )
        if not ok:
            return None
        return encoded.tobytes()
    finally:
        camera.release()


def post_json(path: str, payload: dict[str, Any]) -> requests.Response:
    return requests.post(
        f"{BASE_URL}{path}",
        json=payload,
        headers=HEADERS,
        timeout=TIMEOUT,
    )


def post_frame(frame_bytes: bytes | None, payload: dict[str, Any]) -> requests.Response | None:
    if not frame_bytes:
        return None

    files = {
        "image": ("frame.jpg", BytesIO(frame_bytes), "image/jpeg"),
    }
    return requests.post(
        f"{BASE_URL}/api/ingest/frame",
        data=payload,
        files=files,
        headers=HEADERS,
        timeout=TIMEOUT,
    )


def send_once() -> None:
    frame_bytes = capture_frame()
    detection_payload = {
        "device_id": DEVICE_ID,
        "timestamp": iso_now(),
        **detect_objects_from_frame(frame_bytes),
    }
    water_payload = read_water_sample()

    water_response = post_json("/api/ingest/water", water_payload)
    detection_response = post_json("/api/ingest/detection", detection_payload)
    frame_response = post_frame(frame_bytes, {"device_id": DEVICE_ID, "timestamp": iso_now()})

    print("water:", water_response.status_code, water_response.text)
    print("detection:", detection_response.status_code, detection_response.text)
    if frame_response is not None:
        print("frame:", frame_response.status_code, frame_response.text)
    else:
        print("frame: skipped (no camera frame captured)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Send Raspberry Pi sensor, detection, and frame data to the web app.")
    parser.add_argument("--once", action="store_true", help="Send one sample and exit")
    parser.add_argument("--interval", type=int, default=5, help="Seconds between sends when running continuously")
    args = parser.parse_args()

    if args.once:
        send_once()
        return

    while True:
        try:
            send_once()
        except Exception as exc:
            print(f"send failed: {exc}")
        time.sleep(max(1, args.interval))


if __name__ == "__main__":
    main()
