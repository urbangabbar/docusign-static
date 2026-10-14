"""Regression tests for public brand separation and media review enforcement."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from check_brand_separation import has_forbidden_reference, scan


class BrandSeparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'data').mkdir()
        (self.root / 'data/search-policy.json').write_text(json.dumps({'internalPaths': {'docs/*': 'Internal', 'data/*': 'Internal', 'scripts/*': 'Internal', '.*': 'Internal'}}))
        (self.root / '_config.yml').write_text('exclude:\n  - data/\n  - docs/\n  - scripts/\n  - AGENTS.md\n  - _config.yml\n')
        (self.root / 'index.html').write_text('<h1>LC Bridge</h1>')

    def test_metadata_links_and_encoded_references_are_rejected(self):
        for value in ['GoCSM', 'GovPreneurs', 'go-csm.app', 'Gov Preneurs',
                      'Go<strong>CSM</strong>', 'Go&#67;SM', '%47%6f%43%53%4d',
                      r'Go\u0043SM', 'ＧｏＣＳＭ']:
            with self.subTest(value=value):
                self.assertTrue(has_forbidden_reference(value))
        self.assertFalse(has_forbidden_reference('LC Bridge for HighLevel / GoKollab'))

    def test_nested_public_docs_are_scanned_but_private_instructions_are_not(self):
        (self.root / 'docs').mkdir()
        (self.root / 'docs/private.md').write_text('GoCSM private operational rule')
        (self.root / 'AGENTS.md').write_text('Never mention GovPreneurs publicly')
        self.assertFalse(scan(self.root)['errors'])
        public = self.root / 'community-agents/docs/index.html'
        public.parent.mkdir(parents=True)
        public.write_text('<footer>Operated by GoCSM</footer>')
        self.assertIn('Forbidden public brand reference: community-agents/docs/index.html', scan(self.root)['errors'])

    def test_hidden_schema_and_discovery_files_are_scanned(self):
        (self.root / 'llms.txt').write_text('GoCSM operator')
        (self.root / 'index.html').write_text('<script type="application/ld+json">{"legalName":"GovPreneurs"}</script>')
        errors = scan(self.root)['errors']
        self.assertIn('Forbidden public brand reference: index.html', errors)
        self.assertIn('Forbidden public brand reference: llms.txt', errors)

    def test_changed_or_new_media_cannot_silently_pass(self):
        image = self.root / 'demo.png'
        image.write_bytes(b'reviewed image fixture')
        approval = {'sha256': {'demo.png': hashlib.sha256(image.read_bytes()).hexdigest()}}
        (self.root / 'data/approved-public-media.json').write_text(json.dumps(approval))
        self.assertFalse(scan(self.root)['errors'])
        image.write_bytes(b'changed image fixture')
        self.assertIn('Public media requires brand review before approval: demo.png', scan(self.root)['errors'])
        (self.root / 'new.pdf').write_bytes(b'new downloadable asset')
        self.assertIn('Public media requires brand review before approval: new.pdf', scan(self.root)['errors'])

    def test_built_artifact_does_not_hide_leaked_private_files(self):
        site = self.root / '_site'
        site.mkdir()
        (site / 'AGENTS.md').write_text('GoCSM private rule leaked')
        self.assertIn('Forbidden public brand reference: AGENTS.md', scan(site, self.root, published=True)['errors'])


if __name__ == '__main__':
    unittest.main()
