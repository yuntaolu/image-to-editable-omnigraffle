#!/usr/bin/env python3
"""Regression tests for measured geometry, reference verification and visual diagnostics."""
import copy
import hashlib
import math
import tempfile
import subprocess
import sys
import json
from pathlib import Path
from PIL import Image, ImageDraw
from source_geometry import prepare, verify_reference
from build_omnigraffle import compile_manifest
from compare_reference import compare

with tempfile.TemporaryDirectory() as tmp:
    p=Path(tmp);im=Image.new('RGB',(800,400),'white');ImageDraw.Draw(im).rectangle((100,100,299,199),fill='#DBF3FF',outline='black');im.save(p/'source.png')
    m={'name':'Measured test','width':400,'reference':{'path':'source.png','sha256':hashlib.sha256((p/'source.png').read_bytes()).hexdigest(),'width_px':800,'height_px':400,'crop_px':[100,50,600,300]},
       'nodes':[{'id':'n','bbox_px':[100,100,200,100],'text':'Input','font_px':24,'fill':'#DBF3FF','stroke':'#000000','stroke_px':2,'corner_px':6,'align':'Left'}],
       'edges':[],'lines':[{'points_px':[[300,150],[600,150]],'width_px':3,'color':'#000000'}]}
    original=copy.deepcopy(m);verify_reference(m,p);n=prepare(m)
    assert m==original
    assert n['height']==200 and n['nodes'][0]['x']==0
    assert abs(n['nodes'][0]['y']-100/3)<1e-9
    assert n['nodes'][0]['font_size']==16 and n['nodes'][0]['corner']==4
    assert all(math.isclose(a,b,abs_tol=1e-9) for pair,want in zip(n['lines'][0]['points'],[[400/3,200/3],[1000/3,200/3]]) for a,b in zip(pair,want))
    assert n['lines'][0]['width']==2
    assert 'HorizontalTextAlignment[n.align' in compile_manifest(m)
    def rejected(change,fn=prepare):
        bad=copy.deepcopy(m);change(bad)
        try:fn(bad)
        except (ValueError,FileNotFoundError):return
        raise AssertionError('Bad reference/geometry accepted')
    rejected(lambda x:x.update(height=300))
    rejected(lambda x:x.pop('reference'))
    rejected(lambda x:x['nodes'][0].update(x=10))
    rejected(lambda x:x['nodes'][0].pop('bbox_px'))
    rejected(lambda x:x['nodes'][0].pop('font_px'))
    rejected(lambda x:x['lines'][0].pop('points_px'))
    rejected(lambda x:x['nodes'][0].update(bbox_px=[0,0,20,20]))
    rejected(lambda x:x['reference'].update(sha256='0'*64),lambda x:verify_reference(x,p))
    rejected(lambda x:x['reference'].update(width_px=900),lambda x:verify_reference(x,p))
    manifest=p/'manifest.json';manifest.write_text(json.dumps(m))
    cli=Path(__file__).with_name('build_omnigraffle.py')
    for target in [p/'source.png',manifest]:
        before=target.read_bytes()
        result=subprocess.run([sys.executable,str(cli),str(manifest),'--out',str(target)],capture_output=True)
        assert result.returncode!=0 and target.read_bytes()==before
    (p/'linked.png').hardlink_to(p/'source.png')
    before=(p/'source.png').read_bytes()
    result=subprocess.run([sys.executable,str(cli),str(manifest),'--out',str(p/'linked.png')],capture_output=True)
    assert result.returncode!=0 and (p/'source.png').read_bytes()==before
    alias_dir=p/'alias-result';alias_dir.mkdir();(alias_dir/'comparison.png').hardlink_to(p/'source.png')
    before=(p/'source.png').read_bytes()
    try:compare(p/'source.png',p/'source.png',alias_dir)
    except ValueError:pass
    else:raise AssertionError('Comparator output alias accepted')
    assert (p/'source.png').read_bytes()==before
    same=compare(p/'source.png',p/'source.png',p/'same')
    assert same['ink_mean_absolute_error']==0 and same['fidelity_status']=='requires_visual_review'
    tall=im.resize((800,600));tall.save(p/'tall.png')
    assert compare(p/'source.png',p/'tall.png',p/'tall-result')['fidelity_status']=='fail_aspect_ratio'
    shifted=Image.new('RGB',im.size,'white');ImageDraw.Draw(shifted).rectangle((160,100,359,199),fill='#DBF3FF',outline='black');shifted.save(p/'shifted.png')
    drift=compare(p/'source.png',p/'shifted.png',p/'shift-result')
    assert drift['aspect_error']==0 and drift['ink_mean_absolute_error']>0 and drift['changed_ink_fraction']>0
    assert drift['fidelity_status']=='requires_visual_review' # never auto-pass a same-ratio redesign
    Image.new('RGB',(1,1000),'white').save(p/'thin.png')
    Image.new('RGB',(1600,100),'white').save(p/'wide.png')
    thin=compare(p/'thin.png',p/'wide.png',p/'thin-result')
    with Image.open(p/'thin-result/comparison.png') as diagnostic:assert diagnostic.width<=3216 and diagnostic.height<=1600
    assert thin['fidelity_status']=='fail_aspect_ratio'
    Image.new('RGB',(4000,1),'white').save(p/'flat.png')
    assert compare(p/'flat.png',p/'flat.png',p/'flat-result')['diagnostic_resolution_limited']
    try:compare(p/'source.png',p/'shifted.png',p,source_crop=[0,0,999,400])
    except ValueError:pass
    else:raise AssertionError('Invalid crop accepted')
print('PASS: source hash/dimensions, isotropic geometry, font/stroke scale, forbidden relayout, aspect failure and same-ratio drift diagnostics')
