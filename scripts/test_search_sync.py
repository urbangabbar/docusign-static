"""Behavioral checks for page additions, migrations, removals and crawler visibility."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import urllib.robotparser
import xml.etree.ElementTree as ET
from contextlib import redirect_stdout
from io import StringIO

spec = importlib.util.spec_from_file_location('search_sync', Path(__file__).with_name('sync-search.py'))
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)
reconcile_spec = importlib.util.spec_from_file_location('search_reconcile', Path(__file__).with_name('reconcile-search.py'))
reconcile = importlib.util.module_from_spec(reconcile_spec)
reconcile_spec.loader.exec_module(reconcile)
BASE = 'https://lcbridge.app'


class SearchSyncTests(unittest.TestCase):
    def setUp(self):
        self.quiet = redirect_stdout(StringIO())
        self.quiet.__enter__()
        self.addCleanup(self.quiet.__exit__, None, None, None)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'data').mkdir()
        self.policy = {'baseUrl': BASE, 'internalPaths': {'brand/*': 'Internal'},
                       'aiCrawlers': ['OAI-SearchBot']}
        (self.root / 'data/search-policy.json').write_text(json.dumps(self.policy))
        (self.root / 'llms.txt').write_text('# LC Bridge\n\nReviewed product facts.\n')
        self.page('index.html', '/')

    def page(self, path, route, links='', robots=''):
        file = self.root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(f'<title>{route}</title><meta name="description" content="Useful {route}">'
                        f'<link rel="canonical" href="{BASE}{route}">{robots}<h1>{route}</h1>{links}')

    def manifest(self):
        return json.loads((self.root / 'search-manifest.json').read_text())

    def test_new_hierarchy_page_is_in_all_discovery_files(self):
        self.page('index.html', '/', '<a href="/blog/">Blog</a>')
        self.page('blog/index.html', '/blog/')
        self.assertEqual(sync.run(self.root, True), 0)
        urls = [e.text for e in ET.parse(self.root / 'sitemap.xml').iter() if e.tag.endswith('}loc')]
        self.assertIn(BASE + '/blog/', urls)
        self.assertIn('](' + BASE + '/blog/)', (self.root / 'llms.txt').read_text())
        rp = urllib.robotparser.RobotFileParser()
        rp.parse((self.root / 'robots.txt').read_text().splitlines())
        for bot in ('Googlebot', 'OAI-SearchBot'):
            self.assertTrue(rp.can_fetch(bot, BASE + '/blog/'))

    def test_unchanged_pages_keep_lastmod_and_generation_is_idempotent(self):
        self.assertEqual(sync.run(self.root, True), 0)
        manifest = self.manifest()
        manifest['pages'][0]['lastmod'] = '2020-01-01'
        (self.root / 'search-manifest.json').write_text(json.dumps(manifest))
        self.assertEqual(sync.run(self.root, True), 0)
        self.assertEqual(self.manifest()['pages'][0]['lastmod'], '2020-01-01')
        self.assertEqual(sync.run(self.root), 0)
        (self.root / 'index.html').write_text((self.root / 'index.html').read_text() + '<p>New content</p>')
        self.assertEqual(sync.run(self.root), 1)
        self.assertEqual(sync.run(self.root, True), 0)
        self.assertNotEqual(self.manifest()['pages'][0]['lastmod'], '2020-01-01')

    def test_public_noindex_and_wrong_canonical_fail(self):
        self.page('index.html', '/', robots='<meta name="googlebot" content="noindex">')
        self.assertEqual(sync.run(self.root, True), 1)
        self.page('index.html', '/wrong/')
        self.assertEqual(sync.run(self.root, True), 1)

    def test_orphan_is_not_silently_omitted(self):
        self.page('new.html', '/new')
        self.assertEqual(sync.run(self.root, True), 1)

    def test_internal_page_is_excluded(self):
        self.page('brand/index.html', '/brand/', robots='<meta name="robots" content="noindex">')
        self.assertEqual(sync.run(self.root, True), 0)
        self.assertEqual(len(self.manifest()['pages']), 1)

    def test_migration_redirect_is_not_an_indexing_destination(self):
        self.page('index.html', '/', '<a href="/old">Old</a>')
        self.page('old.html', '/old')
        self.assertEqual(sync.run(self.root, True), 0)
        self.page('index.html', '/', '<a href="/new">New</a>')
        self.page('new.html', '/new')
        (self.root / 'old.html').write_text(f'<link rel="canonical" href="{BASE}/new">'
                                           '<meta http-equiv="refresh" content="0;url=/new">')
        self.assertEqual(sync.run(self.root, True), 0)
        self.assertNotIn(BASE + '/old', [p['url'] for p in self.manifest()['pages']])
        self.assertIn({'from': BASE + '/old', 'to': BASE + '/new'}, self.manifest()['redirects'])
        (self.root / 'old.html').write_text(f'<link rel="canonical" href="{BASE}/gone">'
                                           '<meta http-equiv="refresh" content="0;url=/gone">')
        self.assertEqual(sync.run(self.root, True), 1)

    def test_deletion_requires_an_explicit_retirement(self):
        self.page('index.html', '/', '<a href="/old">Old</a>')
        self.page('old.html', '/old')
        self.assertEqual(sync.run(self.root, True), 0)
        self.page('index.html', '/')
        (self.root / 'old.html').unlink()
        self.assertEqual(sync.run(self.root, True), 1)
        (self.root / 'data/search-removals.json').write_text(json.dumps({BASE + '/old': 'Content retired; no replacement'}))
        self.assertEqual(sync.run(self.root, True), 0)
        self.assertEqual(sync.run(self.root), 0)
        self.assertNotIn(BASE + '/old', (self.root / 'llms.txt').read_text())

    def test_accepted_request_survives_unchanged_deploy_but_changes_requeue(self):
        manifest = {'pages': [{'url': BASE + '/', 'title': 'Home', 'contentHash': 'one'}]}
        state = reconcile.reconcile({}, manifest)
        state['urls'][BASE + '/']['status'] = 'accepted'
        self.assertEqual(reconcile.reconcile(state, manifest)['urls'][BASE + '/']['status'], 'accepted')
        manifest['pages'][0]['contentHash'] = 'two'
        self.assertEqual(reconcile.reconcile(state, manifest)['urls'][BASE + '/']['status'], 'pending')
        manifest['pages'] = []
        self.assertEqual(reconcile.reconcile(state, manifest)['urls'][BASE + '/']['status'], 'retired')


if __name__ == '__main__':
    unittest.main()
