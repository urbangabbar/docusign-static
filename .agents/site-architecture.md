# LC Bridge site architecture

Reviewed 2026-10-16 against the public 87-page inventory.

```
LC Bridge (/)
├── Products (/products/)
│   ├── Google Sheets (/google-sheets-integration/)
│   │   ├── Pricing, data catalog, privacy and early-access terms
│   │   ├── Templates hub → 25 report previews
│   │   └── Documentation hub → task guides
│   ├── Community Agents (/community-agents/)
│   │   ├── Pricing
│   │   └── Documentation hub → setup, knowledge and member-context guides
│   └── DocuSign (/docusign-integration/)
│       ├── Pricing, trial, product notices and use cases
│       └── Documentation hub → configuration guides
├── Custom development (/highlevel-development/)
├── About (/about/)
├── Guides (/blog/) → product-specific and integration-method articles
└── Talk to us (/book-a-call/)
```

Every public page uses the same static LC Bridge header and company footer. The company logo returns to `/`. The main menu contains Products, Custom development, About LC Bridge, Guides and Talk to us. The product picker orders Sheets, Community Agents and DocuSign, with all-products access. On mobile it sits inside the company menu.

Product-family pages retain their own header immediately under the company header, with independent product links and a product conversion action. Product logos return to their product overview. Both headers stack while scrolling. Existing task sidebars and content links remain. Sheets articles keep their product navigation, while their breadcrumb reflects their actual Blog URL.

One company footer supplies product, documentation, company and clearly scoped product-notice links. A second large footer would repeat navigation and obscure company context, so product-specific supporting links remain within the page or its local navigation.

URLs, canonicals, forms, install destinations and existing homepage section anchors are preserved. No new hierarchy pages or URL migrations are needed. The existing content strategy and 90-day editorial backlog remain under docs/google-sheets/CONTENT-STRATEGY.md and the data catalogs. Future articles belong under /blog/, link to the appropriate product hub, and answer a distinct task; prioritization needs actual query and accepted-conversion evidence.

The homepage's primary CTA is product discovery; its headline describes the company. Each product keeps its own offer and conversion action. Do not reinterpret the order of products as exclusive company positioning.
