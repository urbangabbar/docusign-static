"""Align both static-site generators with the HTML readers actually receive.

Schema.org validity and Google feature eligibility are separate. In particular,
never fabricate offers or ratings to silence software-app eligibility warnings.
"""
from copy import deepcopy
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin
import json
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://lcbridge.app'
FACTS = json.loads((ROOT / 'data/product-facts.json').read_text())
VOID = set('area base br col embed hr img input link meta param source track wbr'.split())


class Node:
    def __init__(self, tag='', attrs=()):
        self.tag, self.attrs, self.children = tag, dict(attrs), []

    def nodes(self):
        yield self
        for child in self.children:
            if isinstance(child, Node):
                yield from child.nodes()

    def text(self):
        if self.tag in {'script', 'style', 'svg', 'template'} or 'hidden' in self.attrs or self.attrs.get('aria-hidden') == 'true':
            return ''
        return ' '.join(' '.join(c.text() if isinstance(c, Node) else c for c in self.children).split())


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.root = Node()
        self.stack = [self.root]
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                self.stack = self.stack[:i]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def date_value(text):
    text = text.strip().rstrip('.')
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}(?:T.*)?', text):
        return datetime.fromisoformat(text.replace('Z', '+00:00')).isoformat() if 'T' in text else datetime.strptime(text, '%Y-%m-%d').date().isoformat()
    for fmt in ['%d %B %Y', '%B %d, %Y', '%b %d, %Y']:
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            pass
    return None


def content(source, canonical):
    doc = Document(source)
    nodes = list(doc.root.nodes())
    main = next((n for n in nodes if n.tag == 'main'), doc.root)
    main_nodes = list(main.nodes())
    meta = {n.attrs.get('name', n.attrs.get('property')): n.attrs.get('content') for n in nodes if n.tag == 'meta'}
    title = next((n.text() for n in nodes if n.tag == 'title'), '')
    heading = next((n.text() for n in main_nodes if n.tag == 'h1'), title)
    byline = next((n.text() for n in main_nodes if n.tag in {'p', 'div', 'span'} and n.text().startswith('By ') and len(n.text()) < 300), '')
    author = re.match(r'By\s+(.+?)\s*(?:[·|]|\d+\s+min read|Updated|$)', byline)
    modified = re.search(r'Updated\s+((?:\d{1,2} [A-Za-z]+ \d{4})|(?:[A-Za-z]+ \d{1,2}, \d{4}))', byline)
    questions = []
    for node in main_nodes:
        if node.tag != 'details':
            continue
        summary = next((n for n in node.children if isinstance(n, Node) and n.tag == 'summary'), None)
        if not summary or not summary.text().rstrip(' +−').endswith('?'):
            continue
        question = summary.text().rstrip(' +−')
        answer = ' '.join(' '.join(c.text() if isinstance(c, Node) else c for c in node.children if c is not summary).split())
        if answer:
            questions.append({'@type': 'Question', 'name': question, 'acceptedAnswer': {'@type': 'Answer', 'text': answer}})
    crumb = next((n for n in main_nodes if 'breadcrumb' in n.attrs.get('aria-label', '').lower() or set(n.attrs.get('class', '').split()) & {'breadcrumbs', 'crumb', 'seo-crumb'}), None)
    breadcrumbs = []
    if crumb:
        def collect(n):
            if n.tag == 'a':
                breadcrumbs.append((n.text(), urljoin(canonical, n.attrs['href'])))
            elif n.tag not in {'svg', 'script', 'style'}:
                for child in n.children:
                    if isinstance(child, Node):
                        collect(child)
                    elif child.strip(' /\n\t'):
                        breadcrumbs.append((' '.join(child.strip(' /\n\t').split()), canonical))
        collect(crumb)
    return {'title': title, 'heading': heading, 'description': meta.get('description', title),
            'image': meta.get('og:image'), 'text': main.text(), 'breadcrumbs': breadcrumbs,
            'questions': questions, 'modified': date_value(modified[1]) if modified else None,
            'has_updated': 'Updated' in byline,
            'author': author[1].strip() if author else None, 'nodes': main_nodes}


def align_graph(graph, source, canonical):
    """Normalize identities and facts without altering visible editorial content."""
    graph = deepcopy(graph)
    visible = content(source, canonical)
    page = next(n for n in graph if n.get('@id') == canonical + '#webpage')
    if page['@type'] in {'Article', 'TechArticle', 'BlogPosting'}:
        article = {k: v for k, v in page.items() if k in {'@type', 'headline', 'description', 'datePublished', 'dateModified', 'author', 'publisher', 'image'}}
        article.update({'@id': canonical + '#article', 'mainEntityOfPage': {'@id': page['@id']}})
        if article['@type'] == 'TechArticle':
            article['@type'] = 'Article'
        for key in ['headline', 'datePublished', 'dateModified', 'author', 'image']:
            page.pop(key, None)
        page['@type'] = 'WebPage'
        page['mainEntity'] = {'@id': article['@id']}
        graph.append(article)
    page['inLanguage'] = 'en'
    page['name'], page['description'] = visible['title'], visible['description']
    page['publisher'] = {'@id': BASE + '/#organization'}
    if canonical in {BASE + '/blog/', BASE + '/products/'}:
        page['@type'] = 'CollectionPage'
    if page['@type'] == 'CollectionPage' and not any(n.get('@type') == 'ItemList' for n in graph):
        resources = []
        seen = set()
        for container in visible['nodes']:
            if container.tag not in {'article', 'a'}:
                continue
            children = list(container.nodes())
            heading = next((n.text() for n in children if n.tag in {'h2', 'h3'}), None)
            link = next((n for n in children if n.tag == 'a' and n.attrs.get('href')), None)
            if not heading or not link:
                continue
            url = urljoin(canonical, link.attrs['href'])
            if not url.startswith(BASE + '/') or url == canonical or url in seen:
                continue
            if canonical != BASE + '/products/' and not url.startswith(canonical):
                continue
            resources.append({'@type': 'ListItem', 'position': len(resources) + 1, 'name': heading, 'url': url})
            seen.add(url)
        if resources:
            catalogue_id = canonical + '#resources'
            graph.append({'@type': 'ItemList', '@id': catalogue_id, 'name': visible['heading'], 'itemListElement': resources})
            page['mainEntity'] = {'@id': catalogue_id}
    for node in graph:
        if node.get('@type') in {'Article', 'TechArticle', 'BlogPosting'}:
            # Google documents Article, NewsArticle and BlogPosting explicitly.
            if node['@type'] == 'TechArticle':
                node['@type'] = 'Article'
            node['headline'] = visible['heading']
            # A site-wide facts review is not the modification date of every article.
            modified = visible['modified']
            if modified:
                node['dateModified'] = modified
            else:
                node.pop('dateModified', None)
            if visible['author'] == 'LC Bridge editorial team':
                node['author'] = {'@type': 'Organization', '@id': BASE + '/about/#editorial-team',
                                  'name': 'LC Bridge editorial team', 'url': BASE + '/about/#editorial-team'}
            elif visible['author']:
                node['author'] = {'@type': 'Person', 'name': visible['author']}
            else:
                node.pop('author', None)
            if visible['image']:
                node['image'] = [visible['image']]
        if node.get('@type') == 'BreadcrumbList':
            node['@id'] = canonical + '#breadcrumbs'
            if len(visible['breadcrumbs']) >= 2:
                node['itemListElement'] = [{'@type': 'ListItem', 'position': i + 1, 'name': name, 'item': url}
                                         for i, (name, url) in enumerate(visible['breadcrumbs'])]
            page['breadcrumb'] = {'@id': node['@id']}
        if node.get('@id') == BASE + '/#organization':
            node.update(deepcopy(FACTS['organization']))
            node['logo'] = {'@type': 'ImageObject', 'url': BASE + '/assets/lcbridge-lockup-black.png'}
            node['contactPoint'] = {'@type': 'ContactPoint', 'contactType': 'customer support', 'email': 'support@lcbridge.app', 'url': BASE + '/about/'}
    graph = [n for n in graph if n.get('@type') != 'FAQPage']
    if visible['questions']:
        # Retained for semantic consumers; Google retired FAQ rich results in May 2026.
        graph.append({'@type': 'FAQPage', '@id': canonical + '#faq-schema',
                      'isPartOf': {'@id': page['@id']}, 'mainEntity': visible['questions']})
    return graph


def dumps(graph, indent=None):
    # HTML script parsing happens before JSON parsing; escape < without changing text.
    return json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, indent=indent).replace('<', '\\u003c')
