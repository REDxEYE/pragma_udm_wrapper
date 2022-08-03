import ctypes

from ..wrapper import udm_read_property_string, udm_get_property_path, nullptr


def unwrap_string(prop_p: ctypes.c_void_p):
    value = udm_read_property_string(prop_p, nullptr, b'\xBA\xAD\xF0\x0D')
    if value == b'\xBA\xAD\xF0\x0D':
        path = udm_get_property_path(prop_p).decode('ascii')
        raise RuntimeError(f'Failed to read string from "{path}"!')
    return value.decode('ascii')


def unwrap_utf8_string(prop_p: ctypes.c_void_p):
    value = udm_read_property_string(prop_p, nullptr, b'\xBA\xAD\xF0\x0D')
    if value == b'\xBA\xAD\xF0\x0D':
        path = udm_get_property_path(prop_p).decode('utf8')
        raise RuntimeError(f'Failed to read string from "{path}"!')
    return value.decode('utf-8')

