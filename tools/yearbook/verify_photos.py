"""Compare each original-source derivative with the published PDF photograph.

This independent raster comparison catches wrong links, rotations, reflections
and crops, which a placement-count or text audit cannot detect.
"""
from pathlib import Path
import json
import math
import tempfile

import pymupdf as fitz
from PIL import Image
from photo_derivatives import derivative

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / 'resources/design/yearbook'


def correlation(a, b):
    a = list(a.convert('L').resize((128,128),Image.Resampling.LANCZOS).crop((4,4,124,124)).get_flattened_data())
    b = list(b.convert('L').resize((128,128),Image.Resampling.LANCZOS).crop((4,4,124,124)).get_flattened_data())
    ma,mb=sum(a)/len(a),sum(b)/len(b)
    numerator=sum((x-ma)*(y-mb) for x,y in zip(a,b))
    denominator=math.sqrt(sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b))
    return numerator/denominator


def verify():
    catalog=json.loads((DESIGN/'photo-catalog.json').read_text())
    source=fitz.open(ROOT/'storage/app/public/pdf/Abschlusszeitung2020.pdf')
    scores=[]
    with tempfile.TemporaryDirectory(prefix='ak20-photo-audit-') as temporary:
        for n,item in enumerate(catalog['photos']):
            bbox=fitz.Rect(item['pdf_bbox'])
            file,export=derivative(DESIGN/'original',item,(bbox.width,bbox.height),Path(temporary)/str(n))
            pix=source[item['source_page']-1].get_pixmap(matrix=fitz.Matrix(1,1),clip=bbox,alpha=False)
            original=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
            with Image.open(file) as current:
                score=correlation(original,current)
            scores.append({'file':item['file'],'source_page':item['source_page'],
                           'correlation':round(score,5),
                           'reflected':item['layout_reflected_vertical_before_rotation']})
    scores.sort(key=lambda s:s['correlation'])
    report={'comparison':'Original PDF raster vs independently linked original-source crop',
            'compared_regions':len(scores),'minimum_correlation':scores[0]['correlation'],
            'threshold':.90,'results':scores}
    (DESIGN/'photo-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'compared_regions':len(scores),'lowest_matches':scores[:8]},ensure_ascii=False,indent=2))
    assert all(s['correlation']>.90 for s in scores),'Inspect mismatching photo in photo-verification.json'


if __name__=='__main__':
    verify()
