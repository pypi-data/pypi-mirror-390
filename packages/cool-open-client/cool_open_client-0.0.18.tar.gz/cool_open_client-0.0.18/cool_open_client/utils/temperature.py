from __future__ import annotations

from typing import Any, Dict, Mapping, Tuple

TEMPERATURE_FIELDS: Tuple[str, ...] = (
    "ambientTemperature",
    "activeSetpoint",
    "setpoint",
)


def round_temperature_value(value: Any) -> Any:
    """Round float temperature values to the nearest int."""
    if isinstance(value, (int, float)):
        return int(round(float(value)))
    return value


def normalize_temperature_fields(
    payload: Mapping[str, Any] | None,
    fields: Tuple[str, ...] = TEMPERATURE_FIELDS,
) -> Mapping[str, Any] | None:
    """Return a copy of the payload with selected temperature fields rounded to ints."""
    if payload is None or not isinstance(payload, Mapping):
        return payload

    normalized: Mapping[str, Any] | Dict[str, Any] = payload

    for field in fields:
        value = payload.get(field)
        rounded = round_temperature_value(value)
        if rounded != value:
            if normalized is payload:
                normalized = dict(payload)
            normalized[field] = rounded

    return normalized
