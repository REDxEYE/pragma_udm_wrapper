import abc
import ctypes
from functools import cache
from typing import Optional

from .wrapper import (
    udm_get_property_name, udm_get_property_path,
    udm_get_property_type,

    UdmType, nullptr, udm_read_property_string, udm_property_to_ascii, udm_property_to_json
)


class IProperty(abc.ABC):

    def __init__(self, prop_p: int):
        self._prop_p = ctypes.c_void_p(prop_p)
        self._lazy_name: Optional[str] = None
        self._lazy_path: Optional[str] = None
        self._lazy_b_path: Optional[str] = None
        self._lazy_type: Optional[UdmType] = None

    @property
    def name(self):
        if self._lazy_name is None:
            self._lazy_name = udm_get_property_name(self._prop_p).decode('utf8')
        return self._lazy_name

    @property
    def path(self):
        if self._lazy_path is None:
            self._lazy_path = udm_get_property_path(self._prop_p).decode('utf8')
        return self._lazy_path

    @property
    def _b_path(self):
        if self._lazy_b_path is None:
            self._lazy_b_path = udm_get_property_path(self._prop_p)
        return self._lazy_b_path

    @property
    def type(self):
        if self._lazy_type is None:
            self._lazy_type = udm_get_property_type(self._prop_p, nullptr)
        return self._lazy_type

    @property
    def prop_pointer(self):
        return self._prop_p

    def __hash__(self) -> int:
        return self._prop_p.value

    def __eq__(self, o: 'IProperty') -> bool:
        return isinstance(o, IProperty) and self._prop_p.value == o._prop_p.value

    def __ne__(self, o: 'IProperty') -> bool:
        return isinstance(o, IProperty) and self._prop_p.value != o._prop_p.value

    def to_ascii(self) -> str:
        value = udm_property_to_ascii(self._prop_p, self.path.encode('ascii'))
        if value:
            return value.decode('utf8')

    def to_json(self) -> str:
        value = udm_property_to_json(self._prop_p)
        if value:
            return value.decode('utf8')

    def __repr__(self):
        return f'<UdmProperty {self.path!r} of type {self.type.name!r}>'
