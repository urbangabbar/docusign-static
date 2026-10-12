/* Progressive enhancement: every resource is a static, crawlable HTML link. */
(function () {
  var search = document.querySelector('[data-docs-search]');
  if (!search) return;
  var input = search.querySelector('input');
  var clear = search.querySelector('button');
  var groups = Array.from(document.querySelectorAll('[data-docs-group]'));
  var resources = Array.from(document.querySelectorAll('[data-docs-resource]'));
  var status = document.querySelector('[data-docs-status]');
  var empty = document.querySelector('[data-docs-empty]');
  var timer;
  function update() {
    var words = input.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
    var count = 0;
    resources.forEach(function (resource) {
      var text = (resource.textContent + ' ' + (resource.dataset.keywords || '')).toLowerCase();
      var match = words.every(function (word) { return text.includes(word); });
      resource.hidden = !match;
      if (match) count++;
    });
    groups.forEach(function (group) {
      group.hidden = !Array.from(group.querySelectorAll('[data-docs-resource]')).some(function (resource) { return !resource.hidden; });
    });
    empty.hidden = count !== 0;
    clear.hidden = words.length === 0;
    status.textContent = words.length ? count + ' matching ' + (count === 1 ? 'resource' : 'resources') : 'All ' + resources.length + ' resources';
  }
  input.addEventListener('input', function () { clearTimeout(timer); timer = setTimeout(update, 150); });
  clear.addEventListener('click', function () { clearTimeout(timer); input.value = ''; update(); input.focus(); });
  // Restore the full catalogue before the browser follows a category anchor.
  document.querySelectorAll('.ds-categories a, .ds-start a[href*="#"]').forEach(function (link) {
    link.addEventListener('click', function () { clearTimeout(timer); input.value = ''; update(); });
  });
  search.hidden = false;
  update();
})();
