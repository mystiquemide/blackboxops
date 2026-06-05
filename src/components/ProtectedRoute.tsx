import { Navigate, useLocation } from 'react-router-dom';
import { AUTH_TOKEN_KEY, AUTH_USER_KEY } from '../api';

type ProtectedRouteProps = {
  children: React.ReactNode;
};

function hasLocalSession() {
  return Boolean(localStorage.getItem(AUTH_TOKEN_KEY) && localStorage.getItem(AUTH_USER_KEY));
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const location = useLocation();

  if (!hasLocalSession()) {
    const next = `${location.pathname}${location.search}${location.hash}`;
    return <Navigate to={`/signin?next=${encodeURIComponent(next)}`} replace />;
  }

  return children;
}
