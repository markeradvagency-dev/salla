# Luxe — Salla Theme

A premium, motion-rich theme for [Salla](https://salla.sa) built on the official **Twilight** engine
(Twig + webpack + Tailwind/SCSS + Salla web components). Forked structurally from the MIT-licensed
[theme-raed](https://github.com/SallaApp/theme-raed) so every required page and runtime hook stays compatible;
the design, home sections, header, cart drawer, quick view and GSAP layer are custom.

> Salla themes are **Twig**, not React/Vue/Alpine. There is no `theme.json`/`settings.json`: everything
> configurable lives in [`twilight.json`](twilight.json). See [ARCHITECTURE.md](ARCHITECTURE.md).

## Structure
```
twilight.json                 theme metadata, settings, features, home-section schema
webpack.config.js             entries → public/  (app, home, product, cart(checkout), luxe …)
src/
  locales/ar.json en.json     translations (custom keys under "luxe.*")
  views/
    layouts/master.twig       design tokens from settings, hooks, scripts, cart drawer
    pages/                    Salla-mandated pages (index, cart, product/*, customer/*, blog/*, …)
    components/
      header/ footer/         header (announcement, mega menu, search, cart) + footer
      home/                   editable sections: hero, featured-categories, featured-products,
                              brand-story, collection-slider, luxe-testimonials, social-grid, newsletter
      product/                card, category-card, quick-view
      ui/                     button, modal, slider, breadcrumb, pagination, newsletter, cart-drawer
  assets/
    js/luxe.js                GSAP: entrance, split-text, scroll reveal, parallax, magnetic, menus
    js/partials/              slider (drag), cart-drawer, quick-view
    styles/06-luxe/           the theme's design layer (imported last in app.scss)
public/                       build output (committed; Salla serves it)
tools/build-twilight.py       regenerates settings/components in twilight.json
tools/verify.py               static check: JSON, includes, components, built assets, locale keys
```

## Develop
Requires Node ≥ 22.18 (or ≥ 24.11) and pnpm.
```bash
pnpm install
pnpm watch              # webpack dev build
npm i -g @salla.sa/cli  # once
salla login
salla theme preview     # live preview against your store
```
Before committing: `pnpm production && pnpm verify`.

## Install on Salla
1. Push to GitHub (`git remote add origin … && git push -u origin main`).
2. Partners Portal → Themes → create a theme → link the repository (or `salla theme publish` with the CLI).
3. In the store dashboard: Design → Themes → choose **Luxe** → Customize.
4. Set the real repo URL in `twilight.json` (`repository`) via `tools/build-twilight.py`.

## Customize (merchant dashboard)
- **Colors:** background, cards, text, muted, accent (Secondary); primary comes from Salla's store color.
- **Animations:** on/off, intensity (subtle/medium/bold), parallax, page entrance. Honors `prefers-reduced-motion`.
- **Header/cart:** announcement bar, sticky header, cart drawer, quick view.
- **Home sections:** add/reorder from the dashboard; each has an enable switch, images and text.
- **Newsletter:** Salla has no native newsletter API. Paste your provider's (Mailchimp/Klaviyo/…) form action URL
  in *luxe_newsletter_action*; the email field name defaults to `EMAIL`.

## Notes / limits
- Checkout and thank-you flows are Salla-hosted; the theme styles the cart and links into checkout.
- Product grid pagination/filters/sorting use Salla's `<salla-products-list>` / `<salla-filters>`.
- Demo images are Unsplash URLs — replace them in the dashboard before going live.
- Not yet run against a live Salla store from this environment (needs `salla login`); run `salla theme preview` and check
  the cart drawer item fields and the `color` setting format first.
