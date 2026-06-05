export interface EvidenceRef {
  evidence_id: string;
  query: string;
  time_range: string;
  source: string;
  sample_event: Record<string, string>;
  confidence: number;
  risk_flags: string[];
}

export interface PolicyDecision {
  decision_id: string;
  policy_id: string;
  status: 'allow' | 'warn' | 'approval_required' | 'block';
  reason: string;
  risk_level: string;
  matched_rules: string[];
  required_approval: boolean;
}

export interface AgentEvent {
  event_id: string;
  display_id?: string | null;
  incident_id: string;
  session_id: string;
  timestamp: string;
  event_type: string;
  actor: string;
  risk_score: number;
  summary: string;
  payload: Record<string, unknown>;
  evidence_refs: EvidenceRef[];
  policy_decision: PolicyDecision | null;
}

export interface IncidentReplay {
  incident_id: string;
  title: string;
  status: string;
  session_id?: string | null;
  source?: string;
  started_at?: string | null;
  outcome?: string;
  approval_required?: boolean;
  events: AgentEvent[];
  evidence: EvidenceRef[];
  policy_decisions: PolicyDecision[];
}

export interface IncidentSummary {
  incident_id: string;
  title: string;
  severity: string;
  status: string;
  description: string;
}

export interface PolicySummary {
  policy_id: string;
  name: string;
  description: string;
  status: PolicyDecision['status'];
  enabled: boolean;
  risk_level?: string;
  splunk_source?: string;
  original_rule_id?: string | null;
}

export interface Postmortem {
  incident_id: string;
  title: string;
  markdown: string;
}

export interface AuthUser {
  user_id: string;
  email: string;
  name: string;
  created_at: string;
}

export interface AuthSession {
  token: string;
  user: AuthUser;
}

export interface ActionProposalRequest {
  incident_id: string;
  action_type: string;
  target: string;
  evidence_refs: string[];
  requested_by: string;
  reason: string;
}

export interface ActionProposal {
  action_id: string;
  incident_id: string;
  action_type: string;
  target: string;
  evidence_refs: string[];
  requested_by: string;
  reason: string;
  status: 'pending_approval' | 'blocked' | 'allowed' | 'warned' | 'approved' | 'rejected';
  decision: PolicyDecision;
  created_at: string;
  approved_by?: string | null;
  rejected_by?: string | null;
  review_note?: string | null;
  reviewed_at?: string | null;
}

export interface ActionReviewRequest {
  reviewer: string;
  note?: string | null;
}

export interface ActionReviewResponse {
  action_id: string;
  incident_id: string;
  status: 'approved' | 'rejected';
  reviewer: string;
  note: string;
  reviewed_at: string;
}
