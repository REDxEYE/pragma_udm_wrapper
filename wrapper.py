import ctypes
from enum import IntEnum
from pathlib import Path

from platform import architecture
from sys import platform
from typing import Optional

from .type_info import UdmType


class UnsupportedPlatform(Exception):
    pass


current_path = Path(__file__).parent

nullptr = ctypes.c_char_p(0)


def pointer_to_array(pointer, size, ctype=ctypes.c_ubyte):
    return ctypes.cast(pointer, ctypes.POINTER(ctype * size))


def load_library(full_path: Optional[Path] = None) -> Optional[ctypes.CDLL]:
    if full_path is not None and full_path.exists():
        return ctypes.CDLL(full_path.as_posix())
    if platform == 'win32' and architecture()[0] == '64bit':
        return ctypes.WinDLL((current_path / 'bin' / 'util_udm.dll').as_posix())
    elif platform == 'linux' and architecture()[0] == '64bit':
        return ctypes.CDLL((current_path / 'bin' / 'libutil_udm.so').as_posix())
    else:
        raise UnsupportedPlatform(f"Platform {platform}:{architecture()[0]} is not supported")


class BlobResult(IntEnum):
    Success = 0
    DecompressedSizeMismatch = 1
    InsufficientSize = 2
    ValueTypeMismatch = 3
    NotABlobType = 4
    InvalidProperty = 5

    @classmethod
    def from_param(cls, value):
        return cls(value)


class ReadArrayPropertyResult(IntEnum):
    Success = 0
    NotAnArrayType = 1
    RequestedRangeOutOfBounds = 2
    BufferSizeDoesNotMatchExpectedSize = 3

    @classmethod
    def from_param(cls, value):
        return cls(value)


_library = load_library()

# bool udm_add_property_array(UdmProperty udmData,const char *path,UdmType type,UdmArrayType arrayType,uint32_t size)
# _udm_add_property_array_function = _library.udm_add_property_array

# bool udm_add_property_struct(UdmProperty udmData,const char *path,uint32_t numMembers,UdmType *types,
# const char **names)
# _udm_add_property_struct_function = _library.udm_add_property_struct

# region Create/Save/Destroy

# UdmData udm_create(const char *assetType,uint32_t assetVersion,bool clearDataOnDestruction)
udm_create = _library.udm_create
udm_create.argtypes = [ctypes.c_char_p, ctypes.c_uint32, ctypes.c_bool]
udm_create.restype = ctypes.c_void_p

# UdmData udm_load(const char *fileName,bool clearDataOnDestruction)
udm_load = _library.udm_load
udm_load.argtypes = [ctypes.c_char_p, ctypes.c_bool]
udm_load.restype = ctypes.c_void_p

# void udm_destroy(UdmData udmData)
udm_destroy_function = _library.udm_destroy
udm_destroy_function.argtypes = [ctypes.c_void_p]
udm_destroy_function.restype = None

# bool udm_save_binary(UdmData udmData,const char *fileName)
udm_save_binary = _library.udm_save_binary
udm_save_binary.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
udm_save_binary.restype = ctypes.c_bool

#  bool udm_save_ascii(UdmData udmData,const char *fileName,uint32_t asciiFlags)
udm_save_ascii = _library.udm_save_ascii
udm_save_ascii.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint32]
udm_save_ascii.restype = ctypes.c_bool

#  char *udm_get_asset_type(UdmData udmData)
udm_get_asset_type = _library.udm_get_asset_type
udm_get_asset_type.argtypes = [ctypes.c_void_p]
udm_get_asset_type.restype = ctypes.c_char_p

#  udm::Version udm_get_asset_version(UdmData udmData)
udm_get_asset_version = _library.udm_get_asset_version
udm_get_asset_version.argtypes = [ctypes.c_void_p]
udm_get_asset_version.restype = ctypes.c_uint32

# endregion

# void udm_free_memory(UdmData udmData)
udm_free_memory = _library.udm_free_memory
udm_free_memory.argtypes = [ctypes.c_void_p]
udm_free_memory.restype = None
# UdmProperty udm_get_root_property(UdmData parent)
udm_get_root_property = _library.udm_get_root_property
udm_get_root_property.argtypes = [ctypes.c_void_p]
udm_get_root_property.restype = ctypes.c_void_p

# DLLUDM UdmType udm_get_property_type(UdmProperty prop,const char *path);
udm_get_property_type = _library.udm_get_property_type
udm_get_property_type.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
udm_get_property_type.restype = UdmType

# UdmType udm_get_array_value_type(UdmProperty udmData,const char *path)
udm_get_array_value_type = _library.udm_get_array_value_type
udm_get_array_value_type.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
udm_get_array_value_type.restype = UdmType

# DLLUDM UdmElementIterator udm_create_property_child_name_iterator(UdmProperty prop,const char *path);
udm_create_property_child_name_iterator = _library.udm_create_property_child_name_iterator
udm_create_property_child_name_iterator.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
udm_create_property_child_name_iterator.restype = ctypes.c_void_p

# DLLUDM const char *udm_fetch_property_child_name(UdmElementIterator iterator);
udm_fetch_property_child_name = _library.udm_fetch_property_child_name
udm_fetch_property_child_name.argtypes = [ctypes.c_void_p]
udm_fetch_property_child_name.restype = ctypes.c_char_p

# UdmProperty udm_get_property(UdmProperty parent,const char *path)
udm_get_property = _library.udm_get_property
udm_get_property.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
udm_get_property.restype = ctypes.c_void_p

# UdmProperty udm_get_property_i(UdmProperty parent,uint32_t idx)
udm_get_property_i = _library.udm_get_property_i
udm_get_property_i.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
udm_get_property_i.restype = ctypes.c_void_p

# char *udm_property_to_json(UdmProperty prop)
udm_property_to_json = _library.udm_property_to_json
udm_property_to_json.argtypes = [ctypes.c_void_p]
udm_property_to_json.restype = ctypes.c_char_p

# const char *udm_property_to_ascii(UdmProperty prop,const char *path));
udm_property_to_ascii = _library.udm_property_to_ascii
udm_property_to_ascii.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
udm_property_to_ascii.restype = ctypes.c_char_p

# void udm_destroy_property(UdmProperty prop)
udm_destroy_property = _library.udm_destroy_property
udm_destroy_property.argtypes = [ctypes.c_void_p]
udm_destroy_property.restype = None

# uint32_t udm_get_array_size(UdmProperty udmData,const char *path)
udm_get_array_size = _library.udm_get_array_size
udm_get_array_size.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
udm_get_array_size.restype = ctypes.c_uint32

# uint32_t udm_get_property_child_count(UdmProperty udmData,const char *path)
udm_get_property_child_count = _library.udm_get_property_child_count
udm_get_property_child_count.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
udm_get_property_child_count.restype = ctypes.c_uint32

# bool udm_read_property_v(UdmProperty udmData,const char *path,void *outData,uint32_t itemSizeInBytes,
#                           uint32_t arrayOffset,uint32_t numItems);
udm_read_property_v = _library.udm_read_property_v
udm_read_property_v.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32,
                                ctypes.c_uint32]
udm_read_property_v.restype = ctypes.c_bool

# bool udm_write_property_v(UdmProperty udmData,const char *path,void *inData,uint32_t itemSizeInBytes,
#                               uint32_t arrayOffset,uint32_t numItems);
udm_write_property_v = _library.udm_write_property_v
udm_write_property_v.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32,
                                 ctypes.c_uint32]
udm_write_property_v.restype = ctypes.c_bool

# size_t udm_size_of_type(UdmType type);
udm_size_of_type = _library.udm_size_of_type
udm_size_of_type.argtypes = [UdmType]
udm_size_of_type.restype = ctypes.c_size_t

# size_t udm_size_of_struct(uint32_t numMembers,UdmType *types);
udm_size_of_struct = _library.udm_size_of_struct
udm_size_of_struct.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint8)]
udm_size_of_struct.restype = ctypes.c_size_t

# bool udm_read_property(UdmProperty udmData,char *path,UdmType type,void *buffer,uint32_t bufferSize);
udm_read_property = _library.udm_read_property
udm_read_property.argtypes = [ctypes.c_void_p, ctypes.c_char_p, UdmType, ctypes.c_void_p, ctypes.c_uint32]
udm_read_property.restype = ctypes.c_bool

# bool udm_write_property(UdmProperty udmData,char *path,UdmType type,void *buffer,uint32_t bufferSize);
udm_write_property = _library.udm_write_property
udm_write_property.argtypes = [ctypes.c_void_p, ctypes.c_char_p, UdmType, ctypes.c_void_p, ctypes.c_uint32]
udm_write_property.restype = ctypes.c_bool

# ReadArrayPropertyResult udm_read_array_property(UdmProperty udmData,char *path,UdmType type,void *buffer,
#                               uint32_t bufferSize,uint32_t arrayOffset,uint32_t arraySize);
udm_read_array_property = _library.udm_read_array_property
udm_read_array_property.argtypes = [ctypes.c_void_p, ctypes.c_char_p, UdmType, ctypes.c_void_p,
                                    ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
udm_read_array_property.restype = ReadArrayPropertyResult

# bool udm_write_array_property(UdmProperty udmData,char *path,UdmType type,void *buffer,
#                               uint32_t bufferSize,uint32_t arrayOffset,uint32_t arraySize,UdmArrayType arrayType,
#                               uint32_t numMembers,UdmType *types,const char **names);
udm_write_array_property = _library.udm_write_array_property
udm_write_array_property.argtypes = [ctypes.c_void_p, ctypes.c_char_p, UdmType, ctypes.c_void_p,
                                     ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                                     ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_char_p)]
udm_write_array_property.restype = ctypes.c_bool

# char *udm_read_property_s(UdmProperty prop,const char *path,const char *defaultValue)
udm_read_property_string = _library.udm_read_property_s
udm_read_property_string.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
udm_read_property_string.restype = ctypes.c_char_p

# const char **udm_read_property_vs(UdmProperty prop,const char *path,uint32_t *outNumValues)
udm_read_array_property_string = _library.udm_read_property_vs
udm_read_array_property_string.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint32)]
udm_read_array_property_string.restype = ctypes.POINTER(ctypes.c_char_p)

# bool udm_write_property_vs(UdmProperty prop,const char *path,const char **values,uint32_t numValues)
udm_write_array_property_string = _library.udm_write_property_vs
udm_write_array_property_string.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_char_p), ctypes.c_void_p,
                                            ctypes.c_uint32]
udm_write_array_property_string.restype = ctypes.c_bool

# bool udm_write_property_s(UdmProperty prop,const char *path,const char *value)
udm_write_property_string = _library.udm_write_property_s
udm_write_property_string.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
udm_write_property_string.restype = ctypes.c_bool

# char *udm_get_property_name(UdmProperty prop);
udm_get_property_name = _library.udm_get_property_name
udm_get_property_name.argtypes = [ctypes.c_void_p]
udm_get_property_name.restype = ctypes.c_char_p

# char *udm_get_property_path(UdmProperty prop);
udm_get_property_path = _library.udm_get_property_path
udm_get_property_path.argtypes = [ctypes.c_void_p]
udm_get_property_path.restype = ctypes.c_char_p

# UdmProperty udm_get_from_property(UdmProperty prop);
udm_get_from_property = _library.udm_get_from_property
udm_get_from_property.argtypes = [ctypes.c_void_p]
udm_get_from_property.restype = ctypes.c_char_p

# UdmElementIterator udm_create_property_child_name_iterator(UdmProperty prop,const char *path);
udm_create_property_child_name_iterator = _library.udm_create_property_child_name_iterator
udm_create_property_child_name_iterator.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
udm_create_property_child_name_iterator.restype = ctypes.c_void_p

# const char *udm_fetch_property_child_name(UdmElementIterator iterator);
udm_fetch_property_child_name = _library.udm_fetch_property_child_name
udm_fetch_property_child_name.argtypes = [ctypes.c_void_p]
udm_fetch_property_child_name.restype = ctypes.c_char_p

# UdmType *udm_get_struct_member_types(UdmProperty udmData,const char *path,uint32_t *outNumMembers)
udm_get_struct_member_types = _library.udm_get_struct_member_types
udm_get_struct_member_types.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint32)]
udm_get_struct_member_types.restype = ctypes.POINTER(ctypes.c_uint8)

# char **udm_get_struct_member_names(UdmProperty udmData,const char *path,uint32_t *outNumMembers)
udm_get_struct_member_names = _library.udm_get_struct_member_names
udm_get_struct_member_names.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint32)]
udm_get_struct_member_names.restype = ctypes.POINTER(ctypes.c_char_p)

# bool udm_get_blob_size(UdmProperty udmData,const char *path,uint64_t &outSize)
udm_get_blob_size = _library.udm_get_blob_size
udm_get_blob_size.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint64)]
udm_get_blob_size.restype = ctypes.c_bool

# udm::BlobResult udm_read_property_blob(UdmProperty prop,const char *path,uint8_t *outData,size_t outDataSize)
udm_read_property_blob = _library.udm_read_property_blob
udm_read_property_blob.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint8),
                                   ctypes.c_uint64]
udm_read_property_blob.restype = BlobResult

# void udm_pose_to_matrix(const float pos[3],const float rot[4],const float scale[3],float *outMatrix)
udm_pose_to_matrix = _library.udm_pose_to_matrix
udm_pose_to_matrix.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float),
                               ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]
udm_pose_to_matrix.restype = None
