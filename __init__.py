import ctypes
import json
import typing
from typing import Union, Optional, List, Dict, Tuple

from .basic_property import BasicUdmProperty
from .type_info import udm_to_np, udm_type_to_ctypes
from .wrapper import *
import numpy as np


class UdmProperty(BasicUdmProperty):

    def __getitem__(self, item) -> 'UdmProperty':
        return typing.cast(UdmProperty, super().__getitem__(item))

    def _read_value(self, buffer, item_type: UdmType, byte_size: int):
        return udm_read_property(self._prop_p, nullptr, item_type, buffer, byte_size)

    def _read_array_value(self, buffer, item_type: UdmType, byte_size: int, count: int, start: int = 0):
        return udm_read_array_property(self._prop_p, nullptr, item_type, buffer, byte_size, start, count)

    def _get_value(self):
        if UdmType.String <= self.type <= UdmType.Utf8String:
            value = udm_read_property_string(self._prop_p, nullptr, b'')
            return value.decode('utf-8')
        elif UdmType.Int8 <= self.type <= UdmType.Boolean:
            base_type = udm_type_to_ctypes[self.type]
            buffer = base_type(0)
            if self._read_value(ctypes.byref(buffer), self.type, 1 * ctypes.sizeof(buffer)):
                return buffer.value
        elif UdmType.Vector2 <= self.type <= UdmType.Mat3x4 or UdmType.Half <= self.type <= UdmType.Vector4i:
            base_type, item_count = udm_to_np[self.type]
            array = np.zeros(item_count, dtype=base_type)
            if self._read_value(array.ctypes.data, self.type, item_count * array.itemsize):
                return array
        else:
            raise NotImplementedError(f"Can't read \"{self.type}\" type")

    def _get_array_value(self):
        if UdmType.String <= self.array_type <= UdmType.Utf8String:
            value_count = ctypes.c_uint32(0)
            pointer = udm_read_array_property_string(self._prop_p, nullptr, ctypes.byref(value_count))
            return [pointer[i].decode('utf8') for i in range(value_count.value)]
        elif UdmType.Int8 <= self.array_type <= UdmType.Mat3x4 or UdmType.Half <= self.type <= UdmType.Vector4i:
            base_type, item_count = udm_to_np[self.array_type]
            array_len = len(self)
            array = np.zeros((array_len, item_count), dtype=base_type)
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

    def get_value(self):
        if UdmType.String <= self.type <= UdmType.Mat3x4 or UdmType.Half <= self.type <= UdmType.Vector4i:
            return self._get_value()
        elif self.type == UdmType.Element:
            return self
        elif UdmType.Array <= self.type <= UdmType.ArrayLz4 and self.array_type != UdmType.Struct:
            return self._get_array_value()
        elif UdmType.Array <= self.type <= UdmType.ArrayLz4 and self.array_type == UdmType.Struct:
            return self._get_struct_array_value()


class UDM:
    def __init__(self):
        self._udm_data: ctypes.c_void_p = ctypes.c_void_p()

    def create(self, asset_type, version, clear_on_destroy: bool = True) -> bool:
        data = udm_create(asset_type.encode('utf8'), version, clear_on_destroy)
        self._udm_data = ctypes.c_void_p(data)
        return data is not None

    def load(self, filename: Union[str, Path], clear_on_destroy: bool = True) -> bool:
        data = udm_load(filename.encode('utf8'), clear_on_destroy)
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
        if not self._udm_data:
            return
        udm_destroy_function(self._udm_data)

    def __enter__(self, filename, clear_on_destroy=True):
        self.load(filename, clear_on_destroy)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.destroy()

    @property
    def root(self) -> Optional[UdmProperty]:
        if not self._udm_data:
            return None
        return UdmProperty(udm_get_root_property(self._udm_data))
