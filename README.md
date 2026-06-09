# Multi-Agent CV Tailoring Swarm Engine (LangGraph + Ollama)

An enterprise-grade portfolio application showcasing an **Evaluator-Optimizer agentic architecture** designed to match a candidate's master experience data cleanly against specific job descriptions under 60 seconds.

## 🧠 System Architecture Diagram
The graph engine executes using a custom Directed Acyclic Graph (DAG) state layout:
--------------------------------------------------------------------------------------
[START] ──>  Agent A (Generator: CV & Cover Letter Creation)
                   │
                   ├──> Agent B (Auditor: Core Fact-Checking)
                   └──> Agent C (Stylist: Copywriting & Format)
                   │
         [Conditional Router Check]
          ├── If Discrepancies found ──> (Loop back to Agent A for repairs)
          └── If Quality Passed      ──> Agent D (ATS Scoring & Review) ──> [END]
--------------------------------------------------------------------------------------
## 🤖 Swarm Node Layout Matrix

| Agent Identity | Role | Target Objective | Execution Constraints |
| :--- | :--- | :--- | :--- |
| **Agent A** | Master Resume Architect | Draft tailored assets | Strict fallback verification mapping rules |
| **Agent B** | Fact-Checking Auditor | Intercept hallucinations | Cross-checks structural truth against raw Master CV |
| **Agent C** | Executive Copywriter | Language polish & format | Removes boilerplate AI phrasing patterns; controls layouts |
| **Agent D** | Predictive ATS Judge | Strategic final fit evaluation | Concise 3-sentence application recommendation + score index |

## 🛠️ Quickstart Local Setup Guide

### 1. Model Dependencies
Download and serve the optimal structural weights via Ollama:
```bash
ollama run gemma4:e2b
ollama run gemma4:e4b