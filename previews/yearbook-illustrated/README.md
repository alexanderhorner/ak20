# Yearbook iteration 4 — larger illustrations and light grain

The color version retained at commit `6a3bf67` stays unchanged in `previews/yearbook-color/`.

## Review

- [New PDF](AK20-Jahrbuch-Illustrationen.pdf)
- [Nine-page preview](preview.jpg)
- [HTML prototype](prototype/index.html)
- [All pages](all-pages.jpg)
- [Grayscale print proof](grayscale-print-proof.jpg)
- [Generated open-book illustration](prototype/design-assets/book.png)
- [Generated sun-and-arch illustration](prototype/design-assets/arch.png)
- [Generated grain tile](prototype/design-assets/grain.png)
- [Exact image prompts](image-prompts.json)

The assets were generated with the built-in `image_gen.imagegen` tool, with transparent backgrounds. Larger illustrations appear on selected pages, in quiet spaces behind the reading layer. Their opacity ranges from 12% to 24%.

The fine grain sits below the text and original photographs. Its layer opacity is 22%; the tile itself has low alpha, so the resulting texture is very faint. Body text remains selectable and photographs retain the original PDF artwork and quality.

The personal numbers and the pen-loop decorations are removed. Page numbers, contents references, and chapter numbers remain. Added headings stay plain and factual.

## Verification

- 52 exact A4 pages; 30 student profiles.
- All 215 content units and 88 original photo placements preserved.
- 1,025 matched HTML/PDF text positions; maximum drift 0.664 pt.
- Geometry checks for text bounds, footer collisions, photo/text collisions and foreground decoration collisions pass.
- Explicit checks confirm there are no personal-number badges or pen-loop elements, and all page folios remain.
- The unchanged original is embedded. Checksums confirm all three earlier PDF editions are unchanged.
- The visible website and its links use `ak20.alexanderhorner.de`.

## Rebuild

Use the Python environment described in `tools/yearbook/README.md`:

```sh
python tools/yearbook/build_illustrated.py
```

Keep the three generated PNGs in `prototype/design-assets/` when rebuilding. The renderer writes this iteration's folder only.
