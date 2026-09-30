import os
import sys
from pathlib import Path

# Ensure project root directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import json
from src.engine import VeridianITEngine
from src.schemas import Employee
from src import tools

st.set_page_config(
    page_title="Veridian IT Support Agent",
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS styling for premium look & feel
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(120deg, #1E88E5, #42A5F5, #7E57C2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #90A4AE;
        margin-bottom: 1.5rem;
    }
    .status-badge-APPROVED {
        background-color: #2e7d32;
        color: #ffffff;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: bold;
    }
    .status-badge-RESOLVE {
        background-color: #0288d1;
        color: #ffffff;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: bold;
    }
    .status-badge-ROUTE {
        background-color: #ed6c02;
        color: #ffffff;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: bold;
    }
    .status-badge-CLARIFY {
        background-color: #9c27b0;
        color: #ffffff;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: bold;
    }
    .status-badge-UNALLOWABLE {
        background-color: #d32f2f;
        color: #ffffff;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: bold;
    }
    .pass-tag {
        background-color: #1b5e20;
        color: #a5d6a7;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def get_engine():
    data_path = ROOT_DIR / "data" / "data_pack.json"
    return VeridianITEngine(str(data_path))

engine = get_engine()

st.markdown('<div class="main-header">🛡️ Veridian Corp — Internal IT Support Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Rule-based 5-stage pipeline · Pydantic · Streamlit</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Evaluation Requests (REQ-01 to REQ-15)", 
    "✏️ Custom Request Tester", 
    "📊 Batch Evaluation Benchmark", 
    "📚 Knowledge Base & Precedents"
])

# --- TAB 1: Evaluation Requests ---
with tab1:
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.subheader("Select Request")
        req_list = list(engine.requests_map.keys())
        selected_id = st.selectbox(
            "Choose an evaluation test case:",
            req_list,
            format_func=lambda x: f"{x}: {engine.requests_map[x]['employee']['name']} ({engine.requests_map[x]['extracted_entities'].get('issue_type', 'General')})"
        )
        
        req_data = engine.requests_map[selected_id]
        emp = req_data["employee"]
        
        st.markdown("---")
        st.markdown("### 👤 Employee Profile")
        st.write(f"**Name:** {emp['name']}")
        st.write(f"**Email:** {emp['email']}")
        st.write(f"**Role:** {emp['role']}")
        st.write(f"**Status:** {'Contractor' if emp['is_contractor'] else 'Full-time Employee'}")
        st.write(f"**Tenure:** {emp['tenure_years']} years")
        
        st.markdown("---")
        st.markdown("### 💬 Submitted Issue")
        st.info(f'"{req_data["issue_description"]}"')

    with col_right:
        st.subheader("Pipeline Execution Trace")
        
        if st.button("🚀 Run Agent Pipeline", key="btn_run_eval", type="primary"):
            state = engine.process_request_by_id(selected_id)
            
            # Overview Card
            st.markdown(f"### Result Overview")
            status_class = f"status-badge-{state.decision.status}"
            st.markdown(f"**Decision Status:** <span class='{status_class}'>{state.decision.status}</span>", unsafe_allow_html=True)
            st.write(f"**Action Type:** `{state.decision.action_type}`")
            st.write(f"**Routing Target:** `{state.decision.routing_target}`")
            
            st.markdown("---")
            
            # Node 1 & 2
            n1, n2 = st.columns(2)
            with n1:
                st.markdown("#### Node 1: Intent & Entity Parsing")
                st.write(f"**Intent Category:** `{state.intent_category}`")
                st.json(state.extracted_entities.model_dump(exclude_none=True))
            
            with n2:
                st.markdown("#### Node 2: Context & Historical Precedents")
                st.write(f"**Matched KB Rules:** `{', '.join(state.matched_kb_rules)}`")
                for kb_id in state.matched_kb_rules:
                    if kb_id in engine.kb_map:
                        kb = engine.kb_map[kb_id]
                        st.caption(f"**{kb['id']} - {kb['title']}**: {kb['description']}")
                
                if state.matched_precedents:
                    st.markdown("**Matched Ticket Precedents:**")
                    for p in state.matched_precedents:
                        st.caption(f"📌 **{p['ticket_id']}** ({p['status']}): {p['precedent_note']}")

            # Node 3 & 4
            st.markdown("#### Node 3: Policy Decision & Audit Trail")
            st.success(f"**Policy Reasoning:** {state.audit_trail.policy_reasoning}")
            
            st.markdown("#### Node 4: Action Execution Hooks")
            for log_entry in state.audit_trail.execution_log:
                st.code(log_entry, language="text")
                
            # Node 5
            st.markdown("#### Node 5: Agent Final Response")
            st.chat_message("assistant").write(state.generated_response)

            # Export Button
            st.markdown("---")
            st.markdown("### 📥 Compliance Audit Export")
            json_data = tools.export_audit_logs([state.model_dump()], format_type="json")
            st.download_button(
                label="Download Execution Trace (JSON)",
                data=json_data,
                file_name=f"audit_trace_{selected_id}.json",
                mime="application/json"
            )

# --- TAB 2: Custom Request Tester ---
with tab2:
    st.subheader("Simulate Any Custom IT Request")
    c1, c2 = st.columns(2)
    with c1:
        c_name = st.text_input("Employee Name", "Priya Verma")
        c_email = st.text_input("Employee Email", "priya.verma@veridian-corp.example")
    with c2:
        c_role = st.text_input("Role", "Software Engineer")
        c_is_contractor = st.checkbox("Is Contractor?", value=False)
        
    c_desc = st.text_area("Issue Description", "My laptop is 4 years old and won't charge or turn on.")
    
    if st.button("Submit Custom Request", type="primary"):
        emp_dict = {
            "name": c_name,
            "email": c_email,
            "role": c_role,
            "is_contractor": c_is_contractor
        }
        custom_state = engine.process_custom_request(emp_dict, c_desc)
        
        st.markdown("---")
        status_class = f"status-badge-{custom_state.decision.status}"
        st.markdown(f"### Decision Status: <span class='{status_class}'>{custom_state.decision.status}</span> (`{custom_state.decision.action_type}`)", unsafe_allow_html=True)
        st.write(f"**Policy Reasoning:** {custom_state.audit_trail.policy_reasoning}")
        st.chat_message("assistant").write(custom_state.generated_response)

# --- TAB 3: Batch Evaluation Benchmark ---
with tab3:
    st.subheader("📊 Automated Batch Benchmark (15 Requests)")
    st.caption("Executes all 15 grounded test cases deterministically and measures policy decision compliance.")
    
    if st.button("▶️ Run 15-Request Batch Benchmark", type="primary"):
        results = []
        passed_count = 0
        state_dumps = []
        
        for req_id in list(engine.requests_map.keys()):
            state = engine.process_request_by_id(req_id)
            state_dumps.append(state.model_dump())
            expected = engine.requests_map[req_id]["expected_decision"]
            
            is_pass = (state.decision.status == expected["status"])
            if is_pass:
                passed_count += 1
                
            top_precedent = state.matched_precedents[0]["ticket_id"] if state.matched_precedents else "N/A"
            
            results.append({
                "Request ID": req_id,
                "Employee": state.employee.name if hasattr(state.employee, "name") else state.employee.get("name"),
                "Expected Status": expected["status"],
                "Actual Status": state.decision.status,
                "Action Type": state.decision.action_type,
                "Matched Policy": ", ".join(state.matched_kb_rules),
                "Precedent Cited": top_precedent,
                "Pass / Fail": "✅ PASS" if is_pass else "❌ FAIL"
            })
            
        acc_pct = (passed_count / len(results)) * 100.0
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Evaluation Requests", len(results))
        m2.metric("Passed Tests", f"{passed_count} / {len(results)}")
        m3.metric("Policy Compliance Accuracy", f"{acc_pct:.1f}%")
        
        st.markdown("### Benchmark Results Table")
        st.dataframe(results, use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 📥 Compliance Batch Audit Log Export")
        c1, c2 = st.columns(2)
        with c1:
            json_batch = tools.export_audit_logs(state_dumps, format_type="json")
            st.download_button(
                label="Download Full Audit Trace (JSON)",
                data=json_batch,
                file_name="batch_benchmark_audit_trace.json",
                mime="application/json"
            )
        with c2:
            csv_batch = tools.export_audit_logs(state_dumps, format_type="csv")
            st.download_button(
                label="Download Summary Compliance Report (CSV)",
                data=csv_batch,
                file_name="batch_benchmark_compliance_report.csv",
                mime="text/csv"
            )

# --- TAB 4: Knowledge Base & Precedents Browser ---
with tab4:
    st.subheader("Veridian Internal IT Knowledge Base Rules")
    for kb in engine.data_pack["knowledge_base"]:
        with st.expander(f"📌 {kb['id']} - {kb['title']} ({kb['category']})"):
            st.write(kb['description'])
            
    st.markdown("---")
    st.subheader("Historical Ticket Queue & Precedents (TK-1042 to TK-1051)")
    st.dataframe(engine.historical_tickets, use_container_width=True)
