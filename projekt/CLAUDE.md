# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

University seminar project for "Zpracování velkých dat" (Big Data Processing) course at PEF ČZU. Team of 3 students building a data product for a fictional/real company covering the full data lifecycle — from data sources through EDA to visualization and recommendations.

**Language:** Czech (all documentation, comments, and outputs must be in Czech).

## Deliverables

- **HTML companion document** (sections: company intro & KPIs, technical architecture, data strategy & governance, EDA & visualizations (min. 6 charts), conclusions, methodology)
- **Jupyter notebook** with EDA linked to KPIs (template: `data-and-info/eda-template-jupyter-notebook.txt`)
- **Raw data** source files
- **DuckDB database** (`.duckdb` file with prepared tables)
- **PowerPoint presentation** (10–12 min + 5 min discussion)

## Tech Stack

- **Python 3.11+** in Jupyter notebooks
- **DuckDB** — primary analytical database (connect via `duckdb.connect("projekt.duckdb")`)
- **pandas** — data manipulation
- **matplotlib** — visualization
- Standard package bootstrapping pattern: `ensure_package()` function auto-installs missing packages

## EDA Notebook Structure

The EDA notebook follows a fixed template (sections 1–8):
1. Pravidla práce (rules — do not modify)
2. Kontext analýzy (analysis context, KPIs, business questions)
3. Načtení dat a technická příprava (data loading, DuckDB connection)
4. Přehled dat a zdrojů (table overview, schemas, relationships)
5. První orientace v datech (shape, dtypes, granularity, time range)
6. Kvalita dat a omezení (missing values, duplicates, validation)
7. Explore and Visualize (flexible subsections 7.1–7.4: key variables, segments, time analysis, relationships)
8. Závěry a vazba na KPI (conclusions tied to KPIs)

**Section 7 is intentionally flexible** — adapt subsections to fit the data and analytical goals rather than following the template mechanically.

## Key Conventions

- Every analysis step must link back to project goals, KPIs, or analytical questions
- Every output (chart, table) needs a brief interpretation — what it shows and what it cannot claim
- Data quality issues and limitations must be stated explicitly
- Conclusions must distinguish between supported findings, interpretations, and hypotheses
- All code comments should be in Czech and explain each line

## Reference Materials

Course exercise PDFs and prompts are in `data-and-info/`. The file `big-data-projekt-prompts.md` contains structured prompts for different project phases (KPI design, Python tutoring, EDA review, brainstorming).
