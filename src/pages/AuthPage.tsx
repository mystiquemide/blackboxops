import { useMemo, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { ArrowLeft, Fingerprint, LockKeyhole, Play, Radar, ShieldCheck } from 'lucide-react';

import { api, AUTH_TOKEN_KEY, AUTH_USER_KEY } from '../api';
import { friendlyError } from '../lib/errors';

type AuthMode = 'signin' | 'signup';

const authEvidenceNodes = [
  [5, 82, 6], [11, 69, 4], [15, 88, 7], [21, 61, 3], [26, 77, 5],
  [32, 91, 4], [38, 67, 8], [44, 83, 4], [51, 58, 3], [57, 74, 5],
  [63, 89, 7], [69, 62, 4], [75, 78, 3], [82, 54, 6], [88, 71, 4], [94, 86, 7],
];

function AuthBackground() {
  return (
    <div className="auth-background" aria-hidden="true">
      <div className="auth-orbit auth-orbit-one" />
      <div className="auth-orbit auth-orbit-two" />
      <div className="auth-orbit auth-orbit-three" />
      {authEvidenceNodes.map(([left, top, size], index) => (
        <span
          key={`${left}-${top}`}
          className={`auth-node ${index % 5 === 0 ? 'auth-node-orange' : ''} ${index % 4 === 0 ? 'auth-node-blue' : ''}`}
          style={{ left: `${left}%`, top: `${top}%`, width: `${size}px`, height: `${size}px`, animationDelay: `${index * -0.37}s` }}
        />
      ))}
      <div className="auth-bg-label auth-bg-query">AUTH TOKEN ISSUED</div>
      <div className="auth-bg-label auth-bg-policy">POLICY GATE READY</div>
      <div className="auth-bg-label auth-bg-evidence">EVIDENCE CHAIN LIVE</div>
    </div>
  );
}

function initialAuthMode(pathname: string, searchMode: string | null): AuthMode {
  if (pathname.includes('signup') || searchMode === 'signup') return 'signup';
  return 'signin';
}

export default function AuthPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [mode, setMode] = useState<AuthMode>(() => initialAuthMode(window.location.pathname, searchParams.get('mode')));
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [sandboxLoading, setSandboxLoading] = useState(false);
  const [error, setError] = useState(searchParams.get('error') ? 'Google sign-in was cancelled or failed. Use email and password below, or try again.' : '');

  const headline = useMemo(
    () => mode === 'signin'
      ? 'Log in with your BlackBoxOps operator credentials.'
      : 'Create a BlackBoxOps operator account.',
    [mode],
  );

  function switchMode(nextMode: AuthMode) {
    setMode(nextMode);
    setError('');
    navigate(nextMode === 'signin' ? '/signin' : '/signup', { replace: true });
  }

  async function submitLocalAuth(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError('');
    try {
      const session = mode === 'signin'
        ? await api.signIn({ email, password })
        : await api.signUp({ name, email, password });
      localStorage.setItem(AUTH_TOKEN_KEY, session.token);
      localStorage.setItem(AUTH_USER_KEY, JSON.stringify(session.user));
      const next = searchParams.get('next');
      navigate(next && next.startsWith('/') ? next : '/dashboard', { replace: true });
    } catch (err) {
      setError(friendlyError(err, mode === 'signin' ? 'Sign in failed. Try again.' : 'Could not create account. Try again.'));
    } finally {
      setSubmitting(false);
    }
  }

  function continueWithGoogle() {
    window.location.href = api.googleLoginUrl();
  }

  async function exploreSandbox() {
    setSandboxLoading(true);
    setError('');
    try {
      const session = await api.demoSession();
      localStorage.setItem(AUTH_TOKEN_KEY, session.token);
      localStorage.setItem(AUTH_USER_KEY, JSON.stringify(session.user));
      const next = searchParams.get('next');
      navigate(next && next.startsWith('/') ? next : '/incidents', { replace: true });
    } catch {
      setError('Sandbox is unavailable right now. Sign in with email and password to continue.');
      setSandboxLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <AuthBackground />
      <div className="auth-orb auth-orb-blue" />
      <div className="auth-orb auth-orb-orange" />
      <nav className="auth-nav">
        <button onClick={() => navigate('/')}><ArrowLeft size={16} /> Back to site</button>
      </nav>

      <section className="auth-shell">
        <aside className="auth-story">
          <div className="auth-kicker"><Radar size={16} /> BLACKBOXOPS OPERATOR ACCESS</div>
          <h1>{headline}</h1>
          <div className="auth-proof-cards">
            <article><ShieldCheck /><b>Policy-aware access</b><span>Every session routes through the safety gateway before replay.</span></article>
            <article><Fingerprint /><b>Evidence-bound identity</b><span>Sessions carry operator identity for audit context and postmortems.</span></article>
            <article><LockKeyhole /><b>Persistent workspace</b><span>Incidents, policy decisions, and evidence chains persist to your account.</span></article>
          </div>
        </aside>

        <div className="auth-card">

          {/* Sandbox - primary path */}
          <div className="auth-sandbox-block">
            <div className="auth-sandbox-live-bar">
              <span className="auth-sandbox-live-dot" />
              <span className="auth-sandbox-live-label">LIVE</span>
              <span className="auth-sandbox-live-id">incident-2924 · prompt injection</span>
            </div>
            <div className="auth-sandbox-inner">
              <div className="auth-sandbox-title">See BlackBoxOps intercept an injection</div>
              <p className="auth-sandbox-sub">Pre-loaded incident playing back now. Explore it after you enter.</p>
              <div className="auth-sandbox-trace">
                <div className="auth-sandbox-trace-row">
                  <span className="ast-dot" />
                  <div className="ast-body">
                    <span className="ast-tool">splunk_run_query</span>
                    <code className="ast-code">SELECT * FROM users WHERE id = :id OR 1=1</code>
                  </div>
                  <span className="ast-tag ast-tag-logged">logged</span>
                </div>
                <div className="auth-sandbox-trace-row ast-row-danger">
                  <span className="ast-dot ast-dot-red" />
                  <div className="ast-body">
                    <span className="ast-tool ast-tool-red">policy_gate</span>
                    <code className="ast-code ast-code-red">injection_detected · BLOCKED</code>
                  </div>
                  <span className="ast-tag ast-tag-blocked">blocked</span>
                </div>
                <div className="auth-sandbox-trace-row">
                  <span className="ast-dot ast-dot-green" />
                  <div className="ast-body">
                    <span className="ast-tool ast-tool-green">postmortem_seal</span>
                    <code className="ast-code ast-code-green">evidence_sealed · confidence 0.94</code>
                  </div>
                  <span className="ast-tag ast-tag-ready">ready</span>
                </div>
              </div>
              <button
                className="auth-sandbox-cta"
                onClick={exploreSandbox}
                disabled={sandboxLoading}
                type="button"
              >
                <Play size={13} fill="currentColor" />
                {sandboxLoading ? 'Loading sandbox...' : 'Explore sandbox'}
              </button>
              <p className="auth-sandbox-note">No account required. Sandbox resets each session.</p>
            </div>
          </div>

          <div className="auth-divider"><span /> or sign in to your account <span /></div>

          {/* Real account - secondary path */}
          <div className="auth-card-top">
            <div>
              <span>Operator workspace</span>
              <h2>{mode === 'signin' ? 'Sign in' : 'Create account'}</h2>
            </div>
          </div>

          <div className="auth-tabs" role="tablist" aria-label="Authentication mode">
            <button className={mode === 'signin' ? 'active' : ''} onClick={() => switchMode('signin')} type="button">Sign in</button>
            <button className={mode === 'signup' ? 'active' : ''} onClick={() => switchMode('signup')} type="button">Sign up</button>
          </div>

          <form className="auth-form" onSubmit={submitLocalAuth}>
            {mode === 'signup' && (
              <label>
                Name
                <input value={name} onChange={(event) => setName(event.target.value)} placeholder="Your name" required minLength={1} maxLength={80} />
              </label>
            )}
            <label>
              Email
              <input value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@company.com" required type="email" />
            </label>
            <label>
              Password
              <input value={password} onChange={(event) => setPassword(event.target.value)} placeholder={mode === 'signin' ? 'Your password' : 'Create a password (8+ chars)'} required minLength={mode === 'signup' ? 8 : 1} type="password" />
            </label>
            {error && <p className="auth-error">{error}</p>}
            <button className="auth-primary" disabled={submitting} type="submit">
              {submitting ? 'Securing workspace...' : mode === 'signin' ? 'Sign in' : 'Create account'}
            </button>
          </form>

          <div className="auth-divider auth-divider-slim"><span /> or <span /></div>

          <button className="auth-primary auth-google" onClick={continueWithGoogle} type="button">
            <span className="google-mark" aria-hidden="true">G</span>
            Continue with Google
          </button>
        </div>
      </section>
    </main>
  );
}
