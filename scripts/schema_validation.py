"""Content and Google-feature checks shared by the audit and publishing gate."""
from datetime import datetime
from decimal import Decimal, InvalidOperation
from urllib.parse import urlsplit, urljoin
import json
import re
from schema_content import BASE, FACTS, content

ARTICLES = {'Article', 'BlogPosting', 'TechArticle'}


def nodes(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from nodes(child)


def parse_graph(source):
    graph = []
    for raw in re.findall(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', source, re.S | re.I):
        parsed = json.loads(raw)
        graph.extend(parsed if isinstance(parsed, list) else parsed.get('@graph', [parsed]))
    return graph


def check(source, canonical):
    errors, notes = [], []
    try:
        graph = parse_graph(source)
    except (ValueError, AttributeError) as exc:
        return {'errors': ['Invalid JSON-LD: ' + str(exc)], 'notes': []}
    visible = content(source, canonical)
    page_id = canonical + '#webpage'
    pages = [n for n in graph if n.get('@id') == page_id]
    if len(pages) != 1:
        errors.append('Expected one canonical WebPage entity')
    else:
        page = pages[0]
        if page.get('@type') not in {'WebPage', 'CollectionPage', 'AboutPage'}:
            errors.append('Article entity replaces its containing WebPage')
        if page.get('url') != canonical:
            errors.append('WebPage URL differs from canonical')
        if page.get('name') != visible['title'] or page.get('description') != visible['description']:
            errors.append('WebPage title/description differs from page metadata')
    definitions = {}
    for node in nodes(graph):
        if node.get('@id') and len(node) > 1:
            key = node['@id']
            if key in definitions and any(definitions[key][p] != node[p] for p in definitions[key].keys() & node.keys()):
                errors.append('Conflicting definitions for ' + key)
            definitions[key] = {**definitions.get(key, {}), **node}
    for node in nodes(graph):
        if set(node) == {'@id'} and node['@id'].startswith(BASE + '/') and node['@id'] not in definitions:
            errors.append('Unresolved entity reference: ' + node['@id'])
    for node in graph:
        kind = node.get('@type')
        if kind in ARTICLES:
            if node.get('headline') != visible['heading']:
                errors.append('Article headline differs from visible H1')
            if node.get('mainEntityOfPage') != {'@id': page_id}:
                errors.append('Article lacks correct containing page reference')
            if visible['modified'] and node.get('dateModified') != visible['modified']:
                errors.append('Article dateModified differs from displayed update date')
            if visible['has_updated'] and not visible['modified'] and node.get('dateModified'):
                errors.append('Exact article update date invented from a month-only byline')
            if visible['author'] and node.get('author', {}).get('name') != visible['author']:
                errors.append('Article author differs from visible byline')
            for key in ['datePublished', 'dateModified']:
                if key in node:
                    try:
                        datetime.fromisoformat(node[key].replace('Z', '+00:00'))
                    except (ValueError, AttributeError):
                        errors.append('Invalid ISO date: ' + key)
        if kind == 'FAQPage':
            if node.get('mainEntity') != visible['questions']:
                errors.append('FAQ markup differs from visible questions and answers')
            notes.append('FAQPage is semantic markup; Google retired FAQ rich results in May 2026')
        if kind == 'BreadcrumbList':
            items = node.get('itemListElement', [])
            if len(items) < 2 or [x.get('position') for x in items] != list(range(1, len(items) + 1)):
                errors.append('Breadcrumbs need at least two consecutively positioned items')
            if any(not x.get('name') or not x.get('item', '').startswith('https://') for x in items):
                errors.append('Breadcrumb has an empty name or non-absolute URL')
            if len(visible['breadcrumbs']) >= 2 and [(x.get('name'), x.get('item')) for x in items] != visible['breadcrumbs']:
                errors.append('Breadcrumb markup differs from the visible trail')
        if kind == 'ItemList':
            links = {urljoin(canonical, n.attrs['href']) for n in visible['nodes'] if n.tag == 'a' and n.attrs.get('href')}
            for item in node.get('itemListElement', []):
                if item.get('url') not in links or item.get('name', '') not in visible['text']:
                    errors.append('Catalog item not present in page links/content: ' + item.get('url', ''))
        if kind == 'SoftwareApplication':
            if canonical.startswith(FACTS['google-sheets']['url']):
                errors.append('Early-access Sheets page must not advertise a confirmed software purchase offer')
            offers = node.get('offers', [])
            offers = offers if isinstance(offers, list) else [offers]
            if not offers:
                errors.append('Software app has no truthful offer price')
            for offer in offers:
                try:
                    price = Decimal(str(offer['price']))
                    if price < 0 or not re.search(r'\$\s*' + re.escape(format(price, 'f')) + r'(?![\d.])', visible['text']):
                        errors.append('Software offer price is not visible on the page')
                except (InvalidOperation, KeyError):
                    errors.append('Software offer needs a numeric price')
                if offer.get('priceCurrency') != 'USD':
                    errors.append('Software offer currency differs from displayed USD pricing')
            if not node.get('review') and not node.get('aggregateRating'):
                notes.append('No genuine rating/review published: retain the truthful app, do not invent ratings; Google docs list review evidence for software rich results')
        if kind == 'VideoObject':
            if not all(node.get(k) for k in ['name', 'thumbnailUrl', 'uploadDate']):
                errors.append('Video is missing a Google-required field')
            try:
                datetime.fromisoformat(node.get('uploadDate', '').replace('Z', '+00:00'))
            except ValueError:
                errors.append('Video uploadDate is not ISO 8601')
            vid = urlsplit(node.get('embedUrl', '')).path.rsplit('/', 1)[-1]
            if not vid or not any(n.attrs.get('data-youtube-video') == vid or vid in n.attrs.get('src', '') for n in visible['nodes']):
                errors.append('Video schema does not match the visible playable demo')
    return {'errors': sorted(set(errors)), 'notes': sorted(set(notes))}


def vocabulary_errors(graph, vocabulary):
    """Validate names, property domains and object ranges using official vocabulary."""
    terms = {n['@id'].removeprefix('schema:'): n for n in vocabulary['@graph'] if n['@id'].startswith('schema:')}
    def values(node, key):
        value = node.get(key, [])
        return [v['@id'].removeprefix('schema:') for v in (value if isinstance(value, list) else [value])]
    def ancestors(kind, seen=None):
        seen = set() if seen is None else seen
        if kind in seen:
            return seen
        seen.add(kind)
        for parent in values(terms.get(kind, {}), 'rdfs:subClassOf'):
            ancestors(parent, seen)
        return seen
    errors = []
    for node in nodes(graph):
        kind = node.get('@type')
        if not kind:
            continue
        types = kind if isinstance(kind, list) else [kind]
        family = set().union(*(ancestors(t) for t in types))
        for t in types:
            if t not in terms:
                errors.append('Unknown schema type: ' + t)
        for prop, value in node.items():
            if prop.startswith('@'):
                continue
            definition = terms.get(prop)
            if not definition:
                errors.append('Unknown schema property: ' + prop)
                continue
            domains = values(definition, 'schema:domainIncludes')
            if domains and not family.intersection(domains):
                errors.append(f'{prop} is not defined for {kind}')
            ranges = values(definition, 'schema:rangeIncludes')
            for item in (value if isinstance(value, list) else [value]):
                if isinstance(item, dict) and item.get('@type') and ranges:
                    target_types = item['@type'] if isinstance(item['@type'], list) else [item['@type']]
                    target_family = set().union(*(ancestors(t) for t in target_types))
                    if not target_family.intersection(ranges):
                        errors.append(f'{prop} does not accept {item["@type"]}')
    return sorted(set(errors))
