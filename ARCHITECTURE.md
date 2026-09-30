# Salla Theme Architecture (Twilight-compatible)

Sources: docs.salla.dev (Develop a Theme, Directory Structure, Twilight.json, Master Layout) and the reference theme https://github.com/SallaApp/theme-raed.

## 1. Key finding: your requested structure differs from Salla's

Salla themes are **Twig** (Twilight engine) + **webpack** + **@salla.sa/twilight**. There is no `sections/`, `snippets/`, `theme.json`, `settings.json` or `config/`.

| You asked for | Salla equivalent |
|---|---|
| theme.json + settings.json | **`twilight.json`** (root): `name`, `repository`, `author_email`, `support_url`, `description`, `features[]`, `settings[]`, `components[]` |
| layouts/ | `src/views/layouts/master.twig` (+ `customer.twig`) |
| pages/ | `src/views/pages/**` (fixed set of names, see below) |
| sections/ (editable home sections) | `twilight.json > components[]` with `path: "home.xxx"` -> `src/views/components/home/xxx.twig` |
| components/, partials/, snippets/ | `src/views/components/**`, `src/views/pages/partials/**`; Twig `{% include %}` |
| app.js / main.css | `src/assets/js/app.js`, `src/assets/styles/app.scss`, built by webpack into `public/` |
| config/ | `webpack.config.js`, `tailwind.config.js`, `postcss.config.js` |
| React/Vue/Alpine | Not used. Vanilla JS + Salla web components (`salla-*`) |

Page names are fixed by Salla, so I can't invent new ones. Missing files show up as 404s or fall back to defaults.

Tech choices:
- **Tailwind** is supported (Raed uses it).
- **GSAP** is fine. It is loaded from `node_modules` via webpack, no CDN.
- **Alpine.js** is *not* used. It adds a second reactivity layer that competes with Salla's web components and adds weight, so I'd use vanilla JS.
- **Checkout is Salla-hosted** and cannot be themed. We only style the cart and link out to checkout.

## 2. Target tree

```
SALLA/
├── twilight.json
├── package.json, pnpm-workspace.yaml
├── webpack.config.js, tailwind.config.js, postcss.config.js
├── .gitignore, README.md
├── public/                      # build output (committed for Salla import; contains dist)
└── src/
    ├── locales/ar.json, en.json
    ├── views/
    │   ├── layouts/master.twig, customer.twig
    │   ├── pages/
    │   │   ├── index.twig               # {% component home %}
    │   │   ├── cart.twig, thank-you.twig, page-single.twig, loyalty.twig, testimonials.twig
    │   │   ├── product/index.twig       # category/listing (filters, sort, pagination)
    │   │   ├── product/single.twig      # product page
    │   │   ├── brands/index|single.twig
    │   │   ├── blog/index|single.twig
    │   │   ├── customer/profile|orders/index|orders/single|wishlist|notifications|wallet.twig
    │   │   └── partials/product/options.twig, reservations.twig
    │   └── components/
    │       ├── header/header.twig       # top bar, mega menu, search, cart icon, mobile menu
    │       ├── footer/footer.twig
    │       ├── product/card.twig, quick-view.twig
    │       ├── ui/button.twig, modal.twig, breadcrumb.twig, pagination.twig, cart-drawer.twig, newsletter.twig
    │       └── home/                    # merchant-editable sections (registered in twilight.json)
    │           hero.twig, featured-categories.twig, featured-products.twig, brand-story.twig,
    │           collection-slider.twig, testimonials.twig, social-grid.twig, newsletter.twig
    └── assets/
        ├── js/app.js, home.js, product.js, products.js, cart.js, order.js
        │   └── partials/ gsap-init.js, reveal.js, parallax.js, product-card.js, cart-drawer.js, main-menu.js, slider.js
        ├── styles/app.scss (+ 01-settings … 05-utilities, ITCSS layering as in Raed)
        ├── images/, fonts/
```

## 3. Rules the engine imposes

1. **master.twig** must contain `{% block styles %}`, `{% block head %}`, `{% block content %}`, `{% block scripts %}` and the hooks `{% hook 'head:start' %}`, `{% hook head %}`, `{% hook 'head:end' %}`. It also needs matching body hooks for scripts and the Salla runtime.
2. Pages start with `{% extends "layouts.master" %}`. Assets are referenced as `{{ 'home.js' | asset }}`. Webpack entries must match those names.
3. **Home page** is `{% component home %}`. The merchant arranges sections in the dashboard from `features` (built-in `component-*`) and `components` (custom).
4. **Custom section** = one `components[]` entry (`key` UUID, bilingual `title`, `icon`, `path`, `fields`) + one Twig file. Field types: `string`, `collection`, `items`, `boolean`, `static`. Formats: `image`, `textarea`, `switch`, `dropdown-list`, `color`, etc. Values are read in Twig via `component.fieldId` and `item['collection.field']`.
5. **Theme settings** (colors, toggles, animation on/off) go in `twilight.json > settings[]` and are read with `theme.settings.get('id', default)`. Brand color comes from `theme.color.primary` (the `color` feature).
6. **Product cards** use Salla's `<custom-salla-product-card>` and the `product-card.js` bundle. Cart, wishlist, search and login use `<salla-add-product-button>`, `<salla-cart-summary>`, `<salla-search>`, `<salla-login-modal>`, `<salla-quick-buy>` and similar components. Only the styling is ours, and behavior stays with Salla.
7. Every text string must live in `locales/ar.json` and `en.json`, and the layout must support **RTL** (`theme.is_rtl`). Arabic-first, so I'll use logical CSS properties.
8. Local dev is `pnpm install`, `pnpm watch` and `salla theme preview` using the Salla CLI. Release is `salla theme publish` or a GitHub import in Partners Portal.

## 4. Mapping your feature list

| Requirement | Implementation |
|---|---|
| Hero, Categories, Featured Products, Brand Story, Collection Slider, Testimonials, Social, Newsletter | Custom `components[]` in `home/*.twig`, each with an enable switch and editable fields |
| Product page: gallery, thumbs, variants, qty, sticky panel, related, reviews | `product/single.twig` using Salla options partial and native add-to-cart. Gallery uses Swiper or fslightbox as in Raed. Sticky panel is CSS `position: sticky` |
| Category: grid, filters, sort, pagination | `product/index.twig` with the `filters` feature, `<salla-products-list>`, and `salla-filters` |
| Cart drawer | Custom drawer built on `<salla-cart-summary>` events (`cart::updated`) with a link to Salla checkout |
| Mega menu, mobile menu | `mega-menu` feature + `main-menu.js`, styled with GSAP transitions |
| Animations | GSAP + ScrollTrigger, in a small lazy-loaded bundle. Guarded by `prefers-reduced-motion` and a theme setting to turn animations off |
| Customization | `twilight.json > settings`: colors, header sticky, dark top bar, animation toggle, per-section toggles |
| Performance | Native `loading="lazy"`, per-page webpack entries, purged Tailwind, deferred scripts |

## 5. Build order
1. Scaffold config (`package.json`, webpack/tailwind/postcss, `twilight.json`, locales)
2. `master.twig` + header/footer
3. Shared UI components
4. Home sections + `components[]` registration
5. Product, category, cart, customer, other required pages
6. GSAP layer
7. `pnpm build` verification, reference check (every `asset`/`include`/`component` path resolves), README, `.gitignore`, `git init` and commit
