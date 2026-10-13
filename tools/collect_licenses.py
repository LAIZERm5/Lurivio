"""Collect available installed runtime license/notice files for a binary build.

Metadata is recorded where wheels do not contain a full license text. Review
THIRD_PARTY_NOTICES before distributing; this script is not a compliance audit.
"""
import importlib.metadata as metadata
import json
import re
import shutil
import sys
from pathlib import Path

ROOTS=['zxing-cpp','PySide6-Essentials','shiboken6','rapidocr-onnxruntime','onnxruntime',
       'opencv-python','numpy','Pillow','pyclipper','Shapely','PyYAML','protobuf',
       'six','tqdm','colorama','packaging','flatbuffers']

def main():
    target=Path(sys.argv[1] if len(sys.argv)>1 else 'THIRD_PARTY_LICENSES')
    target.mkdir(parents=True,exist_ok=True)
    index=[]
    for name in ROOTS:
        try:
            dist=metadata.distribution(name)
        except metadata.PackageNotFoundError:
            continue
        folder=target/re.sub(r'[^A-Za-z0-9_.-]','_',name)
        folder.mkdir(exist_ok=True)
        license_text=dist.metadata.get('License') or dist.metadata.get('License-Expression') or 'See project documentation'
        (folder/'PACKAGE_METADATA.txt').write_text(
            f"Name: {dist.metadata.get('Name',name)}\nVersion: {dist.version}\nLicense: {license_text}\n"
            + '\n'.join(dist.metadata.get_all('Project-URL',[])),encoding='utf-8')
        copied=[]
        for item in (dist.files or []):
            leaf=item.name.lower()
            if not leaf.startswith(('license','licence','copying','notice')):
                continue
            source=Path(dist.locate_file(item))
            if source.is_file():
                destination=folder/str(item).replace('/','__').replace('\\','__')
                shutil.copy2(source,destination);copied.append(destination.name)
        index.append(dict(name=name,version=dist.version,files=copied))
    supplied=Path(__file__).resolve().parents[1]/'third_party'
    if supplied.exists():
        shutil.copytree(supplied,target/'supplied_license_texts',dirs_exist_ok=True)
    (target/'INDEX.json').write_text(json.dumps(index,indent=2),encoding='utf-8')
    print(f'Collected notices for {len(index)} installed distributions.')

if __name__=='__main__':main()
