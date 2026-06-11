const STATUS_MESSAGES: Record<number, string> = {
  401: 'Your session expired. Sign in again.',
  403: 'You don\'t have permission to do that.',
  404: 'That resource wasn\'t found.',
  409: 'A conflict occurred. The item may already exist.',
  429: 'Too many requests. Wait a moment and try again.',
  500: 'Something went wrong on our end. Try again in a moment.',
  502: 'The server is temporarily unreachable. Try again shortly.',
  503: 'The service is temporarily down. Try again shortly.',
};

const CONTENT_MATCHES: [RegExp, string][] = [
  [/already exists/i, 'An account with that email already exists. Try signing in instead.'],
  [/invalid email or password/i, 'Wrong email or password. Double-check and try again.'],
  [/current password is incorrect/i, 'Your current password is wrong.'],
  [/current password required/i, 'Enter your current password to make this change.'],
  [/password change not available/i, 'Password changes aren\'t available for accounts signed in with Google.'],
  [/missing bearer|invalid bearer/i, 'Your session expired. Sign in again.'],
  [/user not found/i, 'Account not found.'],
  [/failed to fetch|networkerror|load failed|network request failed/i, 'Connection error. Check your internet and try again.'],
  [/422|validation/i, 'Check your details and try again.'],
  [/policy/i, 'A policy prevented this action.'],
];

export function friendlyError(err: unknown, fallback = 'Something went wrong. Try again.'): string {
  const raw = err instanceof Error ? err.message : String(err ?? '');

  for (const [pattern, message] of CONTENT_MATCHES) {
    if (pattern.test(raw)) return message;
  }

  const statusMatch = raw.match(/\b([45]\d{2})\b/);
  if (statusMatch) {
    const code = parseInt(statusMatch[1], 10);
    if (STATUS_MESSAGES[code]) return STATUS_MESSAGES[code];
  }

  if (raw.trim() && raw.length < 200) return raw;
  return fallback;
}
