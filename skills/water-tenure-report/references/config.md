# Report config reference

One YAML (or JSON) file drives every script. Paths inside it are relative to the config file. A
complete working example is [../examples/synthetic-config.yaml](../examples/synthetic-config.yaml).
Keys marked * are required.

## report

| Key | Meaning |
|---|---|
| `title`* | Report title (title page and document properties) |
| `subtitle` | Subtitle of the main volume |
| `subtitle_annexes` | Subtitle of the annex volume (default "Annexes") |
| `authors` | List of author lines. State the authorship honestly: name the person who directed the work and the AI agents that drafted it |
| `date` | Free text, for example "Draft for review, 2 October 2026" |
| `lang` | Language tag, for example `en-GB`, `id` |
| `output_name` | File name stem of the .docx outputs |
| `citation_style` | `oscola` (default) or `apa`. Read by merge.py when formatting references; re-run merge after changing it |
| `accessed` | Access date printed after web URLs ("1 October 2026") |
| `notice` | Optional line shown in bold at the top of the main volume (for example a draft or synthetic-data notice) |

## inputs*

A list of catalogues to merge, each a folder holding `sources.csv` and `arrangements.csv` that passes
`check_catalogue.py` from the `water-tenure-analysis` skill.

| Key | Meaning |
|---|---|
| `path`* | Folder of the catalogue |
| `origin` | Label shown in annexes and figures (for example `catalogue`, `media-scan`) |
| `prefix` | Prepended to every source id of this input, so registers cannot collide (`K01` becomes `NK01`). Inline citations in record text follow |
| `record_prefix` | Replaces the letter part of record ids (`A01` becomes `N01`) |

## chapters_dir, work_dir

`chapters_dir` holds the drafted chapters, `ch<NN>-<slug>.md`, assembled in number order
(`ch00` is front matter). `work_dir` (default `_build`) receives everything the scripts write:
`data/`, `packs/`, `figures/`, `annexes/`, `out/`, and `private/` (material never to be published).
Keep the work directory out of version control.

## area

| Key | Meaning |
|---|---|
| `name` | Area name used in figure titles |
| `groups` | Map of group name to keywords. A record is assigned to a group when its location fields contain a keyword; several matches give `several`, none gives `area-level`. Use it for sub-basins or two basins of one agency |
| `units` | List of map units: `name` (must match the boundary layer's name field), `patterns` (regular expressions matched against the lower-cased `location_admin`), `group` (colour on the location map) |
| `area_level_markers` | Phrases that mark a record as area-wide (not mapped) |
| `max_units_per_record` | A record naming more units than this is not mapped (default 4) |

## gis

| Key | Meaning |
|---|---|
| `admin` | GeoJSON of polygons for the map units (for example geoBoundaries ADM2, see `fetch_basemap.py`) |
| `admin_name_field` | Property holding the unit name (default `shapeName`) |
| `rivers` | GeoJSON of river lines (for example OpenStreetMap waterways) |
| `river_name_field` | Property holding the river name (default `name`) |
| `main_rivers_regex` | Rivers whose name matches are drawn heavier |
| `extent` | `[lon_min, lon_max, lat_min, lat_max]` of the map frame |
| `credit` | Data credit printed under every map; name the sources and their licences |
| `label_rivers` | Optional list of `{name, lon, lat}` river labels |

Without `gis`, the map figures carry a notice instead of a map and everything else still builds.

## parts

A list of `{first_chapter, title, intro}`. A Part page is inserted before the chapter whose number is
`first_chapter`. The List of Figures goes before the first Part page.

## reserved_sources

Method sources cited in chapters but held in no catalogue (FAO publications, the skill itself). Each
key is a token (`{{FAO-LWDP10}}`) with `oscola`, `apa` and `short` forms. Cite only published or
openly available works here; unpublished material belongs in a catalogue with its verifiability set.

## verification

Optional list of `[label, total N, checked or matched n]` for the verification figure in the
methodology chapter. Use the real counts of the project's spot checks.

## ai_use

| Key | Meaning |
|---|---|
| `statement` | The AI-use and authorship statement that opens Annex H |
| `directions` | List of `[when, session, direction]`: the human directions, paraphrased (never transcripts) |
| `not_verified_by_a_person` | List of what no person has yet read against its sources |
| `sessions_json` | Output of `mine_sessions.py` (default `<work>/data/sessions.json` when present) |
| `citecheck_summary` | Markdown summary of the cite-check (default `<work>/data/citecheck-summary.md`) |

See [ai-use-annex.md](ai-use-annex.md).

## Other keys

| Key | Meaning |
|---|---|
| `annexes` | Letters of the annexes to generate and build (default A to K) |
| `annex_b_sensitive_precision` | Decimal places kept for coordinates of sensitive records in Annex B (default 2, about 1 km) |
| `docx` | `heading_color`, `accent_color`, `body_color` (hex), `body_font`, `heading_font`, `page` (`A4` or `Letter`), `reference_doc` (use your own template instead of `make_reference.py`), `pandoc` (path to the pandoc binary) |
| `vocab_check` | Words reported by build.py when they occur in the body text (outside footnotes) |
| `grades.press_media_markers` | Words in a photo or video source's author field that mark it as press (E4) rather than social media (E5) |
