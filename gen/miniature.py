#!/usr/bin/env python3
"""Crea le miniature leggere usate da ricerca, righe e pagina /ig. Si lancia a mano
(python3 gen/miniature.py) quando arriva una foto o un post nuovo: serve Pillow.
Il sito funziona anche senza: build.py usa una miniatura solo se il file esiste."""
import os, glob, json
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def crop(src, dst, w, h, top=False, q=72):
    if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src): return
    im = Image.open(src).convert('RGB'); r = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x = (im.width - w) // 2; y = 0 if top else (im.height - h) // 2
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im.crop((x, y, x + w, y + h)).save(dst, 'WEBP', quality=q, method=6); print(dst)
for f in glob.glob(os.path.join(ROOT, 'assets/foto/*.webp')):
    if not f.endswith('-sm.webp'): crop(f, os.path.join(ROOT, 'assets/mini', os.path.basename(f)), 160, 160)
for f in glob.glob(os.path.join(ROOT, 'assets/stampabili/*.webp')):
    if not f.endswith('-sm.webp'): crop(f, os.path.join(ROOT, 'assets/mini', 'foglio-' + os.path.basename(f)), 160, 160, top=True)
# guide senza una foto propria: una miniatura da un'altra foto, con un taglio diverso (finché non arriva la foto giusta)
for nuovo, da in [('risvegli-notturni', 'quanto-dorme-un-bambino')]:
    src = os.path.join(ROOT, 'assets/foto', da + '.webp'); dst = os.path.join(ROOT, 'assets/mini', nuovo + '.webp')
    if os.path.exists(src) and not os.path.exists(dst):
        im = Image.open(src).convert('RGB'); w, h = im.size; im.crop((w - h, 0, w, h)).resize((160, 160), Image.LANCZOS).save(dst, 'WEBP', quality=72, method=6); print(dst)
crop(os.path.join(ROOT, 'assets/gestionale/inizia-telefono.webp'), os.path.join(ROOT, 'assets/mini/gestionale.webp'), 160, 160, top=True)
# la foto del gestionale, più leggera per il telefono
src = os.path.join(ROOT, 'assets/gestionale/inizia.webp'); dst = os.path.join(ROOT, 'assets/gestionale/inizia-sm.webp')
if not os.path.exists(dst):
    im = Image.open(src).convert('RGB'); im.resize((800, 500), Image.LANCZOS).save(dst, 'WEBP', quality=70, method=6); print(dst)
D = json.load(open(os.path.join(ROOT, 'gen', 'dati.json'), encoding='utf-8'))
for x in D.get('instagram', []):
    s = os.path.join(ROOT, 'img', x['data'] + '-1.jpg')
    if os.path.exists(s):
        crop(s, os.path.join(ROOT, 'assets/ig', x['data'] + '.webp'), 720, 450, q=78)
        crop(s, os.path.join(ROOT, 'assets/ig', x['data'] + '-m.webp'), 160, 160)
