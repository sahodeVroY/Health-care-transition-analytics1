# Care Transition Efficiency & Placement Outcome Analytics

## Overview

**Care Transition Efficiency & Placement Outcome Analytics** is an
analytics project designed to reframe the UAC dataset from a simple
**capacity-monitoring** perspective into a **process-efficiency and
outcome-evaluation** framework.

The UAC Program operates as a multi-stage care and reunification
pipeline rather than simply a healthcare system. The pipeline includes:

**Apprehension & CBP custody → Transfer to HHS care → Medical screening,
sheltering, and case management → Discharge and reunification with a
vetted sponsor**

From a policy and humanitarian perspective, the **speed, continuity, and
reliability** of this pipeline are as important as capacity.

The project analyzes how effectively children move through the pipeline,
identifies delays and bottlenecks, evaluates placement outcomes, and
produces actionable insights for improving reunification timelines and
child welfare outcomes.

------------------------------------------------------------------------

## Problem Statement

Aggregate counts of children in custody are monitored, but
process-efficiency metrics are largely absent.

This project is designed to answer the following questions:

1.  How efficiently are children transferred from **CBP to HHS**?
2.  Are **discharges keeping pace with inflows**?
3.  When and where do **care backlogs accumulate**?
4.  Are **placement outcomes improving or deteriorating over time**?

Without structured transition analytics, important system bottlenecks
can remain hidden.

------------------------------------------------------------------------

## Project Objectives

### Primary Objectives

-   Measure the efficiency of **CBP → HHS transitions**.
-   Evaluate **discharge and sponsor placement outcomes**.
-   Identify **delays and process bottlenecks**.

### Secondary Objectives

-   Support faster reunification.
-   Improve case-management workflows.
-   Inform policy-level process reforms.

------------------------------------------------------------------------

## Dataset

The analysis is based on daily UAC reporting data.

  --------------------------------------------------------------------------------------
  Column                                             Description
  -------------------------------------------------- -----------------------------------
  `Date`                                             Reporting date

  `Children apprehended and placed in CBP custody`   Daily intake volume

  `Children in CBP custody`                          Active CBP care load

  `Children transferred out of CBP custody`          Flow into the HHS system

  `Children in HHS Care`                             Active HHS care load

  `Children discharged from HHS Care`                Successful sponsor placements
  --------------------------------------------------------------------------------------

### Data Interpretation

The dataset represents movement and active loads across the care
pipeline:

``` text
CBP Intake
    ↓
CBP Custody
    ↓
Transfer to HHS
    ↓
HHS Care
    ↓
Discharge / Sponsor Placement
```

The implementation should preserve the distinction between **flows**
(entries, transfers, discharges) and **active loads** (children
currently in CBP custody or HHS care).

------------------------------------------------------------------------

## Analytical Methodology

The analysis should follow the steps below.

### 1. Care Pipeline Modeling

Represent the system as a flow pipeline:

``` text
CBP Custody → HHS Care → Sponsor Placement
```

Track daily movement between these stages and use the available intake,
transfer, custody, HHS-care, and discharge fields to understand pipeline
behavior.

### 2. Transition Efficiency Metrics

Derive process metrics including:

#### Transfer Efficiency Ratio

Measures CBP → HHS transition efficiency.

``` text
Transfer Efficiency Ratio = Transfers ÷ CBP Custody
```

Where:

-   `Transfers` = children transferred out of CBP custody
-   `CBP Custody` = children in CBP custody

#### Discharge Effectiveness

Measures discharge performance relative to the HHS care load.

``` text
Discharge Effectiveness = Discharges ÷ HHS Care
```

Where:

-   `Discharges` = children discharged from HHS care
-   `HHS Care` = children in HHS care

#### Pipeline Throughput Rate

Measures overall movement through the pipeline.

``` text
Pipeline Throughput Rate = Total Exits ÷ Total Entries
```

The implementation should clearly document how `Total Entries` and
`Total Exits` are operationalized from the available dataset fields.

### 3. Backlog & Delay Identification

Analyze:

-   Inflows versus successful exits.
-   Sustained periods where inflows exceed exits.
-   Accumulation of unresolved cases.
-   Locations or periods where process pressure appears to increase,
    where the available data supports such analysis.

### 4. Temporal & Pattern Analysis

Analyze:

-   Weekday versus weekend transition behavior.
-   Month-over-month placement trends.
-   Periods of prolonged stagnation in the pipeline.

### 5. Outcome Stability Analysis

Evaluate:

-   Variability in discharge performance.
-   Consistency of placement outcomes.
-   Sudden drops in reunification success.

------------------------------------------------------------------------

## Key Performance Indicators

The application should calculate and present the following KPIs:

  KPI                                 Purpose
  ----------------------------------- -------------------------------------
  **Transfer Efficiency Ratio**       Measures CBP → HHS transition speed
  **Discharge Effectiveness Index**   Measures placement success
  **Pipeline Throughput**             Measures overall system movement
  **Backlog Accumulation Rate**       Measures delay severity
  **Outcome Stability Score**         Measures consistency of placements

### KPI Implementation Note

The source requirements explicitly define formulas for the **Transfer
Efficiency Ratio**, **Discharge Effectiveness**, and **Pipeline
Throughput Rate**. They describe the remaining KPIs conceptually but do
not provide exact mathematical formulas.

Therefore, the implementation should:

1.  Preserve the required KPI names and intended meanings.
2.  Define transparent formulas for KPIs whose exact formulas are not
    specified.
3.  Document those definitions in the code and research paper.
4.  Avoid presenting an invented formula as an externally mandated
    definition.

------------------------------------------------------------------------

## Streamlit Web Application

The project must include an interactive **Streamlit** web application
for live analytics.

### Core Modules

#### 1. Care Pipeline Flow Visualization

Visualize the movement through:

``` text
CBP Custody → HHS Care → Sponsor Placement
```

The visualization should make pipeline movement and potential
accumulation points easy to understand.

#### 2. Transfer & Discharge Efficiency Panels

Present the key transfer and discharge metrics in clear KPI panels.

At minimum, surface:

-   Transfer Efficiency Ratio
-   Discharge Effectiveness Index
-   Pipeline Throughput
-   Backlog Accumulation Rate
-   Outcome Stability Score

#### 3. Bottleneck Detection Charts

Provide visual analysis of:

-   Inflow versus outflow.
-   Accumulation periods.
-   Delays.
-   Sustained imbalances.

#### 4. Outcome Trend Analysis

Show trends in:

-   Discharges.
-   Placement outcomes.
-   Pipeline performance.
-   Changes over time.

------------------------------------------------------------------------

## User Capabilities

The Streamlit dashboard should allow users to:

### Date Range Selection

Select a reporting period and update the displayed analysis accordingly.

### Ratio-Based Metric Toggles

Allow users to switch ratio-based metrics on or off where appropriate.

### Threshold-Based Visual Alerts

Provide visual alerts when configured analytical thresholds indicate
potential:

-   Backlog accumulation.
-   Reduced transfer efficiency.
-   Reduced discharge performance.
-   Unstable or deteriorating outcomes.

Threshold values should be clearly documented and should not be
presented as official policy thresholds unless such thresholds are
explicitly supplied by the project owner.

------------------------------------------------------------------------

## Suggested Dashboard Flow

The dashboard should prioritize decision-making and move from high-level
status to detailed analysis:

``` text
┌─────────────────────────────────────────────┐
│ Date Range / Metric Controls                │
├─────────────────────────────────────────────┤
│ KPI Summary                                 │
│ Transfer | Discharge | Throughput | ...    │
├─────────────────────────────────────────────┤
│ Care Pipeline Flow                          │
│ CBP → HHS → Sponsor Placement              │
├─────────────────────────────────────────────┤
│ Transfer & Discharge Efficiency             │
├─────────────────────────────────────────────┤
│ Bottleneck / Backlog Analysis               │
├─────────────────────────────────────────────┤
│ Outcome Trends & Stability                  │
└─────────────────────────────────────────────┘
```

The exact UI implementation may vary, but the required analytical
modules and user capabilities should remain available.

------------------------------------------------------------------------

## Research Paper

The project must produce a research paper covering:

### Exploratory Data Analysis (EDA)

Document:

-   Dataset structure.
-   Data quality observations.
-   Trends in custody, transfers, HHS care, and discharges.
-   Relevant temporal patterns.
-   Relationships between pipeline stages.

### Insights

Translate the analysis into findings about:

-   Transition efficiency.
-   Discharge performance.
-   Backlog accumulation.
-   Bottlenecks.
-   Placement trends.
-   Outcome stability.

### Recommendations

Provide evidence-based recommendations aimed at:

-   Reducing delays.
-   Supporting faster reunification.
-   Improving case-management workflows.
-   Strengthening pipeline reliability.
-   Informing policy-level process reforms.

------------------------------------------------------------------------

## Executive Summary

Create a concise executive summary specifically for **government
stakeholders**.

It should focus on:

-   What is happening in the pipeline.
-   Where bottlenecks or delays are occurring.
-   Whether outcomes are improving or deteriorating.
-   Which KPIs require attention.
-   What actions the analysis supports.

The executive summary should prioritize clear findings and actionable
recommendations rather than technical implementation details.

------------------------------------------------------------------------

## Project Deliverables

The final project should contain three major deliverables:

### 1. Research Paper

Includes:

-   EDA
-   Analytical methodology
-   Key findings
-   Insights
-   Recommendations

### 2. Streamlit Dashboard

Provides:

-   Live analytics
-   Interactive care-pipeline visualization
-   KPI monitoring
-   Bottleneck analysis
-   Outcome trend analysis
-   Date-range selection
-   Ratio-based metric controls
-   Threshold-based visual alerts

### 3. Executive Summary

A concise, stakeholder-oriented summary for government decision-makers.

------------------------------------------------------------------------

## Recommended Project Structure

The following structure is recommended so the project remains modular
and easy for Codex to maintain:

``` text
care-transition-analytics/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── src/
│   ├── data/
│   │   ├── load.py
│   │   └── validation.py
│   │
│   ├── analytics/
│   │   ├── pipeline.py
│   │   ├── efficiency.py
│   │   ├── backlog.py
│   │   ├── temporal.py
│   │   └── outcomes.py
│   │
│   └── visualization/
│       └── charts.py
│
├── app/
│   └── streamlit_app.py
│
├── reports/
│   ├── research_paper/
│   └── executive_summary/
│
├── tests/
│
├── requirements.txt
├── README.md
└── .gitignore
```

This is a recommended organization rather than a mandatory folder
structure. The implementation may adapt it to the actual repository and
available tooling.

------------------------------------------------------------------------

## Implementation Principles

### Accuracy First

All metrics must be calculated from the supplied dataset. Do not
fabricate observations, records, locations, outcomes, or trends.

### Reproducibility

The analysis should be reproducible from the raw dataset through the
processing and visualization pipeline.

### Transparent Metrics

Every derived metric should have:

-   A clear name.
-   A documented definition.
-   A documented numerator and denominator where applicable.
-   Appropriate handling for missing or zero denominators.

### Flow vs. Stock Awareness

The implementation must distinguish between:

-   **Flow variables:** intake, transfers, discharges.
-   **Stock variables:** children in CBP custody, children in HHS care.

Avoid blindly treating all fields as interchangeable counts.

### Time-Aware Analysis

Daily data should retain its chronological ordering. Derived analyses
should account for reporting dates and support meaningful weekly/monthly
comparisons.

### Responsible Interpretation

The dashboard and reports should distinguish between:

-   What the data directly shows.
-   What can reasonably be inferred.
-   What requires additional data.

Do not claim individual-level outcomes, causal relationships, geographic
bottlenecks, or exact processing times unless the dataset actually
supports those conclusions.

------------------------------------------------------------------------

## Codex Development Instructions

This project is intended to be developed with **Codex**.

When implementing or modifying the project, Codex should follow these
rules:

1.  **Read the existing repository before changing it.**
2.  **Inspect the actual dataset before implementing analytical
    assumptions.**
3.  Do not invent columns that are not present in the source data.
4.  Keep data loading, metric calculation, visualization, and UI logic
    modular.
5.  Implement calculations in reusable functions rather than duplicating
    formulas throughout the Streamlit app.
6.  Validate data types, especially the reporting date and numeric
    fields.
7.  Handle missing values explicitly.
8.  Protect calculations against division by zero.
9.  Keep metric definitions documented and consistent across the
    dashboard and reports.
10. Use clear, descriptive variable and function names.
11. Add tests for important metric calculations and edge cases.
12. Avoid hard-coding results that should be calculated from the
    dataset.
13. Do not fabricate insights to make charts or reports appear complete.
14. If a requirement is ambiguous, inspect the available data and
    existing project context before making assumptions.
15. Keep the Streamlit interface focused on the analytical questions
    defined in this README.

------------------------------------------------------------------------

## Analytical Questions to Validate Before Completion

Before considering the project complete, verify that the application and
reports can answer:

-   **How efficiently are children transferred from CBP to HHS?**
-   **Are discharges keeping pace with inflows?**
-   **When do backlogs accumulate?**
-   **Where can the available data support identification of
    accumulation?**
-   **Are placement outcomes improving or deteriorating over time?**
-   **Are there sustained periods of pipeline imbalance?**
-   **Are there meaningful weekday/weekend differences?**
-   **What month-over-month placement trends are visible?**
-   **How stable are discharge and placement outcomes?**

If a question cannot be answered reliably from the available dataset,
explicitly state the limitation instead of producing a misleading
result.

------------------------------------------------------------------------

## Definition of Done

The project should be considered complete when:

-   [ ] The dataset is loaded and validated.
-   [ ] The care pipeline is represented as CBP → HHS → Sponsor
    Placement.
-   [ ] Transfer efficiency is calculated.
-   [ ] Discharge effectiveness is calculated.
-   [ ] Pipeline throughput is calculated.
-   [ ] Backlog accumulation is analyzed.
-   [ ] Outcome stability is analyzed.
-   [ ] Temporal patterns are analyzed.
-   [ ] All five required KPIs are presented.
-   [ ] The Streamlit dashboard contains all required core modules.
-   [ ] Date-range selection works.
-   [ ] Ratio-based metric toggles work.
-   [ ] Threshold-based visual alerts are implemented.
-   [ ] Edge cases such as missing values and zero denominators are
    handled.
-   [ ] The research paper contains EDA, insights, and recommendations.
-   [ ] The executive summary is prepared for government stakeholders.
-   [ ] Important analytical functions have tests.
-   [ ] Metric definitions are documented.
-   [ ] No unsupported claims or fabricated data are included.

------------------------------------------------------------------------

## Intended Impact

This project reframes the UAC dataset from a **capacity-monitoring
lens** to a **process-efficiency and outcome-evaluation lens**.

By analyzing how effectively children move through the care pipeline,
the project aims to provide actionable insights for:

-   Improving reunification timelines.
-   Reducing delays and process bottlenecks.
-   Supporting stronger case-management workflows.
-   Improving the reliability of the care-transition pipeline.
-   Strengthening child welfare outcomes.
-   Informing policy-level process reforms.

The central goal is not merely to report **how many children are in the
system**, but to understand **how effectively the system moves children
from one stage to the next and where improvements are needed**.
