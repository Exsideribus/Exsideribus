#!/usr/bin/env python3
"""Current profile visual system: one animated hero and a grouped toolkit.
Python 3 + ImageMagick. No external widget services or Python imaging packages.
The nebula was prepared with imagegen; animation and typography are native layers.
Approved research and project cards are not rewritten.
"""
from pathlib import Path
import argparse
import html
import math
import random
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT/'assets'
NS = 'http://www.w3.org/2000/svg'


def run(*args):
    subprocess.run(args,cwd=ROOT,check=True,stdout=subprocess.DEVNULL)


def svg(body,width,height,title):
    return f'<svg xmlns="{NS}" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img"><title>{html.escape(title)}</title>{body}</svg>'


def text(x,y,value,size=24,color='#edf0f5',weight=400,extra=''):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="DejaVu Sans,sans-serif" font-size="{size}" font-weight="{weight}" {extra}>{html.escape(value)}</text>'


def write(name,body,width,height,title):
    (ASSETS/name).write_text(svg(body,width,height,title),encoding='utf-8')


def icon(slug,cx,y):
    if slug in ('sql','matplotlib','powerbi','excel'):
        if slug=='sql':
            body='<ellipse cx="24" cy="10" rx="19" ry="7"/><path d="M5 10V36C5 45 43 45 43 36V10 M5 23C5 32 43 32 43 23"/>'
        elif slug=='matplotlib':
            body='<circle cx="24" cy="24" r="20"/><circle cx="24" cy="24" r="10" opacity=".5"/><path d="M24 4V44 M4 24H44 M10 10L38 38 M10 38L38 10" opacity=".5"/><path d="M24 24L24 6L39 13L24 24L40 31L28 41Z"/>'
        elif slug=='powerbi':
            body='<rect x="4" y="24" width="9" height="20" rx="2"/><rect x="20" y="13" width="9" height="31" rx="2"/><rect x="36" y="3" width="9" height="41" rx="2"/>'
        else:
            body='<rect x="3" y="6" width="42" height="36" rx="3"/><path d="M3 17H45 M3 29H45 M17 6V42 M31 6V42"/>'
        return f'<g transform="translate({cx-24} {y})" fill="none" stroke="#dce3ed" stroke-width="1.8">{body}</g>'
    root=ET.parse(ASSETS/'icons'/f'{slug}.svg').getroot()
    paths=''.join(f'<path d="{node.attrib["d"]}"/>' for node in root.iter() if node.tag.endswith('path'))
    return f'<g transform="translate({cx-24} {y}) scale(2)" fill="#dce3ed">{paths}</g>'


# All tools are supported by Resume.pdf, except SQL (earlier README) and
# PyQt6 (the gravitational-lensing repository). No proficiency is inferred.
groups=[
    ('Data & machine learning',[('python','Python'),('sql','SQL'),('numpy','NumPy'),('pandas','Pandas'),('scikitlearn','scikit-learn'),('jupyter','Jupyter')]),
    ('Visualization & applications',[('matplotlib','Matplotlib'),('plotly','Plotly'),('streamlit','Streamlit'),('powerbi','Power BI'),('excel','Excel'),('qt','PyQt6')]),
    ('Databases & development',[('postgresql','PostgreSQL'),('mysql','MySQL'),('dbeaver','DBeaver'),('docker','Docker'),('git','Git'),('github','GitHub')]),
    ('Research & simulation',[('godotengine','Godot'),('unity','Unity'),('unrealengine','Unreal Engine'),('nvidia','Omniverse'),('latex','LaTeX'),('markdown','Markdown')]),
]
toolkit='<rect width="1200" height="582" rx="16" fill="#0b0e13"/>'
all_labels=[]
for row,(heading,tools) in enumerate(groups):
    top=18+row*140
    toolkit+=text(28,top+20,heading,22,'#8f9aa8',500)
    for col,(slug,label) in enumerate(tools):
        cx=100+col*200
        toolkit+=icon(slug,cx,top+41)
        toolkit+=text(cx,top+112,label,20,'#c1cad7',extra='text-anchor="middle"')
        all_labels.append(label)
    if row<3:
        toolkit+=f'<path d="M28 {top+126}H1172" stroke="#222b37" stroke-width="1"/>'
write('profile-toolkit-expanded.svg',toolkit,1200,582,'Toolkit: '+', '.join(all_labels))

# Uniform native-SVG typography replaces editor-dependent Markdown headings.
for slug,title,line_start in [('research','Research',210),('toolkit','Toolkit',180),('projects','Projects',200)]:
    body=text(0,49,title,34,weight=500)
    body+=f'<path d="M{line_start} 39H1200" stroke="#29323f" stroke-width="1"/>'
    write(f'profile-heading-{slug}.svg',body,1200,76,title)

for slug,label in [('linkedin','LinkedIn'),('projects','All projects')]:
    body='<rect width="580" height="82" rx="16" fill="#0b0e13"/>'
    if slug=='linkedin':
        body+='<rect x="28" y="25" width="32" height="32" rx="5" fill="#dce3ed"/>'+text(44,49,'in',24,'#0b0e13',600,extra='text-anchor="middle"')
    else:
        body+='<path d="M28 30H40L46 35H60V55H28Z" fill="none" stroke="#dce3ed" stroke-width="1.8"/>'
    body+=text(80,53,label,30,weight=500)
    body+='<path d="M522 41H545 M536 32L545 41L536 50" fill="none" stroke="#8f9aa8" stroke-width="1.5"/>'
    write(f'profile-connect-{slug}.svg',body,580,82,label)
write('profile-footer-gap.svg','',1200,32,'')

# Render static vectors to PNG so typography matches the GIFs on every device.
static_assets=['profile-toolkit-expanded','profile-heading-research','profile-heading-projects','profile-heading-toolkit','profile-connect-linkedin','profile-connect-projects','profile-project-solar','profile-project-commercial']
for asset in static_assets:
    run('convert','-background','none',str(ASSETS/(asset+'.svg')),str(ASSETS/(asset+'.png')))

args=argparse.ArgumentParser()
args.add_argument('--preview',action='store_true',help='Render one hero frame instead of the animation')
preview=args.parse_args().preview

hero_fixed='''<defs><linearGradient id="shade" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#0b0e13" stop-opacity=".05"/><stop offset=".30" stop-color="#0b0e13" stop-opacity=".18"/><stop offset=".52" stop-color="#0b0e13" stop-opacity=".74"/><stop offset=".78" stop-color="#0b0e13" stop-opacity=".80"/><stop offset="1" stop-color="#0b0e13" stop-opacity=".52"/></linearGradient></defs><rect width="1200" height="320" fill="url(#shade)"/>'''
hero_fixed+=text(600,181,'Matheus Najal Cruz',62,'#ffffff',600,extra='text-anchor="middle" letter-spacing=".3"')
hero_fixed+=text(600,229,'Exploring the universe through data.',26,'#d6dce5',extra='text-anchor="middle" font-style="italic"')
rng=random.Random(17)
stars=[(rng.randint(20,1180),rng.randint(15,118),rng.uniform(.9,2.2),rng.uniform(0,math.tau)) for _ in range(24)]
with tempfile.TemporaryDirectory(prefix='exsideribus-hero-') as temp_dir:
    temp=Path(temp_dir)
    background=temp/'background.png'
    run('convert',str(ASSETS/'nebula-banner.png'),'-resize','1240x332^','-gravity','center','-extent','1240x332',str(background))
    frames=[]
    for i in range(1 if preview else 60):
        phase=math.tau*i/60
        dx=20+round(12*math.sin(phase))
        dy=6+round(4*math.cos(phase))
        motion=''
        for j,(sx,sy,r,offset) in enumerate(stars):
            x=sx+18*math.sin(phase+offset)
            y=sy+5*math.cos(phase+offset)
            opacity=.15+.6*(.5+.5*math.sin(phase+offset))**2
            motion+=f'<g fill="#fff" opacity="{opacity:.3f}"><circle cx="{x:.3f}" cy="{y:.3f}" r="{r:.2f}"/>'
            if j%4==0:
                motion+=f'<path d="M{x-6:.3f} {y:.3f}H{x+6:.3f} M{x:.3f} {y-6:.3f}V{y+6:.3f}" stroke="#fff" stroke-width=".65"/>'
            motion+='</g>'
        for start,end,left,top,travel in [(4,24,20,25,1120),(33,54,190,10,970)]:
            if start<=i<=end:
                u=(i-start)/(end-start)
                x=left+travel*u
                y=top+93*u
                alpha=math.sin(math.pi*u)**.6
                motion+=f'<g fill="#fff" opacity="{alpha:.3f}">'
                for tail in range(16,0,-1):
                    tx=x-tail*7
                    ty=y-tail*.65
                    motion+=f'<circle cx="{tx:.2f}" cy="{ty:.2f}" r="{.5+1.5*(1-tail/17):.2f}" opacity="{.65*(1-tail/17):.3f}"/>'
                motion+=f'<circle cx="{x:.3f}" cy="{y:.3f}" r="10" opacity=".12"/><circle cx="{x:.3f}" cy="{y:.3f}" r="4"/></g>'
        source=temp/'overlay.svg'
        source.write_text(svg(motion+hero_fixed,1200,320,'Matheus Najal Cruz — Exploring the universe through data'),encoding='utf-8')
        overlay=temp/'overlay.png'
        run('convert','-background','none',str(source),str(overlay))
        frame=temp/f'{i:03}.png'
        run('convert',str(background),'-crop',f'1200x320+{dx}+{dy}','+repage',str(overlay),'-compose','Over','-composite','-colorspace','Gray',str(frame))
        frames.append(str(frame))
        if preview:
            run('convert',str(frame),str(ASSETS/'profile-hero.png'))
    if not preview:
        palette=temp/'palette.png'
        run('convert','-size','64x1','gradient:black-white','-depth','8',str(palette))
        run('convert','-delay','12','-loop','0',*frames,'+dither','-remap',str(palette),'-layers','Optimize',str(ASSETS/'profile-hero.gif'))
print('Hero '+('preview' if preview else 'animation')+' built. Grouped toolkit: '+str(len(all_labels))+' verified tools. Existing research cards preserved.')
