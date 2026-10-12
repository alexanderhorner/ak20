"""Document the final design system using the same HTML and type as the book."""
from pathlib import Path
import re
from playwright.sync_api import sync_playwright
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'previews/yearbook-editorial';PROTO=OUT/'prototype'
source=(PROTO/'index.html').read_text()
css=re.search(r'<style>(.*?)</style>',source,re.S).group(1)
EXTRA='''
.study-body{position:absolute;left:38pt;right:38pt;top:87pt}.study-body h1{font-size:37pt;margin-bottom:22pt}.study-body h2{font-size:23pt;margin:24pt 0 13pt}.study-body p{font-size:11.5pt;line-height:1.5}.study-body .intro{max-width:480pt}.concept{width:519pt;height:504pt;object-fit:contain;margin:14pt 0 9pt}.study-caption{font:8pt Mono;color:var(--muted)}.swatches{display:grid;grid-template-columns:repeat(6,1fr);gap:10pt;margin-top:30pt}.swatch b{height:43pt;display:block}.swatch span{font:7.2pt Mono;display:block;margin-top:8pt}.specimen{padding:18pt 0;border-bottom:.5pt solid var(--line)}.specimen .meta{font:8pt Mono;color:var(--muted);margin-bottom:12pt}.display-spec{font:35pt Fraunces}.italic-spec{font:26pt FrauncesItalic}.body-spec{font:11.5pt Manrope}.mono-spec{font:8.2pt Mono;letter-spacing:.2pt}.rules{display:grid;grid-template-columns:137pt 1fr;gap:22pt;padding:18pt 0;border-bottom:.5pt solid var(--line)}.rules dt{font:17pt FrauncesText}.rules dd{font-size:11pt;line-height:1.55}@media print{.native-art{visibility:visible}}
'''
def page(body,n,header='DESIGN STUDY'):
 return f'<section class="page"><header><span>AK20 / EDITORIAL EDITION</span><span>{header}</span></header><div class="study-body">{body}</div><footer><span>DESIGN SYSTEM / PRINT PROOF</span><span class="folio">{n:02}</span></footer></section>'
first=page('''<h1>Timeless. With personality.</h1><p class="intro">Expressive serif typography, generous photography and a warm paper palette. A little playfulness in the details; the people and their stories lead the page.</p><img class="concept" src="../concept-board.png" alt="Image-tool concept board"><p class="study-caption">Built-in image generation · visual exploration only.<br>The final book uses the original class photographs and factual content.</p>''',1)
colors=[('INK','#30243B'),('PAPER','#F7F1E6'),('RED','#C7523C'),('BLUE','#B9D0D7'),('BUTTER','#EED88B'),('LILAC','#D7C9DF')]
swatches=''.join(f'<div class="swatch"><b style="background:{hex}"></b><span>{name}<br>{hex}</span></div>' for name,hex in colors)
second=page(f'''<h1>Type, color, rhythm.</h1><p>Ivory and aubergine form the base. Tomato red is the primary accent; the quieter supporting colors appear in small photo mounts.</p><div class="swatches">{swatches}</div><div class="specimen"><p class="meta">FRAUNCES DISPLAY · 600 / OPTICAL SIZE 72</p><p class="display-spec">Unser Jahr. Unsere Geschichten.</p></div><div class="specimen"><p class="meta">FRAUNCES TEXT & ITALIC · 400</p><p class="italic-spec">Kleine Sätze. Große Erinnerungen.</p></div><div class="specimen"><p class="meta">MANROPE · 400 / 600 · BODY 11–11.5 PT</p><p class="body-spec">Thirty complete student profiles. All names, dates, plans, wishes and anecdotes stay intact. Comfortable line lengths and measured spacing make the text easy to revisit.</p></div><div class="specimen"><p class="meta">IBM PLEX MONO · LABELS 8.2 PT / CAPTIONS 7.5 PT</p><p class="mono-spec">WOHNT IN / GEBOREN AM / DAMALS / HEUTE</p></div>''',2)
fourth=page('''<h1>Built for the page.</h1><dl><div class="rules"><dt>Grid</dt><dd>ISO A4, 210 × 297 mm. Outer margins: 38 pt (13.4 mm). Photo-led profile header, shared biographical rows and a consistent two-column reading structure.</dd></div><div class="rules"><dt>Typography</dt><dd>Readable body text, dark field labels, manually fitted long surnames, and embedded fonts. Italics add warmth; fine rules establish the rhythm without heavy boxes.</dd></div><div class="rules"><dt>Playfulness</dt><dd>A red full stop, a small year medallion, a restrained pen loop and colored childhood-photo mounts. Decorative marks stay clear of text and photographs.</dd></div><div class="rules"><dt>Print</dt><dd>52 pages with exact A4 geometry and safe outer margins. The PDF retains selectable vector text and original PDF photo artwork, with the source resolution preserved.</dd></div><div class="rules"><dt>Implementation</dt><dd>The real-content HTML prototype generates the PDF. Browser-measured positions place the original artwork. 1,135 matching text positions differ by less than one point.</dd></div><div class="rules"><dt>Preservation</dt><dd>All 215 content units and 88 photo placements checked. The original PDF is attached unchanged. Version one remains intact. The authorized website update is ak20.alexanderhorner.de.</dd></div></dl>''',4)
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=['--no-sandbox']);tab=b.new_page(viewport={'width':1650,'height':1250})
 tab.goto((PROTO/'index.html').as_uri());tab.evaluate('document.fonts.ready')
 third=tab.locator('.page').nth(2).evaluate('(e)=>e.outerHTML')
 study='<html lang="en"><meta charset="utf-8"><title>AK20 Design System</title><style>'+css+EXTRA+'</style><main>'+first+second+third+fourth+'</main></html>'
 path=PROTO/'design-system.html';path.write_text(study)
 tab.goto(path.as_uri());tab.evaluate('document.fonts.ready');tab.wait_for_function('Array.from(document.images).every(i=>i.complete)')
 for i in range(4):tab.locator('.page').nth(i).screenshot(path=str(OUT/f'design-study-{i+1:02}.png'))
 tab.emulate_media(media='print');tab.pdf(path=str(OUT/'AK20-Design-Study.pdf'),prefer_css_page_size=True,print_background=True)
 b.close()
sheet=Image.new('RGB',(1304,451),'#DED7CF')
for i in range(4):
 im=Image.open(OUT/f'design-study-{i+1:02}.png').convert('RGB');im.thumbnail((298,422));tile=Image.new('RGB',(326,451),'#DED7CF');tile.paste(im,((326-im.width)//2,10));ImageDraw.Draw(tile).text((14,432),f'Study {i+1:02}',fill='#30243B');sheet.paste(tile,(i*326,0))
sheet.save(OUT/'design-study-preview.jpg',quality=94)
print(OUT/'AK20-Design-Study.pdf')
