#!/usr/bin/env python3
"""Compile a point-based reconstruction manifest into a guarded native drawing script."""
import argparse
import json
import math
import re
from pathlib import Path


def validate(m, allow_manual_assets=False):
    def number(v, label, positive=False):
        if isinstance(v, bool) or not isinstance(v, (float, int)) or not math.isfinite(v):
            raise ValueError(f'{label} must be finite')
        if positive and v <= 0:
            raise ValueError(f'{label} must be positive')
    def color(v):
        if v is not None and (not isinstance(v, str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', v)):
            raise ValueError(f'Invalid color: {v!r}')
    def points(values):
        if not isinstance(values, list) or len(values) < 2:
            raise ValueError('A line needs at least two points')
        for pair in values:
            if not isinstance(pair, list) or len(pair) != 2:
                raise ValueError('Each point needs x and y')
            for v in pair:
                number(v, 'coordinate')
    if not isinstance(m, dict) or not isinstance(m.get('name'), str) or not m['name']:
        raise ValueError('A named manifest object is required')
    number(m.get('width'), 'width', True)
    number(m.get('height'), 'height', True)
    nodes=m.get('nodes', [])
    if not nodes:
        raise ValueError('At least one native node is required')
    ids=set()
    for n in nodes:
        key=n.get('id')
        if not isinstance(key,str) or not key or key in ids:
            raise ValueError('Node IDs must be nonempty and unique')
        ids.add(key)
        for k in ('x','y','w','h'):
            number(n.get(k),f'{key}.{k}',k in ('w','h'))
        if not isinstance(n.get('text',''),str):
            raise ValueError('Node text must be a string')
        if n.get('shape','Rectangle') not in ('Rectangle','Circle','Diamond'):
            raise ValueError('Unsupported native shape')
        number(n.get('font_size',9),'font_size',True)
        for k in ('fill','stroke','color'):
            if k in n: color(n[k])
    for e in m.get('edges',[]):
        if e.get('from') not in ids or e.get('to') not in ids:
            raise ValueError('Edge references a missing node')
        for k,default in [('tail',2),('head',1)]:
            if isinstance(e.get(k,default),bool) or e.get(k,default) not in range(1,5):
                raise ValueError('Magnet index must be 1..4')
        if 'points' in e: points(e['points'])
        number(e.get('width',.65),'edge width',True)
        if 'color' in e:color(e['color'])
    for line in m.get('lines',[]):
        points(line.get('points'))
        number(line.get('width',.65),'line width',True)
        if 'color' in line:color(line['color'])
    assets=m.get('assets',[])
    if assets and not allow_manual_assets:
        raise ValueError('Assets require native placement; use --allow-manual-assets only for an explicitly incomplete structure build')
    for a in assets:
        if not all(a.get(k) for k in ('path','kind','source','sha256')):
            raise ValueError('Asset provenance and SHA-256 are required')
        for k in ('x','y','w','h'):number(a.get(k),f'asset.{k}',k in ('w','h'))
    return m


NATIVE = r'''
(() => {
  if(document.portfolio.canvases.some(c=>c.graphics.length)) throw Error('Use a new empty document; existing graphics are protected.');
  const c=document.portfolio.canvases[0];
  c.name=M.name;c.canvasSizingMode=CanvasSizingMode.Fixed;c.canvasSizeIsMeasuredInPages=false;c.size=new Size(M.width,M.height);c.background.fillColor=Color.RGB(1,1,1);
  function rgb(h){return h===null?null:Color.RGB(...[1,3,5].map(i=>parseInt(h.slice(i,i+2),16)/255));}
  const nodes=new Map(), groups=new Map();
  function member(g,key){if(key){if(!groups.has(key))groups.set(key,[]);groups.get(key).push(g);}}
  for(const n of M.nodes){
    const s=c.newShape();s.geometry=new Rect(n.x,n.y,n.w,n.h);s.shape=n.shape||'Rectangle';s.name=n.id;s.text=n.text||'';
    s.fontName=n.bold?'TimesNewRomanPS-BoldMT':'TimesNewRomanPSMT';s.textSize=n.font_size||9;s.textColor=rgb(n.color===undefined?'#243547':n.color);
    s.textHorizontalPadding=1;s.textVerticalPadding=0;s.textHorizontalAlignment=HorizontalTextAlignment.Center;s.textVerticalPlacement=VerticalTextPlacement.Middle;
    s.fillColor=rgb(n.fill===undefined?null:n.fill);s.strokeColor=rgb(n.stroke===undefined?(n.fill?'#61758A':null):n.stroke);s.strokeThickness=.6;s.shadowColor=null;s.cornerRadius=n.corner===undefined?2:n.corner;
    s.magnets=[new Point(-1,0),new Point(1,0),new Point(0,-1),new Point(0,1)];nodes.set(n.id,s);member(s,n.group);
  }
  function style(l,d){l.strokeColor=rgb(d.color===undefined?'#61758A':d.color);l.strokeThickness=d.width||.65;l.shadowColor=null;l.lineType=LineType.Straight;if(d.points)l.points=d.points.map(p=>new Point(...p));l.headType=d.arrow===false?'None':'FilledArrow';l.headScale=.55;l.tailType=d.bidirectional?'FilledArrow':'None';l.tailScale=.55;if(d.dashed)l.strokePattern=StrokeDash.Dash2on2off;member(l,d.group);}
  for(const e of M.edges||[]){const l=c.connect(nodes.get(e.from),nodes.get(e.to));l.tailMagnet=e.tail||2;l.headMagnet=e.head||1;style(l,e);}
  for(const p of M.lines||[]){const l=c.newLine();style(l,Object.assign({arrow:false},p));}
  for(const [key,items]of groups){const g=new Group(items);g.name=key;}
  const figure=new Group(c.graphics);figure.name=M.name;
  console.log('NATIVE_STRUCTURE_CREATED '+M.name+' nodes='+M.nodes.length+' edges='+(M.edges||[]).length+' polylines='+(M.lines||[]).length);
  if((M.assets||[]).length)console.log('PENDING_ASSET_PLACEMENT '+JSON.stringify(M.assets));
})();
'''


def compile_manifest(m, allow_manual_assets=False):
    validate(m,allow_manual_assets)
    return 'const M='+json.dumps(m,ensure_ascii=False,allow_nan=False,separators=(',',':'))+';\n'+NATIVE


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('manifest',type=Path)
    ap.add_argument('--out',required=True,type=Path)
    ap.add_argument('--allow-manual-assets',action='store_true')
    args=ap.parse_args()
    m=json.loads(args.manifest.read_text(encoding='utf-8'))
    script=compile_manifest(m,args.allow_manual_assets)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(script,encoding='utf-8')
    print(f'Wrote {args.out}; execute in a new blank OmniGraffle document.')

if __name__=='__main__':main()
