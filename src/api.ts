import type { ActionProposal, ActionProposalRequest, ActionReviewRequest, ActionReviewResponse, AuthSession, AuthUser, IncidentReplay, IncidentSummary, PolicySummary, Postmortem } from './types';

export const AUTH_TOKEN_KEY = 'blackboxops.auth.token';
export const AUTH_USER_KEY = 'blackboxops.auth.user';

function authHeaders(): Record<string, string> {
  const token = localStorage.getItem(AUTH_TOKEN_KEY);
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, {
    headers: { 'Content-Type': 'application/json', ...authHeaders(), ...(init?.headers ?? {}) },
    ...init,
  });
  if (!response.ok) {
    let detail = `BlackBoxOps API request failed: ${response.status}`;
    try {
      const body = await response.json();
      detail = body.detail ?? detail;
    } catch {
      // Keep the default API error when the response is not JSON.
    }
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

export const api = {
  listIncidents: () => request<IncidentSummary[]>('/incidents'),
  listPolicies: () => request<PolicySummary[]>('/policies'),
  runDemo: () => request<IncidentReplay>('/demo/run', { method: 'POST' }),
  getReplay: (incidentId: string) => request<IncidentReplay>(`/incidents/${incidentId}/replay`),
  proposeAction: (payload: ActionProposalRequest) => request<ActionProposal>('/actions/propose', { method: 'POST', body: JSON.stringify(payload) }),
  listActions: (incidentId?: string) => request<ActionProposal[]>(`/actions${incidentId ? `?incident_id=${encodeURIComponent(incidentId)}` : ''}`),
  approveAction: (actionId: string, payload: ActionReviewRequest) => request<ActionReviewResponse>(`/actions/${actionId}/approve`, { method: 'POST', body: JSON.stringify(payload) }),
  rejectAction: (actionId: string, payload: ActionReviewRequest) => request<ActionReviewResponse>(`/actions/${actionId}/reject`, { method: 'POST', body: JSON.stringify(payload) }),
  getPostmortem: (incidentId: string) => request<Postmortem>(`/incidents/${incidentId}/postmortem`),
  signUp: (payload: { name: string; email: string; password: string }) => request<AuthSession>('/auth/signup', { method: 'POST', body: JSON.stringify(payload) }),
  signIn: (payload: { email: string; password: string }) => request<AuthSession>('/auth/signin', { method: 'POST', body: JSON.stringify(payload) }),
  demoSession: () => request<AuthSession>('/auth/demo', { method: 'POST' }),
  me: (token: string) => request<AuthUser>('/auth/me', { headers: { Authorization: `Bearer ${token}` } }),
  patchPolicy: (policyId: string, enabled: boolean) => request<PolicySummary>(`/policies/${policyId}`, { method: 'PATCH', body: JSON.stringify({ enabled }) }),
  updateProfile: (payload: { name?: string; current_password?: string; new_password?: string }) => request<AuthUser>('/auth/profile', { method: 'PATCH', body: JSON.stringify(payload) }),
  googleLoginUrl: () => '/api/auth/google/login',
};
