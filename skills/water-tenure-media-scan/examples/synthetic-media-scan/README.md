# Synthetic media scan

**Synthetic example, not real data.** Every outlet, account, article, place and number here is
invented. URLs use the reserved `example.org` domain and do not resolve.

| File | Content |
|---|---|
| `sources.csv` | 7 sources: three news articles, a press video, an institutional post by the basin agency, an institutional post by a village government, and a video by a private account (recorded as `private account; TikTok`) |
| `arrangements.csv` | 4 records: night-time gate opening (informal, corroborated by press and the agency's post), tanker water (unclassified, figure UNVERIFIED), sand extraction (unrecognised), a spring ritual seen only on social media (customary, uncorroborated: a clue) |
| `page-cache/` | Invented article texts for `verify_figures.py` |
| `scan-log.md` | What the scan searched, what failed, and what it did not find |

Things to notice:

- **A01** cites the agency's post together with the press report it corroborates.
- **A02** keeps its price figure marked UNVERIFIED because the article body loads by script; the page
  cache holds a browser capture, so `verify_figures.py` reports the figure as found but still marked,
  and a person decides whether to lift the mark.
- **A04** rests only on social media, so it is `uncorroborated` and goes to the report's Clues
  section, not to its findings.
