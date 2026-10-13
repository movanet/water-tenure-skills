# Synthetic report example

**Synthetic example, not real data.** Every place, person, organisation, source, quotation and number
here is invented, and the map layers in `gis/` were drawn for the example (they sit in the open
ocean so they cannot be mistaken for a real place).

| Path | Content |
|---|---|
| `synthetic-config.yaml` | The report config: two input catalogues, map units, Parts, reserved sources, AI-use statement |
| `synthetic-chapters/` | Ten chapter files drafted from the evidence packs under the drafting brief, citing by token |
| `gis/` | Invented boundary and river layers |

The inputs are the synthetic catalogue of the `water-tenure-analysis` skill and the synthetic media
scan of the `water-tenure-media-scan` skill, so the example works when the three skills sit side by
side (as they do in this repository and in the plugin install).

```bash
python ../scripts/run_all.py synthetic-config.yaml
```

Outputs go to `_build/` (not versioned): `data/`, `packs/`, `figures/`, `annexes/` and `out/`, which
holds `main.md`, `annexes.md`, the two .docx files and `build-report.json`.

Four thin tenure types share Chapter 4 to keep the example short. A real report gives every tenure
type its own chapter with all nine sections of the template.
