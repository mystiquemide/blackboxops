import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Play, Search } from 'lucide-react';

import BboConsoleNav from '../components/BboConsoleNav';
import { api } from '../api';

type IncidentTone = 'critical' | 'high' | 'medium' | 'low';
type IncidentStatus = 'blocked' | 'approval' | 'allowed' | 'warned';

type IncidentRow = {
  id: string;
  time: string;
  actor: string;
  risk: IncidentTone;
  status: IncidentStatus;
  trigger: string;
  description: string;
  evidenceRefs: number;
  policyOutcome: string;
  source: string;
  policy: string;
};

const fallbackIncidents: IncidentRow[] = [
  { id: 'INC-20260529', source: 'mock_splunk', trigger: 'Prompt-injection checkout latency incident', description: 'Malicious payload in user input field — SQL injection + data exfiltration attempt. Policy gateway blocked agent action before execution.', time: '2026-05-29 09:14Z', actor: 'bb-agent/checkout-v2', risk: 'critical', status: 'blocked', evidenceRefs: 3, policy: 'POL-INJ-01', policyOutcome: 'PROMPT_INJECTION' },
  { id: 'INC-20260528', source: 'splunk:infra-audit', trigger: 'Unsafe remediation restart proposal', description: 'Agent proposed restarting the payment-processing pod during a live transaction window without runbook sign-off. Approval gate activated.', time: '2026-05-28 14:37Z', actor: 'bb-agent/infra-remediator', risk: 'high', status: 'approval', evidenceRefs: 2, policy: 'POL-APPR-002', policyOutcome: 'UNSAFE_RESTART' },
  { id: 'INC-20260527', source: 'splunk:checkout-logs', trigger: 'Read-only diagnostic sweep — checkout pipeline', description: 'Agent performed authorized read-only query sweep across checkout anomaly index. No write operations. Evidence chain verified. Allowed.', time: '2026-05-27 11:08Z', actor: 'bb-agent/diagnostic-v1', risk: 'low', status: 'allowed', evidenceRefs: 2, policy: 'POL-SEC-001', policyOutcome: 'DIAGNOSTIC_SWEEP' },
  { id: 'INC-20260526', source: 'splunk:infra-audit', trigger: 'High-volume query burst — infra audit index', description: 'Agent issued 847 queries in 4 seconds against infra-audit index. Rate limit warn triggered. No policy block; operational review recommended.', time: '2026-05-26 22:51Z', actor: 'bb-agent/log-sweeper', risk: 'medium', status: 'warned', evidenceRefs: 2, policy: 'POL-WARN-007', policyOutcome: 'QUERY_BURST' },
  { id: 'INC-20260525', source: 'mock_splunk', trigger: 'Credential exposure in agent log output', description: 'Agent surfaced sensitive credential-shaped output in debug logs. Content was quarantined and policy triggered immediate block.', time: '2026-05-25 16:22Z', actor: 'bb-agent/debug-trace', risk: 'critical', status: 'blocked', evidenceRefs: 3, policy: 'POL-SEC-009', policyOutcome: 'CREDENTIAL_EXPOSURE' },
  { id: 'INC-20260524', source: 'splunk:checkout-logs', trigger: 'Baseline checkout session — normal ops', description: 'Routine checkout monitoring session. 847 transactions logged. No anomalies detected. Evidence archived for audit trail continuity.', time: '2026-05-24 08:00Z', actor: 'bb-agent/checkout-v2', risk: 'low', status: 'allowed', evidenceRefs: 1, policy: 'POL-SEC-001', policyOutcome: 'BASELINE_MONITOR' },
];

const filters: Array<'all' | IncidentTone> = ['all', 'critical', 'high', 'medium', 'low'];

function normalizeRisk(value: string, title = ''): IncidentTone {
  const lower = `${value} ${title}`.toLowerCase();
  if (lower.includes('prompt') || lower.includes('critical') || lower.includes('block')) return 'critical';
  if (lower.includes('high')) return 'high';
  if (lower.includes('low')) return 'low';
  return 'medium';
}

function normalizeStatus(status: string, title = ''): IncidentStatus {
  const lower = `${status} ${title}`.toLowerCase();
  if (lower.includes('approval')) return 'approval';
  if (lower.includes('allow')) return 'allowed';
  if (lower.includes('warn')) return 'warned';
  if (lower.includes('block') || lower.includes('prompt')) return 'blocked';
  return 'warned';
}

function Metric({ label, value, tone, sub, small = false }: { label: string; value: string | number; tone: string; sub: string; small?: boolean }) {
  return <div className="bbo-met"><div className="bbo-met-label">{label}</div><div className={`bbo-met-val ${tone} ${small ? 'small' : ''}`}>{value}</div><div className="bbo-met-sub">{sub}</div></div>;
}

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState(fallbackIncidents);
  const [dataMode, setDataMode] = useState<'live' | 'mock'>('mock');
  const [activeFilter, setActiveFilter] = useState<'all' | IncidentTone>('all');
  const [query, setQuery] = useState('');
  const [selectedId, setSelectedId] = useState('INC-20260529');
  const navigate = useNavigate();

  useEffect(() => {
    api.listIncidents()
      .then((items) => {
        if (!items.length) return;
        setDataMode('live');
        setIncidents(items.map((item, index) => ({
          id: item.incident_id,
          time: fallbackIncidents[index]?.time ?? '2026-05-29 09:14Z',
          actor: fallbackIncidents[index]?.actor ?? 'bb-agent/checkout-v2',
          risk: normalizeRisk(item.severity, item.title),
          status: normalizeStatus(item.status, item.title),
          trigger: item.title,
          description: item.description,
          evidenceRefs: item.title.toLowerCase().includes('prompt') ? 3 : 2,
          policyOutcome: fallbackIncidents[index]?.policyOutcome ?? 'REPLAY_AVAILABLE',
          source: fallbackIncidents[index]?.source ?? 'mock_splunk',
          policy: item.title.toLowerCase().includes('prompt') ? 'POL-INJ-01' : 'POL-SEC-001',
        })));
      })
      .catch(() => undefined);
  }, []);

  const visibleIncidents = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return incidents.filter((incident) => {
      const matchesFilter = activeFilter === 'all' || incident.risk === activeFilter;
      const matchesQuery = !needle || [incident.id, incident.actor, incident.trigger, incident.description, incident.policyOutcome, incident.source, incident.policy, incident.status]
        .some((field) => field.toLowerCase().includes(needle));
      return matchesFilter && matchesQuery;
    });
  }, [activeFilter, incidents, query]);

  const featured = incidents.find((incident) => incident.id === selectedId) ?? incidents[0];
  const blockedCount = incidents.filter((incident) => incident.status === 'blocked').length;
  const gatedCount = incidents.filter((incident) => incident.status === 'approval').length;
  const evidenceTotal = incidents.reduce((sum, incident) => sum + incident.evidenceRefs, 0);
  const criticalCount = incidents.filter((incident) => incident.risk === 'critical').length;

  return (
    <div className="bbo-page">
      <div className="bbo-root bbo-incidents">
        <div className="bbo-glow-orange" />
        <BboConsoleNav />
        <section className="bbo-hero">
          <div>
            <div className="bbo-brand-row"><span className="bbo-led orange" /><span className="bbo-tag">BlackBoxOps · Incident Directory</span></div>
            <div className="bbo-hero-title">Every agent operation, replayable with evidence.</div>
          <div className="bbo-hero-sub">BlackBoxOps turns AI ops activity into a forensic incident directory: status, policy outcome, Splunk source, and the evidence_refs needed to prove what happened.</div>
            <div className="bbo-source-note"><span className={`bbo-dot ${dataMode === 'live' ? 'green' : 'red'}`} />{dataMode === 'live' ? 'Live backend incidents loaded' : 'Splunk connector required for live incident data'}</div>
          </div>
          <div className="bbo-posture"><span className="bbo-led" /><div><div className="bbo-posture-label">Live posture</div><div className="bbo-posture-val">{blockedCount} blocked · {gatedCount} gated</div><div className="bbo-op-role">SAFETY LAYER ACTIVE</div></div></div>
        </section>
        <section className="bbo-metrics">
          <Metric label="Incidents" value={incidents.length} tone="blue" sub="Captured sessions" />
          <Metric label="Evidence refs" value={evidenceTotal} tone="blue" sub="Splunk-bound claims" />
          <Metric label="Critical" value={criticalCount} tone="red" sub="High-risk intercepts" />
          <Metric label="Demo path" value="READY" tone="green" sub="Deterministic replay" small />
        </section>
        <section className="bbo-main-grid incidents">
          <aside className="bbo-priority-col">
            <div>
              <div className="bbo-label">Priority case</div>
              <div className="bbo-priority-card">
                <div className="bbo-row-between"><div className="bbo-pc-id">{featured.id}</div><div className="bbo-inc-pills"><span className={`bbo-pill ${featured.status}`}>{featured.status === 'approval' ? 'approval req' : featured.status}</span><span className={`bbo-risk ${featured.risk}`}>{featured.risk}</span></div></div>
                <div className="bbo-pc-title">{featured.trigger}</div>
                <div className="bbo-pc-desc">{featured.description}</div>
                <div className="bbo-kv"><span className="bbo-kv-key">actor</span><span className="bbo-kv-val">{featured.actor}</span></div>
                <div className="bbo-kv"><span className="bbo-kv-key">source</span><span className="bbo-kv-val">{featured.source}</span></div>
                <div className="bbo-kv"><span className="bbo-kv-key">policy</span><span className="bbo-kv-val" style={{ color: 'var(--bbo-red)' }}>{featured.policy}</span></div>
                <div><div className="bbo-kv-key" style={{ marginBottom: 4 }}>evidence_refs</div><div className="bbo-inc-pills">{Array.from({ length: featured.evidenceRefs }, (_, index) => <span className="bbo-ref" key={index}>EVD-{100 + index}</span>)}</div></div>
                <button className="bbo-danger-btn" onClick={() => navigate(`/dashboard?incident=${featured.id}&autoplay=1`)}><Play size={10} fill="currentColor" /> Open in replay room</button>
              </div>
            </div>
            <div><div className="bbo-label">Policy legend</div><div className="bbo-legend"><div className="bbo-legend-row"><span className="bbo-dot red" />Blocked — unsafe action stopped</div><div className="bbo-legend-row"><span className="bbo-dot amber" />Approval required — human gate</div><div className="bbo-legend-row"><span className="bbo-dot green" />Allowed — safe, evidence-backed</div><div className="bbo-legend-row"><span className="bbo-dot blue" />Warned — review recommended</div></div></div>
            <div><div className="bbo-label">Capture sources</div><div className="bbo-legend"><div className="bbo-legend-row"><span className="bbo-dot orange" />splunk sample dataset</div><div className="bbo-legend-row"><span className="bbo-dot blue" />splunk:checkout-logs</div><div className="bbo-legend-row"><span className="bbo-dot muted" />splunk:infra-audit</div></div></div>
          </aside>
          <main className="bbo-directory">
            <div className="bbo-dir-header">
              <label className="bbo-search"><Search /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search incident ID, actor, trigger, policy..." /></label>
              <div className="bbo-filters">{filters.map((filter) => <button key={filter} className={`bbo-filter ${activeFilter === filter ? 'active' : ''}`} onClick={() => setActiveFilter(filter)}>{filter}</button>)}</div>
            </div>
            <div>
              {visibleIncidents.map((incident) => (
                <article className={`bbo-inc-row ${incident.id === selectedId ? 'selected' : ''}`} key={incident.id} onClick={() => setSelectedId(incident.id)}>
                  <div className="bbo-inc-top"><span className="bbo-inc-id">{incident.id}</span><span className="bbo-source">{incident.source}</span><span className="bbo-inc-title">{incident.trigger}</span><div className="bbo-inc-pills"><span className={`bbo-risk ${incident.risk}`}>{incident.risk}</span><span className={`bbo-pill ${incident.status}`}>{incident.status === 'approval' ? 'approval req' : incident.status}</span></div></div>
                  <div className="bbo-inc-bottom"><span className="bbo-inc-desc">{incident.description}</span><div className="bbo-inc-meta"><span className="bbo-muted">{incident.time}</span><span className="bbo-ev-id">{incident.actor}</span><span className="bbo-ref">{incident.evidenceRefs} ev</span><button className="bbo-outline-btn" onClick={(event) => { event.stopPropagation(); navigate(`/dashboard?incident=${incident.id}&autoplay=1`); }}>▶ Replay</button></div></div>
                </article>
              ))}
              {!visibleIncidents.length && <div className="bbo-empty"><div className="bbo-empty-icon">⌕</div><div>No incidents match this filter.</div><button className="bbo-outline-btn" onClick={() => { setActiveFilter('all'); setQuery(''); }}>Reset filters</button></div>}
            </div>
          </main>
        </section>
      </div>
    </div>
  );
}
