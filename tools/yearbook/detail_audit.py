"""Inspect actual browser geometry and export full-size review proofs.

Read-only with respect to the book: reports go in a separate review directory.
Checks relationships between text, pictures, frames and print margins rather
than reproducing the renderer's coordinates.
"""
from pathlib import Path
import argparse
import json

import pymupdf as fitz
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
EDITION = ROOT / 'docs/yearbook/iterations/yearbook-jacket'

MEASURE = r'''() => Array.from(document.querySelectorAll('.page')).map((p, i) => {
 const origin=p.getBoundingClientRect();
 const rect=e=>{const r=e.getBoundingClientRect();return {x:(r.x-origin.x)*.75,y:(r.y-origin.y)*.75,w:r.width*.75,h:r.height*.75}};
 const element=e=>{const s=getComputedStyle(e);return {selector:e.className.baseVal||e.className,...rect(e),padding:['Top','Right','Bottom','Left'].map(k=>parseFloat(s['padding'+k])*.75),marginBottom:parseFloat(s.marginBottom)*.75,radii:['borderTopLeftRadius','borderTopRightRadius','borderBottomRightRadius','borderBottomLeftRadius'].map(k=>s[k]),overflowY:s.overflowY,scrollX:e.scrollWidth-e.clientWidth,scrollY:e.scrollHeight-e.clientHeight}};
 const firstText=e=>{if(!e)return null;const walk=document.createTreeWalker(e,NodeFilter.SHOW_TEXT);while(walk.nextNode()){if(!walk.currentNode.textContent.trim())continue;const r=document.createRange();r.selectNodeContents(walk.currentNode);const b=r.getClientRects()[0];if(b)return {x:(b.x-origin.x)*.75,y:(b.y-origin.y)*.75,w:b.width*.75,h:b.height*.75}}return null};
 const find=s=>p.querySelector(s); const get=s=>find(s)&&getComputedStyle(find(s)).display!=='none'?element(find(s)):null;
 const mounts=[...p.querySelectorAll('.child-mount,.teacher-photo-mount,.gallery-mount')].map(m=>{let image=m.nextElementSibling;if(!image?.matches('.native-art')){image=m.classList.contains('child-mount')?p.querySelector('.student-stage .native-art:nth-of-type(2)'):p.querySelector('.native-art:not(.emoji)')}if(m.classList.contains('child-mount')&&!image?.alt?.endsWith(': childhood'))image=[...p.querySelectorAll('.native-art')].find(e=>e.alt.endsWith(': childhood'));const a=image?rect(image):null;const b=rect(m);return {frame:element(m),image:a,alt:image?.alt,padding:a?[a.y-b.y,b.x+b.w-a.x-a.w,b.y+b.h-a.y-a.h,a.x-b.x]:null}});
 const traits=get('.traits'); const notes=find('.traits ul');
 const lastItem=notes?.lastElementChild;
 const pseudo=getComputedStyle(p,'::before');
 return {page:i+1,classes:p.className,name:find('.profile-title h1')?.textContent,header:get('header'),footer:get('footer'),title:get('.profile-title'),facts:get('.facts'),notes:traits,notesHeading:get('.traits h2'),notesList:get('.traits ul'),lastNote:lastItem?element(lastItem):null,factsText:firstText(find('.fact-row dd')),notesText:firstText(find('.traits li')),caption:get('.teacher-caption')||get('.photo-caption.then'),badge:get('.teacher-badge'),mounts,photoRects:[...p.querySelectorAll('.native-art:not(.emoji):not(.peeking-hands)')].map(e=>({alt:e.alt,...rect(e)})),bodyBounds:[...p.querySelectorAll('.profile-copy,.teacher-traits,.quote-column,.class-list,.back-access')].map(element),quoteColumns:[...p.querySelectorAll('.quote-column')].map(element),quotes:[...p.querySelectorAll('.quote')].map(element),outerCorners:['borderTopLeftRadius','borderTopRightRadius','borderBottomRightRadius','borderBottomLeftRadius'].map(k=>pseudo[k]),overflow:[...p.querySelectorAll('.fact-row dd,.traits li,.teacher-traits li,.quote p,.surname,.nickname,.class-list')].map(element).filter(e=>e.scrollX>1||(e.scrollY>1&&e.overflowY!=='visible'))};
})'''


def run(output, render):
    output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser=p.chromium.launch(args=['--no-sandbox'])
        tab=browser.new_page(viewport={'width':1650,'height':1250})
        tab.goto((EDITION/'prototype/index.html').as_uri());tab.evaluate('document.fonts.ready')
        tab.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)')
        data=tab.evaluate(MEASURE)
        tab.emulate_media(media='print')
        printed=tab.evaluate(MEASURE)
        browser.close()
    issues=[]
    clearances=[]
    for page in data:
        n=page['page']
        if page['overflow']:issues.append({'page':n,'issue':'overflow','details':page['overflow']})
        if page['factsText'] and page['notesText']:
            drift=page['notesText']['x']-page['factsText']['x']
            if abs(drift)>.3:issues.append({'page':n,'issue':'facts/anecdote text axes differ','difference_pt':round(drift,3)})
            if page['lastNote']['marginBottom']>.1:issues.append({'page':n,'issue':'extra margin after final anecdote','difference_pt':page['lastNote']['marginBottom']})
            for key in ['title','facts','notes']:
                drift=page[key]['x']-page['header']['x']
                if abs(drift)>.2:issues.append({'page':n,'issue':'profile element off page grid','element':key,'difference_pt':round(drift,3)})
            child=next(m for m in page['mounts'] if 'child-mount' in m['frame']['selector'])
            portrait=next(a for a in page['photoRects'] if a['alt'].endswith(': portrait'))
            if abs(child['frame']['x']-page['header']['x'])>.2:issues.append({'page':n,'issue':'child mount off page grid'})
            if abs(portrait['x']+portrait['w']-page['header']['x']-page['header']['w'])>.2:issues.append({'page':n,'issue':'profile portrait off outer page grid'})
            if abs(child['frame']['y']+child['frame']['h']-portrait['y']-portrait['h'])>.2:issues.append({'page':n,'issue':'profile photo baselines differ'})
            if abs(page['caption']['y']-child['frame']['y']-child['frame']['h']-12)>.2:issues.append({'page':n,'issue':'child caption gap inconsistent'})
        for body in page['bodyBounds']:
            gap=page['footer']['y']-body['y']-body['h']
            clearances.append({'page':n,'element':body['selector'],'gap_pt':round(gap,3)})
            if gap<24:issues.append({'page':n,'issue':'body crowds running footer','gap_pt':round(gap,3)})
        columns=page['quoteColumns']
        if columns and (abs(columns[0]['w']-columns[1]['w'])>.2 or abs(columns[0]['y']-columns[1]['y'])>.2):issues.append({'page':n,'issue':'quote columns unequal or misaligned'})
        for m in page['mounts']:
            if not m['padding']:issues.append({'page':n,'issue':'unpaired photo frame','frame':m['frame']});continue
            spread=max(m['padding'])-min(m['padding'])
            if spread>.2:issues.append({'page':n,'issue':'unequal photo frame padding','alt':m['alt'],'padding_pt':[round(v,3) for v in m['padding']]})
            if min(m['padding'])<2.8:issues.append({'page':n,'issue':'photo breaches mount','alt':m['alt']})
        if page['caption'] and 'teacher' in page['classes'] and page['mounts']:
            m=page['mounts'][0]['frame'];c=page['caption']
            outer=page['header']['x']+page['header']['w']
            if abs(m['x']+m['w']-outer)>.2:issues.append({'page':n,'issue':'teacher mount off outer page grid'})
            badge=page['badge']
            if abs(badge['x']+badge['w']/2-m['x']-m['w']/2)>.2:issues.append({'page':n,'issue':'teacher badge not centered under photograph'})
            if abs(c['x']-m['x'])>.2:issues.append({'page':n,'issue':'teacher caption not aligned to frame','difference_pt':round(c['x']-m['x'],3)})
            gap=c['y']-m['y']-m['h']
            if abs(gap-12)>.2:issues.append({'page':n,'issue':'teacher caption gap differs from profile caption gap','gap_pt':round(gap,3)})
        if 'side-left' in page['classes']:
            if any(t in page['classes'].split() for t in ['student','memory','teacher','quotes']):
                if page['outerCorners'][2]!='0px' or page['outerCorners'][3]=='0px':issues.append({'page':n,'issue':'header rounding on binding edge','radii':page['outerCorners']})
            if page['notes'] and (page['notes']['radii'][0]=='0px' or page['notes']['radii'][1]!='0px'):issues.append({'page':n,'issue':'anecdote rounding on binding edge','radii':page['notes']['radii']})
        photos=page['photoRects']
        if n==3:
            group=next(a for a in photos if a['alt']=='cover class photo')
            header=page['header']
            if abs(group['x']-header['x'])>.2 or abs(group['x']+group['w']-header['x']-header['w'])>.2:issues.append({'page':n,'issue':'class photograph off page grid'})
        for index,a in enumerate(photos):
            for b in photos[index+1:]:
                # The frontispiece intentionally layers the cutout behind the group.
                if n==3:continue
                x=min(a['x']+a['w'],b['x']+b['w'])-max(a['x'],b['x'])
                y=min(a['y']+a['h'],b['y']+b['h'])-max(a['y'],b['y'])
                if x>1 and y>1:issues.append({'page':n,'issue':'unintended photograph overlap','photos':[a['alt'],b['alt']]})
        # Screen prototypes and print use the same wrapping and placement.
        print_page=printed[n-1]
        for key in ['facts','notes','caption','title','header','footer']:
            if page[key] and print_page[key]:
                drift=max(abs(page[key][k]-print_page[key][k]) for k in ['x','y','w','h'])
                if drift>.02:issues.append({'page':n,'issue':'screen/print geometry differs','element':key,'difference_pt':round(drift,3)})
        for key in ['mounts','photoRects','bodyBounds','quoteColumns']:
            for screen,print_item in zip(page[key],print_page[key]):
                if key=='mounts':screen=screen['frame'];print_item=print_item['frame']
                drift=max(abs(screen[k]-print_item[k]) for k in ['x','y','w','h'])
                if drift>.02:issues.append({'page':n,'issue':'screen/print geometry differs','element':key,'difference_pt':round(drift,3)})
    # Visible serif ascenders can extend beyond a tight heading line box.
    # scrollHeight alone is not clipping; actual text collisions and printable
    # text bounds are verified independently by build_jacket.py.
    report={'pages':len(data),'relationship_issues':len(issues),'issues':issues,'screen_and_print_measured':True,'minimum_body_footer_clearance':min(clearances,key=lambda c:c['gap_pt']),'measurements':data}
    (output/'detail-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    if render:
        pdf=fitz.open(EDITION/'AK20-Jahrbuch-Web.pdf')
        for start in range(0,len(pdf),4):
            sheet=Image.new('RGB',(1648,2348),'#DED7CF');draw=ImageDraw.Draw(sheet)
            for offset in range(min(4,len(pdf)-start)):
                pix=pdf[start+offset].get_pixmap(matrix=fitz.Matrix(1.35,1.35),alpha=False)
                image=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
                x=(offset%2)*824+10;y=(offset//2)*1174+10
                sheet.paste(image,(x,y));draw.text((x,y+1143),f'PDF {start+offset+1:02} / {pdf[start+offset].get_label()}',fill='#30243B')
            sheet.save(output/f'review-{start+1:02}-{min(start+4,len(pdf)):02}.jpg',quality=95)
    print(json.dumps({'pages':len(data),'relationship_issues':len(issues),'minimum_body_footer_clearance':report['minimum_body_footer_clearance'],'issue_types':{name:sum(i['issue']==name for i in issues) for name in sorted({i['issue'] for i in issues})}},indent=2))
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);parser.add_argument('--render',action='store_true')
    args=parser.parse_args();report=run(args.output,args.render)
    raise SystemExit(1 if report['relationship_issues'] else 0)
