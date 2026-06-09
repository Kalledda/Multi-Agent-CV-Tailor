# Multi-Agent CV Tailoring Swarm Engine (LangGraph + Ollama)

An enterprise-grade portfolio application showcasing an **Evaluator-Optimizer agentic architecture** designed to match a candidate's master experience data cleanly against specific job descriptions under 60 seconds.

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

graph TD
    Start([START]) --> AgentA[Agent A: Master Resume Architect]
    AgentA --> AgentB[Agent B: Fact-Checking Auditor]
    AgentA --> AgentC[Agent C: Executive Copywriter]
    
    AgentB --> Router{Conditional Router Check}
    AgentC --> Router
    
    Router -- If Passed: False --> AgentA
    Router -- If Passed: True --> AgentD[Agent D: Predictive ATS Judge]
    AgentD --> End([END])

    classDef default fill:#1e1e2e,stroke:#cdd6f4,stroke-width:1px,color:#cdd6f4;
    classDef highlight fill:#f38ba8,stroke:#f38ba8,stroke-width:1px,color:#11111b;