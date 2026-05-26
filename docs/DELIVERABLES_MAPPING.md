# Deliverables Mapping

| Assignment Requirement | Implementation Location |
| --- | --- |
| Frontend source code | `frontend/` |
| Backend source code | `backend/` |
| Remote MCP tool server | `mcp-server/` |
| Public/synthetic dataset | `data/hr_policies/` |
| Prompt design note | `docs/PROMPT_AND_TOOLS.md` |
| Tool/function usage note | `docs/PROMPT_AND_TOOLS.md` |
| AI interaction improvements | citations, feedback, tool activity, insufficient-evidence behavior |
| Source code repository | monorepo structure in this workspace |
| README setup instructions | `README.md` |
| Full installation/run guide | `RUNBOOK.md` |
| LLM/API key configuration | `.env.example`, `RUNBOOK.md` |
| Dataset configuration | `data/hr_policies/`, ingestion script, `RUNBOOK.md` |
| Architecture overview | `docs/ARCHITECTURE.md` |
| Accuracy and limitations | `docs/RESPONSIBLE_AI.md`, `docs/ASSUMPTIONS_AND_LIMITATIONS.md` |
| Risks such as incorrect answers and over-reliance | `docs/RESPONSIBLE_AI.md` |
| Scale-out considerations | `docs/SCALE_OUT.md` |

## Constraint Mapping

| Constraint | How It Is Addressed |
| --- | --- |
| Runnable on standard developer hardware | local FastAPI, React, MCP server, Chroma, SQLite |
| No paid service required | Groq Free Plan default; no premium LLM required |
| Public/synthetic data only | synthetic HR documents under `data/hr_policies/` |
| Correctness and reliability over polish | citations, fallback retrieval, error states, tests, runbook |
| Assumptions documented | `docs/ASSUMPTIONS_AND_LIMITATIONS.md` |

