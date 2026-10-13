# Synthetic example catalogue

**Synthetic example, not real data.** Every place, person, organisation, source, quote and number in
this folder is invented. The Kali Wening basin, Arunika Province, Mekarsari District and the villages
of Sukarukun, Karangwangi and Tegalsari do not exist. Coordinates are deliberately placed in the open
Indian Ocean (around 12.8 S, 101.1 E) so that they cannot be mistaken for a real place. Source URLs
use the reserved `example.org` domain and do not resolve.

The catalogue reproduces classification problems that recur in real fieldwork (layered tenure,
seasonal pumping, a land-lease nexus, a contested water user group, a machine-written summary that
is not evidence, an allegation kept as uncorroborated) so that the skill's rules can be seen at work.

| File | Content |
|---|---|
| `sources.csv` | 20 sources: interviews, an FGD, a workshop, records, a permit register, statistics, a mapping deliverable, a drone layer, news, an NGO report, an academic paper, a derived summary and an AI-generated note |
| `arrangements.csv` | 18 arrangements across 12 tenure types, including one `unclassified` and two `contested` records |
| `matrix.md` | Output of `build_matrix.py` |

Run from the skill folder:

```bash
python scripts/check_catalogue.py examples/synthetic-catalogue
# 20 sources, 18 arrangements, 0 errors, 0 warnings
python scripts/build_matrix.py examples/synthetic-catalogue --out matrix-check.md
python scripts/export_storymap.py examples/synthetic-catalogue --out map-records.geojson
```

Things to notice:

- **A001** is `corroborated`, not `triangulated`: the agency's plan and the agency's officer are one
  leg (an agency describing its own allocation).
- **A004** is `informal` with `impossible` layered on, keeps two pump counts from two sources in
  `contradictions`, and asks its legal question without answering it.
- **A013** keeps a hearsay payment claim as `uncorroborated`; the map export leaves it out.
- **A016** stays `unclassified` and `contested`: the machine-written summary (S08) says there is no
  water user group, two other sources say there is. The AI-generated desk note (S09) is registered
  but never cited as evidence.
- **A018** shows a plan (minimum release) contradicted by practice, kept as `contested` with both
  versions.
