"""
===================================================================
TABLE OF CONTENTS: graph_engine.py
===================================================================
1. LANGSMITH TELEMETRY & ENV CONFIGURATION
2. COMPACT DEFAULT PROMPT MANIFEST
3. LANGGRAPH TYPE & STATE INITIALIZATION
4. ACTIVE AGENT NODE LOGIC (A, B, C, D)
5. EVALUATOR-OPTIMIZER CONDITIONAL ROUTER
6. STATEGRAPH COMPILATION ENTRYPOINT
===================================================================
"""

import os
import re
import operator
from pydantic import BaseModel, Field
from typing import Annotated, List, Dict, Any, Literal, TypedDict
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
from langgraph.graph import StateGraph, START, END

# =================================================================
# 1. LANGSMITH TELEMETRY & ENV CONFIGURATION
# =================================================================
# LangGraph natively pushes trace telemetry arrays directly if these variables exist
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "CV-Tailor-Swarm"
# Hardcode or load via local .env variable file if required:
# os.environ["LANGCHAIN_API_KEY"] = "ls__your_key_here"

# =================================================================
# 2. COMPACT DEFAULT PROMPT MANIFEST
# =================================================================
PROMPT_DIR = r"C:\Users\fredr\OneDrive\Desktop\Portfolio\Projects\Agentic CV Tailor\agent_prompts"
os.makedirs(PROMPT_DIR, exist_ok=True)

DEFAULT_PROMPTS = {
    "agent_a_prompt.txt": (
        "You are Agent A: The Master Resume Architect. Adapt the candidate's Master CV and draft a pristine Cover Letter matching the target Job Description.\n"
        "CRITICAL RULES:\n"
        "1. Extract relevant matching skills from the Master CV only.\n"
        "2. Do not chat or add introductory text. Return ONLY the tailored markdown CV, a line separator '### COVER LETTER', and the cover letter text.\n\n"
        "--- MASTER CV ---\n{master_cv}\n\n"
        "--- FACT-CHECK FEEDBACK ---\n{fact_check_feedback}\n\n"
        "--- STYLE FEEDBACK ---\n{style_feedback}"
    ),
    "agent_b_prompt.txt": (
        "You are Agent B: The Fact-Checking Auditor. Compare the Generated CV against the Master CV.\n"
        "Identify any fabricated roles or unverified tech stacks. Do not write a long essay.\n"
        "Format your output EXACTLY like this:\n"
        "Passed: [true/false]\n"
        "Discrepancies: [List items or write 'None']\n\n"
        "--- MASTER CV ---\n{master_cv}"
    ),
    "agent_c_prompt.txt": (
        "You are Agent C: The Executive Copywriter. Review the draft for style and AI syntax artifacts.\n"
        "Ensure clear profile summaries, clean bulleted lists, and an education section. Do not use bold or italics.\n"
        "Format your output EXACTLY like this:\n"
        "Passed: [true/false]\n"
        "Critique: [List style adjustments needed or write 'None']"
    ),
    "agent_d_prompt.txt": (
        "You are Agent D: The Predictive ATS Judge. Analyze the final pack against the job criteria.\n"
        "Be extremely brief. Output EXACTLY this format and nothing else:\n\n"
        "SCORE: [0-100]\n"
        "DECISION: [Apply / Do Not Apply]\n"
        "CRITICAL MISSING: [List maximum 3 critical missing requirements, or 'None']\n"
        "SUMMARY REASONING: [Provide a concise, candid structural breakdown. Maximum of 3 sentences explaining your application decision directly to the candidate.]"
    )
}

def get_agent_prompt(filename: str) -> str:
    """Reads prompt configuration files from the disk directory."""
    file_path = os.path.join(PROMPT_DIR, filename)
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(DEFAULT_PROMPTS[filename])
        return DEFAULT_PROMPTS[filename]
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

# =================================================================
# 3. LANGGRAPH TYPE & STATE INITIALIZATION
# =================================================================
class AgentState(TypedDict):
    master_cv: str
    job_description: str
    tailored_cv: str
    cover_letter: str
    fact_check_feedback: str
    style_feedback: str
    iterations: int
    conversation_history: Annotated[List[Dict[str, str]], operator.add]
    final_score: int
    scoring_notes: str

# Read the environment variable passed by Docker Compose, fallback to standard localhost
OLLAMA_HOST = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

# Initialize local Gemma models via Ollama pointing to the dynamic host
llm_creative = Ollama(model="gemma4:e2b", base_url=OLLAMA_HOST, temperature=0.5) 
llm_analytical = Ollama(model="gemma4:e4b", base_url=OLLAMA_HOST, temperature=0.1)

# =================================================================
# 4. ACTIVE AGENT NODE LOGIC (A, B, C, D)
# =================================================================
def agent_a_generator(state: AgentState) -> Dict[str, Any]:
    """Generates tailored CV components using historical contexts and feedback loop adjustments."""
    iterations = state.get("iterations", 0) + 1
    system_prompt = get_agent_prompt("agent_a_prompt.txt")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Generate a tailored CV and Cover Letter matching this specification:\n\n{job_description}")
    ])
    
    response = (prompt | llm_creative).invoke({
        "master_cv": state["master_cv"],
        "job_description": state["job_description"],
        "fact_check_feedback": state.get("fact_check_feedback", "None. First attempt."),
        "style_feedback": state.get("style_feedback", "None. First attempt.")
    })
    
    cv_part = response.split("### COVER LETTER")[0] if "### COVER LETTER" in response else response
    cl_part = response.split("### COVER LETTER")[-1] if "### COVER LETTER" in response else "Cover letter generation pending revision."

    return {
        "tailored_cv": cv_part.strip(),
        "cover_letter": cl_part.strip(),
        "iterations": iterations,
        "conversation_history": [{"agent": f"Agent A (Generator) - Iteration {iterations}", "content": response}]
    }

def agent_b_fact_checker(state: AgentState) -> Dict[str, Any]:
    """Audits the generated resume data string against valid Master entries to prevent hallucination."""
    system_prompt = get_agent_prompt("agent_b_prompt.txt")
    iterations = state.get("iterations", 1)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Audit this generated Tailored CV:\n\n{tailored_cv}")
    ])
    
    response = (prompt | llm_analytical).invoke({"master_cv": state["master_cv"], "tailored_cv": state["tailored_cv"]})
    passed = "passed: true" in response.lower()
    feedback_str = f"Passed: {passed}. Auditor Analysis:\n{response}"
    
    return {
        "fact_check_feedback": response,
        "conversation_history": [{"agent": f"Agent B (Fact Checker) - Iteration {iterations}", "content": feedback_str}]
    }

def agent_c_stylist(state: AgentState) -> Dict[str, Any]:
    """Ensures stylistic formatting guidelines conform to human-written standards."""
    system_prompt = get_agent_prompt("agent_c_prompt.txt")
    iterations = state.get("iterations", 1)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Review this draft for style excellence:\n\nCV:\n{tailored_cv}\n\nCover Letter:\n{cover_letter}")
    ])
    
    response = (prompt | llm_creative).invoke({"tailored_cv": state["tailored_cv"], "cover_letter": state["cover_letter"]})
    passed = "passed: true" in response.lower()
    feedback_str = f"Passed: {passed}. Stylist Analysis:\n{response}"
    
    return {
        "style_feedback": response,
        "conversation_history": [{"agent": f"Agent C (Stylist) - Iteration {iterations}", "content": feedback_str}]
    }

def agent_d_judge(state: AgentState) -> Dict[str, Any]:
    """Evaluates final structural data packets to determine hiring suitability."""
    system_prompt = get_agent_prompt("agent_d_prompt.txt")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Provide final matrix validation:\n\nJob description:\n{job_description}\n\nFinal CV Pack:\n{tailored_cv}")
    ])
    
    response = (prompt | llm_analytical).invoke({"job_description": state["job_description"], "tailored_cv": state["tailored_cv"]})
    
    score_match = re.search(r'SCORE:\s*([0-9]{1,3})', response, re.IGNORECASE)
    score = int(score_match.group(1)) if score_match else 85
    if score > 100: score = 100

    return {
        "final_score": score,
        "scoring_notes": response
    }

# =================================================================
# 5. EVALUATOR-OPTIMIZER CONDITIONAL ROUTER
# =================================================================
def route_feedback(state: AgentState) -> Literal["agent_a_generator", "agent_d_judge"]:
    """Routes execution based on verification flags or step loops limits."""
    if state.get("iterations", 0) >= 3:
        return "agent_d_judge"
        
    fc = state.get("fact_check_feedback", "").lower()
    sf = state.get("style_feedback", "").lower()
    
    if "passed: false" in fc or "passed: false" in sf:
        return "agent_a_generator"
        
    return "agent_d_judge"

# =================================================================
# 6. STATEGRAPH COMPILATION ENTRYPOINT
# =================================================================
def build_cv_swarm_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("agent_a_generator", agent_a_generator)
    workflow.add_node("agent_b_fact_checker", agent_b_fact_checker)
    workflow.add_node("agent_c_stylist", agent_c_stylist)
    workflow.add_node("agent_d_judge", agent_d_judge)
    
    workflow.add_edge(START, "agent_a_generator")
    workflow.add_edge("agent_a_generator", "agent_b_fact_checker")
    workflow.add_edge("agent_a_generator", "agent_c_stylist")
    
    workflow.add_conditional_edges(
        "agent_b_fact_checker", 
        route_feedback,
        {"agent_a_generator": "agent_a_generator", "agent_d_judge": "agent_d_judge"}
    )
    
    workflow.add_edge("agent_d_judge", END)
    return workflow.compile()

app_graph = build_cv_swarm_graph()