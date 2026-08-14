# Grand Lexther Marketing, Inc. — Website

Static HTML/CSS/JS catalog site (not e-commerce). Customers browse products and
brands, then call/email/message to inquire — there is no cart or checkout.

## How it's built

This site is generated from a Python script, not hand-edited page by page:

- `generate.py` — the source of truth. Builds every HTML page from shared
  Python functions (`header()`, `footer()`, `thumb()`, `carousel()`, etc.) plus
  per-category/per-brand data lists near the top of the file.
- `styles.css` — all styling, inlined into every generated HTML file's `<style>`
  tag at build time (so each page is self-contained — no external CSS/JS
  dependency, which matters for previewing single files).
- `site.js` — mobile nav toggle, carousel controller, product gallery swap,
  quantity stepper. Also inlined into every page at build time.

**To make changes: edit `generate.py` and/or `styles.css`/`site.js`, then
re-run `python3 generate.py` to regenerate all HTML files.** Don't hand-edit
the generated `.html` files directly — those edits will be lost on the next
regeneration. (If `generate.py` isn't in this folder, the site was exported as
plain HTML; ask me to reconstruct the generator, or just edit the HTML/CSS
directly going forward.)

## Site structure

- `index.html` — homepage: hero → "Why Grand Lexther" (4 trust pillars) →
  product groups teaser → brands teaser → stats band → Who We Are teaser
  (links out to `who-we-are.html`) → Contact
- `who-we-are.html` — dedicated About page: story/history, established-year +
  years-in-business + location stat plate, "What We Stand For" pillars, CTA
- `products.html` — hub listing all 14 categories, grouped under 7 sections
- `brands.html` — dedicated brands page, grouped by product line (Bearings,
  Power Drills, Electrical Wires & Cables)
- 14 category pages (`welding-materials.html`, `abrasives.html`, `bearings.html`,
  etc.) — each has a photo gallery carousel + item cards. Item cards are
  intentionally minimal: picture + name only, no description text — the
  item's own product page (if it has one) or the category page itself
  carries the detail, so the card doesn't need to repeat it
- `mig-wire-er70s-6.html` — single-*product* detail page with real specs from
  the client (image gallery, quick facts, inquiry box, spec table, packaging
  table, related products). Built by hand in the "4. Generate a single-product
  page" section of `generate.py` — this level of detail needs real per-product
  data, so don't replicate the spec/packaging tables for other items without it.
- Per-item product pages, one per item (gallery + quick description +
  inquiry box + related items, no spec/packaging tables — we don't have real
  specs beyond MIG Wire), built by the generic `product_page()` helper
  (section "4b" in `generate.py`). Categories done so far: **Gloves** (7
  items), **Packaging Materials** (16 items), **Abrasives** (14 items),
  **Tubing & Structural Steel** (10 items) — see each category's `items`
  list in `CATEGORIES` for the exact filenames (3rd
  tuple element). To add another category: give its `items` entries a 3rd
  tuple element (the page filename), then loop `product_page()` over them
  like the existing blocks do. Ask before assuming which category/items
  should get this treatment next.

Nav is fixed to: **Who We Are, Products, Brands, Contact**.

**Products mega-menu**: "Products" in the header opens a flyout listing all
14 categories (flat, like Wyler's `/brands/` browse-categories menu); a
category opens a second flyout listing that category's items. Each item
links to its own product page if its `CATEGORIES` entry has one (see
Gloves), otherwise falls back to `{category}.html#{item-slug}`
(`item_href()` in `generate.py`). Built from `CATEGORIES`/`MEGA_MENU_HTML`
in `generate.py` (`mega_menu_html()`), styled in `styles.css` under
"Products mega-menu".

The **name/label is always a separate element from the chevron**, on
purpose: `.mega-label`/`.mega-cat-link` (an `<a>`, navigates to the
page) sits next to `.mega-toggle`/`.mega-cat-toggle` (a `<button
type="button">`, only ever expands/collapses — never navigates). Don't
merge them back into one clickable element; that's what made the mobile
arrow-vs-navigate distinction impossible before.
- **Desktop** (`@media (hover: hover) and (pointer: fine)`): hovering the
  row opens the flyout via a hover-intent script in `site.js` (adds/removes
  `.mega-open` with a ~250ms close delay so a diagonal mouse path from the
  trigger into the flyout, or from a category into its item sub-panel,
  doesn't slip through the gap and close it early). A plain CSS `:hover`
  fallback (same media guard) and `:focus-within` (keyboard, ungated) cover
  the no-JS case. The chevron button also works here (click toggles
  `.mega-open` directly) but is mostly redundant with hover.
- **Mobile** (`@media (max-width: 860px)`, no hover): the chevron
  button is the only way to expand the list — clicking/tapping it toggles
  `.mega-open` (always-on click handlers in `site.js`, not gated) and the
  flyout collapses into a static, dark-themed, tap-to-expand accordion
  (`max-height` transition instead of the desktop's floating
  opacity/transform dropdown). Tapping the name still navigates normally.
Open/close is animated with a CSS `opacity`/`transform`/`max-height`
transition rather than a JS animation library — same visual effect, no
external dependency; swap in anime.js here if a fancier effect (e.g.
staggered item reveal) is ever wanted.
**Do not re-add `overflow-y:auto`/`max-height` to `.mega-menu` or
`.mega-sub`** — that was the bug that made the second-level flyout
invisible: setting `overflow-y` to non-`visible` also computes `overflow-x`
to `auto`, which clips the `.mega-sub` panel since it escapes to the right
via `left:100%`. If the category/item list ever gets too tall for the
viewport, fix it by scrolling an inner wrapper, not `.mega-menu`/`.mega-sub`
themselves. Item ids are slugified item names (`slugify()`), added to each
item-card in the category page loop — keep item names unique within a
category or ids collide.

## Design system

- Colors pulled from the client's real calling card + a later "make it more
  visually appealing" request: deep charcoal-green ink `#16241D`, forest green
  `#1C7A41` / `#125C2F`, warm gold accent `#C89B3C` / `#A67F2C`, cream
  background `#FAF8F2`. No navy anymore (an earlier version used navy — since
  replaced).
- Headings: Playfair Display (serif, echoes the client's card wordmark). Body:
  IBM Plex Sans. Labels/kickers/mono chips: IBM Plex Mono.
- Cards have soft shadows + hover lift (`--shadow-sm`/`--shadow-md`), ~12px
  radius. Icon badges are circular gradient (green/gold alternating).

## Images — currently all placeholders

Every product/category/brand image is a styled SVG placeholder tile labeled
"SAMPLE IMAGE" (built by the `thumb()` / `carousel()` helpers in
`generate.py`) — not real photos, to avoid using unlicensed web images on a
client's live business site. Hover-zoom and carousel/gallery behavior are
already wired up and will work the same once real `<img>` tags replace the
placeholders.

**Brand logos are the immediate next step** — the client is uploading brand
name/logo images to add to `brands.html`.

## Business facts (real, from the client)

- Legal name: Grand Lexther Marketing, Inc.
- Established: 2003 (`ESTABLISHED_YEAR` in `generate.py` — "years in business"
  on `who-we-are.html` and the homepage stats band is derived from this
  automatically each time the site is regenerated, not hardcoded)
- Tagline: "Wholesaler, Retailer, and Importer of Quality Industrial and
  Construction Materials"
- Address: 197 T. Claudio St., Brgy. Sta. Lucia, San Juan City, Philippines
- Mobile/Viber: (0917) 896 0800 — Telephone: 8366-2167 / 8367-8298
- Email: grandlexther2012@gmail.com
- Content emphasis the client asked for: top-quality materials/equipment,
  trusted industrial supplier, trusted brands, exceptional service,
  best/competitive prices — this is already woven into hero copy and the
  "Why Grand Lexther" section.

## Still pending / open TODOs

- Real product photos (client is sourcing these)
- Real product/item list with specs, beyond what's in `generate.py`'s
  `CATEGORIES` list
- Brand logo images (client uploading soon — go into `brands.html`)
- Business hours (still a placeholder `[Mon–Sat, 8:00 AM – 5:00 PM]`)
- Certifications, warehouse location, delivery coverage area — not yet on
  `who-we-are.html`, ask the client if there's more to add beyond the
  established-2003 story
- Stats band "Clients Served" number — still `[X]`, needs a real figure from
  the client (years-in-business is now solved via `ESTABLISHED_YEAR`)
- Gloves, Packaging Materials, Abrasives, and Tubing & Structural Steel are
  the only categories with per-item pages so far (description + placeholder
  photos, via `product_page()` — see Site structure above). Deciding which
  other categories/items should get the same treatment next, and whether
  real photos are available yet for these four
- Eventually: domain + hosting choice to go live (currently local-only)

## Reference sites the client likes

- https://yalehardwareph.com/ and https://machinebanks.com/ — both PH
  industrial/hardware suppliers. The trust-building homepage flow (hero →
  brands → stats → about → contact) is modeled loosely on Machinebanks. Their
  sprawling mega-menus and cart/account systems were intentionally *not*
  copied — this site stays simpler since it's inquiry-based, not e-commerce.
