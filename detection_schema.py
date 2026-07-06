from __future__ import annotations

from typing import Any

DETECTION_CLASSES: dict[int, str] = {
    0: "Plastic Bottle",
    1: "Debris",
}

DETECTION_CLASS_IDS = tuple(DETECTION_CLASSES.keys())
DETECTION_CLASS_NAMES = tuple(DETECTION_CLASSES.values())
DEFAULT_DETECTION_CLASS_ID = 1


def class_name_from_id(class_id: Any) -> str:
    try:
        normalized_id = int(class_id)
    except (TypeError, ValueError):
        normalized_id = DEFAULT_DETECTION_CLASS_ID
    return DETECTION_CLASSES.get(normalized_id, DETECTION_CLASSES[DEFAULT_DETECTION_CLASS_ID])


def class_id_from_payload(payload: dict[str, Any]) -> int:
    candidate = payload.get("class_id", payload.get("class", payload.get("label", payload.get("object_type", payload.get("class_name")))))
    if isinstance(candidate, str):
        stripped = candidate.strip()
        if stripped.isdigit():
            return int(stripped)
        reverse_lookup = {name.lower(): class_id for class_id, name in DETECTION_CLASSES.items()}
        return reverse_lookup.get(stripped.lower(), DEFAULT_DETECTION_CLASS_ID)
    try:
        normalized_id = int(candidate)
    except (TypeError, ValueError):
        normalized_id = DEFAULT_DETECTION_CLASS_ID
    return normalized_id if normalized_id in DETECTION_CLASSES else DEFAULT_DETECTION_CLASS_ID


def class_name_from_payload(payload: dict[str, Any]) -> str:
    class_id = class_id_from_payload(payload)
    return class_name_from_id(class_id)