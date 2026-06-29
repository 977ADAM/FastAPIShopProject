// Lightweight client-side email check — a friendly pre-flight before the
// server's authoritative EmailStr validation. Requires a dot in the domain.
export function isValidEmail(value) {
  if (typeof value !== 'string') return false
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim())
}
