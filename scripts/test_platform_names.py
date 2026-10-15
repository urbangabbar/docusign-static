"""Check persistent platform identity and media-discovery guardrails."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('platform_names', Path(__file__).with_name('check-platform-names.py'))
names = importlib.util.module_from_spec(spec)
spec.loader.exec_module(names)


class PlatformNamesTests(unittest.TestCase):
    def fixture(self, root, visible=True, org_aliases=None):
        (root / 'data').mkdir()
        aliases = {'name': 'GoHighLevel', 'alternateName': ['Go High Level', 'GHL', 'HighLevel', 'High Level']}
        (root / 'data/product-facts.json').write_text(json.dumps({'platform': aliases}))
        url = 'https://lcbridge.app/'
        (root / 'search-manifest.json').write_text(json.dumps({'baseUrl': url[:-1], 'pages': [
            {'url': url, 'title': 'GoHighLevel apps', 'description': 'GoHighLevel product guides', 'images': []}]}))
        graph = [{'@id': url + '#gohighlevel-platform', **aliases},
                 {'@id': url + '#webpage', 'about': {'@id': url + '#gohighlevel-platform'}},
                 {'@id': url + '#organization', 'alternateName': org_aliases or ['LCBridge']}]
        context = '<p class="lcb-platform-context">GoHighLevel (GHL), also known as HighLevel.</p>' if visible else ''
        (root / 'index.html').write_text(context + '<script type="application/ld+json">' + json.dumps({'@graph': graph}) + '</script>')
        (root / 'image-sitemap.xml').write_text('<urlset xmlns="' + names.NS + '"></urlset>')

    def test_metadata_alone_cannot_replace_visible_platform_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root, visible=False)
            self.assertTrue(any('visible platform' in e for e in names.scan(root)['errors']))

    def test_platform_aliases_do_not_become_company_aliases(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root, org_aliases=['GHL'])
            self.assertTrue(any('incorrectly assigned' in e for e in names.scan(root)['errors']))

    def test_consistent_visible_and_structured_identity_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root)
            self.assertEqual(names.scan(root)['errors'], [])
