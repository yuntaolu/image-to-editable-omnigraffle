#!/usr/bin/env python3
"""Produce source/export diagnostics without warping images or claiming automatic visual approval."""
import argparse
import hashlib
import json
import math
from pathlib import Path
from PIL import Image, ImageChops, ImageOps, ImageStat


def load(path,crop=None):
    with Image.open(path) as raw:
        im=Image.alpha_composite(Image.new('RGBA',raw.size,'white'),raw.convert('RGBA')).convert('RGB')
    if crop is not None:
        x,y,w,h=crop
        if min(x,y)<0 or min(w,h)<=0 or x+w>im.width or y+h>im.height:raise ValueError('Crop outside image')
        im=im.crop((x,y,x+w,y+h))
    return im


def compare(source,render,out,source_crop=None,render_crop=None,max_aspect_error=.01):
    if not math.isfinite(max_aspect_error) or max_aspect_error<0:raise ValueError('Invalid aspect tolerance')
    source,render,out=Path(source),Path(render),Path(out)
    for name in ['comparison.png','overlay.png','difference.png','comparison.json']:
        target=out/name
        if any(target.resolve()==p.resolve() or (target.exists() and p.exists() and target.samefile(p)) for p in (source,render)):
            raise ValueError('Diagnostics must not overwrite inputs')
    a,b=load(source,source_crop),load(render,render_crop)
    drift=abs((b.width/b.height)/(a.width/a.height)-1)
    # One isotropic scale per image, based on width; never stretch to hide drift.
    target_width=min(max(a.width,b.width),1600,1600/max(a.height/a.width,b.height/b.width))
    width=max(1,round(target_width))
    resolution_limited=target_width<1 or min(a.height*target_width/a.width,b.height*target_width/b.width)<1
    a=a.resize((width,max(1,round(a.height*target_width/a.width))),Image.Resampling.LANCZOS)
    b=b.resize((width,max(1,round(b.height*target_width/b.width))),Image.Resampling.LANCZOS)
    height=max(a.height,b.height)
    aa=Image.new('RGB',(width,height),'white');aa.paste(a,(0,0))
    bb=Image.new('RGB',(width,height),'white');bb.paste(b,(0,0))
    delta=ImageChops.difference(aa,bb)
    # A background-heavy diagram must not get a flattering score from whitespace.
    ink=ImageChops.darker(aa.convert('L'),bb.convert('L')).point(lambda v:255 if v<245 else 0)
    ink_count=ink.histogram()[255]
    mean=ImageStat.Stat(delta,ink).mean if ink_count else [0,0,0]
    changed=delta.convert('L').point(lambda v:255 if v>24 else 0)
    changed=ImageChops.multiply(changed,ink)
    report={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'render_sha256':hashlib.sha256(render.read_bytes()).hexdigest(),
            'source_size':list(load(source).size),'render_size':list(load(render).size),'source_crop':source_crop,'render_crop':render_crop,
            'aspect_error':drift,'max_aspect_error':max_aspect_error,'ink_mean_absolute_error':sum(mean)/3/255,
            'changed_ink_fraction':changed.histogram()[255]/ink_count if ink_count else 0,
            'fidelity_status':'fail_aspect_ratio' if drift>max_aspect_error else 'requires_visual_review',
            'diagnostic_resolution_limited':resolution_limited,'visual_review':'pending','note':'Metrics are diagnostics, not a visual pass. Review labels, panel proportions, object inventory, type scale, equations, connectors and artwork.'}
    out.mkdir(parents=True,exist_ok=True)
    sheet=Image.new('RGB',(width*2+16,height),'#dddddd');sheet.paste(aa,(0,0));sheet.paste(bb,(width+16,0))
    sheet.save(out/'comparison.png');Image.blend(aa,bb,.5).save(out/'overlay.png')
    ImageOps.invert(delta).save(out/'difference.png')
    (out/'comparison.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source');p.add_argument('render');p.add_argument('--out',required=True)
    p.add_argument('--source-crop',nargs=4,type=int);p.add_argument('--render-crop',nargs=4,type=int);p.add_argument('--max-aspect-error',type=float,default=.01)
    a=p.parse_args();r=compare(a.source,a.render,a.out,a.source_crop,a.render_crop,a.max_aspect_error)
    print(json.dumps(r,indent=2));raise SystemExit(2 if r['fidelity_status'].startswith('fail') else 0)
