# Responsible AI And Governance

Enterprise Knowledge Copilot is a source-grounded policy assistant proof of concept. It is intended to help users locate and summarize information from a small synthetic HR policy corpus, not to make authoritative employment or benefits decisions.

## Intended Use

| Area | Position |
| --- | --- |
| Primary use | Answer questions about the included synthetic HR policy documents. |
| User role | Employee or evaluator exploring policy information. |
| Decision authority | Informational only; cited source excerpts should be reviewed. |
| Data scope | Synthetic Markdown documents under `data/hr_policies/`. |

## Controls Implemented

- Retrieval-grounded answer path through a remote MCP knowledge server.
- Source citations displayed in the UI for supported answers.
- Configurable relevance threshold for citation eligibility.
- Insufficient-evidence behavior when retrieval does not provide usable support.
- System prompt instruction not to invent policy details.
- Local audit events for chat completion and failures.
- Feedback capture for answer quality review.

## Data Handling

The project uses synthetic documents and local generated storage. Runtime data is written under `storage/` and ignored by Git.

| Data | Location | Notes |
| --- | --- | --- |
| Source policy corpus | `data/hr_policies/` | Synthetic Markdown documents committed to the repo. |
| Conversation history | `storage/copilot.db` | Local SQLite runtime data. |
| Feedback | `storage/copilot.db`, `storage/mcp_feedback.db` | Local answer ratings. |
| Embeddings/index | `storage/chroma/` | Generated from the synthetic corpus. |
| Embedding model cache | `storage/huggingface/` | Downloaded dependency cache. |

## Known Risks

- The LLM may misread or over-compress a retrieved excerpt.
- Vector retrieval may miss the best source chunk.
- A nearest-neighbor result can be semantically weak; the relevance threshold reduces but does not eliminate this risk.
- Users may over-trust generated summaries instead of checking citations.
- Free hosted LLM providers can introduce rate limits or transient failures.
- The synthetic corpus is smaller and cleaner than a real enterprise knowledge base.

## User-Facing Mitigations

- The UI shows sources directly beneath supported answers.
- Unsupported questions are expected to receive an insufficient-evidence response.
- The activity panel shows when retrieval tools are called.
- Feedback buttons allow users to flag weak answers.

## Production Governance Gaps

Before production use, this system would need:

- SSO and user identity propagation.
- Role-based and document-level authorization.
- Approved source ingestion workflows and document versioning.
- Data retention policy and deletion workflows.
- Provider risk review for any hosted LLM.
- Logging, monitoring, tracing, alerting, and incident response.
- Evaluation suites for retrieval accuracy, citation support, and hallucination behavior.
- Human owner review for policy-sensitive answer templates.

## Review Guidance

When evaluating answer quality, check:

- Whether the cited excerpts actually support the generated answer.
- Whether unsupported questions avoid unsupported claims.
- Whether the selected sources come from the expected policy document.
- Whether feedback and audit events are recorded after completion.
