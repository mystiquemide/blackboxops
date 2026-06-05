import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { CheckCircle2, Loader2, ShieldCheck } from 'lucide-react';

import { api, AUTH_TOKEN_KEY, AUTH_USER_KEY } from '../api';

export default function AuthCallbackPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [message, setMessage] = useState('Verifying Google identity...');

  useEffect(() => {
    const token = searchParams.get('token');
    if (!token) {
      navigate('/signin?error=missing-token', { replace: true });
      return;
    }
    const verifiedToken = token;

    async function finishAuth() {
      try {
        localStorage.setItem(AUTH_TOKEN_KEY, verifiedToken);
        const user = await api.me(verifiedToken);
        localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
        setMessage('Google identity verified. Opening workspace...');
        window.setTimeout(() => navigate('/dashboard', { replace: true }), 300);
      } catch {
        localStorage.removeItem(AUTH_TOKEN_KEY);
        localStorage.removeItem(AUTH_USER_KEY);
        navigate('/signin?error=auth-callback', { replace: true });
      }
    }

    void finishAuth();
  }, [navigate, searchParams]);

  return (
    <main className="auth-page auth-callback-page">
      <div className="auth-orb auth-orb-blue" />
      <div className="auth-orb auth-orb-orange" />
      <section className="auth-callback-card">
        <div className="auth-callback-icon"><ShieldCheck size={26} /></div>
        <h1>Securing workspace</h1>
        <p>{message}</p>
        <div className="auth-status"><CheckCircle2 size={14} /> Google OAuth callback received</div>
        <Loader2 className="auth-spinner" size={22} />
      </section>
    </main>
  );
}
