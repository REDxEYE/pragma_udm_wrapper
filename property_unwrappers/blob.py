import ctypes

from ..wrapper import udm_get_blob_size, nullptr, udm_read_property_blob, BlobResult, pointer_to_array


def unwrap_blob(prop_p: ctypes.c_void_p):
    size = ctypes.c_uint64(0)
    if udm_get_blob_size(prop_p, nullptr, ctypes.byref(size)):
        buffer = ctypes.create_string_buffer(size.value)
        res = udm_read_property_blob(prop_p, nullptr, ctypes.cast(buffer, ctypes.POINTER(ctypes.c_uint8)), size)
        if res == BlobResult.Success:
            return bytes(pointer_to_array(buffer, size.value).contents)
        else:
            raise ValueError(f'Failed to read Blob data: {res!r}')
    raise ValueError('Failed to read Blob size')
