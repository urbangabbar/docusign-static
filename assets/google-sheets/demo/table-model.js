const collator = new Intl.Collator('en', { numeric: true, sensitivity: 'base' });
const missing = value => value == null || /^(—|Missing|Unavailable|Not enough data|Not set|Excluded)$/i.test(String(value));
function sortable(value) {
  if (typeof value === 'number') return value;
  const text = String(value ?? '').trim();
  if (/^-?[$€£₹]?[\d,]+(?:\.\d+)?(?:%| days| min)?$/.test(text)) return Number(text.replace(/[$€£₹,%]| days| min/g, ''));
  return text;
}
export function tableRows(rows, filters = {}, sort = null) {
  const matched = rows.filter(row => Object.entries(filters).every(([column, query]) => String(row.cells[column] ?? 'Missing').toLowerCase().includes(query.trim().toLowerCase())));
  if (!sort) return matched;
  return [...matched].sort((a, b) => {
    const left = a.cells[sort.column], right = b.cells[sort.column];
    if (missing(left) || missing(right)) return Number(missing(left)) - Number(missing(right));
    const x = sortable(left), y = sortable(right);
    const order = typeof x === 'number' && typeof y === 'number' ? x - y : collator.compare(String(x), String(y));
    return sort.direction === 'asc' ? order : -order;
  });
}
