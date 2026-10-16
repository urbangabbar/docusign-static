"""Protect shared navigation when product generators and legacy pages coexist."""
from pathlib import Path
import importlib.util
import re
import unittest
from site_chrome import apply_chrome,render_footer,render_company_header,PRODUCTS,ROOT
spec=importlib.util.spec_from_file_location('chrome_sync',Path(__file__).with_name('sync-site-chrome.py'))
sync=importlib.util.module_from_spec(spec);spec.loader.exec_module(sync)

class SiteChromeTests(unittest.TestCase):
    def test_every_public_page_has_the_same_static_footer_and_one_consent_dialog(self):
        pages=list(sync.public_pages())
        self.assertGreaterEqual(len(pages),87)
        for file,path,source in pages:
            with self.subTest(path=path):
                self.assertEqual(re.findall(r'<footer\b.*?</footer>',source,re.S),[render_footer()])
                self.assertEqual(source.count('data-company-header'),1)
                self.assertIn(render_company_header(),source)
                self.assertEqual(source.count('id="analytics-dialog"'),1)
                self.assertEqual(source.count('id="analytics-settings"'),1)
                self.assertEqual(apply_chrome(source,path),source)
                if path.startswith(('/google-sheets-integration/','/community-agents/','/docusign-integration/')):
                    self.assertIn('lcb-product-header',source)
                    self.assertLess(source.index('data-company-header'),source.index('lcb-product-header'))
                    self.assertIn('class="lcb-company-logo" href="/"',source)
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
        source='<html><head></head><body><nav>Product navigation</nav><main id="main"></main><footer>Old</footer></body></html>'
        once=apply_chrome(source,'/docusign-integration/docs/')
        self.assertEqual(apply_chrome(once,'/docusign-integration/docs/'),once)

    def test_company_homepage_positioning_and_cta_remain_about_the_portfolio(self):
        home=(ROOT/'index.html').read_text()
        h1=re.sub('<[^>]+>','',re.search(r'<h1[^>]*>(.*?)</h1>',home,re.S)[1])
        self.assertIn('Your GoHighLevel.',h1)
        self.assertNotIn('Google Sheets',h1)
        self.assertIn('Explore our products',home)
        self.assertNotIn('25 report templates</b>',home)

    def test_missing_product_navigation_cannot_consume_footer_navigation(self):
        source='<html><head></head><body><main id="main"></main><footer><nav>Footer</nav></footer></body></html>'
        with self.assertRaises(ValueError):apply_chrome(source,'/google-sheets-integration/')
