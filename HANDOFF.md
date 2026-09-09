# GLMI Website — Handoff

Last updated: 2026-09-09

**Live:** https://jrtchan18.github.io/glmi-website/
**Repo:** github.com/jrtchan18/glmi-website (branch `main`, public)

> Read `CLAUDE.md` alongside this. That file is the technical reference — how
> the generator works, and crucially *which decisions were deliberate* so they
> don't get "fixed" back. This file is the state of play: what's done, what's
> blocked, what was tried and abandoned, and what I'd do next.

---

## Goal

A static catalog site for **GLMI**, a wholesaler/retailer of industrial and
construction materials in San Juan City, Metro Manila, established 2003.

It is **not e-commerce**. There are no prices anywhere, deliberately — the
client wants buyers to make contact rather than self-serve. The site's job is
to make GLMI look established and legitimate, let a buyer find what they
stock, and convert that into a phone call, a Viber message, or a quote
request.

Reference sites the client likes: yalehardwareph.com (hero slideshow,
proportions) and machinebanks.com (homepage flow). Their mega-menus and
cart/account systems were deliberately *not* copied — this site stays
simpler because it's inquiry-based.

---

## Current state

| | |
|---|---|
| Pages generated | **70** — 5 root, 15 category, 50 item |
| Catalog | **15 categories, 80 items** (50 have their own detail page) |
| Product photography | **2 of 15 categories** — Welding Materials, Gloves |
| Brand logos | **11 of 19 real** |
| Quote system | **Working end-to-end**, EmailJS live |
| Contact details | **Placeholder** — blocked on client |
| SEO | **Nothing exists yet** |
| Custom domain | **Not started** |

### What works
- Full catalog with a two-level Products mega-menu, breadcrumbs, category
  pages and per-item detail pages.
- **Request a Quote**: a `localStorage` cart, per-item option pickers
  (currently diameter × packaging on MIG wire), and EmailJS submission.
  Verified with a real send. Quote requests go to `jrtchan18@gmail.com` —
  the client's own choice, not an oversight.
- Homepage hero slideshow (5 client banners, autoplay, seamless loop, swipe)
  and a warehouse photo carousel in the Who We Are teaser.
- A drop-in photo pipeline: name files after the item slug, put them in the
  category's folder, rebuild. No code changes needed.

### What's placeholder
- Phone, Viber, telephone, email and business hours are all bracketed
  placeholder text. `tel:`/`mailto:` deliberately point nowhere rather than
  at fake data.
- 13 of 15 categories show "SAMPLE IMAGE" tiles instead of photos.
- 30 of 80 items have no detail page and link to a category anchor.
- Caster Wheels' item list is invented, not the client's real range.

---

## Files touched

Everything is generated from three source files. **The 70 `.html` files are
build output — never edit them.**

| File | Role |
|---|---|
| `generate.py` | Source of truth. All content, structure, page building. |
| `styles.css` | All styling. Inlined into every page at build time. |
| `site.js` | Nav, carousels, gallery swap, quote cart. Also inlined. |
| `CLAUDE.md` | Technical reference and record of deliberate decisions. |
| `glmi-catalog.csv` | Import template for the client's item list. |
| `images/` | See below — sources and generated copies are both committed. |

### How `images/` is organised
- `images/Hero Photos/`, `images/Products/<Category>/`, `images/Home*.jpg` —
  **originals** as supplied. Large. Never referenced by any page.
- `images/hero/`, `images/items/<category>/`, `images/about/` — **generated**
  web-sized copies. These are what the pages actually load.
- `images/Brands/` — logos, used directly.

Roughly 38 MB of originals against 4 MB of generated files. Keep both: the
originals are the only copy of the source material, and re-optimising later
needs them.

---

## What changed in this work stream

21 commits, `b7c6cd1` through `945d538`.

**Structure**
- Moved 63 pages out of the repo root into `categories/` and `items/`; root
  went from 68 HTML files to 5. Every generated link became depth-aware.
- Fixed mega-menu item panels being clipped at the bottom of the viewport.
- Made switching between mega-menu categories instant (two panels used to
  overlap for 250ms).

**Homepage**
- Replaced the category plate with a hero banner slideshow: autoplay,
  seamless wrap-around, touch swipe, Yale-style contained width.
- Removed the stats band at the client's request.
- Replaced the Established/San Juan stat plate with a warehouse photo
  carousel.
- Fixed a duplicated `<title>` ("GLMI | Industrial Supplies Trading | GLMI").

**Content**
- Added real Gloves photography and synced the glove range to it —
  removed 3 types the client doesn't stock, added 5 they do.
- Rebuilt the MIG wire page from supplier data: real photos, equivalent
  standards (AWS/GB/DIN/EN), spool + drum packaging as equals, and
  diameter/packaging pickers feeding the quote cart.
- Wired in 7 brand logos; reordered the brand wall to lead with house brands.
- Rewrote the Who We Are story with the client's own copy.

**Design**
- Typography moved behind CSS tokens and iterated through five pairings
  (see below). Now Montserrat 800 + DM Sans + IBM Plex Mono.
- Removed the "Wholesaler · Retailer" line under the header wordmark.
- Fixed product pages not stacking on mobile — they were two ~150px columns
  on a phone, across all 49 product pages.

---

## What was tried and didn't stick

Worth knowing so nobody re-treads it.

**Typography — five pairings before landing.** Playfair Display + IBM Plex
Sans (original, too formal) → Fraunces + Nunito Sans → Archivo Black + DM
Sans → Montserrat 900 → Outfit 900 → **Montserrat 800 + DM Sans**. The
lesson worth keeping: `--font-display-weight` is family-dependent and fails
*silently*. Archivo Black needs 400 (it ships one weight and fakes bold if
asked for more); Montserrat needs 800–900. Wrong value looks subtly off
everywhere with no error.

**Hero, three versions.** Green category plate → single cover photo in a
right column → banner slideshow. It was also briefly full-bleed before being
constrained to the content width. `images/cover-photo.jpg` is left over from
version two and is no longer referenced by anything.

**Stainless steel on the MIG page.** Added, then removed a message later at
the client's request.

**Mobile overrides in the wrong place.** Rules added to the main mobile media
query silently did nothing, because that block sits *above* the rules it
needed to beat and media queries add no specificity. It failed *partially* —
`flex-wrap` applied while `min-width` didn't — which looked like success.
Hence the "Late mobile overrides" block at the end of `styles.css`.

**Carousel loop on `transitionend` alone.** Backgrounding a tab suspends CSS
transitions, so the event never fires and the track gets stranded on a clone.
Needed a 600 ms timeout fallback.

**Cart keyed on URL alone.** Broke as soon as one product had options — two
specs collapsed into one line. Now keyed on URL + options.

**A drum-label crop for the Grand Sumoweld logo.** Reasonable stopgap,
superseded when the client supplied real artwork.

**My own mistake, recorded because it cost real data:** commit `945d538`
says it only corrects doc counts, but it also **deleted
`images/Home.jpg` and `images/Home 2.JPG`**. I used `git add -A`, which
staged a working-tree deletion I never inspected, and the commit message
said nothing about it. The live site was unaffected — pages load the
optimised copies in `images/about/` — and the originals have been restored
from history. **Lesson: check `git status` before `git add -A`, and read the
staged list before committing.**

---

## Next steps

In dependency order. The first two are cheap and block the rest.

1. **Get real contact details from the client.** Phone, Viber, a
   GLMI-branded email inbox, confirmed business hours. Nothing else on this
   list pays off while a buyer can't reach GLMI.
2. **Buy a domain and point it at GitHub Pages.** About an hour plus a
   `CNAME` file. Do this *before* the SEO work — sitemaps, canonical tags
   and `og:url` all bake in absolute URLs.
3. **Build the SEO layer in one session.** `sitemap.xml`, `robots.txt`,
   canonical tags, Open Graph/Twitter cards, and `LocalBusiness` JSON-LD.
   It's generator code, so it applies to all 70 pages at once and every page
   added later inherits it.
4. **Claim the Google Business Profile.** Needs the phone number and takes
   1–2 weeks to verify, so start it the day contact details arrive.
5. **Chase photos and real item lists** for the remaining 13 categories, and
   the 30 items with no detail page. Slowest-moving work; start early even
   though it finishes last. `glmi-catalog.csv` is the template to send.
6. **Build site search.** 80 items across 15 categories with no search box.
   Everything is known at build time, so it's a generated JSON index plus a
   client-side filter — no backend.

---

## What I think is necessary

Ranked by how much they actually matter, not by effort.

**1. Contact details, then a domain. Everything else is secondary.**
A supplier site that can't be phoned reads as abandoned, and
`jrtchan18.github.io` is a personal handle in a business's address bar.
These two are cheap and they gate everything downstream.

**2. The SEO layer is the largest gap on the site.** It's easy to
under-rate because the site *looks* finished. But there is no sitemap, no
canonical tags, no structured data, and no Open Graph. Two consequences:
Google can barely index it, and — more immediately — pasting any product
link into Viber or Messenger unfurls as a bare grey URL. In this market
chat-app sharing *is* a distribution channel, so that's a daily cost, not a
someday-cost.

**3. Photography moves slowest, so start it now.** The pipeline is built and
needs no code. It's purely a content-collection problem, which means it will
take longer than anything technical. Phone photos of real stock on a plain
background are genuinely fine — better than waiting indefinitely for a
photographer, and more credible than stock imagery.

**4. Get the hero copy out of the images.** The banners have their headline
text baked into the pixels. It can't reflow, so it renders small and hard to
read on phones — where most of this audience is — and search engines can't
read a word of it. `alt` text and a hidden `<h1>` compensate for machines but
not for the person squinting at a phone. Moving that copy into HTML over a
plain photo fixes both at once.

**5. Consider whether the quote inbox should stay personal.** It currently
goes to the owner's personal Gmail, which the client chose knowingly. It
works. But if a salesman ever handles follow-up, requests need to land
somewhere they can see, or the 24-hour promise quietly breaks.

**Not worth doing:** real checkout, live inventory, customer accounts, a
blog nobody will maintain, or a chatbot. The quote cart is the right model
for negotiated industrial pricing, and a dormant blog signals a dormant
business.
