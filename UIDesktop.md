Below is a full proposal you can take to architecture review / leadership. It integrates your original vision, the critique, and the strengthened model into a cohesive, executable operating blueprint—and then grounds it with Swaps Desk and FX Options Desk examples.

⸻

🧭 Proposal: Composable FICC Trading Desktop Platform

Built on:
	•	OpenFin Desktop
	•	OpenFin Workspaces
	•	Micro Frontends (MFEs)
	•	Streaming Data (AMPS / Ignite / Deephaven)
	•	gRPC + Webhooks
	•	FDC3
	•	MFE Registry (Control Plane)

⸻

1) 🎯 Vision

Create a Composable, Real-Time, Domain-Aligned Trading Desktop Platform where:

	•	Teams deliver independent capabilities
	•	Traders compose personalized workflows
	•	Data flows stream-first and low-latency
	•	Interoperability is standardized, not custom-built

⸻

2) 🧱 Core Architectural Layers

Layer 1: Desktop Platform Layer
	•	OpenFin Desktop = runtime container
	•	OpenFin Workspaces = layout + workflow orchestration

Responsibilities
	•	Windowing, layout persistence
	•	Identity & entitlements
	•	Interop (FDC3)
	•	Theming injection

⸻

Layer 2: Experience Layer (Micro Frontends)
	•	Independent MFEs:
	•	Pricing
	•	Blotter
	•	Risk
	•	Analytics

Key Rule

MFEs are plug-ins, not apps

⸻

Layer 3: Domain Backend Layer (BFFs)
	•	Domain-aligned BFFs (not per MFE)

Examples:
	•	Rates BFF
	•	FX Options BFF

Responsibilities
	•	Data aggregation
	•	Entitlements
	•	Protocol translation (gRPC ↔ streaming)

⸻

Layer 4: Streaming Data Layer
	•	AMPS / Ignite / Deephaven

Characteristics
	•	Push-based
	•	Schema-governed
	•	Entitlement-filtered

⸻

Layer 5: Control Plane (MFE Registry)
	•	Central service managing:
	•	MFE discovery
	•	Versioning
	•	Compatibility
	•	Workspace configurations

⸻

Layer 6: Workflow Orchestration Layer (NEW – Critical)

Sits between MFEs and platform.

Responsibilities
	•	Multi-step workflow coordination
	•	State management across MFEs
	•	Event sequencing

👉 This solves FDC3 limitations

⸻

3) 🧩 Core Design Principles (Refined)

1) Platform-First Architecture
	•	Desktop is a platform, not a UI container
	•	MFEs integrate via contracts, not assumptions

⸻

2) Controlled Isolation (Not Absolute Isolation)
	•	Default: No direct dependencies
	•	Exception: Domain-level orchestration allowed

👉 Enables performance + realism

⸻

3) Streaming-First Data Model
	•	UI subscribes to data streams
	•	No polling

👉 Critical for FICC latency

⸻

4) Standardized Interoperability
	•	Use FDC3 for:
	•	Context sharing
	•	Simple intents
	•	Use Orchestrator for:
	•	Complex workflows

⸻

5) Domain-Aligned Ownership

Each team owns:
	•	MFE(s)
	•	BFF
	•	Data contracts
	•	FDC3 contracts

⸻

6) Control Plane Governance

MFE Registry ensures:
	•	Version compatibility
	•	Controlled rollout
	•	Workspace-specific configurations

⸻

7) Design System as Runtime Contract
	•	Unified theming
	•	Shared component wrappers (AgGrid, Shadcn)
	•	Enforced at runtime

⸻

8) Workspace-Centric UX
	•	Users compose workflows
	•	Persist layouts and states

⸻

9) Observability by Design
	•	Trace:
	•	Data → Backend → MFE → User interaction

⸻

10) Golden + Custom Workspaces
	•	Predefined templates
	•	User extensions

⸻

4) 🔁 Interaction Model

A. Simple Interaction (FDC3)
	•	FX Option selected → broadcast context
	•	Other MFEs react

B. Complex Interaction (Orchestrated)
	•	Trade lifecycle:
	•	Pricing → Execution → Risk → Booking
	•	Managed by orchestration layer

⸻

5) 📦 Key Platform Components

1) Streaming SDK

Abstracts:
	•	AMPS / Ignite / Deephaven
	•	Subscription lifecycle
	•	Backpressure

⸻

2) Desktop Control Plane (Enhanced Registry)

Capabilities:
	•	Dynamic MFE loading
	•	Version resolution
	•	Feature flags
	•	Workspace-aware deployments

⸻

3) Workflow Orchestrator
	•	Stateful workflows
	•	Event sequencing
	•	Retry / recovery

⸻

4) Design System Kit
	•	Wrapped components:
	•	Grid (AgGrid)
	•	UI primitives (Shadcn)
	•	Enforced styles

⸻

6) 🏦 Example 1: Swaps Desk (Rates)

MFEs

1) Swap Blotter MFE
	•	Real-time trades
	•	Streaming via Rates BFF

2) Pricing MFE
	•	Live curve-based pricing

3) Risk MFE
	•	DV01, PV, sensitivities

4) Trade Execution MFE

⸻

Workflow Example: Swap Trade Execution

Step 1: Pricing
	•	Trader selects swap
	•	Pricing MFE streams:
	•	Yield curves
	•	Live pricing

Step 2: Context Sharing
	•	Instrument broadcast via FDC3

⸻

Step 3: Execution (Orchestrated)
	•	Workflow Orchestrator:
	•	Validates trade
	•	Calls Rates BFF via gRPC
	•	Tracks execution state

⸻

Step 4: Risk Update
	•	Risk MFE auto-refreshes via stream

⸻

Step 5: Blotter Update
	•	Trade appears instantly (stream push)

⸻

Key Observations
	•	No direct MFE coupling
	•	Shared state handled by orchestrator
	•	Data is real-time throughout

⸻

7) 💱 Example 2: FX Options Desk

MFEs

1) Vol Surface MFE
	•	Visualizes implied volatility

2) Option Pricing MFE
	•	Greeks, premium

3) Strategy Builder MFE
	•	Multi-leg structures

4) Execution MFE

⸻

Workflow Example: FX Option Strategy Trade

Step 1: Market Analysis
	•	Vol Surface MFE streams:
	•	Smile/skew data

⸻

Step 2: Strategy Creation
	•	Strategy Builder:
	•	Creates multi-leg structure

⸻

Step 3: Context Sharing
	•	Strategy broadcast via FDC3

⸻

Step 4: Execution (Orchestrated)
	•	Workflow Orchestrator:
	•	Validates multi-leg consistency
	•	Calls FX Options BFF
	•	Handles partial fills

⸻

Step 5: Risk + PnL Update
	•	Risk MFE streams Greeks
	•	PnL updates in real-time

⸻

Key Observations
	•	Complex multi-leg handled outside FDC3
	•	Real-time Greeks via streaming layer
	•	Clean separation of concerns

⸻

8) ⚖️ Why This Works (Stronger Argument)

Compared to Traditional Desktops

Capability	Traditional	Proposed
Deployment	Monolithic	Independent MFEs
Data	Request/response	Streaming
Interop	Custom	FDC3 + Orchestrator
UX	Static	Workspace-driven
Scalability	Hard	Built-in


⸻

Business Impact

1) Faster Time to Market
	•	Teams deploy independently

2) Improved Trader Productivity
	•	Personalized workflows

3) Better Performance
	•	Streaming-first → lower latency

4) Reduced Risk
	•	Isolation + observability

⸻

9) 🚨 Non-Negotiables for Success
	1.	Streaming SDK standardization
	2.	Strong data + FDC3 contracts
	3.	Control plane enforcement
	4.	Workflow orchestration layer
	5.	Domain-aligned teams
	6.	Design system governance

⸻

10) 🧠 Final Positioning Statement

This architecture is not just a UI modernization—it is a strategic shift to a Composable Trading Platform, enabling real-time, domain-driven, and user-configurable trading workflows across FICC.

⸻

If you want next step:

I can convert this into:
	•	Architecture diagram (C4 / layered view)
	•	Execution roadmap (6–12 months phased rollout)
	•	Operating model + RACI
	•	OKRs/KPIs tied to business outcomes

Just tell me 👍


This design transforms the trading desktop from a collection of siloed applications into a Composable Trading Operating System. By utilizing OpenFin Workspaces as the delivery shell and a custom Registry as the control plane, we enable high-velocity feature delivery without compromising the stability of the Tier-1 trading environment.
1. Vision and Objectives
To establish a Marketplace of Trading Capabilities where business logic is decentralized (federated) but the user experience and operational risk are managed centrally.
 * Decouple Release Cycles: Allow the FX desk to deploy a pricer update at 10:00 AM without impacting the Rates desk’s blotter.
 * Contextual Intelligence: Use FDC3 to ensure that clicking a CUSIP in a research MFE instantly updates the "Order Entry" and "Risk" MFEs.
 * Zero-Config Discovery: Traders should find tools as easily as searching on a smartphone, with entitlements pre-filtered.
2. Core Platform Capabilities
The MFE Registry (Control Plane)
The "Source of Truth" for the ecosystem. It is a gRPC-based service storing the state of all deployed MFEs, their versions, and their interoperability contracts.
The Storefront (The "App Store")
A React-based discovery portal embedded in OpenFin. It allows PMs to "shop" for components and see live previews of MFEs using mock data.
The Workspace Provider
A specialized OpenFin service that intercepts Home (Search) and Store requests. It dynamically builds the user’s UI by querying the Registry based on the user's LDAP/Active Directory groups.
3. User Journeys
Developer Registration Flow
 * Build: Dev pushes code to a domain-specific repo.
 * Validate: CI/CD runs a "Platform Compatibility Test" (e.g., checking for specific ag-grid versions and Tailwind-only CSS).
 * Register: A POST request is sent to the Registry with the MFE manifest.
 * Sandbox: The MFE is instantly available in the "Staging" Storefront for PM approval.
Product Manager Workflow Configuration
 * Browse: PM enters the Storefront and filters by "Yield Curve" or "Execution."
 * Compose: PM uses a drag-and-drop "Workspace Builder" to snap MFEs together.
 * Publish: PM saves the layout as a "Public Workspace" for the Swaps Desk.
Trader Workspace Consumption
 * Search: Trader hits Alt + Space, types "Rates Dashboard."
 * Launch: OpenFin Home resolves the intent, fetches the PM-approved layout, and hydrates the MFEs.
 * Sync: As the trader filters for "USD Libor," all MFEs in that workspace update via FDC3 broadcast channels.
4. MFE Registration Model
The Registry captures a JSON schema for every component. This is critical for automated discovery.
| Field | Data Type | Requirement |
|---|---|---|
| appId | String | Unique identifier (e.g., fx-options-volsurface). |
| manifestUrl | URL | The location of the app.json (OpenFin config). |
| fdc3Config | Object | Declares listensTo and publishes context types (e.g., fdc3.instrument). |
| dataContracts | Array | AMPS topics or gRPC endpoints required for the MFE to function. |
| entitlements | Array | Required AD Groups (e.g., APP_FICC_TRADER_PROD). |
| performanceSLA | Object | Target "Time to Interactive" (TTI) and Max Memory usage. |
5. Governance and Approval Model
We utilize a Two-Tiered Gatekeeping system:
 * Automated (The "Synthetic Auditor"):
   * Bundle Analysis: Rejects MFEs exceeding 500KB (initial load).
   * Security Scan: Checks for vulnerable NPM packages and hardcoded secrets.
   * Design Linting: Verifies Shadcn/Tailwind tokens match the bank's brand.
 * Human (The "Product Gate"):
   * UX Review: Platform Design Leads verify the MFE doesn't "break" the OpenFin grid layout.
   * Risk Approval: Business Risk confirms the data displayed meets regulatory transparency requirements.
6. Workspace Composition Model
Using OpenFin Platform API, we treat layouts as "Stateful Snapshots."
 * View Injection: MFEs are loaded as OpenFin Views within a Window.
 * Interlink Logic: If the PM defines a "Side-by-Side" workflow, the Registry injects a "Bridge Script" that maps FDC3 intents specifically for that layout, preventing context leakage to other open windows.
 * Persistence: Layouts are stored in the Registry as JSON, allowing a trader to log in from a different terminal and see the exact same MFE positions.
7. Federation Model
The "Hub and Spoke" model ensures the platform team is not a bottleneck.
 * Platform Team (The Hub): Owns the OpenFin license, the Registry API, the Design System, and the "Shell."
 * Domain Pods (The Spokes): FX, Rates, Credit, and Commodities teams each own their MFEs, their domain-aligned BFF (Backend for Frontend), and their data pipelines (e.g., Ignite/AMPS).
8. Operating Model
 * Platform Architect: Defines the "Contract" (FDC3, gRPC patterns).
 * Domain Lead: Accountable for the MFE lifecycle and business logic.
 * SRE: Monitors the Registry and the "Health" of the OpenFin bus across the floor.
9. Examples
FX Options Desk
 * MFE: "Volatility Surface Visualizer."
 * Integration: Registered as an MFE that consumes a Deephaven stream. It publishes the fdc3.valuation context.
 * Onboarding: Devs register it; PM adds it to the "FX Options Core" workspace.
Swaps Desk
 * Workflow: Creating a "Relative Value" workspace.
 * Action: PM drags an "AgGrid-powered Blotter" and a "Real-time Curve Chart."
 * Result: When a trader selects a 10Y Swap in the blotter, the chart MFE (developed by a different team) automatically re-plots the curve for that specific tenor.
10. KPIs and Success Metrics
 * Time to Desktop: Measure from "Code Commit" to "Visible in Storefront" (Target: < 1 hour for minor updates).
 * Component Reuse: % of MFEs used in more than one desk's workspace.
 * Crash Rate per MFE: Using OpenFin's system-report, identify which domain's MFE causes the most renderer crashes.
11. Risks and Mitigation Strategies
| Risk | Mitigation |
|---|---|
| Data Silos | Enforce a "Standard Data Catalog" in the Registry; MFEs cannot use "dark" data sources. |
| Performance Degradation | Implement "Lazy Hydration"—MFEs in background tabs are throttled until focused. |
| FDC3 Version Bloat | Use a central Interop Broker to map legacy intents to new FDC3 standards. |
Next Steps:
Would you like me to provide a sample TypeScript manifest definition for the MFE Registry or a system architecture diagram showing the flow between OpenFin and the gRPC backend?


This design transforms the trading desktop from a collection of siloed applications into a Composable Trading Operating System. By utilizing OpenFin Workspaces as the delivery shell and a custom Registry as the control plane, we enable high-velocity feature delivery without compromising the stability of the Tier-1 trading environment.
1. Vision and Objectives
To establish a Marketplace of Trading Capabilities where business logic is decentralized (federated) but the user experience and operational risk are managed centrally.
 * Decouple Release Cycles: Allow the FX desk to deploy a pricer update at 10:00 AM without impacting the Rates desk’s blotter.
 * Contextual Intelligence: Use FDC3 to ensure that clicking a CUSIP in a research MFE instantly updates the "Order Entry" and "Risk" MFEs.
 * Zero-Config Discovery: Traders should find tools as easily as searching on a mobile device, with entitlements pre-filtered.
2. Core Platform Capabilities
MFE Registry (The Control Plane)
The "Source of Truth" for the ecosystem. It is a gRPC-based service storing the state of all deployed MFEs, their versions, and their interoperability contracts (FDC3 intents and context).
Storefront (The "App Store")
A React-based discovery portal embedded in OpenFin. It allows Product Managers to "shop" for components, view documentation, and see live previews of MFEs using mock data.
Workspace Provider
A specialized OpenFin service that intercepts Home (Search) and Store requests. It dynamically builds the user’s UI by querying the Registry based on the user's LDAP/Active Directory groups and specific entitlements.
3. User Journeys
Developer Registration Flow
 * Build: Developer pushes code to a domain-specific repository.
 * Validate: CI/CD runs a Platform Compatibility Test (e.g., checking for specific ag-grid versions and Tailwind-only CSS).
 * Register: A POST request is sent to the Registry with the MFE manifest (entry points, FDC3 config, and metadata).
 * Sandbox: The MFE is instantly available in the "Staging" Storefront for UAT and PM approval.
Product Manager Workflow Configuration
 * Browse: PM enters the Storefront and filters by "Yield Curve" or "Execution."
 * Compose: PM uses a drag-and-drop Workspace Builder to snap MFEs together into a logical layout.
 * Publish: PM saves the layout as a "Public Workspace" for the Swaps Desk, defining the default FDC3 channels for the components.
Trader Workspace Consumption
 * Search: Trader hits Alt + Space (OpenFin Home), types "Rates Dashboard."
 * Launch: OpenFin Home resolves the intent, fetches the PM-approved layout, and hydrates the MFEs.
 * Sync: As the trader filters for "USD Libor," all MFEs in that workspace update via FDC3 broadcast channels.
4. MFE Registration Model
The Registry captures a structured schema for every component to ensure automated discovery and safety.
| Field | Data Type | Requirement | Purpose |
|---|---|---|---|
| appId | String | Unique | Internal identifier (e.g., fx-options-volsurface). |
| manifestUrl | URL | Mandatory | The location of the app.json (OpenFin config). |
| fdc3Config | Object | Mandatory | Declares listensTo and publishes context types. |
| dataContracts | Array | Optional | AMPS topics or gRPC endpoints required. |
| entitlements | Array | Mandatory | Required AD Groups (e.g., APP_FICC_TRADER_PROD). |
| perfSLA | Object | Mandatory | Target "Time to Interactive" (TTI) and Max Memory. |
5. Governance and Approval Model
We utilize a Two-Tiered Gatekeeping system to maintain Tier-1 stability.
 * Automated (The "Synthetic Auditor"):
   * Bundle Analysis: Rejects MFEs exceeding 500KB initial load.
   * Security Scan: Checks for vulnerable NPM packages and hardcoded secrets.
   * Design Linting: Verifies Shadcn/Tailwind tokens match the bank's design system.
 * Human (The "Product Gate"):
   * UX Review: Platform Design Leads verify the MFE follows layout guidelines.
   * Risk Approval: Business Risk confirms data displayed meets regulatory transparency requirements.
6. Workspace Composition Model
Using the OpenFin Platform API, we treat layouts as "Stateful Snapshots."
 * View Injection: MFEs are loaded as OpenFin Views within a Window.
 * Interlink Logic: The Registry injects a "Bridge Script" that maps FDC3 intents specifically for that layout, preventing context leakage to other open windows.
 * Persistence: Layouts are stored in the Registry as JSON, allowing a trader to roam across terminals and see their exact MFE configuration.
7. Federation Model
The "Hub and Spoke" model ensures the platform team is not a bottleneck.
 * Platform Team (The Hub): Owns the OpenFin license, the Registry API, the Design System, and the "Shell" (Workspaces).
 * Domain Pods (The Spokes): FX, Rates, Credit, and Commodities teams each own their MFEs, their domain-aligned BFF (Backend for Frontend), and their data pipelines (e.g., Ignite/AMPS/Deephaven).
8. Operating Model
 * Platform Architect: Defines the "Contract" (FDC3, gRPC patterns, and MFE lifecycle).
 * Domain Lead: Accountable for the MFE business logic, performance, and uptime.
 * Product Manager: Curates workspaces and defines "Gold" templates for the desk.
 * SRE: Monitors the Registry and the "Health" of the OpenFin bus across the trading floor.
9. Implementation Examples
FX Options Desk
 * MFE: "Volatility Surface Visualizer."
 * Integration: Registered as an MFE that consumes a Deephaven stream. It publishes the fdc3.valuation context.
 * Onboarding: Developers register it; the PM adds it to the "FX Options Core" workspace.
Swaps Desk
 * Workflow: Creating a "Relative Value" workspace.
 * Composition: PM drags an AgGrid-powered Blotter (Rates Team) and a "Real-time Curve Chart" (Analytics Team).
 * Result: When a trader selects a 10Y Swap in the blotter, the chart MFE automatically re-plots the curve for that specific tenor via FDC3.
10. KPIs and Success Metrics
 * Time to Desktop: Measure from "Code Commit" to "Visible in Storefront" (Target: < 1 hour).
 * Component Reuse: Percentage of MFEs used in more than one desk's workspace.
 * Stability Index: Average "Time Between Crashes" per MFE using OpenFin's system-report.
 * Adoption Rate: Percentage of traders using custom-configured workspaces vs. default layouts.
11. Risks and Mitigation Strategies
> Risk: Data Silos leading to inconsistent pricing across MFEs.
> Mitigation: Enforce a "Standard Data Catalog" in the Registry; MFEs are restricted to authorized gRPC/AMPS streams.
> 
> Risk: Performance degradation (Memory Leaks) in a long-running OpenFin process.
> Mitigation: Implement "Lazy Hydration"—MFEs in background tabs are throttled or hibernated until focused.
> 
> Risk: FDC3 Version Bloat (Incompatibility between older and newer MFEs).
> Mitigation: Use a central Interop Broker within the Control Plane to map legacy intents to new FDC3 standards in real-time.
> 
Would you like me to provide a sample TypeScript manifest definition for the MFE Registry or a gRPC service definition for the Registration API?


--------

# Micro Frontend (MFE) Registry Storefront Approach  
**FICC Trading Desktop Ecosystem**  
**Built on OpenFin Desktop + OpenFin Workspaces**  
**Tier-1 Investment Bank – Enterprise Architecture**

## 1. Vision and Objectives

**Vision**  
A single, governed storefront where any FICC product team can register independently deployable MFEs that instantly become discoverable, composable, and interoperable inside trader workspaces — while the Platform team retains full control over security, latency, entitlements, and regulatory compliance.

**Objectives**  
- Federate MFE ownership to 12+ product squads (FX, Rates, Credit, Commodities, Swaps) without creating 12+ siloed desktops.  
- Reduce new capability onboarding from 8–12 weeks to <5 business days.  
- Guarantee <50 ms FDC3 intent latency and <10 ms data-stream latency inside any workspace.  
- Enforce bank-wide design system (AgGrid Enterprise + Shadcn/Tailwind + OpenFin styling tokens) at registration time.  
- Maintain full audit trail for every MFE version deployed to production (MiFID II / SEC Reg SCI requirement).  
- Enable traders to self-compose workspaces using only approved, entitled MFEs.

## 2. Core Platform Capabilities

### 2.1 MFE Storefront (Trader-facing)
- OpenFin Application: `ficc-storefront-v2` (single manifest).  
- Catalog UI with faceted search (asset-class, workflow, desk, tags).  
- “Add to Workspace” drag-and-drop directly into OpenFin Workspace Layout.  
- Live preview pane showing FDC3 intents supported.  
- Entitlement-gated (via OpenFin Runtime permissions + internal LDAP group check).

### 2.2 MFE Registry (Control Plane – single source of truth)
- Backend: Go microservice + PostgreSQL + Redis cache (sub-10 ms reads).  
- REST + gRPC API protected by mTLS + JWT (bank IAM).  
- Stores immutable JSON manifests (OpenFin app.json compatible).  
- Event stream (Kafka) for every registration/approval/version change → audit log + notification.

### 2.3 Governance Control Plane
- Automated CI/CD pipeline hook (GitHub Actions + OpenFin CLI).  
- Runtime validation service (WebAssembly) that spins up MFE in isolated OpenFin container and runs:  
  - Design-system compliance scan (Tailwind class whitelist + AgGrid theme check).  
  - Performance SLA test (CPU < 15 %, memory < 120 MB, FDC3 round-trip < 50 ms).  
  - Security scan (dependency CVE + OpenFin sandbox escape check).

## 3. User Journeys

### 3.1 Developer Registration Flow (5 steps, <30 min)
1. Squad pushes MFE to internal GitHub (monorepo or independent repo).  
2. CI generates OpenFin manifest + FDC3 context map + data-contract YAML.  
3. Developer opens `https://registry.ficc.bank/register` → auto-fills from GitHub.  
4. Submits registration → automated governance pipeline runs (see §5).  
5. On approval → MFE appears in Storefront within 60 seconds (Redis pub/sub).

### 3.2 Product Manager Workflow Configuration Flow
1. PM logs into `workflow-studio.ficc.bank` (low-code OpenFin app).  
2. Drags registered MFEs from Storefront catalog into canvas.  
3. Defines FDC3 intent chains (e.g., “ViewTrade” → “PriceBlotter” → “TradeTicket”).  
4. Saves as “Gold Workflow” template with versioned JSON layout.  
5. Publishes to OpenFin Workspace Catalog → auto-deployed to all entitled traders.

### 3.3 Trader Workspace Consumption Flow
1. Trader opens OpenFin Desktop → launches Storefront.  
2. Searches “FX Option Volatility Surface” → clicks “Add to Current Workspace”.  
3. MFE snaps into layout (OpenFin Workspace API `addApplication`).  
4. Trader drags, resizes, snaps with other MFEs; FDC3 context automatically flows.  
5. Saves workspace → persisted in OpenFin Workspace Server with user ID + entitlement snapshot.

## 4. MFE Registration Model (JSON Schema)

```json
{
  "mfeId": "fx-options-vol-surface-v2",
  "version": "2.3.1",
  "ownerSquad": "FX-Options",
  "manifestUrl": "https://artifactory.bank/fx-options/vol-surface/2.3.1/app.json",
  "fdc3": {
    "intents": ["ViewInstrument", "Trade", "PriceUpdate"],
    "contextTypes": ["fdc3.instrument", "fdc3.trade", "custom.ficc.price"]
  },
  "dataContracts": {
    "ingest": ["AMPS://fx.options.vol", "Ignite://price.cache"],
    "egress": ["gRPC://trade.booking.v2"]
  },
  "bff": "https://bff-fx.bank/internal",
  "designSystem": { "agGridTheme": "bank-dark", "tailwindPreset": "ficc-v1" },
  "performanceSLA": { "cpu": 12, "mem": 95, "fdc3LatencyMs": 42 },
  "entitlements": ["FX-OPT-DESK", "TRADER-LVL-3"],
  "complianceTags": ["MiFID-II-audit", "Reg-SCI"]
}

