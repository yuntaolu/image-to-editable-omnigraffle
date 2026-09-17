# Image to Editable OmniGraffle

Reconstruct scientific figure images as native OmniGraffle objects: editable Times New Roman text, graph nodes, modules, attached connectors and data-backed curves. Preserve complex artwork as separately selectable transparent assets and export selected objects to a transparent, zero-margin PDF.

## Install

Copy the skill into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R skills/image-to-editable-omnigraffle ~/.codex/skills/
```

Invoke `$image-to-editable-omnigraffle` with a source image/PDF, the scientific description or caption, any plot data, and your desired final width/output location.

Requires macOS, OmniGraffle 7 Pro with automation, and a host Computer Use integration. The compiler and structural inspector need Python 3. Plot generation additionally needs a Python plotting package such as matplotlib. Image extraction uses the host's image-edit capability when needed; an API key is not required for the built-in image tool.

## What is editable?

| Content | Treatment |
|---|---|
| Text, modules, graph nodes, axes, connectors | Native OmniGraffle objects |
| Curves with source data | Native polylines and labels, or separately replaceable Python-generated vector plots |
| Complex source artwork | Source-faithful transparent extraction, kept as a separate image asset |
| Complex equations | Native text where reliable; otherwise a separately replaceable vector asset |

A full-image background with text overlaid is not an editable reconstruction. An embedded SVG/PDF/PNG is not described as native geometry.

## Reproducible native structure

```bash
cd skills/image-to-editable-omnigraffle
python3 scripts/build_omnigraffle.py examples/minimal.json --out /tmp/draw-example.js
python3 scripts/test_workflow.py
```

Run the generated script through OmniGraffle's Automation Console and FilePicker in a **new blank document**. It refuses populated documents. See [the workflow and manifest contract](skills/image-to-editable-omnigraffle/references/native-workflow.md).

The compiler does not save, export, upload or inject OS events. Those steps remain visible native application actions. Image assets require explicit native placement and are never silently discarded; the default compiler rejects pending assets.

## Validation

The bundled checks exercise malformed endpoints, duplicate IDs, nonfinite coordinates, invalid dimensions, pending-asset handling and Graffle inventory formats. Actual acceptance also requires a native save/reopen and an inspected PDF export. See [validation.md](validation.md) for the recorded test scope.

Export settings: **PDF → Selection (Current Canvas) → 100% → Transparent background**; **Include margin off, value 0 px**; exclude notes and nonprinting layers.

## Workflow references

The object-source decision process was informed by [image-to-editable-ppt-skill](https://github.com/ningzimu/image-to-editable-ppt-skill), an MIT-licensed PowerPoint reconstruction workflow. No PowerPoint runtime is bundled or required here. Optional locally installed `yuntao-omnigraffle`, `ccf-visual-composer`, and `nature-figure` skills can assist with native authoring, composition and Python scientific plotting.

This repository contains generic instructions, helpers and a synthetic example. Research manuscripts, test images, source measurements and reconstructed private figures are excluded.

## License

MIT. See [LICENSE](LICENSE).
