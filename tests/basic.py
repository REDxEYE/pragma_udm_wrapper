from pathlib import Path
from pragma_udm_wrapper import UDM, UdmType

if __name__ == '__main__':
    udm = UDM()
    path = str(Path.cwd()) +'/tests/test_material_ascii.pmat'
    if not udm.load(path):
        print('Failed to load UDM file ' +path +'!')
        sys.exit(1)
        
    root = udm.root
    prop = root['pbr']
    print(prop)
    prop = root['materialPaths']
    print(prop)
    prop = root['mass']
    print(prop)
    prop = root['eyeOffset']
    print(prop)
    prop = root['materials']
    print(prop)
    prop = root['skins[0]/materials']
    print(prop)
    prop = root['skeleton/assetData/bones/ValveBiped.Bip01_Pelvis/pose']
    print(prop)
    prop = root['collisionMeshes[0]/assetData/vertices']
    print(prop)
    prop = root['meshGroups/eli_reference/meshes[0]/subMeshes[0]/assetData/vertices']
    print(prop)
    prop = root['meshGroups/eli_reference/meshes[0]/subMeshes[0]/assetType']
    print(prop)

    udm.destroy()
