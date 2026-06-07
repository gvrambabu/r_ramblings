# FICC Cross-Asset Strategic Trade Management Platform

## Historical Data Store — Specialist Panel Review Framework

### Technology Candidate: Apache S3 + Apache Iceberg + Dremio

-----

|Field                 |Value                                                                           |
|----------------------|--------------------------------------------------------------------------------|
|**Document Role**     |Neutral Moderator Framework for Specialist Validation Panel                     |
|**Audience**          |Moderator, S3/Iceberg/Dremio Specialists, CTO Rep, Risk Technology Lead, CDO Org|
|**Companion Document**|Document 1 — Historical Data Store Business Case & ADR                          |
|**Status**            |DRAFT — Pre-Panel Preparation                                                   |

-----

> **MODERATOR NOTE:** This document is written entirely in a neutral, investigative voice. It is not written to validate or invalidate the S3+Iceberg+Dremio candidate. Its purpose is to surface the specific technical claims the stack must substantiate to meet the FICC Historical Data Store requirements defined in Document 1. The Exadata candidate is assessed through the same criteria framework in the parallel evaluation process.

-----

## 1. Purpose and Scope of This Document

This document is the working framework for a structured specialist panel review session. It is designed for use by a neutral moderator who will facilitate a technical deep-dive with specialists in the S3 + Apache Iceberg + Dremio stack, testing whether this technology combination can meet the requirements for the FICC Historical Data Store (HDS).

The HDS requirements are derived from Document 1 and summarized in Section 3. The question framework in Sections 4–10 is organized by requirement domain. Each question block includes:

- The primary question the specialists must answer
- The business context explaining why the question matters in FICC terms
- Follow-up probe questions that the moderator may use to pressure-test or clarify the initial response

> **WHAT THIS SESSION IS NOT:** This is not a vendor presentation or product pitch. Specialists are expected to provide honest technical assessments, including known limitations, workarounds, and open questions. The panel values a candid *“this works but with these constraints”* over an unqualified *“yes”*. The moderator will note any claims that require written follow-up substantiation.

-----

### 1.1 Panel Composition (Recommended)

|Role                                  |Background Expected                                                                                                               |Focus Domain                                                 |
|--------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------|
|S3 / Object Storage Specialist        |Deep experience with S3 at scale: versioning, lifecycle, consistency model, WORM configuration, cross-region replication          |Storage tier, data durability, compliance                    |
|Apache Iceberg Specialist             |Core committer or production-scale implementer; knowledge of catalog architecture, snapshot model, compaction, schema evolution   |Table format, ACID semantics, time-travel, bitemporal design |
|Dremio Query Engine Specialist        |Production Dremio deployment at financial services scale; Reflections architecture; Arrow Flight; concurrent workload management  |Query performance, concurrency, SQL completeness, integration|
|Data Pipeline / Integration Specialist|Experience integrating Kafka/event streams with Iceberg; GridGain CDC to S3 pipelines; near-real-time ingestion at high throughput|GridGain to HDS pipeline, ingestion latency, consistency     |
|Neutral Moderator                     |Capital Markets Technology Architecture Lead; familiar with FICC trade lifecycle, regulatory requirements, Exadata alternative    |Session facilitation, FICC context translation, scoring      |

-----

### 1.2 Session Format

|Segment                |Duration|Description                                                                               |
|-----------------------|--------|------------------------------------------------------------------------------------------|
|Opening                |15 min  |Moderator presents HDS requirements summary (this document, Section 3). No questions yet. |
|Domain Q&A — Blocks 1–3|60 min  |Moderator leads questions from Sections 4–6 (Data Model, Query Performance, CCAR Scale).  |
|Break                  |15 min  |—                                                                                         |
|Domain Q&A — Blocks 4–6|60 min  |Moderator leads questions from Sections 7–9 (Ingestion, Operational, Compliance).         |
|Open Challenge Round   |20 min  |Moderator poses the three hardest scenarios (Section 10). All specialists respond jointly.|
|Scoring and Next Steps |15 min  |Moderator reviews scoring rubric (Section 11). Agrees on follow-up items and deadlines.   |

-----

## 2. Moderator Ground Rules and Facilitation Notes

### 2.1 Principles of Neutral Moderation

- The moderator represents neither the S3+Iceberg+Dremio camp nor the Exadata camp. All questions are asked with equal rigor in each respective evaluation.
- The moderator does not express opinions on the technology. Observations are factual: *“You have stated X. Does that address requirement HDS-001?”*
- The moderator tracks unanswered or partially answered questions in a live issues log visible to all participants.
- If specialists disagree among themselves, the moderator surfaces the disagreement explicitly and records both positions rather than seeking premature consensus.
- Claims that cannot be substantiated in the session are recorded as *“Requires written follow-up within 5 business days.”*

### 2.2 Question Framing Language

The moderator should frame questions in FICC operational terms, not vendor terms.

|FICC Operational Term                             |Technical Translation for Specialists                                                                                                      |
|--------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
|A CCAR-style query across 5 years of trade history|Full table scan across ~5 billion rows, multiple joins, GROUP BY aggregation, running in a batch window of 4 hours                         |
|Bitemporal reconstruction as of March 31          |Query: *“Give me the state of table T as it was valid on 2024-03-31, as recorded in the system no later than 2024-04-05”*                  |
|Finance sub-ledger reconciliation                 |Complex multi-table join: trade table JOIN event table JOIN valuation snapshot table, filtered by month, aggregated to booking entity level|
|Regulatory audit reconstruction                   |Point-in-time query with exact transaction timestamp precision; full event lineage trace from trade ID                                     |
|Historical blotter subscription                   |User-facing query refreshing every 30 seconds; result set 50K–5M rows; multi-dimensional filter; must complete in < 10 seconds             |
|Near-real-time ingestion from GridGain            |Event stream at 5,000–50,000 events/second peak; each event must be queryable in the HDS within 30 seconds of being written to GridGain    |
|7-year immutable retention                        |No record can be physically deleted or modified; logical cancellation events only; audit trail must survive storage tier migration         |

-----

## 3. HDS Requirements Summary (From Document 1)

The following table restates the must-have requirements from Document 1, Section 5.1. Specialists should keep this in view throughout the session.

|ID     |Requirement                                                              |Priority     |
|-------|-------------------------------------------------------------------------|-------------|
|HDS-001|Bitemporal data model: valid time + transaction time for all records     |**MUST HAVE**|
|HDS-002|Immutable event append — logical cancellation only, no physical deletes  |**MUST HAVE**|
|HDS-003|Full event replay and state reconstruction as of any historical timestamp|**MUST HAVE**|
|HDS-004|Columnar storage for efficient analytical scan queries                   |**MUST HAVE**|
|HDS-005|ANSI SQL compliance with a mature optimizer for complex joins            |**MUST HAVE**|
|HDS-006|Time-series join capability (as-of join, snapshot join)                  |**MUST HAVE**|
|HDS-007|Concurrent heavy analytical workloads without intraday tier impact       |**MUST HAVE**|
|HDS-008|7-year data retention for all trade events                               |**MUST HAVE**|
|HDS-009|Scalability to 10+ billion events without performance degradation        |**MUST HAVE**|
|HDS-010|Partition pruning and predicate pushdown for efficient subset queries    |**MUST HAVE**|
|HDS-011|Near-real-time ingestion from GridGain event stream (< 30 second lag)    |**MUST HAVE**|
|HDS-012|Row and column-level RBAC                                                |**MUST HAVE**|
|HDS-013|Integration with downstream Finance, Risk, and Regulatory Reporting      |**MUST HAVE**|
|HDS-017|ACID transactions for event ingestion consistency                        |**MUST HAVE**|
|HDS-018|Parallel query execution and workload management                         |**MUST HAVE**|

-----

## 4. Question Domain 1: Data Model and Bitemporal Capability

This domain tests the most architecturally critical requirement: the ability to serve bitemporal queries with valid time and transaction time semantics across a trade history that may span 10+ years and billions of events.

-----

### Q1: How does this stack implement true bitemporal querying — specifically, both valid time (VT) and transaction time (TT) as independently queryable axes?

**Why We Ask:**
Iceberg’s native time-travel is snapshot-based (transaction time only). True bitemporality in the FICC sense requires querying *“what was the business-effective state of a trade on VT=March 31, as it was known to the system at TT=April 5.”* This is distinct from snapshot time-travel.

**Follow-up Probes:**

- Show us the table schema design that stores both VT and TT columns on each event record.
- Demonstrate a query: trade T, valid_date = 2024-03-31, known_as_of = 2024-04-05.
- Is this resolved at the application layer or the database layer? What is the query plan?
- What is the performance cost of bitemporal predicates on a table with 2 billion events?
- Can partition pruning operate on both VT and TT simultaneously?

-----

### Q2: Iceberg’s snapshot model is transaction-time oriented. How do you prevent conflation of Iceberg snapshot time-travel with true valid-time bitemporality?

**Why We Ask:**
A common implementation error is to use Iceberg snapshot time-travel as a proxy for valid-time reconstruction. These are categorically different. Iceberg snapshots reflect when data was written to the store; valid time reflects when the business event was economically effective. For a backdated trade amendment booked on April 5 with an economic effective date of March 31, the Iceberg snapshot and the valid-time state diverge immediately.

**Follow-up Probes:**

- Walk through a concrete backdated amendment scenario: trade booked on April 5, valid date March 31. How is this stored?
- How would you reconstruct the position state as it should have been reported for March 31 close?
- Is this bitemporality design documented? Are there reference implementations in production at a financial institution?
- What happens to Iceberg snapshot time-travel when a compaction (rewrite) job runs? Are bitemporal queries still consistent post-compaction?

-----

### Q3: Describe the immutability guarantee of this stack. Can records ever be physically deleted or overwritten?

**Why We Ask:**
HDS-002 requires that trade event records cannot be physically deleted or modified. This is a regulatory requirement — records must survive litigation holds, regulatory examinations, and audit. The mechanism of immutability matters: application-layer enforcement is weaker than storage-layer enforcement.

**Follow-up Probes:**

- At what layer is immutability enforced: S3, Iceberg, Dremio, or application?
- S3 Object Lock (WORM) can enforce immutability at the storage layer. Is this the intended mechanism? Does Iceberg interact correctly with S3 Object Lock?
- What happens during Iceberg compaction (file rewriting)? Does it interact with WORM locks? Can this accidentally delete data?
- How does a legal hold override work — can a specific record set be locked beyond its standard retention period?
- What is your evidence (production deployment or vendor documentation) that this immutability survives a storage tier migration (e.g., S3 Standard to S3 Glacier Deep Archive)?

-----

## 5. Question Domain 2: Query Performance — Historical Blotter and Finance Queries

This domain tests whether the stack can serve the interactive and batch analytical workloads identified in Document 1, Scenarios 3.1 and 3.4, at acceptable latency and concurrency.

-----

### Q4: What is the realistic query latency for a historical blotter query: 2 million trade records, multi-dimensional filter (desk, product, counterparty, date range), with joins to lifecycle events?

**Why We Ask:**
Historical blotter subscriptions require results in under 10 seconds for interactive use. Without acceleration, a cold Dremio query over 2 million Parquet files on S3 could easily exceed this. The Reflections mechanism is the likely answer, but its limitations must be understood.

**Follow-up Probes:**

- Without Reflections pre-computation, what is the cold query latency for this workload on a representative dataset? Provide numbers from a benchmark or production deployment.
- With Reflections enabled, what is the warm query latency? What is the Reflection build time, and how stale can it become?
- What happens when a user applies a filter combination not covered by an existing Reflection? Automatic fallback to raw scan — what is the latency?
- How many concurrent historical blotter queries can the cluster serve before latency degrades beyond the 10-second target?
- What is the operational burden of managing Reflections at scale? Who owns refresh scheduling, and what monitoring exists?

-----

### Q5: Finance sub-ledger reconciliation requires a time-series join: for each trade event, find the nearest valuation snapshot in time. How does this “as-of join” perform at scale?

**Why We Ask:**
This is a notoriously difficult query pattern for analytical databases. It requires finding, for each row in Table A, the latest row in Table B where `timestamp_B <= timestamp_A`. Native SQL does not have a standard “as-of join” operator; most implementations require correlated subqueries or window functions that can be extremely expensive at scale.

**Follow-up Probes:**

- Does Dremio support an efficient as-of join operation natively, or must it be implemented as a correlated subquery / window function?
- Show the query plan for: `JOIN trade_events e ON valuation_snapshots v WHERE v.snapshot_time = MAX(v.snapshot_time) WHERE v.snapshot_time <= e.event_time AND v.trade_id = e.trade_id`
- What is the execution time for this join across 500,000 trade events and 10 million valuation snapshots?
- Is there a Reflection design that pre-materializes the join to avoid runtime cost?
- How does this perform for Iceberg tables that are heavily partitioned by date — does the join span many partition files?

-----

### Q6: Dremio uses Apache Arrow and columnar in-memory processing. What are the actual memory requirements for a concurrent session handling 10 simultaneous heavy analytical queries?

**Why We Ask:**
The Finance month-end close and CCAR batch workloads will likely run concurrently with ongoing trader historical blotter sessions. Memory pressure under concurrency is a well-known challenge for in-memory query engines. Spill-to-disk behavior under memory pressure must be understood.

**Follow-up Probes:**

- What is the per-query memory footprint for a 2-billion-row scan with aggregation?
- Does Dremio support memory-bounded execution with automatic spill to disk? What is the performance penalty when spilling?
- What workload isolation mechanisms exist — can CCAR batch jobs be quarantined from interactive blotter queries?
- What is the observed throughput degradation curve as concurrent queries increase from 5 to 20 to 50?
- What happens if a query exhausts available memory — clean failure with error, or does it impact other running queries?

-----

## 6. Question Domain 3: CCAR / FRTB Scale Workloads

This is the highest-stakes performance domain. CCAR and FRTB workloads define the true scale ceiling of the HDS. Failure here means the bank’s regulatory capital process is at risk.

-----

### Q7: Our CCAR workload requires scanning 5 million trades across 13 quarters of projected scenarios. Can this stack execute this within a 4-hour overnight batch window?

**Why We Ask:**
This is not a theoretical benchmark — it is a live regulatory obligation. The stack must demonstrate, not claim, this capability. We need reference benchmarks at this scale.

**Follow-up Probes:**

- Provide a reference production deployment where a dataset of comparable size (5B+ rows) was scanned within a 4-hour window. What was the Dremio cluster configuration?
- How does the query parallelize across Dremio executor nodes? What is the scaling curve?
- What is the S3 read throughput that limits this workload? What S3 configuration (prefix distribution, request rate limits) is required at this scale?
- If the batch window is at risk (e.g., due to a data quality rerun), what is the ability to run a partial/incremental re-execution?
- How does Iceberg partition pruning reduce the effective dataset size for scenario-partitioned CCAR data?

-----

### Q8: FRTB Sensitivity-Based Method requires computing delta, vega, and curvature sensitivities for 1.2 million risk factors. Does Dremio support the complex SQL window functions and aggregations this requires?

**Why We Ask:**
FRTB SBM aggregation logic requires nested GROUP BY operations across risk buckets and correlations, conditional aggregations (diversified vs. undiversified), and multiple passes over the sensitivity dataset. This is SQL-intensive and tests the maturity of the query optimizer.

**Follow-up Probes:**

- Does Dremio support correlated subqueries, nested GROUP BY, and CASE-based conditional aggregations at FRTB scale?
- Can you share a query complexity benchmark: how many GROUP BY levels and CASE expressions before the optimizer degrades?
- FRTB requires running the same sensitivity data through multiple aggregation paths (low, medium, high correlation scenarios). How does Dremio handle query fan-out of this type?
- What is the recommended Iceberg table design for sensitivity data — partition by risk class, bucket by bucket ID, or other?
- Have you deployed this for an FRTB workload in production? If not, what is the closest comparable deployment?

-----

### Q9: Historical VaR backtesting requires computing daily P&L for each of 250 trading days across 800,000 positions. This is a nested loop computation. How does this stack handle it?

**Why We Ask:**
This workload has a cross-join character: for each position, for each of 250 historical scenarios, compute P&L. Naively implemented as a SQL cross-join, this produces 200 million result rows. The implementation typically requires either a denormalized storage design or a computation push-down to the query engine.

**Follow-up Probes:**

- What is the recommended data model for storing historical scenario results — pre-computed at ingestion, or computed at query time?
- If computed at query time, demonstrate the execution plan for a 250-day VaR computation over 800K positions.
- Does Dremio support user-defined functions (UDFs) for custom P&L calculation logic that may be needed for complex instruments?
- What is the ability to incrementally update the VaR dataset when new trades are added intraday, without recomputing the full 250-day history?
- How does this workload interact with Iceberg’s file size and compaction settings — does query performance degrade as the number of small files increases?

-----

## 7. Question Domain 4: Data Ingestion from GridGain

The HDS is useless if it cannot receive data from the intraday tier promptly and reliably. This domain tests the pipeline between GridGain and the S3+Iceberg+Dremio stack.

-----

### Q10: Our requirement is that trade events written to GridGain are queryable in the HDS within 30 seconds. What is the architecture of the ingestion pipeline, and what is the measured end-to-end latency?

**Why We Ask:**
The pipeline likely involves GridGain CDC/continuous queries, a Kafka topic, a streaming consumer writing to Iceberg, and Dremio metadata refresh. Each hop adds latency. Iceberg’s default commit behavior may batch writes, which introduces additional lag.

**Follow-up Probes:**

- Walk through each hop in the pipeline and the latency contribution of each hop.
- Iceberg streaming ingestion typically writes micro-batches. What is the minimum micro-batch interval? Is 30-second end-to-end achievable?
- Does Dremio automatically detect new Iceberg snapshots, or does it require a manual metadata refresh command? What is the refresh latency?
- What happens during GridGain maintenance (rolling restart, rebalance) — does the CDC stream pause, and does the HDS handle gaps gracefully?
- At peak trading volumes (50,000 events/second), what is the throughput capacity of the ingestion pipeline? What is the backlog recovery time if the pipeline falls behind?

-----

### Q11: ACID semantics are required for event ingestion — specifically, a trade and all its constituent leg events must be written atomically, or not at all. How does Iceberg support multi-table atomic writes?

**Why We Ask:**
A single trade capture event in FICC often generates writes to multiple Iceberg tables: the trade table, the event table, the position delta table, and possibly the valuation table. These must be atomic — a partial write (e.g., trade written but position delta lost) creates reconciliation breaks.

**Follow-up Probes:**

- Does Apache Iceberg support multi-table transactions natively? Or is atomicity limited to a single table?
- If multi-table atomicity is not natively supported, what is the compensating design — saga pattern, application-layer coordination, or other?
- What is the failure mode if a write to the HDS fails mid-transaction? What is the recovery mechanism?
- How does concurrent write contention on the Iceberg catalog manifest at peak throughput? Have you observed commit conflicts at 50K events/second?
- What catalog implementation is used (Hive Metastore, Glue, Nessie, Polaris)? What are the consistency and latency characteristics of catalog operations at scale?

-----

### Q12: The HDS must maintain a complete and ordered event log with no gaps and no duplicates. How is exactly-once delivery guaranteed from GridGain through Kafka to Iceberg?

**Why We Ask:**
Exactly-once semantics in distributed streaming pipelines are well-understood to be hard. The combination of GridGain CDC, Kafka at-least-once delivery, and Iceberg idempotent writes must be designed carefully to guarantee exactly-once event landing.

**Follow-up Probes:**

- Is the Kafka consumer configured for at-least-once or exactly-once semantics? If at-least-once, how are duplicates detected and deduplicated before the Iceberg write?
- What is the event ordering guarantee? Can events from the same trade arrive out of order due to Kafka partition routing, and if so, how is ordering reconstructed in Iceberg?
- What monitoring exists to detect event gaps — trades that should have arrived but did not?
- How does the pipeline handle schema evolution — if the GridGain event schema changes (new fields added), how is this propagated to the Iceberg schema without pipeline downtime?

-----

## 8. Question Domain 5: Operational Characteristics

The HDS will be a production-critical system for the bank’s regulatory and Finance processes. Operational maturity, not just technical capability, is evaluated here.

-----

### Q13: What is the Dremio cluster’s failure mode when an executor node fails during a CCAR batch run that has been executing for 2 hours?

**Why We Ask:**
Long-running CCAR batch queries represent a specific operational risk: a node failure mid-query means the query must restart from scratch, potentially missing the batch window. Fault tolerance and checkpointing are critical.

**Follow-up Probes:**

- Does Dremio support query checkpointing and restart from a checkpoint after node failure? Or does the query restart from scratch?
- What is the fault tolerance model for Dremio executors — is partial results state preserved on coordinator when an executor fails?
- What is the recommended Dremio cluster topology for CCAR-scale resilience — minimum executor count, replication factor?
- Has this failure scenario been tested in your environment? What was the observed behavior?
- Is there a mechanism to run CCAR-scale queries on a dedicated Dremio resource pool isolated from interactive query pools?

-----

### Q14: Iceberg compaction (file rewriting) is required to maintain query performance over time. How does compaction interact with live query traffic and active ingestion?

**Why We Ask:**
Iceberg tables that receive continuous streaming writes accumulate many small Parquet files, degrading scan performance over time. Compaction rewrites these into larger files. This competes for S3 I/O and can affect query latency. In a bank context, compaction cannot run during trading hours without a documented impact analysis.

**Follow-up Probes:**

- What is the compaction strategy recommended for a high-ingestion Iceberg table receiving 50K events/second?
- Does compaction block concurrent reads or writes? What is the Iceberg isolation guarantee during compaction?
- How is compaction scheduled — manual, automated, or event-triggered? Who manages the schedule?
- What is the performance degradation curve if compaction is delayed — at what file count does query latency materially degrade?
- How long does compaction take for a 1-year partition of trade event data (estimated at 500 GB compressed Parquet)?

-----

### Q15: Describe the role-based access control model for this stack. Can we enforce column-level and row-level security such that a trader can only see their own desk’s data?

**Why We Ask:**
FICC data is sensitive. A Muni trader must not see Rates desk positions. A junior analyst must not see trader identities. Row-level and column-level security must be enforced at the query engine layer, not the application layer, to be defensible.

**Follow-up Probes:**

- Is row-level security enforced at the Dremio query engine layer (filter applied before data leaves the engine) or at the application layer?
- Is column-level masking supported natively — e.g., mask the `trader_id` column for users without `trader_identity` permission?
- How are access control policies defined and managed — code, UI, LDAP/AD integration?
- What is the audit log granularity — is every data access (SELECT query) logged with user identity, timestamp, and data rows returned?
- How does access control scale when there are 500+ users with different permission profiles across 20 desks and 5 legal entities?

-----

## 9. Question Domain 6: Regulatory Compliance and Audit

This domain tests whether the stack can meet the specific regulatory requirements articulated in Document 1, Scenarios 3.5 and 3.3. These are non-negotiable requirements.

-----

### Q16: A regulator submits an inquiry: “Provide all FX swap trades between your US entity and Counterparty X during calendar year 2023, including all amendments, their timestamps, the user who booked each event, and the market data used for valuation at each event.” Can this query be answered from this stack, and within what timeframe?

**Why We Ask:**
This is a realistic regulatory inquiry (based on CFTC examination patterns). It requires joining trade events, user audit logs, and market data snapshots — potentially stored in different Iceberg tables or separate systems. The answer must be complete, consistent, and defensible.

**Follow-up Probes:**

- Are user identity (trader, ops user) and system metadata stored in the Iceberg event table, or in a separate system? How are they joined?
- Is market data stored in the same HDS, or is it a separate system? How is the *“market data used for valuation at event time”* query resolved?
- What is the query execution time for this regulatory extraction across one year of FX swap data for a single counterparty?
- How is the extracted dataset certified as complete and unmodified for submission to the regulator?
- Does the stack have a formal data lineage capability — can you trace each event record back to its source system, ingestion timestamp, and transformation steps?

-----

### Q17: S3 Object Lock (WORM) is the primary immutability mechanism at the storage layer. What is the interaction between Iceberg’s metadata management and S3 Object Lock, and can Iceberg’s housekeeping operations accidentally unlock or delete records within the retention period?

**Why We Ask:**
This is a specific technical risk that has caught production implementations. Iceberg’s built-in maintenance procedures (`expireSnapshots`, `deleteOrphanFiles`) are designed to clean up old data. If S3 Object Lock is enabled, these operations should fail safely — but the interaction must be explicitly tested and documented.

**Follow-up Probes:**

- Have you tested Iceberg `expireSnapshots` against S3 Object Lock in COMPLIANCE mode? What was the result?
- If Iceberg metadata (manifest files, snapshot files) is not covered by S3 Object Lock, can the table be rendered unreadable while the data files remain locked?
- What is the recommended configuration for a regulatory WORM deployment — which S3 Object Lock mode (Governance vs. Compliance), what retention period, and which Iceberg maintenance operations must be disabled?
- Who in your organization has production experience with Iceberg on S3 WORM for a financial regulatory use case? Can you provide a reference?

-----

### Q18: Is there documented evidence of this S3 + Iceberg + Dremio stack being accepted by financial regulators (CFTC, SEC, FCA, ESMA, PRA) as an approved data store for regulatory trade data?

**Why We Ask:**
Technology novelty is a legitimate regulatory risk. Regulators examining a firm’s records management will scrutinize whether the data store meets their expectations for data integrity, immutability, and auditability. Exadata has 20+ years of regulatory acceptance. The Iceberg/Dremio stack is newer in regulated contexts.

**Follow-up Probes:**

- Are there published or documented cases of the CFTC, SEC, or FCA accepting S3+Iceberg as a compliant records management system for OTC derivative trade data?
- What engagement has Dremio or the Iceberg project had with financial regulators to establish compliance posture?
- What compensating controls would you recommend if direct regulatory precedent is not available — e.g., independent auditor attestation of immutability, external hash registry for event records?
- What is the risk assessment if a regulator challenges the data store design during an examination?

-----

## 10. Open Challenge Round: The Three Hardest Scenarios

These three scenarios are presented to the full specialist panel in open discussion. The moderator presents each scenario verbally, without telegraphing the expected answer. The panel is asked to discuss collaboratively.

-----

### 10.1 The Backdated Amendment Stress Test

> **CHALLENGE SCENARIO**
> 
> It is April 7, 2024. The Finance team is running the March 31 month-end close. A trader notifies Operations that a credit default swap booked on April 2 should have had an effective date of March 28 (backdated). Operations amends the trade in the STMP at 09:47 AM on April 7, changing the valid date to March 28.
> 
> The Finance team needs to determine:
> 
> - **(a)** What the correct March 31 position state is, reflecting this backdated amendment
> - **(b)** What the position state would have been reported as on April 1, before this correction was known
> 
> This is a classic bitemporal query. **The challenge:** demonstrate how this is served by the stack, step by step, including the specific query syntax and execution plan.

-----

### 10.2 The Pipeline Failure Recovery Test

> **CHALLENGE SCENARIO**
> 
> The Kafka consumer feeding events from GridGain to the Iceberg tables fails at 10:15 AM and is not detected until 11:45 AM — 90 minutes of trade events are not in the HDS. At 12:00 PM, the Risk Technology team needs to run an intraday FRTB sensitivity report off the HDS.
> 
> **The challenge:** What is the recovery procedure? How quickly can the 90-minute gap be backfilled? What is the consistency state of the HDS during backfill — does it present a partial view of data, and if so, how is the partial view communicated to consuming systems so they don’t report on incomplete data? What controls exist to detect this failure before it affects downstream systems?

-----

### 10.3 The 7-Year Point-in-Time Query Under Cost Optimization Pressure

> **CHALLENGE SCENARIO**
> 
> It is 2031. Seven years of trade data are in the HDS. Under cost optimization pressure, the data engineering team has moved data older than 2 years to S3 Glacier Deep Archive at $0.004/GB/month. An FRTB Internal Models Approval audit requires reconstructing the full sensitivity history for a trading book from 2025 to 2028 — data that now sits in Glacier.
> 
> The audit team needs a response within 5 business days.
> 
> **The challenge:** What is the Glacier restore procedure? What is the restore latency (Glacier restore can take 12 hours for Expedited tier, 48 hours for Standard)? Once restored, how does Dremio query the restored data alongside hot-tier data transparently? What is the cost of the restore operation? Is the bank’s regulatory response timeline achievable?

-----

## 11. Scoring Rubric and Decision Output

### 11.1 Response Quality Scoring

The moderator scores each question response on the following scale and records scores in the live issues log:

|Score          |Label                    |Criteria                                                                                                                           |
|---------------|-------------------------|-----------------------------------------------------------------------------------------------------------------------------------|
|**4 — Full**   |Requirement Met          |Specialist provides a clear, substantiated answer with production evidence or documented benchmark. Requirement is fully addressed.|
|**3 — Partial**|Requirement Mostly Met   |Specialist provides a credible answer with identified constraints or caveats. Requirement is met with known workarounds.           |
|**2 — Gap**    |Requirement Partially Met|Specialist acknowledges a gap or limitation. A compensating design is proposed but not validated. Written follow-up required.      |
|**1 — Risk**   |Requirement At Risk      |Specialist cannot address the requirement or the proposed solution introduces material operational or regulatory risk.             |
|**0 — Fail**   |Requirement Not Met      |Specialist confirms the requirement cannot be met with this stack as currently designed.                                           |

-----

### 11.2 Requirement Scoring Summary Template

|HDS Req ID    |Requirement (Short)           |Score (0–4)|Notes / Follow-up|
|--------------|------------------------------|-----------|-----------------|
|HDS-001       |Bitemporal (VT + TT)          |           |                 |
|HDS-002       |Immutable append only         |           |                 |
|HDS-003       |Event replay / reconstruction |           |                 |
|HDS-004       |Columnar storage              |           |                 |
|HDS-005       |ANSI SQL + optimizer          |           |                 |
|HDS-006       |Time-series / as-of join      |           |                 |
|HDS-007       |Workload isolation            |           |                 |
|HDS-008       |7-year retention              |           |                 |
|HDS-009       |10B event scalability         |           |                 |
|HDS-010       |Partition pruning / pushdown  |           |                 |
|HDS-011       |< 30 sec ingestion lag        |           |                 |
|HDS-012       |Row + column RBAC             |           |                 |
|HDS-013       |Downstream integration        |           |                 |
|HDS-017       |ACID ingestion transactions   |           |                 |
|HDS-018       |Parallel execution / WLM      |           |                 |
|Challenge 10.1|Backdated amendment bitemporal|           |                 |
|Challenge 10.2|Pipeline failure recovery     |           |                 |
|Challenge 10.3|7-year cold tier query        |           |                 |

-----

### 11.3 Panel Conclusion Categories

|Outcome                                        |Criteria                                                                                                             |Next Step                                                                          |
|-----------------------------------------------|---------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
|**APPROVED — Proceed to POC**                  |All MUST HAVE requirements scored 3 or 4. No score of 0. No unresolved written follow-ups on critical items.         |Commission POC benchmark using actual FICC trade data. Define POC success criteria.|
|**CONDITIONAL — Proceed with remediation plan**|All MUST HAVE requirements scored 2 or above. At most 3 items scored 2. Written follow-up plan agreed with deadlines.|Resolve follow-up items within 10 business days. Re-score before POC decision.     |
|**DEFERRED — Further design work required**    |One or more MUST HAVE requirements scored 1. Material gaps in bitemporal design, immutability, or CCAR scale.        |Specialists present revised design addressing gaps. New panel session scheduled.   |
|**REJECTED — Does not meet requirements**      |Any MUST HAVE requirement scored 0. Or regulatory compliance (Domain 6) scored below 2 on multiple questions.        |Proceed with Exadata as primary candidate. Document rejection rationale for ARB.   |

-----

## 12. Written Follow-up and POC Framework

### 12.1 Written Follow-up Commitment Template

For each question where the panel response was scored 2 (Gap) and written follow-up was committed:

|Field             |Content                                                                      |
|------------------|-----------------------------------------------------------------------------|
|Question Reference|(e.g., Q1 — Bitemporal Design)                                               |
|Gap Identified    |(Description of the unanswered aspect)                                       |
|Committed Response|(What the specialist will provide)                                           |
|Response Format   |(Written document / benchmark results / reference architecture / code sample)|
|Due Date          |(Agreed date — maximum 10 business days from panel session)                  |
|Owner             |(Named specialist responsible)                                               |
|Reviewer          |(Moderator or nominated technical reviewer)                                  |

-----

### 12.2 Proof of Concept Benchmark Design (If Panel Approved)

If the panel outcome is APPROVED or CONDITIONAL, the following POC benchmarks are required before the final technology selection decision:

|Benchmark                           |Dataset                                            |Success Criterion                                              |
|------------------------------------|---------------------------------------------------|---------------------------------------------------------------|
|POC-1: Historical blotter query     |2M trades, 5 dimensions, multi-join                |< 10 seconds end-to-end, cold start                            |
|POC-2: CCAR scale scan              |5M trades × 13 quarters (65M rows)                 |< 4 hours on reference cluster configuration                   |
|POC-3: Bitemporal reconstruction    |Backdated amendment dataset from Section 10.1      |Correct VT/TT reconstruction with < 5 second latency           |
|POC-4: Ingestion pipeline latency   |Live GridGain event stream, 10K events/sec         |End-to-end < 30 seconds, 0 gaps, 0 duplicates                  |
|POC-5: Concurrent workload          |5 blotter queries + 1 CCAR batch simultaneous      |No blotter query exceeds 30 seconds; CCAR completes on schedule|
|POC-6: Immutability under compaction|S3 Object Lock COMPLIANCE mode + Iceberg compaction|Zero data loss; compaction fails safely on locked objects      |

-----

> **FINAL NOTE TO MODERATOR:** The quality of this panel session will determine whether the bank makes a well-informed technology decision or a speculative one. Press for specificity. Resist generalities. A claim of *“yes, Iceberg supports that”* without a demonstrated query plan, benchmark number, or production reference should be scored as a gap, not a full. The bank’s regulatory obligations are not a place for optimism without evidence.

-----

*Document 2 of 2 | Specialist Panel Review Framework | FICC STMP HDS Evaluation*
