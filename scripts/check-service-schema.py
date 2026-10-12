#!/usr/bin/env python3
"""Ensure a routine SEO refresh cannot erase the service page's authored schema."""
import importlib.util
import json
from pathlib import Path
import re
import tempfile

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('site_seo', root / 'scripts/update-seo.py')
seo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(seo)
source = (root / 'highlevel-development/index.html').read_text()

def graph(text):
    return json.loads(re.search(r'<script id="lcbridge-structured-data"[^>]*>(.*?)</script>', text, re.S)[1])['@graph']

original = graph(source)
service = next(n for n in original if n['@type'] == 'Service')
page = next(n for n in original if n['@type'] == 'WebPage')
faq = next(n for n in original if n['@type'] == 'FAQPage')
with tempfile.TemporaryDirectory() as tmp:
    target = Path(tmp) / 'index.html'
    target.write_text(source)
    for _ in range(2):
        assert seo.update_page(target)
        updated = graph(target.read_text())
        assert [n for n in updated if n['@type'] == 'Service'] == [service]
        updated_page = next(n for n in updated if n['@type'] == 'WebPage')
        assert updated_page['mainEntity'] == {'@id': service['@id']}
        for field in ['dateModified', 'inLanguage', 'primaryImageOfPage']:
            assert updated_page[field] == page[field]
        assert next(n for n in updated if n['@type'] == 'FAQPage')['mainEntity'] == faq['mainEntity']
        assert len({n['@id'] for n in updated}) == len(updated)
print('Service identity, page attribution, and visible FAQs survive repeated SEO refreshes.')
