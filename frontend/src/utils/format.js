// Formats a numeric amount as Russian rubles, e.g. 1250 -> "1 250 ₽".
// Uses a regular space as the grouping separator for predictable test output.
export function formatPrice(value) {
  const n = Number(value) || 0
  const grouped = Math.round(n)
    .toString()
    .replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
  return `${grouped} ₽`
}
