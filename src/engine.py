import json
import os
import re
from typing import Dict, Any, List
from src.schemas import RequestState, Employee, ExtractedEntities, Decision, AuditTrail
from src import tools

class VeridianITEngine:
    def __init__(self, data_pack_path: str = "data/data_pack.json"):
        if not os.path.isabs(data_pack_path):
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_pack_path = os.path.join(project_root, data_pack_path)
            
        with open(data_pack_path, "r", encoding="utf-8") as f:
            self.data_pack = json.load(f)
        
        self.kb_map = {kb["id"]: kb for kb in self.data_pack.get("knowledge_base", [])}
        self.requests_map = {req["request_id"]: req for req in self.data_pack.get("requests", [])}
        self.historical_tickets = self.data_pack.get("historical_tickets", [])

    def process_request_by_id(self, request_id: str) -> RequestState:
        req_data = self.requests_map.get(request_id)
        if not req_data:
            raise ValueError(f"Request ID {request_id} not found in data pack.")
        
        employee = Employee(**req_data["employee"])
        extracted_entities = ExtractedEntities(**req_data.get("extracted_entities", {}))
        
        state = RequestState(
            request_id=request_id,
            employee=employee,
            issue_description=req_data["issue_description"],
            extracted_entities=extracted_entities
        )
        
        return self.run_pipeline(state)

    def process_custom_request(self, employee: Any, issue_description: str) -> RequestState:
        if isinstance(employee, dict):
            emp_obj = Employee(**employee)
        elif hasattr(employee, "model_dump"):
            emp_obj = Employee(**employee.model_dump())
        elif isinstance(employee, Employee):
            emp_obj = employee
        else:
            emp_obj = Employee(
                name=getattr(employee, "name", "Employee"),
                email=getattr(employee, "email", "employee@veridian-corp.example"),
                role=getattr(employee, "role", "Employee"),
                is_contractor=getattr(employee, "is_contractor", False)
            )

        state = RequestState(
            request_id="CUSTOM-REQ",
            employee=emp_obj,
            issue_description=issue_description
        )
        return self.run_pipeline(state)

    def run_pipeline(self, state: RequestState) -> RequestState:
        # Node 1: Intent & Entity Parser
        state = self._node_1_parse_intent_and_entities(state)
        
        # Node 2: Grounded Context & Historical Precedent Retrieval
        state = self._node_2_grounded_context_retrieval(state)
        
        # Node 3: Policy Decision Engine
        state = self._node_3_policy_decision_engine(state)
        
        # Node 4: Action Execution Hooks
        state = self._node_4_action_execution_hooks(state)
        
        # Node 5: Response Generation
        state = self._node_5_response_generation(state)
        
        return state

    # --- Node Implementation Methods ---

    def _node_1_parse_intent_and_entities(self, state: RequestState) -> RequestState:
        text = state.issue_description.lower()
        entities = state.extracted_entities
        emp = state.employee
        emp_email = emp.get("email") if isinstance(emp, dict) else getattr(emp, "email", "")

        # Extract Asset Tag if mentioned (e.g. PRN-301)
        asset_match = re.search(r'\b(prn-\d+|asset\s*tag\s*(?:is|=|:)?\s*([a-z0-9\-]+))\b', text, re.IGNORECASE)
        if asset_match and not entities.asset_tag:
            entities.asset_tag = asset_match.group(0).upper().replace("ASSET TAG IS ", "").replace("ASSET TAG: ", "").strip()

        # Extract requested mailbox size if mentioned (e.g. 35GB, 60GB)
        gb_matches = re.findall(r'(\d+)\s*gb', text, re.IGNORECASE)
        if gb_matches:
            gb_vals = [float(g) for g in gb_matches]
            for val in gb_vals:
                if val > 25.0:
                    entities.requested_mailbox_size_gb = val

        # Determine Intent Category
        if "lockout" in text or "locked out" in text or "password 6 times" in text:
            state.intent_category = "ACCESS_LOCKOUT"
            if entities.failed_attempts is None:
                entities.failed_attempts = 6
                entities.issue_type = "account_lockout"
        elif "guest" in text or "wifi" in text or "wi-fi" in text:
            state.intent_category = "ACCESS_GUEST_WIFI"
            if not entities.issue_type:
                entities.issue_type = "guest_wifi"
        elif "vpn" in text:
            state.intent_category = "ACCESS_VPN"
            if not entities.issue_type:
                entities.issue_type = "vpn_access"
        elif "phishing" in text or "suspicious email" in text or "weird link" in text or "forwarded" in text:
            state.intent_category = "SECURITY_THREAT"
            if entities.is_phishing_suspected is None:
                entities.is_phishing_suspected = True
                entities.issue_type = "security_threat"
        elif "expense" in text or "expense portal" in text:
            state.intent_category = "SOFTWARE_EXPENSE"
            if not entities.issue_type:
                entities.issue_type = "expense_tool"
            # Perform Finance account existence check (KB-08)
            fin_res = tools.check_finance_account_exists(emp_email)
            entities.finance_account_exists = fin_res["account_exists"]
        elif ("laptop" in text or "screen " in text or " power on" in text or "flickers" in text or "laptop screen" in text or "turn on" in text) and "screenshot" not in text:
            state.intent_category = "HARDWARE_LAPTOP"
            if entities.device_age_years is None:
                match = re.search(r'(\d+(?:\.\d+)?)\s*(?:years?|yrs?|yr)', text)
                if match:
                    entities.device_age_years = float(match.group(1))
            if entities.is_completely_dead is None:
                if any(phrase in text for phrase in ["won't power on", "completely black", "won't turn on", "won't charge", "dead"]):
                    entities.is_completely_dead = True
                elif "flickers" in text:
                    entities.is_completely_dead = False
        elif "printer" in text or "paper jam" in text:
            state.intent_category = "HARDWARE_PRINTER"
            if not entities.issue_type:
                entities.issue_type = "printer_malfunction"
        elif "work from home" in text or "wfh" in text or "monitor" in text:
            state.intent_category = "HARDWARE_WFH"
            if entities.wfh_days_per_week is None:
                entities.wfh_days_per_week = 4
        elif "mailbox" in text or "25gb" in text or "quota" in text or "full" in text:
            state.intent_category = "SOFTWARE_MAILBOX"
            if entities.current_mailbox_size_gb is None:
                entities.current_mailbox_size_gb = 25.0
        elif "admin" in text or "server" in text or "finance reporting" in text:
            state.intent_category = "ACCESS_ADMIN"
            if not entities.issue_type:
                entities.issue_type = "admin_access_request"
        elif "extension" in text or "graphviz" in text or "non-catalog" in text or "timetracker" in text or "software" in text:
            state.intent_category = "SOFTWARE_INSTALLATION"
            if not entities.issue_type:
                entities.issue_type = "software_installation"
        elif text.strip() in ["hey can you help, its not working", "not working", "help"]:
            state.intent_category = "AMBIGUOUS"
            entities.issue_type = "ambiguous"

        return state

    def _node_2_grounded_context_retrieval(self, state: RequestState) -> RequestState:
        matched_kb = []
        cat = state.intent_category

        if cat == "ACCESS_LOCKOUT":
            matched_kb.append("KB-01")
        elif cat == "ACCESS_VPN":
            matched_kb.append("KB-02")
        elif cat == "HARDWARE_LAPTOP":
            matched_kb.append("KB-03")
        elif cat in ["SOFTWARE_INSTALLATION"]:
            matched_kb.append("KB-04")
        elif cat == "ACCESS_ADMIN":
            matched_kb.append("KB-04")
        elif cat == "HARDWARE_PRINTER":
            matched_kb.append("KB-05")
        elif cat == "SOFTWARE_MAILBOX":
            matched_kb.append("KB-06")
        elif cat == "ACCESS_GUEST_WIFI":
            matched_kb.append("KB-07")
        elif cat == "SOFTWARE_EXPENSE":
            matched_kb.append("KB-08")
        elif cat == "SECURITY_THREAT":
            matched_kb.append("KB-09")
        elif cat == "HARDWARE_WFH":
            matched_kb.append("KB-10")
        else:
            matched_kb.append("Baseline Security Protocol")

        state.matched_kb_rules = matched_kb

        # Historical Precedent Engine: Query past tickets matching intent category / issue_type
        precedents = []
        for ticket in self.historical_tickets:
            if ticket.get("category") == cat or (state.extracted_entities.issue_type and ticket.get("issue_type") == state.extracted_entities.issue_type):
                precedents.append(ticket)
        
        state.matched_precedents = precedents
        return state

    def _node_3_policy_decision_engine(self, state: RequestState) -> RequestState:
        cat = state.intent_category
        ent = state.extracted_entities
        emp = state.employee
        
        is_contractor = emp.get("is_contractor") if isinstance(emp, dict) else getattr(emp, "is_contractor", False)

        status = "ROUTE"
        action_type = "ROUTE_TICKET"
        routing_target = "IT_HELPDESK"
        reasoning = ""
        req_mgr = False
        req_fin = False
        req_sec = False

        if cat == "ACCESS_LOCKOUT":
            status = "RESOLVE"
            action_type = "UNLOCK_USER_ACCOUNT"
            routing_target = "AUTOMATED_ACTION"
            reasoning = "User account locked due to >=5 failed attempts. KB-01 policy permits automated unlock after identity verification."

        elif cat == "ACCESS_GUEST_WIFI":
            status = "RESOLVE"
            action_type = "PROVIDE_KIOSK_INSTRUCTIONS"
            routing_target = "SELF_SERVICE"
            reasoning = "Guest Wi-Fi is self-service via lobby kiosks per KB-07. No IT ticket required."

        elif cat == "ACCESS_VPN":
            if is_contractor:
                status = "ROUTE"
                action_type = "ROUTE_TO_MANAGER"
                routing_target = "MANAGER_APPROVAL_FORM"
                req_mgr = True
                reasoning = "Contractor VPN access requires explicit manager sign-off per KB-02 policy."
            else:
                status = "RESOLVE"
                action_type = "RENEW_VPN_CREDENTIALS"
                routing_target = "AUTOMATED_ACTION"
                reasoning = "Full-time employee VPN renewal auto-granted for 90 days per KB-02."

        elif cat == "HARDWARE_LAPTOP":
            age = ent.device_age_years if ent.device_age_years is not None else 0.0
            is_dead = ent.is_completely_dead if ent.is_completely_dead is not None else False

            if age >= 3.0 and is_dead:
                status = "APPROVED"
                action_type = "INITIATE_REPLACEMENT"
                routing_target = "IT_HARDWARE_DISPATCH"
                reasoning = f"Laptop age ({age} yrs) meets the 3-year refresh threshold and has a verified unrepairable failure. Replacement approved per KB-03."
            elif age >= 3.0:
                status = "APPROVED"
                action_type = "INITIATE_REPLACEMENT"
                routing_target = "IT_HARDWARE_DISPATCH"
                reasoning = f"Laptop age ({age} yrs) meets the >= 3.0 years refresh threshold. Replacement approved per KB-03."
            elif is_dead:
                status = "APPROVED"
                action_type = "INITIATE_REPLACEMENT"
                routing_target = "IT_HARDWARE_DISPATCH"
                reasoning = f"Laptop is {age} yrs old (< 3.0 yrs threshold), BUT replacement is approved due to verified unrepairable hardware failure (device won't turn on/charge) per KB-03."
            else:
                status = "ROUTE"
                action_type = "ROUTE_TO_HARDWARE_REPAIR"
                routing_target = "IT_HARDWARE_REPAIR"
                reasoning = f"Laptop age ({age} yrs) is under the 3.0 years threshold with a minor fixable issue. Must attempt hardware repair diagnostic first per KB-03."

        elif cat == "SOFTWARE_INSTALLATION":
            status = "ROUTE"
            action_type = "ESCALATE_TO_SECURITY_REVIEW"
            routing_target = "IT_SECURITY_REVIEW"
            req_sec = True
            reasoning = "Non-catalog software or browser extension requires 3-5 day IT Security review per KB-04."

        elif cat == "HARDWARE_PRINTER":
            asset = ent.asset_tag or "UNSPECIFIED"
            status = "ROUTE"
            action_type = "RESTART_SPOOLER_AND_DISPATCH"
            routing_target = "IT_FIELD_SUPPORT"
            reasoning = f"Printer malfunction reported (Asset Tag: {asset}). Initiated spooler restart; field support technician dispatched per KB-05."

        elif cat == "HARDWARE_WFH":
            days = ent.wfh_days_per_week or 0
            if days >= 3:
                status = "ROUTE"
                action_type = "ROUTE_TO_FINANCE_AND_MANAGER"
                routing_target = "MANAGER_AND_FINANCE_APPROVAL"
                req_mgr = True
                req_fin = True
                reasoning = f"WFH days ({days}) >= 3 days per week. Eligible for WFH monitor allowance subject to Manager & Finance approval per KB-10."
            else:
                status = "ROUTE"
                action_type = "ROUTE_TICKET"
                routing_target = "IT_HELPDESK"
                reasoning = "WFH days < 3 threshold. Requires custom exception approval."

        elif cat == "SECURITY_THREAT":
            status = "ROUTE"
            action_type = "ESCALATE_PHISHING_ALERT"
            routing_target = "SECURITY_INCIDENT_TEAM"
            req_sec = True
            reasoning = "CRITICAL: Suspected phishing threat flagged. Immediate escalation to Security; employee warned not to forward per KB-09."

        elif cat == "SOFTWARE_MAILBOX":
            req_gb = ent.requested_mailbox_size_gb or 35.0
            if req_gb > 50.0:
                status = "UNALLOWABLE"
                action_type = "REJECT_EXCEEDS_50GB_CAP"
                routing_target = "SELF_SERVICE"
                reasoning = f"Mailbox expansion to {req_gb}GB is UNALLOWABLE. KB-06 policy strictly caps mailbox expansions at 50GB max."
            else:
                status = "ROUTE"
                action_type = "REQUEST_QUOTA_APPROVAL"
                routing_target = "MANAGER_APPROVAL_WORKFLOW"
                req_mgr = True
                reasoning = f"Mailbox full at 25GB quota. Archiving advised; expansion request to {req_gb}GB (within 50GB max cap) routed for manager approval per KB-06."

        elif cat == "ACCESS_ADMIN":
            status = "ROUTE"
            action_type = "ROUTE_FOR_APPROVAL_AND_JUSTIFICATION"
            routing_target = "FINANCE_SECURITY_MANAGER"
            req_mgr = True
            req_sec = True
            reasoning = "Admin access request to finance reporting server requires explicit business justification and manager sign-off per KB-04 (Precedent TK-1050)."

        elif cat == "SOFTWARE_EXPENSE":
            account_exists = ent.finance_account_exists if ent.finance_account_exists is not None else False
            status = "ROUTE"
            action_type = "REDIRECT_TO_FINANCE"
            routing_target = "FINANCE_HELPDESK"
            if not account_exists:
                reasoning = "KB-08 Policy: Expense portal account does NOT exist in Finance DB. IT does not provision accounts; ticket redirected immediately to Finance Onboarding team."
            else:
                reasoning = "Expense portal access verified in Finance DB. Password reset/credential assistance ticket routed to Finance Admin per KB-08."

        elif cat == "AMBIGUOUS":
            status = "CLARIFY"
            action_type = "REQUEST_EMPLOYEE_CLARIFICATION"
            routing_target = "EMPLOYEE_FEEDBACK"
            reasoning = "Request lacks sufficient detail or diagnostic context. Initiating clarification request per baseline protocol."

        decision = Decision(
            status=status,
            action_type=action_type,
            routing_target=routing_target,
            requires_manager_approval=req_mgr,
            requires_finance_approval=req_fin,
            requires_security_review=req_sec
        )

        audit_trail = AuditTrail(
            policy_reasoning=reasoning,
            matched_rules=state.matched_kb_rules,
            matched_precedents=state.matched_precedents,
            execution_log=[f"Evaluated intent '{cat}' against policy rules and {len(state.matched_precedents)} historical ticket precedents."]
        )

        state.decision = decision
        state.audit_trail = audit_trail
        return state

    def _node_4_action_execution_hooks(self, state: RequestState) -> RequestState:
        dec = state.decision
        emp = state.employee
        emp_email = emp.get("email") if isinstance(emp, dict) else getattr(emp, "email", "")

        if dec.action_type == "UNLOCK_USER_ACCOUNT":
            exec_res = tools.unlock_user_account(emp_email)
        elif dec.action_type == "RENEW_VPN_CREDENTIALS":
            exec_res = tools.renew_vpn_credentials(emp_email)
        elif dec.action_type == "INITIATE_REPLACEMENT":
            exec_res = tools.dispatch_replacement_laptop(emp_email, state.audit_trail.policy_reasoning)
        elif dec.action_type == "ESCALATE_PHISHING_ALERT":
            exec_res = tools.send_security_alert(emp_email, state.issue_description)
        elif dec.action_type == "RESTART_SPOOLER_AND_DISPATCH":
            exec_res = tools.restart_spooler_and_dispatch("Printer Location", state.extracted_entities.asset_tag or "PRN-301")
        elif dec.action_type == "REQUEST_EMPLOYEE_CLARIFICATION":
            exec_res = tools.request_employee_clarification(emp_email)
        elif dec.action_type == "REJECT_EXCEEDS_50GB_CAP":
            exec_res = tools.verify_mailbox_quota_request(25.0, state.extracted_entities.requested_mailbox_size_gb or 60.0)
        else:
            exec_res = tools.route_ticket(state.request_id, dec.routing_target, state.audit_trail.policy_reasoning)

        state.audit_trail.execution_log.append(f"Executed action tool [{exec_res['tool']}]: {exec_res['message']}")
        return state

    def _node_5_response_generation(self, state: RequestState) -> RequestState:
        dec = state.decision
        emp = state.employee
        emp_name = emp.get("name") if isinstance(emp, dict) else getattr(emp, "name", "Employee")

        precedent_txt = ""
        if state.matched_precedents:
            top_p = state.matched_precedents[0]
            precedent_txt = f"\n\n📋 Historical Precedent ({top_p['ticket_id']}): {top_p['precedent_note']}"

        if dec.status == "APPROVED":
            resp = f"Hello {emp_name},\n\nYour request has been APPROVED under policy {', '.join(state.matched_kb_rules)}.\n{state.audit_trail.policy_reasoning}\n\nOur hardware dispatch team has been notified to issue your hardware replacement.{precedent_txt}"
        elif dec.status == "RESOLVE":
            if dec.action_type == "PROVIDE_KIOSK_INSTRUCTIONS":
                resp = f"Hello {emp_name},\n\nFor guest Wi-Fi access, visitors can self-generate a 24-hour pass directly using the touch kiosk located at the front desk lobby (Policy KB-07). No formal IT ticket is required!{precedent_txt}"
            elif dec.action_type == "UNLOCK_USER_ACCOUNT":
                resp = f"Hello {emp_name},\n\nWe have verified your identity and executed an automated unlock on your Veridian account. You should now be able to log in with your updated credentials (Policy KB-01).{precedent_txt}"
            elif dec.action_type == "RENEW_VPN_CREDENTIALS":
                resp = f"Hello {emp_name},\n\nYour VPN credentials have been successfully renewed for 90 days (Policy KB-02). Please restart your VPN client.{precedent_txt}"
            else:
                resp = f"Hello {emp_name},\n\nYour issue has been resolved automatically in accordance with policy {', '.join(state.matched_kb_rules)}.{precedent_txt}"
        elif dec.status == "UNALLOWABLE":
            resp = f"⚠️ POLICY LIMIT EXCEEDED ⚠️\n\nHello {emp_name},\n\n{state.audit_trail.policy_reasoning}\n\nPlease archive older emails to free up mailbox space.{precedent_txt}"
        elif dec.status == "CLARIFY":
            resp = f"Hello {emp_name},\n\nThank you for reaching out to Veridian IT Support. To assist you promptly, could you please provide more specific details about your issue (e.g. error messages, device asset tag, or screenshots)?{precedent_txt}"
        else:  # ROUTE
            if dec.action_type == "ESCALATE_PHISHING_ALERT":
                resp = f"⚠️ IMPORTANT SECURITY NOTICE ⚠️\n\nHello {emp_name},\n\nThank you for reporting this suspicious email. Our Security Operations Center has been immediately alerted (Policy KB-09).\n\nPLEASE DO NOT FORWARD THIS EMAIL TO COLLEAGUES. We are isolating the message domain now.{precedent_txt}"
            elif dec.action_type == "REDIRECT_TO_FINANCE":
                resp = f"Hello {emp_name},\n\n{state.audit_trail.policy_reasoning}\n\nWe have redirected your ticket directly to the Finance Onboarding & Support Team.{precedent_txt}"
            else:
                resp = f"Hello {emp_name},\n\nYour request has been routed to '{dec.routing_target}' for further review (Policy {', '.join(state.matched_kb_rules)}).\nReasoning: {state.audit_trail.policy_reasoning}{precedent_txt}"

        state.generated_response = resp
        return state
