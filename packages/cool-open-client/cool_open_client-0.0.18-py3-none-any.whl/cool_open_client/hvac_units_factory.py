from __future__ import annotations

from typing import Any, Dict, List

from .cool_automation_client import CoolAutomationClient
from .unit import HVACUnit
from .client.models.unit_response_data import UnitResponseData
from .utils.dict_to_model import dict_to_model


class HVACUnitsFactory:
    @classmethod
    async def create(cls, token: str = None):
        if token is None:
            raise ValueError("token is required")

        client = await CoolAutomationClient.create(token)
        return cls(client)

    def __init__(self, client=None, event_loop=None) -> None:
        self._client = client
        self._event_loop = event_loop

    async def generate_units_from_api(self) -> List[HVACUnit]:
        units = await self._client.get_controllable_units()
        hvac_units: List[HVACUnit] = []
        units_payload = self._extract_mapping(units.data)

        for unit_id, payload in units_payload.items():
            raw_unit = self._ensure_dict(payload)
            if isinstance(raw_unit, dict) and raw_unit.get("type") not in (None, 1):
                continue

            try:
                unit = dict_to_model(UnitResponseData, payload)
            except TypeError:
                continue

            temperature_limits = {}
            if unit.temperature_limits is not None:
                temperature_limits = unit.temperature_limits.to_dict()

            supported_fan_modes = [
                value
                for value in (
                    self._client.fan_modes.get(mode)
                    for mode in (unit.supported_fan_modes or [])
                )
                if value is not None
            ]
            supported_operation_modes = [
                value
                for value in (
                    self._client.operation_modes.get(mode)
                    for mode in (unit.supported_operation_modes or [])
                )
                if value is not None
            ]
            supported_operation_statuses = [
                value
                for value in (
                    self._client.operation_statuses.get(status)
                    for status in (unit.supported_operation_statuses or [])
                )
                if value is not None
            ]
            supported_swing_modes = [
                value
                for value in (
                    self._client.swing_modes.get(mode)
                    for mode in (unit.supported_swing_modes or [])
                )
                if value is not None
            ]

            hvac_unit = HVACUnit(
                unit.id or unit_id,
                unit.name or unit_id,
                active_fan_mode=self._client.fan_modes.get(unit.active_fan_mode),
                active_operation_mode=self._client.operation_modes.get(unit.active_operation_mode),
                active_operation_status=self._client.operation_statuses.get(unit.active_operation_status),
                active_setpoint=unit.active_setpoint,
                active_swing_mode=self._client.swing_modes.get(unit.active_swing_mode),
                ambient_temperature=unit.ambient_temperature,
                temerature_range=temperature_limits,
                supported_fan_modes=supported_fan_modes,
                supported_operation_modes=supported_operation_modes,
                supported_operation_statuses=supported_operation_statuses,
                supported_swing_modes=supported_swing_modes,
                is_half_degree=bool(unit.is_half_c_degree_enabled),
                client=self._client,
                event_loop=self._event_loop,
            )
            hvac_units.append(hvac_unit)
        return hvac_units

    @staticmethod
    def _extract_mapping(payload: Any) -> Dict[str, Any]:
        if payload is None:
            return {}
        if isinstance(payload, dict):
            return payload
        additional = getattr(payload, "additional_properties", None)
        if isinstance(additional, dict):
            return additional
        if hasattr(payload, "to_dict"):
            dumped = payload.to_dict()
            if isinstance(dumped, dict):
                return dumped
        return {}

    @staticmethod
    def _ensure_dict(payload: Any) -> Dict[str, Any]:
        if isinstance(payload, dict):
            return payload
        if hasattr(payload, "model_dump"):
            dumped = payload.model_dump(by_alias=True, exclude_none=True)
            if isinstance(dumped, dict):
                return dumped
        if hasattr(payload, "to_dict"):
            dumped = payload.to_dict()
            if isinstance(dumped, dict):
                return dumped
        return {}
