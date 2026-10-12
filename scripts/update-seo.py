#!/usr/bin/env python3
"""Write static JSON-LD from visible page content and reviewed product facts.

No build step or browser dependency is required. Run after editing product facts,
FAQ answers, article headings, or canonical URLs, then run check-site.py.
"""
from pathlib import Path
from html.parser import HTMLParser
import html
import json
import re
import hashlib

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://lcbridge.app'
FACTS = json.loads((ROOT / 'data/product-facts.json').read_text())
DATE = FACTS['lastReviewed']
ASSET_VERSIONS = {
    '/assets/' + name: hashlib.sha256((ROOT / 'assets' / name).read_bytes()).hexdigest()[:8]
    for name in ['brand.css', 'fonts.css', 'seo-content.css', 'analytics.js', 'analytics-config.js', 'video-player.js']
}


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def plain(markup):
    parser = Text()
    parser.feed(markup)
    return ' '.join(' '.join(parser.parts).split())


ORG = {'@type': 'Organization', '@id': BASE + '/#organization', **FACTS['organization'],
       'logo': {'@type': 'ImageObject', 'url': BASE + '/assets/lcbridge-lockup-black.png'},
       'contactPoint': {'@type': 'ContactPoint', 'contactType': 'customer support',
                        'email': 'support@lcbridge.app', 'url': BASE + '/about/'}}


def application(product):
    data = FACTS[product]
    app = {'@type': 'SoftwareApplication', '@id': data['url'] + '#app',
           'name': data['name'], 'url': data['url'], 'description': data['description'],
           'applicationCategory': 'BusinessApplication',
           'operatingSystem': 'Web: HighLevel / GoHighLevel',
           'softwareRequirements': data['requirements'],
           'publisher': {'@id': BASE + '/#organization'},
           'softwareHelp': {'@type': 'WebPage',
                            'url': data['url'] + ('how-to-add-ai-agent-highlevel-community/'
                                                 if product == 'community-agents' else 'docs/'),
                            'name': data['name'] + ' documentation'}}
    if product == 'docusign':
        offers = []
        for plan in data['plans']:
            offers.append({'@type': 'Offer', 'name': plan['name'] + ' monthly',
                           'price': str(plan['monthlyUSD']), 'priceCurrency': 'USD',
                           'url': data['url'] + 'pricing',
                           'description': 'Monthly billing per ' + plan['unit'] +
                                          '; DocuSign subscription billed separately.'})
        app['offers'] = offers
    else:
        app['offers'] = {'@type': 'Offer', 'name': 'Standard monthly',
                         'price': '47', 'priceCurrency': 'USD',
                         'url': data['url'] + 'pricing/',
                         'description': '$47/month per HighLevel sub-account includes $47 of AI usage. '
                                        'Unused allowance expires at renewal. Additional usage is metered '
                                        'at 4 times provider cost and billed through HighLevel. Taxes and '
                                        'agency resale pricing may change the final charge.'}
    return app


def video(product):
    data = FACTS[product]
    v = data['video']
    return {'@type': 'VideoObject', '@id': data['url'] + '#video',
            'name': data['name'] + ' product demo', 'description': data['description'],
            'thumbnailUrl': [v['thumbnailUrl']], 'duration': v['duration'],
            'uploadDate': v['uploadDate'],
            'embedUrl': 'https://www.youtube-nocookie.com/embed/' + v['id'],
            'publisher': {'@id': BASE + '/#organization'}}


def update_page(path):
    source = path.read_text()
    if re.search(r'http-equiv=["\']refresh', source, re.I):
        return False
    canonical_match = re.search(r'<link\b[^>]*rel="canonical"[^>]*href="([^"]+)"', source)
    if not canonical_match:
        return False
    canonical = canonical_match.group(1)
    title = plain(re.search(r'<title>(.*?)</title>', source, re.S).group(1))
    desc_match = re.search(r'<meta name="description" content="([^"]+)"', source)
    description = html.unescape(desc_match.group(1)) if desc_match else title
    h1 = re.search(r'<h1\b[^>]*>(.*?)</h1>', source, re.S)
    heading = plain(h1.group(1)) if h1 else title
    # Retain meaningful authored article dates/term graphs, not stale FAQs or product facts.
    prior = []
    for block in re.findall(r'<script\b[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', source, re.S):
        parsed = json.loads(block)
        prior.extend(parsed.get('@graph', [parsed]))
    source = re.sub(r'\s*<script\b[^>]*type="application/ld\+json"[^>]*>.*?</script>', '', source, flags=re.S)
    kind = 'AboutPage' if canonical == BASE + '/about/' else 'WebPage'
    webpage = {'@type': kind, '@id': canonical + '#webpage', 'url': canonical,
               'name': title, 'description': description,
               'isPartOf': {'@id': BASE + '/#website'},
               'publisher': {'@id': BASE + '/#organization'}}
    graph = [ORG, {'@type': 'WebSite', '@id': BASE + '/#website', 'url': BASE + '/',
                   'name': 'LC Bridge', 'publisher': {'@id': BASE + '/#organization'}}, webpage]
    if canonical != BASE + '/':
        crumbs = [('Home', BASE + '/')]
        if '/docusign-integration/' in canonical and canonical != BASE + '/docusign-integration/':
            crumbs.append(('DocuSign Integration', BASE + '/docusign-integration/'))
            if '/docs/' in canonical and not canonical.endswith('/docs/'):
                crumbs.append(('Documentation', BASE + '/docusign-integration/docs/'))
        elif '/community-agents/' in canonical and canonical != BASE + '/community-agents/':
            crumbs.append(('Community Agents', BASE + '/community-agents/'))
        elif '/blog/' in canonical and canonical != BASE + '/blog/':
            crumbs.append(('Blog', BASE + '/blog/'))
        crumbs.append((heading, canonical))
        graph.append({'@type': 'BreadcrumbList', '@id': canonical + '#breadcrumbs',
                      'itemListElement': [{'@type': 'ListItem', 'position': i + 1,
                                          'name': name, 'item': url}
                                         for i, (name, url) in enumerate(crumbs)]})
        webpage['breadcrumb'] = {'@id': canonical + '#breadcrumbs'}
    product = 'docusign' if '/docusign-integration/' in canonical else 'community-agents' if '/community-agents/' in canonical else None
    if product:
        app = application(product)
        root_url = FACTS[product]['url']
        if canonical in [root_url, root_url + ('pricing' if product == 'docusign' else 'pricing/')]:
            graph.append(app)
            webpage['mainEntity'] = {'@id': app['@id']}
        if canonical == root_url:
            graph.append(video(product))
            webpage['video'] = {'@id': root_url + '#video'}
    article_page = '/blog/' in canonical and canonical != BASE + '/blog/' or '/docs/' in canonical and not canonical.endswith('/docs/') or product == 'community-agents' and canonical != FACTS[product]['url'] and not canonical.endswith('/pricing/')
    if article_page:
        old = next((n for n in prior if n.get('@type') in ['BlogPosting', 'Article', 'TechArticle']), {})
        article = {'@type': 'BlogPosting' if '/blog/' in canonical else 'TechArticle',
                   '@id': canonical + '#article', 'headline': heading, 'description': description,
                   'datePublished': old.get('datePublished', DATE), 'dateModified': DATE,
                   'mainEntityOfPage': {'@id': canonical + '#webpage'},
                   'author': {'@type': 'Organization', '@id': BASE + '/#organization',
                              'name': 'LC Bridge', 'url': BASE + '/about/#editorial-team'},
                   'publisher': {'@id': BASE + '/#organization'},
                   'image': [BASE + ('/assets/community-agents-demo.webp' if product == 'community-agents' else '/assets/og-docusign.png')]}
        graph.append(article)
        webpage['mainEntity'] = {'@id': article['@id']}
    if canonical == BASE + '/about/':
        graph.append({'@type': 'Person', '@id': BASE + '/about/#arun', 'name': 'Arun',
                      'jobTitle': 'Founder', 'url': BASE + '/about/#arun',
                      'image': BASE + '/assets/arun-headshot.jpg',
                      'worksFor': {'@id': BASE + '/#organization'}})
    questions = []
    for block in re.findall(r'<details\b[^>]*>(.*?)</details>', source, re.S):
        summary = re.search(r'<summary\b[^>]*>(.*?)</summary>', block, re.S)
        if not summary:
            continue
        question = plain(re.sub(r'<svg\b.*?</svg>', '', summary.group(1), flags=re.S)).rstrip(' +−')
        answer = plain(block[summary.end():])
        if question.endswith('?') and answer:
            questions.append({'@type': 'Question', 'name': question,
                              'acceptedAnswer': {'@type': 'Answer', 'text': answer}})
    if questions:
        graph.append({'@type': 'FAQPage', '@id': canonical + '#faq-schema', 'mainEntity': questions})
    for node in prior:
        if node.get('@type') == 'DefinedTermSet':
            graph.append(node)
    markup = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, indent=2)
    source = source.replace('</head>', '<script id="lcbridge-structured-data" type="application/ld+json">\n' + markup + '\n</script>\n</head>', 1)
    for asset, version in ASSET_VERSIONS.items():
        source = re.sub(re.escape(asset) + r'(?:\?v=[a-f0-9]+)?(?=["\'])',
                        asset + '?v=' + version, source)
    path.write_text(source)
    return True


if __name__ == '__main__':
    count = 0
    for path in ROOT.rglob('*.html'):
        parts = path.relative_to(ROOT).parts
        if parts[0] in ['output', 'docs', 'scripts', 'blog-drafts', 'Claude outputs'] or any(part in parts for part in ['.git', '.playwright-mcp']):
            continue
        count += update_page(path)
    print(f'Updated static schema on {count} canonical pages.')
