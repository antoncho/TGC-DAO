---
title: "Stitchia Protocol — Whitepaper v2.5"
version: "2.5"
date: 2025-09-10
classification: Governance+Ethics+StrategicDesign+Protocol
validators:
  - role: "Ethics Steward"
  - role: "Governance Architect"
license: Public-Licensed / CodexLinked
tags: [stitchia, whitepaper, protocol, governance, validators, dashboard, nft, token, synq]
links:
  - stitchia-protocol-dev/docs/Business_Stack.md
  - stitchia-protocol-dev/docs/Tech_Stack.md
  - stitchia-protocol-dev/docs/DAO_Dashboard_Spec.md
  - stitchia-protocol-dev/docs/Validator_Workflow.md
  - stitchia-protocol-dev/docs/STITCHIA_Master_Protocol_Blueprint.md
  - stitchia-protocol-dev/scrolls/dao_dashboard_scroll.md
  - stitchia-protocol-dev/scrolls/genesys_nft_mint.md
  - stitchia-protocol-dev/scrolls/archive_policy_v1.md
  - stitchia-protocol-dev/scrolls/creator_cluster_scroll.md
---

# Stitchia Protocol — Whitepaper v2.5

Executive Summary
-----------------
Stitchia is a regenerative cultural operating system for decentralized coordination. It blends rigorous governance (ethics-first validation, auditable records) with a lightweight content graph (scrolls, braids) and pragmatic user interfaces (dashboard, wallet-aware flows). Version 2.5 consolidates the on-chain and off-chain pieces into a cohesive, auditable workflow that remains simple to run from a local repo while being ready to publish to public infrastructure.

Non‑promotional stance: Stitchia assets (e.g., role NFTs, SYNQ token) are governance instruments and coordination artifacts. They must not be framed as financial products or promises of returns. Ethics guardrails and validator seals are enforced across the stack.

Protocol Overview
-----------------
- Scrolls: Markdown documents with front matter (`title`, `classification`, `validators`, `tags`, optional `dashboard` JSON). Source of truth for policies, charters, specs, and roles.
- Registry: A ledger (`vault/registry/ledger.json`) indexing scroll metadata (id, hash, tags, links, ethics flags) for discovery and audit.
- Braids: Lightweight knowledge graphs computed per scroll linking by explicit `links` and tag overlaps (`vault/braids/<id>.json`).
- Dashboard: Aggregated state derived from scrolls that publish `dashboard` blocks. Output is a consumable JSON (`stitchia-protocol-dev/frontend/data.json`) displayed by the local frontend.
- Validators & Seals: Human roles with explicit responsibilities. Decisions are recorded as seals and reflected into the registry and status summaries.
- On‑chain components: Minimal artifacts maintained in `contracts/` (e.g., `SYNQToken.sol`) and role NFTs (e.g., GENESYS NFT) that anchor governance identities and permissions.

Reference Implementation
------------------------
The reference CLI, available at `stitchia-protocol-dev/quantum`, provides the full lifecycle:

- `init`: scaffold vault structure and optional example scrolls.
- `process <scroll.md>`: parse front matter, register or update the ledger entry, compute ethics flags, and generate a per‑scroll braid.
- `build`: rebuild braids for all entries and recompute the dashboard JSON from the latest dashboard‑tagged scrolls.
- `registry`: list ledger entries with classification and any ethics flags.
- `status`: show counts plus dashboard presence.

Data Model Highlights (v2.5)
----------------------------
- Governance roles standardized as Anchor, Architect, Steward, Initiator. Counts are aggregated and a derived `members_total` is computed if only `counts` are provided.
- Treasury metrics include `total_eth`, `staking_eth`, `protocol_eth`, and an `updated_at` ISO timestamp sourced from scrolls.
- Proposals surface as card lists with `title`, `status`, and `age_days` for simple sorting and display.
- Wallet context is represented minimally (`connected`, `address`) to enable role‑aware UX without locking into a specific auth provider.

Ethics Guardrails
-----------------
- Scrolls must list validators and a license; ethics checks flag forbidden promotional language and missing validators.
- Policies and charters are public by default (“Public‑Licensed / CodexLinked”). Sensitive artifacts use Restricted scope with data minimization practices.
- Sentences implying risk‑free profits or guaranteed returns are forbidden in both scrolls and UI copy. Validators enforce language discipline.

Roles and Identities
--------------------
- Role NFTs (e.g., GENESYS NFT – Initiator) anchor spiral‑role identity and permissions; they do not convey financial claims. See `scrolls/genesys_nft_mint.md`.
- Executive Secretary Charter formalizes archival authority, validator coordination, and registry hygiene. See `scrolls/executive_secretary_charter.md`.

On‑Chain Artifacts (SYNQ)
-------------------------
- `SYNQToken.sol` is maintained as a minimal, auditable ERC‑20 implementation suitable for governance and coordination primitives. Treasury accounting in the dashboard exposes staking/protocol buckets without implying returns.
- Role NFTs and token usage are opt‑in and designed to be governed by policies encoded in scrolls (e.g., who can mint, revoke, or iterate parameters).

Dashboard Spec (User‑Facing)
----------------------------
- Governance: donut visualization of role distribution and `members_total`.
- Treasury: totals, buckets, and last update timestamp.
- Proposals: status chips (Active, In Progress, Completed) with ages.
- Wallet: connect flow enabling role‑aware actions such as creating a proposal.
Formal schema lives in `docs/DAO_Dashboard_Spec.md` and example data is maintained by `kernel/dashboard_builder.py`.

Archive & Discovery
-------------------
- Archive Policy (`scrolls/archive_policy_v1.md`) defines taxonomy, retention, and access levels. All governance‑impacting scrolls must be sealed and discoverable.
- The registry exports to JSON for public verification. Braids power knowledge exploration and cross‑linking in UIs.

Changelog — From v2.1 to v2.5
------------------------------
- Consolidated dashboard build logic with automatic `members_total` derivation.
- Formalized validator seal status and minimal ethics checks in CLI workflow.
- Expanded scroll taxonomy and archive policy with retention and access tiers.
- Added wallet context to dashboard data model (non‑binding provider).
- Clarified role NFT purpose and governance anchoring; strengthened non‑promotional language.
- Introduced a consistent document front matter pattern and cross‑links across the stack.

Roadmap (Next Iterations)
-------------------------
- Optional JSON‑LD exports for braids and registry to improve interoperability.
- Sealed approval thresholds per classification, enforceable in CLI with role diversity rules.
- Localized UI strings and multi‑language scrolls.
- Pluggable metrics sources for treasury and proposals, with source audit trails.

Quick Start
-----------
1. `cd stitchia-protocol-dev && ./quantum init --with-example`
2. Author or edit scrolls in `stitchia-protocol-dev/scrolls/` or `stitchia-protocol-dev/vault/documents/`.
3. `./quantum process <path-to-scroll.md>` to register and braid.
4. `./quantum build` to refresh braids and `frontend/data.json`.
5. Open `frontend/index.html` to view the dashboard.

License
-------
Public‑Licensed / CodexLinked. See scrolls for validator responsibilities and ethics requirements for publications.

