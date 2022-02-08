from typing import Any

from .wrapper import *
from .type_info import udm_to_np, udm_type_to_ctypes
import ctypes
import numpy as np


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

    def _read_value(self, buffer, item_type: UdmType, byte_size: int):
        return udm_read_property(self._prop_p, nullptr, item_type, buffer, byte_size)

    def _read_array_value(self, buffer, item_type: UdmType, byte_size: int, count: int, start: int = 0):
        return udm_read_array_property(self._prop_p, nullptr, item_type, buffer, byte_size, start, count)

    def _get_value(self, type_override: UdmType = None):
        self_type = type_override or self.type
        if UdmType.String <= self_type <= UdmType.Utf8String:
            value = udm_read_property_string(self._prop_p, nullptr, b'\xBA\xAD\xF0\x0D')
            if value == b'\xBA\xAD\xF0\x0D':
                raise RuntimeError(f'Failed to read string from "{self.path}"!')
            return value.decode('utf-8')
        # elif self_type == UdmType.BlobLz4 or self_type == UdmType.Blob:
        #     value = udm_read_property_string(self._prop_p, nullptr, b'\xBA\xAD\xF0\x0D')
        #     if value == b'\xBA\xAD\xF0\x0D':
        #         raise RuntimeError(f'Failed to read string from "{self.path}"!')
        #     return value
        elif UdmType.Int8 <= self_type <= UdmType.Boolean:
            base_type = udm_type_to_ctypes[self_type]
            buffer = base_type(0)
            if self._read_value(ctypes.byref(buffer), self_type, 1 * ctypes.sizeof(buffer)):
                return buffer.value
        elif UdmType.Vector2 <= self_type <= UdmType.Mat3x4 or UdmType.Half <= self_type <= UdmType.Vector4i:
            base_type, item_count = udm_to_np[self_type]
            array = np.zeros(item_count, dtype=base_type)
            if self._read_value(array.ctypes.data, self_type, item_count * array.itemsize):
                return array
        else:
            raise NotImplementedError(f"Can't read \"{self_type}\" type")

    def _get_array_value(self):
        if UdmType.String <= self.array_type <= UdmType.Utf8String:
            value_count = ctypes.c_uint32(0)
            pointer = udm_read_array_property_string(self._prop_p, nullptr, ctypes.byref(value_count))
            return [pointer[i].decode('utf8') for i in range(value_count.value)]
        elif UdmType.Int8 <= self.array_type <= UdmType.Mat3x4 or UdmType.Half <= self.type <= UdmType.Vector4i:
            base_type, item_count = udm_to_np[self.array_type]
            array_len = len(self)
            if item_count > 1:
                array = np.zeros((array_len, item_count), dtype=base_type)
            else:
                array = np.zeros((array_len,), dtype=base_type)
            array_bytesize = array_len * item_count * array.itemsize
            self._read_array_value(array.ctypes.data, self.array_type, array_bytesize, array_len)
            return array
        elif self.array_type == UdmType.Element:
            return list(self)

    def _get_struct_member_names(self):
        value_count = ctypes.c_uint32(0)
        pointer = udm_get_struct_member_names(self._prop_p, nullptr, ctypes.byref(value_count))
        return [pointer[i].decode('utf8') for i in range(value_count.value)]

    def _get_struct_member_types(self):
        value_count = ctypes.c_uint32(0)
        pointer = udm_get_struct_member_types(self._prop_p, nullptr, ctypes.byref(value_count))
        return [UdmType(pointer[i]) for i in range(value_count.value)]

    def _get_struct_array_value(self):
        member_names = self._get_struct_member_names()
        member_types = self._get_struct_member_types()
        dtype_info = []
        for mname, mtype in zip(member_names, member_types):
            np_type, sub_item_count = udm_to_np[mtype]
            dtype_info.append((mname, np_type, (sub_item_count,)))
        array_dtype = np.dtype(dtype_info)
        item_count = len(self)
        array = np.zeros((item_count,), array_dtype)
        if self._read_value(array.ctypes.data, self.type, item_count * array.itemsize):
            return array
        pass
