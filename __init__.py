import ctypes
import json
import typing
from typing import Union, Optional, List, Dict, Tuple

from .basic_property import BasicUdmProperty
from .type_info import udm_to_np, udm_type_to_ctypes
from .wrapper import *
import numpy as np


class UdmProperty(BasicUdmProperty):
    _return_value_on_lookup = True

    @classmethod
    def set_return_mode(cls, return_value):
        cls._return_value_on_lookup = return_value

    def __getitem__(self, item) -> Union['UdmProperty', typing.Any]:
        prop = typing.cast(UdmProperty, super().__getitem__(item))
        if (prop.type != UdmType.Array or prop.type != UdmType.Element) and self._return_value_on_lookup:
            return prop.get_value()
        return prop

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

    def get_value(self, type_override: UdmType = None):
        self_type = type_override or self.type
        if UdmType.String <= self_type <= UdmType.Mat3x4 or UdmType.Half <= self_type <= UdmType.Vector4i:
            return self._get_value(type_override)
        elif self_type == UdmType.Element:
            return self
        elif UdmType.Array <= self_type <= UdmType.ArrayLz4 and self.array_type != UdmType.Struct:
            return self._get_array_value()
        elif UdmType.Array <= self_type <= UdmType.ArrayLz4 and self.array_type == UdmType.Struct:
            return self._get_struct_array_value()


class UDM:
    def __init__(self, return_value_on_lookup=True):
        self._udm_data: ctypes.c_void_p = ctypes.c_void_p()
        UdmProperty.set_return_mode(return_value_on_lookup)

    def create(self, asset_type, version, clear_on_destroy: bool = True) -> bool:
        data = udm_create(asset_type.encode('utf8'), version, clear_on_destroy)
        self._udm_data = ctypes.c_void_p(data)
        return data is not None

    def load(self, filename: Union[str, Path], clear_on_destroy: bool = True) -> bool:
        data = udm_load(str(filename).encode('utf8'), clear_on_destroy)
        self._udm_data = ctypes.c_void_p(data)
        return data is not None

    def save(self, filename: Union[str, Path], binary: bool = True, ascii_flags: int = 0) -> bool:
        if binary and ascii_flags:
            raise RuntimeError(f'Ascii flags are not supposed to be used when binary mode is chosen')
        if binary:
            return udm_save_binary(self._udm_data, Path(filename).as_posix().encode('utf8'))
        else:
            return udm_save_ascii(self._udm_data, Path(filename).as_posix().encode('utf8'), ascii_flags)

    def destroy(self) -> None:
        if not self._udm_data or self._udm_data.value == 0:
            return
        udm_destroy_function(self._udm_data)
        self._udm_data.value = 0

    def __del__(self):
        if self._udm_data.value != 0:
            self.destroy()
            self._udm_data.value = 0

    @property
    def root(self) -> Optional[UdmProperty]:
        if not self._udm_data:
            return None
        return UdmProperty(udm_get_root_property(self._udm_data))
