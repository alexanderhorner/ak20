"""Save a design study and HTML proof before exporting the yearbook PDF."""
from pathlib import Path
import re
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/yearbook/iterations/yearbook-print'
PROTO = OUT / 'prototype'
source = (PROTO / 'index.html').read_text()
css = re.search(r'<style>(.*?)</style>', source, re.S).group(1)
extra = '''
.study{position:absolute;left:38pt;right:38pt;top:91pt}.study h1{font-size:40pt;margin-bottom:23pt}.study p{font-size:11pt;line-height:17pt}.study h2{font-size:22pt;margin:27pt 0 13pt}.swatches{display:flex;gap:12pt;margin:20pt 0 20pt}.swatches div{flex:1}.swatches b{display:block;height:43pt}.swatches span{display:block;font:7.2pt Mono;margin-top:7pt}.type-sample{padding:10pt 0;border-bottom:.5pt solid var(--line)}.type-sample p{font:8pt Mono;color:var(--muted);margin-bottom:10pt}.type-sample b{font:32pt Fraunces}.type-sample em{font-size:26pt}.roles{display:grid;grid-template-columns:1fr 1fr;gap:25pt}.roles h2{font-size:20pt}.roles p{font-size:10pt;line-height:16pt}.role-art{height:82pt;margin:10pt 0;position:relative;overflow:hidden;background:#F6E3D7}.role-art svg{position:absolute;width:160pt;height:160pt;right:-12pt;top:-32pt}.role-art.quiet svg{width:260pt;height:160pt;right:-45pt;top:0}.study .study-caption{font:7.5pt Mono;line-height:13pt;margin-top:17pt;color:var(--muted)}@media print{.native-art{visibility:visible}}
'''
colors = [('INK', '#30243B'), ('PAPER', '#FBF5E9'), ('PROFILE', '#BD503A'),
          ('PHOTOS', '#8BB9C7'), ('TEACHERS', '#EDCD57'), ('QUOTES', '#BAA1D0')]
swatches = ''.join(f'<div><b style="background:{c}"></b><span>{n}<br>{c}</span></div>' for n, c in colors)
art = (ROOT / 'resources/design/yearbook/illustrations/refined/arch.svg').read_text()
quiet = '<svg viewBox="0 0 260 160"><circle cx="110" cy="220" r="155" fill="#E58C73" opacity=".16"/><circle cx="110" cy="220" r="120" fill="#F6E3D7"/></svg>'
first = f'''<section class="page"><header><span>AK20 / DESIGNSTUDIE</span><span>FORM UND FLÄCHE</span></header><div class="study"><h1>Farbe, Form und Fläche<span class="red-text">.</span></h1><p>Die Farbversion bleibt die Grundlage. Große Kurven bilden eine ruhige zweite Ebene; abstrakte Kompositionen markieren die Kapitel.</p><div class="swatches">{swatches}</div><div class="type-sample"><p>FRAUNCES / NAMEN UND TITEL</p><b>Klasse 10a. 2020.</b></div><div class="type-sample"><p>FRAUNCES ITALIC / AKZENTE</p><em>Typische Eigenschaften:</em></div><div class="type-sample"><p>MANROPE 11.5 PT / IBM PLEX MONO 7.5–8.2 PT</p><span>Lesetext, Fakten, Beschriftungen und Seitenzahlen.</span></div><div class="roles"><div><h2>Kapitelillustration</h2><div class="role-art">{art}</div><p>Größere Bögen und Halbkreise, in der freien Fläche komponiert. Kräftigere Farbe; bewusst am Seitenrand angeschnitten.</p></div><div><h2>Hintergrund</h2><div class="role-art quiet">{quiet}</div><p>Breite Kurven im Farbton des Steckbriefs. Leichtes Korn. Text und Fotos bleiben klar davor; keine einzelnen Bildstempel.</p></div></div><p class="study-caption">45 PT BUND / 31 PT AUSSENRAND / 20 PT GRUPPENABSTAND<br>240 PPI FOTOZIEL / JPEG 91 / VEKTORTEXT UND -FORMEN</p></div><footer><span>DESIGN / HTML-PROTOTYP</span><span class="folio">01</span></footer></section>'''
with sync_playwright() as p:
    browser = p.chromium.launch(args=['--no-sandbox'])
    tab = browser.new_page(viewport={'width':1650, 'height':1250})
    tab.goto((PROTO / 'index.html').as_uri()); tab.evaluate('document.fonts.ready')
    specimens = [tab.locator('.page').nth(i).evaluate('(e)=>e.outerHTML') for i in [0,2,42]]
    path = PROTO / 'design-system.html'
    path.write_text('<!doctype html><html lang="de"><meta charset="utf-8"><title>AK20 Designstudie</title><style>'+css+extra+'</style><main>'+first+''.join(specimens)+'</main></html>')
    tab.goto(path.as_uri()); tab.evaluate('document.fonts.ready')
    tab.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)')
    assert tab.locator('.study').evaluate('(e)=>(e.getBoundingClientRect().bottom-e.closest(".page").getBoundingClientRect().top)*.75')<787
    for i in range(4):
        tab.locator('.page').nth(i).screenshot(path=str(OUT/f'design-study-{i+1:02}.png'))
    if '--pdf' in __import__('sys').argv:
        tab.emulate_media(media='print')
        tab.pdf(path=str(OUT/'AK20-Designstudie-Druck.pdf'),prefer_css_page_size=True,print_background=True)
    browser.close()
sheet=Image.new('RGB',(1304,451),'#DED7CF')
for i in range(4):
    im=Image.open(OUT/f'design-study-{i+1:02}.png').convert('RGB');im.thumbnail((298,422))
    sheet.paste(im,(i*326+(326-im.width)//2,10));ImageDraw.Draw(sheet).text((i*326+14,432),f'{i+1:02}',fill='#30243B')
sheet.save(OUT/'design-study-preview.jpg',quality=94)
print(path)
