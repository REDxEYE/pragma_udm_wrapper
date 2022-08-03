import ctypes
from typing import Iterator, Any, Dict, List, Union, Optional

import numpy as np

from .property_unwrappers import string, integer, float_, vectors, blob
from .iproperty import IProperty
from .type_info import UdmType, udm_to_np
from .wrapper import (
    udm_get_property_type, udm_get_property_i,
    udm_get_property, udm_get_array_size,
    udm_get_array_value_type, udm_get_property_child_count,
    nullptr, udm_create_property_child_name_iterator, udm_fetch_property_child_name, udm_get_struct_member_names,
    udm_get_struct_member_types, udm_size_of_struct, udm_read_property, udm_read_array_property, udm_get_property_path,
    udm_size_of_type, ReadArrayPropertyResult
)


class ArrayIterator(Iterator['PropertyValue']):
    def __init__(self, array_prop: 'ArrayProperty'):
        self._prop = array_prop
        self._size = len(array_prop)
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= self._size:
            raise StopIteration
        res = self._prop[self._index]
        self._index += 1
        return res


class ArrayProperty(IProperty, List['PropertyValue']):

    def __init__(self, prop_p: int):
        super().__init__(prop_p)
        self._lazy_array_type: Optional[UdmType] = None

    def __len__(self) -> int:
        return udm_get_array_size(self._prop_p, nullptr)

    def __iter__(self) -> Iterator[IProperty]:
        return ArrayIterator(self)

    def __contains__(self, __x: object) -> bool:
        raise NotImplementedError('Contains not supported to ArrayProperty')

    @property
    def array_type(self) -> UdmType:
        if self._lazy_array_type is None:
            self._lazy_array_type = udm_get_array_value_type(self._prop_p, nullptr)
        return self._lazy_array_type

    def __getitem__(self, item: int) -> 'PropertyValue':
        if isinstance(item, int):
            prop_p = udm_get_property_i(self._prop_p, item)
            if prop_p is None or prop_p == 0:
                raise IndexError(f'Index out of range <{item}/{len(self)}>')
            return _unwrap_property(prop_p)
        elif isinstance(item, slice):
            res = []
            for i in range(item.start, min(item.stop, len(self))):
                res.append(_unwrap_property(udm_get_property_i(self._prop_p, i)))
            return res
        else:
            raise NotImplementedError(
                f'UdmProperty {self.path!r} does not support indexing with index "{item}" of type "{type(item)}"')

    def __repr__(self):
        return f'<UdmProperty {self.path!r} of type {self.type.name}<{self.array_type.name}> >'

    def value(self):
        res = []
        for i in range(0, len(self)):
            res.append(_unwrap_property(udm_get_property_i(self._prop_p, i)))
        return res


class ValueArrayProperty(ArrayProperty):
    def __init__(self, prop_p: int):
        super().__init__(prop_p)
        self.data_buffer = None

    def __contains__(self, __x: object) -> bool:
        raise NotImplementedError('Contains not supported to ArrayProperty')

    def __getitem__(self, item: int) -> Union[int, List[int], np.ndarray]:
        if isinstance(item, int):
            if self.data_buffer is None:
                self.value()
            return self.data_buffer[item]

        elif isinstance(item, slice):
            if self.data_buffer is None:
                self.value()
            return self.data_buffer[item]
        else:
            raise NotImplementedError(
                f'UdmProperty {self.path!r} does not support indexing with index "{item}" of type "{type(item)}"')

    def __repr__(self):
        return f'<UdmProperty {self.path!r} of type {self.type.name}<{self.array_type.name}> >'

    def value(self):
        data_type, data_len = udm_to_np[self.array_type]
        if len(self) == 0:
            return np.zeros(0, data_type)
        if data_len > 1:
            buffer = np.zeros((len(self), data_len), data_type)
        else:
            buffer = np.zeros(len(self), data_type)

        buffer_size = buffer.nbytes
        assert buffer_size == udm_size_of_type(self.array_type) * len(self)

        res = udm_read_array_property(self._prop_p, nullptr, self.array_type, buffer.ctypes.data, buffer_size, 0,
                                      len(self))
        if res == ReadArrayPropertyResult.Success:
            self.data_buffer = buffer
            return buffer
        else:
            del buffer
            raise ValueError(f"Failed to read value from {self!r}: {res!r}")


class StructArrayProperty(ArrayProperty):
    def __init__(self, prop_p: int):
        super().__init__(prop_p)
        dtype_info = []
        types = self._get_struct_member_types()
        for mname, mtype in zip(self._get_struct_member_names(), types):
            np_type, sub_item_count = udm_to_np[mtype]
            dtype_info.append((mname, np_type, (sub_item_count,)))
        self._dtype = np.dtype(dtype_info)

        sizeof = udm_size_of_struct(len(types), (ctypes.c_uint8 * len(types))(*types))
        assert sizeof == self._dtype.itemsize, 'Item size of generated numpy DType does not match with UDM calculated size'
        self.data_buffer = None

    def __iter__(self) -> Iterator[IProperty]:
        raise NotImplementedError()

    def __contains__(self, __x: object) -> bool:
        raise NotImplementedError('Contains not supported to ArrayProperty')

    def __getitem__(self, item: int | str) -> 'IProperty':
        if isinstance(item, (int, str)) and self.array_type == UdmType.Struct:
            if self.data_buffer is not None:
                return self.data_buffer[item]
            else:
                self.data_buffer = self.value()
                return self.data_buffer[item]
        else:
            raise NotImplementedError(
                f'UdmProperty "{self.path}" does not support indexing with index "{item}" of type "{type(item)}"')

    def __repr__(self):
        return f'<UdmProperty {self.path} of type {self.type.name}<{self.array_type.name}> >'

    def value(self):
        item_count = len(self)
        array = np.zeros((item_count,), self._dtype)
        res = udm_read_property(self._prop_p, nullptr, self.type, array.ctypes.data, item_count * array.itemsize)
        if res:
            return array
        else:
            del array
            raise ValueError(f'Failed to read {self.path}')

    @property
    def array_type(self) -> UdmType:
        return UdmType.Struct

    def _get_struct_member_names(self):
        value_count = ctypes.c_uint32(0)
        pointer = udm_get_struct_member_names(self._prop_p, nullptr, ctypes.byref(value_count))
        return [pointer[i].decode('utf8') for i in range(value_count.value)]

    def _get_struct_member_types(self):
        value_count = ctypes.c_uint32(0)
        pointer = udm_get_struct_member_types(self._prop_p, nullptr, ctypes.byref(value_count))
        return [UdmType(pointer[i]) for i in range(value_count.value)]


class ElementIterator(Iterator[str]):
    def __init__(self, array_prop: 'ElementProperty'):
        self._prop = array_prop
        self._iterator = udm_create_property_child_name_iterator(self._prop.prop_pointer, nullptr)
        self._size = len(array_prop)

    def __iter__(self):
        return self

    def __next__(self):
        if not self._iterator:
            raise StopIteration
        name = udm_fetch_property_child_name(self._iterator)
        if name is None or name == 0:
            raise StopIteration
        return name.decode('utf8')


class ElementProperty(IProperty, Dict[str, 'PropertyValue']):

    def __setitem__(self, __k: str, __v) -> None:
        raise NotImplementedError()

    def __delitem__(self, __v) -> None:
        raise NotImplementedError()

    def __len__(self) -> int:
        return udm_get_property_child_count(self._prop_p, nullptr)

    def __iter__(self) -> Iterator[str]:
        return ElementIterator(self)

    def __contains__(self, item: str):
        prop = udm_get_property(self._prop_p, item.encode('utf8'))
        return prop is not None and prop != 0

    def __getitem__(self, item) -> 'PropertyValue':
        if isinstance(item, str):
            prop_p = udm_get_property(self._prop_p, item.encode('utf8'))
            if prop_p is None or prop_p == 0:
                raise IndexError(f'UdmProperty {self.path!r} does not have "{item}" property')
            return _unwrap_property(prop_p)
        else:
            raise NotImplementedError(
                f'UdmProperty {self.path!r} does not support indexing with index "{item}" of type "{type(item)}"')

    def items(self):
        for name in self:
            yield name, self[name]

    def values(self):
        for name in self:
            yield self[name]

    def get(self, item: str, default: Any = None):
        if item in self:
            return self[item]
        return default


PropertyValue = Union[ArrayProperty, ValueArrayProperty,
                      StructArrayProperty, ElementProperty,
                      IProperty, int, float, str, bytes,
                      None
]


def _array_subtype_selector(prop_p):
    array_type = udm_get_array_value_type(prop_p, nullptr)
    if array_type <= UdmType.Utf8String:
        return ArrayProperty(prop_p)
    elif UdmType.Utf8String < array_type <= UdmType.Mat3x4:
        return ValueArrayProperty(prop_p)
    elif array_type == UdmType.Struct:
        return StructArrayProperty(prop_p)
    elif UdmType.Half <= array_type <= UdmType.Vector4i:
        return ValueArrayProperty(prop_p)
    elif UdmType.Element <= array_type <= UdmType.ArrayLz4:
        return ArrayProperty(prop_p)
    else:
        raise NotImplementedError(f'Unknown array subtype: {array_type} for {udm_get_property_path(prop_p)}')


_prop_unwrappers = (
    None,
    string.unwrap_string,
    string.unwrap_utf8_string,
    integer.unpack_int_type,
    integer.unpack_int_type,
    integer.unpack_int_type,
    integer.unpack_int_type,
    integer.unpack_int_type,
    integer.unpack_int_type,
    integer.unpack_int_type,
    integer.unpack_int_type,
    float_.unpack_float_type,
    float_.unpack_double_type,
    integer.unpack_int_type,

    vectors.unpack_vector_type,
    vectors.unpack_vector_type,
    vectors.unpack_vector_type,
    vectors.unpack_vector_type,
    vectors.unpack_vector_type,

    vectors.unpack_vector_type,
    vectors.unpack_vector_type,

    vectors.unpack_vector_type,
    vectors.unpack_vector_type,

    vectors.unpack_vector_type,
    vectors.unpack_vector_type,

    blob.unwrap_blob,
    blob.unwrap_blob,

    ElementProperty,
    _array_subtype_selector,
    _array_subtype_selector,

    None,
    None,

    float_.unpack_half_type,
    vectors.unpack_vector_type,
    vectors.unpack_vector_type,
    vectors.unpack_vector_type,
)


def _unwrap_property(prop_p) -> PropertyValue:
    prop_type = udm_get_property_type(prop_p, nullptr)
    unwprapper = _prop_unwrappers[prop_type]
    if unwprapper is None:
        return None
    return unwprapper(prop_p)
