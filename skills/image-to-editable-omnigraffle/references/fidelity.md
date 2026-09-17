# Source-fidelity contract

## Reconstruction is the default

A supplied image is the composition to reconstruct, not just a theme to borrow. Preserve its aspect ratio, panel widths, scientific objects, vector/tensor strips, matrices, separators, grouping, line routes, equation typography, relative type scale and whitespace. Do not replace these with a simpler card layout or omit details to make native scripting easier.

Treat a user-requested redesign as a different mode. Do not set `mode: redesign` merely to bypass missing measurements. Point-coordinate legacy manifests are redesign drafts until mapped to the reference.

## Measure before building

1. Read the actual source image and record path, SHA-256, pixel width/height and any intentional crop. Cropping is explicit; no automatic content trim or independent panel crops to conceal drift.
2. Inventory every visible item, including repeated cells, feature vectors, matrix masks, small legends, panels and math. Assign an ID and treatment: native, extracted, data-backed plot or equation asset. A figure with fewer meaningful elements than the source is incomplete even if its main boxes are correct.
3. Record source-pixel bounding boxes and connector routes from the actual reference. Never backfill invented source coordinates by scaling an already redesigned native diagram just to satisfy the schema. Use local OCR/text measurements when available, then visually reconcile missed/merged items. Record measured font size, weight, alignment, line breaks, padding, stroke width and corner radius. Do not guess a uniform 9 pt size for the entire drawing.
4. Choose one final width in points. Compute one isotropic scale from the source crop; derive height, positions, font sizes, strokes and radii using it. Never independently compress height or widen one panel.
5. Preserve the source's actual artwork. A tensor strip is reconstructed as its visible cells, not renamed as a generic `h` box. Complex artwork is transparently extracted and placed in the measured box. Account for transparent padding by mapping the cutout’s visible-content bounds to the source object bounds; do not scale the entire padded bitmap as though it were the visible object, with all surrounding editable text removed from the bitmap. Do not approximate a distinctive asset to avoid extraction.
6. Preserve typeset equations. Do not replace fractions, subscripts or superscripts with literal underscores/carets, or simulate complex math with a pile of Unicode glyphs. Use accurate native rich text when supported; otherwise render the transcribed LaTeX to a separately replaceable vector asset at the measured position.

## Scientific corrections are local exceptions

The paper/data determine scientific truth. If the generated PNG is wrong, record an object/region-level correction with its evidence, source and corrected bounds, and reason. Correct only that content or route; retain the surrounding composition. A corrected waveform keeps the same plot area, axes, typography and visual treatment as far as truthful data allow.

Report these as explicit source differences. They do not authorize global relayout, shrinking typography, replacing all graphs, or adding new panels. Do not call an altered region pixel-identical. If the source is too defective to reconstruct faithfully, explain the exact conflict instead of silently switching the whole figure to redesign.

## Acceptance has separate gates

- **Structural:** native object/text inventory, attached connectors, replaceable assets, source save/reopen.
- **Scientific:** labels, equations, topology, numbers and recorded corrections are supported.
- **Visual fidelity:** a reference-to-export comparison confirms the intended composition and appearance.

A native object count, embedded fonts, intact data or a successful PDF export passes only its own check. None proves visual fidelity.

Export the selected objects with transparency and zero margin. Render that exact exported PDF. Compare it with the corresponding declared crop of the source:

```bash
pdftoppm -singlefile -png -scale-to 1600 figure.pdf preview
python3 scripts/compare_reference.py source.png preview.png --out comparison
```

Use `--source-crop LEFT TOP WIDTH HEIGHT` only for a measured crop that matches the intended selected-object extent. `--render-crop` is for an explicitly documented render border, not individual panel warping.

The helper preserves aspect ratio to pixel rounding, caps diagnostic images on both axes, flags subpixel-limited comparisons, writes side-by-side, 50% overlay and difference diagnostics, and reports aspect drift and foreground-focused error. Aspect error above 1% is a default geometric failure; the tolerance is a working check, not a research accuracy claim. Missing content or shifted labels can still fail below that tolerance. Different fonts/antialiasing may affect pixel error, so there is no universal pixel-score pass threshold.

Inspect the full figure and each panel at matching scale. Check shared edges, baselines, object counts, matrix/tensor cells, line endings, text wrapping, equations, stroke/gradient treatment and artwork identity. Use the overlay to locate drift. Correct mismatched objects in the authoring source, re-export, and compare again. Preserve the comparison with `structural_pass`, `scientific_pass`, `fidelity_pass`, exact reviewed render hash, reviewed regions and explicit remaining differences in the run's QA record. Overall completion requires all three gates; unknown is not pass.

If the source and final physical width make readable text impossible, state that constraint and propose the smallest layout change as a redesign decision. Do not quietly enlarge labels or simplify the source during reconstruction.
