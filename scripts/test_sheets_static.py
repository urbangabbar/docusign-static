"""Public report previews must remain understandable without JavaScript."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('site_check', ROOT/'scripts/check-site.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class StaticReportTests(unittest.TestCase):
    def test_all_reports_have_one_document_title_and_their_static_values(self):
        catalog=json.loads((ROOT/'data/google-sheets-reports.json').read_text())
        self.assertEqual(len(catalog),25)
        for report in catalog:
            path=ROOT/'google-sheets-integration/templates'/report['slug']/'index.html'
            page=module.Page(path)
            self.assertEqual(page.title_count,1,report['slug'])
            self.assertEqual(page.h1_count,1,report['slug'])
            source=path.read_text()
            self.assertIn('Invented sample',source)
            self.assertIn('Record grain:',source)
            self.assertIn('Required data and boundaries',source)
            self.assertIn('/google-sheets-integration/#apply',page.links)
            self.assertIn('/google-sheets-integration/docs/creating-reports/',page.links)
            self.assertNotIn('data-action=',source)

if __name__=='__main__':unittest.main()
