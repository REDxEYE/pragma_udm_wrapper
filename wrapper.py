import ctypes
from pathlib import Path

from platform import architecture
from sys import platform
from typing import Union, Optional

from .type_info import UdmType


class UnsupportedPlatform(Exception):
    pass


current_path = Path(__file__).parent

nullptr = ctypes.c_char_p(0)


def pointer_to_array(pointer, size, type=ctypes.c_ubyte):
    return ctypes.cast(pointer, ctypes.POINTER(type * size))


def load_library() -> Optional[ctypes.CDLL]:
    if platform == 'win32' and architecture()[0] == '64bit':
        return ctypes.WinDLL((current_path / 'bin' / 'util_udm.dll').as_posix())
    elif platform == 'linux' and architecture()[0] == '64bit':
        return cdll.LoadLibrary((current_path / 'bin' / 'libutil_udm.so').as_posix())
    else:
        raise UnsupportedPlatform(f"Platform {platform}:{architecture()[0]} is not supported")


def _define_fundamental_type_functions(name, ctype):
    read_property_function = getattr(_library, f'udm_read_property_{name}')
    read_property_function.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctype]
    read_property_function.restype = ctype

    write_property_function = getattr(_library, f'udm_write_property_{name}')
    write_property_function.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctype]
    write_property_function.restype = None

    # TYPE* udm_write_property_v(UdmProperty udmData,const char *path,UdmType type,uint32_t *outNumValues)
    read_property_array_function = getattr(_library, f'udm_read_property_v{name}')
    read_property_array_function.argtypes = [ctypes.c_void_p, ctypes.c_char_p, UdmType, ctypes.POINTER(ctypes.c_uint32)]
    read_property_array_function.restype = ctypes.POINTER(ctype)

    # bool udm_write_property_v(UdmProperty udmData,const char *path,UdmType type,TYPE *values,uint32_t numValues)
    write_property_array_function = getattr(_library, f'udm_write_property_v{name}')
    write_property_array_function.argtypes = [ctypes.c_void_p, ctypes.c_char_p, UdmType, ctypes.c_void_p,
                                              ctypes.c_uint32]
    write_property_array_function.restype = ctypes.c_bool

    read_property_structure_array_function = getattr(_library, f'udm_read_property_sv{name}')
    read_property_structure_array_function.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint32,
                                                       ctypes.c_uint32, UdmType, ctypes.POINTER(ctypes.c_uint32)]
    read_property_structure_array_function.restype = ctypes.POINTER(ctype)

    write_property_structure_array_function = getattr(_library, f'udm_write_property_sv{name}')
    write_property_structure_array_function.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctype]
    write_property_structure_array_function.restype = None

    return (read_property_function, write_property_function,
            read_property_array_function, write_property_array_function,
            read_property_structure_array_function, write_property_structure_array_function
            )


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


# noinspection PyPep8Naming
class depricated:
    (udm_read_property_b,
     udm_write_property_b,
     udm_read_array_property_b,
     udm_write_array_property_b,
     udm_read_structure_array_property_b,
     udm_write_structure_array_property_b
     ) = _define_fundamental_type_functions('b', ctypes.c_bool)

    (udm_read_property_f,
     udm_write_property_f,
     udm_read_array_property_f,
     udm_write_array_property_f,
     udm_read_structure_array_property_f,
     udm_write_structure_array_property_f,
     ) = _define_fundamental_type_functions('f', ctypes.c_float)

    (udm_read_property_d,
     udm_write_property_d,
     udm_read_array_property_d,
     udm_write_array_property_d,
     udm_read_structure_array_property_d,
     udm_write_structure_array_property_d,
     ) = _define_fundamental_type_functions('d', ctypes.c_double)

    (udm_read_property_i8,
     udm_write_property_i8,
     udm_read_array_property_i8,
     udm_write_array_property_i8,
     udm_read_structure_array_property_i8,
     udm_write_structure_array_property_i8,
     ) = _define_fundamental_type_functions('i8', ctypes.c_int8)

    (udm_read_property_ui8,
     udm_write_property_ui8,
     udm_read_array_property_ui8,
     udm_write_array_property_ui8,
     udm_read_structure_array_property_ui8,
     udm_write_structure_array_property_ui8,
     ) = _define_fundamental_type_functions('ui8', ctypes.c_uint8)

    (udm_read_property_i16,
     udm_write_property_i16,
     udm_read_array_property_i16,
     udm_write_array_property_i16,
     udm_read_structure_array_property_i16,
     udm_write_structure_array_property_i16,
     ) = _define_fundamental_type_functions('i16', ctypes.c_int16)

    (udm_read_property_ui16,
     udm_write_property_ui16,
     udm_read_array_property_ui16,
     udm_write_array_property_ui16,
     udm_read_structure_array_property_ui16,
     udm_write_structure_array_property_ui16,
     ) = _define_fundamental_type_functions('ui16', ctypes.c_uint16)

    (udm_read_property_i,
     udm_write_property_i,
     udm_read_array_property_i,
     udm_write_array_property_i,
     udm_read_structure_array_property_i,
     udm_write_structure_array_property_i,
     ) = _define_fundamental_type_functions('i', ctypes.c_int32)

    (udm_read_property_ui,
     udm_write_property_ui,
     udm_read_array_property_ui,
     udm_write_array_property_ui,
     udm_read_structure_array_property_ui,
     udm_write_structure_array_property_ui,
     ) = _define_fundamental_type_functions('ui', ctypes.c_uint32)

    (udm_read_property_i64,
     udm_write_property_i64,
     udm_read_array_property_i64,
     udm_write_array_property_i64,
     udm_read_structure_array_property_i64,
     udm_write_structure_array_property_i64,
     ) = _define_fundamental_type_functions('i64', ctypes.c_int64)

    (udm_read_property_ui64,
     udm_write_property_ui64,
     udm_read_array_property_ui64,
     udm_write_array_property_ui64,
     udm_read_structure_array_property_ui64,
     udm_write_structure_array_property_ui64,
     ) = _define_fundamental_type_functions('ui64', ctypes.c_uint64)


# bool udm_read_property(UdmProperty udmData,char *path,UdmType type,void *buffer,uint32_t bufferSize);
udm_read_property = _library.udm_read_property
udm_read_property.argtypes = [ctypes.c_void_p, ctypes.c_char_p, UdmType, ctypes.c_void_p, ctypes.c_uint32]
udm_read_property.restype = ctypes.c_bool

# bool udm_write_property(UdmProperty udmData,char *path,UdmType type,void *buffer,uint32_t bufferSize);
udm_write_property = _library.udm_write_property
udm_write_property.argtypes = [ctypes.c_void_p, ctypes.c_char_p, UdmType, ctypes.c_void_p, ctypes.c_uint32]
udm_write_property.restype = ctypes.c_bool

# bool udm_read_array_property(UdmProperty udmData,char *path,UdmType type,void *buffer,
#                               uint32_t bufferSize,uint32_t arrayOffset,uint32_t arraySize);
udm_read_array_property = _library.udm_read_array_property
udm_read_array_property.argtypes = [ctypes.c_void_p, ctypes.c_char_p, UdmType, ctypes.c_void_p,
                                    ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
udm_read_array_property.restype = ctypes.c_bool

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
udm_write_property_string.restype = None

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
