"""Real-content HTML prototypes -> print PDF -> original-quality PDF artwork.

All geometry is shared between the HTML prototype and the final PDF. The browser
lays out text and provides artwork coordinates. No website or original is changed.
"""
from pathlib import Path
import html, json, re, hashlib, math
import pymupdf as fitz
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT/'storage/app/public/pdf/Abschlusszeitung2020.pdf'
V1 = ROOT/'previews/yearbook/AK20-Jahrbuch-Redesign.pdf'
V2 = ROOT/'previews/yearbook-editorial/AK20-Jahrbuch-Editorial.pdf'
OUT = ROOT/'previews/yearbook-color'
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
def art(src,bbox,x,y,w,h,key,extra='',kind='photo'):
    b=fitz.Rect(bbox);s=min(w/b.width,h/b.height);pw,ph=b.width*s,b.height*s
    xx,yy=x+(w-pw)/2,y+(h-ph)/2
    item={'id':f'art-{len(image_items)}','key':key,'source':src,'clip':list(b),'kind':kind}
    image_items.append(item)
    # Prototypes only: alpha retains the source's transparency on ivory paper.
    # Final artwork is copied from the PDF, not resampled from this preview PNG.
    filename=f"{item['id']}.png"
    source[src].get_pixmap(matrix=fitz.Matrix(2,2),clip=b,alpha=True).save(ASSETS/filename)
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
    pages.append({'section':section,'html':f'<section class="page {cls} accent-{accent}" data-page="{n}"><header><span>AK20 / KLASSE 10a</span><span>{html.escape(section.upper())}</span></header><span class="chapter-tab" aria-hidden="true"></span>{body}{footer(n)}</section>'})

def star(x,y,size=20,color='red'):
    return f'<div class="spark {color}" aria-hidden="true" style="left:{x}pt;top:{y}pt;font-size:{size}pt">✳</div>'
def loop(x,y,w=100,h=35,color='red'):
    return f'<svg class="loop {color}" style="left:{x}pt;top:{y}pt;width:{w}pt;height:{h}pt" viewBox="0 0 100 35" aria-hidden="true"><path d="M1 27 C25 17 69 9 87 15 C114 25 61 43 33 19 C17 5 55 3 95 27"/></svg>'

def rosette(x,y,size=90,color='butter',background=False):
    petals=''.join(f'<ellipse cx="50" cy="24" rx="10" ry="22" transform="rotate({angle} 50 50)"/>' for angle in range(0,360,45))
    css='emblem-background' if background else 'motif'
    return f'<svg class="{css} rosette {color}" style="left:{x}pt;top:{y}pt;width:{size}pt;height:{size}pt" viewBox="0 0 100 100" aria-hidden="true"><g>{petals}</g><circle cx="50" cy="50" r="29" fill="var(--paper)"/></svg>'

def corner_motif(x,y,size=30):
    return f'<svg class="motif corner-motif" style="left:{x}pt;top:{y}pt;width:{size}pt;height:{size}pt" viewBox="0 0 40 40" aria-hidden="true"><path d="M0 0 H32 A32 32 0 0 1 0 32 Z" fill="var(--blue)"/><circle cx="29" cy="29" r="6" fill="var(--red)"/></svg>'

# Cover typography and original class-photo composition.
record('Klasse 10a','cover',0);record(NEW_URL,'cover-url',0);record('Passwort: Parameterverfahren','cover',0)
cover=f'''<div class="cover-title"><h1>Unser<br>Jahr<span class="red-text">.</span></h1><p class="cover-class">Klasse 10a</p></div>
{rosette(447,228,108,'butter',True)}<div class="year-seal">2020</div>{loop(385,147,130,62,'blue')}{corner_motif(498,91,36)}
{art(0,(24.285,180.0446,571.485,609.1823),38,342,519,398,'cover composition')}
<div class="cover-access"><a href="https://{NEW_URL}">{NEW_URL}</a><span>Passwort: Parameterverfahren</span></div>'''
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
<span class="photo-caption then">KINDERFOTO</span><span class="photo-caption now">KLASSE 10a</span>{loop(214,414,90,14,'blue')}
</div><div class="profile-copy"><dl class="facts">{facts}</dl><section class="traits"><h2>Typische<br><em>Eigenschaften:</em></h2><ul>{traits}</ul></section></div>'''
    add('Steckbriefe',body,'student', ['red','blue','butter','lilac'][n%4])

# Editorial chapter openers use bold typography and the original photographs.
add('Fotos',f'''<div id="memory-intro" class="chapter-title"><span class="eyebrow">02 / FOTOS</span><h1>Fotos<span class="red-text">.</span></h1><p>Klasse 10a · 2020</p></div>{rosette(466,282,68,'butter')}{loop(350,298,99,33,'red')}
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
<div class="teacher-index">{''.join(f'<div><span>0{j+1}</span><b>{name}</b></div>' for j,name in enumerate(['Frau Bullard','Herr Schönberger','Herr Götz','Herr Hippe']))}</div>{rosette(456,295,65,'red')}{loop(391,691,134,39,'blue')}''','chapter-opener teacher-opener')
for i in [25,26]:
    bs=source[i].get_text('dict')['blocks'];tb=[b for b in bs if b['type']==0 and raw(b).startswith(('Frau Bullard:','Herr Schönberger:','Herr Götz:','Herr Hippe:'))];ib=[b for b in bs if b['type']==1]
    for j,b in enumerate(tb):
        text=raw(b);name=text.split('\n')[0].rstrip(':');traits=text.split('•')[1:]
        record(text.split('\n')[0],'teacher-name',i)
        for trait in traits:record(trait,'teacher-trait',i)
        img=min(ib,key=lambda q:abs((q['bbox'][1]+q['bbox'][3])/2-(b['bbox'][1]+b['bbox'][3])/2))
        body=f'''<div class="teacher-title"><h1>{esc(name)}</h1><span class="eyebrow">EIGENSCHAFTEN UNSERER LEHRER</span></div>
<ul class="teacher-traits">{''.join(f'<li>{esc(t)}</li>' for t in traits)}</ul><div class="teacher-photo-mount"></div>
{art(i,img['bbox'],364,211,178,244,name)}<span class="teacher-caption">UNSERE LEHRER / 2020</span>{rosette(398,528,88,'butter',True)}<span class="teacher-badge">{1+j if i==25 else 3+j:02}</span>{loop(384,636,126,32,'blue')}'''
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

CSS='''
@font-face{font-family:Fraunces;src:url('../../../tools/yearbook/fonts/Fraunces-Display.ttf');font-weight:600}
@font-face{font-family:FrauncesText;src:url('../../../tools/yearbook/fonts/Fraunces-Text.ttf')}
@font-face{font-family:FrauncesItalic;src:url('../../../tools/yearbook/fonts/Fraunces-Italic.ttf')}
@font-face{font-family:Manrope;src:url('../../../tools/yearbook/fonts/Manrope-Regular.ttf');font-weight:400}
@font-face{font-family:Manrope;src:url('../../../tools/yearbook/fonts/Manrope-Semibold.ttf');font-weight:600}
@font-face{font-family:Mono;src:url('../../../tools/yearbook/fonts/IBMPlexMono-Regular.ttf')}
:root{--ink:#30243b;--paper:#f7f1e6;--red:#c7523c;--blue:#b9d0d7;--butter:#eed88b;--lilac:#d7c9df;--line:#cbbfc1;--muted:#5f5360}
*{box-sizing:border-box}body{margin:0;padding:24px;background:#ded7cf;color:var(--ink);font-family:Manrope,sans-serif;font-size:11pt;line-height:1.45}
main{display:grid;grid-template-columns:repeat(2,210mm);gap:24px;justify-content:center}.page{width:210mm;height:297mm;position:relative;background:var(--paper);overflow:hidden}
h1,h2,p,dl,dt,dd,ul,ol{margin:0}h1,h2{font-family:Fraunces;font-weight:600;line-height:1.02}em{font-family:FrauncesItalic;font-weight:400;font-style:normal}
a{color:inherit;text-decoration:none}.red-text{color:var(--red)}header{position:absolute;left:38pt;right:38pt;top:29pt;display:flex;justify-content:space-between;font:7.5pt Mono,monospace;letter-spacing:.55pt;border-bottom:.45pt solid var(--line);padding-bottom:16pt}
footer{position:absolute;left:38pt;right:38pt;bottom:24pt;display:flex;justify-content:space-between;align-items:baseline;font:7pt Mono,monospace;letter-spacing:.4pt}.folio{font:15pt FrauncesText;letter-spacing:0}
.eyebrow,.photo-caption,.opener-caption,.teacher-caption{font:7.5pt Mono,monospace;letter-spacing:.5pt}.native-art{position:absolute;display:block;object-fit:contain}.spark,.loop{position:absolute;pointer-events:none}.spark{color:var(--red);font-family:serif}.spark.blue{color:var(--blue)}.spark.butter{color:var(--butter)}.loop path{fill:none;stroke:var(--red);stroke-width:1.35;stroke-linecap:round}.loop.blue path{stroke:#627f94}.loop.red path{stroke:var(--red)}
.cover-title{position:absolute;left:38pt;top:84pt}.cover-title h1{font-size:87pt;letter-spacing:-2pt;line-height:.93}.cover-class{font:25pt FrauncesText;margin-top:22pt}.year-seal{position:absolute;left:462pt;top:238pt;width:83pt;height:83pt;border:1pt solid #627f94;border-radius:50%;display:flex;align-items:center;justify-content:center;font:24pt FrauncesItalic;color:var(--red);transform:rotate(-8deg)}.cover-access{position:absolute;left:38pt;right:38pt;top:756pt;display:flex;justify-content:space-between;align-items:baseline;font-size:9pt}.cover-access span{font-size:8pt}
.opening{position:absolute;left:38pt;top:86pt;right:38pt}.opening h1{font-size:41pt;margin:20pt 0 15pt}.opening h1 em{font-size:36pt}.opening p{font-size:11pt}.chapter-index{position:absolute;left:38pt;right:38pt;top:290pt}.chapter-index a{display:grid;grid-template-columns:40pt 1fr 28pt;align-items:baseline;padding:13pt 0;border-top:.5pt solid var(--line)}.chapter-index b{font:11pt Mono;color:var(--red)}.chapter-index span{font:22pt FrauncesText}.chapter-index i{font:13pt FrauncesText}.class-list-heading{position:absolute;left:38pt;top:526pt;font-size:20pt}.class-list{position:absolute;left:38pt;right:38pt;top:566pt;columns:2;column-gap:30pt;list-style:none;font-size:9pt;line-height:14pt}.class-list li{break-inside:avoid}.class-list a{display:flex;justify-content:space-between}.class-list a span:last-child{font:8pt Mono;color:var(--muted)}
.profile-title{position:absolute;left:38pt;top:92pt;width:261pt}.profile-title h1 span{display:block}.first-name{font:29pt FrauncesText;line-height:1.12}.surname{font-size:43pt;margin-top:3pt;letter-spacing:-.8pt;line-height:1.06}.nickname{font:19pt FrauncesItalic;margin-top:15pt}.student-index{position:absolute;left:235pt;top:344pt;font:26pt FrauncesText;color:var(--red);text-align:center}.student-index small{display:block;font:7pt Mono;margin-top:6pt;color:var(--muted)}.child-mount{position:absolute;left:40pt;top:231pt;width:137pt;height:178pt;background:var(--butter)}.accent-blue .child-mount{background:var(--blue)}.accent-lilac .child-mount{background:var(--lilac)}.accent-butter .child-mount{background:#e2c2b6}.photo-caption{position:absolute;top:418pt;color:var(--muted)}.then{left:46pt}.now{right:39pt}.profile-copy{position:absolute;top:449pt;left:38pt;right:38pt}.facts{border-top:.55pt solid var(--line);border-bottom:.55pt solid var(--line);padding:9pt 0}.fact-row{display:grid;grid-template-columns:140pt 1fr;gap:21pt;padding:5pt 0;align-items:baseline;break-inside:avoid}.fact-row dt{font:8.2pt Mono,monospace;letter-spacing:.2pt;color:var(--muted)}.fact-row dd{font-size:11.5pt;line-height:16.5pt;padding-left:12pt;border-left:.5pt solid var(--line)}.traits{display:grid;grid-template-columns:140pt 1fr;gap:21pt;margin-top:20pt}.traits h2{font-size:23pt;line-height:1.12}.trait-label{display:block;font:8pt Mono,monospace;letter-spacing:0;margin-top:14pt}.traits ul{list-style:none;padding:0 0 0 12pt}.traits li,.teacher-traits li{position:relative;padding-left:12pt;font-size:11.5pt;line-height:17pt;margin-bottom:7pt;break-inside:avoid}.traits li::before,.teacher-traits li::before{content:'•';position:absolute;left:0;color:var(--red)}.emoji{position:relative;display:inline-block;width:24pt;height:12.5pt;vertical-align:-2pt}
.chapter-title{position:absolute;left:38pt;top:91pt;right:38pt}.chapter-title h1{font-size:68pt;line-height:.97;margin:34pt 0 23pt;letter-spacing:-1.2pt}.chapter-title p{font-size:12pt}.opener-caption{position:absolute;top:757pt;left:49pt;color:var(--muted)}.memory-title{position:absolute;left:38pt;top:90pt}.memory-title h1{font-size:43pt;margin-bottom:15pt}.gallery-photo{outline:4pt solid #fffdf8}.teacher-index{position:absolute;left:38pt;right:38pt;top:420pt}.teacher-index div{display:flex;gap:28pt;align-items:baseline;padding:19pt 0;border-bottom:.5pt solid var(--line)}.teacher-index span{font:11pt Mono;color:var(--red)}.teacher-index b{font:24pt FrauncesText}
.teacher-title{position:absolute;left:38pt;right:38pt;top:91pt}.teacher-title h1{font-size:44pt;letter-spacing:-.8pt;margin-bottom:23pt}.teacher-traits{position:absolute;left:38pt;top:210pt;width:298pt;list-style:none;padding:0}.teacher-traits li{margin-bottom:9pt}.teacher-photo-mount{position:absolute;left:357pt;top:204pt;width:192pt;height:258pt;background:var(--blue)}.accent-butter .teacher-photo-mount{background:var(--butter)}.teacher-caption{position:absolute;left:365pt;top:477pt;font-size:6.8pt}
.quote-title{position:absolute;left:38pt;top:91pt;right:38pt}.quote-title h1{font-size:51pt}.quote-subtitle{font:20pt FrauncesItalic;margin-top:13pt}.quote-columns{position:absolute;left:38pt;right:38pt;top:209pt;display:grid;grid-template-columns:1fr 1fr;gap:26pt}.quote-column{min-width:0}.quote{margin-bottom:15pt;padding-bottom:14pt;border-bottom:.45pt solid var(--line);break-inside:avoid}.quote-rule{width:26pt;height:1.5pt;background:var(--red);margin-bottom:11pt}.quote:nth-child(3n+2) .quote-rule{background:#627f94}.quote:nth-child(3n) .quote-rule{background:#b39738}.quote p{font-size:11.5pt;line-height:17pt}.quote b{font-weight:600}.fact-row dd,.traits li,.teacher-traits li,.quote p{text-wrap:pretty}
.back-title{position:absolute;left:38pt;top:124pt}.back-title h1{font-size:128pt;letter-spacing:-5pt}.back-title p{font:38pt FrauncesItalic;margin-top:20pt}.back-access{position:absolute;left:40pt;top:694pt;font:14pt FrauncesText}.back-access a{display:block;font:10pt Manrope;margin-top:20pt}

/* Color is assigned to sections; softer profile colors group each person's material. */
:root{--paper:#FBF5E9;--red:#BD503A;--blue:#8BB9C7;--butter:#EDCD57;--lilac:#BAA1D0;--line:#C8BDB2}
.accent-red{--accent:#E58C73;--wash:#F6E3D7}.accent-blue{--accent:#A2C7D2;--wash:#E6EFF0}.accent-butter{--accent:#EBD16B;--wash:#FAF0CA}.accent-lilac{--accent:#C6AED8;--wash:#EEE4F2}
.motif,.emblem-background{position:absolute;pointer-events:none}.rosette g{fill:var(--butter)}.rosette.blue g{fill:var(--blue)}.rosette.red g{fill:#DD7C63}.rosette.profile g{fill:var(--accent)}
.chapter-tab{position:absolute;right:0;top:83pt;width:17pt;height:46pt;border-radius:9pt 0 0 9pt;background:var(--red)}.group-photo .chapter-tab{background:var(--blue)}.group-teacher .chapter-tab{background:var(--butter)}.group-quote .chapter-tab{background:var(--lilac)}.group-other .chapter-tab{display:none}
.cover,.back{background:#FAEDC2}.cover::before{content:'';position:absolute;inset:735pt 0 0;background:var(--paper);border-radius:34pt 0 0 0}.year-seal{left:469pt;top:250pt;width:64pt;height:64pt;border:0;background:var(--paper);font-size:22pt;transform:rotate(-6deg)}
.opening h1{font-size:49pt;margin-top:19pt;margin-bottom:15pt}.chapter-index{top:228pt}.chapter-index a{padding:12pt 16pt;border-top:0;border-left:4pt solid var(--red);margin-bottom:7pt;background:#F6E3D7}.chapter-index a:nth-child(2){border-color:var(--blue);background:#E6EFF0}.chapter-index a:nth-child(3){border-color:var(--butter);background:#FAF0CA}.chapter-index a:nth-child(4){border-color:var(--lilac);background:#EEE4F2}.chapter-index span{font-size:21pt}.class-list-heading{top:490pt}.class-list{top:531pt}
.student::before{content:'';position:absolute;left:0;right:0;top:73pt;height:366pt;background:var(--wash);border-radius:0 0 30pt 0}.profile-title{width:276pt}.student-index{left:226pt;top:347pt;width:58pt;height:32pt;text-align:center;font-size:29pt;line-height:1;color:var(--ink)}.child-mount{left:38pt;width:123pt;height:175pt;background:var(--accent)}.accent-blue .child-mount,.accent-lilac .child-mount,.accent-butter .child-mount{background:var(--accent)}.photo-caption.then{left:38pt}.photo-caption.now{right:38pt}.traits{padding:16pt 14pt;margin-top:20pt;background:var(--wash);border-radius:0 18pt 18pt 0;grid-template-columns:140pt 1fr}.traits h2{font-size:19pt;line-height:1.22}.traits h2 em{font-size:18pt}.traits ul{padding-left:0}
.photo-opener{background:#E6EFF0}.photo-opener .chapter-title h1{font-size:89pt}.opener-caption{top:716pt;left:48pt}.memory::before{content:'';position:absolute;left:0;right:0;top:73pt;height:92pt;background:#E6EFF0;border-radius:0 0 24pt 0}.gallery-photo{outline:0}.gallery-mount{position:absolute;background:#FFFDF6;border-radius:2pt}.memory-title h1{font-size:43pt}
.teacher-opener{background:#FAF0CA}.teacher-index{top:377pt}.teacher-index div{padding:20pt 0}.teacher::before{content:'';position:absolute;left:0;right:0;top:73pt;height:113pt;background:#FAF0CA;border-radius:0 0 24pt 0}.teacher-photo-mount{background:var(--butter)}.teacher-caption{font-size:7.5pt}
.quotes::before{content:'';position:absolute;left:0;right:0;top:73pt;height:95pt;background:#EEE4F2;border-radius:0 0 24pt 0}.quote-title h1{font-size:42pt}.quote-columns{top:190pt}.quote-rule{width:31pt;height:2pt;border-radius:1pt}.quote:nth-child(3n+2) .quote-rule{background:#577F90}.quote:nth-child(3n) .quote-rule{background:#B99831}
.teacher-badge{position:absolute;left:421pt;top:556pt;width:42pt;text-align:center;font:28pt FrauncesText;line-height:1}.back-access a{margin-top:0;font-size:11pt}.back-title p{font-size:43pt}

@page{size:A4;margin:0}@media print{html,body{margin:0;padding:0;background:white}main{display:block}.page{break-after:page;break-inside:avoid}.page:last-child{break-after:auto}.native-art{visibility:hidden}a{color:inherit;text-decoration:none}}
'''

def document(pages_to_write):
    return '<!doctype html><html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>AK20 · Yearbook color prototype</title><style>'+CSS+'</style><main>'+''.join(p['html'] for p in pages_to_write)+'</main></html>'

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
    for qi,sheet in enumerate(quote_sheets):
        for column in sheet:
            for q in column:record(q['text'],'quote',q['src'])
        body=f'<div {"id=quotes-start" if qi==0 else ""} class="quote-title"><h1>Historische Zitate<span class="red-text">.</span></h1></div><div class="quote-columns">'+''.join('<div class="quote-column">'+''.join(q['html'] for q in column)+'</div>' for column in sheet)+'</div>'
        add('Historische Zitate',body,'quotes')
    add('Bis bald',f'''<div class="back-title"><h1>10a<span class="red-text">.</span></h1><p>2020</p></div>{rosette(418,432,116,'blue')}{loop(310,577,138,53,'red')}
<div class="back-access"><a href="https://{NEW_URL}">{NEW_URL}</a></div>
{art(28,next(b for b in source[28].get_text('dict')['blocks'] if b['type']==1)['bbox'],431,740,115,25,'original quote-page arrow') }''','back')
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
    selected=[0,1,2,21,32,33,42,43,47]
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
        # Photos must never cover text. Decorative loops are intentionally exempt.
        for a in p['art']:
            if image_items[int(a['id'].split('-')[1])]['kind']=='emoji':continue
            for t in p['text']:
                overlap_w=min(a['x']+a['w'],t['x']+t['w'])-max(a['x'],t['x'])
                overlap_h=min(a['y']+a['h'],t['y']+t['h'])-max(a['y'],t['y'])
                assert not(overlap_w>1 and overlap_h>1),(p['page'],a,t,'photo overlaps text')
    # The final PDF is this very HTML: fonts, line wrapping and spacing are shared.
    page.emulate_media(media='print');page.pdf(path=str(OUT/'_browser.pdf'),prefer_css_page_size=True,print_background=True)
    browser.close()
measurement_html.unlink()

# Place original PDF photos at the exact DOM-measured positions.
pdf=fitz.open(OUT/'_browser.pdf');assert len(pdf)==len(pages),(len(pdf),len(pages))
# Normalize Chromium's sub-point paper rounding to exact ISO A4 geometry.
for sheet in pdf:sheet.set_mediabox(fitz.Rect(0,0,W,H))
for p in dom:
    for a in p['art']:
        item=image_items[int(a['id'].split('-')[1])]
        target=fitz.Rect(a['x'],a['y'],a['x']+a['w'],a['y']+a['h'])
        pdf[p['page']-1].show_pdf_page(target,source,item['source'],clip=fitz.Rect(item['clip']))
        if item['kind']=='photo':photos.append({'id':item['key'],'source_page':item['source']+1,'source_bbox':item['clip'],'output_page':p['page']})
pdf.embfile_add(SOURCE.name,SOURCE.read_bytes(),filename=SOURCE.name,desc='Unverändertes Original für die vollständige Archivierung')
toc=[[1,'Unser Jahr',1],[1,'Inhalt',2],[1,'Steckbriefe',3]]+[[2,p['name'],i+3] for i,p in enumerate(profiles)]
for section in ['Fotos','Unsere Lehrer','Historische Zitate','Bis bald']:toc.append([1,section,next(i+1 for i,p in enumerate(pages) if p['section']==section)])
pdf.set_toc(toc);pdf.set_metadata({'title':'AK20 · Klasse 10a · 2020 — Farbe','author':'Klasse 10a','subject':'Abschlussjahrbuch 2020; vollständiger Originalinhalt; ak20.alexanderhorner.de'})
FINAL=OUT/'AK20-Jahrbuch-Farbe.pdf';pdf.save(FINAL,garbage=4,deflate=True);pdf.close();pdf=fitz.open(FINAL)
failures=[]
for u in units:
    if norm(u['text']) not in norm(pdf[u['output_page']-1].get_text()):failures.append(u)
assert not failures,json.dumps(failures,ensure_ascii=False,indent=2)
# Confirm the PDF retained the HTML positions of independently measurable text.
matched_spans=0;max_type_drift=0
for page_info in dom:
    spans=[s for b in pdf[page_info['page']-1].get_text('dict')['blocks'] if b['type']==0 for l in b['lines'] for s in l['spans']]
    for t in page_info['text']:
        matches=[s for s in spans if s['text'].strip()==t['text'].strip()]
        if not matches:continue  # wrapped text is covered by the complete-content check
        drift=min(max(abs(s['bbox'][0]-t['x']),abs(s['bbox'][1]-t['y'])) for s in matches)
        assert drift<1.5,(page_info['page'],t['text'],'HTML/PDF type drift',drift)
        max_type_drift=max(max_type_drift,drift);matched_spans+=1
assert matched_spans>800,('too few matched typography samples',matched_spans)
assert all(abs(p.rect.width-W)<.001 and abs(p.rect.height-H)<.001 for p in pdf)
assert pdf.embfile_get(SOURCE.name)==SOURCE.read_bytes()
assert hashlib.sha256(V1.read_bytes()).hexdigest()==original_v1_hash
assert hashlib.sha256(V2.read_bytes()).hexdigest()==original_v2_hash
assert NEW_URL in pdf[0].get_text() and OLD_URL not in ''.join(p.get_text() for p in pdf)
assert sum(1 for p in pdf for link in p.get_links() if link.get('uri','').rstrip('/')=='https://'+NEW_URL)==2
expected=sum(len([b for b in source[i].get_text('dict')['blocks'] if b['type']==1 and (i not in range(1,16) or b['width']!=1539)]) for i in range(1,30))
assert len(photos)==expected+2,(len(photos),expected)
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
report={'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'version_one_unchanged_sha256':original_v1_hash,'version_two_unchanged_sha256':original_v2_hash,'redesigned_pages':len(pdf),'student_profiles':30,'verified_content_units':len(units),'original_photo_placements':len(photos),'visible_website':NEW_URL,'original_attachment_byte_identical':True,'html_and_pdf_share_layout':True,'all_pages_pass_dom_geometry_checks':True,'html_pdf_matched_text_spans':matched_spans,'maximum_type_position_drift_pt':round(max_type_drift,3),'page_size_mm':[210,297],'verification':'PASS','units':units,'photos':photos,'geometry':dom}
(OUT/'content-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
# Every page gets rendered for visual inspection. Selected pages are shared.
thumbs=[]
selected=[0,1,2,21,32,33,42,43,47]
for i,p in enumerate(pdf):
    pix=p.get_pixmap(matrix=fitz.Matrix(.7,.7),alpha=False)
    image=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
    if i in selected:
        p.get_pixmap(matrix=fitz.Matrix(1.35,1.35),alpha=False).save(OUT/f'page-{i+1:02}.png')
    image.thumbnail((142,202));tile=Image.new('RGB',(154,224),'#DED7CF');tile.paste(image,((154-image.width)//2,5));ImageDraw.Draw(tile).text((6,210),f'{i+1:02}',fill='#30243b');thumbs.append(tile)
contact=Image.new('RGB',(1232,math.ceil(len(pdf)/8)*224),'#DED7CF')
for i,im in enumerate(thumbs):contact.paste(im,((i%8)*154,(i//8)*224))
contact.save(OUT/'all-pages.jpg',quality=94)
preview=Image.new('RGB',(1050,1485),'#DED7CF')
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
