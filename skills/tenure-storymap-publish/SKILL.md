---
name: tenure-storymap-publish
description: 'Publishes a checked water tenure catalogue as map records for the water tenure storymap engine (github.com/movanet/water-tenure-storymap): writes a privacy-filtered publication copy of the catalogue (no names, sensitive points rounded and marked aggregate_only, uncorroborated and social-media-only records left out), then runs the storymap''s import_catalogue.py to a seed file or to a running site. This skill should be used when the user asks to publish, map, upload, import or seed tenure records or a tenure catalogue to a storymap, a tenure map or a tenure engine, or to prepare catalogue data for public release ("publikasikan ke peta tenurial", "storymap").'
license: MIT
metadata:
  version: "1.0.0"
  author: "CRPG - Center for Regulation, Policy and Governance (vibe-coded with AI agents, orchestrated by Mohamad Mova Al'Afghani)"
---

# Publish a tenure catalogue to the storymap

The companion repository **movanet/water-tenure-storymap** is a map and story site with a tenure
engine (the software behind https://tenure.crpg.info). Its `tools/import_catalogue.py` reads a
catalogue in this pack's format and turns each arrangement into a tenure record. A map is public and
precise in a way a report is not, so nothing goes onto it without the protection rules below and a
person's approval.

## Data-protection rules

- **No names.** No respondent names, codes, quotes or private social-media accounts on the map.
- **Coordinates only from sources.** A record without source-stated coordinates is not placed, or is
  placed at a village centroid that the map labels as approximate (`--centroids`). Never estimate a
  point.
- **Sensitive records are aggregate_only**: informal, impossible, unrecognised and assumed tenure;
  sacred or ritual sites; records mentioning allegations; uncorroborated records; records citing a
  consent-restricted or non-anonymised source. Their coordinates are rounded before export
  (default 2 decimals, about 1 km), and the storymap API adds its own jitter to aggregate_only points
  on public reads.
- **Clues are not published.** Records resting only on social media, AI-generated or derived sources
  are left out; uncorroborated records are left out unless the person responsible decides otherwise.
- **Ask the community** before publishing the location of a customary or sacred site, even rounded.
- **Photos**: only with the consent of the people shown; check for faces of private persons and for
  embedded GPS data before upload.
- **Tokens stay in the environment.** Posting to a site uses a bearer token read from an environment
  variable, never typed on the command line or saved in the project.

## Steps

1. **Check** the catalogue: `check_catalogue.py <catalogue-dir>` (water-tenure-analysis skill), no
   errors.
2. **Publication copy:**

   ```bash
   python <skill-dir>/scripts/publication_copy.py <catalogue-dir> --out <publication-dir>
   ```

   It adds a `sensitivity` column (which the importer honours), rounds coordinates, drops clue-only and
   uncorroborated records, and clears quotes, respondent codes, GEDSI and security notes, and the
   paths of sources a reader cannot open.
3. **Review**: a person reads `<publication-dir>/arrangements.csv` before anything is sent.
4. **Import** with the storymap repository checked out (see its README for setup):

   ```bash
   # to a seed file for a new site (set SEED_FILE to it; the API loads it into an empty database)
   python tools/import_catalogue.py --arrangements <publication-dir>/arrangements.csv \
       --sources <publication-dir>/sources.csv --out records.geojson --season-map "MT1=wet,MT2=dry1,MT3=dry2"

   # or to a running site
   export TENURE_API_TOKEN=...    # set in the shell, never in a file in the project
   python tools/import_catalogue.py --arrangements ... --sources ... --post https://<your-site>
   ```

   Useful options: `--centroids FILE` (name,lat,lon for villages), `--scheme-map` (scheme names to
   the site's irrigation-scheme vocabulary), `--all-aggregate` (mark everything aggregate_only),
   `--id-prefix` (default `cat-`), `--vocab` (the site's vocabulary file). Records are validated
   against the site's vocabulary before anything is written or sent; skipped rows are reported.
5. **Check on the map** that aggregate-only points appear only approximately and that no record shows
   a name or a quote.

An alternative for review without the storymap is `export_storymap.py` in the water-tenure-analysis
skill, which applies the same rules and writes plain GeoJSON.

## Script

| Script | What it does |
|---|---|
| `scripts/publication_copy.py <dir> --out <dir> [--include-uncorroborated] [--sensitive-precision N] [--precision N]` | Writes the privacy-filtered copy of the catalogue described above. Standard library only |
