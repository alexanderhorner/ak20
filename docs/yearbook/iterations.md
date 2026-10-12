# Yearbook design checkpoints

All work stays on `design/yearbook-2020`. Nothing is deployed.

| Iteration | PDF | Checkpoint |
| --- | --- | --- |
| 1 — initial colorful design | [PDF](iterations/yearbook/AK20-Jahrbuch-Redesign.pdf) | `00995d4` |
| 2 — editorial typography | [PDF](iterations/yearbook-editorial/AK20-Jahrbuch-Editorial.pdf) | `c11091a` |
| 3 — color sections and rosettes | [PDF](iterations/yearbook-color/AK20-Jahrbuch-Farbe.pdf) | `6a3bf67` — retained version the user liked |
| 4 — larger background illustrations, light grain, no personal numbering | [PDF](iterations/yearbook-illustrated/AK20-Jahrbuch-Illustrationen.pdf) | `6c27a57` |

For each further reviewable iteration:

1. Commit the current PDF, prototype, previews, audit and renderer before changing its design.
2. Preserve earlier PDF editions. Use a new output folder for a new design direction.
3. Re-run preservation and layout checks, then inspect the rendered pages and grayscale proof.
4. Commit the completed iteration with a descriptive message and update this index.
5. Keep unrelated VPS/deployment changes out of these commits. Deploy only when asked.

| Further iteration | PDF | Checkpoint |
| --- | --- | --- |
| 5 — refined color, original-source photographs | [PDF](iterations/yearbook-refined/AK20-Jahrbuch-Verfeinert.pdf) | `bbf9ea7` — photo checks and portable contents links |
| 6 — photograph cover, peeking hands, mirrored interior | [PDF](iterations/yearbook-print/AK20-Jahrbuch-Web.pdf) | `7bf5a68` |
| 7 — abstract covers, quiet endpapers, photograph on page 3 | [PDF](iterations/yearbook-jacket/AK20-Jahrbuch-Web.pdf) | `97a434d` — HTML; `674500c` — final PDF and print exports |

The latest complete book has 56 PDF pages and a 52-page interior. Exterior
covers, inside-cover panels and interior are exported separately. The original
106-file source package is retained unchanged under `resources/design/yearbook/`.

Every exported original-source photo is compared visually with the published
PDF to check identity, orientation, reflection and cropping, in addition to
content/placement/spacing/font checks. The removed decorative arrow remains in
the source archive; it is omitted only at the user's request.
