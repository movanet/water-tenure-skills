# Diagram brief

Mechanism diagrams explain how an arrangement works: who controls a gate, how a permit is issued,
which tenure types sit at one point. They are optional; charts and maps come from `figures.py`.

## Tooling

Any diagram tool that exports a clean PNG will do. The reference pipeline used **Archify**
(https://github.com/tt-a1i/archify, MIT, a third-party Agent Skill that writes architecture,
workflow and data-flow diagrams as standalone HTML with inline SVG and validates them). Install it
following its own instructions; it is not part of this pack. Then:

1. Author each diagram in `<work>/diagrams/<slug>/` following the tool's own workflow and quality
   gate.
2. Export a PNG at 2x or more to `<work>/figures/dia-<slug>.png`, in light theme with no animation:
   `python scripts/export_diagram.py <slug>.html <work>/figures/dia-<slug>.png` (needs Playwright).
3. Insert it in a chapter as `![<caption>](figures/dia-<slug>.png)`; `build.py` numbers it.

## Rules for every diagram

- Every label is a fact from the evidence pack or the catalogue, with its source token kept in the
  diagram's source notes. Do not invent actors, numbers or steps.
- At most 10 to 12 nodes per view; split larger diagrams into views.
- Use the local terms in their original form, with an English gloss.
- Mark the human control points (scope, framework, review and release) visually distinct from the
  AI or automated steps in method diagrams.
- No icons, logos or brand marks of third parties.

## Diagram set used by the reference report

| Slug | Type | What it shows | Source of every label |
|---|---|---|---|
| `methodology-overview` | workflow | Framework, skill, desk sweeps, mechanical gate, spot verification, merge and grade, drafting, checks, human review | The project's run records, checker outputs and verification counts |
| `skill-build` | data flow | How the analytical framework became the skill: inputs, the directions of the person who set the method, the agent's build and test steps, the release | The skill's own history and the build session record |
| `roles` | architecture | Who did what: the human orchestrator, the orchestrating agent, the subagents, tools and data stores; edges directs, executes, reviews, records | The AI-use record (Annex H) |
| `agency-control-chain` | architecture | The chain of control over surface water, from ministry to basin agency to field staff and user groups | The agency-control chapter and pack only |
| `permit-path` | workflow | How a water-use permit is applied for, recommended, decided and counted in allocation; a separate groundwater path where one exists | The permit and licence packs only |
| `layering-point` | architecture | One named point with four or more records of different tenure types around it, each labelled with type, holder and record id | `master_arrangements.csv`: search `location_admin` and `location_hydro` for repeated place names |

For each diagram, record the PNG path, the HTML path, the tool's validation result and one caption
sentence. For `layering-point`, say which place was chosen and why.
