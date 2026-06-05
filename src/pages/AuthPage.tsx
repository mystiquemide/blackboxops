import { useMemo, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { ArrowLeft, Fingerprint, LockKeyhole, Radar, ShieldCheck, Sparkles } from 'lucide-react';

import { api, AUTH_TOKEN_KEY, AUTH_USER_KEY } from '../api';

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
  const [error, setError] = useState(searchParams.get('error') ? 'Authentication failed. Try again or use email and password.' : '');

  const headline = useMemo(
    () => mode === 'signin' ? 'Log in with your existing BlackBoxOps operator credentials.' : 'Create a new BlackBoxOps operator account for this demo workspace.',
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
      setError(err instanceof Error ? err.message : 'Authentication failed');
    } finally {
      setSubmitting(false);
    }
  }

  function continueWithGoogle() {
    window.location.href = api.googleLoginUrl();
  }

  function continueWithDemo() {
    const session = {
      token: 'demo-preview-token',
      user: { email: 'judge@blackboxops.demo', name: 'Judge Demo', provider: 'demo' },
    };
    localStorage.setItem(AUTH_TOKEN_KEY, session.token);
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(session.user));
    const next = searchParams.get('next');
    navigate(next && next.startsWith('/') ? next : '/incidents', { replace: true });
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
          <div className="auth-kicker"><Radar size={16} /> BLACKBOXOPS IDENTITY GATE</div>
          <h1>{headline}</h1>
          <div className="auth-proof-cards">
            <article><ShieldCheck /><b>Policy-aware access</b><span>Route operators into the safety gateway before replay.</span></article>
            <article><Fingerprint /><b>Evidence-bound identity</b><span>Every session carries a user identity for audit context.</span></article>
            <article><LockKeyhole /><b>Operator accounts</b><span>Log in with existing credentials, or sign up only when creating a new account.</span></article>
          </div>
        </aside>

        <div className="auth-card">
          <div className="auth-card-top">
            <div>
              <span>Secure workspace</span>
              <h2>{mode === 'signin' ? 'Log in' : 'Sign up'}</h2>
            </div>
          </div>

          <div className="auth-tabs" role="tablist" aria-label="Authentication mode">
            <button className={mode === 'signin' ? 'active' : ''} onClick={() => switchMode('signin')} type="button">Log in</button>
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
              <input value={email} onChange={(event) => setEmail(event.target.value)} placeholder="email@gmail.com" required type="email" />
            </label>
            <label>
              Password
              <input value={password} onChange={(event) => setPassword(event.target.value)} placeholder={mode === 'signin' ? 'Your password' : 'Create a password'} required minLength={mode === 'signup' ? 8 : 1} type="password" />
            </label>
            {error && <p className="auth-error">{error}</p>}
            <button className="auth-primary" disabled={submitting} type="submit">
              {submitting ? 'Securing workspace...' : mode === 'signin' ? 'Log in to dashboard' : 'Create account'}
            </button>
            <button className="auth-demo-button" onClick={continueWithDemo} type="button">
              <Sparkles size={15} /> Enter judge demo
            </button>
            <div className="auth-divider"><span /> Optional OAuth <span /></div>
            <button className="auth-primary auth-google" onClick={continueWithGoogle} type="button">
              <span className="google-mark" aria-hidden="true">G</span>
              Continue with Google
            </button>
            <p className="auth-helper">
              {mode === 'signin'
                ? 'Log in with existing credentials, or enter the judge demo for the deterministic Splunk replay.'
                : 'Create a new local operator account. The judge demo remains available if OAuth is not configured.'}
            </p>
          </form>
        </div>
      </section>
    </main>
  );
}
