# Scan protocol

How to plan and run an N-day scan of news and social media for water tenure at named places, and
what to record while doing it.

Contents: 1. The scope sheet · 2. The query plan · 3. Passes with last30days · 4. The web-search
lanes · 5. From results to records · 6. The scan log

## 1. The scope sheet

Agree it with the person directing the work before the first search, and keep it in a scope file
(the example is [../examples/synthetic-scan-scope.yaml](../examples/synthetic-scan-scope.yaml)):

- **Area and places.** The basin or district, then the sub-areas to sweep one by one (sub-basins,
  districts or villages). A scan that searches only the basin name finds national stories and misses
  local ones.
- **Window.** Exact dates, for example 1 to 30 September. Record the window in the catalogue and the
  report; a "30-day scan" without dates cannot be repeated.
- **Themes.** What counts as water tenure at a place for this scan. A typical list: access to water
  in drought and how it is shared; springs and wells; irrigation structures, gates and turns;
  extraction (sand, minerals) that affects water users; community water systems; customary and
  religious practice at water sources; conflicts between users at a named point.
- **Exclusions.** Topics the director rules out, for example disasters as such, utility bills,
  water taxes and fees. Write them as terms so `scan_check.py` can flag records for review. An
  excluded topic can still appear when the record is about tenure at a place (a flood that destroyed
  a village intake and changed who controls it).
- **Languages.** The local languages of the press and of posts, plus English.

## 2. The query plan

Build a plan of place by theme, in each language, before running anything. One line per query:

| Place | Theme | Language | Query (example) | Lane |
|---|---|---|---|---|
| Karangwangi | drought access | id | `air kemarau Karangwangi` | last30days, web |
| Karangwangi | irrigation turns | id | `giliran air saluran Karangwangi` | web, news |
| Tegalsari | springs | jv | `tuk Tegalsari` | last30days |
| (district) | extraction | id | `tambang pasir Kali Wening` | web, video |
| (basin) | agency notices | id | `<basin agency name> jadwal` | agency site |

Rules for the plan:

- Use the words people use locally (terms for springs, gate turns, pumps, water officials); take
  them from the field catalogue's `local_name` values when one exists.
- Include the official channels: the basin agency's and the district's news pages and their
  institutional social accounts. Their posts are E5 when they are social media and E1 when they are
  official documents.
- Add at least one adversarial query per theme (conflict, protest, complaint, rejection) so the scan
  does not only find the official story.

## 3. Passes with last30days

`last30days` (https://github.com/mvanhorn/last30days-skill, MIT, by Matt Van Horn; tested with
version 3.26.0) is a Claude Code plugin that searches recent posts across platforms such as Reddit,
X, YouTube, TikTok, Instagram and Hacker News, plus the web, and ranks them by engagement. Install
it from its own marketplace:

```
/plugin marketplace add mvanhorn/last30days-skill
/plugin install last30days@last30days-skill
```

Run one pass per place-and-theme topic, with the window set explicitly:

```
/last30days <topic in the local language> --days=30
```

- `--days=N` sets the look-back; `--quick` and `--deep` trade speed against depth.
- Some platforms work only with an API key or a logged-in browser session, which the tool's own
  setup wizard asks about. Decide that with the person directing the scan. Keys and browser
  settings stay in the tool's own configuration on that machine; never copy them into the project,
  the catalogue or a report.
- Passes can hang on one platform. Stop a hung pass, note it in the scan log, and continue; do not
  report a platform as searched when its pass did not complete.
- The tool saves its raw output to its own folder. Treat that output as a list of leads: open every
  item you use and cite the item itself, not the tool's summary.

## 4. The web-search lanes

`last30days` is strongest on social platforms. Local press, agency notices and regional broadcasters
are found faster with plain web search:

- the agent's web search tool, by place and theme, in each language;
- a news search restricted to the window (for example a news aggregator's search with a date
  filter);
- the basin agency's and district government's own news pages, read from newest back to the start of
  the window;
- the video channels of regional broadcasters for press video (graded E4, not E5).

When last30days is not installed, the web lanes alone make a valid scan; say so in the scan log and
the report's method section.

## 5. From results to records

For every item that evidences an arrangement at a place:

1. Open it. Record title, author or account, outlet or platform, date of publication, URL.
2. Register it in `sources.csv` with the right `source_type`: `news`, `photo-video` (press video and
   photos), `social-media`, `admin-record` (an official notice or document), `ngo-report`.
   `author_org` takes the form `Author; Outlet` or `Account; Platform`. For a private person write
   `private account; <Platform>` and keep the handle out of the catalogue.
3. Write or extend an arrangement record with the `water-tenure-analysis` skill's rules: one rule-set
   by user group by place by period, located administratively and hydrologically, classified on the
   FAO typology, legal questions as questions.
4. Copy every figure exactly as printed, with its unit, and say in `figures_source` which source
   prints it. Mark it UNVERIFIED when the page text could not be read.
5. A record resting only on social media is graded `uncorroborated` and noted as a clue.

Then run, in this order: `check_catalogue.py`, `scan_check.py --scope`, `verify_figures.py --cache`.

## 6. The scan log

Keep a short log beside the catalogue (`scan-log.md`), because the report's method section and
Annex H need it:

- the window, the places and themes, the languages;
- each last30days pass: topic, flags, date run, platforms completed, platforms that failed or hung;
- each web lane: queries run, date run;
- audited absences: what was searched for and not found, by place;
- items seen but excluded, with the scope rule that excluded them;
- figures left UNVERIFIED and why.
