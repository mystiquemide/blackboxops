import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle2, KeyRound, LogOut, ShieldCheck, User } from 'lucide-react';
import { api, AUTH_TOKEN_KEY, AUTH_USER_KEY } from '../api';
import BboConsoleNav from '../components/BboConsoleNav';

function useCurrentUser() {
  const raw = localStorage.getItem(AUTH_USER_KEY);
  if (!raw) return null;
  try { return JSON.parse(raw) as { name: string; email: string; provider: string; picture?: string }; }
  catch { return null; }
}

function userInitials(name: string): string {
  return name.split(' ').map((n) => n[0] ?? '').slice(0, 2).join('').toUpperCase() || '?';
}

export default function AccountPage() {
  const navigate = useNavigate();
  const user = useCurrentUser();

  const [name, setName] = useState(user?.name ?? '');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [profileMsg, setProfileMsg] = useState<{ type: 'ok' | 'err'; text: string } | null>(null);
  const [passwordMsg, setPasswordMsg] = useState<{ type: 'ok' | 'err'; text: string } | null>(null);
  const [savingProfile, setSavingProfile] = useState(false);
  const [savingPassword, setSavingPassword] = useState(false);

  if (!user) {
    navigate('/signin', { replace: true });
    return null;
  }

  const isLocal = user.provider === 'local';
  const isSandbox = user.provider === 'demo';

  async function saveProfile(event: React.FormEvent) {
    event.preventDefault();
    if (!name.trim()) return;
    setSavingProfile(true);
    setProfileMsg(null);
    try {
      const updated = await api.updateProfile({ name: name.trim() });
      const stored = JSON.parse(localStorage.getItem(AUTH_USER_KEY) ?? '{}');
      localStorage.setItem(AUTH_USER_KEY, JSON.stringify({ ...stored, name: updated.name }));
      setProfileMsg({ type: 'ok', text: 'Profile updated.' });
    } catch (err) {
      setProfileMsg({ type: 'err', text: err instanceof Error ? err.message : 'Update failed.' });
    } finally {
      setSavingProfile(false);
    }
  }

  async function savePassword(event: React.FormEvent) {
    event.preventDefault();
    if (newPassword.length < 8) {
      setPasswordMsg({ type: 'err', text: 'New password must be at least 8 characters.' });
      return;
    }
    setSavingPassword(true);
    setPasswordMsg(null);
    try {
      await api.updateProfile({ current_password: currentPassword, new_password: newPassword });
      setCurrentPassword('');
      setNewPassword('');
      setPasswordMsg({ type: 'ok', text: 'Password updated.' });
    } catch (err) {
      setPasswordMsg({ type: 'err', text: err instanceof Error ? err.message : 'Update failed.' });
    } finally {
      setSavingPassword(false);
    }
  }

  function signOut() {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(AUTH_USER_KEY);
    navigate('/signin', { replace: true });
  }

  return (
    <div className="bbo-account-page">
      <BboConsoleNav />
      <div className="bbo-account-shell">

        <header className="bbo-account-header">
          <div className="bbo-account-avatar-lg">{userInitials(user.name)}</div>
          <div>
            <div className="bbo-account-title">{user.name}</div>
            <div className="bbo-account-email">{user.email}</div>
            <span className={`bbo-account-badge ${user.provider}`}>{user.provider === 'demo' ? 'Sandbox session' : user.provider === 'google' ? 'Google account' : 'Email account'}</span>
          </div>
        </header>

        {isSandbox && (
          <div className="bbo-account-notice">
            <ShieldCheck size={15} />
            You're in a sandbox session. Create a real account to save incidents, customize policies, and keep your workspace between sessions.
            <button onClick={() => navigate('/signup')} type="button">Create account</button>
          </div>
        )}

        <div className="bbo-account-grid">

          <section className="bbo-account-section">
            <div className="bbo-account-section-title"><User size={14} /> Profile</div>
            <form onSubmit={saveProfile} className="bbo-account-form">
              <label>
                Display name
                <input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Your name"
                  required
                  minLength={1}
                  maxLength={80}
                  disabled={isSandbox}
                />
              </label>
              <label>
                Email
                <input value={user.email} disabled type="email" />
              </label>
              {profileMsg && (
                <p className={`bbo-account-msg ${profileMsg.type}`}>
                  {profileMsg.type === 'ok' && <CheckCircle2 size={13} />} {profileMsg.text}
                </p>
              )}
              <button className="bbo-account-btn" type="submit" disabled={savingProfile || isSandbox}>
                {savingProfile ? 'Saving...' : 'Save profile'}
              </button>
            </form>
          </section>

          {isLocal && (
            <section className="bbo-account-section">
              <div className="bbo-account-section-title"><KeyRound size={14} /> Change password</div>
              <form onSubmit={savePassword} className="bbo-account-form">
                <label>
                  Current password
                  <input
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    type="password"
                    placeholder="Current password"
                    required
                  />
                </label>
                <label>
                  New password
                  <input
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    type="password"
                    placeholder="New password (8+ chars)"
                    required
                    minLength={8}
                  />
                </label>
                {passwordMsg && (
                  <p className={`bbo-account-msg ${passwordMsg.type}`}>
                    {passwordMsg.type === 'ok' && <CheckCircle2 size={13} />} {passwordMsg.text}
                  </p>
                )}
                <button className="bbo-account-btn" type="submit" disabled={savingPassword}>
                  {savingPassword ? 'Updating...' : 'Update password'}
                </button>
              </form>
            </section>
          )}

          <section className="bbo-account-section bbo-account-section-danger">
            <div className="bbo-account-section-title"><LogOut size={14} /> Session</div>
            <p className="bbo-account-section-sub">Sign out of your current session on this device.</p>
            <button className="bbo-account-btn danger" onClick={signOut} type="button">
              Sign out
            </button>
          </section>

        </div>
      </div>
    </div>
  );
}
