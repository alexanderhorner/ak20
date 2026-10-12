"""Rebuild the archival yearbook without changing the original or the website."""
from pathlib import Path
import re, json, hashlib, html, math, tempfile
import pymupdf as fitz
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from PIL import Image, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'storage/app/public/pdf/Abschlusszeitung2020.pdf'
OUT = ROOT / 'docs/yearbook/iterations/yearbook'
OUT.mkdir(parents=True, exist_ok=True)
W, H = 595.276, 841.89
INK, CREAM, CORAL, LIME, LILAC = '#202638', '#FAF6EC', '#F37962', '#D9ED88', '#CBC5F4'
PALETTE = [CORAL, LILAC, LIME]
for name, file in [('Body','FreeSans.ttf'),('Bold','FreeSansBold.ttf'),('Italic','FreeSansOblique.ttf')]:
    pdfmetrics.registerFont(TTFont(name, '/usr/share/fonts/truetype/freefont/' + file))
source = fitz.open(SOURCE)
c = canvas.Canvas(str(OUT / '_layout.pdf'), pagesize=(W,H))
c.setTitle('AK20 · Klasse 10a · Abschlussjahrbuch 2020')
c.setAuthor('Klasse 10a')
placements, units, photos, page_labels = [], [], [], []
page_no = 0

def raw(block):
    return '\n'.join(''.join(s['text'] for s in l['spans']) for l in block['lines'])

def clean(t):
    return re.sub(r'\s+', ' ', t.replace('\xad\n','').replace('\xad','').replace('\t',' ')).strip()

def esc(t):
    return html.escape(clean(t))

def label(t, x, y, size=10, color=INK, font='Bold'):
    c.setFillColor(color); c.setFont(font,size); c.drawString(x,H-y-size,t)

def rect(x,y,w,h,color,r=0):
    c.setFillColor(color)
    if r: c.roundRect(x,H-y-h,w,h,r,fill=1,stroke=0)
    else: c.rect(x,H-y-h,w,h,fill=1,stroke=0)

def para(markup,x,y,w,size=12,leading=None,font='Body',color=INK):
    p=Paragraph(markup,ParagraphStyle('p',fontName=font,fontSize=size,leading=leading or size*1.38,textColor=color))
    _,h=p.wrap(w,H)
    p.drawOn(c,x,H-y-h)
    return h

def star(x,y,r=15,color=INK):
    p=c.beginPath()
    for k in range(16):
        a=k*math.pi/8; rr=r if k%2==0 else r*.4
        xx=x+math.cos(a)*rr; yy=H-y+math.sin(a)*rr
        if k==0:p.moveTo(xx,yy)
        else:p.lineTo(xx,yy)
    p.close();c.setFillColor(color);c.drawPath(p,fill=1,stroke=0)

def start(section, accent=LILAC):
    global page_no
    page_no+=1;page_labels.append(section)
    rect(0,0,W,H,CREAM)
    rect(34,31,6,16,accent)
    label('AK20 / KLASSE 10a',49,32,9)
    label(section.upper(),335,32,9)
    c.setStrokeColor(INK);c.setLineWidth(.5);c.line(34,43,W-34,43)
    label('ABSCHLUSSJAHRBUCH 2020',34,805,8)
    label(f'{page_no:02}',W-53,801,13)

def finish():c.showPage()

def photo(src_index,bbox,x,y,w,h,key):
    b=fitz.Rect(bbox); scale=min(w/b.width,h/b.height)
    pw,ph=b.width*scale,b.height*scale
    xx,yy=x+(w-pw)/2,y+(h-ph)/2
    rect(xx-7,yy-7,pw+14,ph+28,'#FFFFFF',2)
    placements.append((page_no-1,src_index,tuple(b),tuple(fitz.Rect(xx,yy,xx+pw,yy+ph))))
    photos.append({'id':key,'source_page':src_index+1,'source_bbox':list(b),'output_page':page_no})
    return xx,yy,pw,ph

def record(t,kind,src):
    units.append({'kind':kind,'source_page':src+1,'output_page':page_no,'text':t})

# Cover: keep the complete original photo composition, including the cutout.
start('Unser Jahr',CORAL)
label('DAS WAREN',38,88,24)
label('WIR.',30,111,109)
rect(357,111,193,51,LIME,18);label('KLASSE 10a',373,122,23)
label('2020',350,171,59)
star(526,239,20,CORAL)
photo(0,(24.285,180.0446,571.485,609.1823),38,277,519,407,'cover-composition')
rect(41,730,258,38,LILAC,13);label('GROSSE PLÄNE. GUTE ERINNERUNGEN.',53,742,10)
for t in ['Klasse 10a','ak20.alexanderhorner.com','Passwort: Parameterverfahren']:record(t,'cover',0)
label('ak20.alexanderhorner.com',331,737,10)
label('Passwort: Parameterverfahren',331,753,9,font='Body')
finish()

# A navigable editorial opening, with all students listed.
profiles=[]
for i in range(1,16):
    blocks=source[i].get_text('dict')['blocks']
    for half in [0,1]:
        text=[b for b in blocks if b['type']==0 and (b['bbox'][1]>420)==bool(half)]
        images=[b for b in blocks if b['type']==1 and b['width']!=1539 and (b['bbox'][1]>420)==bool(half)]
        lines=raw(text[0]).splitlines()
        nickname=lines[-1] if lines[-1].startswith('„') else ''
        name=clean(' '.join(lines[:-1] if nickname else lines))
        profiles.append({'name':name,'nick':nickname,'blocks':text,'images':images,'source':i})
start('Inhalt',LIME)
label('Ein Jahr. Eine Klasse.',34,78,33)
para('30 Persönlichkeiten. Unzählige Erinnerungen.<br/>Unser Abschlussjahr zum Immer-wieder-Durchblättern.',36,128,470,13)
for title,desc,num,y in [('01 / DAS SIND WIR','Steckbriefe & Kinderfotos','03',199),('02 / MITTENDRIN','Unsere gemeinsamen Momente','33',272),('03 / UNSERE LEHRER','Eigenschaften, die bleiben','43',345),('04 / UNVERGESSEN','Historische Zitate','48',418)]:
    rect(34,y,527,61,PALETTE[int(num)%3],9);label(title,48,y+10,14);label(desc,48,y+33,11,font='Body');label(num,512,y+16,23)
label('DIE KLASSE 10a',36,519,13)
for n,p in enumerate(profiles):label(p['name'],36+(n//15)*270,552+(n%15)*14,10,font='Body')
finish()

# Each student gets a whole page: no shortened facts or traits.
for n,p in enumerate(profiles):
    accent=PALETTE[n%3];start('Das sind wir',accent)
    rect(464,75,97,36,accent,16);label(f'{n+1:02} / 30',482,86,13)
    name=p['name'];size=36
    while pdfmetrics.stringWidth(name,'Bold',size)>414:size-=1
    label(name,34,87,size)
    if p['nick']:label(p['nick'],37,141,19,font='Italic')
    photo(p['source'],p['images'][0]['bbox'],43,205,165,247,f'{name}: portrait')
    label('HEUTE',47,473,9)
    # The original separates the facts into one or two blocks.
    blocks=p['blocks'];trait_idx=next(j for j,b in enumerate(blocks) if 'Typische Eigenschaften:' in raw(b))
    facts=' '.join(raw(b) for b in blocks[1:trait_idx]);facts=clean(facts)
    fact_parts=re.split(r'(?=Wohnt in |Geboren am |Nach dem Abschluss:|Will in der Zukunft:)',facts)
    y=206
    for f in filter(None,fact_parts):
        match=re.match(r'(Wohnt in|Geboren am|Nach dem Abschluss:|Will in der Zukunft:)\s*(.*)',f)
        if match:
            label(match[1].rstrip(':').upper(),244,y,9,color='#686C78')
            y+=17; y+=para(esc(match[2]),244,y,301,13)+19
        else:y+=para(esc(f),244,y,301,13)+16
    assert y < 520, (name, 'facts exceed their area', y)
    rect(34,529,325,229,accent,13)
    label('Ganz typisch.',50,545,22)
    label('Typische Eigenschaften:',51,573,8)
    trait_text='\n'.join(raw(b) for b in blocks[trait_idx+1:])
    traits=[t for t in trait_text.split('•') if clean(t)]
    y=593
    for t in traits:
        # This original emoji uses a custom Type3 font; preserve its exact artwork.
        txt=esc(t)
        if '🦖' in txt:
            emoji_span=next(s for b in blocks for l in b.get('lines',[]) for s in l['spans'] if '🦖' in s['text'])
            emoji_path=OUT/'_emoji.png'
            source[p['source']].get_pixmap(matrix=fitz.Matrix(4,4),clip=emoji_span['bbox']).save(emoji_path)
            txt=txt.replace('🦖♥️',f'<img src="{emoji_path}" width="25" height="13" valign="middle"/>')
        label('•',50,y,12)
        y+=para(txt,65,y,274,12)+10
    assert y<755,(name,y)
    photo(p['source'],p['images'][1]['bbox'],395,555,150,190,f'{name}: childhood')
    label('DAMALS',400,766,9)
    star(391,518,19,accent)
    for b in blocks:record(raw(b),'profile',p['source'])
    finish()

# Photo chapter: every photo is shown in full with its original clipping/rotation.
start('Mittendrin',CORAL)
label('Weißt du',35,118,67);label('noch?',35,187,85)
para('Die Bilder. Die Momente. Die Menschen.<br/>Unsere gemeinsame Zeit in Schnappschüssen.',38,300,447,16)
rect(35,402,525,294,LILAC,18)
photo(16,source[16].get_text('dict')['blocks'][0]['bbox'],60,423,476,241,'chapter-preview')
label('MITTENDRIN / 2020',51,717,13)
star(502,307,27,CORAL);finish()
for i in range(16,25):
    accent=PALETTE[(i-16)%3];start('Mittendrin',accent)
    label('Unser Film in Bildern.',34,76,30)
    label(f'MOMENTE / {i-15:02}',36,123,10)
    images=[b for b in source[i].get_text('dict')['blocks'] if b['type']==1]
    # Reuse the original arrangement but give it airy margins and photo mounts.
    src_area=fitz.Rect(36,34,559.3,807)
    dest_area=fitz.Rect(50,174,545,766)
    scale=min(dest_area.width/src_area.width,dest_area.height/src_area.height)
    ox=dest_area.x0+(dest_area.width-src_area.width*scale)/2
    for j,b in enumerate(images):
        bb=fitz.Rect(b['bbox'])
        photo(i,bb,ox+(bb.x0-src_area.x0)*scale,dest_area.y0+(bb.y0-src_area.y0)*scale,bb.width*scale,bb.height*scale,f'memory-{i+1}-{j+1}')
    star(537,143,13,accent);finish()

# Four teachers, four pages. Keep all original anecdotes verbatim.
start('Unsere Lehrer',LILAC)
label('Die bleiben',35,126,65);label('im Kopf.',35,198,76)
para('Eigenschaften unserer Lehrer',39,316,490,22,font='Bold')
for j,name in enumerate(['Frau Bullard','Herr Schönberger','Herr Götz','Herr Hippe']):
    rect(38,410+j*66,519,50,PALETTE[j%3],12);label(name,56,424+j*66,21)
star(510,355,25,CORAL);finish()
for i in [25,26]:
    bs=source[i].get_text('dict')['blocks']
    teachers=[b for b in bs if b['type']==0 and raw(b).startswith(('Frau Bullard:','Herr Schönberger:','Herr Götz:','Herr Hippe:'))]
    imgs=[b for b in bs if b['type']==1]
    for j,b in enumerate(teachers):
        text=raw(b);name=text.split('\n')[0].rstrip(':');start('Unsere Lehrer',PALETTE[j%3])
        label(name,35,86,38)
        img=min(imgs,key=lambda x:abs((x['bbox'][1]+x['bbox'][3])/2-(b['bbox'][1]+b['bbox'][3])/2))
        photo(i,img['bbox'],386,181,150,205,name)
        rect(383,439,157,201,PALETTE[j%3],16)
        label('LEGENDÄR.',398,468,18);star(461,564,36,INK)
        y=184
        for t in text.split('•')[1:]:
            label('•',39,y,12);y+=para(esc(t),54,y,299,12)+12
        assert y<785,(name,y)
        record(text.split('\n')[0],'teacher-name',i)
        for trait in text.split('•')[1:]:record(trait,'teacher-trait',i)
        finish()

# Quote cards keep original dialogue groups together and flow across pages.
quote_groups=[]
for i in [27,28,29]:
    for b in source[i].get_text('dict')['blocks']:
        if b['type'] == 0 and b['bbox'][1] > (100 if i == 27 else 0):
            quote_groups.append((i,raw(b)))
# The decorative title fragments are typography, not quotes.
quote_groups=[(i,t) for i,t in quote_groups if clean(t) not in ['Zitate','Historische Z','Historische Zitate']]
quote_page=0;column=0;y=0
for n,(i,t) in enumerate(quote_groups):
    markup='<br/>'.join(esc(line) for line in t.replace('\xad\n','').splitlines())
    style=ParagraphStyle('quote',fontName='Body',fontSize=11,leading=15.2,textColor=INK)
    par=Paragraph(markup,style);_,height=par.wrap(222,1000)
    card_h=height+34
    if not quote_page or y+card_h>771:
        if quote_page and column==0:column=1;y=166
        else:
            if quote_page:finish()
            quote_page+=1;column=0;start('Historische Zitate',LIME)
            label('Das wurde wirklich gesagt.',34,80,30)
            label(f'HISTORISCHE ZITATE / {quote_page:02}',36,125,10);y=166
    assert card_h<605,(n,card_h)
    x=34+column*272
    rect(x,y,255,card_h,PALETTE[n%3],11)
    par.drawOn(c,x+16,H-y-17-height)
    record(t,'quote',i);y+=card_h+14
finish()
# Retain the tiny printed image on the original quotes page as a closing detail.
start('Bis bald',CORAL)
label('10a.',32,108,132)
label('Ein Kapitel bleibt.',37,290,40)
para('Abschluss 2020.<br/>Und so viele Geschichten, die bleiben.',40,365,440,18)
star(503,384,34,LILAC)
rect(37,492,520,180,LIME,18)
label('AK20',60,513,57)
label('KLASSE 10a / 2020',63,599,16)
for j,b in enumerate(source[28].get_text('dict')['blocks']):
    if b['type']==1:photo(28,b['bbox'],389,728,149,34,f'quote-detail-{j}')
label('Originalinhalt vollständig erhalten.',39,745,11,font='Body')
finish();c.save()

# Layer original PDF artwork into the new layout, retaining photo quality.
out=fitz.open(OUT/'_layout.pdf')
for dst,src,clip,target in placements:
    out[dst].show_pdf_page(fitz.Rect(target),source,src,clip=fitz.Rect(clip),keep_proportion=True)
out.embfile_add('Abschlusszeitung2020-original.pdf',SOURCE.read_bytes(),filename=SOURCE.name,desc='Unverändertes Original für die vollständige Archivierung')
toc=[[1,'Unser Jahr',1],[1,'Inhalt',2],[1,'Das sind wir',3]]
toc += [[2,p['name'],3+n] for n,p in enumerate(profiles)]
for section in ['Mittendrin','Unsere Lehrer','Historische Zitate','Bis bald']:
    toc.append([1,section,page_labels.index(section)+1])
out.set_toc(toc)
out.set_metadata({'title':'AK20 — Klasse 10a — Abschlussjahrbuch 2020','author':'Klasse 10a','subject':'Neugestaltetes Jahrbuch mit vollständigem Originalinhalt'})
PDF=OUT/'AK20-Jahrbuch-Redesign.pdf'
out.save(PDF,garbage=4,deflate=True)
out.close();out=fitz.open(PDF)

# Check every factual source block, not just overall character counts.
def normalize(t):
    return re.sub(r'\s+','',t.replace('\xad','').replace('🦖','').replace('♥','').replace('\ufe0f','').replace(':','').casefold())
failures=[]
for u in units:
    if normalize(u['text']) not in normalize(out[u['output_page']-1].get_text()):failures.append(u)
assert not failures, json.dumps(failures,ensure_ascii=False,indent=2)
assert out.embfile_get('Abschlusszeitung2020-original.pdf')==SOURCE.read_bytes()
expected_photos=sum(len([b for b in source[i].get_text('dict')['blocks'] if b['type']==1 and (i not in range(1,16) or b['width']!=1539)]) for i in range(1,30))
# Cover montage and chapter repeat count as additions, not lost source images.
assert len(photos)==expected_photos+2,(len(photos),expected_photos)
report={'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'source_pages':len(source),'redesigned_pages':len(out),'student_profiles':len(profiles),'verified_content_blocks':len(units),'photo_placements':len(photos),'original_attachment_byte_identical':True,'text_verification':'PASS (line wraps and discretionary hyphens normalized; original emoji artwork retained inline)','units':units,'photos':photos}
(OUT/'content-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
# Shareable overview and selected pages.
selected=[0,2,3,12,33,35,43,47]
thumbs=[]
for idx in selected:
    pix=out[idx].get_pixmap(matrix=fitz.Matrix(1.2,1.2),alpha=False)
    path=OUT/f'page-{idx+1:02}.png';pix.save(path)
    im=Image.open(path).convert('RGB');im.thumbnail((298,422))
    tile=Image.new('RGB',(330,460),'#E8E3D9');tile.paste(im,((330-im.width)//2,12))
    ImageDraw.Draw(tile).text((16,440),f'{idx+1:02} / {page_labels[idx]}',fill=INK)
    thumbs.append(tile)
sheet=Image.new('RGB',(1320,920),'#E8E3D9')
for i,im in enumerate(thumbs):sheet.paste(im,((i%4)*330,(i//4)*460))
sheet.save(OUT/'preview.jpg',quality=92)
for name in ['_layout.pdf','_emoji.png']:(OUT/name).unlink(missing_ok=True)
print(json.dumps({k:v for k,v in report.items() if k not in ['units','photos']},ensure_ascii=False,indent=2))
print(PDF)
