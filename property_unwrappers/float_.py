import ctypes

import numpy as np

from ..type_info import udm_type_to_ctypes, UdmType
from ..wrapper import udm_get_property_type, udm_read_property, nullptr, udm_get_property_path


def unpack_half_type(prop_p: ctypes.c_void_p):
    buffer = np.zeros(1, np.float16)
    res = udm_read_property(prop_p, nullptr, UdmType.Half, buffer.ctypes.data, 2)
    if res:
        return float(buffer[0])
    else:
        del buffer
        raise ValueError(f'Failed to read {udm_get_property_path(prop_p)}')


def unpack_float_type(prop_p: ctypes.c_void_p):
    buffer = ctypes.c_float(0)
    res = udm_read_property(prop_p, nullptr, UdmType.Float, ctypes.byref(buffer), ctypes.sizeof(buffer))
    if res:
        return buffer.value
    else:
        del buffer
        raise ValueError(f'Failed to read {udm_get_property_path(prop_p)}')


def unpack_double_type(prop_p: ctypes.c_void_p):
    buffer = ctypes.c_double(0)
    res = udm_read_property(prop_p, nullptr, UdmType.Double, ctypes.byref(buffer), ctypes.sizeof(buffer))
    if res:
        return buffer.value
    else:
        del buffer
        raise ValueError(f'Failed to read {udm_get_property_path(prop_p)}')
