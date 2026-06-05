import { api } from './api';
import type { ActionProposal, ActionProposalRequest, ActionReviewResponse } from './types';

export async function actionWorkflowContract(incidentId: string): Promise<ActionReviewResponse> {
  const request: ActionProposalRequest = {
    incident_id: incidentId,
    action_type: 'restart_service',
    target: 'checkout-api',
    evidence_refs: ['EVD-100', 'EVD-101'],
    requested_by: 'sre-lead@acme.corp',
    reason: 'Restart checkout-api after evidence review.',
  };

  const proposal: ActionProposal = await api.proposeAction(request);
  const proposals: ActionProposal[] = await api.listActions(incidentId);
  if (!proposals.some((item) => item.action_id === proposal.action_id)) {
    throw new Error('Proposed action must be visible in the action list');
  }

  return api.approveAction(proposal.action_id, {
    reviewer: 'sre-lead@acme.corp',
    note: 'Approved from frontend workflow contract.',
  });
}
