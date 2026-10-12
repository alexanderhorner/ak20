# Yearbook design sources

This directory contains authoring material, separate from Laravel's public assets,
Blade templates, and storage runtime. Nothing here changes the served PDF.

- `original/`: complete, unmodified InDesign package. The `.indd` is the native
  document; `.idml` is its interchange form. The three PDFs are the original page,
  spread, and single-photo-page exports. `Links/` contains original photographs;
  `Document fonts/` contains the packaged original fonts. Keep the package's
  filenames and these sibling directories intact for InDesign relinking.
- `original-manifest.json`: byte sizes and SHA-256 of all 106 uploaded files,
  including package metadata. No original was renamed, recompressed or discarded.
- `photo-catalog.json`: original image filenames, EXIF orientation, dimensions,
  and IDML frame geometry mapped to the published PDF's photo regions. This is
  the source index for using or regrouping original photographs.
- `fonts/`: the redesign's bundled, openly licensed typefaces and licenses.

Generated PDFs, HTML prototypes, and visual proofs live in `docs/yearbook/`.
Build scripts and dependencies live in `tools/yearbook/`.
The Laravel download remains `storage/app/public/pdf/Abschlusszeitung2020.pdf`.

The original package is an archive: edit derivatives, not these files. Its
packaged fonts are retained for reconstructing the original document; the new
edition uses only the separately licensed fonts in `fonts/`.
