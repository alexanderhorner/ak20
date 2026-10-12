# AK20 PDF redesign

A print-ready A4 yearbook preview on `design/yearbook-2020`. This does not change the website, replace the original PDF, or deploy anything.

## Outputs

- `docs/yearbook/iterations/yearbook/AK20-Jahrbuch-Redesign.pdf`: 52-page redesign with bookmarks and an embedded, byte-identical copy of the original PDF.
- `docs/yearbook/iterations/yearbook/preview.jpg`: eight-page visual overview.
- `docs/yearbook/iterations/yearbook/page-*.png`: selected full-page previews.
- `docs/yearbook/iterations/yearbook/content-audit.json`: source checksum, content checks, and photo placement inventory. Contains the same personal information as the source PDF; keep it with the yearbook.

## Rebuild

Use Python 3 in an isolated virtual environment, install `tools/yearbook/requirements.txt`, then run:

```sh
python tools/yearbook/build.py
```

The script expects the FreeSans regular, bold, and oblique fonts in `/usr/share/fonts/truetype/freefont/`. It reads only the existing source at `storage/app/public/pdf/Abschlusszeitung2020.pdf` and writes the preview directory.

## Preservation checks

All 30 student profiles, childhood pictures and portraits, nine original photo spreads, four teacher profiles, and three pages of historical quotes are included. Original photo artwork is placed directly from the source PDF, preserving orientation and original clipping without resampling. The cover includes the original cutout, and the small image printed on the quotes page is included on the closing page.

Every factual text block is verified against its redesigned page. Comparison ignores whitespace, capitalization of field labels, label colons, and discretionary hyphens introduced by the original line wrapping. The original dinosaur/heart emoji uses a custom Type3 font; its artwork is rendered inline and preserved in the embedded original. Decorative oversized title fragments and shadows are replaced by the new design. No wording, names, dates, wishes, anecdotes, or quotes are edited or shortened.

The build also checks profile text bounds, the source-image placement count, and byte identity of the embedded original. The original blank last page becomes a designed back cover.

## Editorial version two

The second design and its design system, image concept, HTML prototype, print proofs and checks are documented in `docs/yearbook/iterations/yearbook-editorial/README.md`. Build it with `build_editorial.py` and produce its design study with `make_design_study.py`. Neither command replaces version one's PDF or changes the website.

## Iteration checkpoints

The user requested a commit for every reviewable design iteration. Preserve previous PDF editions and commit each finished proof before further design changes. See `docs/yearbook/iterations.md` for the saved versions. The preferred color checkpoint is `6a3bf67`.

The larger-illustration revision is built by `build_illustrated.py` and documented in `docs/yearbook/iterations/yearbook-illustrated/README.md`.

## Original-source revision

`build_refined.py` starts from the preferred color edition and uses the original
InDesign-linked photographs. Shared styles and vector illustrations live in
`resources/design/yearbook/`; source data and filename/geometry mappings are
archived there as well. The photo catalog can be rebuilt with
`catalog_originals.py`.

Prototype and review first:

```sh
python3 tools/yearbook/build_refined.py --prototype-only
python3 tools/yearbook/make_refined_study.py
```

Then export the same layout:

```sh
python3 tools/yearbook/build_refined.py
python3 tools/yearbook/make_refined_study.py --pdf
```

Outputs: `docs/yearbook/iterations/yearbook-refined/`. Photography targets 240
ppi without upsampling, JPEG quality 91 with full chroma detail, and lossless PNG
for transparency/screenshots. IDML records original cropping and actual layout
orientation; the catalog makes future recropping or regrouping possible. Fonts
and structural shapes remain vector. Original files are not modified.

This web PDF omits the earlier editions' large original-PDF attachment. The
byte-identical original PDF and complete 106-file authoring package remain
archived in the repository. All content and all 88 original linked image files
are still present in the redesigned document. Website and password appear only
in small type on the final page.

## Cover and print refinement

`build_print.py` adds generated grip hands to the untouched original cutout,
removes the original decorative arrow at the user's request, and gives the book
separate front/back covers. Source artwork and prompts are in
`resources/design/yearbook/illustrations/`; print styles are in `styles/print.css`.

```sh
python3 tools/yearbook/build_print.py --prototype-only
python3 tools/yearbook/make_print_study.py
python3 tools/yearbook/build_print.py
python3 tools/yearbook/make_print_study.py --pdf
```

Outputs live in `docs/yearbook/iterations/yearbook-print/`: the complete web PDF,
a two-page cover-panel PDF, and the 50-page numbered interior. The interior's
first page is a right-hand page; margins are mirrored (45 pt binding, 31 pt
outside), with outer-edge folios and chapter tabs. Contents references and links
use the numbered interior. The cover panels have no running headers or folios.

## Latest: abstract covers and endpapers

The latest review uses `build_jacket.py`:

```sh
python3 tools/yearbook/build_jacket.py --prototype-only
python3 tools/yearbook/build_jacket.py
```

The complete 56-page web book is in
`docs/yearbook/iterations/yearbook-jacket/AK20-Jahrbuch-Web.pdf`: abstract front,
quiet inside-front, class photo on PDF page 3 / print folio 1, 52 numbered paper
pages, matching inside-back, and a quieter exterior back. `AK20-Umschlag.pdf`
contains the two exterior panels; `AK20-Vorsatz.pdf` the two inside panels;
`AK20-Innenteil.pdf` the 52-page interior. The website/password are quietly on
the final paper page, before the inside-back and exterior-back covers.

The source photograph check (`verify_photos.py`) independently compares linked
originals with the published PDF to catch rotations, reflections and cropping
errors. Every subsequent export also compares its actual photo derivatives.
Contents anchors become explicit PDF destinations, so all 34 links work in
both the complete book and the extracted interior. Print/source/art checks are
recorded in each edition's audit.

## Final detail review

After exporting the latest jacket edition, run the independent relationship
audit. It measures screen and print layouts, checks photo-frame padding, shared
text axes, caption gaps, photo baselines, mirrored corner direction, footer
clearance and overlaps. It exits unsuccessfully if any relationship fails.

```sh
python3 tools/yearbook/detail_audit.py --output docs/yearbook/iterations/yearbook-jacket/review --render
python3 tools/yearbook/make_jacket_proofs.py
```

The optional render produces fourteen larger four-page sheets covering the
complete 56-page PDF, suitable for detailed visual review. Content preservation
and final PDF/HTML fidelity remain part of `build_jacket.py`.
