"""Index the unmodified InDesign package and resolve photos to PDF regions.

IDML frame transforms provide the page/position; no filename guessing is needed.
The resulting manifest is also the editable source for future photo regrouping.
"""
from pathlib import Path
from zipfile import ZipFile
from urllib.parse import unquote, urlparse
import hashlib
import json
import math
import xml.etree.ElementTree as ET

import pymupdf as fitz
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / 'resources/design/yearbook'
PACKAGE = DESIGN / 'original'
SOURCE = ROOT / 'storage/app/public/pdf/Abschlusszeitung2020.pdf'


def matrix(element):
    return fitz.Matrix(*map(float, element.get('ItemTransform', '1 0 0 1 0 0').split()))


def rectangle(points):
    return fitz.Rect(min(p.x for p in points), min(p.y for p in points),
                     max(p.x for p in points), max(p.y for p in points))


def catalog():
    frames = []
    with ZipFile(PACKAGE / 'Abschlusszeitung 10a.idml') as archive:
        for name in sorted(archive.namelist()):
            if not name.startswith('Spreads/') or not name.endswith('.xml'):
                continue
            tree = ET.fromstring(archive.read(name))
            parents = {child: parent for parent in tree.iter() for child in parent}
            spread = next(tree.iter('Spread'))
            pages = []
            for page in spread.findall('Page'):
                y0, x0, y1, x1 = map(float, page.get('GeometricBounds').split())
                rect = fitz.Rect(x0, y0, x1, y1) * matrix(page)
                pages.append((int(page.get('Name')), rect))
            for link in spread.iter('Link'):
                image = parents[link]
                frame = parents[image]
                anchors = frame.findall('Properties/PathGeometry/GeometryPathType/PathPointArray/PathPointType')
                if not anchors:
                    raise ValueError(('Missing frame geometry', link.attrib))
                transform = matrix(frame)
                parent = parents[frame]
                while parent != spread:
                    transform = transform * matrix(parent)
                    parent = parents[parent]
                points = [fitz.Point(*map(float, a.get('Anchor').split())) * transform for a in anchors]
                spread_rect = rectangle(points)
                page_number, page_rect = max(pages, key=lambda p: (p[1] & spread_rect).get_area())
                local = fitz.Rect(spread_rect.x0 - page_rect.x0, spread_rect.y0 - page_rect.y0,
                                  spread_rect.x1 - page_rect.x0, spread_rect.y1 - page_rect.y0)
                graphic = image.find('Properties/GraphicBounds')
                image_rect = fitz.Rect(*(float(graphic.get(k)) for k in ['Left', 'Top', 'Right', 'Bottom']))
                image_transform = matrix(image) * transform
                bounds = image_rect * image_transform
                crop = [(spread_rect.x0 - bounds.x0) / bounds.width,
                        (spread_rect.y0 - bounds.y0) / bounds.height,
                        (spread_rect.x1 - bounds.x0) / bounds.width,
                        (spread_rect.y1 - bounds.y0) / bounds.height]
                crop = [max(0, min(1, v)) for v in crop]
                rotation = round(math.degrees(math.atan2(image_transform.b, image_transform.a)) / 90) * 90
                filename = Path(unquote(urlparse(link.get('LinkResourceURI')).path)).name
                path = PACKAGE / 'Links' / filename
                assert path.is_file(), ('Missing linked original', filename)
                with Image.open(path) as im:
                    orientation = im.getexif().get(274, 1)
                    oriented = ImageOps.exif_transpose(im)
                    size = list(oriented.size)
                frames.append({'file': 'Links/' + filename, 'source_page': page_number,
                               'frame_bbox': list(local), 'image_id': image.get('Self'),
                               'oriented_pixels': size, 'exif_orientation': orientation,
                               'layout_rotation_degrees_clockwise': rotation,
                               'layout_reflected_vertical_before_rotation': image_transform.a*image_transform.d-image_transform.b*image_transform.c<0,
                               'image_transform': list(image_transform),
                               'crop_normalized': crop,
                               'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    source = fitz.open(SOURCE)
    regions = []
    for i, page in enumerate(source):
        for block in page.get_text('dict')['blocks']:
            if block['type'] != 1 or (i in range(1, 16) and block['width'] == 1539):
                continue  # the old decorative backdrop is superseded
            if i == 0:
                continue  # cover's shadow is a duplicate, mapped separately below
            candidates = [f for f in frames if f['source_page'] == i + 1]
            b = fitz.Rect(block['bbox'])
            def distance(f):
                r = fitz.Rect(f['frame_bbox'])
                return sum((r[k] - b[k]) ** 2 for k in range(4))
            chosen = min(candidates, key=distance)
            # Full image extents can differ from their clipped frame by a few points.
            assert distance(chosen) < 100, (i + 1, b, chosen, distance(chosen))
            regions.append({**chosen, 'pdf_bbox': list(b),
                            'original_pdf_pixels': [block['width'], block['height']]})
    report = {'source_pdf_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              'linked_frames': len(frames), 'mapped_pdf_regions': len(regions),
              'cover': [f for f in frames if f['source_page'] == 1],
              'photos': regions, 'frames': frames,
              'unused_links': sorted('Links/' + p.name for p in (PACKAGE / 'Links').iterdir()
                                     if p.is_file() and 'Links/' + p.name not in {f['file'] for f in frames})}
    (DESIGN / 'photo-catalog.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ['photos', 'frames', 'cover']}, indent=2))


if __name__ == '__main__':
    catalog()
