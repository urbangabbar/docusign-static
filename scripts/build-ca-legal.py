"""Build /community-agents/privacy/ and /community-agents/terms/ from the setup guide's page shell.
Facts come from the production app code (see PR notes). Re-run after editing the copy below."""
import json, re
from pathlib import Path
from html import escape as e

ROOT = Path(__file__).resolve().parent.parent
SHELL = (ROOT / 'community-agents/how-to-add-ai-agent-highlevel-community/index.html').read_text()
UPDATED, UPDATED_ISO = '25 October 2026', '2026-10-25'
ADDRESS = '23–24 Omaxe Greens Extension, Omaxe City-1, Indore, Madhya Pradesh 453771, India'
MAIL = '<a href="mailto:support@lcbridge.app">support@lcbridge.app</a>'


def table(head, rows):
    th = ''.join(f'<th scope="col">{h}</th>' for h in head)
    tr = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows)
    return f'<div class="seo-table"><table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


def page(slug, title, h1, description, sections, lede):
    url = f'https://lcbridge.app/community-agents/{slug}/'
    toc = ''.join(f'<a href="#{i}">{e(h)}</a>' for i, h, _ in sections)
    body = ''.join(f'<h2 id="{i}">{e(h)}</h2>{html}' for i, h, html in sections)
    main = (f'<h1>{e(h1)}</h1><p class="seo-byline">Updated <time datetime="{UPDATED_ISO}">{UPDATED}</time></p>\n'
            f'<p class="lcb-lede">{lede}</p>\n'
            f'<details class="ds-guide-browse"><summary>On this page</summary><nav class="ds-section-links" aria-label="On this page">{toc}</nav></details>\n'
            f'{body}\n')
    s = SHELL
    head_meta = {
        r'<title>.*?</title>': f'<title>{e(title)}</title>',
        r'<meta name="description" content="[^"]*">': f'<meta name="description" content="{e(description)}">',
        r'<link rel="canonical" href="[^"]*">': f'<link rel="canonical" href="{url}">',
        r'<meta property="og:type" content="[^"]*">': '<meta property="og:type" content="website">',
        r'<meta property="og:title" content="[^"]*">': f'<meta property="og:title" content="{e(title)}">',
        r'<meta property="og:description" content="[^"]*">': f'<meta property="og:description" content="{e(description)}">',
        r'<meta property="og:url" content="[^"]*">': f'<meta property="og:url" content="{url}">',
    }
    for pat, rep in head_meta.items():
        s, n = re.subn(pat, lambda _m: rep, s, count=1, flags=re.S)
        assert n == 1, pat
    m = re.search(r'(<script id="lcbridge-structured-data" type="application/ld\+json">)(.*?)(</script>)', s, re.S)
    ld = json.loads(m.group(2))
    shared = [n for n in ld['@graph'] if n['@type'] in ('Organization', 'WebSite', 'Brand')]
    crumbs = [('Home', 'https://lcbridge.app/'), ('Community Agents', 'https://lcbridge.app/community-agents/'), (h1, url)]
    graph = shared + [
        {'@type': 'WebPage', '@id': url + '#webpage', 'url': url, 'name': title, 'description': description,
         'dateModified': UPDATED_ISO, 'about': {'@id': 'https://lcbridge.app/#gohighlevel-platform'},
         'isPartOf': {'@id': 'https://lcbridge.app/#website'}, 'publisher': {'@id': 'https://lcbridge.app/#organization'},
         'breadcrumb': {'@id': url + '#breadcrumbs'}, 'inLanguage': 'en'},
        {'@type': 'BreadcrumbList', '@id': url + '#breadcrumbs', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(crumbs)]}]
    s = s[:m.start()] + m.group(1) + '\n' + json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, indent=2) + '\n' + m.group(3) + s[m.end():]
    s, n = re.subn(r'<nav class="seo-crumb ds-crumb" aria-label="Breadcrumb">.*?</nav>',
                   lambda _m: f'<nav class="seo-crumb ds-crumb" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/community-agents/">Community Agents</a> / {e(h1)}</nav>', s, count=1, flags=re.S)
    assert n == 1
    start = s.index('<h1>')
    end = s.index('<section class="ds-next"')
    end_section = s.index('</section>', end) + len('</section>')
    s = s[:start] + main + s[end_section:]
    out = ROOT / f'community-agents/{slug}/index.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(s)


PRIVACY = [
    ('who-we-are', 'Who we are', f'<p>Community Agents is an app for HighLevel communities made by LC Bridge ({ADDRESS}). This notice explains what the app and the Community Agents pages on lcbridge.app collect, why, and the choices you have. Questions or requests: {MAIL}.</p>'
     '<p>If you run a community, you decide what the app connects to, and we process your members’ content on your behalf to provide the service. If you are a member of a community that uses Community Agents, please contact that community’s owner first; we will help them answer your request.</p>'),
    ('what-we-collect', 'What we collect', table(['Source', 'What we receive'], [
        ['HighLevel, when you install', 'Account and sub-account IDs, company name, company email, white-label domain, installer name and email, and the access tokens HighLevel issues to the app.'],
        ['Your connected community', 'Member profiles (name, email, avatar, role, status, join and activity dates), groups, posts, comments, and direct messages sent to the member accounts you connect for your agents.'],
        ['You, in the app', 'Portal logins for your AI member accounts, agent instructions and knowledge, settings, and, if you choose, your own AI provider key.'],
        ['Billing', 'Subscription status and AI usage. Payments are handled by HighLevel; we never receive card details.'],
        ['Using the app', 'Product analytics events without community content, and session recordings with all text and inputs masked, for signed-in users.'],
        ['Our website', 'Pages visited and button clicks (Google Analytics, RB2B on lcbridge.app pages) and, only if you allow advertising cookies, Meta pixel events used to measure our ads.'],
    ]) + '<p>Before 26 October 2026, the install page also asked for a name, email address and phone number. We keep those records to help with installations and you can ask us to delete them.</p>'),
    ('how-we-use-it', 'How we use it', '<ul><li><strong>Run your agents.</strong> Generate replies from the knowledge and instructions you supply, in the places you enable.</li>'
     '<li><strong>Member Insights.</strong> Summarise a member’s synced posts and comments, including goals, interests and possible buying interest, with the quoted evidence. Insights are shown only to signed-in users of that sub-account. We do not contact members based on them, and they make no automated decisions about anyone.</li>'
     '<li><strong>Billing and usage.</strong> Meter AI usage and charge through HighLevel.</li>'
     '<li><strong>Support and service messages.</strong> Help with installation and send account emails.</li>'
     '<li><strong>Security.</strong> Protect accounts, detect abuse and keep the service running.</li>'
     '<li><strong>Product updates.</strong> We add the installing business to our own CRM to send product news. You can unsubscribe at any time.</li>'
     '<li><strong>Measure our marketing.</strong> Understand which pages and ads lead to installs.</li></ul>'),
    ('ai-processing', 'How AI processing works', '<p>To write a reply or an insight, the app sends the relevant community content, your knowledge and your instructions to an AI model through OpenRouter. Depending on the model chosen for an agent, the model provider may be OpenAI, Anthropic, Google, DeepSeek, Mistral, Moonshot or Z.ai. Those providers process the content under their own terms. Search over your knowledge uses an embedding model that runs on our own servers.</p>'
     '<p>We do not use your community content to train any model we operate. AI disclosure is on by default so members can tell a reply came from AI; we recommend keeping it on.</p>'),
    ('sharing', 'Who we share it with', '<p>We do not sell personal information. We share it only with the services that help us run Community Agents:</p>' + table(['Service', 'Purpose'], [
        ['HighLevel', 'Platform, installation, sign-in and billing'],
        ['Railway', 'Hosting and database'],
        ['OpenRouter and the AI model providers above', 'Generating replies and insights'],
        ['PostHog (United States)', 'Product analytics in the app'],
        ['Resend', 'Account and service email'],
        ['Google Analytics, RB2B', 'Website analytics on lcbridge.app'],
        ['Meta', 'Ad measurement, only after you allow advertising cookies'],
    ]) + '<p>We may also disclose information when the law requires it, or to protect our users and the service.</p>'),
    ('transfers', 'Where data is processed', '<p>Our service providers process data in the United States and other countries, and our team works from India. Where the law requires it, we rely on appropriate safeguards for these transfers.</p>'),
    ('retention', 'How long we keep it', '<p>We keep account and community data while the app is installed for that sub-account so your agents and insights keep working. Ask us at any time and we will delete your sub-account’s data within 30 days, apart from records we must keep for billing, tax or legal reasons. Signed-out sessions are removed within an hour of expiring, and Meta advertising identifiers are removed after 30 days.</p>'),
    ('your-choices', 'Your rights and choices', f'<p>You can ask to access, correct, export or delete your personal information, or object to how we use it, by emailing {MAIL}. We reply within 30 days. Depending on where you live, you may also have the right to complain to your data protection authority.</p>'
     '<ul><li>Turn agents off, narrow where they participate, or pause any conversation from the app.</li><li>Choose “Decline” on the advertising cookie notice, or “Keep analytics off” in the site’s analytics settings.</li><li>Unsubscribe from product emails with the link in any email.</li></ul>'),
    ('cookies', 'Cookies', table(['Cookie', 'Purpose', 'Lasts'], [
        ['ca_session', 'Keeps you signed in to the app', '30 days'],
        ['ca_oauth_state', 'Protects the HighLevel install step', '10 minutes'],
        ['ca_install', 'Continues setup after installing', '1 day'],
        ['ca_marketing_consent', 'Remembers your advertising cookie choice', '180 days'],
        ['ca_meta_context, ca_meta_install', 'Connects an ad visit to an install, only with consent', '30 and 7 days'],
        ['Google Analytics, RB2B, Meta', 'Website analytics and ad measurement (see above)', 'Set by each provider'],
    ]) + '<p>Visitors in the EEA, UK and Switzerland are not given Google Analytics cookies unless they allow analytics.</p>'),
    ('security', 'Security', '<p>OAuth tokens, portal logins and customer API keys are encrypted with AES-256-GCM before they are stored. HighLevel webhooks are verified by signature, administrative access is restricted, and failed sign-ins are rate limited. No system is perfectly secure; tell us at once if you suspect a problem.</p>'),
    ('children', 'Children', '<p>Community Agents is a business tool and is not directed to children under 13. Community owners should not connect communities intended for children.</p>'),
    ('changes', 'Changes and contact', f'<p>If we make a material change, we will update this page and tell installed customers before it takes effect. Contact: {MAIL} · LC Bridge, {ADDRESS}.</p>'),
]

TERMS = [
    ('agreement', 'Agreement', f'<p>These terms apply to Community Agents by LC Bridge (“we”, “us”), including the app at community-agents.lcbridge.app. By installing or using it you agree to them on behalf of yourself and the business you install it for. Our <a href="/community-agents/privacy/">privacy notice</a> explains how we handle data. Questions: {MAIL}.</p>'),
    ('the-service', 'The service', '<p>Community Agents lets you connect a HighLevel community, configure AI agents that reply from the knowledge you supply, and review Member Insights about your members. It is installed from the HighLevel Marketplace for each sub-account. Features may change as we improve the product.</p>'),
    ('your-responsibilities', 'Your responsibilities', '<ul><li>You have the authority to connect the community and the member accounts you use for agents, and you keep their logins secure.</li>'
     '<li>You tell your members that AI is used in your community, as your community rules and the law require. AI disclosure is on by default.</li>'
     '<li>You review how your agents behave before and after you enable them. You decide where they participate, and you are responsible for the replies you choose to enable.</li>'
     '<li>You use Member Insights to inform a human follow-up, not to make decisions about a member that have legal or similarly significant effects.</li>'
     '<li>You comply with HighLevel’s terms and with the laws that apply to your community.</li></ul>'),
    ('acceptable-use', 'Acceptable use', '<p>Do not use Community Agents to send spam, deceive or impersonate people, harass anyone, collect data you are not entitled to, break the law, or interfere with the service or HighLevel. We may suspend agents that do.</p>'),
    ('ai-output', 'AI output', '<p>AI replies and insights can be incomplete or wrong. They are generated from your material and the conversations synced from your community, and they are not professional advice. Check what matters before relying on it.</p>'),
    ('fees', 'Fees and billing', '<p>Community Agents costs $47 per month for each sub-account, which includes $47 of AI usage. Usage above that is metered at four times the AI provider’s cost and charged through your HighLevel wallet. Unused included usage does not roll over. Charges are billed by HighLevel, and taxes may apply. If a payment fails, AI activity pauses after a short grace period until payment completes. Current prices are on the <a href="/community-agents/pricing/">pricing page</a>; we will give notice before changing them.</p>'),
    ('cancelling', 'Cancelling', f'<p>You can cancel at any time by cancelling or uninstalling the app in HighLevel. For a refund request, email {MAIL}.</p>'),
    ('your-content', 'Your content', '<p>You keep all rights to your knowledge, instructions and community content. You give us permission to process it only to provide and support the service for you, as described in the privacy notice.</p>'),
    ('our-service', 'Our service', '<p>We own Community Agents and its software and design. You may not copy, resell or reverse engineer it, except as the law allows.</p>'),
    ('third-parties', 'Third-party services', '<p>The service depends on HighLevel, AI model providers and other services we do not control. Their outages or changes can affect Community Agents, and their own terms apply to your use of them.</p>'),
    ('suspension', 'Suspension and ending', '<p>We may suspend or end access if these terms are breached, payment fails, or we must do so to protect users or comply with the law. You can stop using the service at any time.</p>'),
    ('disclaimers', 'Disclaimers and liability', '<p>The service is provided “as is” and “as available”, without warranties to the extent the law allows. To the extent the law allows, we are not liable for indirect or consequential losses, and our total liability for any claim is limited to the fees you paid for Community Agents in the 12 months before the claim.</p>'),
    ('indemnity', 'Indemnity', '<p>You agree to cover our reasonable losses from claims caused by your content, your community, or your breach of these terms.</p>'),
    ('law', 'Governing law and disputes', f'<p>These terms are governed by the laws of the State of Delaware, United States. Before starting any formal claim, contact us at {MAIL} so we can try to resolve it informally within 30 days.</p>'),
    ('changes', 'Changes and contact', f'<p>We may update these terms. If a change is material, we will tell installed customers before it takes effect. Contact: {MAIL} · LC Bridge, {ADDRESS}.</p>'),
]

page('privacy', 'Community Agents for GoHighLevel: Privacy Notice | LC Bridge', 'Community Agents privacy notice',
     'What Community Agents by LC Bridge collects from GoHighLevel and your community, how AI processing works, who we share data with, and your choices.',
     PRIVACY, 'What the Community Agents app and its pages collect, why, and the choices you have.')
page('terms', 'Community Agents for GoHighLevel: Terms of Service | LC Bridge', 'Community Agents terms of service',
     'The terms for using Community Agents by LC Bridge: the service, your responsibilities, AI output, fees through GoHighLevel, cancelling and liability for GoHighLevel sub-accounts.',
     TERMS, 'The terms that apply when you install or use Community Agents.')
print('Built community-agents/privacy/ and community-agents/terms/')
