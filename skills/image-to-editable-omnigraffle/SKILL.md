---
name: image-to-editable-omnigraffle
description: Reconstruct supplied figure images or PDF panels as editable native OmniGraffle diagrams, with live Times New Roman text, attached connectors, transparent extracted assets, and data-backed scientific plots. Export selection-cropped transparent PDFs. Use for image-to-Graffle conversion and editable scientific figure reconstruction; not for wrapping a whole image in a Graffle file.
---

# Image to Editable OmniGraffle

Turn a figure image into a `.graffle` source and a tightly cropped vector PDF. Use the image as the visual reference and supplied manuscript/data as the scientific authority. A raster concept may contain incorrect labels or connections: correct these from evidence, and record the correction.

## Scope and working files

Resolve the source image, manuscript/caption, protected files, final insertion width and requested outputs first. Reuse a stable task directory containing the reconstruction manifest, necessary assets, drawing script and one current preview. Preserve originals; create a sibling `_editable.graffle` unless replacement is authorized. Do not publish source images, manuscript excerpts or measurements merely because publication of this skill is authorized.

Use optional installed skills where helpful: `ccf-visual-composer` for composition, `yuntao-omnigraffle` for native authoring, and `nature-figure` for Python scientific plots. This skill is self-contained; those names do not authorize installation, a backend change or extra external transmission.

## Decide every object's source before drawing

Inventory all text, equations, shapes, connectors, illustrations and quantitative panels. Classify each as:

1. **Native:** ordinary text, modules, graph nodes, tensor grids, axes, simple symbols and connectors. Rebuild these with native editable elements. Use Times New Roman (`TimesNewRomanPSMT`, bold `TimesNewRomanPS-BoldMT`); report necessary glyph fallback. Preserve mathematical distinctions and signed/ordered target roles.
2. **Extracted asset:** complex illustrations, photos, textures or irregular artwork whose identity must be preserved. Use the host image-edit tool to isolate the exact object with a transparent background. Request no redraw, no added text and no geometry/color changes. Inspect alpha, edges, missing strokes and source identity before embedding. Do not crop a whole panel or the full figure and claim native editability. If a clean source already has transparency, reuse it. Deterministic cropping/background editing is used only when the user explicitly requests that route.
3. **Scientific plot:** when data exist, regenerate curves/bars in Python from those values. Keep units, masks, uncertainty and provenance. Export transparent PDF/SVG/PNG as needed, or map data into native polyline coordinates with native axes/text. An embedded vector plot is movable/resizable but its internal points are not necessarily OmniGraffle-editable; say so. Never recover quantitative results from an AI-generated plot. If data are absent, preserve the supplied plot as a separately replaceable asset, label its limitations, and do not invent values.
4. **Equation:** use native text for simple expressions. Preserve complex math as a separate vector asset if native text cannot render it faithfully; report that editability boundary.

Solve mandatory complex-asset extraction before reconstructing dependent layout. If it fails, retain the working source and report the specific missing object; do not silently replace it with an unrelated icon. Native reconstruction of actual graph nodes or geometric symbols is appropriate and is not an illustration-substitution workaround.

## Reconstruct

Read [native-workflow.md](references/native-workflow.md) before the first native execution. Inspect current application APIs rather than guessing property names.

Use `scripts/build_omnigraffle.py manifest.json --out draw.js` for repeatable native shapes, text, lines and plots. The manifest uses publication points, not screenshot pixels. Record source dimensions and map source pixels to points consistently; choose canvas width to match final insertion width. Adjust the layout before shrinking text below readable size.

The builder creates an OmniGraffle Automation script. Run it in a **new empty document** through the application's console and a FilePicker. It refuses nonempty documents. It does not launch apps, inject OS events, save files, change preferences or upload anything.

- Keep native content grouped by panel. Use named source/target shapes and attached native connectors with explicit magnets.
- Group each complete figure for reliable single-selection PDF export. Nested groups preserve child editability.
- Reuse exact graph topology, direction, dashed/solid semantics and target order. Reserve connector lanes so arrows cannot appear to bypass a module.
- Preserve source-specific visual relationships. Do not replace the supplied composition with a generic set of cards merely because it is easier to script.
- Build only requested panels/formats. Use native property inspectors for small final corrections, and keep the manifest/script consistent with those corrections.

## Export and verify

Save the native source, close and reopen that exact file, then select a group/node and verify live text and attached connectors.

Export **PDF → Selection (Current Canvas) → 100%** with **Transparent background** enabled; **Include margin** disabled and its value **0 px**; notes and nonprinting layers excluded. Do not substitute Current Canvas or All Objects. If Select All is unreliable, group the complete figure and select its single native group. Re-export only after a material change.

Check all of the following:

- Source and PDF show the same labels, scientific relationships and plot values.
- Text, arrows, axes and legend fit at final paper width; no clipping or crossing through unrelated labels.
- PDF dimensions match selected-object bounds; fonts are embedded and margins are intentional.
- Transparent assets retain real alpha, with no white/key-color fringe or duplicate labels.
- The source contains actual native shapes/text/connectors, not a full-image background plus hidden text. `scripts/inspect_graffle.py` reports native counts, attachments and image use.
- Embedded images are described as separate replaceable assets, not as fully editable geometry.
- If manuscript replacement was authorized, rebuild the paper and inspect the affected page, references and page count. Otherwise leave the paper unchanged.
- Preserve requested originals and report the actual changed/unchanged paths. A successful script, save dialog or file existence alone is not completed validation.

If the UI becomes stale, refresh its accessibility state. Dismiss a stuck menu with its exposed Cancel action. Focus the console input before setting its text; verify submission/output separately. Never operate from stale coordinates or assume a queued command executed.

## Delivery

Return the native source, exported PDF and useful preview. State which parts are native, vector assets or raster assets; include source-data provenance and actual checks. Retain the minimal manifest/script/assets necessary to reproduce the result. Do not call the figure submission-ready if layout or scientific checks remain unresolved.
