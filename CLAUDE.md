# GLMI — Website

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

**Folder layout (2026)** — pages are split across three levels so the repo
root stays readable:

```
/                      index.html, products.html, brands.html,
                       who-we-are.html, request-quote.html   (5 only)
/categories/           15 category pages
/items/                48 per-item product pages
/images/               real photos + brand logos
```

Because pages sit at different depths, **every generated link is depth-aware**.
The convention: each page passes a `depth` prefix — `""` for the 5 root pages,
`"../"` for anything in `categories/` or `items/` — into `header()`, `footer()`,
`thumb()`, `carousel()`, `brand_item_html()`, and the href helpers
`cat_href()` / `item_page_href()` / `asset()` (all defined at the top of
`generate.py` under "Output layout"). **Never hardcode a bare `foo.html` link
in generated markup** — it will work from root and 404 from a subfolder, which
is easy to miss when spot-checking one page. Use the helpers.

If you add pages or move things, re-verify with a link check across all
generated HTML (resolve every `href`/`src` relative to its own file, ignoring
`<script>`/`<style>` blocks — the inlined `site.js` contains a `${item.url}`
template literal that looks like a broken link but isn't).

- `index.html` — homepage: hero (**banner slideshow** on white,
  CTAs centered below it — see "Hero slideshow") → "Why GLMI" (4 trust pillars) →
  product groups teaser → brands teaser → stats band → Who We Are teaser
  (links out to `who-we-are.html`) → Contact
- `who-we-are.html` — dedicated About page: story/history, established-year +
  years-in-business + location stat plate, "What We Stand For" pillars, CTA
- `products.html` — hub listing all 15 categories as one flat A&ndash;Z grid
  (modeled on wyler.com.ph/products/), Welding Materials pinned first
  regardless of alphabetical order, everything else sorted by title. **No
  group sections** — that was deliberately removed (2026); `GROUP_ORDER`
  and the `.group`/`.group-head` CSS are gone too, don't re-add them.
  Category pages and product-detail pages also no longer show a
  "SEC.02 &middot; Welding & Metal Work" style label (`cat['sec']`/
  `cat['group']` are still on each `CATEGORIES` entry and still drive the
  breadcrumb/sort, just not rendered as a visible badge anymore)
- `brands.html` — dedicated brands page: a flat, ungrouped logo wall (all of
  `BRANDS`), modeled on bakalatbp.com/brands/ — **no per-category grouping,
  don't reintroduce it.** Each tile is either a real logo (`<img>`) or,
  until the client uploads one, a placeholder tile (icon + brand name text).
  `BRANDS` in `generate.py` is `(name, icon_key, img_path_or_None)` — no
  group/product-line field anymore. `brand_item_html()` renders one tile;
  `.brand-wall`/`.brand-tile`/`.brand-placeholder`/`.brand-logo` in
  `styles.css`. The homepage's "Brands we carry" section shows a curated
  subset — `HOMEPAGE_BRAND_NAMES` in `generate.py` (currently Sumotech,
  G-Weld, Grand Sumoweld, ABC, Yanase, Boysen) — in that exact order, with a
  "View All Brands" link to the full wall. To change which brands appear on
  the homepage, edit `HOMEPAGE_BRAND_NAMES`, not `BRANDS` itself.
- 15 category pages in `categories/` (`categories/welding-materials.html`,
  `categories/abrasives.html`, etc.) — each has a photo gallery carousel +
  item cards. The visible category count on `products.html` is derived from
  `len(CATEGORIES)`, not hardcoded, so adding a category updates it
  automatically. Item cards are
  intentionally minimal: picture + name only, no description text — the
  item's own product page (if it has one) or the category page itself
  carries the detail, so the card doesn't need to repeat it
- `items/mig-wire-er70s-6.html` — single-*product* detail page with real specs
  from the client (image gallery, quick facts, inquiry box, spec table, packaging
  table, related products). Built by hand in the "4. Generate a single-product
  page" section of `generate.py` — this level of detail needs real per-product
  data, so don't replicate the spec/packaging tables for other items without it.
- Per-item product pages in `items/`, one per item (gallery + quick description +
  inquiry box + related items, no spec/packaging tables — we don't have real
  specs beyond MIG Wire), built by the generic `product_page()` helper
  (section "4b" in `generate.py`). Categories done so far: **Gloves** (7
  items), **Packaging Materials** (16 items), **Abrasives** (14 items),
  **Tubing & Structural Steel** (10 items) — see each category's `items`
  list in `CATEGORIES` for the exact filenames (3rd
  tuple element — stored bare, e.g. `cut-off-wheel.html`, with the `items/`
  prefix added by `item_page_href()` at render time; don't put the folder in
  the tuple). To add another category: give its `items` entries a 3rd
  tuple element (the page filename), then loop `product_page()` over them
  like the existing blocks do. Ask before assuming which category/items
  should get this treatment next.

Nav is fixed to: **Who We Are, Products, Brands, Contact**.

**Products mega-menu**: "Products" in the header opens a flyout listing all
15 categories (flat, like Wyler's `/brands/` browse-categories menu); a
category opens a second flyout listing that category's items. Each item
links to its own product page if its `CATEGORIES` entry has one (see
Gloves), otherwise falls back to `categories/{category}.html#{item-slug}`
(`item_href(cat, item, depth)` in `generate.py`). Because the menu is inlined
into all 68 pages at two different depths, it's built once per depth and
cached by `mega_menu(depth)` — that replaced the old single
`MEGA_MENU_HTML` constant, which produced root-relative links that broke
once pages moved into subfolders. Built from `CATEGORIES`/`mega_menu()`
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
**Desktop open/close is instant, no fade** — `.mega-menu`/`.mega-sub` have
no `transition` (removed deliberately, 2026 — the client didn't want a fade
here). Don't re-add one; if animation is wanted on this menu again, ask
first. The mobile accordion's `max-height` transition is unrelated and
untouched (that's a slide/height animation, not a fade).
**Do not re-add `overflow-y:auto`/`max-height` to `.mega-menu` or
`.mega-sub`** — that was the bug that made the second-level flyout
invisible: setting `overflow-y` to non-`visible` also computes `overflow-x`
to `auto`, which clips the `.mega-sub` panel since it escapes to the right
via `left:100%`. If the category/item list ever gets too tall for the
viewport, fix it by scrolling an inner wrapper, not `.mega-menu`/`.mega-sub`
themselves.

**Item panels that would run off the bottom of the screen (2026)** — a
`.mega-sub` is anchored to the top of the row that opens it, so a category
low in a 15-row menu used to push its panel past the bottom of the viewport
(worst case Packaging Materials: 16 items, ~618px tall, opening from a row
at y≈621). Two layers fix this, and they work together:

1. `positionMegaSub()` in `site.js` nudges the panel up by exactly the
   amount it overflows — never higher than the top of the menu — so it
   stays next to the cursor rather than jumping to a fixed spot. Called
   from the hover-intent `openSub()` and the chevron click handler. It
   bails out when `.mega-sub` isn't `position:absolute`, which is how it
   no-ops on the mobile accordion, and it clears any inline `top` there so
   a stale desktop offset can't leak in.
2. `.mega-sub-scroll` (an inner wrapper inside `.mega-sub`, emitted by
   `mega_menu_html()`) carries `max-height:calc(100vh - 96px)` +
   `overflow-y:auto` as the backstop for viewports too short for step 1.
   **The scroll must stay on this inner wrapper** — that's the whole point
   of the warning above. The mobile block resets it to
   `max-height:none; overflow:visible` so the accordion animates its own
   height.

Verified at 1280&times;800 (all 15 panels fit, none clipped) and at
1280&times;600 (still none clipped; Abrasives and Packaging Materials
scroll internally). If you add a category or a long item list, re-check
both.

Item ids are slugified item names (`slugify()`), added to each
item-card in the category page loop — keep item names unique within a
category or ids collide.

**Homepage scroll-reveal animations (anime.js)** — homepage only, not any
other page, and not the Products mega-menu (that stays instant/CSS-only,
deliberately). anime.js is loaded via CDN (`ANIME_JS_TAG`, only passed into
`head()`'s `extra_head` param for `index_page` — don't add it to `head()`
globally, other pages don't need the extra request). Mark any element
`data-reveal` in the homepage HTML and `site.js` will fade + slide it up
(anime.js) when it scrolls into view (IntersectionObserver). Add
`data-reveal-delay="N"` (ms) to stagger items in a grid — set per-element
index in the Python loop that builds the grid (e.g. `i * 60`), not in CSS.
Respects `prefers-reduced-motion` and falls back to plain-visible if
anime.js fails to load. There's also a 2.5s safety-net timeout per element
in case the IntersectionObserver never fires, so content can never get
permanently stuck invisible — keep that when touching this code, it's a
deliberate defensive measure, not dead code. (Note for future debugging: if
you ever test this in an automated/headless browser tab and reveal
animations look stuck, check `document.visibilityState` first —
`requestAnimationFrame`, which anime.js's tweening depends on, is
suspended by the browser for backgrounded/hidden tabs. That's a testing-tool
artifact, not a site bug, and doesn't affect real visitors.)

## Design system

- **White + green only — no blue, no gold.** This was a deliberate rebrand
  (2026): the palette used to lean on navy/steel-blue tones (`--ink:#123A52`,
  `--steel:#2F6178`) plus a "gold" accent that was never actually gold in the
  CSS. Both are gone. Current tokens (`:root` in `styles.css`):
  `--ink:#16241D` (deep charcoal-green, replaces navy — used for header/hero/
  footer backgrounds and body text), `--steel:#3F5C48` / `--steel-light:#8FAE97`
  (muted green-grays, secondary text/borders), `--green:#1C7A41` /
  `--green-dark:#125C2F` (the accent — was misleadingly named `--amber`
  before the rebrand), `--plate:#F3F6F2` (near-white page background),
  `--paper:#FFFFFF`. **If you add a new color anywhere, it must be a shade of
  green, white, or a neutral gray — never blue/navy, never literal gold.**
  There are also several hardcoded green-gray hex values scattered through
  `styles.css` (e.g. `#C7D3C9`, `#46594B`) for text/borders on dark
  backgrounds where a CSS var didn't fit — keep new ones in that same
  green-gray family, don't reach for blue-gray defaults.
- Headings: Playfair Display (serif, echoes the client's card wordmark). Body:
  IBM Plex Sans. Labels/kickers/mono chips: IBM Plex Mono.
- Cards have a border + hover lift, ~12px radius (no box-shadow on plain
  cards — `.why-card`/`.mega-menu`/`.mega-sub` do use a subtle shadow, see
  their rules). Icon badges (`.icon-badge`) are circular gradient, alternating
  between the green accent and the steel tone (`.icon-badge.alt`).
- **Logo mark**: `LOGO_MARK` in `generate.py` (right above `header()`) — a
  rounded-square green-gradient badge with a serif "G" monogram, sits to the
  left of the "GLMI" wordmark in the header on every page. This is a
  code-built placeholder, not a professionally designed logo — swap the
  `<svg>` markup in that one constant for a real logo whenever the client
  has one; nothing else needs to change since every page pulls from
  `header()`. `.logo` is now a row (`.logo-mark` + `.logo-text`), not a
  column — don't collapse that back to just text.

## Hero slideshow

The homepage hero is a **banner slideshow on a white background**,
modeled on yalehardwareph.com's hero. It has been through two earlier
versions — a green `.hero-plate` category box, then a single cover photo in a
right-hand column — **don't reinstate either.** The hero section is white
(`--paper`), not the old dark-green block.

- **Slides are client-supplied banner artwork** with the headline and body
  copy **baked into the image**. That's why the hero has no HTML headline of
  its own — it would duplicate what's already drawn. Sources are
  `images/Hero Photos/1–5.png` (1920&times;1080, ~2.3&nbsp;MB each, kept as
  untouched originals); the page loads `images/hero/hero-1…5.jpg`
  (1600&times;900, ~270&nbsp;KB each — 11.3&nbsp;MB down to 1.3&nbsp;MB).
  **If the client sends new banners, redo that compress step** — this is the
  homepage hero and most visitors are on mobile data. Slide 1 is
  `fetchpriority="high"`; slides 2–5 are `loading="lazy"`, so first paint
  pulls only ~270&nbsp;KB.
- **Because the copy is baked into pixels, search engines and screen readers
  can't read any of it.** Two things compensate, and both must be kept in
  sync with the artwork: the per-slide `alt` text in `HERO_SLIDES`
  (`generate.py`) restates each banner's message in words, and the section
  carries a visually-hidden `<h1>` (`.sr-only` in `styles.css`) so the
  homepage still has a real heading. If you edit the banners, edit these too.
- **Sizing**: the slideshow sits inside a `.wrap` (max-width 1180px), *not*
  full bleed, so white shows around it — matching Yale's proportions. It was
  briefly full-width; don't put it back.
- **Markup reuses the existing `.carousel` structure and the `site.js`
  carousel controller** (arrows, dots, touch swipe) rather than duplicating
  it, with a `.hero-carousel` class carrying the hero-specific styling
  (16:9 slides, white ground, overlaid dots). Two behaviors are **opt-in per
  carousel via attributes**, so the category galleries — which set neither —
  behave exactly as they always have:
  - `data-autoplay="6000"` — advances every 6s. Pauses on hover, on keyboard
    focus, and when the tab is backgrounded; restarts after any manual
    navigation; skipped entirely under `prefers-reduced-motion`.
  - `data-loop` — **seamless wrap-around.** Without it the track visibly
    rewinds from the last slide all the way back to the first. With it,
    `site.js` clones the first slide onto the end and the last onto the
    front (both `aria-hidden`, and excluded from the dot count), so stepping
    past either edge keeps moving in the *same* direction into a clone, then
    silently snaps to the real slide once the animation ends. Snapping is
    driven by `transitionend` **plus a 600ms `setTimeout` fallback** — a
    backgrounded tab suspends CSS transitions, so a missed `transitionend`
    would strand the track on a clone and make the next move rewind. That
    timer is deliberate defensive code, same spirit as the reveal-animation
    safety net; don't delete it.
- **Arrows are hidden below 860px** — at phone widths they sat directly on
  top of the baked-in headline. Swipe and the dots still work there.
- **Known limitation:** because the copy is part of the image, it does not
  reflow, so it renders small on phones. The real fix is either
  mobile-specific banner crops or moving the text out of the artwork into
  HTML over a plain photo — worth raising with the client. Slide 4 also
  hardcodes "Over 23 Years", which will go stale (everything else derives
  from `ESTABLISHED_YEAR`).
- The earlier single cover photo (`images/cover-photo.jpg`, trimmed from
  `images/Cover Photo.png`) is no longer referenced by any page. Kept in the
  repo in case it's wanted elsewhere; safe to delete otherwise.

## Images — mostly placeholders

Every product/category/brand image is a styled SVG placeholder tile labeled
"SAMPLE IMAGE" (built by the `thumb()` / `carousel()` helpers in
`generate.py`) — not real photos, to avoid using unlicensed web images on a
client's live business site. Hover-zoom and carousel/gallery behavior are
already wired up and will work the same once real `<img>` tags replace the
placeholders.

**Brand logos: 10 of 19 are real** (2026) — Makita, Bosch, Phelps Dodge,
G-Weld, Mitutoyo, Sumotech, ABC, Yanase, Boysen, Davies, all in
`images/Brands/`. The remaining 9 still render placeholder tiles: FAG, IKO,
KOYO, Hitachi, AEG, Columbia, Duraflex, Philflex, and **Grand Sumoweld**.
Sumoweld matters more than the rest — it's one of the six brands featured on
the homepage and is named in the "Trusted Brands" copy, so it's the only
placeholder sitting among five real logos there.

Note the logos are a mix of wide wordmarks (Yanase 550&times;91) and
full-bleed coloured squares with the name inside (ABC, Davies, Phelps
Dodge). `.brand-logo` uses a generous `max-height` + `object-fit:contain`
so both shapes stay legible and undistorted — don't drop the cap back to a
small value, it renders the square logos unreadable.

A category with a real photo (`photo=(label, path)` on its `CATEGORIES`
entry — currently Gloves and Caster Wheels) shows that photo **everywhere
the category is represented as a thumbnail**: its own category-page gallery
(first slide), its card on `products.html`, and its card on the homepage
group-teaser section if that category happens to be one of the 7 shown
there. That's `thumb(..., img=c['photo'][1] if c.get('photo') else None)` —
follow that pattern for the next category that gets a real photo, don't
just wire it into the one gallery.

## Business facts (real, from the client)

- Brand name: **GLMI** (`COMPANY` in `generate.py`) — rebranded (2026) from
  "Grand Lexther Marketing, Inc.". The old name should not appear anywhere
  on the site, including the footer copyright line — that's a deliberate
  choice, not an oversight, so don't "restore" the full legal name there.
- Established: 2003 (`ESTABLISHED_YEAR` in `generate.py` — "years in business"
  on `who-we-are.html` and the homepage stats band is derived from this
  automatically each time the site is regenerated, not hardcoded)
- Tagline: "Wholesaler and Retailer of Quality Industrial and Construction
  Materials" — **no "Importer"**. The client dropped that line of business;
  don't reintroduce "importer"/"Importer" anywhere (tagline, hero eyebrow,
  trust-pillar copy, meta descriptions).
- Address: 197 T. Claudio St., Brgy. Sta. Lucia, San Juan City, Philippines
  (real, unchanged)
- **Phone (mobile/Viber + telephone) and email are placeholders**, not real
  data: `PHONE`/`EMAIL` in `generate.py` are empty strings (so `tel:`/
  `mailto:` links degrade gracefully — dialer/mail app opens with nothing
  pre-filled, instead of linking to fake info), and `PHONE_DISPLAY` /
  `LANDLINE_DISPLAY` / `EMAIL_DISPLAY` hold the bracketed placeholder text
  shown in the contact section (`[Mobile/Viber number]` etc.). The old real
  number and the grandlexther2012@gmail.com inbox were intentionally
  removed as part of the rebrand — waiting on the client for new
  GLMI-branded contact details to fill back in.
- **Service is the primary USP** (client's own framing, 2026): GLMI's
  differentiator is responsive, dependable, customer-focused service, not
  just materials — the hero copy leads with this now ("Top-quality
  materials. Service you can trust."). Keep future homepage/marketing copy
  tilted toward service, not just product breadth/pricing, unless the
  client says otherwise. Content emphasis: top-quality materials/equipment,
  trusted industrial supplier, trusted brands, exceptional service,
  best/competitive prices — this is woven into hero copy and the
  "Why GLMI" section.

## Request a Quote (client-side cart + EmailJS)

Product pages no longer have "Call to Inquire"/"Email Inquiry" — they have
a single **Add to Quote** button. This is a real feature, not decoration:

- **Cart** lives in `localStorage` (`glmiQuoteCart`, key constant
  `QUOTE_CART_KEY` in `site.js`), shape `[{url, name, qty}]`. Shared
  sitewide — every product page can add to it, the nav badge
  (`#quoteCount`) reads it on every page load, `request-quote.html` renders
  and edits it. No backend, no cookies, per-browser only (same limitation
  as any localStorage cart — clearing browser data empties it).
  **`url` is always stored site-root-relative** (`items/cut-off-wheel.html`),
  never relative to the page that added it — `request-quote.html` sits at the
  root and drops these straight into hrefs, so a `"../"`-prefixed value would
  break there. The `data-url` on each Add to Quote button emits the
  root-relative form directly (`{ITEM_DIR}/{slug}`). `normalizeCartUrl()` in
  `site.js` rewrites pre-subfolder carts (bare `cut-off-wheel.html`) on read
  so carts saved before the 2026 folder move don't 404; safe to delete once
  no visitor could still be holding one.
- **"Add to Quote"** buttons (`.add-to-quote`, in `product_page()` and the
  hardcoded MIG Wire page) read the page's own quantity stepper, merge into
  the cart by `url`, give a 1.6s "Added ✓" confirmation. They never
  navigate — always `type="button"`.
- **`request-quote.html`** is a static shell (`generate.py` section "7")
  with empty containers (`#quoteItems`, `#quoteEmptyState`,
  `#quoteSuccessState`, `#quoteForm`) — Python can't know a visitor's cart
  contents at build time, so all rendering (item rows, qty +/-, remove,
  empty state) happens client-side in `site.js`, gated on `#quoteItems`
  existing (so this code is a no-op on every other page). There are three
  mutually-exclusive views toggled by hiding/showing these containers:
  empty cart, the form, and post-submit success. **On a successful send,
  show `#quoteSuccessState` directly — do not call `renderQuoteItems()`.**
  That function decides empty-vs-form purely from current cart contents,
  and the cart is intentionally cleared right after a successful send, so
  calling it there would show the generic "cart is empty" message instead
  of a thank-you — that exact bug happened once already, don't reintroduce
  it.
- **Sending the email is EmailJS** (client-side, no backend) — chosen over
  a plain `mailto:` link so it works reliably on mobile/webmail users with
  no configured mail app, not just desktop. **Configured and live** (2026)
  — real credentials are in constants at the top of `site.js`:
  `QUOTE_EMAILJS_PUBLIC_KEY`, `QUOTE_EMAILJS_SERVICE_ID`
  (`service_3d2q6dy`), `QUOTE_EMAILJS_TEMPLATE_ID` (`template_e31ibb4`),
  `QUOTE_EMAIL_TO` (`jrtchan18@gmail.com`). Verified working end-to-end
  (real test send returned `status: 200`). EmailJS free tier caps at
  ~200 emails/month — if the client outgrows that, they'll need to upgrade
  their EmailJS plan (dashboard.emailjs.com), nothing in this codebase
  needs to change. The submit handler still checks for a `'YOUR_'`
  placeholder prefix and shows a friendly "not set up yet, call or email us
  directly" message instead of silently failing — **don't remove that
  check**, it's the fallback if credentials are ever blanked out again
  (e.g. rotated for a new EmailJS account).
  The EmailJS template must accept these params (sent from `site.js`):
  `to_email`, `from_name`, `company`, `phone`, `reply_to`, `notes`,
  `items_list` (a newline-joined "- Name (xQty)" list).
  `EMAILJS_TAG` in `generate.py` loads the EmailJS CDN script, passed via
  `head()`'s `extra_head` only for `request-quote.html` — same pattern as
  `ANIME_JS_TAG` for the homepage, don't load it globally.
- The homepage hero's "Request a Quote" button now links to
  `request-quote.html` (used to scroll to `#contact`) — that's intentional,
  don't revert it; the general contact section/CTAs (Call Now, Email Us,
  the header call button, `mini_cta()`) are untouched and still use
  `tel:`/`mailto:` since those aren't tied to a specific item list.

## Still pending / open TODOs

- Caster Wheels items list (Swivel/Rigid/Heavy-Duty/Light-Duty Casters) is
  a generic placeholder — ask the client for their actual caster wheel
  product list, same as every other category's real item list
- Real product photos (client is sourcing these)
- Real product/item list with specs, beyond what's in `generate.py`'s
  `CATEGORIES` list
- Brand logos for the remaining 9 placeholder tiles — **Grand Sumoweld
  first**, since it's featured on the homepage alongside five real logos
- Business hours (still a placeholder `[Mon–Sat, 8:00 AM – 5:00 PM]`)
- Certifications, warehouse location, delivery coverage area — not yet on
  `who-we-are.html`, ask the client if there's more to add beyond the
  established-2003 story
- ~~Stats band "Clients Served" number~~ — moot: the homepage stats band
  ("N Product Categories / 15+ Brands Carried / N+ Years in Business /
  [X] Clients Served") was **removed at the client's request (2026)**, along
  with its `.stats-band`/`.stats-grid` CSS. Don't re-add it. The separate
  `.stat-plate` on `who-we-are.html` stays, and its category count now
  derives from `len(CATEGORIES)` rather than a hardcoded 14.
- Gloves, Packaging Materials, Abrasives, and Tubing & Structural Steel are
  the only categories with per-item pages so far (description + placeholder
  photos, via `product_page()` — see Site structure above). Deciding which
  other categories/items should get the same treatment next, and whether
  real photos are available yet for these four
- Real phone number(s) and a new GLMI-branded email inbox — see "Business
  facts" above, these are currently placeholder text sitewide
- Confirm with the client whether "GLMI" is meant to stand alone going
  forward, or whether a full legal name should still appear somewhere (e.g.
  a required-by-law line in the footer) once that's finalized

Hosting: live on GitHub Pages at https://jrtchan18.github.io/glmi-website/,
served from the `main` branch of github.com/jrtchan18/glmi-website (repo was
renamed from `grand-lexther-website` as part of the GLMI rebrand). **Changes
only go live once committed AND pushed** — regenerating locally isn't
enough.

## Reference sites the client likes

- https://yalehardwareph.com/ and https://machinebanks.com/ — both PH
  industrial/hardware suppliers. The trust-building homepage flow (hero →
  brands → stats → about → contact) is modeled loosely on Machinebanks. Their
  sprawling mega-menus and cart/account systems were intentionally *not*
  copied — this site stays simpler since it's inquiry-based, not e-commerce.
