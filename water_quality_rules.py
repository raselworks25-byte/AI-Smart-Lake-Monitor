from __future__ import annotations

from typing import Any

WATER_QUALITY_RULES = {
    "clean": {"tds_max": 90, "turbidity_min": 3.0},
    "dirty": {"tds_min": 170, "turbidity_max": 2.0},
    "temperature": 35,
}


def classify_water_quality(tds: Any, turbidity: Any) -> str:
    try:
        numeric_tds = float(tds)
        numeric_turbidity = float(turbidity)
    except (TypeError, ValueError):
        return "Moderate"

    if numeric_tds <= WATER_QUALITY_RULES["clean"]["tds_max"] and numeric_turbidity > WATER_QUALITY_RULES["clean"]["turbidity_min"]:
        return "Good"
    if numeric_tds >= WATER_QUALITY_RULES["dirty"]["tds_min"] and numeric_turbidity <= WATER_QUALITY_RULES["dirty"]["turbidity_max"]:
        return "Poor"
    return "Moderate"
