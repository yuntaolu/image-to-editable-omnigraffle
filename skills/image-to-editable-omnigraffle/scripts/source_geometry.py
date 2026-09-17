"""Map measured source pixels to native points without changing the composition."""
import copy
import math
import re


def prepare(m):
    m=copy.deepcopy(m)
    mode=m.get('mode','reconstruct')
    if mode=='redesign':return m
    if mode!='reconstruct':raise ValueError('mode must be reconstruct or explicitly authorized redesign')
    ref=m.get('reference')
    if not isinstance(ref,dict):raise ValueError('Reconstruction requires reference dimensions/hash and measured pixel geometry; legacy point manifests need explicit mode=redesign')
    def finite(v,label,positive=False):
        if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or (positive and v<=0):
            raise ValueError(f'{label} must be finite'+(' and positive' if positive else ''))
        return v
    rw=finite(ref.get('width_px'),'reference width',True);rh=finite(ref.get('height_px'),'reference height',True)
    if not isinstance(ref.get('sha256'),str) or not re.fullmatch('[0-9a-fA-F]{64}',ref['sha256']):raise ValueError('reference.sha256 must identify the actual source image')
    crop=ref.get('crop_px',[0,0,rw,rh])
    if not isinstance(crop,list) or len(crop)!=4:raise ValueError('reference crop_px is [left, top, width, height]')
    ox,oy,cw,ch=[finite(v,'crop coordinate')for v in crop]
    if min(ox,oy)<0 or min(cw,ch)<=0 or ox+cw>rw or oy+ch>rh:raise ValueError('Reference crop lies outside source')
    scale=finite(m.get('width'),'publication width',True)/cw;height=ch*scale
    if 'height'in m and abs(finite(m['height'],'height',True)-height)>.01:raise ValueError('Reconstruction height must preserve the reference crop aspect ratio')
    m['height']=height
    def box(item):
        if any(k in item for k in ('x','y','w','h')):raise ValueError('Reconstruction accepts bbox_px, not independent point coordinates')
        b=item.get('bbox_px')
        if not isinstance(b,list)or len(b)!=4:raise ValueError('Every node/asset needs measured bbox_px')
        x,y,w,h=[finite(v,'bbox coordinate')for v in b]
        if min(w,h)<=0 or x<ox or y<oy or x+w>ox+cw or y+h>oy+ch:raise ValueError('Object bbox is outside the declared source crop')
        item.update(x=(x-ox)*scale,y=(y-oy)*scale,w=w*scale,h=h*scale)
    def points(item):
        if 'points'in item:raise ValueError('Reconstruction requires measured points_px, not independent point routes')
        pts=item.get('points_px')
        if not isinstance(pts,list)or len(pts)<2:raise ValueError('Every connector/curve requires measured points_px')
        converted=[]
        for p in pts:
            if not isinstance(p,list)or len(p)!=2:raise ValueError('Point needs x and y')
            x,y=[finite(v,'point coordinate')for v in p]
            if not(ox<=x<=ox+cw and oy<=y<=oy+ch):raise ValueError('Point is outside source crop')
            converted.append([(x-ox)*scale,(y-oy)*scale])
        item['points']=converted
        if 'width'in item:raise ValueError('Use measured width_px in reconstruction mode')
        item['width']=finite(item.get('width_px'),'stroke width',True)*scale
        if 'color'not in item:raise ValueError('Record the source connector/curve color')
    for n in m.get('nodes',[]):
        box(n)
        if 'font_size'in n:raise ValueError('Use measured font_px in reconstruction mode')
        if n.get('text'):n['font_size']=finite(n.get('font_px'),'measured font size',True)*scale
        if 'corner'in n:raise ValueError('Use measured corner_px in reconstruction mode')
        corner=finite(n.get('corner_px',0),'corner radius')
        if corner<0:raise ValueError('Corner radius cannot be negative')
        n['corner']=corner*scale
        for field in ['fill','stroke']:
            if field not in n:raise ValueError('Record source fill/stroke explicitly, including null')
        if n['stroke'] is not None:n['stroke_width']=finite(n.get('stroke_px'),'stroke width',True)*scale
        for src,dest in [('hpadding_px','hpadding'),('vpadding_px','vpadding')]:
            v=finite(n.get(src,0),src)
            if v<0:raise ValueError('Text padding cannot be negative')
            n[dest]=v*scale
    for item in m.get('edges',[])+m.get('lines',[]):points(item)
    for a in m.get('assets',[]):box(a)
    m['mode']='reconstruct';m['reference_transform']={'scale':scale,'origin_px':[ox,oy],'crop_px':crop}
    return m


def verify_reference(m,base_dir):
    """CLI boundary: verify declared dimensions/hash against the actual source image."""
    if m.get('mode','reconstruct')=='redesign':return
    import hashlib
    from pathlib import Path
    from PIL import Image
    ref=m.get('reference',{})
    if not isinstance(ref,dict) or not isinstance(ref.get('path'),str):raise ValueError('reference.path is required for reconstruction')
    p=Path(ref['path']);p=p if p.is_absolute() else Path(base_dir)/p
    if hashlib.sha256(p.read_bytes()).hexdigest().lower()!=str(ref.get('sha256','')).lower():raise ValueError('Reference image hash mismatch')
    with Image.open(p) as image:
        if image.size!=(ref.get('width_px'),ref.get('height_px')):raise ValueError('Reference image dimensions mismatch')
