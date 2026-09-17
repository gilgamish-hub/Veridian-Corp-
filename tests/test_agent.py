import pytest
from src.engine import VeridianITEngine
from src.schemas import Employee
from src import tools

@pytest.fixture
def engine():
    return VeridianITEngine(data_pack_path="data/data_pack.json")

def test_req_01_laptop_replacement(engine):
    state = engine.process_request_by_id("REQ-01")
    assert state.decision.status == "APPROVED"
    assert state.decision.action_type == "INITIATE_REPLACEMENT"
    assert "KB-03" in state.matched_kb_rules

def test_req_02_guest_wifi(engine):
    state = engine.process_request_by_id("REQ-02")
    assert state.decision.status == "RESOLVE"
    assert state.decision.action_type == "PROVIDE_KIOSK_INSTRUCTIONS"
    assert "KB-07" in state.matched_kb_rules

def test_req_03_account_lockout(engine):
    state = engine.process_request_by_id("REQ-03")
    assert state.decision.status == "RESOLVE"
    assert state.decision.action_type == "UNLOCK_USER_ACCOUNT"
    assert "KB-01" in state.matched_kb_rules

def test_req_04_non_catalog_software(engine):
    state = engine.process_request_by_id("REQ-04")
    assert state.decision.status == "ROUTE"
    assert state.decision.action_type == "ESCALATE_TO_SECURITY_REVIEW"
    assert "KB-04" in state.matched_kb_rules

def test_req_05_vpn_renewal(engine):
    state = engine.process_request_by_id("REQ-05")
    assert state.decision.status == "RESOLVE"
    assert state.decision.action_type == "RENEW_VPN_CREDENTIALS"
    assert "KB-02" in state.matched_kb_rules

def test_req_06_printer_spooler_and_asset_tag(engine):
    state = engine.process_request_by_id("REQ-06")
    assert state.decision.status == "ROUTE"
    assert state.decision.action_type == "RESTART_SPOOLER_AND_DISPATCH"
    assert state.extracted_entities.asset_tag == "PRN-301"
    assert "KB-05" in state.matched_kb_rules

def test_req_07_wfh_monitor(engine):
    state = engine.process_request_by_id("REQ-07")
    assert state.decision.status == "ROUTE"
    assert state.decision.action_type == "ROUTE_TO_FINANCE_AND_MANAGER"
    assert "KB-10" in state.matched_kb_rules

def test_req_08_phishing_escalation(engine):
    state = engine.process_request_by_id("REQ-08")
    assert state.decision.status == "ROUTE"
    assert state.decision.action_type == "ESCALATE_PHISHING_ALERT"
    assert "KB-09" in state.matched_kb_rules

def test_req_09_mailbox_quota(engine):
    state = engine.process_request_by_id("REQ-09")
    assert state.decision.status == "ROUTE"
    assert state.decision.action_type == "REQUEST_QUOTA_APPROVAL"
    assert "KB-06" in state.matched_kb_rules

def test_req_09_mailbox_quota_exceeds_50gb_cap(engine):
    emp = Employee(name="Rohit Desai", email="rohit.desai@veridian-corp.example")
    state = engine.process_custom_request(emp, "My mailbox is full, please expand it to 60GB.")
    assert state.decision.status == "UNALLOWABLE"
    assert state.decision.action_type == "REJECT_EXCEEDS_50GB_CAP"
    assert "50GB" in state.audit_trail.policy_reasoning

def test_req_10_admin_access_precedent(engine):
    state = engine.process_request_by_id("REQ-10")
    assert state.decision.status == "ROUTE"
    assert state.decision.action_type == "ROUTE_FOR_APPROVAL_AND_JUSTIFICATION"
    assert len(state.matched_precedents) > 0
    assert state.matched_precedents[0]["ticket_id"] == "TK-1050"

def test_req_11_contractor_vpn(engine):
    state = engine.process_request_by_id("REQ-11")
    assert state.decision.status == "ROUTE"
    assert state.decision.action_type == "ROUTE_TO_MANAGER"
    assert "KB-02" in state.matched_kb_rules

def test_req_12_expense_tool_finance_account_check(engine):
    state = engine.process_request_by_id("REQ-12")
    assert state.decision.status == "ROUTE"
    assert state.decision.action_type == "REDIRECT_TO_FINANCE"
    assert state.extracted_entities.finance_account_exists is False
    assert "NOT exist in Finance DB" in state.audit_trail.policy_reasoning

def test_req_13_laptop_repair(engine):
    state = engine.process_request_by_id("REQ-13")
    assert state.decision.status == "ROUTE"
    assert state.decision.action_type == "ROUTE_TO_HARDWARE_REPAIR"
    assert "KB-03" in state.matched_kb_rules

def test_req_14_browser_extension(engine):
    state = engine.process_request_by_id("REQ-14")
    assert state.decision.status == "ROUTE"
    assert state.decision.action_type == "ESCALATE_TO_SECURITY_REVIEW"
    assert "KB-04" in state.matched_kb_rules

def test_req_15_ambiguous_request(engine):
    state = engine.process_request_by_id("REQ-15")
    assert state.decision.status == "CLARIFY"
    assert state.decision.action_type == "REQUEST_EMPLOYEE_CLARIFICATION"

def test_audit_log_exporter(engine):
    state = engine.process_request_by_id("REQ-01")
    json_export = tools.export_audit_logs([state.model_dump()], format_type="json")
    csv_export = tools.export_audit_logs([state.model_dump()], format_type="csv")
    assert "REQ-01" in json_export
    assert "REQ-01" in csv_export
