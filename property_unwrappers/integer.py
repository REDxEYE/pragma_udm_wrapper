import ctypes

from ..type_info import udm_type_to_ctypes
from ..wrapper import udm_get_property_type, udm_read_property, nullptr, udm_get_property_path


def unpack_int_type(prop_p: ctypes.c_void_p):
    prop_type = udm_get_property_type(prop_p, nullptr)
    base_type = udm_type_to_ctypes[prop_type]
    buffer = base_type(0)
    res = udm_read_property(prop_p, nullptr, prop_type, ctypes.byref(buffer), ctypes.sizeof(buffer))
    if res:
        return buffer.value
    else:
        del buffer
        raise ValueError(f'Failed to read {udm_get_property_path(prop_p)}')
