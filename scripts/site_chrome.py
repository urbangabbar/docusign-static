"""Shared, server-rendered navigation and footer for every LC Bridge page."""
from pathlib import Path
from html import escape
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
PRODUCTS=json.loads((ROOT/'data/site-navigation.json').read_text())['products']

def version(asset):return asset+'?v='+hashlib.sha256((ROOT/asset.lstrip('/')).read_bytes()).hexdigest()[:8]
def anchor(url,label):return f'<a href="{escape(url)}">{escape(label)}</a>'
def product_switcher():
    items=''.join(f'<a href="{p["url"]}" data-product="{p["id"]}"><strong>{escape(p["name"])}</strong><span>{escape(p["description"])}</span><small>{p["status"]}</small></a>' for p in PRODUCTS)
    return '<details class="lcb-product-switcher" data-product-switcher><summary>Products <span aria-hidden="true">⌄</span></summary><nav class="lcb-product-panel" aria-label="LC Bridge products">'+items+anchor('/products/','View all products →')+'</nav></details>'
def product_bridge():
    return '<div class="lcb-site-bridge"><div class="lcb-chrome-wrap"><a class="lcb-parent-link" href="/" aria-label="Back to LC Bridge"><span aria-hidden="true">←</span><img src="/assets/lcbridge-lockup-black.svg" alt="LC Bridge" width="108" height="36"></a>'+product_switcher()+'</div></div>'
def render_footer():
    product_links=''.join(anchor(p['url'],p['name']) for p in PRODUCTS)+anchor('/products/','All products')
    learn=anchor('/google-sheets-integration/templates/','25 Google Sheets report templates')+''.join(anchor(p['docs'],p['name'].replace(' integration','')+' docs') for p in PRODUCTS)+anchor('/blog/','Guides & articles')
    company=anchor('/about/','About LC Bridge')+anchor('/highlevel-development/','Custom development')+anchor('/book-a-call/','Talk to our team')+anchor('mailto:support@lcbridge.app','support@lcbridge.app')
    notices=anchor('/google-sheets-integration/privacy/','Google Sheets privacy')+anchor('/google-sheets-integration/terms/','Google Sheets early-access terms')+anchor('/docusign-integration/privacy','DocuSign privacy')+anchor('/docusign-integration/terms','DocuSign terms')
    return '<footer class="lcb-site-footer" data-shared-footer><div class="lcb-chrome-wrap"><div class="lcb-footer-top"><a href="/" aria-label="LC Bridge home"><img src="/assets/lcbridge-lockup-black.svg" alt="LC Bridge" width="180" height="60" loading="lazy"></a><p>Products and custom software.<br>Built for GoHighLevel.</p><a class="lcb-footer-home" href="/">Back to LC Bridge <span aria-hidden="true">↗</span></a></div><div class="lcb-footer-columns"><nav aria-label="Footer products"><h2>Products</h2>'+product_links+'</nav><nav aria-label="Footer resources"><h2>Learn</h2>'+learn+'</nav><nav aria-label="Footer company"><h2>Company</h2>'+company+'</nav><nav aria-label="Product notices"><h2>Product notices</h2>'+notices+'</nav></div><div class="lcb-footer-bottom"><p class="lcb-platform-context">For GoHighLevel (GHL), also known as HighLevel.</p><p>LC Bridge is an independent company. GoHighLevel, Google Sheets, and DocuSign are trademarks of their respective owners and do not sponsor or endorse LC Bridge.</p><div><span>© 2026 LC Bridge</span><button type="button" class="lcb-consent-link" id="analytics-settings">Analytics preferences</button></div></div></div></footer>'
def consent_dialog():
    return '<dialog class="lcb-consent-dialog" id="analytics-dialog" aria-labelledby="analytics-title"><h2 id="analytics-title">Analytics preferences</h2><p id="analytics-description">Optional analytics require your consent before any analytics requests are sent. Hosted forms have their own provider controls.</p><div><button type="button" data-analytics-consent="granted">Allow analytics</button><button type="button" data-analytics-consent="denied">Keep analytics off</button></div></dialog>'
def apply_chrome(source,path):
    path='/'+path.lstrip('/')
    # Remove previous platform-alias blocks; the common footer supplies one visible block.
    source=re.sub(r'<p\b[^>]*class="[^"]*\blcb-platform-context\b[^"]*"[^>]*>.*?</p>','',source,flags=re.S)
    source=re.sub(r'<footer\b.*?</footer>',lambda _:render_footer(),source,flags=re.S)
    source=re.sub(r'\s*<dialog\b[^>]*id="analytics-dialog".*?</dialog>','',source,flags=re.S)
    source=re.sub(r'<div class="lcb-site-bridge">.*?</div></div>','',source,flags=re.S)
    # Product-family navigation retains its own tasks. The parent bar makes the company and sibling products explicit.
    is_product=path.startswith(('/google-sheets-integration/','/community-agents/','/docusign-integration/')) or 'data-sheets-generated="true"' in source
    if is_product:
        if not re.search(r'\bid=[\"\']main[\"\']',source):
            source=re.sub(r'<main\b(?![^>]*\bid=)', '<main id="main"',source,count=1)
        start=re.search(r'<body\b[^>]*>',source).end()
        skip=re.search(r'<a\b[^>]*href=["\']#main["\'][^>]*>.*?</a>',source[start:],re.S)
        if skip and skip.start()<1000:pos=start+skip.end()
        else:
            source=source[:start]+'<a class="lcb-site-skip" href="#main">Skip to content</a>'+source[start:];pos=start+len('<a class="lcb-site-skip" href="#main">Skip to content</a>')
        source=source[:pos]+product_bridge()+source[pos:]
    else:
        head,sep,body=source.partition('<main')
        # Existing generated switchers are replaced to reflect the same source order.
        head=re.sub(r'<details class="lcb-product-switcher".*?</details>',lambda _:product_switcher(),head,flags=re.S)
        head=re.sub(r'<a\b[^>]*href="(?:/products/|#products)"[^>]*>\s*Products\s*</a>',lambda _:product_switcher(),head,flags=re.S)
        source=head+sep+body
    # Correct company-logo destinations without changing product identity links.
    source=re.sub(r'<a\b[^>]*aria-label="LC Bridge home"[^>]*>',lambda m:re.sub(r'href="[^"]*"','href="/"',m[0]),source)
    source=re.sub(r'\s*<link\b[^>]*href="/assets/site-chrome.css[^\"]*"[^>]*>','',source)
    source=re.sub(r'\s*</head>',lambda _:'\n<link rel="stylesheet" href="'+version('/assets/site-chrome.css')+'">\n</head>',source,count=1)
    source=re.sub(r'\s*<script\b[^>]*src="/assets/site-chrome.js[^\"]*"[^>]*>\s*</script>','',source)
    source=re.sub(r'\s*</body>',lambda _:consent_dialog()+'<script src="'+version('/assets/site-chrome.js')+'" defer></script>\n</body>',source,count=1)
    return source
