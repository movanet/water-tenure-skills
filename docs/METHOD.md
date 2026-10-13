# The method in plain language

This page explains, without code, what the skills do and why. The rules themselves live in the
skills, chiefly `skills/water-tenure-analysis/`.

## 1. What water tenure is

FAO describes water tenure as the relationship, legally or customarily defined, between people, as
individuals or groups, with respect to water (FAO 2016). A **tenure arrangement** is the way people
gain access to water and use it, and relate to each other through formal or informal rules: who may
take water, from where, when, how much, on what conditions, who decides, who pays, who maintains, who
enforces, and what happens when the rules are broken.

A water tenure assessment asks which arrangements exist in an area, how they work, who they serve and
who they leave out, and how secure they are. FAO's approach runs two streams with different expertise:
a **field stream** that describes practice, and a **legal stream** that asks what the law says about
it. These skills are the field stream. They describe; they do not decide what the law requires.

## 2. The FAO typology

Arrangements are classified into two families of types (FAO 2016; FAO 2020; applied in AlAfghani and
Susetyo 2023 and AlAfghani, Lee and Yasuda 2025).

**Derived from formal law:** rights that follow land ("traditional" formal rights); long-term permits
("modern" formal rights); short-term regulatory licences; agency control, where a public body holds
broad powers to allocate and operate water; water supply contracts; commonhold, where a defined group
such as a water user association holds water in common; investment contracts; de minimis rights, the
freedom to take small quantities for basic needs without a permit; declared or exempt commercial uses;
reserves and minimum flows.

**Not established on formal law:** customary tenure; religious-law tenure; informal tenure, a use
without formal basis that persists and may be tolerated; assumed rights, where a public or
quasi-public use is treated as lawful though no instrument is in evidence; impossible tenure, where
the holder lacks the legal capacity to hold a right (an unregistered collective); unrecognised
tenure, livelihoods water law does not address, such as fishing or wetland use.

A record that the evidence does not allow to classify stays **unclassified**, and says what would
decide it. Layering is normal: one village can take water under four types at once, and one plot can
move between types with the season. Each use is also coded on the FAO water-use codes (drinking water,
irrigation of several kinds, livestock, aquaculture, industry, power, environment, navigation,
fishing, wetlands, recreation and culture), so tenure can be cross-tabulated against use.

## 3. The record

The unit of analysis is the **arrangement record**: one rule-set governing one user group's use of one
source, at one place, in one period. Each record says how the arrangement works in plain prose, where
it is (administratively, from province to hamlet, and hydrologically, from basin to gate, spring or
well), who uses the water and who controls access, and which sources support each statement, with a
pinpoint (page, line, slide, timestamp, row) a reviewer can open. Every source is registered once,
with its type, date, location and how far it can be opened by a reader.

Records are kept as two CSV files because people verify them in a spreadsheet: filter by village or
source, tick rows, add notes. A checker script enforces the closed vocabularies, the pairing of every
citation with a pinpoint, and the confidence rules below.

## 4. Confidence and evidence grades

Two separate measures:

- **Confidence** belongs to a record and comes from triangulation. *Triangulated*: three or more
  independent origins, of at least two primary source types. *Corroborated*: two independent origins.
  *Single-source*: one first-hand source. *Uncorroborated*: hearsay or an allegation. *Contested*:
  sources disagree, and both versions are kept. Two documents produced from the same round of
  fieldwork count as one origin; so do an agency's report of its own work and its official describing
  it.
- **Evidence grade** belongs to a source and says what kind of source it is: E1 primary legal or
  official; E2 field primary (interview, focus group, workshop, observation); E3 scholarly or
  technical; E4 press; E5 social media; D a derived digest (a summary, a wiki page), which only points
  to an original.

Social media are clues. A post can corroborate other evidence about the same place, time and actor;
on its own it is a lead for follow-up, never a finding. Material written by an AI system is never
evidence at all.

## 5. The legal boundary

Several types rest on a legal premise: that no permit exists, that a holder lacks legal personality,
that a use falls outside water law. The field stream does not decide those premises. It records what
people and officials report ("farmers say they hold no permit"; "the agency officer says the pumps are
tolerated"), cites who said it, classifies on that reported practice, and writes the legal question as
a question for the legal stream. The report never calls a use illegal in its own voice.

## 6. Place, season and who is missing

Arrangements are tied to named places and points: a spring, a gate, an intake, a reach. Position
matters: head-end and tail-end farmers on the same canal live under different arrangements. Seasons
matter: a canal rotation in the wet season can give way to river pumping in the dry season. And the
evidence is searched for the users who are easily missed: women's household and hygiene water,
tenants and seasonal lessees, landless labourers, fishers, herders, upland households beyond the
canal, people with disabilities. An absence the evidence supports is itself a finding.

## 7. Verification

- The checker runs on every catalogue; errors must be fixed and warnings read.
- **Spot verification**: every figure and every quotation, and at least one record in five, is
  re-opened at its pinpoint and compared with the source. Results are reported as "n of N checked",
  never as a percentage alone.
- In a long report, a **cite-check** reads a sample of footnoted statements against their sources,
  prioritising figures, quotations and statements about who decides, pays or is excluded.
- Figures are copied exactly as printed. Conflicting figures are kept side by side, each with its
  source; they are never averaged.
- What no person has verified is listed, plainly, in the report.

## 8. Where AI agents fit

AI agents register sources, extract records, search, draft and check at a volume a team cannot. They
work under written rules (the skills), and their output is checked by scripts and read by people at
fixed gates: scope, catalogue, report, legal referral, publication. The person directing the work sets
the questions, the method and the scope rulings, and decides at each gate. Reports say so. See
[RESPONSIBLE-USE.md](RESPONSIBLE-USE.md).

## References

- FAO (2016). *Exploring the concept of water tenure*. Land and Water Discussion Paper 10. FAO.
- FAO (2020). *Unpacking water tenure for improved food security and sustainable development*. FAO.
- Hodgson, S., et al. (Eds.) (2024). *Water tenure perspectives: Proceedings of the Water Tenure Mondays
  webinar series*. FAO. https://doi.org/10.4060/cd2941en
- AlAfghani, M. M., & Susetyo, B. (2023). Water tenure security for palm oil, hydropower, and
  geothermal. *IOP Conference Series: Earth and Environmental Science, 1199*, 012016.
- AlAfghani, M. M., Lee, J., & Yasuda, Y. (2025). Potential contribution of the water tenure approach
  to the implementation of international norms applicable to river basins. *Journal of Energy &
  Natural Resources Law*. https://doi.org/10.1080/02646811.2025.2545686
