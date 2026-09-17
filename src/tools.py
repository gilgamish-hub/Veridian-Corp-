"""
Deterministic Action Hooks & Integration Tools for Veridian IT Support Agent
"""
import json
import csv
import io
from typing import List, Dict, Any

# Mock Finance Database for account existence checks (KB-08)
FINANCE_ACCOUNT_DATABASE = {
    "sneha.kulkarni@veridian-corp.example": False,  # Account does not exist in Finance system
    "aditi.sharma@veridian-corp.example": True,
    "kavya.pillai@veridian-corp.example": True,
    "farhan.ali@veridian-corp.example": True,
}

def check_finance_account_exists(user_email: str) -> dict:
    """Check if employee has an active account in the Finance/Expense tool system (KB-08)."""
    exists = FINANCE_ACCOUNT_DATABASE.get(user_email, False)
    return {
        "tool": "check_finance_account_exists",
        "user_email": user_email,
        "account_exists": exists,
        "message": f"Finance account check for {user_email}: {'EXISTS' if exists else 'NOT_FOUND in Finance DB'}"
    }

def verify_mailbox_quota_request(current_gb: float, requested_gb: float) -> dict:
    """Validate mailbox expansion against KB-06 50GB hard cap."""
    if requested_gb > 50.0:
        return {
            "tool": "verify_mailbox_quota_request",
            "allowable": False,
            "max_cap_gb": 50.0,
            "message": f"Requested mailbox quota ({requested_gb}GB) exceeds the 50GB hard policy cap (KB-06)."
        }
    return {
        "tool": "verify_mailbox_quota_request",
        "allowable": True,
        "max_cap_gb": 50.0,
        "message": f"Requested quota ({requested_gb}GB) is within allowable limit (cap: 50GB)."
    }

def unlock_user_account(user_email: str) -> dict:
    return {
        "tool": "unlock_user_account",
        "status": "SUCCESS",
        "message": f"Account unlock command successfully dispatched for {user_email}. User is unlocked."
    }

def renew_vpn_credentials(user_email: str) -> dict:
    return {
        "tool": "renew_vpn_credentials",
        "status": "SUCCESS",
        "message": f"VPN credential renewal token generated for {user_email}. Expiry reset to +90 days."
    }

def route_ticket(ticket_id: str, target_department: str, justification: str) -> dict:
    return {
        "tool": "route_ticket",
        "status": "ROUTED",
        "message": f"Ticket {ticket_id} assigned to '{target_department}'. Justification: {justification}"
    }

def send_security_alert(user_email: str, details: str) -> dict:
    return {
        "tool": "send_security_alert",
        "status": "ALERT_TRIGGERED",
        "message": f"High priority security event flagged by {user_email}. Alert sent to SOC: {details}"
    }

def dispatch_replacement_laptop(user_email: str, reason: str) -> dict:
    return {
        "tool": "dispatch_replacement_laptop",
        "status": "APPROVED",
        "message": f"Hardware replacement order dispatched for {user_email}. Reason: {reason}"
    }

def restart_spooler_and_dispatch(location: str, asset_tag: str = "UNSPECIFIED") -> dict:
    return {
        "tool": "restart_spooler_and_dispatch",
        "status": "DISPATCHED",
        "asset_tag": asset_tag,
        "message": f"Print spooler restart initiated for {location} (Asset Tag: {asset_tag}). Field support ticket logged."
    }

def request_employee_clarification(user_email: str, details_needed: str = "error details/screenshots") -> dict:
    return {
        "tool": "request_employee_clarification",
        "status": "CLARIFICATION_SENT",
        "message": f"Automated request for clarification sent to {user_email} requesting {details_needed}."
    }

def export_audit_logs(states: List[Dict[str, Any]], format_type: str = "json") -> str:
    """Export pipeline execution trace for compliance auditing."""
    if format_type.lower() == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Request ID", "Employee", "Intent", "Decision Status", "Action Type", "Routing Target", "Matched Rules", "Policy Reasoning"])
        for s in states:
            dec = s.get("decision", {})
            audit = s.get("audit_trail", {})
            emp = s.get("employee", {})
            writer.writerow([
                s.get("request_id"),
                emp.get("name") if isinstance(emp, dict) else str(emp),
                s.get("intent_category"),
                dec.get("status"),
                dec.get("action_type"),
                dec.get("routing_target"),
                ", ".join(s.get("matched_kb_rules", [])),
                audit.get("policy_reasoning")
            ])
        return output.getvalue()
    else:
        return json.dumps(states, indent=2)
