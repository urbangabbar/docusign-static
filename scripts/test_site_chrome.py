"""Protect shared navigation when product generators and legacy pages coexist."""
from pathlib import Path
import importlib.util
import re
import unittest
from site_chrome import apply_chrome,render_footer,PRODUCTS,ROOT
spec=importlib.util.spec_from_file_location('chrome_sync',Path(__file__).with_name('sync-site-chrome.py'))
sync=importlib.util.module_from_spec(spec);spec.loader.exec_module(sync)

class SiteChromeTests(unittest.TestCase):
    def test_every_public_page_has_the_same_static_footer_and_one_consent_dialog(self):
        pages=list(sync.public_pages())
        self.assertGreaterEqual(len(pages),87)
        for file,path,source in pages:
            with self.subTest(path=path):
                self.assertEqual(re.findall(r'<footer\b.*?</footer>',source,re.S),[render_footer()])
                self.assertEqual(source.count('id="analytics-dialog"'),1)
                self.assertEqual(source.count('id="analytics-settings"'),1)
                self.assertEqual(apply_chrome(source,path),source)
                if path.startswith(('/google-sheets-integration/','/community-agents/','/docusign-integration/')):
                    self.assertEqual(source.count('class="lcb-site-bridge"'),1)
                    self.assertIn('href="/" aria-label="Back to LC Bridge"',source)
    def test_product_order_is_consistent_in_all_switchers_and_homepage_sections(self):
        order=[p['id'] for p in PRODUCTS]
        self.assertEqual(order,['google-sheets','community-agents','docusign'])
        for _,path,source in sync.public_pages():
            for menu in re.findall(r'<details class="lcb-product-switcher".*?</details>',source,re.S):
                self.assertEqual(re.findall('data-product="([^"]+)"',menu),order,path)
        home=(ROOT/'index.html').read_text()
        self.assertEqual(re.findall(r'<article\b[^>]*data-product="([^"]+)"',home),order)
        products=(ROOT/'products/index.html').read_text()
        self.assertEqual(re.findall(r'class="prod-card-main" href="([^"]+)"',products),[p['url'] for p in PRODUCTS])
    def test_minified_product_page_remains_idempotent(self):
        source='<html><head></head><body><main id="main"></main><footer>Old</footer></body></html>'
        once=apply_chrome(source,'/docusign-integration/docs/')
        self.assertEqual(apply_chrome(once,'/docusign-integration/docs/'),once)
