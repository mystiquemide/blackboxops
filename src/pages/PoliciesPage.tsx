import { useEffect, useMemo, useState } from 'react';
import { AlertTriangle, ArrowRight, ArrowUpRight, Pause, Play, Shield, ShieldAlert, Star } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import BboConsoleNav from '../components/BboConsoleNav';
import { api } from '../api';
import type { PolicySummary } from '../types';

type PolicyOutcome = 'block' | 'approval_required' | 'warn' | 'allow';
type Policy = PolicySummary & { tags: string[]; featured?: boolean; linkedIncident?: string | null };

const fallbackPolicies: Policy[] = [
  { policy_id: 'POL-INJ-01', name: 'Block Prompt Injection', status: 'block', enabled: true, featured: true, linkedIncident: 'INC-20260529', description: 'Scans Splunk log payloads for prompt-injection signatures before agent processing. Blocks the agent action chain and preserves evidence_refs when injection content is detected in user input, checkout logs, or audit streams.', tags: ['PROMPT_INJECTION', 'SQL_INJECTION', 'DATA_EXFIL'] },
  { policy_id: 'POL-SYS-05', name: 'Require Approval for Destructive SPL', status: 'approval_required', enabled: true, linkedIncident: 'INC-20260528', description: 'Pauses agent execution when SPL commands contain destructive keywords such as delete, drop, or format. Requires explicit SRE-lead approval before the operation resumes.', tags: ['DESTRUCTIVE_SPL', 'HUMAN_IN_LOOP', 'SRE_APPROVAL'] },
  { policy_id: 'POL-API-12', name: 'Warn on High-Volume Queries', status: 'warn', enabled: true, linkedIncident: 'INC-20260526', description: 'Flags Splunk queries that return more than 10,000 events or execute more than 100 searches in a 5-second window. Action proceeds but evidence is flagged.', tags: ['QUERY_BURST', 'RATE_LIMIT', 'EVIDENCE_FLAG'] },
  { policy_id: 'POL-NET-03', name: 'Block External IP Egress', status: 'block', enabled: true, linkedIncident: null, description: 'Prevents agent network calls to unapproved external IP ranges. Blocks egress attempts not matching the allowlist and records the attempted destination in evidence.', tags: ['EGRESS_BLOCK', 'IP_ALLOWLIST', 'EXFIL_PREVENTION'] },
];

const filters: Array<'all' | PolicyOutcome> = ['all', 'block', 'approval_required', 'warn', 'allow'];

function Metric({ label, value, tone, sub }: { label: string; value: string | number; tone: string; sub: string }) {
  return <div className="bbo-met"><div className="bbo-met-label">{label}</div><div className={`bbo-met-val ${tone}`}>{value}</div><div className="bbo-met-sub">{sub}</div></div>;
}

function policyIcon(status: PolicyOutcome) {
  if (status === 'block') return <ShieldAlert size={15} />;
  if (status === 'approval_required') return <Pause size={15} />;
  if (status === 'warn') return <AlertTriangle size={15} />;
  return <Shield size={15} />;
}

function shortOutcome(status: PolicyOutcome) {
  return status === 'approval_required' ? 'approval_req' : status;
}

function outcomeClass(status: PolicyOutcome) {
  return status;
}

export default function PoliciesPage() {
  const [policies, setPolicies] = useState(fallbackPolicies);
  const [dataMode, setDataMode] = useState<'live' | 'mock'>('mock');
  const [activeFilter, setActiveFilter] = useState<'all' | PolicyOutcome>('all');
  const [selectedId, setSelectedId] = useState('POL-INJ-01');
  const navigate = useNavigate();

  useEffect(() => {
    api.listPolicies()
      .then((items) => {
        if (!items.length) return;
        setDataMode('live');
        setPolicies(items.map((item, index) => ({
          ...item,
          tags: fallbackPolicies[index]?.tags ?? [item.status.toUpperCase()],
          featured: item.policy_id === 'POL-INJ-01' || item.name.toLowerCase().includes('prompt'),
          linkedIncident: fallbackPolicies[index]?.linkedIncident ?? null,
        })));
      })
      .catch(() => undefined);
  }, []);

  const visible = useMemo(() => policies.filter((policy) => activeFilter === 'all' || policy.status === activeFilter), [activeFilter, policies]);
  const activeCount = policies.filter((policy) => policy.enabled).length;
  const blockCount = policies.filter((policy) => policy.status === 'block').length;
  const approvalCount = policies.filter((policy) => policy.status === 'approval_required').length;
  const warnCount = policies.filter((policy) => policy.status === 'warn').length;

  const togglePolicy = (id: string) => {
    const target = policies.find((policy) => policy.policy_id === id);
    if (!target) return;
    const newEnabled = !target.enabled;
    setPolicies((current) => current.map((policy) => policy.policy_id === id ? { ...policy, enabled: newEnabled } : policy));
    api.patchPolicy(id, newEnabled).catch(() => {
      setPolicies((current) => current.map((policy) => policy.policy_id === id ? { ...policy, enabled: !newEnabled } : policy));
    });
  };

  return (
    <div className="bbo-page">
      <div className="bbo-root bbo-policies">
        <div className="bbo-glow-red" />
        <div className="bbo-glow-blue" />
        <BboConsoleNav />
        <section className="bbo-hero">
          <div>
            <div className="bbo-brand-row"><span className="bbo-led red" /><span className="bbo-tag">BlackBoxOps · Safety Gateway</span></div>
            <div className="bbo-hero-title">Rules that stop unsafe agent actions before execution.</div>
            <div className="bbo-hero-sub">BlackBoxOps evaluates every agent operation against named policies that can block, warn, allow, or require human approval. Each decision becomes part of the replayable evidence trail.</div>
            <div className="bbo-source-note"><span className={`bbo-dot ${dataMode === 'live' ? 'green' : 'blue'}`} />{dataMode === 'live' ? 'Live backend policy library loaded' : 'Using local YAML policy library — fail-closed, offline-safe'}</div>
          </div>
          <div className="bbo-gateway-badge"><div className="bbo-gateway-icon"><Shield size={15} /></div><div><div className="bbo-gateway-label">Gateway posture</div><div className="bbo-gateway-val">Fail-closed</div><div className="bbo-gateway-sub">{activeCount} rules active · {blockCount} blocking</div></div></div>
        </section>
        <section className="bbo-metrics">
          <Metric label="Active policies" value={activeCount} tone="green" sub="Currently enabled" />
          <Metric label="Blocking rules" value={blockCount} tone="red" sub="Hard stops" />
          <Metric label="Approval gates" value={approvalCount} tone="amber" sub="Human in loop" />
          <Metric label="Warnings" value={warnCount} tone="blue" sub="Evidence-flagged" />
        </section>
        <section className="bbo-main-grid policies">
          <main className="bbo-policy-list">
            <div className="bbo-list-header"><div className="bbo-label">Policy library · Safety gateway rules</div><div className="bbo-filters">{filters.map((filter) => <button className={`bbo-filter ${activeFilter === filter ? 'active' : ''}`} onClick={() => setActiveFilter(filter)} key={filter}>{filter === 'approval_required' ? 'approval' : filter}</button>)}</div></div>
            <div>
              {visible.map((policy) => (
                <article className={`bbo-policy-card ${policy.featured ? 'featured' : ''} ${selectedId === policy.policy_id ? 'selected' : ''}`} key={policy.policy_id} onClick={() => setSelectedId(policy.policy_id)}>
                  <div className="bbo-policy-top">
                    <div className={`bbo-policy-icon ${outcomeClass(policy.status)}`}>{policyIcon(policy.status)}</div>
                    <div style={{ flex: 1 }}><div className="bbo-policy-name">{policy.name}</div><div className="bbo-policy-id">{policy.policy_id}</div></div>
                    <div className="bbo-policy-right"><span className={`bbo-pill ${outcomeClass(policy.status)}`}>{shortOutcome(policy.status)}</span><button className="bbo-toggle" onClick={(event) => { event.stopPropagation(); togglePolicy(policy.policy_id); }}><span className={`bbo-track ${policy.enabled ? 'on' : 'off'}`}><span className="bbo-thumb" /></span><span className={`bbo-toggle-label ${policy.enabled ? 'on' : 'off'}`}>{policy.enabled ? 'ON' : 'OFF'}</span></button></div>
                  </div>
                  <div className="bbo-policy-desc">{policy.description}</div>
                  <div className="bbo-policy-footer">{policy.tags.map((tag) => <span className="bbo-tag-pill" key={tag}>{tag}</span>)}{policy.featured && <span className="bbo-pill block"><Star size={9} fill="currentColor" />Active in incident replay</span>}{policy.linkedIncident && <span className="bbo-ref"><ArrowRight size={9} />{policy.linkedIncident}</span>}</div>
                </article>
              ))}
              {!visible.length && <div className="bbo-empty"><div className="bbo-empty-icon"><Shield size={26} /></div><div>No policies match this filter.</div><button className="bbo-outline-btn" onClick={() => setActiveFilter('all')}>Show all policies</button></div>}
            </div>
          </main>
          <aside className="bbo-right-rail">
            <div className="bbo-rail-section"><div className="bbo-label">Enforcement model</div>{[
              ['allow', 'Safe action proceeds. Evidence logged.', 'green'],
              ['warn', 'Proceeds with caution flag. Evidence preserved.', 'amber'],
              ['approval_required', 'Execution paused. Human must approve.', 'amber'],
              ['block', 'Execution stopped. Incident recorded.', 'red'],
            ].map(([name, desc, color]) => <div className="bbo-enf-row" key={name}><span className={`bbo-dot ${color}`} style={{ marginTop: 4 }} /><div><div className="bbo-enf-outcome" style={{ color: `var(--bbo-${color})` }}>{name}</div><div className="bbo-enf-desc">{desc}</div></div></div>)}</div>
            <div className="bbo-rail-section"><div className="bbo-label">Gateway stats</div>{[
              ['Total evaluations', '1,402', 'blue'], ['Actions blocked', '38', 'red'], ['Approvals issued', '14', 'amber'], ['Warnings fired', '91', 'amber'], ['Pass rate', '93.4%', 'green'],
            ].map(([label, value, color]) => <div className="bbo-gstat" key={label}><span className="bbo-kv-key">{label}</span><span className="bbo-kv-val" style={{ color: `var(--bbo-${color})`, fontWeight: 700 }}>{value}</span></div>)}</div>
            <div className="bbo-rail-section"><div className="bbo-label">Posture config</div><div className="bbo-gstat"><span className="bbo-kv-key">Mode</span><span className="bbo-kv-val" style={{ color: 'var(--bbo-red)' }}>FAIL-CLOSED</span></div><div className="bbo-gstat"><span className="bbo-kv-key">Source</span><span className="bbo-kv-val">mock_splunk</span></div><div className="bbo-gstat"><span className="bbo-kv-key">MCP-ready</span><span className="bbo-kv-val" style={{ color: 'var(--bbo-green)' }}>YES</span></div></div>
          </aside>
        </section>
        <section className="bbo-demo-callout"><div className="bbo-demo-title"><Shield size={10} /> Demo replay path — powered by POL-INJ-01</div><div className="bbo-demo-body">Policy <span className="bbo-demo-id">POL-INJ-01</span> drives the main incident replay. When a prompt-injection payload appears in Splunk log evidence <span className="bbo-demo-id">EVD-101</span>, this rule fires, blocks the agent action, and records the decision as incident <span className="bbo-demo-id">INC-20260529</span>. Open the incident directory or replay dashboard to see the full evidence chain.</div><div className="bbo-callout-actions"><button className="bbo-outline-btn red" onClick={() => navigate('/dashboard?incident=INC-20260529&autoplay=1')}><Play size={9} fill="currentColor" />Open replay dashboard<ArrowUpRight size={10} /></button><button className="bbo-outline-btn" onClick={() => navigate('/incidents')}>Open incidents directory</button></div></section>
      </div>
    </div>
  );
}
