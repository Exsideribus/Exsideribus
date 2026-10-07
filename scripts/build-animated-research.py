#!/usr/bin/env python3
"""Animate the existing code-native research SVGs, preserving all captions.
Requires Python 3 and ImageMagick. No Python imaging packages or network calls.
"""
from pathlib import Path
import math
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)


def run(*args):
    subprocess.run(args, cwd=ROOT, check=True, stdout=subprocess.DEVNULL)


def wrap(body, title):
    return f'<svg xmlns="{NS}" width="580" height="260" viewBox="0 0 580 260"><title>{title}</title>{body}</svg>'


def wave(y, control):
    return f'M0 {y}Q75 {control} 145 {y}T290 {y}T435 {y}T580 {y}T725 {y}T870 {y}'


ocean_source = ET.parse(ASSETS / 'research-mental-health.svg').getroot()
lens_source = ET.parse(ASSETS / 'research-lensing.svg').getroot()
ocean_text = ''.join(ET.tostring(node, encoding='unicode') for node in ocean_source.findall(f'{{{NS}}}text'))
lens_base = ''.join(ET.tostring(node, encoding='unicode') for node in lens_source if node.tag != f'{{{NS}}}title')

with tempfile.TemporaryDirectory(prefix='exsideribus-research-') as temp_dir:
    temp = Path(temp_dir)
    ocean_frames, lens_frames = [], []
    for i in range(80):
        phase = 2 * math.pi * i / 80
        shift = -290 * i / 80
        ocean = '''<defs><linearGradient id="water" x2="0" y2="1"><stop stop-color="#242c36"/><stop offset="1" stop-color="#0b0e13"/></linearGradient><clipPath id="card"><rect width="580" height="260" rx="16"/></clipPath></defs><rect width="580" height="260" rx="16" fill="#0b0e13"/>'''
        ocean += f'<g clip-path="url(#card)"><g transform="translate({shift:.3f} 0)"><path d="{wave(86,51)}V154H0Z" fill="url(#water)"/><g fill="none" stroke="#8d9aa9" stroke-width="1.2" opacity=".75"><path d="{wave(89,55)}"/><path d="{wave(104,78)}" opacity=".55"/><path d="{wave(119,102)}" opacity=".28"/></g></g></g>'
        ocean += f'<circle cx="443" cy="43" r="23" fill="#e2e6eb" opacity="{.065 + .045*(.5+.5*math.sin(phase)):.3f}"/><circle cx="443" cy="43" r="14" fill="#e2e6eb"/>' + ocean_text

        rotation = math.radians(-18)
        x0, y0 = 100 * math.cos(phase), 34 * math.sin(phase)
        x = 294 + x0 * math.cos(rotation) - y0 * math.sin(rotation)
        y = 76 + x0 * math.sin(rotation) + y0 * math.cos(rotation)
        light = '<g fill="#fff">'
        for j in range(8,0,-1):
            tail_angle = phase - j*.055
            tx0, ty0 = 100*math.cos(tail_angle), 34*math.sin(tail_angle)
            tx = 294 + tx0*math.cos(rotation)-ty0*math.sin(rotation)
            ty = 76 + tx0*math.sin(rotation)+ty0*math.cos(rotation)
            light += f'<circle cx="{tx:.3f}" cy="{ty:.3f}" r="2" opacity="{.45*(1-j/9):.3f}"/>'
        light += f'<circle cx="{x:.3f}" cy="{y:.3f}" r="9" opacity=".09"/><circle cx="{x:.3f}" cy="{y:.3f}" r="5.5" opacity=".28"/><circle cx="{x:.3f}" cy="{y:.3f}" r="3.4"/></g>'

        for slug, body, title, frames in [
            ('ocean', ocean, 'Depths of the Mind VR — Published at SeGAH 2026', ocean_frames),
            ('lensing', lens_base+light, 'Gravitational lensing simulator — paper planned', lens_frames),
        ]:
            source = temp / f'{slug}.svg'
            source.write_text(wrap(body, title), encoding='utf-8')
            frame = temp / f'{slug}-{i:03}.png'
            run('convert','-background','none',str(source),str(frame))
            frames.append(str(frame))
    palette = temp / 'palette.png'
    run('convert',ocean_frames[0],lens_frames[0],'+append','-colors','256','-unique-colors',str(palette))
    for frames, target in [(ocean_frames,'research-mental-health.gif'), (lens_frames,'research-lensing.gif')]:
        run('convert','-delay','10','-loop','0',*frames,'+dither','-remap',str(palette),'-layers','Optimize',str(ASSETS/target))
print('Animated research cards: 580x260, 80 frames each, 8-second seamless loops.')
