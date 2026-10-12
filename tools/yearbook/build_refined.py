"""Real-content HTML prototypes -> PDF with original-source photo derivatives.

All geometry is shared between the HTML prototype and the final PDF. The browser
lays out text; original-photo derivatives use the measured coordinates. Originals
and the live website remain unchanged.
"""
from pathlib import Path
import html, json, re, hashlib, math, sys
import pymupdf as fitz
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
from photo_derivatives import derivative
from verify_photos import correlation

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT/'storage/app/public/pdf/Abschlusszeitung2020.pdf'
V1 = ROOT/'docs/yearbook/iterations/yearbook/AK20-Jahrbuch-Redesign.pdf'
V2 = ROOT/'docs/yearbook/iterations/yearbook-editorial/AK20-Jahrbuch-Editorial.pdf'
OUT = ROOT/'docs/yearbook/iterations/yearbook-refined'
DESIGN = ROOT/'resources/design/yearbook'
CATALOG = json.loads((DESIGN/'photo-catalog.json').read_text())
V3 = ROOT/'docs/yearbook/iterations/yearbook-color/AK20-Jahrbuch-Farbe.pdf'
original_v3_hash = hashlib.sha256(V3.read_bytes()).hexdigest()
PROTO = OUT/'prototype'
ASSETS = PROTO/'assets'
for folder in [OUT,PROTO,ASSETS]: folder.mkdir(parents=True,exist_ok=True)
source=fitz.open(SOURCE)
W,H=595.276,841.89
OLD_URL='ak20.alexanderhorner.com'
NEW_URL='ak20.alexanderhorner.de'
original_v1_hash=hashlib.sha256(V1.read_bytes()).hexdigest()
original_v2_hash=hashlib.sha256(V2.read_bytes()).hexdigest()
units=[];photos=[];pages=[];image_items=[]

def raw(b):return '\n'.join(''.join(s['text'] for s in l['spans']) for l in b['lines'])
def clean(t):return re.sub(r'\s+',' ',t.replace('\xad\n','').replace('\xad','').replace('\t',' ')).strip()
def esc(t):return html.escape(clean(t))
def norm(t):return re.sub(r'\s+','',t.replace('\xad','').replace(':','').replace('•','').replace('🦖','').replace('♥','').replace('\ufe0f',''))
def record(t,kind,src):units.append({'kind':kind,'source_page':src+1,'output_page':len(pages)+1,'text':t})
def original_photo(src, bbox):
    matches=[p for p in CATALOG['photos'] if p['source_page']==src+1]
    item=min(matches,key=lambda p:sum((a-b)**2 for a,b in zip(p['pdf_bbox'],bbox)))
    assert max(abs(a-b) for a,b in zip(item['pdf_bbox'],bbox))<.01
    return item

def art(src,bbox,x,y,w,h,key,extra='',kind='photo',original=None):
    b=fitz.Rect(bbox);s=min(w/b.width,h/b.height);pw,ph=b.width*s,b.height*s
    xx,yy=x+(w-pw)/2,y+(h-ph)/2
    item={'id':f'art-{len(image_items)}','key':key,'source':src,'clip':list(b),'kind':kind}
    image_items.append(item)
    original=original or original_photo(src,bbox)
    path,export=derivative(DESIGN/'original',original,(pw,ph),ASSETS/item['id'])
    iw,ih=export['export_pixels'];scale=min(w/iw,h/ih)
    pw,ph=iw*scale,ih*scale
    xx,yy=x+(w-pw)/2,y+(h-ph)/2
    export['effective_ppi']=round(min(iw/pw,ih/ph)*72,1)
    if src>0:
        pix=source[src].get_pixmap(matrix=fitz.Matrix(1,1),clip=b,alpha=False)
        before=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
        with Image.open(path) as after: score=correlation(before,after)
        assert score>.90,('photo differs from original PDF',key,score)
        export['visual_correlation_with_original_pdf']=round(score,5)
    item['derivative']=str(path);item['original']=export
    filename=path.name
    mount=f'<span class="gallery-mount" style="left:{xx-3:.4f}pt;top:{yy-3:.4f}pt;width:{pw+6:.4f}pt;height:{ph+6:.4f}pt"></span>' if extra=='gallery-photo' else ''
    return mount+f'<img class="native-art {extra}" id="{item["id"]}" src="assets/{filename}" alt="{html.escape(key)}" style="left:{xx:.4f}pt;top:{yy:.4f}pt;width:{pw:.4f}pt;height:{ph:.4f}pt">'

def emoji_markup(t,src):
    value=esc(t)
    if '🦖' not in value:return value
    span=next(s for b in source[src].get_text('dict')['blocks'] for l in b.get('lines',[]) for s in l['spans'] if '🦖' in s['text'])
    item={'id':f'art-{len(image_items)}','key':'original dinosaur/heart emoji','source':src,'clip':list(span['bbox']),'kind':'emoji'}
    image_items.append(item);filename=f"{item['id']}.png"
    source[src].get_pixmap(matrix=fitz.Matrix(4,4),clip=span['bbox'],alpha=True).save(ASSETS/filename)
    return value.replace('🦖♥️',f'<img class="native-art emoji" id="{item["id"]}" src="assets/{filename}" alt="🦖♥️">')

def footer(n):return f'<footer><span>ABSCHLUSSJAHRBUCH / 2020</span><span class="folio">{n:02}</span></footer>'
def add(section,body,cls='',accent='red'):
    n=len(pages)+1
    group='profile' if cls=='student' else ('photo' if 'memory' in cls or 'photo-opener' in cls else ('teacher' if 'teacher' in cls else ('quote' if cls=='quotes' else 'other')))
    cls+=f' group-{group}'
    background=''
    if group=='profile':
        background='''<svg class="profile-background" viewBox="0 0 595.276 366" aria-hidden="true"><circle cx="123" cy="433" r="265" fill="var(--accent)" opacity=".16"/><circle cx="123" cy="433" r="211" fill="var(--wash)"/><circle cx="492" cy="-82" r="274" fill="var(--paper)" opacity=".30"/></svg>'''
    if cls.startswith('cover'):background+=illustration('arch',331,91,300,300,.50)
    if 'photo-opener' in cls:background+=illustration('fan',347,161,303,247,.45)
    if 'teacher-opener' in cls:background+=illustration('discs',348,114,270,270,.60)
    if cls.startswith('back'):background+=illustration('fan',255,326,390,390,.55)
    if cls.startswith('teacher '):background+='''<svg class="teacher-background" viewBox="0 0 240 260" aria-hidden="true"><circle cx="246" cy="160" r="174" fill="#EDCD57" opacity=".09"/><circle cx="246" cy="160" r="117" fill="var(--paper)"/></svg>'''
    background+='<span class="paper-grain" aria-hidden="true"></span>'
    pages.append({'section':section,'html':f'<section class="page {cls} accent-{accent}" data-page="{n}">{background}<header><span>AK20 / KLASSE 10a</span><span>{html.escape(section.upper())}</span></header><span class="chapter-tab" aria-hidden="true"></span>{body}{footer(n)}</section>'})

def illustration(name,x,y,w,h,opacity):
    svg=(DESIGN/f'illustrations/refined/{name}.svg').read_text()
    return svg.replace('<svg ',f'<svg class="chapter-illustration" aria-hidden="true" style="left:{x}pt;top:{y}pt;width:{w}pt;height:{h}pt;opacity:{opacity}" ',1)

def star(x,y,size=20,color='red'):
    return f'<div class="spark {color}" aria-hidden="true" style="left:{x}pt;top:{y}pt;font-size:{size}pt">✳</div>'
def rosette(x,y,size=90,color='butter',background=False):
    petals=''.join(f'<ellipse cx="50" cy="24" rx="10" ry="22" transform="rotate({angle} 50 50)"/>' for angle in range(0,360,45))
    css='emblem-background' if background else 'motif'
    return f'<svg class="{css} rosette {color}" style="left:{x}pt;top:{y}pt;width:{size}pt;height:{size}pt" viewBox="0 0 100 100" aria-hidden="true"><g>{petals}</g><circle cx="50" cy="50" r="29" fill="var(--paper)"/></svg>'

def corner_motif(x,y,size=30):
    return f'<svg class="motif corner-motif" style="left:{x}pt;top:{y}pt;width:{size}pt;height:{size}pt" viewBox="0 0 40 40" aria-hidden="true"><path d="M0 0 H32 A32 32 0 0 1 0 32 Z" fill="var(--blue)"/><circle cx="29" cy="29" r="6" fill="var(--red)"/></svg>'

# Cover typography and original class-photo composition.
record('Klasse 10a','cover',0)
cover=f'''<div class="cover-title"><h1>Unser<br>Jahr<span class="red-text">.</span></h1><p class="cover-class">Klasse 10a</p></div>
<div class="year-seal">2020</div>
{art(0,(0,0,86,110),38,350,86,110,'cover cutout',original=CATALOG['cover'][0])}
{art(0,(0,0,6000,4000),38,413,519,346,'cover class photo',original=CATALOG['cover'][1])}'''
add('Unser Jahr',cover,'cover')

# Extract the original profiles once. No rewrites or invented facts.
profiles=[]
for i in range(1,16):
    bs=source[i].get_text('dict')['blocks']
    for half in [0,1]:
        tb=[b for b in bs if b['type']==0 and (b['bbox'][1]>420)==bool(half)]
        ib=[b for b in bs if b['type']==1 and b['width']!=1539 and (b['bbox'][1]>420)==bool(half)]
        ls=raw(tb[0]).splitlines();nick=ls[-1] if ls[-1].startswith('„') else ''
        name=clean(' '.join(ls[:-1] if nick else ls))
        ti=next(j for j,b in enumerate(tb) if 'Typische Eigenschaften:' in raw(b))
        facts=clean(' '.join(raw(b) for b in tb[1:ti]));parts=[]
        for f in filter(None,re.split(r'(?=Wohnt in |Geboren am |Nach dem Abschluss:|Will in der Zukunft:)',facts)):
            m=re.match(r'(Wohnt in|Geboren am|Nach dem Abschluss:|Will in der Zukunft:)\s*(.*)',f)
            assert m,(name,f)
            parts.append((m[1],m[2]))
        traits=[t for t in '\n'.join(raw(b) for b in tb[ti+1:]).split('•') if clean(t)]
        profiles.append({'name':name,'nick':nick,'blocks':tb,'images':ib,'source':i,'facts':parts,'traits':traits})

contents=''.join(f'<li><a href="#student-{n}"><span>{esc(p["name"])}</span><span>{n+3:02}</span></a></li>' for n,p in enumerate(profiles))
add('Inhalt',f'''<div class="opening"><span class="eyebrow">KLASSE 10a / ABSCHLUSS 2020</span><h1>Inhalt<span class="red-text">.</span></h1><p>30 Steckbriefe · Fotos · Lehrer · Zitate</p></div>
<nav class="chapter-index"><a href="#student-0"><b>01</b><span>Steckbriefe</span><i>03</i></a><a href="#memory-intro"><b>02</b><span>Fotos</span><i>33</i></a><a href="#teacher-intro"><b>03</b><span>Unsere Lehrer</span><i>43</i></a><a href="#quotes-start"><b>04</b><span>Historische Zitate</span><i>48</i></a></nav>
<h2 class="class-list-heading">Die Klasse 10a</h2><ol class="class-list">{contents}</ol>{rosette(486,96,60,'blue')}''','contents')

for n,p in enumerate(profiles):
    for b in p['blocks']:record(raw(b),'profile',p['source'])
    first,surname=p['name'].split(' ',1)
    facts=''.join(f'<div class="fact-row"><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>' for k,v in p['facts'])
    traits=''.join(f'<li>{emoji_markup(t,p["source"])}</li>' for t in p['traits'])
    nickname=f'<p class="nickname">{esc(p["nick"])}</p>' if p['nick'] else ''
    body=f'''<div id="student-{n}" class="student-stage"><div class="profile-title"><h1><span class="first-name">{esc(first)}</span><span class="surname">{esc(surname)}</span></h1>{nickname}</div>
{rosette(211,319,88,'profile',True)}<span class="student-index">{n+1:02}</span><div class="child-mount"></div>
{art(p['source'],p['images'][0]['bbox'],350.34,96,206.66,310,p['name']+': portrait')}
{art(p['source'],p['images'][1]['bbox'],44,237,111,163,p['name']+': childhood')}
<span class="photo-caption then">KINDERFOTO</span><span class="photo-caption now">KLASSE 10a</span>
</div><div class="profile-copy"><dl class="facts">{facts}</dl><section class="traits"><h2>Typische<br><em>Eigenschaften:</em></h2><ul>{traits}</ul></section></div>'''
    add('Steckbriefe',body,'student', ['red','blue','butter','lilac'][n%4])

# Editorial chapter openers use bold typography and the original photographs.
add('Fotos',f'''<div id="memory-intro" class="chapter-title"><span class="eyebrow">02 / FOTOS</span><h1>Fotos<span class="red-text">.</span></h1><p>Klasse 10a · 2020</p></div>
{art(16,source[16].get_text('dict')['blocks'][0]['bbox'],48,355,499,362,'photo-chapter repeat')}
<span class="opener-caption">KLASSE 10a</span>''','chapter-opener photo-opener')
for i in range(16,25):
    ib=[b for b in source[i].get_text('dict')['blocks'] if b['type']==1]
    body=f'<div class="memory-title"><h1>Fotos<span class="red-text">.</span></h1><span class="eyebrow">02 / FOTOS / {i-15:02}</span></div>'
    area=fitz.Rect(36,34,559.3,807);dest=fitz.Rect(46,180,549,758)
    s=min(dest.width/area.width,dest.height/area.height);ox=dest.x0+(dest.width-area.width*s)/2
    for j,b in enumerate(ib):
        bb=fitz.Rect(b['bbox']);x=ox+(bb.x0-area.x0)*s;y=dest.y0+(bb.y0-area.y0)*s
        body+=art(i,bb,x,y,bb.width*s,bb.height*s,f'memory-{i+1}-{j+1}','gallery-photo')
    body+=corner_motif(510,93,29)
    add('Fotos',body,'memory', ['blue','butter','lilac'][i%3])

add('Unsere Lehrer',f'''<div id="teacher-intro" class="chapter-title"><span class="eyebrow">03 / LEHRER</span><h1>Unsere<br><em>Lehrer.</em></h1></div>
<div class="teacher-index">{''.join(f'<div><span>0{j+1}</span><b>{name}</b></div>' for j,name in enumerate(['Frau Bullard','Herr Schönberger','Herr Götz','Herr Hippe']))}</div>''','chapter-opener teacher-opener')
for i in [25,26]:
    bs=source[i].get_text('dict')['blocks'];tb=[b for b in bs if b['type']==0 and raw(b).startswith(('Frau Bullard:','Herr Schönberger:','Herr Götz:','Herr Hippe:'))];ib=[b for b in bs if b['type']==1]
    for j,b in enumerate(tb):
        text=raw(b);name=text.split('\n')[0].rstrip(':');traits=text.split('•')[1:]
        record(text.split('\n')[0],'teacher-name',i)
        for trait in traits:record(trait,'teacher-trait',i)
        img=min(ib,key=lambda q:abs((q['bbox'][1]+q['bbox'][3])/2-(b['bbox'][1]+b['bbox'][3])/2))
        body=f'''<div class="teacher-title"><h1>{esc(name)}</h1><span class="eyebrow">EIGENSCHAFTEN UNSERER LEHRER</span></div>
<ul class="teacher-traits">{''.join(f'<li>{esc(t)}</li>' for t in traits)}</ul><div class="teacher-photo-mount"></div>
{art(i,img['bbox'],364,211,178,244,name)}<span class="teacher-caption">UNSERE LEHRER / 2020</span>{rosette(398,528,88,'butter',True)}<span class="teacher-badge">{1+j if i==25 else 3+j:02}</span>'''
        add('Unsere Lehrer',body,'teacher', ['blue','butter'][j])

# Real dialogue, not invented sample quotations. Browser measures and paginates it.
quote_groups=[]
for i in [27,28,29]:
    for b in source[i].get_text('dict')['blocks']:
        if b['type']==0 and b['bbox'][1]>(100 if i==27 else 0):quote_groups.append((i,raw(b)))
quote_groups=[(i,t) for i,t in quote_groups if clean(t) not in ['Zitate','Historische Z','Historische Zitate']]
def dialogue(t):
    lines=[]
    for line in t.replace('\xad\n','').splitlines():
        # The original's hard-wrapped continuation lines become natural paragraphs.
        if lines and not re.match(r'^(?:[\wÄÖÜäöüß][^:]{0,65}:|\*|- etwas)',line):lines[-1]+=' '+line
        else:lines.append(line)
    result=[]
    for line in lines:
        m=re.match(r'^([^:]{1,65}:)(.*)$',line)
        result.append(f'<b>{esc(m[1])}</b> {esc(m[2])}' if m else esc(line))
    return '<br>'.join(result)
quote_cards=[]
for n,(src,text) in enumerate(quote_groups):
    quote_cards.append({'src':src,'text':text,'html':f'<article class="quote" data-quote="{n}"><div class="quote-rule"></div><p>{dialogue(text)}</p></article>'})

CSS=(DESIGN/'styles/refined.css').read_text()

def document(pages_to_write):
    return '<!doctype html><html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>AK20 · Yearbook refined prototype</title><style>'+CSS+'</style><main>'+''.join(p['html'] for p in pages_to_write)+'</main></html>'

# Finish quote pagination using actual font metrics in Chromium.
measurement_html=PROTO/'_measure.html'
measurement_html.write_text(document([{'html':f'<section class="page"><div class="quote-columns"><div class="quote-column">{"".join(q["html"] for q in quote_cards)}</div><div></div></div></section>'}]),encoding='utf-8')
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1650,'height':1250},device_scale_factor=1)
    page.goto(measurement_html.as_uri());page.evaluate('document.fonts.ready');page.wait_for_function('Array.from(document.images).every(i=>i.complete)')
    heights=page.locator('.quote').evaluate_all('(els)=>els.map(e=>e.getBoundingClientRect().height*72/96+15)')
    # Determine the minimum number of complete facing-column pages.
    bins=1;used=0
    for height in heights:
        assert height<566,('quote too tall',height)
        if used+height>566:bins+=1;used=0
        used+=height
    column_count=max(8,2*math.ceil(bins/2))
    target=sum(heights)/column_count
    prefix=[0]
    for h in heights:prefix.append(prefix[-1]+h)
    dp={(0,0):(0,[])}
    for count in range(1,column_count+1):
        for end in range(count,len(heights)+1):
            candidates=[]
            for begin in range(count-1,end):
                if (count-1,begin) not in dp:continue
                height=prefix[end]-prefix[begin]
                if height>566:continue
                cost,groups=dp[count-1,begin]
                candidates.append((cost+(height-target)**2,groups+[(begin,end)]))
            if candidates:dp[count,end]=min(candidates,key=lambda v:v[0])
    assert (column_count,len(heights)) in dp, 'balanced quote layout unavailable'
    groups=dp[column_count,len(heights)][1]
    columns=[quote_cards[a:b] for a,b in groups]
    quote_sheets=[[columns[i],columns[i+1]] for i in range(0,len(columns),2)]
    arrow_sheet=max(i for i,sheet in enumerate(quote_sheets) if any(q['src']==28 for col in sheet for q in col))
    for qi,sheet in enumerate(quote_sheets):
        for column in sheet:
            for q in column:record(q['text'],'quote',q['src'])
        body=f'<div {"id=quotes-start" if qi==0 else ""} class="quote-title"><h1>Historische Zitate<span class="red-text">.</span></h1></div><div class="quote-columns">'+''.join('<div class="quote-column">'+''.join(q['html'] for q in column)+'</div>' for column in sheet)+'</div>'
        if qi==arrow_sheet:
            body+=art(28,next(b for b in source[28].get_text('dict')['blocks'] if b['type']==1)['bbox'],500,768,57,12,'original quote-page arrow')
        add('Historische Zitate',body,'quotes')
    record(NEW_URL,'end-url',0);record('Passwort: Parameterverfahren','end-access',0)
    add('Bis bald',f'''<div class="back-title"><h1>10a<span class="red-text">.</span></h1><p>2020</p></div>
<div class="back-access"><a href="https://{NEW_URL}">{NEW_URL}</a><span>Passwort: Parameterverfahren</span></div>''','back')
    html_path=PROTO/'index.html';html_path.write_text(document(pages),encoding='utf-8')
    page.goto(html_path.as_uri());page.evaluate('document.fonts.ready');page.wait_for_function('Array.from(document.images).every(i=>i.complete)')
    assert page.evaluate("document.fonts.check('12px Fraunces') && document.fonts.check('12px Manrope') && document.fonts.check('12px Mono')"), 'fonts not loaded'
    # Fit the few long surnames within the same visual grid; never shrink body text.
    page.evaluate('''()=>{document.querySelectorAll('.surname').forEach(e=>{let size=43;e.style.fontSize=size+'pt';while(e.scrollWidth>e.clientWidth+1 && size>28){size-=.5;e.style.fontSize=size+'pt'}})}''')
    # Save deterministic fitted sizes into the HTML so reopening matches the PDF.
    sizes=page.locator('.surname').evaluate_all('(els)=>els.map(e=>e.style.fontSize)')
    for i,size in enumerate(sizes):
        pages[i+2]['html']=pages[i+2]['html'].replace('class="surname"',f'class="surname" style="font-size:{size}"')
    html_path.write_text(document(pages),encoding='utf-8')
    page.goto(html_path.as_uri());page.evaluate('document.fonts.ready');page.wait_for_function('Array.from(document.images).every(i=>i.complete)')
    # This is the HTML prototype stage, before PDF construction.
    selected=[0,1,2,21,32,33,42,43,47,51]
    for idx in selected:page.locator('.page').nth(idx).screenshot(path=str(OUT/f'html-page-{idx+1:02}.png'))
    # Geometry and overlap checks on every page, using actual rendered font bounds.
    dom=page.evaluate('''()=>Array.from(document.querySelectorAll('.page')).map((p,idx)=>{let r=p.getBoundingClientRect();let box=e=>{let b=e.getBoundingClientRect();return {x:(b.x-r.x)*.75,y:(b.y-r.y)*.75,w:b.width*.75,h:b.height*.75}};let content=[...p.querySelectorAll('.profile-copy,.teacher-traits,.quote-column,.class-list,.chapter-title,.back-access')].map(e=>({type:e.className,...box(e)}));let decor=[...p.querySelectorAll('.loop,.spark,.motif')].map(e=>({type:e.className.baseVal||e.className,...box(e)}));let art=[...p.querySelectorAll('.native-art')].map(e=>({id:e.id,...box(e)}));let text=[];let walker=document.createTreeWalker(p,NodeFilter.SHOW_TEXT);while(walker.nextNode()){let n=walker.currentNode;if(!n.textContent.trim() || n.parentElement.closest('.spark,.loop,.motif'))continue;let range=document.createRange();range.selectNodeContents(n);for(let b of range.getClientRects())text.push({heading:n.parentElement.closest('h1,h2')?[...p.querySelectorAll('h1,h2')].indexOf(n.parentElement.closest('h1,h2'))+1:0,text:n.textContent,x:(b.x-r.x)*.75,y:(b.y-r.y)*.75,w:b.width*.75,h:b.height*.75})}return {page:idx+1,content,art,text,decor}})''')
    for p in dom:
        for b in p['content']:
            assert b['y']+b['h']<787,(p['page'],b,'content collides with footer')
        for b in p['text']:
            assert b['x']>=35 and b['x']+b['w']<=W-32,(p['page'],b,'text exceeds outer margins')
            assert b['y']>=24 and b['y']+b['h']<=H-18,(p['page'],b,'text outside printable area')
        for ti,a in enumerate(p['text']):
            for b in p['text'][ti+1:]:
                if a['heading'] and a['heading']==b['heading']:continue
                ow=min(a['x']+a['w'],b['x']+b['w'])-max(a['x'],b['x'])
                oh=min(a['y']+a['h'],b['y']+b['h'])-max(a['y'],b['y'])
                assert not(ow>1 and oh>2),(p['page'],a,b,'separate text regions overlap')
        for a in p['decor']:
            for t in p['text']:
                ow=min(a['x']+a['w'],t['x']+t['w'])-max(a['x'],t['x'])
                oh=min(a['y']+a['h'],t['y']+t['h'])-max(a['y'],t['y'])
                assert not(ow>1 and oh>1),(p['page'],a,t,'decoration overlaps text')
        # Photos must never cover text. Background curves are intentionally underlays.
        for a in p['art']:
            if image_items[int(a['id'].split('-')[1])]['kind']=='emoji':continue
            for t in p['text']:
                overlap_w=min(a['x']+a['w'],t['x']+t['w'])-max(a['x'],t['x'])
                overlap_h=min(a['y']+a['h'],t['y']+t['h'])-max(a['y'],t['y'])
                assert not(overlap_w>1 and overlap_h>1),(p['page'],a,t,'photo overlaps text')
    # The final PDF is this very HTML: fonts, line wrapping and spacing are shared.
    (OUT/'layout.json').write_text(json.dumps(dom,ensure_ascii=False,indent=2))
    if '--prototype-only' in sys.argv:
        browser.close();measurement_html.unlink();print('HTML prototype ready:',html_path);sys.exit(0)
    page.emulate_media(media='print');page.pdf(path=str(OUT/'_browser.pdf'),prefer_css_page_size=True,print_background=True)
    browser.close()
measurement_html.unlink()

# Embed original-photo derivatives at the exact DOM-measured positions.
pdf=fitz.open(OUT/'_browser.pdf');assert len(pdf)==len(pages),(len(pdf),len(pages))
# Normalize Chromium's sub-point paper rounding to exact ISO A4 geometry.
for sheet in pdf:sheet.set_mediabox(fitz.Rect(0,0,W,H))
for p in dom:
    for a in p['art']:
        item=image_items[int(a['id'].split('-')[1])]
        target=fitz.Rect(a['x'],a['y'],a['x']+a['w'],a['y']+a['h'])
        if 'derivative' in item:
            pdf[p['page']-1].insert_image(target,filename=item['derivative'],keep_proportion=False)
        else:
            pdf[p['page']-1].show_pdf_page(target,source,item['source'],clip=fitz.Rect(item['clip']))
        if item['kind']=='photo':photos.append({'id':item['key'],'source_page':item['source']+1,'source_bbox':item['clip'],'output_page':p['page'],'original':item['original']})
# The complete originals are archived separately. Avoid attaching an 18 MB
# duplicate to a PDF intended for reading on the web.
# Replace Chromium's named anchors with portable, explicit PDF destinations.
# Absolute-positioned HTML can leave the first zero-height anchor unresolved,
# and named destinations do not survive extraction of the interior reliably.
anchor_pages={f'student-{n}':n+2 for n in range(30)}
anchor_pages.update({'memory-intro':32,'teacher-intro':42,'quotes-start':47})
contents_links=pdf[1].get_links()
assert len(contents_links)==34
for link in contents_links:
    anchor=link.get('nameddest')
    assert anchor in anchor_pages,('unexpected contents destination',link)
    pdf[1].delete_link(link)
    pdf[1].insert_link({'kind':fitz.LINK_GOTO,'from':link['from'],'page':anchor_pages[anchor],'to':fitz.Point(0,0)})
toc=[[1,'Unser Jahr',1],[1,'Inhalt',2],[1,'Steckbriefe',3]]+[[2,p['name'],i+3] for i,p in enumerate(profiles)]
for section in ['Fotos','Unsere Lehrer','Historische Zitate','Bis bald']:toc.append([1,section,next(i+1 for i,p in enumerate(pages) if p['section']==section)])
pdf.set_toc(toc);pdf.set_metadata({'title':'AK20 · Klasse 10a · 2020 — Verfeinert','author':'Klasse 10a','subject':'Abschlussjahrbuch 2020; vollständiger Originalinhalt; ak20.alexanderhorner.de'})
FINAL=OUT/'AK20-Jahrbuch-Verfeinert.pdf';pdf.save(FINAL,garbage=4,deflate=True);pdf.close();pdf=fitz.open(FINAL)
failures=[]
for u in units:
    if norm(u['text']) not in norm(pdf[u['output_page']-1].get_text()):failures.append(u)
assert not failures,json.dumps(failures,ensure_ascii=False,indent=2)
# Confirm the PDF retained the HTML positions of independently measurable text.
matched_spans=0;max_type_drift=0
for page_info in dom:
    spans=[s for b in pdf[page_info['page']-1].get_text('dict',flags=fitz.TEXTFLAGS_DICT & ~fitz.TEXT_PRESERVE_IMAGES)['blocks'] if b['type']==0 for l in b['lines'] for s in l['spans']]
    for t in page_info['text']:
        matches=[s for s in spans if s['text'].strip()==t['text'].strip()]
        if not matches:continue  # wrapped text is covered by the complete-content check
        drift=min(max(abs(s['bbox'][0]-t['x']),abs(s['bbox'][1]-t['y'])) for s in matches)
        assert drift<1.5,(page_info['page'],t['text'],'HTML/PDF type drift',drift)
        max_type_drift=max(max_type_drift,drift);matched_spans+=1
assert matched_spans>800,('too few matched typography samples',matched_spans)
assert all(abs(p.rect.width-W)<.001 and abs(p.rect.height-H)<.001 for p in pdf)
assert pdf.embfile_count()==0
assert hashlib.sha256(V1.read_bytes()).hexdigest()==original_v1_hash
assert hashlib.sha256(V2.read_bytes()).hexdigest()==original_v2_hash
assert hashlib.sha256(V3.read_bytes()).hexdigest()==original_v3_hash
archive_manifest=json.loads((DESIGN/'original-manifest.json').read_text())
for f in archive_manifest['files']:
    assert hashlib.sha256((DESIGN/'original'/f['path']).read_bytes()).hexdigest()==f['sha256']
assert {p['original']['file'] for p in photos}=={f['file'] for f in CATALOG['frames']}
assert NEW_URL not in pdf[0].get_text() and 'Passwort' not in pdf[0].get_text()
assert NEW_URL in pdf[-1].get_text() and 'Passwort: Parameterverfahren' in pdf[-1].get_text()
assert OLD_URL not in ''.join(p.get_text() for p in pdf)
assert sum(1 for p in pdf for link in p.get_links() if link.get('uri','').rstrip('/')=='https://'+NEW_URL)==1
expected=sum(len([b for b in source[i].get_text('dict')['blocks'] if b['type']==1 and (i not in range(1,16) or b['width']!=1539)]) for i in range(1,30))
assert len(photos)==expected+3,(len(photos),expected)
expected_image_regions={(i+1,tuple(round(v,4) for v in b['bbox'])) for i in range(1,30) for b in source[i].get_text('dict')['blocks'] if b['type']==1 and (i not in range(1,16) or b['width']!=1539)}
placed_image_regions={(p['source_page'],tuple(round(v,4) for v in p['source_bbox'])) for p in photos if p['source_page']!=1}
assert expected_image_regions==placed_image_regions, 'source image region coverage differs'

# Verify text using the source independently of the first version's audit.
source_units=[]
for i in range(1,16):source_units.extend(raw(b) for b in source[i].get_text('dict')['blocks'] if b['type']==0)
source_units.extend(raw(b) for i in [25,26] for b in source[i].get_text('dict')['blocks'] if b['type']==0 and raw(b).startswith(('Frau Bullard:','Herr Schönberger:','Herr Götz:','Herr Hippe:')))
source_units.extend(t for _,t in quote_groups)
assert len(source_units)==len([u for u in units if u['kind']=='profile'])+4+len(quote_groups)
# Independently confirm all extracted source paragraphs were recorded intact.
recorded=''.join(norm(u['text']) for u in units)
for t in source_units:assert norm(t) in recorded,('unrecorded source text',t)
report={'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'version_one_unchanged_sha256':original_v1_hash,'version_two_unchanged_sha256':original_v2_hash,'favorite_color_version_unchanged_sha256':original_v3_hash,'redesigned_pages':len(pdf),'student_profiles':30,'verified_content_units':len(units),'original_photo_placements':len(photos),'visible_website':NEW_URL,'original_archive_files_verified':len(archive_manifest['files']),'originals_archived_separately':True,'original_photo_files_used':len({p['original']['file'] for p in photos}),'pdf_bytes':FINAL.stat().st_size,'photo_export_target_ppi':240,'all_exported_photos_match_original_orientation_and_crop':True,'minimum_source_photo_visual_correlation':min(p['original'].get('visual_correlation_with_original_pdf',1) for p in photos),'jpeg_quality':91,'cover_access_removed':True,'access_on_last_page_only':True,'html_and_pdf_share_layout':True,'contents_links_resolve':34,'all_pages_pass_dom_geometry_checks':True,'html_pdf_matched_text_spans':matched_spans,'maximum_type_position_drift_pt':round(max_type_drift,3),'page_size_mm':[210,297],'verification':'PASS','units':units,'photos':photos,'geometry':dom}
(OUT/'content-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
# Every page gets rendered for visual inspection. Selected pages are shared.
thumbs=[]
selected=[0,1,2,21,32,33,42,43,47,51]
for i,p in enumerate(pdf):
    pix=p.get_pixmap(matrix=fitz.Matrix(.7,.7),alpha=False)
    image=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
    if i in selected:
        p.get_pixmap(matrix=fitz.Matrix(1.35,1.35),alpha=False).save(OUT/f'page-{i+1:02}.png')
    image.thumbnail((142,202));tile=Image.new('RGB',(154,224),'#DED7CF');tile.paste(image,((154-image.width)//2,5));ImageDraw.Draw(tile).text((6,210),f'{i+1:02}',fill='#30243b');thumbs.append(tile)
contact=Image.new('RGB',(1232,math.ceil(len(pdf)/8)*224),'#DED7CF')
for i,im in enumerate(thumbs):contact.paste(im,((i%8)*154,(i//8)*224))
contact.save(OUT/'all-pages.jpg',quality=94)
preview=Image.new('RGB',(1050,1980),'#DED7CF')
for i,idx in enumerate(selected):
    im=Image.open(OUT/f'page-{idx+1:02}.png').convert('RGB');im.thumbnail((320,453));preview.paste(im,((i%3)*350+15,(i//3)*495+12));ImageDraw.Draw(preview).text(((i%3)*350+15,(i//3)*495+472),f'{idx+1:02} / {pages[idx]["section"]}',fill='#30243b')
preview.save(OUT/'preview.jpg',quality=94)
# Grayscale spread proof: typography must also work without accent colors.
gray=Image.new('RGB',(1050,742),'white')
for pos,idx in enumerate([2,33]):
    pix=pdf[idx].get_pixmap(matrix=fitz.Matrix(.88,.88),colorspace=fitz.csGRAY,alpha=False)
    im=Image.frombytes('L',(pix.width,pix.height),pix.samples).convert('RGB')
    gray.paste(im,(pos*525,0))
gray.save(OUT/'grayscale-print-proof.jpg',quality=94)
(OUT/'_browser.pdf').unlink()
print(json.dumps({k:v for k,v in report.items() if k not in ['units','photos','geometry']},ensure_ascii=False,indent=2))
print(FINAL)
