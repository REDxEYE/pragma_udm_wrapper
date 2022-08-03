import ctypes
from pathlib import Path
from typing import Union, Optional
import numpy as np
import numpy.typing as npt

from .exceptions import UDMNotLoaded
from .properties import ElementProperty
from .type_info import UdmType, udm_to_np, udm_type_to_ctypes
from . import wrapper

__all__ = ['UDM', 'UdmType']


class UDM:
    def __init__(self):
        self._udm_data: ctypes.c_void_p = ctypes.c_void_p()

    def create(self, asset_type, version, clear_on_destroy: bool = True) -> bool:
        data = wrapper.udm_create(asset_type.encode('utf8'), version, clear_on_destroy)
        self._udm_data = ctypes.c_void_p(data)
        return data is not None

    def load(self, filename: Union[str, Path], clear_on_destroy: bool = True) -> bool:
        data = wrapper.udm_load(str(filename).encode('utf8'), clear_on_destroy)
        self._udm_data = ctypes.c_void_p(data)
        return data is not None

    def save(self, filename: Union[str, Path], binary: bool = True, ascii_flags: int = 0) -> bool:
        if binary and ascii_flags:
            raise RuntimeError(f'Ascii flags are not supposed to be used when binary mode is chosen')
        if binary:
            return wrapper.udm_save_binary(self._udm_data, Path(filename).as_posix().encode('utf8'))
        else:
            return wrapper.udm_save_ascii(self._udm_data, Path(filename).as_posix().encode('utf8'), ascii_flags)

    def destroy(self) -> None:
        if not self._udm_data or self._udm_data.value == 0:
            return
        wrapper.udm_destroy_function(self._udm_data)
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
    def root(self) -> Optional[ElementProperty]:
        if not self._udm_data:
            return None
        return ElementProperty(wrapper.udm_get_root_property(self._udm_data))

    @property
    def asset_type(self):
        if not self._udm_data:
            return None
        asset_type = wrapper.udm_get_asset_type(self._udm_data)
        if asset_type is not None and asset_type != 0:
            return asset_type.decode('utf8')
        return None

    @property
    def asset_version(self):
        if not self._udm_data:
            return None
        return wrapper.udm_get_asset_version(self._udm_data)


def _int_to_ptr(ptr, target_type):
    return ctypes.cast(ptr,ctypes.POINTER(target_type))


def pose_to_matrix(pos: Optional[npt.NDArray[np.float]] = None,
                   rot: Optional[npt.NDArray[np.float]] = None,
                   scl: Optional[npt.NDArray[np.float]] = None):
    if pos is None:
        pos = np.zeros(3, np.float32)
    if rot is None:
        rot = np.zeros(4, np.float32)
    if scl is None:
        scl = np.ones(3, np.float32)

    mat = np.zeros((4, 4), np.float32)

    wrapper.udm_pose_to_matrix(_int_to_ptr(pos.ctypes.data, ctypes.c_float),
                               _int_to_ptr(rot.ctypes.data, ctypes.c_float),
                               _int_to_ptr(scl.ctypes.data, ctypes.c_float),
                               _int_to_ptr(mat.ctypes.data, ctypes.c_float))
    return mat
