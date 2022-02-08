import typing
from typing import Union

from .basic_property import BasicUdmProperty
from .exceptions import UDMNotLoaded
from .type_info import udm_to_np, udm_type_to_ctypes
from .wrapper import *


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

    def get_value(self, type_override: UdmType = None):
        self_type = type_override or self.type
        if UdmType.String <= self_type <= UdmType.BlobLz4 or UdmType.Half <= self_type <= UdmType.Vector4i:
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

    def __getitem__(self, key):
        root = self.root
        if root is None:
            raise UDMNotLoaded("UDM file wasn't loaded")
        return root[key]

    @property
    def root(self) -> Optional[UdmProperty]:
        if not self._udm_data:
            return None
        return UdmProperty(udm_get_root_property(self._udm_data))
