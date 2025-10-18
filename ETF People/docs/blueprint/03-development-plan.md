# Development Plan & Phasing

Execution roadmap structured for investor clarity. Timelines assume team mobilisation upon funding.

## Timeline Summary
| Phase | Duration | Primary Goal | Exit Criteria | Ownership |
|-------|----------|--------------|---------------|-----------|
| 0. Discovery & Strategy | 4–6 weeks | Validate demand, scope regulatory envelope | Green-lit requirements & investment memo | ETF People (lead), TGC (support) |
| 1. Concept & Experience | 6–8 weeks | Design user journeys, architecture, content plan | Approved UX, architecture, and partner brief | TGC (tech lead), ETF People (content lead) |
| 2. Build & Integration | 12–16 weeks | Ship portal + launchpad MVPs, wire integrations | End-to-end staging environment, security sign-off | TGC (delivery), ETF People (QA & GTM prep) |
| 3. Pilot & Rollout | 8–10 weeks | Run beta, finalise compliance, launch GTM | Live product with reference clients + GTM kit | ETF People (client ops), TGC (support) |
| 4. Optimisation | Ongoing | Iterate, scale, expand jurisdictions | Quarterly roadmap & growth metrics dashboard | Joint PMO |

## Phase Detail

### Phase 0 — Discovery & Strategy
- Interview asset managers, regulators, custodians (target: 10+ sessions) using structured questionnaires covering compliance comfort, tech expectations, and success metrics.
- Map competitive/tokenization landscape, categorising offerings by issuance model, custody approach, and interoperability capabilities.
- Conduct regulatory analysis across priority jurisdictions (UK, EU, GCC, APAC); log licensing requirements, sandbox opportunities, and disclosure templates.
- Produce go-to-market hypothesis, pricing assumptions, and business model canvas for ETF People.
- TGC drafts preliminary technical options (permissioned vs. public infrastructure, rollup choices, access models) informed by findings.
- Deliverables: Discovery report, regulator engagement plan, investment memo, and initial risk register.

### Phase 1 — Concept & Experience Design
- Translate findings into detailed product requirements (MVP vs. full platform) covering user journeys, data requirements, and compliance checkpoints.
- Produce wireframes, UI prototypes, and content architecture for the knowledge portal and launchpad dashboards.
- Draft reference technical architecture: microservices map, smart contract modules, integration interfaces, security layers, observability stack.
- Align with shortlisted partners through workshop series (tokenization platform, custody, compliance automation) to validate integration feasibility.
- Create success metrics dashboards and analytics instrumentation plans.
- Deliverables: Product requirement document, UX prototype, architecture blueprint, data governance charter, and partnership evaluation matrix.

### Phase 2 — Build & Integration
- Implement frontend/backend for portal, launchpad, and admin tooling using modular, API-first principles; include role-based access control and audit logging from day one.
- Develop and test smart contract templates adhering to ERC-1400/1410 standards with pluggable compliance hooks.
- Build integration connectors for tokenization APIs, KYC/AML providers, custodial services, market data feeds, and interoperability modules (bridges/appchains).
- Establish CI/CD pipelines, infrastructure-as-code templates, and observability dashboards (metrics, traces, logs).
- Conduct threat modeling, security reviews, smart contract audits, and compliance walkthroughs with external advisors.
- Deliverables: Functioning staging environment, documented APIs, integration playbooks, security audit reports, and runbooks.

### Phase 3 — Pilot & Rollout
- Onboard a controlled cohort of asset managers (2–3 lighthouse accounts) with clear success metrics and support SLAs.
- Run structured pilot sprints: onboarding workshop, build sprint, issuance simulation, and live reporting validation.
- Capture qualitative + quantitative feedback, reprioritise backlog, and finalise compliance documentation (disclosure packs, operations manuals).
- Produce GTM assets (whitepapers, demo videos, ROI calculators, pricing sheets) and enablement kits for sales/partnership teams.
- Execute interoperability pilots with chosen bridge/providers; document custody playbooks and settlement procedures.
- Deliverables: Pilot case studies, updated product + compliance docs, GTM toolkit, signed reference agreements.

### Phase 4 — Post-Launch Optimisation
- Monitor product analytics, user funnels, conversion metrics, and platform health (latency, uptime, error budgets).
- Implement feature flags and experimentation frameworks to rollout enhancements safely.
- Expand into additional jurisdictions/asset classes based on regulatory clearance; maintain compliance change logs and update policy packs.
- Introduce monetisation experiments (tiered subscriptions, performance fees, co-build packages) informed by pilot learnings.
- Maintain ongoing security, compliance, and governance cadences—quarterly audits, incident response drills, and data privacy assessments.
- Deliverables: Quarterly roadmap, OKR review packs, compliance attestations, customer success scorecards, and partner performance reports.

## Prototype Track Overlay
- Phases 0–3 executed with reduced scope (portal essentials, launchpad concept flows, limited integrations) to deliver a live proof to investors and anchor clients.
- Prioritise no-code/low-code components and manual compliance support where automation is not yet justified.
- Define clear upgrade paths so prototype assets transition smoothly into full platform builds.

> Dependencies and milestones across phases align with the cost model in `04-cost-estimates.md`.
