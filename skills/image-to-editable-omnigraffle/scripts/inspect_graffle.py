#!/usr/bin/env python3
"""Read native Graffle object, text, image and connector inventory without modification."""
import argparse
import collections
import json
import plistlib
import zipfile
from pathlib import Path


def inspect(path):
    path=Path(path)
    if path.is_dir():raw=(path/'data.plist').read_bytes()
    elif zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:raw=z.read('data.plist')
    else:raw=path.read_bytes()
    doc=plistlib.loads(raw)
    def walk(items):
        for item in items:
            yield item
            yield from walk(item.get('Graphics',[]))
    out=[]
    for sheet in doc.get('Sheets',[doc]):
        gs=list(walk(sheet.get('GraphicsList',[])))
        lines=[g for g in gs if g.get('Class')=='LineGraphic']
        ids={g.get('ID') for g in gs if g.get('ID') is not None}
        out.append({'canvas':sheet.get('SheetTitle',''),'classes':dict(collections.Counter(g.get('Class') for g in gs)),
                    'text_objects':sum(bool(g.get('Text',{}).get('Text')) for g in gs),
                    'image_objects':sum('ImageID' in g for g in gs),
                    'attached_connectors':sum(g.get('Head',{}).get('ID') in ids and g.get('Tail',{}).get('ID') in ids for g in lines),
                    'longest_polylines':sorted([len(g.get('Points',[])) for g in lines],reverse=True)[:3]})
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('file');args=p.parse_args()
    print(json.dumps(inspect(args.file),indent=2))
