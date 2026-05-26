# Responsible AI And Governance

## Intended Use

Enterprise Knowledge Copilot helps employees find information in a small synthetic HR policy knowledge base. It is a POC, not an authoritative HR decision system.

## Accuracy Controls

- Answers are grounded in retrieved MCP policy chunks.
- Citations are shown to users for verification.
- Unsupported questions should receive an insufficient-evidence response.
- The system prompt explicitly prohibits inventing policy details.

## Known Risks

- The LLM may summarize retrieved text incorrectly.
- The retriever may miss relevant chunks.
- Users may over-rely on generated answers.
- Free hosted LLM rate limits can interrupt usage.
- Synthetic documents are smaller and cleaner than real enterprise policy stores.

## Feedback Handling

Users can mark answers as helpful or needing work. Feedback is stored locally and also sent to the MCP feedback tool when available.

## Auditability

The gateway stores message history, citations, tool-call completion metadata, latency, and feedback. A production system would add user identity, access-control decisions, and immutable audit logging.

## Data Governance

Only synthetic HR documents are included. No protected, private, or company-confidential data is required.

