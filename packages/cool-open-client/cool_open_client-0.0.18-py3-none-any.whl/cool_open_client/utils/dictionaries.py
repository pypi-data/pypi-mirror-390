from __future__ import annotations
from collections.abc import Mapping
from bidict import bidict, OnDup, OnDupAction
from abc import abstractmethod, ABC
from typing import Any, Dict, List, Optional, Union


def create_types_class(types: Union[Dict[str, str], List[str]]) -> BaseTypes:
    if isinstance(types, dict):
        return DictTypes(types)

    return ListTypes(types)


class BaseTypes(ABC):
    def __init__(self, data: Union[Dict[str, str], List[str]]) -> None:
        self.data = data

    @abstractmethod
    def get(self, key: Union[str, int]) -> Optional[str]:
        pass


class DictTypes(BaseTypes):
    """This class is used to convert between the integer values used by the API and the string values used by the user.
       It is implemented as a bidirectional dictionary, but with some custom logic to handle duplicate keys and values.
       The API will return duplicate keys, but the user should not be able to set duplicate values.
    """
    
    def __init__(self, data: Union[Dict[str, Any], Any]) -> None:
        """This is an initializer for the class.
           Converts the dictionary to a bidict, and converts the keys to integers.
        """
        self.data = bidict()
        self.data.on_dup = OnDup(key=OnDupAction.RAISE, val=OnDupAction.DROP_NEW)
        normalized_data = self._normalize_mapping(data)
        entries = []
        for key, value in normalized_data.items():
            parsed_key = self._parse_key(key)
            parsed_value = self._parse_value(value)
            if parsed_key is not None and parsed_value is not None:
                entries.append((parsed_key, parsed_value))
        self.data.putall(entries, on_dup=OnDup(key=OnDupAction.DROP_NEW, val=OnDupAction.DROP_NEW))

    def get(self, key: Union[str, int]) -> Optional[str]:
        """
        Return the value associated with the given key.
        """
        parsed_key = self._parse_key(key)
        if parsed_key is None:
            return None
        return self.data.get(parsed_key)

    def get_inverse(self, key: str) -> Union[int, str, None]:
        """
        This method returns the key associated with the given value.
        :param key: The value to look up.
        :return: The key associated with the given value.
        """
        return self.data.inverse.get(key)

    def _normalize_mapping(self, payload: Any) -> Dict[str, Any]:
        if payload is None:
            return {}
        if isinstance(payload, Mapping):
            return dict(payload)
        additional = getattr(payload, "additional_properties", None)
        if isinstance(additional, Mapping) and additional:
            return dict(additional)
        if hasattr(payload, "model_dump"):
            dumped = payload.model_dump(by_alias=True, exclude_none=True)
            if isinstance(dumped, Mapping) and dumped:
                return dict(dumped)
        if hasattr(payload, "to_dict"):
            dumped = payload.to_dict()
            if isinstance(dumped, Mapping) and dumped:
                return dict(dumped)
        return {}

    def _parse_key(self, key: Any) -> int:
        try:
            return int(key)
        except (TypeError, ValueError):
            return None

    def _parse_value(self, value: Any) -> str:
        if isinstance(value, str):
            return value

        if isinstance(value, Mapping):
            for candidate_key in ("mode", "status", "value", "name", "label"):
                candidate_value = value.get(candidate_key)
                if isinstance(candidate_value, str):
                    return candidate_value
            for candidate_value in value.values():
                if isinstance(candidate_value, str):
                    return candidate_value

        additional = getattr(value, "additional_properties", None)
        if isinstance(additional, Mapping):
            return self._parse_value(additional)

        if hasattr(value, "model_dump"):
            dumped = value.model_dump(by_alias=True, exclude_none=True)
            if isinstance(dumped, Mapping):
                return self._parse_value(dumped)

        if hasattr(value, "to_dict"):
            dumped = value.to_dict()
            if isinstance(dumped, Mapping):
                return self._parse_value(dumped)

        if value is not None:
            return str(value)

        return None

class ListTypes(BaseTypes):
    def get(self, key: Union[int, str]) -> Optional[str]:
        index = key
        if isinstance(key, str):
            try:
                index = int(key)
            except ValueError:
                return None
        try:
            return self.data[index]
        except (IndexError, TypeError):
            return None
