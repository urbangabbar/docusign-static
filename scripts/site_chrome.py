"""Shared, server-rendered navigation and footer for every LC Bridge page."""
from pathlib import Path
from html import escape
import hashlib,json,re
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
PRODUCTS=json.loads((ROOT/'data/site-navigation.json').read_text())['products']

def version(asset):return asset+'?v='+hashlib.sha256((ROOT/asset.lstrip('/')).read_bytes()).hexdigest()[:8]
def anchor(url,label):return f'<a href="{escape(url)}">{escape(label)}</a>'
def product_switcher():
    items=''.join(f'<a href="{p["url"]}" data-product="{p["id"]}"><strong>{escape(p["name"])}</strong><span>{escape(p["description"])}</span><small>{p["status"]}</small></a>' for p in PRODUCTS)
    return '<details class="lcb-product-switcher" data-product-switcher><summary>Products <span aria-hidden="true">⌄</span></summary><nav class="lcb-product-panel" aria-label="LC Bridge products">'+items+anchor('/products/','View all products →')+'</nav></details>'
def company_links():
    return product_switcher()+anchor('/highlevel-development/','Custom development')+anchor('/about/','About LC Bridge')+anchor('/blog/','Guides')+'<a class="lcb-company-cta" href="/book-a-call/">Talk to us <span aria-hidden="true">↗</span></a>'
def render_company_header():
    return '<header class="lcb-company-header" aria-label="LC Bridge" data-company-header><div class="lcb-chrome-wrap lcb-company-row"><a class="lcb-company-logo" href="/" aria-label="LC Bridge home"><img src="/assets/lcbridge-lockup-black.svg" alt="LC Bridge" width="168" height="56"></a><nav class="lcb-company-desktop" aria-label="LC Bridge main navigation">'+company_links()+'</nav><details class="lcb-company-menu" data-company-menu><summary aria-label="LC Bridge menu">Menu <span aria-hidden="true">+</span></summary><nav class="lcb-company-mobile" aria-label="LC Bridge mobile navigation">'+company_links()+'</nav></details></div></header>'

class NavigationRange(HTMLParser):
    """Locate the first full navigation block, including nested native menus."""
    def __init__(self,source):
        super().__init__(convert_charrefs=False)
        self.source=source; self.offsets=[0];self.start=None;self.end=None;self.depth=0;self.tag=None;self.stopped=False
        for line in source.splitlines(True):self.offsets.append(self.offsets[-1]+len(line))
        self.feed(source)
    def position(self):
        line,col=self.getpos();return self.offsets[line-1]+col
    def handle_starttag(self,tag,attrs):
        if self.end is not None or self.stopped:return
        if tag=='main' and self.start is None:self.stopped=True;return
        if self.start is None and tag in ('nav','header'):
            self.start=self.position();self.tag=tag;self.depth=1
        elif self.start is not None and tag==self.tag:self.depth+=1
    def handle_endtag(self,tag):
        if self.start is not None and self.end is None and tag==self.tag:
            self.depth-=1
            if not self.depth:self.end=self.source.index('>',self.position())+1

def first_navigation(source):
    start=re.search(r'<body\b[^>]*>',source).end()
    parsed=NavigationRange(source[start:])
    if parsed.start is None or parsed.end is None:raise ValueError('Missing complete navigation')
    return start+parsed.start,start+parsed.end

def render_footer():
    product_links=''.join(anchor(p['url'],p['name']) for p in PRODUCTS)+anchor('/products/','All products')
    learn=anchor('/google-sheets-integration/templates/','25 Google Sheets report templates')+''.join(anchor(p['docs'],p['name'].replace(' integration','')+' docs') for p in PRODUCTS)+anchor('/blog/','Guides & articles')
    company=anchor('/about/','About LC Bridge')+anchor('/highlevel-development/','Custom development')+anchor('/book-a-call/','Talk to our team')+anchor('mailto:support@lcbridge.app','support@lcbridge.app')
    notices=anchor('/google-sheets-integration/privacy/','Google Sheets privacy')+anchor('/google-sheets-integration/terms/','Google Sheets early-access terms')+anchor('/docusign-integration/privacy','DocuSign privacy')+anchor('/docusign-integration/terms','DocuSign terms')
    return '<footer class="lcb-site-footer" data-shared-footer><div class="lcb-chrome-wrap"><div class="lcb-footer-top"><a href="/" aria-label="LC Bridge home"><img src="/assets/lcbridge-lockup-black.svg" alt="LC Bridge" width="180" height="60" loading="lazy"></a><p>Products and custom software.<br>Built for GoHighLevel.</p><a class="lcb-footer-home" href="/">Back to LC Bridge <span aria-hidden="true">↗</span></a></div><div class="lcb-footer-columns"><nav aria-label="Footer products"><h2>Products</h2>'+product_links+'</nav><nav aria-label="Footer resources"><h2>Learn</h2>'+learn+'</nav><nav aria-label="Footer company"><h2>Company</h2>'+company+'</nav><nav aria-label="Product notices"><h2>Product notices</h2>'+notices+'</nav></div><div class="lcb-footer-bottom"><p class="lcb-platform-context">For GoHighLevel (GHL), also known as HighLevel.</p><p>LC Bridge is an independent company. GoHighLevel, Google Sheets, and DocuSign are trademarks of their respective owners and do not sponsor or endorse LC Bridge.</p><div><span>© 2026 LC Bridge</span><button type="button" class="lcb-consent-link" id="analytics-settings">Analytics preferences</button></div></div></div></footer>'
def consent_dialog():
    return '<dialog class="lcb-consent-dialog" id="analytics-dialog" aria-labelledby="analytics-title"><h2 id="analytics-title">Analytics preferences</h2><p id="analytics-description">Optional analytics require your consent before any analytics requests are sent. One exception: the Google Sheets campaign page loads the Meta pixel by default to measure our ads, and Keep analytics off stops it. Hosted forms have their own provider controls.</p><div><button type="button" data-analytics-consent="granted">Allow analytics</button><button type="button" data-analytics-consent="denied">Keep analytics off</button></div></dialog>'
def apply_chrome(source,path):
    path='/'+path.lstrip('/')
    # Remove previous platform-alias blocks; the common footer supplies one visible block.
    source=re.sub(r'<p\b[^>]*class="[^"]*\blcb-platform-context\b[^"]*"[^>]*>.*?</p>','',source,flags=re.S)
    source=re.sub(r'<footer\b.*?</footer>',lambda _:render_footer(),source,flags=re.S)
    source=re.sub(r'\s*<dialog\b[^>]*id="analytics-dialog".*?</dialog>','',source,flags=re.S)
    source=re.sub(r'<div class="lcb-site-bridge">.*?</div></div>','',source,flags=re.S)
    # Replace only a previously generated company header, retaining product navigation below it.
    had_company_header='data-company-header' in source
    source=re.sub(r'<header class="lcb-company-header".*?</header>','',source,flags=re.S)
    is_product=path.startswith(('/google-sheets-integration/','/community-agents/','/docusign-integration/')) or 'data-sheets-generated="true"' in source
    family=next((p['id'] for p in PRODUCTS if path.startswith(p['url'])),None)
    if family is None and 'data-sheets-generated="true"' in source:family='google-sheets'
    if family:
        source=re.sub(r'(<body\b[^>]*)(>)',lambda m:re.sub(r' data-product-family="[^"]*"','',m[1])+' data-product-family="'+family+'"'+m[2],source,count=1)
    if is_product:
        begin,end=first_navigation(source)
        nav=source[begin:end]
        # Mark the existing product header for stacking and identify its navigation separately.
        opening=re.match(r'<(?:nav|header)\b[^>]*>',nav)[0]
        if 'class="' in opening:
            updated=re.sub(r'class="([^"]*)"',lambda m:'class="'+m[1]+('' if 'lcb-product-header' in m[1].split() else ' lcb-product-header')+'"',opening,count=1)
        else:updated=opening[:-1]+' class="lcb-product-header">'
        nav=updated+nav[len(opening):]
        family_name=next(p['name'] for p in PRODUCTS if p['id']==family)
        if nav.startswith('<header') and 'aria-label=' not in updated:
            nav=nav.replace(updated,updated[:-1]+' aria-label="'+family_name+' product navigation">',1)
        nav=re.sub(r'<summary(?![^>]*aria-label)([^>]*)>(?=Menu)',lambda m:'<summary'+m[1]+' aria-label="'+family_name+' menu">',nav)
        nav=nav.replace('aria-label="Main navigation"','aria-label="'+next(p['name'] for p in PRODUCTS if p['id']==family)+' navigation"')
        if family=='community-agents':
            nav=re.sub(r'<a class="ca-brand"[^>]*>', '<a class="ca-brand" href="/community-agents/" aria-label="Community Agents by LC Bridge home">',nav,count=1)
        if path=='/docusign-integration/':
            nav=re.sub(r'<a\b[^>]*aria-label="LCBridge home"[^>]*>.*?</a>', '<a class="brand lcb-docusign-brand" href="/docusign-integration/" aria-label="DocuSign integration by LC Bridge home"><img src="/assets/docusign-logo.svg" alt="DocuSign" width="139" height="28"><span>Integration <small>by LC Bridge</small></span></a>',nav,count=1,flags=re.S)
        source=source[:begin]+nav+source[end:]
    elif not had_company_header:
        begin,end=first_navigation(source)
        source=source[:begin]+source[end:]
    if not re.search(r'\bid=["\']main["\']',source):
        source=re.sub(r'<main\b(?![^>]*\bid=)', '<main id="main"',source,count=1)
    start=re.search(r'<body\b[^>]*>',source).end()
    skip=re.search(r'<a\b[^>]*href=["\']#main["\'][^>]*>.*?</a>',source[start:],re.S)
    if skip and skip.start()<1000:pos=start+skip.end()
    else:
        source=source[:start]+'<a class="lcb-site-skip" href="#main">Skip to content</a>'+source[start:];pos=start+len('<a class="lcb-site-skip" href="#main">Skip to content</a>')
    source=source[:pos]+render_company_header()+source[pos:]
    # Correct company-logo destinations without changing product identity links.
    source=re.sub(r'<a\b[^>]*aria-label="LC Bridge home"[^>]*>',lambda m:re.sub(r'href="[^"]*"','href="/"',m[0]),source)
    source=re.sub(r'\s*<link\b[^>]*href="/assets/site-chrome.css[^\"]*"[^>]*>','',source)
    source=re.sub(r'\s*</head>',lambda _:'\n<link rel="stylesheet" href="'+version('/assets/site-chrome.css')+'">\n</head>',source,count=1)
    source=re.sub(r'\s*<script\b[^>]*src="/assets/site-chrome.js[^\"]*"[^>]*>\s*</script>','',source)
    source=re.sub(r'\s*</body>',lambda _:consent_dialog()+'<script src="'+version('/assets/site-chrome.js')+'" defer></script>\n</body>',source,count=1)
    return source
