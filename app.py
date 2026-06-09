"""
===================================================================
TABLE OF CONTENTS: app.py
===================================================================
1. STREAMLIT CONFIGURATION & DATA RECOVERY
2. PARAMETER SELECTION & DUAL COLUMN UI INPUTS
3. RUNTIME LANGGRAPH OVER-THE-AIR STREAMING LOOPS
4. TRACE INSTRUMENTATION VIA LANGCHAIN_CONTEXT
5. OUTPUT VIEW TABS & PERFORMANCE BENCHMARKING
===================================================================
"""

import os
import time
import streamlit as st
from graph_engine import app_graph
from langchain_core.tracers.context import collecting_tracers

# =================================================================
# 1. STREAMLIT CONFIGURATION & DATA RECOVERY
# =================================================================
st.set_page_config(page_title="Agentic CV Tailor Swarm", page_icon="💼", layout="wide")

st.title("💼 Enterprise Agentic CV Tailor Swarm")
st.write("Orchestrating concurrent local models via LangGraph state machine tracking engines.")

MASTER_CV_PATH = "master_cv.md"
if not os.path.exists(MASTER_CV_PATH):
    with open(MASTER_CV_PATH, "w", encoding="utf-8") as f:
        f.write("# Master CV File\n\n(Paste historic work experiences here.)")

with open(MASTER_CV_PATH, "r", encoding="utf-8") as f:
    master_cv_data = f.read()

# =================================================================
# 2. PARAMETER SELECTION & DUAL COLUMN UI INPUTS
# =================================================================
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📋 Input Parameters")
    with st.expander("📝 View / Edit Loaded Master CV", expanded=False):
        edited_master_cv = st.text_area("Master Profile Context", value=master_cv_data, height=250)
        if edited_master_cv != master_cv_data:
            with open(MASTER_CV_PATH, "w", encoding="utf-8") as f:
                f.write(edited_master_cv)
                
    job_description_input = st.text_area(
        "🎯 Target Job Description", 
        placeholder="Paste target job criteria here...",
        height=300
    )
    launch_swarm = st.button("Execute Tailor Swarm 🚀", type="primary", use_container_width=True)

with col_right:
    st.subheader("🤖 Swarm Engine Live Pipeline")
    status_msg = st.empty()
    progress_bar = st.empty()
    
    col_a, col_b = st.columns(2)
    col_c, col_d = st.columns(2)
    slot_a, slot_b = col_a.empty(), col_b.empty()
    slot_c, slot_d = col_c.empty(), col_d.empty()
    
    slot_a.info("🤖 **Agent A (Generator)**\n\n*Status:* 💤 Idle")
    slot_b.info("🛡️ **Agent B (Fact Checker)**\n\n*Status:* 💤 Idle")
    slot_c.info("🎨 **Agent C (Stylist)**\n\n*Status:* 💤 Idle")
    slot_d.info("⚖️ **Agent D (Judge)**\n\n*Status:* 💤 Idle")

# =================================================================
# 3. RUNTIME LANGGRAPH OVER-THE-AIR STREAMING LOOPS
# =================================================================
    if launch_swarm:
        if not job_description_input.strip():
            st.error("Please provide a valid target job specification.")
        else:
            st.session_state.update({"tailored_cv": "", "cover_letter": "", "history": [], "score": 0, "notes": "", "execution_time": 0.0, "langsmith_url": ""})

            initial_state = {
                "master_cv": edited_master_cv,
                "job_description": job_description_input,
                "conversation_history": [],
                "iterations": 0,
                "fact_check_feedback": "",
                "style_feedback": ""
            }
            
            start_time = time.time()
            
            try:
                status_msg.markdown("### ⚙️ Initializing Swarm Nodes...")
                progress_bar.progress(5)
                
                # =================================================================
                # 4. TRACE INSTRUMENTATION VIA LANGCHAIN_CONTEXT
                # =================================================================
                # Intercepts graph calls to surface LangSmith RunIDs directly into the UI dashboard
                with collecting_tracers() as tracers:
                    for event in app_graph.stream(initial_state):
                        node_name = list(event.keys())[0]
                        node_data = event[node_name]
                        
                        if "conversation_history" in node_data:
                            st.session_state["history"].extend(node_data["conversation_history"])
                        
                        if node_name == "agent_a_generator":
                            status_msg.markdown("### ⏳ Architecting Tailored Content Assets...")
                            progress_bar.progress(25)
                            slot_a.warning("🤖 **Agent A**\n\n*Status:* 🧠 Generating...")
                            if "tailored_cv" in node_data: st.session_state["tailored_cv"] = node_data["tailored_cv"]
                            if "cover_letter" in node_data: st.session_state["cover_letter"] = node_data["cover_letter"]
                            
                        elif node_name == "agent_b_fact_checker":
                            status_msg.markdown("### ⏳ Executing Counter-Hallucination Audit...")
                            progress_bar.progress(50)
                            slot_b.warning("🛡️ **Agent B**\n\n*Status:* 🔍 Verification checking...")
                            
                        elif node_name == "agent_c_stylist":
                            progress_bar.progress(70)
                            slot_c.warning("🎨 **Agent C**\n\n*Status:* ✍️ Refining syntax flow...")
                            
                        elif node_name == "agent_d_judge":
                            status_msg.markdown("### ⏳ Calculating Predictive Match Suitability Index...")
                            progress_bar.progress(90)
                            slot_d.warning("⚖️ **Agent D**\n\n*Status:* 📊 Compiling Score metrics...")
                            if "final_score" in node_data: st.session_state["score"] = node_data["final_score"]
                            if "scoring_notes" in node_data: st.session_state["notes"] = node_data["scoring_notes"]

                    # Extract the unique execution trace ID for portfolio showcasing
                    if tracers and hasattr(tracers[0], "latest_run") and tracers[0].latest_run:
                        run_id = tracers[0].latest_run.id
                        st.session_state["langsmith_url"] = f"https://smith.langchain.com/public/{run_id}/d"

                st.session_state["execution_time"] = round(time.time() - start_time, 2)
                st.rerun()
                
            except Exception as e:
                status_msg.error("System pipeline fault identified.")
                st.error(f"Execution Error Details: {e}")

# =================================================================
# 5. OUTPUT VIEW TABS & PERFORMANCE BENCHMARKING
# =================================================================
if "tailored_cv" in st.session_state and st.session_state["tailored_cv"] != "" and launch_swarm is False:
    st.markdown("---")
    metric_score = st.session_state["score"]
    score_color = "green" if metric_score >= 80 else "orange" if metric_score >= 60 else "red"
    
    st.markdown(f"## 🎯 System Interview Fit Index: :{score_color}[**{metric_score} / 100**]")
    
    tab_cv, tab_cl, tab_logs = st.tabs(["📄 Optimized Tailored CV", "✉️ Generated Cover Letter", "🧠 Swarm Conversation Dossier"])
    
    with tab_cv:
        cv_text = st.text_area("Edit structural details directly:", value=st.session_state["tailored_cv"], height=400, key="cv_editor_area")
        st.download_button("Download CV Text Asset", cv_text, file_name="Tailored_CV.md")
        
    with tab_cl:
        cl_text = st.text_area("Edit body text details directly:", value=st.session_state["cover_letter"], height=400, key="cl_editor_area")
        st.download_button("Download Cover Letter Asset", cl_text, file_name="Cover_Letter.txt")
        
    with tab_logs:
        if st.session_state.get("langsmith_url"):
            st.success(f"🔗 **Portfolio Reviewers Live Deep Trace:** [View Complete LangSmith Graph Execution Trace]({st.session_state['langsmith_url']})")
            
        with st.chat_message("assistant", avatar="⚖️"):
            st.markdown(f"### **Agent D (Judge) Snapshot Analysis**")
            st.info(st.session_state['notes'])
            
        for idx, turn in enumerate(st.session_state.get("history", []), 1):
            agent_label = turn['agent']
            avatar_emoji = "🛡️" if "Fact Checker" in agent_label else "🎨" if "Stylist" in agent_label else "✍️"
            with st.chat_message("user" if "Generator" in agent_label else "assistant", avatar=avatar_emoji):
                st.markdown(f"#### **{agent_label}**")
                st.markdown(turn['content'])
        
        st.markdown("---")
        st.metric(label="⏱️ Total Swarm Execution Latency", value=f"{st.session_state['execution_time']} seconds", delta="Target: < 60s")