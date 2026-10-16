export function chartScale(chart) {
  const values = chart.groups.flatMap(group => [group.value, group.target, ...(group.series || []).map(series => series.value)]);
  values.push(...(chart.multiSeries || []).flatMap(series => series.values), ...(chart.comparison || []), ...(chart.pace || []));
  const max = Math.max(chart.unit === 'percent' ? 100 : 1, ...values.filter(Number.isFinite));
  const ceiling = chart.unit === 'count' ? Math.ceil(max / 2) * 2 : max;
  return { max: ceiling, ticks: [0, ceiling / 2, ceiling] };
}
export function chartTickLabel(label, count) {
  if (/^\d{4}-\d{2}-\d{2}$/.test(label)) return label.slice(5);
  const length = Math.max(6, Math.min(24, Math.floor(340 / Math.max(count, 1) / 7)));
  return label.length > length ? label.slice(0, length - 1) + '…' : label;
}
