# Validation record

## Source-fidelity regression

The initial two private examples passed structural/native checks, but **failed visual fidelity**. Their exported aspect ratios deviated by 23.4% and 28.2% from the reference PNGs; feature-vector strips, mask matrices, panel grouping, and equation typography were also simplified. Those earlier checks must not be read as visual approval.

The revised default requires measured source geometry, source hash/dimension verification, isotropic scaling, a complete visual inventory, and a source/export comparison. Explicit redesign remains separate. Both prior examples are now rejected by the aspect-ratio diagnostic; their images are not distributed.

New executable tests cover source hash and dimension mismatches, cropping, uniform font/stroke/geometry scaling, forbidden independent coordinate/aspect changes, missing measurements, same-image diagnostics, large-aspect failure, and same-aspect positional drift. Additional regressions reject overwriting the manifest/reference (including hard links) and bound extreme-aspect comparison images without zero-sized resizes. A same-image comparison still returns `requires_visual_review`, not an automatic pass. The changes have not retroactively repaired the two earlier native figures.

The following native checks were performed on the initial version using OmniGraffle 7.26. They establish native-operation behavior, not source fidelity.

## Executed checks

- Python contract tests: missing connector targets, duplicate IDs, nonfinite coordinates, invalid dimensions, pending-asset rejection and exact polyline serialization.
- Graffle inventory: XML/binary plist, zipped single-file and package formats; dangling endpoint references are not reported as attached connectors.
- Independent read-only review and isolated forward tests, including the generated script's refusal to mutate populated documents.
- Two real scientific-figure reconstructions executed through the OmniGraffle Automation Console, saved as separate files and reopened.
- Test figure A: 51 native shape/text objects, 45 native lines, including 34 attached connectors; no image objects.
- Test figure B: 47 native shape/text objects, 29 native lines, including 27 attached connectors; no image objects.
- Source-backed plots retained 10,055 samples per trace in native editable polylines. Python also generated a transparent scientific plot from the same supplied data.
- Both PDFs were exported using Selection (Current Canvas), 100%, transparent background, zero additional margin, notes/nonprinting layers excluded. Rendered PDFs inspected; alpha renders confirmed transparent backgrounds.
- A separate source-artwork extraction produced an RGBA asset with transparent pixels. It was imported via File → Place Image, resized proportionally, and saved as a single, separately selectable image object in its own test document. This tests image placement; it does not make the image's internal artwork native-editable.

## Fixes learned from these tests

- Preserve explicit null colors instead of silently substituting defaults.
- Verify connector endpoints against actual native object IDs.
- Reserve routes around labels and inspect word wrapping after native rendering.
- Focus the console field, submit separately, and verify a completion message.
- Verify the active document after closing a console: another document's console can become foreground.
- Choose PDF explicitly; export preferences may come from unrelated work.

The private test images, measurements, manuscripts, and reconstructed figures are not distributed. The public example is synthetic. Structural checks do not replace visual or scientific review. Tests cover OmniGraffle 7.26; other versions require the same native open/export checks. The builder does not automate native image placement or the saving/exporting process.
