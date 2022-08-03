from . import UDM
from .properties import ElementProperty, PropertyValue
from .iproperty import IProperty


class ITypeWrapper:

    def __init__(self, prop: IProperty):
        self._prop = prop

    def __getitem__(self, item) -> PropertyValue:
        return self._prop[item]


class ITypeRootWrapper:
    _root: ElementProperty
    ASSET_TYPE = 'FILL ME'
    ASSET_VERSION_MIN = 1
    ASSET_VERSION_MAX = 1

    @property
    def _root(self):
        return self._udm.root

    def __init__(self, udm: UDM):
        self._udm = udm
        if self._udm.asset_type != self.ASSET_TYPE:
            raise ValueError(f'Invalid asset type, expected: {self.ASSET_TYPE}, got {self._udm.asset_type}')
        version = self._udm.asset_version
        if version < self.ASSET_VERSION_MIN or version > self.ASSET_VERSION_MAX:
            raise ValueError(
                f'Invalid asset version, supported between {self.ASSET_VERSION_MIN}-{self.ASSET_VERSION_MAX}, got {version}')
