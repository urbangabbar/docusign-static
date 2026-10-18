"""Regression checks for facts that previously drifted between HTML and JSON-LD."""
import json
from pathlib import Path
import unittest
from copy import deepcopy
from schema_content import align_graph, content, dumps, BASE
from schema_validation import check, parse_graph

ROOT = Path(__file__).resolve().parents[1]

class SchemaContentTests(unittest.TestCase):
    def test_published_pages_match_visible_facts(self):
        manifest = json.loads((ROOT / 'search-manifest.json').read_text())
        for page in manifest['pages']:
            rel = page['url'].removeprefix(BASE + '/')
            path = ROOT / (rel + 'index.html' if page['url'].endswith('/') else rel + '.html')
            with self.subTest(url=page['url']):
                self.assertEqual(check(path.read_text(), page['url'])['errors'], [])

    def test_member_insights_update_comes_from_displayed_time_not_global_review(self):
        url = BASE + '/community-agents/member-insights/'
        source = (ROOT / 'community-agents/member-insights/index.html').read_text()
        changed = source.replace('16 October 2026', '17 October 2026')
        graph = align_graph(parse_graph(source), changed, url)
        article = next(n for n in graph if n['@type'] == 'Article')
        self.assertEqual(article['dateModified'], '2026-10-17')
        self.assertTrue(any('dateModified' in e for e in check(changed, url)['errors']))

    def test_month_only_date_does_not_invent_a_day(self):
        c = content('<main><h1>Guide</h1><div>By LC Bridge editorial team · Updated Jul 2026</div></main>', BASE + '/guide/')
        self.assertIsNone(c['modified'])
        self.assertEqual(c['author'], 'LC Bridge editorial team')

    def test_faq_text_round_trips_html_and_script_terminators_safely(self):
        source = '<main><h1>FAQ</h1><details><summary>Can A &amp; B sync?</summary><p>Yes &lt;script&gt; remains text.</p></details></main>'
        question = content(source, BASE)['questions'][0]
        self.assertEqual(question['name'], 'Can A & B sync?')
        self.assertEqual(question['acceptedAnswer']['text'], 'Yes <script> remains text.')
        encoded = dumps([question])
        self.assertNotIn('<', encoded)
        self.assertEqual(json.loads(encoded)['@graph'], [question])

    def test_early_access_has_no_fake_free_software_offer(self):
        source = (ROOT / 'google-sheets-integration/index.html').read_text()
        graph = parse_graph(source)
        self.assertFalse(any(n['@type'] == 'SoftwareApplication' for n in graph))
        self.assertIn('Planned early-access base rates', source)

    def test_article_and_page_have_distinct_resolved_identities(self):
        url = BASE + '/blog/connect-gohighlevel-google-sheets/'
        graph = parse_graph((ROOT / 'blog/connect-gohighlevel-google-sheets/index.html').read_text())
        article = next(n for n in graph if n['@type'] == 'BlogPosting')
        page = next(n for n in graph if n['@id'] == url + '#webpage')
        self.assertNotEqual(page['@id'], article['@id'])
        self.assertEqual(page['mainEntity'], {'@id': article['@id']})
        self.assertEqual(article['mainEntityOfPage'], {'@id': page['@id']})

    def test_wrong_offer_price_is_rejected(self):
        url = BASE + '/community-agents/pricing/'
        source = (ROOT / 'community-agents/pricing/index.html').read_text()
        graph = deepcopy(parse_graph(source))
        next(n for n in graph if n['@type'] == 'SoftwareApplication')['offers']['price'] = '99999'
        import re
        changed = re.sub(r'(<script[^>]*type="application/ld\+json"[^>]*>).*?(</script>)', lambda m:m[1] + dumps(graph) + m[2], source, flags=re.S)
        self.assertIn('Software offer price is not visible on the page', check(changed, url)['errors'])

    def test_editorial_team_does_not_redefine_company_url(self):
        source = (ROOT / 'community-agents/member-insights/index.html').read_text()
        article = next(n for n in parse_graph(source) if n['@type'] == 'Article')
        self.assertEqual(article['author']['name'], 'LC Bridge editorial team')
        self.assertNotEqual(article['author']['@id'], BASE + '/#organization')

if __name__ == '__main__':
    unittest.main()
