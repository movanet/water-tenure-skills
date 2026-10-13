# Tenure and use typology

How to classify what the evidence shows. Read this before you assign a `tenure_type` or `water_use`
to a record.

Contents: 1. What counts as an arrangement · 2. Tenure types · 3. Classifying from field evidence ·
4. Water use codes · 5. User attributes · 6. The tenure x use matrix · 6a. Security · 6b. Definitions
that disagree · 6c. Sub-types met in other countries · 7. Analytical lenses · 8. Where the
vocabulary came from

## 1. What counts as an arrangement

FAO defines water tenure as the relationship, legally or customarily defined, between people, as
individuals or groups, with respect to water resources, and a water tenure arrangement as the way
people gain access to and use water and relate to each other through a set of formal or informal
rules and agreements (FAO 2016, *Exploring the concept of water tenure*, Land and Water Discussion
Paper 10).

FAO's land tenure work frames tenure as deciding who can use what resources, for how long, and under
what conditions (FAO 2002, *Land tenure and rural development*, Land Tenure Studies 3). Applied to
water, every record in the catalogue should answer four questions:

| Question | Record fields |
|---|---|
| Who can use water? | `users`, `user_attributes`, `holder_controller` |
| What resource? | `water_source`, `location_hydro` |
| For how long / when? | `period_season`, duration in `arrangement` |
| Under what conditions? | `access_rule`, `allocation_rule`, `payment`, `labour_contribution`, `decision_making`, `enforcement_sanction` |

One arrangement is one rule-set governing one group's use of one source in one place. When the same
farmers draw from a canal under the water user group's rotation in the first planting season and pump
from the river in the dry season, that is **two** records linked through `secondary_tenure_types` /
`notes`, not one blurred record. Water moves and seasons change who has it (the "transient tenure"
problem), so `period_season` is not optional decoration: an arrangement that holds only in the dry
season must say so.

## 2. Tenure types

FAO's water tenure work groups arrangements into **two families and 16 named types** (FAO 2016;
FAO 2020, *Unpacking water tenure for improved food security and sustainable development*; applied in
AlAfghani and Susetyo 2023 and AlAfghani, Lee and Yasuda 2025). There is no single "formal" type.
Use the vocabulary key in the first column; `scripts/check_catalogue.py` rejects anything else. The
short definitions below are paraphrases; quote the published FAO texts, not this table, in anything
you publish.

### Family 1: arrangements derived from formal law

| Key | FAO name | Short definition (paraphrase) | Field indicators |
|---|---|---|---|
| `traditional-formal-right` | 'Traditional' formal water rights | Rights to use water that follow from land tenure rights or from prior use | Water follows the land title; riparian or prior-use claims |
| `modern-permit` | 'Modern' formal water rights | Long-term, permit-based rights (often 12-30 years or more), separate from land, assertable against the state and third parties | Long-term permit document, register entry |
| `regulatory-licence` | Regulatory licences | Short-term (for example annual) licences | Annual or short licence, renewal cycle |
| `agency-control` | Agency control ("agency tenure") | A public agency (irrigation, water, river basin or regional development) holds broad legal powers to abstract and use water | River-basin agency, dam operator, water utility or irrigation agency allocating water and operating gates |
| `water-supply-contract` | Water supply contracts | Written contracts for bulk supply | Bulk raw-water contracts between an agency and a utility or industry |
| `commonhold` | Commonhold water tenure | Rights to water held in common by a defined community of users, such as members of a water user organization | Water user association or federation holding and distributing a share; check whether it exists "only on paper" |
| `investment-contract` | Investment contracts | Water rights embedded in investment or concession agreements | Industrial estates, plantations, mines, hydropower concessions |
| `de-minimis` | De minimis (small-scale) rights | The right to take small quantities for non-commercial uses (domestic needs, subsistence gardens) without administrative formalities | Household dug wells and shallow boreholes, buckets from the river, small garden watering |
| `exempt-declared-commercial` | Declared or exempt commercial uses | Commercial uses exempted from permits or merely declared | Small enterprises below a permit threshold |
| `reserve-minimum-flow` | Reserves and minimum flow requirements | Water set aside for the environment or for basic needs | Environmental flow releases, reserved volumes in basin plans |

### Family 2: arrangements not established on the basis of formal law

| Key | FAO name | Short definition (paraphrase) | Field indicators |
|---|---|---|---|
| `customary` | Customary water tenure | Rights based on customary or local law, which formal law may or may not recognise | Rules attributed to ancestors or custom (*adat*), a customary office-holder, ritual preconditions, sacred sources |
| `religious-law` | Religious law water tenure | Arrangements derived from religious law | Mosque or prayer-house water open to all, endowed (waqf) wells, religious rules on sharing |
| `informal` | Informal water tenure | Use without a formal basis, either tolerated by the water administration (sometimes for years) or simply unlawful | Pumping from canals or rivers without a permit, unofficial canal openings, pipes into primary canals |
| `assumed` | Assumed water rights | Formal rights wrongly assumed to exist because the use is by a public or quasi-public body and looks official | A utility, village government or agency abstracting with no current permit, everyone treating it as lawful |
| `impossible` | Impossible water tenure | Formal rights that cannot exist because the presumed holder lacks legal capacity (for example an informal water committee) | Unregistered water user group, informal pump group, community water committee without legal personality |
| `unrecognised` | Unrecognised water tenure | Livelihood activities that water law does not typically regulate, such as inland fisheries and wetland use | Fishing, duck herding in canals, wetland harvesting, sand or reed gathering |

Plus `unclassified`, for when the evidence does not allow a call yet. Use it rather than guess, and
say in `classification_basis` what evidence would decide it.

## 3. Classifying from field evidence

Four of the Family 2 labels rest on a legal premise: that no formal right exists (`informal`,
`assumed`), that the holder has no legal personality (`impossible`), or that the use falls outside
water law (`unrecognised`). This skill does not decide those premises. It does three things instead:

1. **Classify on what the evidence shows about practice and about how people and officials treat
   the use.** "Agency staff say they know about the pumps and do not act" is evidence of toleration;
   "the farmers say they have no permit" is evidence of absence of a permit. Both are reported
   facts, cited to their source.
2. **Write the premise into `classification_basis` as a reported fact**, with the source:
   `informal: farmers state they hold no abstraction permit (INT-V1-04 l.212); the gate keeper
   describes them as "maling air" (INT-GOV-02 l.88)`.
3. **Put the legal question in `legal_flag`**: `Does pumping by an unregistered farmer group from the
   Kali Wening require an abstraction permit, and could such a group hold one?` Do not answer it. See
   [legal-boundary.md](legal-boundary.md).

FAO's guidance notes that informal, assumed and impossible tenure can usually be identified only
through interviews and field research, warns against the judgmental tone of calling informal use
"illegal water use", and notes that the rich and politically connected use water informally too.
Write records in that neutral register: describe the use, attribute any label of illegality to
whoever used it.

**Decision order** when a use could fit several types:

1. Is there a document (permit, contract, register entry) that the evidence actually shows? Then a
   Family 1 type, and cite the document or the record that shows it. A respondent saying "we have a
   permit" is a claim; record it and mark `confidence` accordingly.
2. Is the use run by a public or quasi-public body and treated as official, with no document in
   evidence? Candidate `assumed`.
3. Is the presumed holder an unregistered collective? Candidate `impossible` (often alongside
   `informal` for the use itself; record both via `secondary_tenure_types`).
4. Does the rule-set claim authority from custom, ancestors, ritual or a customary office? `customary`.
5. Is the activity a livelihood that water law does not address at all (fishing, ducks, wetlands)?
   `unrecognised`.
6. Otherwise, a use without formal basis that persists: `informal`. Record whether toleration is
   evidenced.

Layering is normal. A single village can draw household water from a primary canal (`informal`),
from sacred wells (`customary`) and from private shallow wells (`de-minimis`) at the same time.
Catalogue every layer.

## 4. Water use codes

Use the FAO water tenure assessment use codes in `water_use` (several allowed, `;`-separated). The
codes group uses by their likely tenure implications. The letters below follow AlAfghani and Susetyo
(2023); see the variants note after the table.

| Code | Use | Notes |
|---|---|---|
| A1 | Drinking water, urban infrastructure | Piped utility supply |
| A2 | Drinking water, rural infrastructure | Village piped schemes, community water systems |
| A3 | Drinking water, rural unimproved | Dug wells, shallow boreholes, springs, river, refill vendors as a source |
| B1 | Commercial estate irrigation | Plantations, estates |
| B2 | Public irrigation scheme | Government-built schemes |
| B3 | Small-scale non-public irrigation | Farmer- or NGO-built systems, private pumps outside schemes |
| B4 | River-bank gardens / flood-recession irrigation | |
| B5 | Livestock watering | Flag pastoralists who do not own the land at watering points |
| B6 | Aquaculture | Fish ponds, brackish ponds, dug fish pits |
| C | Commerce / industry | Only direct abstraction or bulk contracts, not utility-supplied industry |
| D1 | Power, thermal | Cooling water |
| D2 | Power, hydropower | |
| E1 | Environment, instream | |
| E2 | Environment, diversion | |
| F | Navigation | Includes informal navigation |
| G1 | Livelihoods, inland fishing | |
| G2 | Livelihoods, wetlands | |
| H1 | Recreation / landscape, instream | |
| H2 | Recreation / landscape, other | Includes ritual and cultural sites where they are not domestic sources |
| I | Other | Name it in `arrangement` |

Domestic uses beyond drinking (bathing, washing, ablution, menstrual hygiene in the fields) fall
under A1-A3; record the sub-use in `arrangement`. Field studies regularly find that the domestic and
hygiene uses of women are the least recorded, so look for them. Reviewers object when drinking and
other domestic use are run together, so name the sub-use.

**Code variants.** The letters are not stable across documents:

- AlAfghani, Lee and Yasuda (2025), Table 1, puts livestock, aquaculture and commerce under C1-C3.
- AlAfghani and Susetyo (2023) puts livestock and aquaculture at B5/B6 and commerce at C.
- Project documents sometimes split C into industry and mining.

This skill uses the letters listed above. When you take a matrix from another document, map its codes
and say so in `report.md`.

## 5. User attributes

FAO's guidance names "user categories" as an output but gives no user typology. The catalogue
therefore carries its own `users` (who, in plain words: "rice farmers at the tail of the West
secondary canal", "seasonal onion growers renting land", "the district water utility") and
`user_attributes`, a `;`-separated list from this vocabulary, used only when the source supports it:

`women` · `men` · `persons-with-disabilities` · `elderly` · `youth` · `landless` · `tenant-or-lessee` ·
`sharecropper` · `labourer` · `non-resident-landowner` · `migrant-or-outsider` · `tail-end` ·
`head-end` · `upland-not-served` · `smallholder` · `large-landholder` · `indigenous-or-customary-community` ·
`public-entity` · `private-company` · `collective-unregistered` · `collective-registered`

The checker warns on values outside this list. Record who is **absent** too. "Women manage all
household water but none attend water user group meetings" is a finding about users, and it belongs
in `gedsi_notes` with its source and denominator.

## 6. The tenure x use matrix

FAO's mapping task crosses tenure types (rows) with use codes (columns) and marks each combination
found. AlAfghani, Lee and Yasuda (2025, Table 1) give one for the Kahayan catchment in Central
Kalimantan. `scripts/build_matrix.py` derives it from `arrangements.csv`, with the count of records
in each cell instead of an X, so every mark traces back to records and from records to sources.
Empty rows are findings too: say whether a type is absent or simply not yet looked for.

## 6a. Security: what this skill records and what it leaves

AlAfghani and Susetyo (2023) define tenure security as "the defeasibility and defensibility of a
particular tenure", both sociologically (de facto) and legally (de jure). AlAfghani, Lee and Yasuda
(2025) use "de facto" where FAO says "perceived security", to emphasise the empirical assessment.
They note two things:

- Upstream users usually control "wet water" while downstream users may hold only "paper water".
- Informal tenure, though insecure in law, can be secure in practice because of the political
  economy.

This skill records the **de facto / perceived** side only (`perceived_security`, `upstream_downstream`,
`recognition_reported`, `conflicts`), with evidence. A numeric legal security score and governance
ratings are for the legal and governance stages (see [legal-boundary.md](legal-boundary.md)).

Three factors drive de facto strength (AlAfghani, Lee and Yasuda 2025). Describe them when the
evidence allows:

1. Position in the allocation framework.
2. Upstream or downstream location.
3. Overlap with other tenures.

## 6b. Definitions that disagree between sources

Project reports sometimes define *assumed* tenure as users assuming they have rights, "common in
customary systems", and elsewhere in the same document use the FAO definition (public or
quasi-public users wrongly presumed to hold formal rights). Use the FAO definition. Customary users
who believe they have rights are `customary`, with their belief recorded under `perceived_security`.

The same practice can be treated as customary in one chapter and informal in another. Classify each
instance by its own evidence:

- A canal-wall opening built by the village water official and governed by village rules can be
  `customary`.
- One opened at night by individual farmers is `informal`.

## 6c. Sub-types and refinements met in other countries

The FAO typology is a common vocabulary, not a closed list (FAO 2024, *Water Tenure Perspectives*,
p. 208 fn 59). When an arrangement fits a type only loosely:

1. Keep the closest key in `tenure_type`.
2. Name the sub-type in `arrangement`.
3. Explain the fit in `classification_basis`.

Sub-types documented in that volume (pages are printed pages):

| Sub-type | Closest key | Where |
|---|---|---|
| Informal "deliberately illegal" vs "evolved over time" | `informal` | Ch. 3 Table 1, p. 22 |
| Informal *access* vs informal *use* (a legal well over-abstracting is informal use) | `informal` | Ch. 6, pp. 82-83 |
| Paper WUA: the user body exists only in documents | `commonhold` on paper; describe the practice | Ch. 5, p. 63 |
| Collective permit shared by companies and villagers | `commonhold` / `modern-permit` | Ch. 10, p. 146 |
| Concession contract between basin agency and WUAs (members, caps, meters) | `investment-contract` / `commonhold` | Ch. 8, p. 117 |
| Oral licence issued by the water authority | `regulatory-licence`, flag the form | Ch. 7, p. 92 |
| Municipal deliberation giving use against a payment | `informal`, flag | Ch. 15, p. 212 |
| Customary tenure embedded in pastoralists' land tenure | `customary` | Ch. 4, p. 49 |
| "Living customary tenure", renegotiated each season, nested in formal WUAs | `customary` | Ch. 10, pp. 139, 147 |
| Tenancy-linked access: a land lease carries well water | Record land and water tenure separately | Ch. 8, pp. 112-113 |
| Religious allocation events (releases for pilgrimages and festivals, wells for travellers) | `religious-law` | Ch. 15, p. 215 |

Two further distinctions help describe arrangements:

- **Infrastructure rights vs resource rights** (van Koppen, Ch. 13, pp. 171-176). Rights earned by
  building or maintaining a canal or well ("hydraulic property creation", sweat equity, joining
  fees, turns) are not rights to the water flowing in it. Record which one the evidence shows.
- **"Sharing in" vs "sharing out"** (Ch. 12-13, pp. 164, 180): allocation among members of a
  community, as against allocation to outsiders.

## 7. Analytical lenses (optional, attribute them)

These describe *patterns across* arrangements. They are analytical lenses from CRPG's field work and
from the literature, not FAO categories, and must be attributed as such when used.

| Lens | Meaning | Origin |
|---|---|---|
| Tolerated illegality | Agencies know of and do not act on informal use, which becomes durable | CRPG field analysis; compare FAO 2024, Ch. 6 and Ch. 15 |
| Land-water tenure nexus | Land leases move water use to people with no water arrangement (seasonal lessees who pump for themselves) | CRPG field analysis; the same pattern in FAO 2024, Ch. 8, pp. 112-113 |
| Bundle of rights and bundle of power | Formal entitlements versus the capacity to exercise them (information, forum, enforcement, exit, bargaining) | CRPG extension of the FAO bundle-of-rights discussion; mark it as a forward-looking lens |
| Visibility as governance | Who is absent from registers and counts is the governance question | CRPG |
| Economic power as de facto tenure | Capacity to pay for pumping decides access where formal tenure is absent | CRPG field analysis; AlAfghani, Lee and Yasuda 2025 on wet and paper water |

The five-part bundle (access, withdrawal, management, exclusion, alienation) is from the commons
literature (Schlager and Ostrom 1992), **not** from FAO, whose own bundle lists use, participation,
consultation, management, transfer and conflict rights. Do not attribute the five-part bundle to FAO.

## 8. Where the vocabulary came from

Published sources (cite these):

- FAO, *Exploring the concept of water tenure* (Land and Water Discussion Paper 10, FAO 2016), by
  Stephen Hodgson. Use it for definitions.
- FAO, *Unpacking water tenure for improved food security and sustainable development* (FAO 2020).
- Hodgson S and others (eds), *Water tenure perspectives: Proceedings of the Water Tenure Mondays
  webinar series* (FAO 2024), <https://doi.org/10.4060/cd2941en>. Fourteen country and thematic
  chapters; see [calibration-cases.md](calibration-cases.md) section 4.
- AlAfghani MM, Lee J and Yasuda Y, 'Potential contribution of the water tenure approach to the
  implementation of international norms applicable to river basins' (2025) *Journal of Energy &
  Natural Resources Law*, <https://doi.org/10.1080/02646811.2025.2545686>. Used here: Table 1, the
  Kahayan tenure x use matrix; Table 2, the Dayak Ngaju customary lexicon; de jure versus de facto
  security.
- AlAfghani MM and Susetyo B, 'Water Tenure Security for Palm Oil, Hydropower, and Geothermal' (2023)
  1199 *IOP Conference Series: Earth and Environmental Science* 012016.
- FAO, *Land tenure and rural development* (Land Tenure Studies 3, FAO 2002).
- Schlager E and Ostrom E, 'Property-rights regimes and natural resources: a conceptual analysis'
  (1992) 68 *Land Economics* 249.

FAO and its partners (including the KnoWat project) also circulate water tenure assessment guidance.
Draft versions marked "for validation" or "do not cite" may guide method, but do not quote them in
published text: cite the published FAO works above where the content matches. Draft guidance has also
been known to number its tables inconsistently with their captions, so cite tables by caption.
