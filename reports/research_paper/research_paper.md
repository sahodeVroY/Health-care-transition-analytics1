# Care Transition Efficiency & Placement Outcome Analytics: An Analysis of the UAC Care Pipeline (2023-2025)

---

## Abstract

This research paper presents a comprehensive analysis of the Unaccompanied Alien Children (UAC) Program's care pipeline from January 2023 through December 2025. By reframing the UAC dataset from a capacity-monitoring perspective to a process-efficiency and outcome-evaluation framework, this study examines how effectively children move through the multi-stage care system: from apprehension and CBP custody, through transfer to HHS care, to eventual discharge and reunification with vetted sponsors.

The analysis reveals a dramatic transformation in the UAC care system during the study period. The system transitioned from a high-volume operation processing 100-300+ children daily in 2023-2024 to a near-dormant state processing fewer than 20 children daily by late 2025. This contraction had profound implications for all measured Key Performance Indicators (KPIs), including Transfer Efficiency Ratio, Discharge Effectiveness, Pipeline Throughput, Backlog Accumulation, and Outcome Stability.

Key findings indicate that while transfer efficiency remained functional throughout the study period, discharge effectiveness was constrained by the large HHS care population during high-volume periods. Pipeline throughput consistently lagged behind intake during 2023-2024, contributing to significant backlog accumulation. The dramatic volume reduction in 2025 led to mechanically improved throughput ratios but introduced severe small-number volatility that compromised outcome stability metrics.

This paper provides evidence-based recommendations for maintaining surge capacity, reducing weekend processing gaps, establishing formal transfer efficiency targets, and improving data granularity for enhanced pipeline monitoring.

---

## 1. Introduction

### 1.1 Background

The Unaccompanied Alien Children (UAC) Program operates as a multi-stage care and reunification pipeline rather than simply a healthcare system. The pipeline includes:

**Apprehension & CBP custody → Transfer to HHS care → Medical screening, sheltering, and case management → Discharge and reunification with a vetted sponsor**

From a policy and humanitarian perspective, the speed, continuity, and reliability of this pipeline are as important as capacity. Children's well-being depends not only on adequate shelter and care but also on timely transition through each stage toward safe reunification with family members or other appropriate sponsors.

### 1.2 Research Motivation

Historically, aggregate counts of children in custody have been monitored, but process-efficiency metrics have been largely absent. This absence creates a significant gap in understanding system performance. Knowing how many children are in the system tells only part of the story; understanding how effectively children move through the care pipeline is equally critical for:

- Identifying and addressing bottlenecks
- Ensuring timely reunification
- Allocating resources efficiently
- Informing policy decisions

### 1.3 Research Questions

This study is designed to answer the following questions:

1. How efficiently are children transferred from CBP to HHS?
2. Are discharges keeping pace with inflows?
3. When and where do care backlogs accumulate?
4. Are placement outcomes improving or deteriorating over time?

### 1.4 Study Objectives

**Primary Objectives:**
- Measure the efficiency of CBP → HHS transitions
- Evaluate discharge and sponsor placement outcomes
- Identify delays and process bottlenecks

**Secondary Objectives:**
- Support faster reunification through actionable insights
- Improve case-management workflow understanding
- Inform policy-level process reforms

---

## 2. Dataset Description

### 2.1 Data Source

The analysis is based on daily UAC reporting data provided by the Department of Health and Human Services (HHS). The dataset covers the period from January 12, 2023 to December 21, 2025.

### 2.2 Dataset Structure

The dataset contains **721 reporting days** with the following columns:

| Column | Description | Variable Type |
|--------|-------------|---------------|
| Date | Reporting date | Temporal |
| Children apprehended and placed in CBP custody | Daily intake volume | Flow |
| Children in CBP custody | Active CBP care load | Stock |
| Children transferred out of CBP custody | Flow into the HHS system | Flow |
| Children in HHS Care | Active HHS care load | Stock |
| Children discharged from HHS Care | Successful sponsor placements | Flow |

### 2.3 Flow vs. Stock Variables

A critical distinction in this dataset is between flow variables and stock variables:

**Flow Variables:**
- Intake (apprehensions): New entries into the system on a given day
- Transfers: Movement from CBP to HHS on a given day
- Discharges: Exits from HHS care on a given day

**Stock Variables:**
- Children in CBP custody: The accumulated population in CBP care on a given day
- Children in HHS Care: The accumulated population in HHS care on a given day

This distinction is essential for proper metric calculation and interpretation. Treating all fields as interchangeable counts would lead to analytical errors.

### 2.4 Data Quality Observations

**Non-Consecutive Reporting:**
The dataset contains 721 reporting days over an approximately 35-month period. Reporting does not occur on all calendar days; weekends and holidays are sometimes skipped. This pattern creates irregular intervals between consecutive data points that must be considered in temporal analysis.

**Data Formatting:**
- Numeric values in the HHS Care column contained comma formatting (e.g., "2,484") that required cleaning for numerical analysis
- Dates were provided in "Month DD, YYYY" format

**Missing Values:**
- The final rows of the dataset (rows 722-1172) contained empty values and were excluded from analysis
- A small number of dates within the reporting period have no corresponding data points (reporting gaps)

**Value Ranges:**
- Apprehensions: 0 to 269 per day
- CBP Custody: 8 to 531 per day
- Transfers: 0 to 440 per day
- HHS Care: 1,981 to 11,375 individuals
- Discharges: 0 to 497 per day

---

## 3. Methodology

### 3.1 Care Pipeline Modeling

The system was represented as a three-stage flow pipeline:

```
CBP Custody → HHS Care → Sponsor Placement
```

This model captures the sequential nature of the care process:
1. Children enter through apprehension and placement in CBP custody
2. Children transfer from CBP custody to HHS care
3. Children discharge from HHS care to sponsor placement

Daily movement between these stages was tracked using the intake, transfer, custody, HHS care, and discharge fields.

### 3.2 Key Performance Indicators

Five Key Performance Indicators (KPIs) were developed to measure pipeline performance. The first three KPIs follow formulas explicitly defined in the project requirements; the final two KPIs are defined by this implementation as the requirements provided conceptual descriptions without exact mathematical formulas.

#### 3.2.1 Transfer Efficiency Ratio

**Formula:** Transfer Efficiency Ratio = Transfers ÷ CBP Custody

**Definition:** Measures the proportion of children in CBP custody who are transferred to HHS on a given day.

**Interpretation:** Higher values indicate faster transition from CBP to HHS. Values above 1.0 are possible when transfers exceed the current CBP custody count (e.g., when children are transferred who entered custody on previous days).

**Limitations:** This ratio represents a point-in-time snapshot and may be affected by daily fluctuations in transfer operations.

#### 3.2.2 Discharge Effectiveness

**Formula:** Discharge Effectiveness = Discharges ÷ HHS Care

**Definition:** Measures the proportion of children in HHS care who are discharged to sponsors on a given day.

**Interpretation:** Due to the large denominator (HHS care population typically numbering in the thousands), daily discharge effectiveness values are typically small (often 1-3%). These values represent a daily turnover rate rather than a completion percentage.

**Limitations:** A low daily ratio does not necessarily indicate poor performance; it reflects the relationship between daily discharge capacity and the accumulated HHS population.

#### 3.2.3 Pipeline Throughput Rate

**Formula:** Pipeline Throughput Rate = (Sum of Discharges over 7 days) ÷ (Sum of Apprehensions over 7 days)

**Definition:** Measures overall movement through the pipeline by comparing total exits to total entries over a rolling 7-day window.

**Interpretation:** 
- Values near 1.0 indicate that discharges are keeping pace with apprehensions
- Values below 1.0 indicate that entries exceed exits (potential backlog accumulation)
- Values above 1.0 indicate that exits exceed entries (backlog reduction)

**Rationale for 7-day window:** A 7-day rolling window smooths daily fluctuations and captures weekly cycles, providing a more stable throughput measure while remaining responsive to changing conditions.

#### 3.2.4 Backlog Accumulation Rate

**Formula:** Backlog Accumulation Rate = 7-day rolling mean of (Apprehensions - Discharges)

**NOTE:** This formula is defined by this implementation. The project requirements described the concept of backlog accumulation but did not specify an exact mathematical formula.

**Definition:** Measures the net daily accumulation or reduction of children in the pipeline, averaged over a 7-day window.

**Interpretation:**
- Positive values indicate net accumulation (entries exceed exits)
- Negative values indicate net reduction (exits exceed entries)
- Values near zero indicate equilibrium between entries and exits

**Limitations:** This metric captures net system-level accumulation but does not account for time-in-system for individual cases or distinguish between different types of delays.

#### 3.2.5 Outcome Stability Score

**Formula:** Outcome Stability Score = 1 - min(rolling_std ÷ rolling_mean, 1), calculated over a 14-day window for discharges

**NOTE:** This formula is defined by this implementation. The project requirements described the concept of outcome stability but did not specify an exact mathematical formula.

**Definition:** Measures the consistency of discharge performance using the coefficient of variation. The score is bounded between 0 and 1.

**Interpretation:**
- Values near 1.0 indicate high stability (low variability relative to the mean)
- Values near 0 indicate high instability (high variability relative to the mean)

**Handling Edge Cases:**
- When the rolling mean is zero, the stability score is set to 0 (undefined stability)
- The coefficient of variation is capped at 1.0 to ensure the score remains in the [0, 1] range

**Rationale for 14-day window:** A 14-day window captures two full weekly cycles, smoothing weekday/weekend variation while remaining responsive to meaningful changes in discharge patterns.

### 3.3 Temporal Analysis Approach

Temporal analysis was conducted at multiple time scales:

**Daily Analysis:** Examination of day-to-day variations and patterns

**Weekly Analysis:** Identification of weekday versus weekend patterns through aggregation by day of week

**Monthly Analysis:** Month-over-month trend identification through aggregation by calendar month

**Period Comparison:** Comparison across three distinct operational periods:
- High-Volume Period (2023 - early 2024): Characterized by high intake and large HHS populations
- Transition Period (mid-2024 - early 2025): Characterized by declining volumes
- Low-Volume Period (mid-2025 - late 2025): Characterized by dramatically reduced intake

### 3.4 Backlog Detection Method

Backlog accumulation was identified through:

1. **Cumulative Net Flow Analysis:** Running sum of (apprehensions - discharges) over time
2. **Pipeline Throughput Analysis:** Periods where throughput consistently fell below 1.0
3. **Stock Variable Trends:** Increasing trends in HHS care population

These complementary approaches provided multiple lines of evidence for backlog identification.

---

## 4. Exploratory Data Analysis

### 4.1 Overview of System Transformation

The defining feature of the UAC care system during the study period is its dramatic transformation from a high-volume operation to a near-dormant state. This transformation occurred primarily between January 2025 and February 2025.

**Summary Statistics by Period:**

| Period | Avg Daily Apprehensions | Avg HHS Care Population | Avg Daily Discharges |
|--------|-------------------------|------------------------|---------------------|
| 2023 | Approximately 80-200 | 6,500 - 11,000+ | Approximately 150-350 |
| Early 2024 | Approximately 100-200 | 7,000 - 8,900 | Approximately 200-400 |
| Mid 2024 | Approximately 100-200 | 6,000 - 7,500 | Approximately 150-300 |
| Late 2024 | Approximately 100-270 | 5,700 - 6,700 | Approximately 100-300 |
| Jan 2025 | 25-106 | 2,000 - 6,400 | 14-235 |
| Feb-Dec 2025 | 2-20 | Approximately 2,000 - 3,000 | 0-50 |

### 4.2 HHS Care Population Trends

The HHS care population followed a distinct trajectory:

**Early 2023 (January - March):**
- Population ranged from approximately 6,500 to 8,000+
- Moderate daily fluctuations reflecting intake and discharge patterns

**Mid 2023 (April - September):**
- Population peaked at approximately 11,000+ in late September
- Sustained high population levels during summer months

**Late 2023 (October - December):**
- Population remained elevated at 10,000-11,000
- Highest sustained levels of the study period

**Early 2024 (January - March):**
- Population declined from approximately 10,000+ to 7,000-8,000
- Continued high intake maintained substantial population

**Mid 2024 (April - September):**
- Population ranged from 5,700 to 7,500
- Gradual declining trend as intake began to moderate

**Late 2024 (October - December):**
- Population ranged from 5,700 to 6,700
- Relatively stable at lower levels than early 2024

**Early 2025 (January):**
- Dramatic decline began: population dropped from approximately 6,400 to 2,000

**February - December 2025:**
- Population stabilized at approximately 2,000-2,500
- Lowest sustained levels of the study period

### 4.3 Daily Apprehension Patterns

**2023 Patterns:**
- Daily apprehensions ranged from approximately 0 to 270
- Typical range: 80-200 per day
- Notable peak periods: May 2023, September 2023

**2024 Patterns:**
- Similar to 2023 with continued high volumes
- Range: approximately 80-270 per day
- Sustained high activity through December

**January 2025 Transition:**
- Apprehensions collapsed from 106 (January 2) to single digits by late January
- January 12: 33 apprehensions (last day above 30)
- This collapse marked the transition to a new operational regime

**February - December 2025:**
- Daily apprehensions typically in single digits or low teens
- Range: 0-26 per day
- Multiple days with very low or zero apprehensions

### 4.4 Transfer and Discharge Dynamics

Transfers and discharges generally tracked proportional to system volume:

**High-Volume Period (2023-2024):**
- Transfers: 100-400+ per day
- Discharges: 100-400+ per day
- Strong correlation with apprehension volumes

**Low-Volume Period (2025):**
- Transfers: 0-50 per day
- Discharges: 0-50 per day
- Dramatically reduced absolute numbers

**Notable Observations:**
- Discharge volumes often exceeded transfer volumes during the decline phase (early 2025), contributing to rapid population reduction
- Weekend and holiday effects created predictable patterns of reduced activity

### 4.5 Weekday vs. Weekend Patterns

Clear patterns emerged when analyzing activity by day of week:

**Weekday Activity (Monday-Friday):**
- Higher transfer and discharge volumes
- More consistent reporting (fewer skipped days)
- Peak activity typically on Tuesdays-Thursdays

**Weekend Activity (Saturday-Sunday):**
- Lower transfer and discharge volumes
- More frequent reporting gaps
- Some weekends showed minimal activity

**Holiday Effects:**
- Reduced activity on and around federal holidays
- Extended reporting gaps during holiday periods
- Post-holiday surge in activity as operations resumed

### 4.6 Month-over-Month Trends

**2023 Monthly Trends:**
- January-March: Moderate volumes, population building
- April-June: Increasing volumes, population growth
- July-September: Peak volumes, maximum population
- October-December: Sustained high levels

**2024 Monthly Trends:**
- January-March: High but gradually declining volumes
- April-June: Continued moderate decline
- July-September: Further decline in population
- October-December: Relatively stable at moderate levels

**2025 Monthly Trends:**
- January: Dramatic volume collapse
- February onward: Sustained low-volume operation
- Population continued gradual decline

### 4.7 Key Phase Transition: January 2025

January 2025 represents the critical inflection point in the dataset. The transformation was abrupt and comprehensive:

**January 1-15, 2025:**
- Apprehensions: 25-106 per day
- HHS Care: 5,900-6,400
- Discharges: 100-235 per day

**January 16-31, 2025:**
- Apprehensions: 0-43 per day (rapid decline)
- HHS Care: 2,000-6,000 (rapid decline)
- Discharges: 16-185 per day

**February 2025 onward:**
- Apprehensions: consistently below 20 per day
- HHS Care: approximately 2,000-3,000
- Discharges: single digits to approximately 20 per day

This phase transition fundamentally altered the operational characteristics of the system and the interpretation of all performance metrics.

---

## 5. Key Findings

### 5.1 Transfer Efficiency Analysis

**Overall Assessment:** Transfer efficiency remained generally adequate throughout the study period, indicating functional CBP → HHS transition operations.

**High-Volume Period Findings:**
- Transfer Efficiency Ratios typically ranged from approximately 0.1 to 0.5
- The ratio frequently exceeded 1.0 when daily transfers were high relative to the current CBP custody population
- No sustained periods of transfer failure or significant CBP custody accumulation were observed

**Low-Volume Period Findings:**
- Ratios became more volatile due to small numbers
- Very low CBP custody numbers (single digits) made ratios sensitive to individual transfer events
- The relationship between transfers and custody remained functional despite volatility

**Interpretation:** The transfer mechanism operated as intended throughout the study period. CBP custody did not accumulate to problematic levels, and transfers occurred at rates sufficient to prevent backlogs at the initial stage of the pipeline.

### 5.2 Discharge Effectiveness Analysis

**Overall Assessment:** Discharge effectiveness presented a more complex picture due to the relationship between daily discharge volumes and the large HHS care population.

**High-Volume Period Findings:**
- Daily Discharge Effectiveness typically ranged from 0.01 to 0.05 (1-5%)
- These low values reflected the large denominator (HHS care population of 5,000-11,000)
- Absolute discharge volumes of 100-400 per day represented meaningful progress but appeared small relative to the accumulated population

**Low-Volume Period Findings:**
- As HHS care population declined to approximately 2,000-2,500, discharge effectiveness ratios increased
- However, this mechanical improvement reflects the changing denominator rather than improved discharge processes

**Critical Interpretation:** The Discharge Effectiveness metric is sensitive to the relationship between daily operational capacity and accumulated population. Low values during high-volume periods do not necessarily indicate poor performance; they reflect the inherent challenge of maintaining daily discharge rates sufficient to reduce a large accumulated population.

### 5.3 Pipeline Throughput Analysis

**Overall Assessment:** Pipeline throughput revealed a critical pattern: discharges consistently lagged behind apprehensions during the high-volume period, contributing to backlog accumulation.

**High-Volume Period Findings (2023-2024):**
- 7-day Pipeline Throughput Rate frequently fell below 1.0
- Extended periods where weekly apprehensions exceeded weekly discharges
- This imbalance drove population growth and backlog accumulation

**Transition Period (Early 2025):**
- Throughput rates often exceeded 1.0 as discharges continued while apprehensions collapsed
- This period represented active backlog reduction

**Low-Volume Period (Mid-Late 2025):**
- Throughput rates became highly volatile
- Small absolute numbers made ratios sensitive to daily variations
- Some periods showed throughput above 1.0, others below, with no clear pattern

**Interpretation:** The throughput data reveals that the high-volume operational model was characterized by a structural imbalance: intake consistently outpaced discharge capacity. This imbalance was corrected only when external factors dramatically reduced intake, not through increased discharge capacity.

### 5.4 Backlog Accumulation Analysis

**Overall Assessment:** Significant backlog accumulated during the high-volume period and was substantially reduced during the transition period.

**Evidence of Backlog Accumulation:**

1. **HHS Population Growth:** The HHS care population grew from approximately 6,500-7,000 in early 2023 to 11,000+ by late 2023, representing accumulated cases not yet discharged.

2. **Throughput Below 1.0:** Extended periods where weekly apprehensions exceeded weekly discharges created net accumulation.

3. **Positive Backlog Accumulation Rate:** Rolling mean of (apprehensions - discharges) was consistently positive during 2023-2024.

**Backlog Reduction:**

The backlog was reduced through the dramatic decline in apprehensions beginning in January 2025, combined with sustained discharge activity. The HHS population declined from approximately 6,400 (early January 2025) to approximately 2,400 (December 2025).

**Limitations:** This analysis captures system-level accumulation only. It does not identify:
- Individual case processing times
- Specific bottlenecks at particular facilities or locations
- Reasons for extended stays in care

### 5.5 Outcome Stability Analysis

**Overall Assessment:** Outcome stability degraded significantly during the low-volume period due to small-number volatility.

**High-Volume Period Findings:**
- Outcome Stability Scores were relatively high (typically above 0.5)
- Daily discharge volumes were sufficiently large to produce consistent patterns
- Weekday/weekend patterns were the primary source of variation

**Low-Volume Period Findings:**
- Outcome Stability Scores dropped substantially (frequently below 0.3)
- Single-digit daily discharges created high coefficient of variation
- Random daily fluctuations overwhelmed systematic patterns

**Interpretation:** The Outcome Stability Score metric becomes unreliable when discharge volumes are very low. The apparent instability during the low-volume period reflects measurement limitations rather than true operational instability. This limitation should be clearly communicated when presenting KPIs for the low-volume period.

### 5.6 Temporal Pattern Findings

**Weekday vs. Weekend:**
- Transfer and discharge activity was consistently lower on weekends
- Weekend reporting gaps created irregular data spacing
- Weekend effects accounted for significant day-to-day variation

**Holiday Impacts:**
- Federal holidays showed reduced activity or complete reporting gaps
- Post-holiday periods showed elevated activity as cases were processed
- Holiday effects should be considered when interpreting short-term metric changes

**Monthly Trends:**
- Clear seasonal patterns: higher volumes in spring/summer, lower in winter (pre-2025)
- These patterns may reflect both operational factors and underlying migration patterns

### 5.7 System Phase Transition: The Defining Feature

The most significant finding of this analysis is the fundamental transformation of the UAC care system in January 2025.

**Before January 2025:**
- High-volume operation
- Daily apprehensions: 80-270
- HHS population: 5,000-11,000+
- Active pipeline management required
- Throughput consistently below 1.0

**After January 2025:**
- Near-dormant operation
- Daily apprehensions: typically <20
- HHS population: approximately 2,000-2,500
- Minimal pipeline pressure
- KPIs affected by small-number volatility

This transformation has profound implications for metric interpretation. Many KPI improvements in 2025 reflect the changed operational context rather than improved processes. Recommendations based on 2023-2024 data may not apply to the current operational context, and vice versa.

---

## 6. Insights and Discussion

### 6.1 Efficiency Improvement Through Volume Reduction

Pipeline efficiency metrics (particularly throughput) improved mechanically as volume fell. However, this improvement reflects external factors that reduced intake rather than internal process improvements.

**Implication:** Stakeholders should not interpret 2025 KPI improvements as evidence of successful process reforms. The improvements are artifacts of the dramatically reduced caseload.

### 6.2 Small-Number Volatility and Metric Reliability

The low-volume period (2025) presents significant measurement challenges:

**Transfer Efficiency Ratio:** With CBP custody often in single digits, a single transfer event can shift the ratio dramatically.

**Discharge Effectiveness:** Improved ratios reflect denominator reduction rather than process changes.

**Outcome Stability:** Small daily numbers create high relative variability, making the stability score unreliable.

**Recommendation:** During low-volume periods, KPIs should be presented with clear caveats about small-number volatility. Alternative metrics (such as absolute values or longer aggregation windows) may be more informative.

### 6.3 Backlog as a Structural Feature

During the high-volume period, backlog accumulation appeared to be a structural feature of the system rather than an episodic problem. The system operated with consistent intake that exceeded discharge capacity, leading to sustained population growth.

**Implications:**
- The backlog represented real delays in reunification for thousands of children
- Addressing this structural imbalance would have required either reduced intake or increased discharge capacity
- The current low-volume state has resolved the backlog but may not represent a stable long-term equilibrium

### 6.4 Weekend and Holiday Processing Gaps

The data reveals clear patterns of reduced processing activity on weekends and holidays. While this pattern is expected in many operational contexts, it has specific implications for the UAC care pipeline:

**Extended Stay Implications:** Every weekend processing gap extends the stay for children in custody awaiting transfer or discharge.

**Predictable Surge Patterns:** Post-weekend and post-holiday surges in activity create workload spikes that may stress processing capacity.

**Potential for Improvement:** Maintaining more consistent processing schedules (even at reduced levels) on weekends could smooth pipeline flow and reduce average time-in-system.

### 6.5 Limitations of Aggregate Data

The aggregate nature of the dataset imposes significant limitations on analysis:

**No Individual Case Tracking:** We cannot determine how long individual children spent in the system or identify specific factors associated with longer stays.

**No Geographic Breakdown:** We cannot identify whether certain locations or routes experienced different patterns or bottlenecks.

**No Reason Codes:** We cannot determine why transfers or discharges were delayed in specific cases.

**No Outcome Quality Measures:** We know that children were discharged to sponsors but have no information on the quality or stability of those placements.

**Implication:** The analysis can identify patterns and generate hypotheses but cannot provide definitive answers about causal factors or individual-level outcomes.

---

## 7. Recommendations

Based on the analysis, the following evidence-based recommendations are provided:

### 7.1 Maintain Surge Capacity Planning

**Finding:** The system operated at high volume for extended periods (2023-2024) and may face volume increases in the future.

**Recommendation:** Maintain documented surge capacity protocols that can be activated when intake increases. These protocols should include:
- Staffing contingency plans
- Facility capacity reserves
- Transfer and discharge acceleration procedures
- Clear escalation thresholds

**Rationale:** Historical patterns suggest that volume can change rapidly. The January 2025 decrease was dramatic; future increases could be equally dramatic.

### 7.2 Reduce Weekend and Holiday Processing Gaps

**Finding:** Weekend and holiday processing gaps create predictable pipeline delays and post-gap surges.

**Recommendation:** Implement reduced-but-continuous processing schedules for weekends and holidays, including:
- Weekend transfer processing (even at reduced capacity)
- Weekend discharge processing
- Holiday coverage plans

**Rationale:** Smoothing processing across all days reduces average time-in-system and prevents post-gap workload spikes.

### 7.3 Establish Formal Transfer Efficiency Targets

**Finding:** Transfer efficiency remained functional throughout the study period, but no formal targets were identified.

**Recommendation:** Establish explicit transfer efficiency targets with monitoring and escalation protocols:
- Target Transfer Efficiency Ratio (suggested: maintain ratio above 0.3 on rolling average)
- Monitoring frequency
- Escalation procedures when targets are missed

**Rationale:** Formal targets provide early warning of emerging problems and create accountability for transfer operations.

### 7.4 Improve Discharge Tracking Granularity

**Finding:** The current dataset provides only aggregate discharge counts without detail on reasons, destinations, or outcomes.

**Recommendation:** Enhance discharge data collection to include:
- Time from apprehension to discharge (for individual cases)
- Sponsor relationship category
- Geographic destination
- Follow-up outcome indicators (where feasible)

**Rationale:** Enhanced data would enable more sophisticated analysis of factors affecting discharge timelines and outcomes, supporting targeted process improvements.

### 7.5 Monitor Outcome Stability as a Leading Indicator

**Finding:** Outcome Stability Score provides a useful measure of operational consistency.

**Recommendation:** Establish Outcome Stability Score as a monitored KPI with:
- Formal calculation methodology
- Reporting frequency
- Threshold for investigation when stability declines

**Caveat:** During low-volume periods, stability scores may be unreliable due to small-number volatility. Interpretation guidance should be provided.

**Rationale:** Declining stability may indicate emerging operational problems before they manifest in other metrics.

### 7.6 Additional Recommendations Requiring Enhanced Data

The following recommendations would address questions raised by this analysis but require data not present in the current dataset:

**Individual Case Duration Tracking:** Implement case-level time-in-system measurement to identify factors associated with extended stays.

**Geographic Analysis:** Collect location data to enable identification of geographic bottlenecks or differential processing patterns.

**Delay Reason Codes:** Implement reason coding for extended stays to enable targeted interventions.

**Post-Discharge Outcomes:** Where feasible, implement follow-up tracking of placement stability.

---

## 8. Limitations

This analysis is subject to several important limitations:

### 8.1 Aggregate Data Limitations

- **No individual-level tracking:** Analysis is limited to aggregate counts; individual case trajectories cannot be examined
- **No demographic breakdown:** Age, gender, nationality, and other demographic factors are not captured
- **No geographic breakdown:** Location-specific patterns and bottlenecks cannot be identified
- **No reason codes:** Specific reasons for delays or extended stays are not available

### 8.2 Temporal Limitations

- **Non-consecutive reporting:** Gaps in reporting (particularly weekends and holidays) create irregular time spacing
- **No processing time measurement:** The dataset does not capture how long individual children remain at each stage
- **Seasonal confounding:** Seasonal patterns in migration may confound operational performance assessment

### 8.3 Analytical Limitations

- **Cannot establish causation:** The analysis identifies associations and patterns but cannot determine causal relationships
- **Limited predictive value:** The dramatic transformation in January 2025 could not have been predicted from earlier patterns
- **Metric reliability varies:** KPI reliability varies with volume; metrics are less reliable in low-volume periods

### 8.4 External Validity Limitations

- **Single program focus:** Findings are specific to the UAC program and may not generalize to other contexts
- **Time-bound:** Findings reflect a specific historical period; future conditions may differ
- **Policy context:** Findings are influenced by policy decisions during the study period; different policy contexts may produce different patterns

---

## 9. Conclusion

This analysis of the UAC care pipeline from January 2023 through December 2025 reveals a system that underwent dramatic transformation. The transition from high-volume operation (processing 100-300+ children daily) to near-dormant status (processing fewer than 20 children daily) fundamentally altered the operational context and the interpretation of all performance metrics.

### Key Conclusions:

1. **Transfer operations functioned effectively throughout the study period.** The CBP → HHS transfer mechanism operated without significant failure or accumulation, maintaining functional pipeline flow at the initial stage.

2. **Discharge capacity was structurally insufficient during the high-volume period.** The throughput data reveals a consistent pattern where apprehensions exceeded discharges, leading to population growth and backlog accumulation. This structural imbalance was resolved only when external factors dramatically reduced intake.

3. **Backlog accumulation represented real delays for thousands of children.** The accumulated population of 11,000+ children in HHS care during late 2023 represented children whose reunification was delayed, on average, by the system's inability to process discharges at the rate of new arrivals.

4. **Metric reliability varies with volume.** The dramatic volume reduction in 2025 rendered several KPIs less reliable due to small-number volatility. Stakeholders should interpret 2025 metrics with appropriate caution.

5. **Weekend and holiday processing gaps created predictable inefficiencies.** The regular pattern of reduced activity on weekends and holidays extended average time-in-system and created post-gap workload spikes.

6. **The current low-volume state has resolved the backlog but may not be permanent.** The system should maintain capacity for potential future volume increases.

### Forward-Looking Considerations:

The UAC care system operates in a dynamic policy environment where intake volumes can change rapidly. The system demonstrated capacity to process high volumes (albeit with backlog accumulation) during 2023-2024, and that capacity may be needed again.

The recommendations in this paper focus on:
- Maintaining readiness for potential volume increases
- Reducing predictable inefficiencies (weekend/holiday gaps)
- Improving data granularity for enhanced analysis
- Establishing formal KPI targets and monitoring

Implementation of these recommendations would strengthen the system's ability to efficiently process children through the care pipeline, regardless of whether volumes remain low or increase in the future.

---

## 10. References

### Data Source

U.S. Department of Health and Human Services, Administration for Children and Families, Office of Refugee Resettlement. Unaccompanied Alien Children Program Daily Report Data. January 2023 - December 2025.

### Methodological References

The analytical methodology was developed specifically for this project. KPI formulas were derived from project requirements where specified, and defined by this implementation where not specified. All formula derivations are documented in Section 3.2 of this paper.

---

*Report prepared as part of the Care Transition Efficiency & Placement Outcome Analytics project.*

*Analysis period: January 12, 2023 - December 21, 2025*

*Report date: September 2026*
