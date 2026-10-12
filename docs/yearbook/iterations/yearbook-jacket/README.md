# Abstract covers and first paper page

The latest edition keeps the preferred color system and original-source
photography, with separate abstract covers and quiet inside-cover panels.

The complete web PDF follows the physical book order:

1. Abstract front cover: class/year typography and the large colored fan motif.
2. Quiet inside-front cover: a small blue class emblem and year.
3. First right-hand paper page, printed folio 1: class photograph with the
   original cutout and two generated grip hands.
4. Contents, printed folio 2, followed by the 30 profiles and all other content.
5. Last paper page, printed folio 52: a small class/year mark; website and
   password in subtle type near the bottom.
6. Matching quiet inside-back cover; then the exterior back with abstract art
   and a small identity mark. No large front-style title or contact block.

The book has 56 PDF pages: four unnumbered cover/inside-cover panels and 52
numbered interior pages. Physical page margins, running headers, outer-edge
folios and chapter tabs are mirrored. No source text or photograph is omitted;
the original decorative arrow is removed at the user's request.

## Outputs

- `AK20-Jahrbuch-Web.pdf`: complete book, about 18.4 MB.
- `AK20-Umschlag.pdf`: exterior front/back A4 panels.
- `AK20-Vorsatz.pdf`: inside-front/inside-back A4 panels.
- `AK20-Innenteil.pdf`: 52 pages, beginning on a right-hand page. Print at
  actual size, duplex, long-edge binding. Contents numbers match the interior.
- `prototype/index.html`: entire real-content HTML proof, reviewed before PDF.
- `opening-proof.jpg`, `cover-proof.jpg`, `print-spreads.jpg`, `all-pages.jpg`:
  rendered visual proofs; `content-audit.json` contains preservation/layout checks.

Cover panels are A4. A printer's hardcover wrap, spine and bleed dimensions can
be applied when the binding specification is known; no spine width is guessed.

Build with `python3 tools/yearbook/build_jacket.py --prototype-only`, review the
HTML, then run the same script without that flag to export PDFs. Styles are in
`resources/design/yearbook/styles/jacket.css`. Original sources, font licenses,
image prompts and all previous editions remain preserved separately.

The generated hands use the built-in image tool, with the exact prompt saved at
`resources/design/yearbook/illustrations/hands-prompt.json`. The original face
remains unchanged. Photos target 240 ppi, JPEG quality 91, full chroma detail,
with lossless PNG transparency/screenshots and no upscaling. Text and structural
shapes stay vector. The complete 106-file original package is untouched.
