# Yearbook design checkpoints

All work stays on `design/yearbook-2020`. Nothing is deployed.

| Iteration | PDF | Checkpoint |
| --- | --- | --- |
| 1 — initial colorful design | [PDF](yearbook/AK20-Jahrbuch-Redesign.pdf) | `00995d4` |
| 2 — editorial typography | [PDF](yearbook-editorial/AK20-Jahrbuch-Editorial.pdf) | `c11091a` |
| 3 — color sections and rosettes | [PDF](yearbook-color/AK20-Jahrbuch-Farbe.pdf) | `6a3bf67` — retained version the user liked |
| 4 — larger background illustrations, light grain, no personal numbering | [PDF](yearbook-illustrated/AK20-Jahrbuch-Illustrationen.pdf) | Current illustration iteration |

For each further reviewable iteration:

1. Commit the current PDF, prototype, previews, audit and renderer before changing its design.
2. Preserve earlier PDF editions. Use a new output folder for a new design direction.
3. Re-run preservation and layout checks, then inspect the rendered pages and grayscale proof.
4. Commit the completed iteration with a descriptive message and update this index.
5. Keep unrelated VPS/deployment changes out of these commits. Deploy only when asked.
