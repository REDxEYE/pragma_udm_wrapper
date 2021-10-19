import ctypes
from enum import IntEnum

import numpy as np


class UdmType(IntEnum):
    Nil = 0
    String = 1
    Utf8String = 2
    Int8 = 3
    UInt8 = 4
    Int16 = 5
    UInt16 = 6
    Int32 = 7
    UInt32 = 8
    Int64 = 9
    UInt64 = 10
    Float = 11
    Double = 12
    Boolean = 13
    Vector2 = 14
    Vector3 = 15
    Vector4 = 16
    Quaternion = 17
    EulerAngles = 18
    Srgba = 19
    HdrColor = 20
    Transform = 21
    ScaledTransform = 22
    Mat4 = 23
    Mat3x4 = 24
    Blob = 25
    BlobLz4 = 26
    Element = 27
    Array = 28
    ArrayLz4 = 29
    Reference = 30
    Struct = 31
    Half = 32
    Vector2i = 33
    Vector3i = 34
    Vector4i = 35
    Count = 36
    Last = Count - 1
    Invalid = 255

    @classmethod
    def from_param(cls, value):
        return cls(value)


udm_type_to_ctypes = {
    UdmType.String: ctypes.c_char_p,
    UdmType.Utf8String: ctypes.c_char_p,
    UdmType.Int8: ctypes.c_int8,
    UdmType.UInt8: ctypes.c_uint8,
    UdmType.Int16: ctypes.c_int16,
    UdmType.UInt16: ctypes.c_uint16,
    UdmType.Int32: ctypes.c_int32,
    UdmType.UInt32: ctypes.c_uint32,
    UdmType.Int64: ctypes.c_int64,
    UdmType.UInt64: ctypes.c_uint64,
    UdmType.Float: ctypes.c_float,
    UdmType.Double: ctypes.c_double,
    UdmType.Boolean: ctypes.c_bool,
}

udm_to_np = {
    UdmType.String: (np.uint8, 1),
    UdmType.Utf8String: (np.uint8, 1),
    UdmType.Int8: (np.int8, 1),
    UdmType.UInt8: (np.uint8, 1),
    UdmType.Srgba: (np.uint8, 3),
    UdmType.Int16: (np.int16, 1),
    UdmType.UInt16: (np.uint16, 1),
    UdmType.HdrColor: (np.uint16, 3),
    UdmType.Int32: (np.int32, 1),
    UdmType.UInt32: (np.uint32, 1),
    UdmType.Int64: (np.int64, 1),
    UdmType.UInt64: (np.uint64, 1),
    UdmType.Float: (np.float32, 1),
    UdmType.Half: (np.float16, 1),
    UdmType.Double: (np.double, 1),
    UdmType.Boolean: (np.uint8, 1),
    UdmType.Vector2: (np.float32, 2),
    UdmType.Vector3: (np.float32, 3),
    UdmType.EulerAngles: (np.float32, 3),
    UdmType.Vector4: (np.float32, 4),
    UdmType.Quaternion: (np.float32, 4),
    UdmType.Transform: (np.float32, 7),
    UdmType.ScaledTransform: (np.float32, 10),
    UdmType.Mat4: (np.float32, 16),
    UdmType.Mat3x4: (np.float32, 12),
    UdmType.Vector2i: (np.int32, 2),
    UdmType.Vector3i: (np.int32, 3),
    UdmType.Vector4i: (np.int32, 4),
}
