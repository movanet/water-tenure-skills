# Calibration cases

Worked patterns to set the level of detail and to make classification calls. They are not evidence
for a new catalogue: cite the originals listed against each published case.

Section 1 is **synthetic**: invented villages in a fictional basin, built to reproduce classification
problems met in real, unpublished Indonesian fieldwork without reproducing any of its data. Sections
2 and 4 come from published sources and carry their citations.

Contents:
1. A synthetic irrigation basin: the grain of a village inventory, and patterns that recur
2. Kahayan catchment, Central Kalimantan (published)
3. Remote cases from secondary sources
4. Other countries (FAO 2024, published)
5. What the cases teach

## 1. A synthetic irrigation basin (invented; not real data)

The synthetic example catalogue in
[../examples/synthetic-catalogue/](../examples/synthetic-catalogue/) is set in the fictional Kali
Wening basin, Arunika Province. Its design mirrors a common study design: three villages chosen for
contrasting irrigation conditions.

| Village (fictional) | Scheme | Condition | Main water sources |
|---|---|---|---|
| Sukarukun | Wening scheme | Modernised canals | Irrigation channel |
| Karangwangi | Wening scheme | Embankment collapsed years ago | Pumping from a secondary canal and the river |
| Tegalsari | Upland, outside the scheme | No canal reaches it | Springs, dug wells, rain |

A good village-level inventory reads like this (synthetic counts):

| Village | Informal tenure points | Other |
|---|---|---|
| Sukarukun | 3 canal openings; 1 pump with storage | 4 household boreholes (de minimis) |
| Karangwangi | 6 pumps from the river; 2 canal openings; 5 household pipes into the secondary canal | 2 sacred wells (customary) |

That is the right grain: type, count, location, each traceable to a map layer or a mapping walk.

### Patterns that recur, and how to classify them

These patterns were met repeatedly in real fieldwork. They are described here in general terms.

| Pattern | Classification and why |
|---|---|
| Collective river pumping by an unregistered pump group, running for decades. Members agree fees by deliberation and pay in kind per unit of land per season, cut on crop failure. The group says it would hold a permit if it could | `informal` (no permit reported, use persists), with `impossible` layered on (unregistered collective). Legal question flagged, not answered |
| Dry-season lease of most village land to outside growers, who pump for themselves; water follows ability to pay | Lessees' pumping `informal`. The pattern is a land-water nexus: land tenure moves water use to people with no water arrangement |
| Gate rotation at a division structure: the basin agency allocates hours per week and locks gates; the village group distributes inside the village; villages trade turns | `agency-control` for the scheme allocation; `commonhold` for the village distribution if the group is evidenced as recognised, otherwise flag it |
| Sacred wells and a pond: hundreds of households draw through their own small pumps and pipes; an annual thanksgiving ritual is held; access rules not documented | `customary` for the site and ritual, `de-minimis` for household pumping. The absence of documented rules is itself recorded |
| A village water official who also chairs the water user group, built canal openings with pipes to higher plots, and sets the date of the planting ritual, which delays irrigation | `customary` office overlapping `commonhold`. Flag the overlap of authority |
| Households taking primary-canal water by pipe or settling well, and river water during canal closure | `informal`. Avoid the hedge "may impact downstream allocations" unless a source shows it |
| Duck herders from outside the district grazing flocks along irrigation canals | `unrecognised`. "Locals assume they pay someone off" is hearsay: `uncorroborated` |
| A government programme lending pumps to farmers, contrary to the basin agency's stated policy | Record the actors and the practice. The authority question goes to `legal_flag` |
| Alleged paid diversion at gates ("water mafia") | `uncorroborated` until independently corroborated. Fee figures that differ across documents often describe two mechanisms; keep both, each with its source. Confidential informant notes stay out of any catalogue |
| Utility abstraction: barred from canals except existing intakes; difficulty renewing permits; community resistance at springs | `agency-control`. Permit-term and cap statements are flagged |

### Traps met when testing the skill on a real village corpus

A first run of this skill on one village's material produced 14 records, 0 checker errors, and every
quote and figure re-opened at its pinpoint. The run surfaced traps that will recur:

- **Transcripts missing locally.** The village interview transcripts were not on disk; every village
  voice arrived second-hand, through decks and an analysis paper. Register the originals as
  `drive-only` and cap confidence.
- **A village summary that is not evidence.** A machine-written village summary had to be treated as
  AI-generated: its pump fee contradicted two independent sources that agreed with each other.
- **One question, three answers.** Whether a water user group exists in the village: one document
  says no, two say yes. The record stays `unclassified`, `contested`.
- **Wrong-village attribution.** An analysis presented FGD figures under one village's heading, but
  one of the speakers quoted was from another district. Check each speaker's village before
  attributing.
- **Quotes moving between villages.** Two quotes tagged to one village in a preliminary-findings deck
  are attributed to another village in the field report.
- **Verbatim official interviews hidden in an extraction file.** Two agency interviews existed only
  inside a large text-extraction file. Cite them with a `char-offset` locator; they supplied
  independent official legs.

A baseline run without the skill found a similar number of arrangements and contradictions. It also
gave each arrangement a "legal status", used respondents' names, and cited the AI-written summary as
evidence. Those are the three things this skill exists to stop.

### The denominator lesson

The same set of women's interviews appeared with two different denominators in two decks, and with a
third framing ("never invited") elsewhere. The correct record states the interview set, the n, and
the file it was counted from.

## 2. Kahayan catchment, Central Kalimantan (AlAfghani and Susetyo 2023; AlAfghani, Lee and Yasuda 2025)

Table 1 of the JENRL paper maps tenure against use for the catchment. Most tenure there is de
minimis or customary. Modern permits attach to estates, commerce and hydropower. Informal tenure
appears in rural supply and aquaculture, assumed tenure in public irrigation and hydropower, and a
minimum-flow reserve exists.

Table 2 gives the Dayak Ngaju customary lexicon. It is the model for recording customary
arrangements: local term, physical form, who controls it, who may use it and on what condition.

| Term | Form | Control and use rule |
|---|---|---|
| handil | Dug canal, plus the fields along it | Canal and fields under collective management |
| tatas | Dug channel about 1x1 m | Owner (individual or family) levies a share of forest products carried through it; the family may extract resources up to about 500 m either side |
| saka / sungei | Small creek | Owners supervise activities; others may fish only if connected by marriage |
| beje | Dug pond, 25-250 m2 | Fish gather in it in the dry season; harvested by the farmer who dug it |
| baruh | Natural pond | Fishing is free access |
| pukung pahewan | Protected area | Guarded by custom against destruction |
| tabat | Weir | Not described |

Sources: AlAfghani, Lee and Yasuda (2025), Tables 1-2, citing Lubis (2013) and Satia et al. (2019);
AlAfghani and Susetyo (2023).

Note the hedging in the source paper, which says the authors could not confirm which types of
licence a hydropower plant held. Write unknowns like that.

## 3. Remote cases from secondary sources

Cases far from the field area (a nickel-processing island, a large food estate, a hydropower cascade)
can be described from investigative journalism, NGO monitoring and photo credits, with each figure
attributed inline.

What to copy:

- one claim per figure, each with outlet and date;
- source errors logged instead of silently fixed (a likely paste error in an ethnic name kept and
  flagged).

What to avoid: extending the cases beyond their sources, inferring tenure types nobody has described,
and turning "200 residents" into "200 families".

## 4. Other countries

Hodgson S, Gillet V, Espinosa Flor S, Ramirez Fionda S, Kiersch B and Vallée D (eds), *Water tenure
perspectives: Proceedings of the Water Tenure Mondays webinar series* (FAO 2024),
<https://doi.org/10.4060/cd2941en>. Page numbers are the printed ones.

The volume contains 14 articles from the 2021-22 webinars. The field cases below show what good
field-level description looks like in other systems. Chapters 2 (Islamic law), 11 (statutory
approaches to customary rights), 12-13 (conceptual) and 14 (transboundary) are doctrinal or
legislative. Read them for vocabulary and send their substance to the legal stage.

**Ch. 3, Indonesia and Viet Nam** (Al'Afghani, Lê Văn Chính, Hodgson, pp. 19-36), pilot areas
Kahayan, Rejoso and Nui Coc:

- At Nui Coc only the hydropower dam of four main facilities held a permit. The irrigation scheme and
  two water supply systems ran on assumed or informal tenure (p. 28).
- In Rejoso, unregistered artesian wells irrigating paddy are linked to the decline of the Umbulan
  spring. Community suppliers had no permit, either because they did not know one was needed or
  because the process was too onerous (pp. 24, 28).
- Viet Nam has religious arrangements: wells and ponds at pagodas (p. 28).
- Security is nested: a farmer's access depends on the WUO's service, the WUO's on the operator's
  delivery, and the operator's on its permit (p. 35). Record the chain, not just the farmer.

**Ch. 4, Awash basin, Ethiopia** (pp. 37-54):

- Permits for large estates specify no quantity, and gate operators make rough guesses (p. 44).
- A WUA receives water only when a neighbouring private estate has surplus (p. 45). This is
  commonhold on paper and dependency in practice.
- Pastoralists' water-point access and rights of way are not formalised. Their resistance shows up as
  canal diversions and cane fires (pp. 45, 49).
- Sugar estates rent land from pastoral clans (p. 41).

**Ch. 5, Warna sub-basin, Maharashtra** (pp. 55-68), two villages, four months:

- Groundwater is held by landowners. Canal rights are tied to land in the command area, so the
  landless are excluded (p. 58).
- In droughts, well water was lent to neighbours as a stop-gap courtesy that is now eroding.
  Irrigation water is shared within kin and caste (p. 63).
- A WUA exists on paper: no villager knew of it, though canal supply formally requires one (p. 63).
- Officials ignore over-irrigation of sugarcane beyond an agreement (p. 63).
- Methods used: transect walks; timelines of use and conflict; respondents listed by role
  (pp. 56, 62).

**Ch. 6, Spain, Duero and Upper Guadiana** (pp. 69-86):

- Water Register sections distinguish public concessions, private rights and small uses (Table 4,
  p. 74). The text is inconsistent on section letters (p. 82), so check before citing.
- Collective wells and collective management without rights (p. 74).
- Informal use runs at 20-30%, from over-abstraction by legal wells plus undeclared wells (p. 81).
- Irrigated area was mapped from satellite imagery, refined with aerial photos and the cadastre,
  then set against registered rights (pp. 75-81). The gap between the register and the field is the
  finding.

**Ch. 7, West Bank, Palestine** (Trottier, pp. 87-102):

- Spring systems run on time-based turns. In Battir, five families take a 5-day cycle (p. 90). In Ein
  Far'a a "day of thirst" is open to anyone (p. 90). Shareholders get gravity water free but owe
  maintenance labour in proportion to their water hours (p. 90).
- Rights are written on land deeds (p. 89), but custom passes them to sons only (p. 89 fn 28).
- Well companies keep accountant records of hours since the well began (p. 90).
- Wells drilled 2000-2008 got oral licences (p. 92).
- Unlicensed investor wells sell water and have dried springs (pp. 91-93).
- The poor pick mallow growing on leaks (p. 94): an invisible use.

**Ch. 8, Berrechid aquifer, Morocco** (pp. 103-120):

- A survey of 6 municipalities found 7,700+ water points, against 3,000 recorded by the basin agency
  for 16 municipalities (p. 111).
- Tenants lease land together with its wells, and some reports say they pump 2.5-4.5 times more
  than locals (pp. 112-113). This is the land-water nexus in another country.
- A 2021 concession contract between the basin agency and two WUAs lists members, area per crop, a
  GPS inventory of water points, a per-hectare cap and meters (p. 117).

**Ch. 9, Morogoro, Tanzania** (pp. 121-137):

- Farmers and pastoralists each claim customary or informal rights, and neither claim is
  enforceable (p. 132).
- Fishers negotiated permission to fish during designated times (p. 132).
- Women decide on household water but hold no recognised claim (pp. 133-134).
- Methods used: household survey; sex-separated FGDs.
- The chapter's own figures disagree with themselves: sample 278 vs 273; awareness 2% vs 25%
  (pp. 126-132). Check tables against text.

**Ch. 10, Kikuletwa, Upper Pangani, Tanzania** (Komakech, pp. 139-148):

- Furrow rights are earned by labour and fees ("hydraulic property creation"). Upstream users get day
  flows and downstream users night flows (p. 141).
- On the Ngarenaro, elders use a 70 cm bamboo stick with marks setting each canal's depth, reduced
  proportionally at low flow; fines are paid in livestock (pp. 142-144).
- On the Nduruma, permit holders cut back below their permits in dry months by negotiated turns, out
  of solidarity (pp. 144-145).
- One collective permit of 150 l/s is shared by agribusinesses, a golf course and villagers on 2-3
  hour turns every 14 days, with the intake closed on Sundays (p. 146).

**Ch. 15, Rwanda, Senegal, Sri Lanka** (Espinosa Flor, Kiersch, pp. 203-220):

- Rwanda: subsidised runoff dams and project boreholes run without permits, their users assuming
  legality because the project is official (p. 211). A textbook `assumed` case.
- Sri Lanka:
  - Paddy water follows registration in the Agricultural Land Register (pp. 212-214).
  - Water is released for pilgrimages and festivals, and communal wells and pots serve travellers
    (p. 215): religious practice as allocation events.
  - Pumping from tanks and canals is overlooked (p. 212).
- Senegal:
  - Only 139 of 402 private wells are authorised (p. 213).
  - A municipal deliberation form lets an agribusiness pay the municipality (p. 212).
  - Flood-recession land and water in Podor is held by four lineages and managed by the eldest male;
    women gain access through inheritance, loan, lease or purchase (pp. 213-214).
  - Griots set customary fishing rules (pp. 215-216).
  - Perceived security there exceeds legal security (p. 215).

**What the volume adds to method:**

- Separate what should happen from what actually happens (p. 36). The intention is to understand,
  not to judge (p. 35).
- Registers understate use, sometimes by more than half (Morocco, Spain). A register is evidence of
  paper, not of water.
- Distinguish informal *access* from informal *use* (pp. 82-83). Informality is a warning signal, and
  authorities seldom want to uncover it.
- Perceived security often departs from legal security, in both directions (pp. 20, 208, 215, 218).
- Community transect walks and maps can explain customary tenure quickly (p. 175).

## 5. What the cases teach

- Count and locate. "8 pump points" with a map layer beats "widespread pumping".
- Layering is the norm. One village, one season, three tenure types.
- Season decides tenure. The same plot can sit under scheme rotation in the wet season and under
  informal river pumping in the dry season.
- Position decides access. Head-end versus tail-end, served versus upland.
- Land and water tenure move separately. Leases, absentee owners and inheritance shift who uses water.
- The official view is evidence of toleration, not of legality.
- A "no difference" finding is reportable (for example, gender differences in use and roles but not
  in tenure arrangements).
- Unverified is a label, not a reason to drop. An "uncorroborated" label keeps an allegation usable
  and honest.
