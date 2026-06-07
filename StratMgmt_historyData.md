# Example
# FICC Cross-Asset Strategic Trade Management Platform

## Historical Data Store — Business Case & Architecture Decision Record

-----

|Field                      |Value                                                                                  |
|---------------------------|---------------------------------------------------------------------------------------|
|**Document Classification**|Internal — Architecture Review Board                                                   |
|**Document Type**          |Architecture Decision Record (ADR) / Business Case                                     |
|**Audience**               |CTO, CDO, Head of FICC Technology, Architecture Review Board, Finance & Risk Technology|
|**Companion Document**     |Document 2 — HDS Specialist Panel Review Framework                                     |
|**Status**                 |DRAFT — Awaiting ARB Review                                                            |

-----

## 1. Executive Summary

The FICC Strategic Trade Management Platform (STMP) has designated GridGain as the in-memory data fabric for all intraday and near-real-time needs: event storage, trade snapshot serving, and live position queries. This is an appropriate and well-scoped decision for latency-sensitive workloads.

However, a class of mission-critical workloads exists that GridGain is architecturally mismatched to serve. These include regulatory stress-testing datasets (CCAR, FRTB), historical blotter subscriptions spanning months of activity, Finance sub-ledger reconciliation queries, and large-scale trade population analysis. Serving these workloads from GridGain would require memory overprovisioning at prohibitive cost, introduce cluster instability risk, and yield inferior query performance compared to purpose-built analytical stores.

> **ARCHITECTURAL PRINCIPLE:** The correct architecture is a tiered data strategy. GridGain owns the hot tier (intraday, millisecond-latency, active trades). A dedicated Historical Data Store owns the warm and cold tiers (days to years, analytical workloads, regulatory submissions). These tiers are complementary, not competitive.

This document makes the case for the Historical Data Store, defines its required capabilities through concrete business scenarios, quantifies the risk of not having it, and establishes the evaluation framework for technology selection.

-----

## 2. Architectural Context: The Two-Tier Data Strategy

### 2.1 GridGain’s Role and Scope

GridGain (Apache Ignite) is an in-memory computing platform optimized for:

- Sub-millisecond read/write latency for active trade state
- Distributed caching with co-located compute for position calculations
- Event streaming with durable write-ahead log for intraday trade events
- Serving live blotter queries for active positions on the trading floor

GridGain’s design constraints make it the wrong tool for historical analytical workloads:

- RAM-resident storage is cost-prohibitive at the multi-year, multi-billion-event scale required for CCAR and regulatory history
- GridGain is not optimized for column-scan analytics on large datasets; it is row/key-value optimized
- Long-running analytical queries compete with latency-sensitive intraday operations, risking grid instability
- GridGain does not natively support bitemporal querying (valid time vs. transaction time) at the query layer
- Native SQL in Ignite lacks the optimizer maturity of purpose-built analytical databases for complex multi-join regulatory queries

### 2.2 The Historical Data Store’s Role

The Historical Data Store (HDS) is the persistence and analytical tier for all trade and position data beyond the intraday horizon. It is the system of record for time-series trade history, and the compute substrate for all heavy analytical workloads. The boundary between GridGain and the HDS is defined as follows:

|Dimension            |GridGain (Hot Tier)                                |Historical Data Store (Warm/Cold Tier)            |
|---------------------|---------------------------------------------------|--------------------------------------------------|
|Time horizon         |Current trading day + rolling window (e.g., 5 days)|Days to 7+ years                                  |
|Latency requirement  |Sub-millisecond to low-millisecond                 |Seconds to minutes acceptable                     |
|Query pattern        |Point lookups, key-based, small result sets        |Full-scans, aggregations, joins, large result sets|
|Data volume per query|Single trade / small position sets                 |Millions to billions of records                   |
|Storage economics    |RAM — expensive per GB                             |Disk/object store — commodity cost                |
|Primary users        |Traders, real-time risk systems                    |Finance, Risk, Compliance, Audit, Regulatory      |
|Concurrency model    |High-frequency short transactions                  |Long-running analytical batch jobs                |
|Bitemporal support   |Limited / not native                               |First-class requirement                           |
|Retention            |Days to weeks                                      |7–10 years (regulatory minimum)                   |

-----

## 3. Business Scenarios Requiring a Dedicated Historical Data Store

The following scenarios are drawn from live operational needs across FICC desks, Finance, Risk, and Regulatory functions. Each scenario is assessed against GridGain’s capabilities to establish the gap.

### 3.1 Scenario 1: Heavy-Duty Historical Blotter Subscriptions

#### 3.1.1 Business Context

Head traders, desk heads, and senior risk managers require blotter views that span not just today’s activity but weeks or months of trade history. This is a core daily workflow in practice:

- A Rates desk head reviewing all IRS trades booked in Q4 to assess year-end positioning
- A Credit trader reviewing all CDS trades on a reference entity over the past six months following a ratings watch event
- A Muni desk reviewing all TOB trades across a fiscal year for tax reporting
- A Regional Head reviewing all APAC-booked FX forwards over a three-month window for capacity planning

#### 3.1.2 Data Characteristics

- Typical query scope: 50,000 to 5,000,000 trade records per query
- Filters: multi-dimensional (desk, product, counterparty, currency, tenor, booking entity, status)
- Joins required: trades to lifecycle events, trades to positions, trades to reference data
- Refresh pattern: subscription-style — user expects results updated as amendments or new trades arrive

#### 3.1.3 GridGain Gap

Loading 2–5 million records from GridGain into a blotter would require the full dataset to be materialized in application memory, bypassing the distributed compute advantage. Query optimizer limitations mean multi-dimensional filter queries over historical partitions cause full-partition scans. A dedicated OLAP store with columnar indexing can serve this query in seconds with predicate pushdown.

> **⚠️ RISK:** Without an HDS, historical blotter queries would require either prohibitive GridGain RAM expansion or a degraded user experience with multi-minute waits — both unacceptable for senior trading floor users.

-----

### 3.2 Scenario 2: Trades Over Months — Lifecycle and Amendment History

#### 3.2.1 Business Context

Middle office, compliance, and audit functions routinely need to reconstruct the complete lifecycle of trades over their multi-month or multi-year existence:

- Full amendment history for a 30-year USD IRS: 47 rate resets, 3 partial terminations, 1 novation over 18 months
- Compliance reconstruction of all lifecycle events for a CDS index position during a credit event determination period
- Operations reconstructing the exact trade state as it was known on a specific business date (bitemporal query)
- Model Risk requesting full re-valuation history for a structured Muni TRS for model validation purposes

#### 3.2.2 The Bitemporal Requirement

This is a first-class architectural requirement. Two independent time axes must be supported:

- **Valid Time (VT):** The business date the event was economically effective
- **Transaction Time (TT):** The system date the event was recorded in the platform

Example query: *“Give me the trade state of trade STMP-IRS-00441 as it was known on Valid Date March 31, 2024, as recorded in the system no later than April 5, 2024.”*

This is standard for regulatory reconstruction and financial statement restatement. GridGain does not support bitemporal querying at the database layer — it would require application-layer reconstruction with full event replay from an event log, which is not scalable for historical depth.

> **📋 REGULATORY REQUIREMENT:** EMIR, Dodd-Frank, and MiFID II all require the ability to reconstruct trade state as of a historical date within defined timeframes (same-day for audit, T+1 for regulatory). A bitemporal store is the implementation mechanism.

-----

### 3.3 Scenario 3: CCAR-Style Large-Scale Regulatory Stress Testing Queries

#### 3.3.1 Business Context

Comprehensive Capital Analysis and Review (CCAR), FRTB IMA, and internal stress testing frameworks require batch analytical processing across the full historical trade population:

- Select all OTC derivative trades with maturity > 1 year, cross every historical market scenario (250+ scenarios), compute PFE profile for each trade, aggregate by counterparty and netting set — for the entire book of 800,000 trades
- Historical VaR backtesting: compute daily P&L for each of the past 250 trading days across the full position set, validate against actual P&L (Model Risk mandate)
- FRTB Sensitivity-Based Method: compute delta, vega, curvature sensitivities for all in-scope instruments across all regulatory risk buckets for regulatory capital submission
- Fed CCAR submission: reconstruct position-level data as of the stress test reference date for each of 9 supervisory scenarios across 13 quarters of projection

#### 3.3.2 Data Volume and Compute Requirements

|Workload                    |Record Scope                  |Typical Runtime Target|Storage Required |
|----------------------------|------------------------------|----------------------|-----------------|
|CCAR position reconstruction|5M trades × 13 quarters       |< 4 hours             |2–5 TB analytical|
|Historical VaR (250d)       |800K positions × 250 scenarios|< 2 hours             |500 GB–1 TB      |
|FRTB SBM sensitivities      |1.2M risk factors             |Overnight batch       |800 GB+          |
|PFE Monte Carlo (10K paths) |200K netting sets             |< 6 hours             |3–8 TB temp      |
|Backtesting full P&L explain|250 days × 800K positions     |< 3 hours             |1–2 TB           |

#### 3.3.3 GridGain Gap

These workloads require sustained, high-throughput sequential scans across billions of records. GridGain is not designed for sequential column-scan analytics — it will serialize I/O through its row-oriented storage engine, performing 10–50x worse than a columnar store for these access patterns. More critically, running CCAR-scale workloads on the same GridGain cluster that serves intraday trading would create resource contention and latency spikes that are operationally unacceptable on the trading floor.

> **⚠️ RISK:** Executing CCAR/FRTB workloads on GridGain without an HDS would require a separate dedicated GridGain cluster for regulatory workloads — at 5–10x the infrastructure cost of an analytical store — with no performance advantage.

-----

### 3.4 Scenario 4: Finance Sub-Ledger Type Queries

#### 3.4.1 Business Context

Finance and Product Control functions require the trade management platform to serve as a source for accounting entries, P&L attribution, and sub-ledger reconciliation:

- **Month-end close:** Extract all cash flow events, fixing events, and accrual entries for the full book to feed the General Ledger — potentially 2–10 million accounting records per monthly close
- **Daily P&L explain:** Finance requires all P&L attribution factors (delta P&L, gamma P&L, time decay, new activity) by trade and rolled to desk — requires joining trade history, valuation snapshots, and market data across the day
- **IAS 39 / IFRS 9 hedge accounting:** Identify all hedging instruments and hedged items, extract fair value history, compute ineffectiveness — requires scanning multi-year trade history
- **Tax lot accounting:** FIFO/LIFO lot identification for Muni bond positions requires scanning full position history by tax lot inception date
- **Intercompany reconciliation:** Finance needs to reconcile internal mirror trades across entities, matching notionals, rates, and cash flows — requires joining two sides of the trade book

#### 3.4.2 Query Complexity Example — Month-End P&L Reconciliation

A typical month-end P&L reconciliation query for a mid-size desk requires:

1. Join trades to all lifecycle events in the month (potentially 500K events)
1. Join each event to its valuation snapshot (time-series join — find the valuation snapshot closest to each event timestamp)
1. Join to market data reference at event time
1. Aggregate by booking entity, desk, trader, product hierarchy, and P&L type
1. Compare aggregated result to Finance GL balance

This is a classic OLAP workload — columnar storage, vectorized execution, and a mature SQL optimizer are the correct tools. GridGain cannot serve this efficiently.

-----

### 3.5 Scenario 5: Regulatory Audit and Inquiry Response

#### 3.5.1 Business Context

Regulators (CFTC, SEC, FCA, ESMA) submit inquiries that require reconstructing complete trade histories on short notice:

- *“Provide all FX swap trades between your US entity and Counterparty X from January 1 to December 31, including all amendments and their timestamps, the trader who booked each event, and the market data used for valuation at each amendment.”* — Typical SEC inquiry scope
- CFTC large trader position reporting: daily submission of all positions above threshold, with full audit trail of position changes
- EMIR REFIT: reconciliation of all reportable trades against trade repository records, requiring joins across years of trade data

> **🚨 REGULATORY RISK:** Failure to respond to regulatory inquiries within mandated timeframes (typically 5–10 business days) constitutes a reportable compliance breach. The HDS must support same-day data reconstruction for regulatory inquiries with < 5 second response for point-in-time queries and < 30 minutes for large-population historical reconstructions.

-----

### 3.6 Scenario 6: Risk Surveillance and Anomaly Detection on Historical Patterns

Market Surveillance, Compliance, and Risk functions require historical trade data for pattern analysis:

- Detection of wash trading, front-running, or marking patterns requires analyzing sequences of trades by the same trader across weeks or months
- Counterparty concentration analysis: track evolution of exposure to a counterparty or sector over a rolling 12-month window
- Product P&L outlier detection: identify trades whose P&L at booking materially exceeded desk norms over historical periods
- Trader performance analysis and risk-adjusted return attribution over full evaluation periods

-----

## 4. Risk of Not Implementing a Dedicated Historical Data Store

|Risk Category  |Specific Risk                                                    |Likelihood                 |Impact                                        |Mitigation if HDS Exists                      |
|---------------|-----------------------------------------------------------------|---------------------------|----------------------------------------------|----------------------------------------------|
|Regulatory     |Failure to respond to CFTC/SEC inquiry within mandated window    |Medium                     |**CRITICAL** — potential enforcement action   |Same-day reconstruction from bitemporal store |
|Regulatory     |CCAR/FRTB submission delay or data quality failure               |High without HDS           |**HIGH** — capital surcharge, remediation plan|OLAP store serves regulatory batch on schedule|
|Financial      |Month-end P&L reconciliation breaks, delayed close               |High without HDS           |**HIGH** — financial restatement risk         |Finance sub-ledger queries served natively    |
|Operational    |GridGain cluster instability from CCAR workload contention       |High if run on same cluster|**CRITICAL** — intraday trading disruption    |Workload isolation via separate tier          |
|Cost           |GridGain RAM overprovisioning to store 3+ years of history       |Certain without HDS        |**HIGH** — 5–10x storage cost premium         |Commodity storage in analytical store         |
|Audit          |Inability to reconstruct bitemporal trade state for audit        |Medium                     |**HIGH** — audit qualification risk           |Native bitemporal queries in HDS              |
|User Experience|Multi-minute wait for historical blotter queries for senior users|Certain without HDS        |**MEDIUM** — adoption and trust erosion       |Sub-second columnar scan for blotter queries  |

-----

## 5. Functional Requirements for the Historical Data Store

### 5.1 Core Capabilities

|Requirement ID|Requirement                                                                            |Priority     |Source Scenario|
|--------------|---------------------------------------------------------------------------------------|-------------|---------------|
|HDS-001       |Bitemporal data model: valid time + transaction time for all trade and position records|**MUST HAVE**|3.2, 3.5       |
|HDS-002       |Immutable event append — no physical deletes; logical cancellation events only         |**MUST HAVE**|3.2, 3.5       |
|HDS-003       |Full event replay and state reconstruction as of any historical timestamp              |**MUST HAVE**|3.2, 3.5       |
|HDS-004       |Columnar storage for efficient analytical scan queries (CCAR, historical blotter)      |**MUST HAVE**|3.1, 3.3       |
|HDS-005       |SQL query interface with ANSI SQL compliance and optimizer for complex joins           |**MUST HAVE**|3.1, 3.3, 3.4  |
|HDS-006       |Time-series join capability (as-of join, snapshot join) for valuation history          |**MUST HAVE**|3.4            |
|HDS-007       |Support for concurrent heavy analytical workloads without impacting intraday tier      |**MUST HAVE**|3.3            |
|HDS-008       |Data retention of minimum 7 years for all trade events (regulatory minimum)            |**MUST HAVE**|3.5            |
|HDS-009       |Scalability to 10+ billion events without performance degradation                      |**MUST HAVE**|3.3            |
|HDS-010       |Partition pruning and predicate pushdown for efficient subset queries                  |**MUST HAVE**|3.1, 3.3       |
|HDS-011       |Real-time or near-real-time ingestion from GridGain event stream (< 30 second lag)     |**MUST HAVE**|3.1            |
|HDS-012       |Role-based access control at row and column level for data segregation                 |**MUST HAVE**|3.5            |
|HDS-013       |Integration with downstream Finance GL, Risk, and Regulatory Reporting systems         |**MUST HAVE**|3.4, 3.5       |
|HDS-014       |Support for structured (trade economics) and semi-structured (event payloads) data     |SHOULD HAVE  |3.2            |
|HDS-015       |Query federation across HDS and GridGain for hybrid intraday + historical queries      |SHOULD HAVE  |3.1            |
|HDS-016       |Storage cost optimization via tiered storage (hot/warm/cold within HDS)                |SHOULD HAVE  |General        |
|HDS-017       |Native ACID transactions for event ingestion consistency                               |**MUST HAVE**|3.2            |
|HDS-018       |Parallel query execution and workload management / resource governance                 |**MUST HAVE**|3.3            |

-----

## 6. Target Architecture: Two-Tier Data Strategy

### 6.1 Data Flow Design

|Step                     |Description                                                                             |Mechanism                                 |
|-------------------------|----------------------------------------------------------------------------------------|------------------------------------------|
|1 — Event Capture        |All trade events written to GridGain as primary write path                              |Application writes to GridGain WAL + cache|
|2 — Event Streaming      |GridGain CDC stream publishes all events to message bus                                 |Kafka topic per event type                |
|3 — HDS Ingestion        |HDS consumer reads from Kafka, enriches with metadata, writes to append-only event store|Streaming ingest pipeline (< 30s lag)     |
|4 — State Materialization|HDS materializes current and point-in-time trade states from event replay               |HDS internal compaction job               |
|5 — Analytical Serving   |Heavy analytical queries (CCAR, blotter, Finance) route directly to HDS                 |SQL / JDBC / REST API                     |
|6 — Live Serving         |Intraday point-lookup and position queries route to GridGain                            |GridGain SQL / native API                 |
|7 — Federation (Optional)|Queries spanning both tiers federated at query layer                                    |Query router / virtual view               |

### 6.2 Workload Routing Matrix

|Workload                            |Route To|Rationale                                     |
|------------------------------------|--------|----------------------------------------------|
|Live trader blotter (today’s trades)|GridGain|Sub-millisecond latency required              |
|Historical blotter (> 1 day)        |**HDS** |Columnar scan, large result set               |
|Real-time position query            |GridGain|Co-located compute, live aggregation          |
|Historical position reconstruction  |**HDS** |Bitemporal query, multi-month scope           |
|CCAR / FRTB stress testing          |**HDS** |Multi-billion record scans, workload isolation|
|Finance P&L reconciliation          |**HDS** |Complex joins, month-end batch                |
|Regulatory audit reconstruction     |**HDS** |Bitemporal, full event lineage                |
|Intraday fixing / reset processing  |GridGain|Event-driven, millisecond processing          |
|Market surveillance pattern analysis|**HDS** |Multi-month sequential scan                   |
|SoR audit extract                   |**HDS** |Immutable, full lineage required              |

-----

## 7. Technology Evaluation: Exadata vs. S3 + Iceberg + Dremio

Two candidate implementations have been identified. This section provides an objective framing of each. Detailed validation questioning for the S3/Iceberg/Dremio stack is addressed in Document 2.

### 7.1 Candidate A: Oracle Exadata

Oracle Exadata is an engineered system combining compute and high-performance storage (Exadata Smart Flash Cache) with the Oracle Database engine.

|Dimension           |Exadata Strengths                                                                |Exadata Concerns                                                                      |
|--------------------|---------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|
|Query performance   |Smart Scan offload to storage cells for full-table scans; validated at FICC scale|Performance dependent on Exadata-specific optimization; less portable                 |
|SQL capability      |Mature Oracle SQL with advanced analytics, temporal queries, partitioning        |Oracle SQL extensions reduce portability; licensing tied to Oracle ecosystem          |
|Operational maturity|25+ year operational track record in capital markets                             |High operational overhead; DBA-intensive; slower schema evolution                     |
|Bitemporal support  |Oracle Workspace Manager / Flashback for temporal queries                        |Bitemporal available but requires schema design discipline; not native                |
|Cost                |—                                                                                |High — Exadata hardware + Oracle Database EE + Partitioning options; significant CapEx|
|Scalability         |Scale-up model; well-proven at petabyte scale                                    |Scale-up economics less favorable than cloud-native scale-out for burst workloads     |
|Cloud               |Exadata Cloud@Customer available                                                 |OCI ecosystem lock-in; less natural for multi-cloud strategies                        |
|Data format         |Standard export interfaces available                                             |Proprietary Oracle storage format — migration risk                                    |
|Regulatory          |Strong compliance track record; widely accepted by regulators                    |—                                                                                     |

### 7.2 Candidate B: S3 + Apache Iceberg + Dremio

This cloud-native stack combines S3 as the storage layer, Apache Iceberg as the open table format, and Dremio as the SQL query engine with Apache Arrow-based execution.

|Dimension            |S3 + Iceberg + Dremio Strengths                                                 |S3 + Iceberg + Dremio Concerns (for specialist validation)                    |
|---------------------|--------------------------------------------------------------------------------|------------------------------------------------------------------------------|
|Cost                 |Commodity object storage — orders of magnitude cheaper per GB than Exadata flash|Dremio licensing cost; compute cost for heavy concurrent workloads            |
|Scalability          |Virtually unlimited storage scale; compute scales independently                 |Query engine scaling under extreme concurrency needs validation               |
|Openness             |Open table format — no vendor lock-in on storage; portable across engines       |Ecosystem maturity for FICC-specific workloads needs validation               |
|Schema evolution     |Iceberg supports schema and partition evolution without rewrite                 |Complex schema changes at trade event level need testing                      |
|ACID semantics       |Iceberg provides ACID transactions at table level                               |Multi-table ACID across trade + position + event tables needs validation      |
|Bitemporal           |Iceberg time-travel queries natively supported (snapshot-based)                 |Iceberg time-travel is snapshot-based, not true bitemporal — **gap to assess**|
|Query performance    |Dremio Reflections can pre-aggregate common queries                             |Cold query performance without Reflections; complex multi-join CCAR queries   |
|Operational          |Cloud-native, managed services reduce operational overhead                      |Newer operational model; less battle-tested in FICC regulatory contexts       |
|Integration          |Open APIs; Arrow Flight for fast data transfer                                  |Integration with GridGain and legacy systems needs validation                 |
|Regulatory acceptance|Emerging acceptance                                                             |Regulators have less familiarity; needs careful compliance design             |

### 7.3 Evaluation Criteria

|Criterion                                            |Weight|Measurement                                                              |
|-----------------------------------------------------|------|-------------------------------------------------------------------------|
|Bitemporal query capability (native or configurable) |20%   |Can serve ‘as-of VT, TT’ queries without application-layer reconstruction|
|CCAR/FRTB scale query performance                    |20%   |Benchmark: 5M trades × 250 scenarios in < 4 hours                        |
|Total Cost of Ownership (3-year)                     |15%   |Fully loaded cost including DBA, migration, support                      |
|Integration with GridGain event stream               |10%   |Ingestion latency < 30 seconds; validated connector                      |
|SQL query completeness for Finance sub-ledger queries|10%   |TPC-H style benchmark + bank-specific query library                      |
|Data retention and storage economics at 10-year scale|10%   |Cost per TB per year at projected volume                                 |
|Regulatory compliance posture                        |10%   |Audit trail completeness, data immutability guarantees                   |
|Operational maturity and bank-wide skill availability|5%    |Existing team skills, vendor support tier                                |

-----

## 8. Recommendation

> **RECOMMENDATION:** Approve the investment in a dedicated Historical Data Store as a separate tier from GridGain. The business case is established across six distinct scenario categories representing regulatory, financial, operational, and user-experience requirements. Proceeding without an HDS creates material regulatory risk (CCAR/FRTB/audit reconstruction), financial risk (Finance reconciliation), and operational risk (GridGain cluster instability from analytical workload contention).

**Next steps:**

1. Approve this ADR at the Architecture Review Board
1. Initiate the specialist panel evaluation process (see Document 2) for Exadata vs. S3+Iceberg+Dremio
1. Commission a proof-of-concept benchmark using actual FICC trade data for the top 3 query patterns from Section 3
1. Assign a Technology Owner and Product Owner for the HDS program
1. Define the GridGain-to-HDS data pipeline design as the first technical deliverable

The final technology choice between Exadata and S3+Iceberg+Dremio should be made after the specialist panel review and benchmark results, evaluated against the weighted criteria in Section 7.3.

-----

## 9. Glossary

|Term            |Definition                                                                                                              |
|----------------|------------------------------------------------------------------------------------------------------------------------|
|ADR             |Architecture Decision Record — formal documentation of a significant architectural decision                             |
|Bitemporal      |Data model tracking two time axes: valid time (business effective date) and transaction time (system record date)       |
|CCAR            |Comprehensive Capital Analysis and Review — Federal Reserve stress testing framework for large US bank holding companies|
|CDC             |Change Data Capture — technique to stream database changes to downstream systems in near real-time                      |
|Columnar storage|Database storage format organizing data by column rather than row, optimizing analytical scan performance               |
|Dremio          |Open-source SQL query engine based on Apache Arrow, designed for querying data lake formats including Iceberg           |
|FRTB            |Fundamental Review of the Trading Book — Basel III/IV market risk capital framework                                     |
|GridGain        |Commercial distribution of Apache Ignite in-memory computing platform; the designated intraday data tier                |
|HDS             |Historical Data Store — the dedicated analytical persistence tier for trade and position history                        |
|Iceberg         |Apache Iceberg — open table format for large analytic datasets with ACID guarantees and time-travel capability          |
|OLAP            |Online Analytical Processing — workload pattern for complex analytical queries over large datasets                      |
|PFE             |Potential Future Exposure — regulatory credit risk metric requiring Monte Carlo simulation over trade populations       |
|S3              |Amazon Simple Storage Service (or compatible object storage) — storage layer in the cloud-native HDS candidate          |
|STMP            |Strategic Trade Management Platform — the overarching FICC platform of which the HDS is a component                     |
|VaR             |Value at Risk — statistical risk measure; historical VaR backtesting is a key HDS workload                              |
|WAL             |Write-Ahead Log — durability mechanism in GridGain ensuring events are persisted before acknowledgment                  |

-----

*Document 1 of 2 | Architecture Decision Record | FICC STMP*
