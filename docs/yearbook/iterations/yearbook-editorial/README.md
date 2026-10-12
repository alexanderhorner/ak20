# AK20 — Editorial edition

A second, more refined yearbook design. Version one is retained unchanged in `docs/yearbook/iterations/yearbook/`. The website is not modified or deployed.

## Review the design

- [Final 52-page PDF](AK20-Jahrbuch-Editorial.pdf)
- [Four-page design study](AK20-Design-Study.pdf)
- [Real-content HTML prototype](prototype/index.html)
- [HTML design system](prototype/design-system.html)
- [Selected page overview](preview.jpg)
- [All 52 pages](all-pages.jpg)
- [Grayscale print proof](grayscale-print-proof.jpg)
- [Image-tool concept board](concept-board.png) and [exact prompt](image-concept-prompt.txt)

The concept board was made with the built-in `image_gen.imagegen` tool. Its photographs are visual placeholders used only in the study. All photos in the final book come from the original PDF.

## Design system

The direction uses expressive serif titles, comfortable body text, subtle italic accents, and a photographic layout. Warm paper and dark aubergine carry each page. Small colored photo mounts, a year medallion, and restrained pen loops keep it playful without relying on stickers or fashion-driven effects.

| Role | Color |
| --- | --- |
| Ink | `#30243B` |
| Paper | `#F7F1E6` |
| Primary red | `#C7523C` |
| Supporting blue | `#B9D0D7` |
| Butter yellow | `#EED88B` |
| Lilac | `#D7C9DF` |
| Pen stroke blue | `#627F94` |
| Small labels | `#5F5360` |

Fraunces Display supplies the titles; Fraunces Text and Italic supply names, folios and warmer accents. Manrope regular and semibold handle factual text and speaker names. IBM Plex Mono handles captions and labels. Body text is 11–11.5 pt, field labels 8.2 pt, and photo captions 7.5 pt. The large names are fitted to their allotted width without reducing reading text.

Fraunces static instances use weight 600 / optical size 72 for display and weight 400 / optical size 14 for text. Italics use weight 400 / optical size 36. Softness is 35 and wonk is 1. Manrope uses weights 400 and 600. Fonts and their licenses are bundled in `tools/yearbook/fonts/`.

## Print and implementation

The book is exactly ISO A4, 210 × 297 mm, with 38 pt outer margins. Fifty-two pages allow normal duplex printing. Text and small vector graphics remain sharp at print size. Original photographs are placed directly from the source PDF, retaining their original resolution, orientation and clipping; they are not replaced with the raster prototype previews.

The HTML prototype generates the final text layout, so CSS font metrics, line breaks and spacing carry into the PDF. Chromium supplies measured image coordinates, and PyMuPDF places the original PDF artwork there. Quote groups stay together and are distributed evenly across columns using their measured heights. PDF paper dimensions are normalized to exact A4 after Chromium's small rounding differences.

The source resolution sets the available photographic detail. The output is an A4 RGB PDF with embedded fonts and safe margins for ordinary printing.

## Verification

`content-audit.json` records:

- all 30 complete student profiles;
- 215 verified content units;
- 88 photo placements, including the original cover composition and one intentional chapter repeat;
- the original dinosaur/heart artwork retained inline;
- every page checked for content overflow, footer collisions, photo/text collisions, decorative/text collisions, and collisions between separate text regions;
- 1,135 matching HTML/PDF text positions, with maximum position drift of 0.664 pt;
- exact A4 geometry, working website links, and all pages successfully rendered;
- a byte-identical attachment of the original PDF and an unchanged checksum for version one.

Text comparison ignores whitespace, label colons, bullet formatting, and original discretionary line-break hyphens. Names, dates, plans, wishes, anecdotes, dialogue and spelling are preserved. The sole requested content substitution is the visible website: `ak20.alexanderhorner.de`. The archival attachment retains the unchanged source.

## Rebuild

From the repository root, use an isolated Python environment:

```sh
python3 -m venv /tmp/ak20-pdf-env
/tmp/ak20-pdf-env/bin/pip install -r tools/yearbook/requirements.txt
/tmp/ak20-pdf-env/bin/python3 -m playwright install chromium
/tmp/ak20-pdf-env/bin/python3 tools/yearbook/build_editorial.py
/tmp/ak20-pdf-env/bin/python3 tools/yearbook/make_design_study.py
```

The HTML uses relative font paths within this repository. The image-tool concept board is retained as an exploration asset; rebuilding the final PDF does not require generating any new images.
