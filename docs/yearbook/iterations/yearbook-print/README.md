# Covers and print refinement

Based on the preserved refined color edition in `../yearbook-refined/`.

- [Complete web PDF](AK20-Jahrbuch-Web.pdf): front cover, 50 numbered interior
  pages, back cover. Selectable vector text/shapes, bookmarks and contents links.
- [Cover panels](AK20-Umschlag.pdf): unnumbered A4 front and back, in that order.
- [Interior](AK20-Innenteil.pdf): 50 pages, starting on a right-hand page, with
  outer-edge folios/tabs and mirrored margins (45 pt binding / 31 pt outside).
- [HTML prototype](prototype/index.html), [design study](prototype/design-system.html),
  `preview.jpg`, `all-pages.jpg`, `cover-proof.jpg`, and `print-spreads.jpg`:
  visual/layout proofs before and after PDF export.
- `content-audit.json`: text preservation, original-photo coverage, byte-identical
  source archive, font/image alignment and numbered print-page checks.

The cover's original face and group photograph remain untouched. The two small
hands were made with the built-in image generation tool; their source and exact
prompt are in `resources/design/yearbook/illustrations/hands*`. The decorative
arrow is removed as requested. Every other original photo, all 30 profiles,
four teacher profiles, and all facts/anecdotes/quotes remain. The removed arrow
and all source photographs remain in the unmodified source package.

Website and password occur only in small type on the back cover. This web PDF
uses 240 ppi photo derivatives, JPEG quality 91 with full chroma detail, and
lossless PNG transparency/screenshots, without upscaling small originals. The
full originals are archived separately; no large duplicate attachment is added.

## Printing

Use `AK20-Innenteil.pdf` at actual size on A4, duplex, long-edge binding. Page 1
is a right-hand page; the printed contents page numbers match the interior.
`AK20-Umschlag.pdf` contains the separate front/back cover panels. These are A4
panels; a printer's hardcover wrap, spine and bleed dimensions can be applied
once their binding specification is available. No spine width has been guessed.

The existing website/production PDF remain unchanged. All work is committed on
`design/yearbook-2020`, with previous design editions preserved.
