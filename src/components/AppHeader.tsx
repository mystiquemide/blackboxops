import { Link, useLocation } from 'react-router-dom';

export default function AppHeader() {
  const location = useLocation();

  const getLinkStyle = (path: string) => {
    const isActive = location.pathname === path;
    return {
      textDecoration: 'none',
      color: isActive ? 'var(--white)' : 'var(--textMuted)',
      fontWeight: isActive ? 600 : 400,
      borderBottom: isActive ? '2px solid var(--splunkGreen)' : '2px solid transparent',
      paddingBottom: '4px',
      transition: 'all 0.2s ease',
    };
  };

  return (
    <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', paddingBottom: '1rem', borderBottom: '1px solid var(--border)' }}>
      {/* Brand */}
      <Link to="/" style={{ textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '10px' }}>
        <div style={{ width: '24px', height: '14px', borderRadius: '4px', border: '1px solid var(--borderStrong)', background: 'linear-gradient(90deg, #111827 0 68%, var(--blackboxOrange) 68% 100%)', position: 'relative' }}>
            <div style={{ position: 'absolute', right: '3px', top: '4px', width: '4px', height: '4px', borderRadius: '999px', background: 'var(--splunkGreen)', boxShadow: '0 0 8px var(--splunkGreen)' }} />
        </div>
        <span style={{ color: 'var(--textPrimary)', fontWeight: 800 }}>BlackBox<span style={{ color: 'var(--splunkGreen)' }}>Ops</span></span>
      </Link>

      {/* Internal Navigation */}
      <div style={{ display: 'flex', gap: '24px', alignItems: 'center' }}>
        <Link to="/dashboard" style={getLinkStyle('/dashboard')}>Replay</Link>
        <Link to="/incidents" style={getLinkStyle('/incidents')}>Incidents</Link>
        <Link to="/policies" style={getLinkStyle('/policies')}>Policies</Link>
      </div>

      {/* Status */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <span className="badge badge-low">● System Online</span>
      </div>
    </header>
  );
}
