#!/usr/bin/env python3
"""Small contract checks: reject broken topology and preserve native data points."""
import copy
import json
import plistlib
import tempfile
import zipfile
from pathlib import Path
from build_omnigraffle import compile_manifest, validate
from inspect_graffle import inspect

m=json.loads((Path(__file__).parents[1]/'examples/minimal.json').read_text())
m['lines']=[{'points':[[0,1],[2,3],[4,5]],'source':'synthetic self-test'}]
s=compile_manifest(m)
assert json.loads(s.split('const M=',1)[1].split(';\n',1)[0])['lines'][0]['points']==[[0,1],[2,3],[4,5]]
for change in [lambda x:x['edges'][0].update(to='missing'),lambda x:x['nodes'][0].update(w=-1),lambda x:x['lines'][0].update(points=[[0,float('nan')],[1,2]]),lambda x:x['nodes'].append(x['nodes'][0]),lambda x:x.update(assets=[{'path':'unplaced.png'}])]:
    bad=copy.deepcopy(m);change(bad)
    try:validate(bad)
    except ValueError:pass
    else:raise AssertionError('Invalid manifest accepted')
fixture={'Sheets':[{'GraphicsList':[{'ID':1,'Class':'ShapedGraphic'},{'ID':2,'Class':'ShapedGraphic'},{'Class':'LineGraphic','Head':{'ID':2},'Tail':{'ID':1},'Points':['{0,0}','{1,1}']}]}]}
with tempfile.TemporaryDirectory() as tmp:
    p=Path(tmp);raw=plistlib.dumps(fixture);(p/'plain.graffle').write_bytes(raw)
    with zipfile.ZipFile(p/'zip.graffle','w') as z:z.writestr('data.plist',raw)
    (p/'package.graffle').mkdir();(p/'package.graffle/data.plist').write_bytes(raw)
    results=[inspect(p/n) for n in ['plain.graffle','zip.graffle','package.graffle']]
    assert results[0]==results[1]==results[2]
    assert results[0][0]['attached_connectors']==1
    fixture['Sheets'][0]['GraphicsList'][-1]['Head']['ID']=999
    (p/'dangling.graffle').write_bytes(plistlib.dumps(fixture))
    assert inspect(p/'dangling.graffle')[0]['attached_connectors']==0
print('PASS: topology validation, finite data, IDs, asset gate, polyline preservation and native inventory formats')
