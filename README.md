# Image to Editable OmniGraffle Figures

Reconstruct scientific figure images while preserving the source PNG composition. Source-pixel measurements and a rendered comparison are required before claiming fidelity. 

Build native OmniGraffle objects: editable Times New Roman text, graph nodes, modules, attached connectors, and data-backed curves. Preserve complex artwork as separately selectable transparent assets and export selected objects to a transparent, zero-margin PDF.

## Install

Copy the skill into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R skills/image-to-editable-omnigraffle ~/.codex/skills/
```

Invoke `$image-to-editable-omnigraffle` with a source image/PDF, the scientific description or caption, any plot data, and your desired final width/output location.

Requires macOS, OmniGraffle 7 Pro with automation, and integration with the host "Computer Use" plugin. The tools need Python 3.10+. Reconstruction-mode reference verification and comparison diagnostics additionally require Pillow 9.1+ (`python3 -m pip install "Pillow>=9.1"` if absent). The structural inspector and explicit redesign mode use only the standard library. Plot generation also requires a Python plotting package, such as matplotlib. 

The documented PDF rasterization command uses Poppler (`pdftoppm`), and a native PNG export is also suitable. Check the chosen interpreter with `python3 -c "from PIL import Image"` and check `pdftoppm -v` before comparison; use the host’s bundled dependency runtime when available. Image extraction uses the host's image-editing capability when needed, and no API key is required for the built-in image tool.

## What is editable?

| Content | Treatment |
|---|---|
| Text, modules, graph nodes, axes, connectors | Native OmniGraffle objects |
| Curves with source data | Native polylines and labels, or separately replaceable Python-generated vector plots |
| Complex source artwork | Source-faithful transparent extraction, kept as a separate image asset |
| Complex equations | Native text where reliable; otherwise a separately replaceable vector asset |

A full-image background with text overlaid is not an editable reconstruction. An embedded SVG/PDF/PNG is not described as native geometry.

## Faithful reconstruction

```bash
cd skills/image-to-editable-omnigraffle
python3 scripts/build_omnigraffle.py measured-manifest.json --out /tmp/draw-figure.js
python3 scripts/compare_reference.py source.png exported-preview.png --out comparison
python3 scripts/test_workflow.py
python3 scripts/test_fidelity.py
```

The measured manifest records the actual reference image hash/dimensions, source-pixel boxes/routes, measured font sizes, and source styles. One uniform transform derives native geometry; independent height changes are rejected. See [the source-fidelity contract](skills/image-to-editable-omnigraffle/references/fidelity.md).

Legacy point-based construction is available only with explicit `mode: redesign`; `examples/minimal.json` is a synthetic redesign example, not a reconstruction template. Do not choose redesign merely to bypass measurements.

Run the generated script through OmniGraffle's Automation Console and FilePicker in a **new blank document**. It refuses populated documents. See [the workflow and manifest contract](skills/image-to-editable-omnigraffle/references/native-workflow.md).

The compiler does not save, export, upload, or inject OS events. Those steps remain visible native application actions. Image assets require explicit native placement and are never silently discarded; the default compiler rejects pending assets.

## Validation

The bundled checks exercise malformed endpoints, duplicate IDs, nonfinite coordinates, invalid dimensions, pending-asset handling, and Graffle inventory formats. Acceptance separately requires structural, scientific, and visual-fidelity checks, including native save/reopen and a source-to-export comparison. The comparator emits side-by-side/overlay/difference images and fails on excessive aspect drift; it never automatically declares visual fidelity from a pixel score. Correct topology and native object counts alone are insufficient. See [validation.md](validation.md) for the recorded test scope.

Export settings: **PDF → Selection (Current Canvas) → 100% → Transparent background**; **Include margin off, value 0 px**; exclude notes and nonprinting layers.

## Workflow references

The object-source decision process was informed by [image-to-editable-ppt-skill](https://github.com/ningzimu/image-to-editable-ppt-skill), an MIT-licensed PowerPoint reconstruction workflow. No PowerPoint runtime is bundled or required here. Optional locally installed [yuntao-omnigraffle](https://github.com/yuntaolu/yuntao-omnigraffle), [ccf-visual-composer](https://github.com/mikubaka88/CCFA-Skills/tree/main/ccf-visual-composer), and [nature-figure](https://github.com/Yuan1z0825/nature-skills/tree/main/skills/nature-figure) skills can assist with native authoring, composition, and Python scientific plotting.

This repository contains generic instructions, helpers, and a synthetic example. Research manuscripts, test images, source measurements, and reconstructed private figures are excluded.

## License

MIT. See [LICENSE](LICENSE).
