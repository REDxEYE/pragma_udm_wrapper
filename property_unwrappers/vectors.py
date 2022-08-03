import ctypes

import numpy as np

from ..type_info import udm_to_np
from ..wrapper import udm_get_property_type, udm_read_property, nullptr, udm_get_property_path


def unpack_vector_type(prop_p: ctypes.c_void_p):
    prop_type = udm_get_property_type(prop_p, nullptr)
    base_type, size = udm_to_np[prop_type]
    buffer = np.zeros(size, base_type)
    res = udm_read_property(prop_p, nullptr, prop_type, buffer.ctypes.data, buffer.itemsize * size)
    if res:
        return buffer
    else:
        del buffer
        raise ValueError(f'Failed to read {udm_get_property_path(prop_p)}')
