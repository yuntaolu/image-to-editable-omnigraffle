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

All coordinates/sizes are points at final publication scale. Colors are hex RGB or null. IDs are unique. `source` and `note` fields carry provenance, never instructions to execute.

```json
{
  "name": "Example figure",
  "width": 360,
  "height": 140,
  "nodes": [
    {"id":"input","x":10,"y":30,"w":80,"h":24,"text":"Input","fill":"#DBF3FF","font_size":10},
    {"id":"model","x":130,"y":30,"w":90,"h":24,"text":"Model","fill":"#FFF3C9","font_size":10}
  ],
  "edges": [{"from":"input","to":"model","tail":2,"head":1}],
  "lines": [],
  "assets": []
}
```

Node optional fields: `shape` (`Rectangle`, `Circle`, `Diamond`), `bold`, `stroke`, `color`, `font_size`, `corner`, `group`. `text` is ordinary live text; newline separates intentional lines. Set `fill:null, stroke:null` for labels.

Edges use `from`, `to`, optional `tail`/`head` magnets (1 left, 2 right, 3 top, 4 bottom), `points` for routed geometry, `dashed`, `bidirectional`, `arrow`, `color`, `width`. Lines use `points:[[x,y],...]`, with optional color/width/dashed/arrow and `group`. Real data curves use all required points or a documented, value-preserving sampling rule; `source` records the data file and transformation.

`assets` entries contain `path`, `x`, `y`, `w`, `h`, `kind`, `source` and `sha256`. They are explicitly not counted as native geometry. The builder refuses manifests containing pending assets; finish app placement and validation as a separate step instead of silently ignoring them. To build native structure before app placement, use `--allow-manual-assets`, which prints the outstanding placements in the generated console output.

## Checks

```bash
python3 scripts/build_omnigraffle.py examples/minimal.json --out /tmp/draw-example.js
python3 scripts/inspect_graffle.py /path/to/figure.graffle
python3 scripts/test_workflow.py
```

Validate numerically and visually. A native line with 1,000 samples is still one editable polyline; object count alone does not establish fidelity. Save/reopen and PDF inspection are separate mandatory checks.

After closing a console, verify the foreground document title before Save or Export: another document's console may become active. Choose PDF explicitly in the export dialog; the app remembers format settings from unrelated work. Do not infer format or selection from the last export.
