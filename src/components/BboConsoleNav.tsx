import { useEffect, useRef, useState } from 'react';
import { NavLink, Link, useNavigate } from 'react-router-dom';
import { ChevronDown, LogOut, Settings, User } from 'lucide-react';
import { AUTH_TOKEN_KEY, AUTH_USER_KEY } from '../api';

function userInitials(name: string): string {
  return name
    .split(' ')
    .map((n) => n[0] ?? '')
    .slice(0, 2)
    .join('')
    .toUpperCase() || '?';
}

function useCurrentUser() {
  const raw = localStorage.getItem(AUTH_USER_KEY);
  if (!raw) return null;
  try { return JSON.parse(raw) as { name: string; email: string; provider: string; picture?: string }; }
  catch { return null; }
}

export default function BboConsoleNav() {
  const navigate = useNavigate();
  const user = useCurrentUser();
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let mounted = true;
    const controller = new AbortController();
    fetch('/api/health', { signal: controller.signal })
      .then((response) => { if (mounted) setApiOnline(response.ok); })
      .catch(() => { if (mounted) setApiOnline(false); });
    return () => { mounted = false; controller.abort(); };
  }, []);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  function logout() {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(AUTH_USER_KEY);
    navigate('/signin', { replace: true });
  }

  const statusText = apiOnline === null ? 'Checking' : apiOnline ? 'Connected' : 'Offline';
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
        <div className={`bbo-system-pill ${statusClass}`}><i />{statusText}</div>

        {user && (
          <>
            <div className="bbo-user-menu" ref={menuRef}>
              <button
                className="bbo-user-trigger"
                onClick={() => setMenuOpen((prev) => !prev)}
                type="button"
                aria-haspopup="true"
                aria-expanded={menuOpen}
              >
                {user.picture
                  ? <img className="bbo-avatar bbo-avatar-photo" src={user.picture} alt={user.name} referrerPolicy="no-referrer" />
                  : <span className="bbo-avatar">{userInitials(user.name)}</span>}
                <span className="bbo-user-name">{user.name.split(' ')[0]}</span>
                <ChevronDown size={12} className={menuOpen ? 'bbo-chevron open' : 'bbo-chevron'} />
              </button>

              {menuOpen && (
                <div className="bbo-dropdown" role="menu">
                  <div className="bbo-dropdown-header">
                    <div className="bbo-dropdown-header-top">
                      {user.picture
                        ? <img className="bbo-dropdown-avatar-photo" src={user.picture} alt={user.name} referrerPolicy="no-referrer" />
                        : <span className="bbo-dropdown-avatar-initials">{userInitials(user.name)}</span>}
                      <div>
                        <div className="bbo-dropdown-name">{user.name}</div>
                        <div className="bbo-dropdown-email">{user.email}</div>
                      </div>
                    </div>
                    <span className="bbo-dropdown-provider">{user.provider}</span>
                  </div>
                  <div className="bbo-dropdown-divider" />
                  <button
                    className="bbo-dropdown-item"
                    onClick={() => { setMenuOpen(false); navigate('/account'); }}
                    type="button"
                    role="menuitem"
                  >
                    <Settings size={13} /> Account settings
                  </button>
                  <button
                    className="bbo-dropdown-item"
                    onClick={() => { setMenuOpen(false); navigate('/account'); }}
                    type="button"
                    role="menuitem"
                  >
                    <User size={13} /> Profile
                  </button>
                  <div className="bbo-dropdown-divider" />
                  <button
                    className="bbo-dropdown-item bbo-dropdown-danger"
                    onClick={logout}
                    type="button"
                    role="menuitem"
                  >
                    <LogOut size={13} /> Sign out
                  </button>
                </div>
              )}
            </div>

            <button className="bbo-logout" onClick={logout} type="button">
              <LogOut size={11} style={{ verticalAlign: 'middle', marginRight: 4 }} />
              Sign out
            </button>
          </>
        )}
      </div>
    </nav>
  );
}
