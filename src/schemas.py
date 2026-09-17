from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

class Employee(BaseModel):
    name: str
    email: str
    role: Optional[str] = "Employee"
    is_contractor: bool = False
    tenure_years: float = 1.0

class ExtractedEntities(BaseModel):
    device_type: Optional[str] = None
    device_age_years: Optional[float] = None
    is_completely_dead: Optional[bool] = None
    issue_type: Optional[str] = None
    failed_attempts: Optional[int] = None
    software_name: Optional[str] = None
    is_catalog_software: Optional[bool] = None
    is_browser_extension: Optional[bool] = None
    wfh_days_per_week: Optional[int] = None
    forwarded_to_team: Optional[bool] = None
    is_phishing_suspected: Optional[bool] = None
    current_mailbox_size_gb: Optional[float] = None
    requested_mailbox_size_gb: Optional[float] = None
    target_system: Optional[str] = None
    access_level: Optional[str] = None
    location: Optional[str] = None
    asset_tag: Optional[str] = None
    finance_account_exists: Optional[bool] = None
    extra_details: Dict[str, Any] = Field(default_factory=dict)

class Decision(BaseModel):
    status: str  # RESOLVE | APPROVE | ROUTE | CLARIFY | UNALLOWABLE
    action_type: str
    routing_target: str
    requires_manager_approval: bool = False
    requires_finance_approval: bool = False
    requires_security_review: bool = False

class AuditTrail(BaseModel):
    policy_reasoning: str
    matched_rules: List[str] = Field(default_factory=list)
    matched_precedents: List[Dict[str, Any]] = Field(default_factory=list)
    execution_log: List[str] = Field(default_factory=list)

class RequestState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    request_id: str
    employee: Any
    issue_description: str
    intent_category: str = "GENERAL"
    extracted_entities: ExtractedEntities = Field(default_factory=ExtractedEntities)
    matched_kb_rules: List[str] = Field(default_factory=list)
    matched_precedents: List[Dict[str, Any]] = Field(default_factory=list)
    decision: Optional[Decision] = None
    audit_trail: Optional[AuditTrail] = None
    generated_response: Optional[str] = None
