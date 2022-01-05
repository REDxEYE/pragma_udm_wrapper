import json
from typing import Any

from .wrapper import *
import ctypes


class BasicUdmProperty:

    def __init__(self, prop_p: int):
        self._prop_p = ctypes.c_void_p(prop_p)

    @property
    def type(self) -> UdmType:
        return udm_get_property_type(self._prop_p, nullptr)

    @property
    def array_type(self) -> UdmType:
        if self.type == UdmType.Array or self.type == UdmType.ArrayLz4:
            return udm_get_array_value_type(self._prop_p, nullptr)
        else:
            return UdmType.Invalid

    @property
    def name(self):
        return udm_get_property_name(self._prop_p).decode('utf8')

    @property
    def path(self):
        return udm_get_property_path(self._prop_p).decode('utf8')

    def __getitem__(self, item) -> 'BasicUdmProperty':
        if isinstance(item, int) and self.type == UdmType.Array:
            prop = udm_get_property_i(self._prop_p, item)
        elif isinstance(item, int) and self.type != UdmType.Array:
            raise NotImplementedError(f'UdmProperty "{self.path}" not an array. Type: "{self.type}"')

        elif isinstance(item, str):
            prop = udm_get_property(self._prop_p, item.encode('utf8'))
        else:
            raise NotImplementedError(
                f'UdmProperty "{self.path}" does not support indexing with {item} type: "{type(item)}"')
        if prop is None:
            raise IndexError(f'UdmProperty "{self.path}" does not have "{item}" property')
        return self.__class__(prop)

    def __contains__(self, item: str):
        prop = udm_get_property(self._prop_p, item.encode('utf8'))
        return prop is not None and prop != 0

    def get(self, item: str, default: Any = None):
        if item in self:
            return self[item]
        return default

    def to_string(self, default: str = ''):
        return udm_read_property_string(self._prop_p, nullptr, default.encode('utf8')).decode('utf8')

    def to_ascii(self) -> str:
        value = udm_property_to_ascii(self._prop_p, nullptr)
        if value:
            return value.decode('utf8')

    def to_json(self) -> str:
        value = udm_property_to_json(self._prop_p)
        if value:
            return value.decode('utf8')

    def to_dict(self):
        import json
        return json.loads(self.to_json())

    def __len__(self) -> int:
        if self.type == UdmType.Array or self.type == UdmType.ArrayLz4:
            return udm_get_array_size(self._prop_p, nullptr)
        elif self.type == UdmType.Element:
            return udm_get_property_child_count(self._prop_p, nullptr)

    def __iter__(self):
        for _, item in self.items():
            yield item

    def items(self):
        if self.type == UdmType.Element:
            iterator = udm_create_property_child_name_iterator(self._prop_p, nullptr)
            if not iterator:
                raise StopIteration
            name = udm_fetch_property_child_name(iterator)
            while name is not None:
                name_d = name.decode('utf8')
                yield name_d, self[name_d]
                name = udm_fetch_property_child_name(iterator)
        else:
            array_size = udm_get_array_size(self._prop_p, nullptr)
            for i in range(array_size):
                elem = udm_get_property_i(self._prop_p, i)
                if self.array_type == UdmType.Element:
                    yield i, self.__class__(elem)
                else:
                    yield i, elem

    @property
    def children(self):
        if (self.type == UdmType.Array or self.type == UdmType.ArrayLz4) and self.array_type == UdmType.Element:
            return {i: elem for i, elem in self.items()}
        elif self.type == UdmType.Element:
            return {name: elem for name, elem in self.items()}
        return {}

    def __repr__(self):
        if self.type == UdmType.Array or self.type == UdmType.ArrayLz4:
            prop_type = f"{self.type.name} of {self.array_type.name}"
        else:
            prop_type = self.type.name
        return f'<UdmProperty {self.path} of type "{prop_type}">'
