import { useEffect, useState } from 'react';
import { NavLink, Link, useNavigate } from 'react-router-dom';
import { AUTH_TOKEN_KEY, AUTH_USER_KEY } from '../api';

export default function BboConsoleNav() {
  const navigate = useNavigate();
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);

  useEffect(() => {
    let mounted = true;
    const controller = new AbortController();
    fetch('/api/health', { signal: controller.signal })
      .then((response) => { if (mounted) setApiOnline(response.ok); })
      .catch(() => { if (mounted) setApiOnline(false); });
    return () => { mounted = false; controller.abort(); };
  }, []);

  function logout() {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(AUTH_USER_KEY);
    navigate('/signin', { replace: true });
  }

  const statusText = apiOnline === null ? 'Checking backend' : apiOnline ? 'Backend connected' : 'Mock fallback';
  const statusClass = apiOnline === false ? 'offline' : apiOnline === null ? 'checking' : '';

  return (
    <nav className="bbo-topnav">
      <Link to="/" className="bbo-brand">
        <span className="bbo-brand-mark" />
        <span>BlackBox<span>Ops</span></span>
      </Link>
      <div className="bbo-navlinks">
        <NavLink to="/dashboard" className={({ isActive }) => isActive ? 'active' : ''}>Replay</NavLink>
        <NavLink to="/incidents" className={({ isActive }) => isActive ? 'active' : ''}>Incidents</NavLink>
        <NavLink to="/policies" className={({ isActive }) => isActive ? 'active' : ''}>Policies</NavLink>
      </div>
      <div className="bbo-top-actions">
        <div className={`bbo-system-pill ${statusClass}`}><i /> {statusText}</div>
        <button className="bbo-logout" onClick={logout} type="button">Log out</button>
      </div>
    </nav>
  );
}
