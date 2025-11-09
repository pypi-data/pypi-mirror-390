from __future__ import annotations

from typing import Any

from .client.models.unit_response_data import UnitResponseData
from .utils.temperature import normalize_temperature_fields

_ORIGINAL_UNIT_RESPONSE_DATA_FROM_DICT = UnitResponseData.from_dict.__func__


def _patched_unit_response_data_from_dict(cls, obj: Any):
    if isinstance(obj, dict):
        obj = normalize_temperature_fields(obj)
    return _ORIGINAL_UNIT_RESPONSE_DATA_FROM_DICT(cls, obj)


UnitResponseData.from_dict = classmethod(_patched_unit_response_data_from_dict)
