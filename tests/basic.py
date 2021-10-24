import sys
from pathlib import Path
from pragma_udm_wrapper import UDM, UdmType

if __name__ == '__main__':
    udm = UDM()
    path = Path.cwd() / '/pragma_udm_wrapper/tests/test_material_ascii.pmat'
    if not udm.load(path):
        print(f'Failed to load UDM file {path}!', file=sys.stderr)
        sys.exit(1)

    root = udm.root
    prop = root['pbr']
    print(prop)

    prop = root['pbr/properties']
    print(prop)

    prop = root['pbr/properties/roughness_factor']
    print(prop)

    prop = root['pbr/properties/rma_info/requires_ao_update']
    print(prop)

    prop = root['pbr/textures/albedo_map']
    print(prop)

    udm.destroy()
