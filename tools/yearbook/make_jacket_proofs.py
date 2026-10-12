"""Refresh opening, facing-page and cutout-detail proofs from the final PDF."""
from pathlib import Path

import pymupdf as fitz
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/yearbook/iterations/yearbook-jacket'


def page_label(page):
    """Decode the Unicode prefix left as a hex string by PyMuPDF's helper."""
    label = page.get_label()
    if label.startswith('<FEFF') and label.endswith('>'):
        return bytes.fromhex(label[5:-1]).decode('utf-16-be')
    return label


def rendered(page, scale):
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    return Image.frombytes('RGB', (pix.width, pix.height), pix.samples)


def main():
    with fitz.open(OUT / 'AK20-Jahrbuch-Web.pdf') as pdf:
        opening = Image.new('RGB', (1950, 940), '#DED7CF')
        draw = ImageDraw.Draw(opening)
        for i in range(3):
            opening.paste(rendered(pdf[i], 1), (i * 650 + 27, 20))
            draw.text((i * 650 + 27, 881), f'PDF {i+1:02} / {page_label(pdf[i])}', fill='#30243B')
        opening.save(OUT / 'opening-proof.jpg', quality=95)

        spreads = Image.new('RGB', (1696, 1268), '#DED7CF')
        draw = ImageDraw.Draw(spreads)
        # Each pair is a true left/right facing spread in the paper interior.
        for i, (left, right) in enumerate([(3, 4), (33, 34), (45, 46), (49, 50)]):
            x, y = (i % 2) * 848 + 30, (i // 2) * 634 + 20
            a, b = rendered(pdf[left], .66), rendered(pdf[right], .66)
            spreads.paste(a, (x, y)); spreads.paste(b, (x + a.width, y))
            draw.text((x, y + 575), f'Innenteil {page_label(pdf[left])} / {page_label(pdf[right])}', fill='#30243B')
        spreads.save(OUT / 'print-spreads.jpg', quality=95)

        pdf[2].get_pixmap(matrix=fitz.Matrix(3, 3), clip=fitz.Rect(31, 340, 150, 433), alpha=False).save(OUT / 'peeking-detail.png')
    print('Refreshed opening, physical spreads and peeking detail from the final PDF.')


if __name__ == '__main__':
    main()
