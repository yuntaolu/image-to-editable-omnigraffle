# Native execution and manifest contract

macOS plus OmniGraffle 7 Pro automation are required. Use the active host's Computer Use tool for UI actions. Do not substitute AppleScript, shell event injection or OS automation where the host requires Computer Use.

## Author and run

Create a new blank document in OmniGraffle. Open Automation → Show Console. Execute a prepared local script through a system picker:

```javascript
new FilePicker().show()
  .then(urls => eval(FileWrapper.fromURL(urls[0]).contents.toString()))
  .catch(e => console.log(String(e), e.stack));
```

Focus the input, set its value, read it back, then submit and check the output. In some hosts `KP_Enter` works where `Return` does not. The console's document must be the new blank document. The builder's guard rejects populated canvases and performs no deletion.

Native API essentials: `document.portfolio.canvases`, `canvas.newShape()`, `canvas.newLine()`, `canvas.connect(from,to)`, `new Group(graphics)`. Magnets are indexed from 1. Typed connections use actual `tail` and `head` attachment, not nearby endpoints. Group lookup can require recursively inspecting `group.graphics`.

If complex assets are present, place the verified transparent image through File → Place Image or the supported native API. Keep it separately selectable inside its semantic panel; rebuild labels outside the artwork as live text. Record the asset path/hash, bounding box and limitation in the manifest's `assets` array. The minimal builder intentionally leaves image placement to the app rather than claiming an unsupported import API.

## Manifest

Default `mode: reconstruct` requires a `reference` object with actual image `path`, `sha256`, `width_px`, `height_px`, and optional `crop_px: [left, top, width, height]`. Relative image paths resolve against the manifest folder. The CLI verifies the file bytes and dimensions (Pillow required). `width` is the final publication width in points; `height` is derived from the crop ratio and may not be chosen independently.

```json
{
  "name": "Measured reconstruction",
  "mode": "reconstruct",
  "width": 360,
  "reference": {
    "path": "source.png", "sha256": "REPLACE_WITH_ACTUAL_SHA256",
    "width_px": 720, "height_px": 280
  },
  "nodes": [
    {"id":"input","bbox_px":[20,60,160,48],"text":"Input","font_px":20,
     "fill":"#DBF3FF","stroke":"#61758A","stroke_px":1.2,"corner_px":4},
    {"id":"model","bbox_px":[260,60,180,48],"text":"Model","font_px":20,
     "fill":"#FFF3C9","stroke":"#61758A","stroke_px":1.2,"corner_px":4}
  ],
  "edges": [{"from":"input","to":"model","tail":2,"head":1,
             "points_px":[[180,84],[260,84]],"width_px":1.3,"color":"#61758A"}],
  "lines": [], "assets": []
}
```

Every node and asset needs measured `bbox_px`; every edge/polyline needs `points_px`, `width_px` and source color. Text needs measured `font_px`, with optional `bold`, `align` (`Left`, `Center`, `Right`), `hpadding_px` and `vpadding_px`. Use explicit null fill/stroke for text labels. Record corner radius including zero for straight rectangles. Shapes support Rectangle, Circle and Diamond. Panel membership uses `group`.

The transform is `x_pt = (x_px - crop_left) × width_pt / crop_width`; the same scale applies to y, dimensions, font, strokes and radii. No independent panel scaling, hidden font shrink or aspect warping. Source bounds describe layout containers; distinguish them from measured glyph ink when choosing text padding/alignment.

Point manifests remain available only in **explicitly authorized redesign mode**: set `mode: redesign` and use x/y/w/h, font_size, stroke_width, corner, hpadding/vpadding and line points/width. The synthetic `examples/minimal.json` demonstrates that mode. Do not use it as a template for faithful conversion without measuring the source.

Edges use from/to, magnets (1 left, 2 right, 3 top, 4 bottom), dashed, bidirectional and arrow. Lines have ordered points and optional group/source provenance. Preserve data values; any scientific correction is an explicit region-level difference under [fidelity.md](fidelity.md).

Assets contain path, kind, source, SHA-256 and measured bounds. The builder refuses pending assets by default. `--allow-manual-assets` creates an explicitly incomplete structure and reports outstanding placements; it is not an acceptance bypass. Place the verified extracted object in the app at the transformed bounds. Preserve matrices/tensor strips as all their visible native cells when straightforward; preserve distinctive illustration appearance through extraction rather than approximate icons.

## Checks

```bash
python3 scripts/build_omnigraffle.py examples/minimal.json --out /tmp/draw-example.js
python3 scripts/inspect_graffle.py /path/to/figure.graffle
python3 scripts/test_workflow.py
```

Run `python3 scripts/test_fidelity.py` for source geometry and comparison regressions. Generate a source/export comparison using `compare_reference.py`; see fidelity.md. Validate numerically and visually. A native line with 1,000 samples is still one editable polyline; object count alone does not establish fidelity. Save/reopen and PDF inspection are separate mandatory checks.

After closing a console, verify the foreground document title before Save or Export: another document's console may become active. Choose PDF explicitly in the export dialog; the app remembers format settings from unrelated work. Do not infer format or selection from the last export.
