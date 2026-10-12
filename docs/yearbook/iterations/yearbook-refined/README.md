# Refined color edition — original photographs

Based on the preferred color checkpoint (`6a3bf67`), preserved unchanged in
`../yearbook-color/`. The rosette numbers stay; all pen loops are removed.

Chapter pages use larger abstract arch/fan compositions. Profile backgrounds use
broad, faint curves tied to their wash color. The shared, subtle paper texture
comes from the earlier image-tool exploration; structural shapes are native SVG
for precise layout and crisp printing. Nothing alters the people in the photos.

The cover has no URL/password. Both appear quietly on the final page, with the
website updated to `ak20.alexanderhorner.de`. The original small arrow remains in
the quotes section, where it came from.

## Source and export

The complete InDesign package is preserved in
`resources/design/yearbook/original/`. The source catalog maps all 88 linked
original image files to the published PDF through IDML geometry, with explicit
rotation/crop records. All 30 students, four teachers, gallery images, names,
facts, anecdotes and dialogue are preserved. The class photograph is repeated
as a chapter opener; splitting the original cover into its actual photo and
cutout yields 89 photo placements.

The new web PDF uses original-source derivatives at a target of 240 ppi, JPEG
quality 91 and full chroma detail. Smaller originals are never upscaled. PNG
transparency/screenshots are lossless. Text, chapter art and number badges remain
vector. Original images and all earlier PDFs remain unchanged. The complete
originals are archived separately rather than embedded again in this web PDF.

## Review artifacts

- `prototype/index.html`: entire book, built and reviewed before PDF export.
- `prototype/design-system.html`: roles, type, color and real-page specimens.
- `design-study-preview.jpg`: four-page study overview.
- `AK20-Jahrbuch-Verfeinert.pdf`: final PDF.
- `preview.jpg`, `all-pages.jpg`, `page-*.png`: rendered PDF proofs.
- `grayscale-print-proof.jpg`: contrast/readability proof.
- `content-audit.json`: independent source-content, photo-coverage and all-page
  geometry checks, including measured HTML/PDF typography correspondence.

Build commands are in `tools/yearbook/README.md`. This is a review artifact on
`design/yearbook-2020`; the website and production PDF have not been replaced.
