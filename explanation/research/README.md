# Research directory

Research records for Part I, the 4-bit Carry Look-Ahead adder. Original papers are in `../ref/papers/` and previous submissions in `../ref/submission_ref/`; neither is modified.

| File | Contents |
|---|---|
| `research_log.md` | Dated, factual log of what was examined, measured and decided. Append only. |
| `literature_review.md` | What each provided paper does, what can be used and its limits, plus external references. |
| `paper_comparison.md` | Side-by-side table of the provided papers' reported numbers and conditions. |
| `submission_reference_analysis.md` | What the three earlier submissions did well and badly. |
| `design_decisions.md` | Each decision with alternatives, reasoning, evidence and status. |

Reading order: this file, `design_decisions.md`, `literature_review.md`, `paper_comparison.md`, `submission_reference_analysis.md`, `research_log.md`. Then `../part1/planning/`.

## Maintaining these files

- Add entries to `research_log.md` with the date; correct errors by adding a dated correction, not by rewriting.
- Label claims as one of: **Literature** (a source states it), **Estimate** (calculated, not simulated), **Measured** (our ngspice or MAGIC output, with file path).
- Cite provided papers by file number and PDF page, such as `[33, p.2]`. Cite external sources with authors, title, venue, year and DOI or URL, and state how much of the source was read.
- Do not record a number without a file that produced it or a source that states it.
- A decision goes in `design_decisions.md` only with its alternatives and evidence. Update its status when simulation confirms or overturns it.
