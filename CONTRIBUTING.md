# Contributing

Contributions are welcome: corrections to the method, new calibration cases from published sources,
better scripts, translations of trigger terms, and reports of where the skills went wrong in practice.

## Before you start

- Open an issue describing the problem or the change, especially for changes to the record schema,
  the vocabularies or the checker's rules: other tools (the storymap importer, the report pipeline)
  depend on them.
- Read [docs/METHOD.md](docs/METHOD.md) and [docs/RESPONSIBLE-USE.md](docs/RESPONSIBLE-USE.md).

## What must never be committed

- Real field data: transcripts, interview notes, quotes from unpublished fieldwork, respondent codes
  of real people, photos, catalogues or coordinates of real places from unpublished work, report or
  annex text of real assessments.
- Credentials of any kind, cookie or browser-session settings, internal hostnames, IP addresses or
  local file paths.
- Copies of third-party tools.

Examples must be synthetic, labelled "Synthetic example, not real data", and set in the fictional Kali
Wening basin (or another clearly invented place). Calibration cases from **published** sources are
welcome with full citations and page pinpoints.

## Making a change

1. Fork, branch, and make the change.
2. Run the tests (offline):

   ```bash
   pip install pytest -r skills/water-tenure-report/requirements.txt
   pytest
   ```

   Install pandoc as well to run the .docx build test; without it that test is skipped.
3. If you changed a skill, check that its `SKILL.md` still has valid front matter, stays under about
   500 lines, and that every file it mentions exists. If you changed the record schema or a
   vocabulary, update the checker, the templates, the synthetic examples and the tests together.
4. Validate the plugin if you touched `.claude-plugin/`: `claude plugin validate . --strict`.
5. Open a pull request describing what changed and why, and how you tested it.

## Style

- Plain, precise English (British spelling in the skills); no emoji or status icons; no claims a test
  does not support.
- Python 3.9 or later; the standard library wherever possible.
- Conventional Commits for commit messages.

## AI-assisted contributions

This repository was itself written by AI coding agents under human orchestration, and AI-assisted
contributions are welcome. Say so in the pull request, name the tool and model, and confirm that a
person has read the change. The person opening the pull request is responsible for it.

## Licence

By contributing you agree that your contribution is released under the MIT licence of this
repository.
