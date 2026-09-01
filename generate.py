import os
import re
import datetime

OUT = os.path.dirname(os.path.abspath(__file__))

# ---- Output layout ----
# Root holds only the 5 top-level pages (index, products, brands, who-we-are,
# request-quote); the 15 category pages and 48 per-item product pages live in
# subfolders so the repo root stays readable.
#
# Because pages now sit at different depths, EVERY generated link has to be
# depth-aware. The convention: each page-building call passes a `depth` prefix
# ("" for root pages, "../" for anything in a subfolder) into header(),
# footer(), thumb(), carousel(), and the href helpers below. If you add a new
# page, pass the right depth — a missing one produces links that work from
# root and 404 from a subfolder, which is easy to miss when spot-checking.
CAT_DIR = "categories"
ITEM_DIR = "items"

for _d in (CAT_DIR, ITEM_DIR):
    os.makedirs(os.path.join(OUT, _d), exist_ok=True)

def cat_href(cat_slug, depth=""):
    """Link to a category page from a page at `depth`."""
    return f"{depth}{CAT_DIR}/{cat_slug}.html"

def item_page_href(filename, depth=""):
    """Link to a per-item product page from a page at `depth`."""
    return f"{depth}{ITEM_DIR}/{filename}"

def asset(path, depth=""):
    """Link to a static asset (images/...) from a page at `depth`."""
    return f"{depth}{path}"

# ---- Product photos ----
# Source photos live in the folder named by a category's `photo_dir`, named
# after the item's page slug:  cotton-gloves.png, cotton-gloves-2.png, ...
# The first (unsuffixed) file is the item's main/thumbnail shot; the numbered
# ones fill out its gallery.
#
# Client photos arrive straight off a phone or a supplier (1250x1250, ~1 MB
# each). The build writes web-sized JPEGs into images/items/<category>/ and
# the pages reference those — a category page showing nine items would
# otherwise pull ~10 MB. Recompression is skipped when the output is already
# newer than the source, so regenerating is cheap.
#
# To add photos for a new category: create the folder, name the files after
# the item slugs, and add `photo_dir=` to that CATEGORIES entry. No other
# code changes — items with no matching file keep their SVG placeholder.
PHOTO_MAX_PX = 1000
PHOTO_QUALITY = 82
IMG_EXTS = (".png", ".jpg", ".jpeg", ".webp")
WEB_PHOTO_DIR = "images/items"

try:
    from PIL import Image as _PILImage
except ImportError:
    _PILImage = None

def optimize_photo(src_rel, out_dir_rel):
    """Web-sized JPEG copy of a source photo; returns a path relative to OUT.
    Falls back to the original file if Pillow isn't installed, so the build
    still works (just heavier) on a machine without it."""
    if _PILImage is None:
        return src_rel
    src = os.path.join(OUT, src_rel)
    stem = os.path.splitext(os.path.basename(src_rel))[0]
    dst_rel = f"{out_dir_rel}/{stem}.jpg"
    dst = os.path.join(OUT, dst_rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if (not os.path.exists(dst)) or os.path.getmtime(dst) < os.path.getmtime(src):
        im = _PILImage.open(src).convert("RGB")
        w, h = im.size
        if max(w, h) > PHOTO_MAX_PX:
            s = PHOTO_MAX_PX / max(w, h)
            im = im.resize((round(w * s), round(h * s)), _PILImage.LANCZOS)
        im.save(dst, "JPEG", quality=PHOTO_QUALITY, optimize=True, progressive=True)
    return dst_rel

_photo_cache = {}

def item_photos(cat, page_slug):
    """Every photo for one item, ordered: `slug.ext` first, then `slug-2.ext`,
    `slug-3.ext`, ... Returns [] when the category has no photo_dir or nothing
    matches, in which case the page keeps its SVG placeholders.

    Cached: the same item is looked up from its own page, its category page,
    the category carousel, and every sibling's "related items" grid."""
    key = (cat.get("slug"), page_slug)
    if key in _photo_cache:
        return _photo_cache[key]
    _photo_cache[key] = result = _item_photos_uncached(cat, page_slug)
    return result

def _first_photo(cat, page_slug):
    """An item's main photo, or None so thumb() falls back to a placeholder."""
    photos = item_photos(cat, page_slug)
    return photos[0] if photos else None

def _item_photos_uncached(cat, page_slug):
    src_dir_rel = cat.get("photo_dir")
    if not src_dir_rel:
        return []
    src_dir = os.path.join(OUT, src_dir_rel)
    if not os.path.isdir(src_dir):
        return []
    base = os.path.splitext(page_slug)[0]          # cut-off-wheel.html -> cut-off-wheel
    numbered = []
    for fn in os.listdir(src_dir):
        stem, ext = os.path.splitext(fn)
        if ext.lower() not in IMG_EXTS:
            continue
        if stem == base:
            numbered.append((0, fn))
        else:
            # Exact `base-<digits>` only, so `anti-cut-gloves` never swallows
            # a future `anti-cut-gloves-heavy`.
            m = re.fullmatch(re.escape(base) + r"-(\d+)", stem)
            if m:
                numbered.append((int(m.group(1)), fn))
    out_dir_rel = f"{WEB_PHOTO_DIR}/{cat['slug']}"
    return [optimize_photo(f"{src_dir_rel}/{fn}", out_dir_rel) for _, fn in sorted(numbered)]

COMPANY = "GLMI"
# Contact details are placeholders — real numbers/email not finalized yet.
# PHONE/EMAIL (used in tel:/mailto: hrefs) are intentionally blank so the
# Call/Email buttons degrade gracefully (open the dialer/mail app with
# nothing pre-filled) instead of linking to fake contact info.
PHONE = ""
PHONE_DISPLAY = "[Mobile/Viber number]"
LANDLINE_DISPLAY = "[Telephone number]"
EMAIL = ""
EMAIL_DISPLAY = "[Email address]"
ADDRESS = "197 T. Claudio St., Brgy. Sta. Lucia, San Juan City, Philippines"
TAGLINE = "Wholesaler and Retailer of Quality Industrial and Construction Materials"
ESTABLISHED_YEAR = 2003
YEARS_IN_BUSINESS = datetime.date.today().year - ESTABLISHED_YEAR

# ---- Icons (reused simple line-icon set) ----
ICONS = {
  "welding": '<path d="M12 2 3 7v10l9 5 9-5V7z"/><path d="M3 7l9 5 9-5"/>',
  "abrasive": '<circle cx="12" cy="12" r="9"/><path d="M12 3v18M3 12h18"/>',
  "cutting": '<path d="M12 2v6m0 0-3 3m3-3 3 3M5 22l5-9m9 9-5-9M9 13h6"/>',
  "drill": '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
  "pneumatic": '<rect x="4" y="9" width="16" height="6" rx="1"/><path d="M8 9V7a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>',
  "hydraulic": '<path d="M4 4c4 0 4 4 8 4s4-4 8-4M4 20c4 0 4-4 8-4s4 4 8 4"/>',
  "wire": '<path d="M4 12c2-4 4 4 6 0s4 4 6 0 4 4 4 4"/>',
  "construction": '<path d="M3 21V8l9-5 9 5v13M9 21v-6h6v6"/>',
  "sheet": '<rect x="3" y="3" width="18" height="18" rx="1"/><path d="M3 9h18M9 21V9"/>',
  "tubing": '<path d="M4 21V3M4 3h4v6H4M4 12h4v9M20 21V3M20 3h-4v6h4M20 12h-4v9"/>',
  "bearing": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="3.2"/>',
  "glove": '<path d="M7 22V2m0 0h6a4 4 0 0 1 0 8H7m10 12v-8m0 0h-4a4 4 0 0 0 0 8h4"/>',
  "safety": '<circle cx="7" cy="12" r="3.2"/><circle cx="17" cy="12" r="3.2"/><path d="M10.2 12h3.6M4 12c0-1 .5-2 1.5-2M20 12c0-1-.5-2-1.5-2"/>',
  "packaging": '<rect x="3" y="7" width="18" height="13" rx="1"/><path d="M3 12h18M9 7V5a3 3 0 0 1 6 0v2"/>',
  "tag": '<path d="M20.59 13.41 11 3.83A2 2 0 0 0 9.59 3.24L4 3a1 1 0 0 0-1 1l.24 5.59a2 2 0 0 0 .59 1.41l9.58 9.58a2 2 0 0 0 2.83 0l4.35-4.35a2 2 0 0 0 0-2.82z"/><circle cx="8" cy="8.5" r="1.2"/>',
  "brand": '<path d="M12 2 4 6v6c0 5 3.5 8.5 8 10 4.5-1.5 8-5 8-10V6z"/><path d="m9.5 12 1.8 1.8L15 10"/>',
  "quote": '<path d="M9 2h6a2 2 0 0 1 2 2v1h1a2 2 0 0 1 2 2v13a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h1V4a2 2 0 0 1 2-2z"/><path d="M9 12l2 2 4-4"/>',
  "remove": '<path d="M18 6 6 18M6 6l12 12"/>',
}

def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

def icon(name, size=30, cls=""):
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" class="{cls}">{ICONS[name]}</svg>'

def thumb(label, icon_key, size=32, img=None, logo=False, depth=""):
    """Photo thumbnail with hover-zoom built in via CSS. Pass img (a file path) to use a real photo
    instead of the SVG placeholder; set logo=True for brand logos (white backing, contain-fit).
    `depth` prefixes the image path for pages in subfolders (see "Output layout" up top)."""
    if img:
        cls = "thumb logo-thumb" if logo else "thumb"
        return f"""<div class="{cls}">
          <img class="thumb-photo" src="{asset(img, depth)}" alt="{label}" loading="lazy">
        </div>"""
    return f"""<div class="thumb">
          <span class="sample-tag">SAMPLE IMAGE</span>
          <div class="thumb-visual">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="width:{size}px;height:{size}px;">{ICONS[icon_key]}</svg>
            <span class="thumb-label">{label}</span>
          </div>
        </div>"""

def thumb_visual(label, icon_key, size=32, show_label=True):
    """Bare inner visual (no outer .thumb aspect-ratio box) — for use inside custom-sized containers like gallery thumbnails."""
    label_html = f'<span class="thumb-label">{label}</span>' if show_label else ""
    return f"""<div class="thumb-visual">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="width:{size}px;height:{size}px;">{ICONS[icon_key]}</svg>
            {label_html}
          </div>"""

def carousel(slides, depth="", contain=False):
    """slides: list of (label, icon_key) or (label, icon_key, img). Renders a prev/next + dots carousel.
    Pass img (a file path) on a slide to show a real photo instead of the SVG placeholder.
    `depth` prefixes image paths for pages in subfolders (see "Output layout" up top).
    `contain` letterboxes photos on white instead of cropping them to fill — use it
    when the slides are square product shots rather than wide scene photos."""
    def render_slide(slide):
        lbl, ic = slide[0], slide[1]
        img = slide[2] if len(slide) > 2 else None
        if img:
            return f"""<div class="carousel-slide has-photo">
          <img class="cs-photo" src="{asset(img, depth)}" alt="{lbl}" loading="lazy">
        </div>"""
        return f"""<div class="carousel-slide">
          <span class="sample-tag">SAMPLE IMAGE</span>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">{ICONS[ic]}</svg>
          <span class="cs-label">{lbl}</span>
        </div>"""
    slide_html = "\n        ".join(render_slide(s) for s in slides)
    return f"""<div class="gallery-wrap">
      <div class="carousel{' photo-contain' if contain else ''}">
        <div class="carousel-track">
        {slide_html}
        </div>
        <button class="carousel-btn prev" type="button" aria-label="Previous photo">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>
        </button>
        <button class="carousel-btn next" type="button" aria-label="Next photo">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l6-6-6-6"/></svg>
        </button>
        <div class="carousel-dots"></div>
      </div>
    </div>"""

# ---- Category data ----
# slug, title, section code+name, icon key, short description, list of (item name, item desc)
CATEGORIES = [
  dict(slug="welding-materials", title="Welding Materials", sec="SEC.01", group="Welding & Metal Work", icon="welding",
       desc="MIG wires for welding and fabrication work, available in standard spool sizes and wire diameters.",
       items=[("MIG Wires", "Various wire diameters and spool sizes for MIG welding applications.", "mig-wire-er70s-6.html")]),
  dict(slug="abrasives", title="Abrasives", sec="SEC.02", group="Welding & Metal Work", icon="abrasive",
       desc="A full abrasives line for grinding, sanding, and surface finishing on metal and other materials.",
       items=[
         ("Cut-off Wheel", "Cut-off wheels for fast, precise cutting of metal and other materials.", "cut-off-wheel.html"),
         ("Depressed Center Wheel", "Depressed center grinding wheels for heavy-duty material removal on angle grinders.", "depressed-center-wheel.html"),
         ("Grinding Wheel", "Grinding wheels for shaping, deburring, and heavy material removal.", "grinding-wheel.html"),
         ("Abrasive Mop Wheel", "Abrasive mop wheels for blending, deburring, and finishing metal surfaces.", "abrasive-mop-wheel.html"),
         ("Radial Wheel (Flat/Stand)", "Radial wheels, flat and stand types, for deburring and surface conditioning.", "radial-wheel-flat-stand.html"),
         ("Flap Disc", "Flap discs for blending and finishing metal surfaces.", "flap-disc.html"),
         ("Non-Woven Wheel", "Non-woven abrasive wheels for light deburring, blending, and surface finishing.", "non-woven-wheel.html"),
         ("Sanding Belt", "Sanding belts for belt sanders, in various grit options.", "sanding-belt.html"),
         ("Sand Paper", "Sanding sheets in assorted grit levels for surface prep and finishing.", "sand-paper.html"),
         ("Emery Cloth", "Emery cloth for hand sanding, deburring, and surface prep.", "emery-cloth.html"),
         ("Honing Stone", "Honing stones for sharpening and fine surface finishing.", "honing-stone.html"),
         ("Mounted Stone", "Mounted stones for precision grinding and deburring in tight spaces.", "mounted-stone.html"),
         ("Buffing Pad", "Buffing pads for polishing and finishing metal and other surfaces.", "buffing-pad.html"),
         ("Buffing Compound/Paste", "Buffing compound and paste for polishing and achieving a fine surface finish.", "buffing-compound-paste.html"),
       ]),
  dict(slug="cutting-tools", title="Cutting Tools / Drills", sec="SEC.03", group="Welding & Metal Work", icon="cutting",
       desc="Cutting accessories and drill bits used alongside our welding and metal work supplies.",
       items=[
         ("Drill Bits", "For metal, wood, and masonry drilling."),
         ("Cutting Discs", "For metal cutting and fabrication work."),
       ]),
  dict(slug="power-drills", title="Power Drills", sec="SEC.04", group="Tools & Equipment", icon="drill",
       desc="Power drills from trusted brands for professional and industrial use.",
       items=[
         ("Makita", "Power drills and accessories."),
         ("Hitachi", "Power drills and accessories."),
         ("Bosch", "Power drills and accessories."),
         ("AEG", "Power drills and accessories."),
       ]),
  dict(slug="pneumatic-tools", title="Pneumatic Tools", sec="SEC.05", group="Tools & Equipment", icon="pneumatic",
       desc="Air-powered tools for industrial, automotive, and shop applications. Contact us with your required tool type and specs.",
       items=[("Pneumatic Tools", "Ask us for available models and specifications for your application.")]),
  dict(slug="hydraulic-hose-fittings", title="Hydraulic Hose & Fittings", sec="SEC.06", group="Tools & Equipment", icon="hydraulic",
       desc="Hoses and fitting sets for hydraulic systems across industrial equipment.",
       items=[
         ("Hydraulic Hose", "Various sizes and pressure ratings."),
         ("Fittings", "Connectors and adapters for hydraulic hose assemblies."),
       ]),
  dict(slug="wires-cables", title="Electrical Wires / Cables", sec="SEC.07", group="Electrical", icon="wire",
       desc="Electrical wires and cables from established Philippine brands.",
       items=[
         ("Phelps Dodge", "Electrical wires and cables."),
         ("Columbia", "Electrical wires and cables."),
         ("Duraflex", "Electrical wires and cables."),
         ("Philflex", "Electrical wires and cables."),
       ]),
  dict(slug="construction-materials", title="Construction Materials", sec="SEC.08", group="Construction & Steel", icon="construction",
       desc="Core construction materials to support building and fit-out projects.",
       items=[
         ("Paints", "For structural and finishing work."),
         ("Plywood", "Various thicknesses for construction use."),
         ("Good Lumber", "Quality lumber for construction projects."),
       ]),
  dict(slug="sheets", title="Sheets", sec="SEC.09", group="Construction & Steel", icon="sheet",
       desc="Sheet materials for construction, fabrication, and signage applications.",
       items=[
         ("Acrylic Sheets", "For signage, displays, and fabrication."),
         ("G.I. Sheets", "Galvanized iron sheets for construction."),
         ("B.I. Sheets", "Black iron sheets for fabrication work."),
         ("Polycarbonate Sheets", "For roofing and glazing applications."),
       ]),
  dict(slug="tubing-structural-steel", title="Tubing & Structural Steel", sec="SEC.10", group="Construction & Steel", icon="tubing",
       desc="Structural steel products for construction and fabrication projects.",
       items=[
         ("Angle Bar", "Angle bars for framing and structural support.", "angle-bar.html"),
         ("Flat Bar", "Flat bars for fabrication, framing, and general structural use.", "flat-bar.html"),
         ("Square Tube", "Square tubes for fabrication and structural use.", "square-tube.html"),
         ("Rectangular Tube", "Rectangular tubes for fabrication and structural use.", "rectangular-tube.html"),
         ("Slotted Angle Bar", "Slotted angle bars for shelving, racking, and structural framing.", "slotted-angle-bar.html"),
         ("Shafting", "Steel shafting for machinery and fabrication use.", "shafting.html"),
         ("B.I./G.I. Pipes", "Black iron (B.I.) and galvanized iron (G.I.) pipes for plumbing, structural, and fabrication use.", "bi-gi-pipes.html"),
         ("SKD11", "SKD11 tool steel bar stock for die and mold fabrication.", "skd11.html"),
         ("S45C", "S45C carbon steel bar stock for general machining and fabrication.", "s45c.html"),
         ("4140", "AISI 4140 alloy steel bar stock for machining and fabrication.", "4140.html"),
       ]),
  dict(slug="bearings", title="Bearings", sec="SEC.11", group="Bearings", icon="bearing",
       desc="Industrial bearings from established manufacturers, across standard sizes.",
       items=[
         ("FAG", "Industrial bearings."),
         ("IKO", "Industrial bearings."),
         ("KOYO", "Industrial bearings."),
       ]),
  dict(slug="gloves", title="Gloves", sec="SEC.12", group="Safety & PPE", icon="glove",
       desc="Work gloves for industrial, construction, and general handling use.",
       photo=("Assorted Gloves", "images/Products/assorted gloves.png"),
       photo_dir="images/Products/Gloves",
       # This list is the client's actual glove range (2026) — it mirrors the
       # photos in photo_dir exactly. Maong, Latex and Cadet Gloves were
       # removed because the client doesn't stock them. Descriptions for the
       # five newly added types are drafts pending the client's own wording.
       items=[
         ("Cotton Gloves", "Lightweight cotton work gloves for general handling and light-duty tasks.", "cotton-gloves.html"),
         ("Dotted Gloves", "Cotton gloves with PVC dot grip across the palm for a firmer hold on smooth surfaces.", "dotted-gloves.html"),
         ("Palm Fit Gloves", "Palm-coated gloves that keep fingertip dexterity for assembly and precision handling.", "palm-fit-gloves.html"),
         ("Top Fit Gloves", "Snug-fitting coated gloves for general assembly, sorting, and warehouse handling.", "top-fit-gloves.html"),
         ("Rubberized Gloves", "Rubber-coated gloves for improved grip and light liquid protection.", "rubberized-gloves.html"),
         ("Nitrile Gloves", "Nitrile-coated gloves offering chemical and oil resistance.", "nitrile-gloves.html"),
         ("Leather Gloves", "Heavy-duty leather gloves built for grip and abrasion resistance on tougher jobs.", "leather-gloves.html"),
         ("Anti-Cut Gloves", "Cut-resistant gloves for handling sheet metal, glass, and other sharp-edged materials.", "anti-cut-gloves.html"),
         ("Anti-Static Gloves", "Anti-static gloves for electronics work and any handling where static discharge is a risk.", "anti-static-gloves.html"),
       ]),
  dict(slug="safety-products", title="Safety Products", sec="SEC.13", group="Safety & PPE", icon="safety",
       desc="Personal protective equipment and safety accessories for industrial sites.",
       items=[
         ("Goggles", "Eye protection for industrial work."),
         ("Safety Shoes", "Protective footwear for job sites."),
         ("Leak Detector", "For detecting gas and pipeline leaks."),
       ]),
  dict(slug="packaging-materials", title="Packaging Materials", sec="SEC.14", group="Packaging Materials", icon="packaging",
       desc="Packaging supplies for shipping, bundling, and warehousing needs.",
       items=[
         ("Packaging Tape", "Packaging tape for sealing and bundling cartons and parcels.", "packaging-tape.html"),
         ("Masking Tape", "Masking tape for temporary bonding, marking, and light surface protection.", "masking-tape.html"),
         ("Kraft Tape", "Kraft paper tape for carton and box sealing.", "kraft-tape.html"),
         ("Corner Angle Board", "Corner angle boards for edge protection on palletized and stacked loads.", "corner-angle-board.html"),
         ("LDPE/HD/PP Plastic Bags/Sheets", "LDPE, HDPE, and PP plastic bags and sheets for wrapping, covering, and packing goods.", "ldpe-hd-pp-plastic-bags-sheets.html"),
         ("P.E. Foam", "Polyethylene foam sheets and rolls for cushioning and surface protection.", "pe-foam.html"),
         ("Plastic and Wooden Pallets", "Plastic and wooden pallets for storage, handling, and shipping of palletized goods.", "plastic-and-wooden-pallets.html"),
         ("Plastic Crates", "Plastic crates for storage, handling, and transport of goods.", "plastic-crates.html"),
         ("Bins", "Storage bins for warehousing and general handling use.", "bins.html"),
         ("Bubble Sheets", "Bubble wrap sheets for cushioning and protecting goods in transit.", "bubble-sheets.html"),
         ("Stretch Film", "For pallet wrapping and load stability.", "stretch-film.html"),
         ("Styropore", "Styrofoam sheets and blocks for cushioning and insulation.", "styropore.html"),
         ("Nylon Strap", "Nylon strapping for bundling and securing goods.", "nylon-strap.html"),
         ("Metal and Plastic Clip", "Metal and plastic strapping clips and seals for securing straps in place.", "metal-and-plastic-clip.html"),
         ("Rubber Bands", "Rubber bands for general bundling and handling use.", "rubber-bands.html"),
         ("Tape Dispenser", "Tape dispensers for fast, consistent taping in packing operations.", "tape-dispenser.html"),
       ]),
  dict(slug="caster-wheels", title="Caster Wheels", sec="SEC.15", group="Bearings", icon="bearing",
       desc="Caster wheels for material handling equipment, furniture, and industrial mobility.",
       photo=("Assorted Caster Wheels — Sample Photo", "images/Products/caster wheels.png"),
       items=[
         ("Swivel Casters", "Swivel-mount casters for maneuverable equipment and carts."),
         ("Rigid Casters", "Fixed-direction casters for straight-line load movement."),
         ("Heavy-Duty Casters", "Reinforced casters for heavy industrial loads."),
         ("Light-Duty Casters", "Casters for furniture and light equipment."),
       ]),
]

by_slug = {c["slug"]: c for c in CATEGORIES}
slug_order = [c["slug"] for c in CATEGORIES]

# ---- Brand data (single source for both the homepage brand strip and brands.html) ----
# name, product-line group, icon key, logo image path (None until a real logo is uploaded)
# Brands are shown as a flat, ungrouped logo wall (brands.html + a curated
# subset on the homepage) — name, icon key (used only when there's no real
# logo yet), logo image path (None until the client uploads one).
BRANDS = [
    ("FAG", "bearing", None),
    ("IKO", "bearing", None),
    ("KOYO", "bearing", None),
    ("Makita", "drill", "images/Brands/makita.webp"),
    ("Hitachi", "drill", None),
    ("Bosch", "drill", "images/Brands/bosch.png"),
    ("AEG", "drill", None),
    ("Phelps Dodge", "wire", "images/Brands/Phelps dodge.png"),
    ("Columbia", "wire", None),
    ("Duraflex", "wire", None),
    ("Philflex", "wire", None),
    ("G-Weld", "welding", "images/Brands/G Weld PF Series.png"),
    ("Mitutoyo", "cutting", "images/Brands/mitotuyo.png"),
    ("Sumotech", "brand", "images/Brands/Sumotech.png"),
    ("Grand Sumoweld", "welding", None),
    ("ABC", "brand", "images/Brands/ABC.jpg"),
    ("Yanase", "brand", "images/Brands/Yanase.jpg"),
    ("Boysen", "brand", "images/Brands/Boysen.png"),
    ("Davies", "brand", "images/Brands/Davies.jpg"),
]
BRANDS_BY_NAME = {b[0]: b for b in BRANDS}
HOMEPAGE_BRAND_NAMES = ["Sumotech", "G-Weld", "Grand Sumoweld", "ABC", "Yanase", "Boysen"]

# Order the brands.html wall: these lead, in exactly this order (the client's
# own house brands first, then the marquee manufacturers). Everything else
# follows in BRANDS order.
#
# The client asked for the tail to be "random" — it's deliberately NOT
# shuffled at build time. A random order would rewrite brands.html on every
# regeneration and fill the git history with meaningless diffs; the intent
# ("order doesn't matter back there") is served by a stable arbitrary order.
BRANDS_FEATURED = [
    "Sumotech", "Grand Sumoweld", "G-Weld", "ABC", "Yanase",
    "Mitutoyo", "Phelps Dodge", "Bosch", "Makita",
]

# Fail the build loudly on a typo — a misspelled name would otherwise just
# drop that brand off the front of the wall without any error.
_unknown_brands = sorted({n for n in BRANDS_FEATURED + HOMEPAGE_BRAND_NAMES if n not in BRANDS_BY_NAME})
if _unknown_brands:
    raise SystemExit(f"generate.py: unknown brand name(s) {_unknown_brands} — must match a name in BRANDS")

BRANDS_ORDERED = [BRANDS_BY_NAME[n] for n in BRANDS_FEATURED] + \
                 [b for b in BRANDS if b[0] not in set(BRANDS_FEATURED)]

def brand_item_html(name, icon_key, img, reveal_delay=None, depth=""):
    if img:
        inner = f'<img class="brand-logo" src="{asset(img, depth)}" alt="{name}">'
    else:
        inner = f'<div class="brand-placeholder">{icon(icon_key, size=26)}<span>{name}</span></div>'
    attrs = f' data-reveal data-reveal-delay="{reveal_delay}"' if reveal_delay is not None else ''
    return f'<div class="brand-tile"{attrs}>{inner}</div>'

# ---- Nav "Products" mega-menu: hover a category, see the items under it ----
def item_href(cat, item, depth=""):
    """Link to an item: its own product page if it has one, else the anchor on
    its category page."""
    name, link = item[0], (item[2] if len(item) == 3 else None)
    if link:
        return item_page_href(link, depth)
    return f'{cat_href(cat["slug"], depth)}#{slugify(name)}'

def mega_menu_html(depth=""):
    rows = []
    for cat in CATEGORIES:
        sub_links = "\n            ".join(
            f'<a href="{item_href(cat, item, depth)}">{item[0]}</a>' for item in cat["items"]
        ) or f'<a href="{cat_href(cat["slug"], depth)}">View {cat["title"]}</a>'
        rows.append(f"""<li class="mega-cat">
          <div class="mega-cat-row">
            <a href="{cat_href(cat['slug'], depth)}" class="mega-cat-link">{cat['title']}</a>
            <button type="button" class="mega-cat-toggle" aria-expanded="false" aria-label="Show {cat['title']} items">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="chev"><path d="M9 18l6-6-6-6"/></svg>
            </button>
          </div>
          <div class="mega-sub">
            <div class="mega-sub-scroll">
            {sub_links}
            </div>
          </div>
        </li>""")
    return "\n        ".join(rows)

# The menu is identical at every depth apart from its link prefixes, and it's
# inlined into all 68 pages — so build it once per distinct depth and reuse.
# (Was a single MEGA_MENU_HTML constant before pages moved into subfolders.)
_MEGA_MENU_CACHE = {}

def mega_menu(depth=""):
    if depth not in _MEGA_MENU_CACHE:
        _MEGA_MENU_CACHE[depth] = mega_menu_html(depth)
    return _MEGA_MENU_CACHE[depth]

# Logo mark — a badge with a stylized "G" monogram, echoing the icon-badge
# gradient treatment already used in the "Why GLMI" cards elsewhere on the
# site. Placeholder-quality (built in code, not by a graphic designer) —
# swap for a professionally designed mark whenever the client has one;
# everything referencing it (header, this constant) can stay as-is, just
# replace the <svg>...</svg> markup here.
LOGO_MARK = """<svg class="logo-mark" viewBox="0 0 40 40" width="36" height="36" aria-hidden="true">
        <defs>
          <linearGradient id="logoMarkGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stop-color="#1C7A41"/>
            <stop offset="1" stop-color="#125C2F"/>
          </linearGradient>
        </defs>
        <rect x="1" y="1" width="38" height="38" rx="10" fill="url(#logoMarkGrad)"/>
        <text x="20" y="27" font-family="'Playfair Display', serif" font-size="21" font-weight="700" fill="#FAF8F2" text-anchor="middle">G</text>
      </svg>"""

def header(active=None, depth=""):
    return f"""<header>
  <div class="header-inner">
    <a href="{depth}index.html" class="logo">
      {LOGO_MARK}
      <span class="logo-text">
        <span class="name">GL<span>MI</span></span>
        <span class="tagline">Wholesaler &middot; Retailer</span>
      </span>
    </a>
    <button class="nav-toggle" id="navToggle" aria-expanded="false" aria-controls="mainNav">MENU</button>
    <nav id="mainNav">
      <div class="nav-item has-mega">
        <div class="mega-row">
          <a href="{depth}products.html" class="mega-label"{' aria-current="page"' if active=="products" else ""}>Products</a>
          <button type="button" class="mega-toggle" aria-expanded="false" aria-label="Show product categories">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>
          </button>
        </div>
        <div class="mega-menu">
          <ul class="mega-cats">
            {mega_menu(depth)}
          </ul>
          <div class="mega-cta"><a href="{depth}products.html">View Full Catalog &rarr;</a></div>
        </div>
      </div>
      <a href="{depth}brands.html"{' aria-current="page"' if active=="brands" else ""}>Brands</a>
      <a href="{depth}who-we-are.html"{' aria-current="page"' if active=="about" else ""}>Who We Are</a>
      <a href="{depth}index.html#contact">Contact</a>
      <a href="{depth}request-quote.html" class="quote-link"{' aria-current="page"' if active=="quote" else ""}>
        {icon("quote", cls="")}
        <span class="txt">Request a Quote</span>
        <span class="quote-badge" id="quoteCount" hidden>0</span>
      </a>
      <a href="tel:{PHONE}" class="call-btn">
        {icon("tag", cls="")}
        <span class="txt">{PHONE_DISPLAY}</span>
      </a>
    </nav>
  </div>
</header>"""

def footer(depth=""):
    return f"""<footer>
  <div class="wrap footer-inner">
    <span>&copy; 2026 {COMPANY}. All rights reserved.</span>
    <div class="footer-links">
      <a href="{depth}products.html">Products</a>
      <a href="{depth}brands.html">Brands</a>
      <a href="{depth}who-we-are.html">Who We Are</a>
      <a href="{depth}index.html#contact">Contact</a>
    </div>
  </div>
</footer>
<script>
{JS_CONTENT}
</script>"""

CSS_CONTENT = open(os.path.join(os.path.dirname(__file__), "styles.css")).read()
JS_CONTENT = open(os.path.join(os.path.dirname(__file__), "site.js")).read()

def head(title, desc, extra_head=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | {COMPANY}</title>
<meta name="description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet">
<style>
{CSS_CONTENT}
</style>
{extra_head}</head>
<body>"""

# Loaded only on the homepage — scroll-reveal animations (see site.js) use
# this. Other pages don't need it, so don't add this to head() globally.
ANIME_JS_TAG = '<script src="https://cdn.jsdelivr.net/npm/animejs@3.2.2/lib/anime.min.js"></script>\n'

# Loaded only on request-quote.html — sends the quote request email
# client-side (no backend). Credentials (public key / service ID / template
# ID) live as plain constants at the top of site.js, not here.
EMAILJS_TAG = '<script src="https://cdn.jsdelivr.net/npm/@emailjs/browser@4/dist/email.min.js"></script>\n'

def mini_cta(cat_title=None, heading=None, sub=None):
    heading = heading or f"Need pricing for {cat_title}?"
    sub = sub or "Send us the item, quantity, and specs — we'll get back with a quote."
    return f"""<div class="mini-cta">
        <div>
          <h3>{heading}</h3>
          <p>{sub}</p>
        </div>
        <div class="ctas">
          <a href="tel:{PHONE}" class="btn btn-primary">Call Now</a>
          <a href="mailto:{EMAIL}" class="btn btn-ghost" style="color:var(--ink);border-color:var(--ink);">Email Us</a>
        </div>
      </div>"""

# =========================================================
# 1. Generate each category page
# =========================================================
for idx, cat in enumerate(CATEGORIES):
    slug = cat["slug"]
    depth = "../"  # category pages live in categories/
    prev_cat = CATEGORIES[idx - 1] if idx > 0 else CATEGORIES[-1]
    next_cat = CATEGORIES[idx + 1] if idx < len(CATEGORIES) - 1 else CATEGORIES[0]

    _cards = []
    for item in cat["items"]:
        name, _d, link = item if len(item) == 3 else (item[0], item[1], None)
        photos = item_photos(cat, link or f"{slugify(name)}.html")
        pic = thumb(name, cat["icon"], size=30,
                    img=(photos[0] if photos else None), depth=depth)
        if link:
            _cards.append(f"""<a href="{item_page_href(link, depth)}" id="{slugify(name)}" class="item-card">
            {pic}
            <div class="item-body"><h4>{name}</h4></div>
          </a>""")
        else:
            _cards.append(f"""<div id="{slugify(name)}" class="item-card">
            {pic}
            <div class="item-body"><h4>{name}</h4></div>
          </div>""")
    item_cards = "\n          ".join(_cards)

    gallery_slides = []
    for item in cat["items"]:
        nm = item[0]
        lk = item[2] if len(item) == 3 else None
        ph = item_photos(cat, lk or f"{slugify(nm)}.html")
        gallery_slides.append((nm, cat["icon"], ph[0]) if ph else (nm, cat["icon"]))
    if not gallery_slides:
        gallery_slides = [(cat["title"], cat["icon"])]
    if cat.get("photo"):
        photo_label, photo_img = cat["photo"]
        gallery_slides = [(photo_label, cat["icon"], photo_img)] + gallery_slides
    # Product shots are square on white; the gallery frame is 21:9, so letterbox
    # them (contain) instead of cropping a thin band out of the middle.
    gallery_html = carousel(gallery_slides, depth=depth, contain=bool(cat.get("photo_dir")))
    # Categories with real photography shouldn't still apologise for placeholders.
    gallery_sub = ("Real product photos &mdash; ask us for more angles or specs on any item."
                   if cat.get("photo_dir")
                   else "Sample placeholders shown below &mdash; swap in real product photos once available.")

    page = head(cat["title"], cat["desc"]) + "\n" + header(active="products", depth=depth) + f"""

<div class="breadcrumb">
  <div class="wrap">
    <a href="{depth}index.html">Home</a><span class="sep">/</span><a href="{depth}products.html">Products</a><span class="sep">/</span><span class="current">{cat['title']}</span>
  </div>
</div>

<section class="cat-hero" style="padding:44px 0 52px;">
  <div class="wrap cat-hero-inner">
    <div class="cat-hero-icon">{icon(cat["icon"], size=34)}</div>
    <div>
      <h1>{cat['title']}</h1>
      <p>{cat['desc']}</p>
    </div>
  </div>
</section>

<main>
  <section>
    <div class="wrap">
      <div class="section-head">
        <div>
          <span class="kicker">Photo Gallery</span>
          <h2>{cat['title']} &mdash; Gallery</h2>
        </div>
        <p class="sub">{gallery_sub}</p>
      </div>
      {gallery_html}

      <div class="section-head">
        <div>
          <span class="kicker">Available Items</span>
          <h2>{cat['title']}</h2>
        </div>
        <p class="sub">Photos and full specs available on request &mdash; call or message us with what you need.</p>
      </div>
      <div class="card-grid" style="grid-template-columns:repeat(auto-fill, minmax(240px,1fr));">
          {item_cards}
      </div>

      <div style="margin-top:48px;">
        {mini_cta(cat['title'])}
      </div>

      <div class="cat-pagination">
        <a href="{cat_href(prev_cat['slug'], depth)}"><span class="dir">&larr; Previous</span>{prev_cat['title']}</a>
        <a href="{cat_href(next_cat['slug'], depth)}" class="next"><span class="dir">Next &rarr;</span>{next_cat['title']}</a>
      </div>
    </div>
  </section>
</main>

""" + footer(depth=depth) + "\n</body>\n</html>"

    with open(os.path.join(OUT, CAT_DIR, f"{slug}.html"), "w") as f:
        f.write(page)

# =========================================================
# 2. Generate products hub page — flat A-Z grid, no group sections
#    (Welding Materials pinned first, like Wyler's /products/ page)
# =========================================================
az_categories = sorted(CATEGORIES, key=lambda c: c["title"])
welding_cat = next(c for c in az_categories if c["slug"] == "welding-materials")
az_categories.remove(welding_cat)
az_categories.insert(0, welding_cat)

category_cards = "\n        ".join(
    f"""<a href="{cat_href(c['slug'])}" class="plate-card">
          <span class="rivet tl"></span><span class="rivet tr"></span><span class="rivet bl"></span><span class="rivet br"></span>
          {thumb(c['title'], c['icon'], img=(c['photo'][1] if c.get('photo') else None))}
          <div class="plate-body">
            <h4>{c['title']}</h4>
            <p>{c['desc']}</p>
            <span class="go">View Products &rarr;</span>
          </div>
        </a>""" for c in az_categories
)

products_page = head("Products", "Full product catalog — welding materials, abrasives, bearings, tools, electrical wires, safety gear, and construction hardware.") + "\n" + header(active="products") + f"""

<div class="breadcrumb">
  <div class="wrap"><a href="index.html">Home</a><span class="sep">/</span><span class="current">Products</span></div>
</div>

<section class="cat-hero" style="padding:44px 0 52px;">
  <div class="wrap">
    <span class="group-code mono">Full Catalog</span>
    <h1 style="margin-top:8px;">All Product Categories</h1>
    <p style="color:#C7D3C9;font-size:15px;margin-top:8px;max-width:560px;">{len(CATEGORIES)} categories, A&ndash;Z. Select a category to view items, or contact us directly with your requirements.</p>
  </div>
</section>

<main>
  <section>
    <div class="wrap">
      <div class="card-grid">
        {category_cards}
      </div>
    </div>
  </section>
</main>

""" + footer() + "\n</body>\n</html>"

with open(os.path.join(OUT, "products.html"), "w") as f:
    f.write(products_page)

# =========================================================
# 3. Generate homepage
# =========================================================
group_teasers = [
    ("welding-materials", "welding", "Welding & Metal Work", "Welding materials, abrasives, cutting tools/drills."),
    ("power-drills", "drill", "Tools & Equipment", "Power drills, pneumatic tools, hydraulic hose &amp; fittings."),
    ("wires-cables", "wire", "Electrical", "Electrical wires and cables."),
    ("construction-materials", "construction", "Construction &amp; Steel", "Construction materials, sheets, tubing &amp; structural steel."),
    ("bearings", "bearing", "Bearings", "FAG, IKO, KOYO."),
    ("gloves", "glove", "Safety &amp; PPE", "Gloves and safety products."),
    ("packaging-materials", "packaging", "Packaging Materials", "Tape, stretch film, plastic &amp; metal straps."),
]
teaser_cards = "\n        ".join(
    f"""<a href="{cat_href(slug)}" class="plate-card" data-reveal data-reveal-delay="{i * 60}">
          <span class="rivet tl"></span><span class="rivet tr"></span><span class="rivet bl"></span><span class="rivet br"></span>
          {thumb(name, ic, img=(by_slug[slug]['photo'][1] if by_slug[slug].get('photo') else None))}
          <div class="plate-body">
            <h4>{name}</h4>
            <p>{desc}</p>
            <span class="go">View Products &rarr;</span>
          </div>
        </a>""" for i, (slug, ic, name, desc) in enumerate(group_teasers)
)

homepage_brand_tiles = "\n        ".join(
    brand_item_html(*BRANDS_BY_NAME[name], reveal_delay=i * 60)
    for i, name in enumerate(HOMEPAGE_BRAND_NAMES)
)

# ---- Homepage hero slideshow ----
# Client-supplied banner artwork (images/Hero Photos/*.png, kept as the
# untouched originals; the page loads the compressed images/hero/*.jpg).
# The headline/body copy is BAKED INTO each image, which is why the hero has
# no HTML headline of its own anymore — it would duplicate what's already
# drawn. That also means search engines and screen readers can't read any of
# it, so the alt text below carries the same message in text form and the
# section keeps a visually-hidden <h1>. Keep both in sync if the artwork
# changes.
HERO_SLIDES = [
    ("images/hero/hero-1.jpg",
     "Trusted wholesaler and retailer since 2003 — top-quality materials, service you can trust. "
     "MIG welding wire spools, assorted work gloves, abrasive discs and belts, caster wheels and a fiber drum."),
    ("images/hero/hero-2.jpg",
     "Top-notch welding and safety equipment — weld stronger, work safer. "
     "Grand Sumoweld MIG wires paired with Sumotech safety gloves in leather, nitrile and cotton."),
    ("images/hero/hero-3.jpg",
     "Quality materials with exceptional service — your industrial supply partner. "
     "Cordless power drills, structural steel bar and angle, bearings, sanding belts, flap discs and MIG wire."),
    ("images/hero/hero-4.jpg",
     "Serving our partners since 2003 — a supplier contractors have trusted for over 23 years. "
     "Phelps Dodge electrical wire, Davies paints, threaded rod, steel sheets and tubing, and fiberglass ladders."),
    ("images/hero/hero-5.jpg",
     "Brands we carry — trusted brands, exceptional service. "
     "G-Weld, Sumotech, Grand Sumoweld, Yanase, Mitutoyo, Phelps Dodge, Boysen, Davies, Nation, ABC, Makita and Bosch."),
]

hero_slides_html = "\n        ".join(
    f"""<div class="carousel-slide" role="group" aria-roledescription="slide" aria-label="Slide {i + 1} of {len(HERO_SLIDES)}">
          <img src="{asset(src)}" alt="{alt}" width="1600" height="900"
               {'fetchpriority="high"' if i == 0 else 'loading="lazy"'}>
        </div>"""
    for i, (src, alt) in enumerate(HERO_SLIDES)
)

index_page = head(f"{COMPANY} | Industrial Supplies Trading",
                   f"{COMPANY} supplies welding materials, tools, bearings, electrical wires, safety gear, and construction hardware to contractors and industrial buyers — backed by responsive, dependable service.",
                   extra_head=ANIME_JS_TAG) + "\n" + header() + f"""

<a id="top"></a>
<section class="hero">
  <h1 class="sr-only">{COMPANY} &mdash; wholesaler and retailer of quality industrial and construction materials, serving contractors and industrial buyers since {ESTABLISHED_YEAR}</h1>
  <div class="wrap">
    <div class="carousel hero-carousel" data-autoplay="6000" data-loop aria-roledescription="carousel" aria-label="{COMPANY} highlights">
      <div class="carousel-track">
        {hero_slides_html}
      </div>
      <button class="carousel-btn prev" type="button" aria-label="Previous slide">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>
      </button>
      <button class="carousel-btn next" type="button" aria-label="Next slide">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l6-6-6-6"/></svg>
      </button>
      <div class="carousel-dots"></div>
    </div>
  </div>
  <div class="wrap hero-ctas">
    <a href="products.html" class="btn btn-primary">Browse Products</a>
    <a href="request-quote.html" class="btn btn-ghost hero-ghost">Request a Quote</a>
  </div>
</section>

<main>
  <section class="why-us">
    <div class="wrap">
      <div class="section-head" data-reveal>
        <div>
          <span class="kicker">Why {COMPANY}</span>
          <h2>Built on quality, trust, and service.</h2>
        </div>
        <p class="sub">What sets us apart as your industrial supply partner.</p>
      </div>
      <div class="why-grid">
        <div class="why-card" data-reveal data-reveal-delay="0">
          <div class="icon-badge"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2 3 7v10l9 5 9-5V7z"/><path d="M12 22V12M3 7l9 5 9-5"/></svg></div>
          <h3>Top-Quality Materials</h3>
          <p>Genuine, dependable stock across every category &mdash; from welding wire to structural steel &mdash; so what you install or resell holds up.</p>
        </div>
        <div class="why-card" data-reveal data-reveal-delay="80">
          <div class="icon-badge alt"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2 4 6v6c0 5 3.5 8.5 8 10 4.5-1.5 8-5 8-10V6z"/></svg></div>
          <h3>Trusted Industrial Supplier</h3>
          <p>{COMPANY} has built its reputation as a dependable wholesaler and retailer for contractors and industrial buyers.</p>
        </div>
        <div class="why-card" data-reveal data-reveal-delay="160">
          <div class="icon-badge"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="5"/><path d="M8.5 13.5 6 21l6-3 6 3-2.5-7.5"/></svg></div>
          <h3>Trusted Brands</h3>
          <p>Sumotech, Sumoweld, G-Weld, Yanase, ABC, and more &mdash; established names you can rely on.</p>
        </div>
        <div class="why-card" data-reveal data-reveal-delay="240">
          <div class="icon-badge alt"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg></div>
          <h3>Exceptional Service, Best Prices</h3>
          <p>Direct, responsive support and competitive pricing on bulk and trade orders &mdash; call or message us for a quote.</p>
        </div>
      </div>
    </div>
  </section>

  <section id="products">
    <div class="wrap">
      <div class="section-head" data-reveal>
        <div>
          <span class="kicker">What We Supply</span>
          <h2>Product groups</h2>
        </div>
        <p class="sub">14 categories across 7 groups. Browse the full catalog for item-level detail.</p>
      </div>
      <div class="card-grid">
        {teaser_cards}
      </div>
      <div style="text-align:center;margin-top:32px;">
        <a href="products.html" class="btn btn-primary" style="display:inline-flex;">View Full Catalog</a>
      </div>
    </div>
  </section>

  <section id="brands">
    <div class="wrap">
      <div class="section-head" data-reveal>
        <div>
          <span class="kicker">Trusted Names</span>
          <h2>Featured brands</h2>
        </div>
        <p class="sub">Genuine stock from established manufacturers across our product lines.</p>
      </div>
      <div class="brand-wall">
        {homepage_brand_tiles}
      </div>
      <div style="text-align:center;margin-top:32px;">
        <a href="brands.html" class="btn btn-primary" style="display:inline-flex;">View All Brands</a>
      </div>
    </div>
  </section>

  <section id="who-we-are">
    <div class="wrap about">
      <div class="about-copy" data-reveal>
        <span class="kicker">Who We Are</span>
        <h2>Built for the trade, not the storefront.</h2>
        <p>{COMPANY} is a trusted wholesaler and retailer of quality industrial and construction materials, established in {ESTABLISHED_YEAR}. We supply contractors, fabricators, and industrial buyers with top-quality materials and equipment from trusted brands &mdash; backed by exceptional service and competitive prices.</p>
        <p><a href="who-we-are.html" class="btn btn-ghost" style="color:var(--ink);border-color:var(--ink);display:inline-flex;margin-top:8px;">Read Our Full Story &rarr;</a></p>
      </div>
      <div class="stat-plate" data-reveal data-reveal-delay="120">
        <div class="stat"><h3>{ESTABLISHED_YEAR}</h3><p>Established</p></div>
        <div class="stat"><h3 style="font-size:20px;">San Juan City</h3><p>Metro Manila, PH</p></div>
      </div>
    </div>
  </section>

  <section class="contact" id="contact">
    <div class="wrap contact-inner">
      <div data-reveal>
        <h2>Need stock or a quote?</h2>
        <p>Send us your item list and quantities &mdash; we'll get back with pricing and availability. No online orders, just a direct line to us.</p>
        <div class="contact-ctas">
          <a href="tel:{PHONE}" class="btn btn-primary">Call Now</a>
          <a href="mailto:{EMAIL}" class="btn btn-ghost">Email Us</a>
        </div>
      </div>
      <div class="contact-plate" data-reveal data-reveal-delay="120">
        <div class="row">{icon("tag")}<div><div class="label">Mobile / Viber</div><div class="value">{PHONE_DISPLAY}</div></div></div>
        <div class="row">{icon("tag")}<div><div class="label">Telephone</div><div class="value">{LANDLINE_DISPLAY}</div></div></div>
        <div class="row">{icon("tag")}<div><div class="label">Email</div><div class="value">{EMAIL_DISPLAY}</div></div></div>
        <div class="row">{icon("tag")}<div><div class="label">Address</div><div class="value">{ADDRESS}</div></div></div>
        <div class="row">{icon("tag")}<div><div class="label">Business Hours</div><div class="value">[Mon&ndash;Sat, 8:00 AM &ndash; 5:00 PM]</div></div></div>
      </div>
    </div>
  </section>
</main>

""" + footer() + "\n</body>\n</html>"

with open(os.path.join(OUT, "index.html"), "w") as f:
    f.write(index_page)

print("Generated:", len(CATEGORIES), "category pages + products.html + index.html")

# =========================================================
# 4. Generate a single-product page (example: MIG Wire ER70S-6)
# =========================================================
def gthumb(label, icon_key, active=False):
    cls = "gthumb active" if active else "gthumb"
    return f"""<div class="{cls}">
            {thumb_visual(label, icon_key, size=22, show_label=True)}
          </div>"""

mig_gallery_items = [
    ("MIG Wire — Spool View", "welding"),
    ("MIG Wire — Coil Packaging", "packaging"),
    ("MIG Wire — Wire Surface Detail", "welding"),
    ("MIG Wire — Diameter Reference", "tag"),
]
gallery_thumbs_html = "\n          ".join(
    gthumb(lbl, ic, active=(i == 0)) for i, (lbl, ic) in enumerate(mig_gallery_items)
)

feat_items = [
    "Copper-coated mild steel wire for smooth, consistent wire feeding.",
    "Suitable for 100% CO2 or Argon-CO2 mixed shielding gas.",
    "Stable arc performance with low spatter and clean bead appearance.",
    "Supports flat, horizontal, vertical, and overhead welding positions.",
    "Available across common diameters for light to heavy fabrication work.",
    "Spool and coil packaging options for shop use or bulk supply.",
]
feat_html = "\n        ".join(
    f'<li>{icon("tag", size=16)}<span>{t}</span></li>' for t in feat_items
)

spec_rows = [
    ("Classification", "ER70S-6"),
    ("Material", "Mild steel, copper coated"),
    ("Available Diameters", "0.8mm, 0.9mm, 1.0mm, 1.2mm, 1.6mm"),
    ("Shielding Gas", "100% CO2 or Argon-CO2 mixed gas"),
    ("Welding Position", "All positions (flat, horizontal, vertical, overhead)"),
    ("Standard Packaging", "5kg / 15kg / 20kg spool"),
]
spec_html = "\n        ".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in spec_rows)

pack_rows = [
    ("0.8mm", "5kg / spool", "Ask for availability"),
    ("0.9mm", "15kg / spool", "Ask for availability"),
    ("1.0mm", "15kg / spool", "Ask for availability"),
    ("1.2mm", "15kg / spool", "Ask for availability"),
    ("1.6mm", "15kg / spool", "Ask for availability"),
]
pack_html = "\n        ".join(
    f"<tr><td>{d}</td><td>{p}</td><td>{n}</td></tr>" for d, p, n in pack_rows
)

MIG_SLUG = "mig-wire-er70s-6.html"
mig_depth = "../"  # this is an item page — lives in items/

related_items = [c for c in CATEGORIES if c["group"] == "Welding & Metal Work" and c["slug"] != "welding-materials"]
related_html = "\n        ".join(
    f"""<a href="{cat_href(c['slug'], mig_depth)}" class="plate-card">
          <span class="rivet tl"></span><span class="rivet tr"></span><span class="rivet bl"></span><span class="rivet br"></span>
          {thumb(c['title'], c['icon'], img=(c['photo'][1] if c.get('photo') else None), depth=mig_depth)}
          <div class="plate-body"><h4>{c['title']}</h4><span class="go">View &rarr;</span></div>
        </a>""" for c in related_items
)

mig_page = head("MIG Welding Wire — ER70S-6", "MIG welding wire ER70S-6, copper coated, multiple diameters, for CO2 and Argon-CO2 shielded welding.") + "\n" + header(active="products", depth=mig_depth) + f"""

<div class="breadcrumb">
  <div class="wrap">
    <a href="{mig_depth}index.html">Home</a><span class="sep">/</span><a href="{mig_depth}products.html">Products</a><span class="sep">/</span><a href="{cat_href('welding-materials', mig_depth)}">Welding Materials</a><span class="sep">/</span><span class="current">MIG Wire ER70S-6</span>
  </div>
</div>

<main>
  <section style="padding-top:48px;">
    <div class="wrap product-hero">

      <div class="product-gallery">
        <div class="gallery-main">
          <span class="sample-tag">SAMPLE IMAGE</span>
          {thumb_visual(mig_gallery_items[0][0], mig_gallery_items[0][1], size=64)}
        </div>
        <div class="gallery-thumbs">
          {gallery_thumbs_html}
        </div>
      </div>

      <div class="product-info">
        <h1>MIG Welding Wire &mdash; ER70S-6</h1>
        <div class="quickfacts">
          <span class="qf">Classification: <b>ER70S-6</b></span>
          <span class="qf">Material: <b>Copper-coated mild steel</b></span>
          <span class="qf">Diameters: <b>0.8&ndash;1.6mm</b></span>
        </div>
        <p class="desc">A general-purpose copper-coated MIG welding wire suited for CO2 and Argon-CO2 shielded welding of mild and medium-strength steel. Commonly used across structural fabrication, general repair, and light-to-medium industrial welding work. Available in multiple diameters and packaging sizes &mdash; contact us for current stock and pricing.</p>

        <div class="inquire-box">
          <div class="row">
            <label>Diameter</label>
            <span class="qf" style="margin:0;">1.2mm (standard) &mdash; other sizes on request</span>
          </div>
          <div class="row">
            <label>Quantity (spools)</label>
            <div class="qty-stepper">
              <button type="button" class="qty-minus" aria-label="Decrease quantity">&minus;</button>
              <input type="text" value="1" inputmode="numeric" aria-label="Quantity">
              <button type="button" class="qty-plus" aria-label="Increase quantity">+</button>
            </div>
          </div>
          <div class="ctas">
            <button type="button" class="btn btn-primary add-to-quote" data-url="{ITEM_DIR}/{MIG_SLUG}" data-name="MIG Welding Wire — ER70S-6">
              {icon("quote", cls="")}
              <span class="btn-txt">Add to Quote</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="wrap">
      <div class="pd-block">
        <h2>Key Features</h2>
        <ul class="feat-list">
          {feat_html}
        </ul>
      </div>

      <div class="pd-block">
        <h2>Specifications</h2>
        <div class="table-scroll">
          <table class="spec-table">
            <tbody>
              {spec_html}
            </tbody>
          </table>
        </div>
      </div>

      <div class="pd-block">
        <h2>Packaging Options</h2>
        <div class="table-scroll">
          <table class="spec-table">
            <thead><tr><th>Diameter</th><th>Standard Packaging</th><th>Notes</th></tr></thead>
            <tbody>
              {pack_html}
            </tbody>
          </table>
        </div>
      </div>

      <div class="pd-block">
        {mini_cta("MIG Wire ER70S-6")}
      </div>

      <div class="pd-block">
        <h2>More from Welding &amp; Metal Work</h2>
        <div class="related-grid">
          {related_html}
        </div>
      </div>
    </div>
  </section>
</main>

""" + footer(depth=mig_depth) + "\n</body>\n</html>"

with open(os.path.join(OUT, ITEM_DIR, MIG_SLUG), "w") as f:
    f.write(mig_page)

print(f"Generated product page: {ITEM_DIR}/{MIG_SLUG}")

# =========================================================
# 4b. Generate simple product pages (description + photos only, no spec/
# packaging tables) — for items whose CATEGORIES entry has a page link.
# =========================================================
def product_gallery(name, photos, gallery_items, depth):
    """Main image + thumbnail strip. Uses the item's real photos when it has
    any, otherwise falls back to the labelled SVG placeholders."""
    if photos:
        thumbs = "\n          ".join(
            f"""<div class="gthumb{' active' if i == 0 else ''}">
            <img src="{asset(p, depth)}" alt="{name} — view {i + 1}" loading="lazy">
          </div>""" for i, p in enumerate(photos)
        )
        return f"""<div class="product-gallery">
        <div class="gallery-main has-photo">
          <img class="gallery-photo" src="{asset(photos[0], depth)}" alt="{name}">
        </div>
        <div class="gallery-thumbs">
          {thumbs}
        </div>
      </div>"""
    thumbs = "\n          ".join(
        gthumb(lbl, ic, active=(i == 0)) for i, (lbl, ic) in enumerate(gallery_items)
    )
    return f"""<div class="product-gallery">
        <div class="gallery-main">
          <span class="sample-tag">SAMPLE IMAGE</span>
          {thumb_visual(gallery_items[0][0], gallery_items[0][1], size=64)}
        </div>
        <div class="gallery-thumbs">
          {thumbs}
        </div>
      </div>"""

def product_page(cat, name, desc, gallery_items, slug):
    depth = "../"  # product pages live in items/
    photos = item_photos(cat, slug)
    gallery_html = product_gallery(name, photos, gallery_items, depth)
    related = [it for it in cat["items"] if it[0] != name and len(it) == 3 and it[2]]
    related_html = "\n        ".join(
        f"""<a href="{item_page_href(it[2], depth)}" class="plate-card">
            <span class="rivet tl"></span><span class="rivet tr"></span><span class="rivet bl"></span><span class="rivet br"></span>
            {thumb(it[0], cat["icon"], img=_first_photo(cat, it[2]), depth=depth)}
            <div class="plate-body"><h4>{it[0]}</h4><span class="go">View &rarr;</span></div>
          </a>""" for it in related
    )
    page = head(name, desc) + "\n" + header(active="products", depth=depth) + f"""

<div class="breadcrumb">
  <div class="wrap">
    <a href="{depth}index.html">Home</a><span class="sep">/</span><a href="{depth}products.html">Products</a><span class="sep">/</span><a href="{cat_href(cat['slug'], depth)}">{cat['title']}</a><span class="sep">/</span><span class="current">{name}</span>
  </div>
</div>

<main>
  <section style="padding-top:48px;">
    <div class="wrap product-hero">

      {gallery_html}

      <div class="product-info">
        <h1>{name}</h1>
        <p class="desc">{desc}</p>

        <div class="inquire-box">
          <div class="row">
            <label>Quantity</label>
            <div class="qty-stepper">
              <button type="button" class="qty-minus" aria-label="Decrease quantity">&minus;</button>
              <input type="text" value="1" inputmode="numeric" aria-label="Quantity">
              <button type="button" class="qty-plus" aria-label="Increase quantity">+</button>
            </div>
          </div>
          <div class="ctas">
            <button type="button" class="btn btn-primary add-to-quote" data-url="{ITEM_DIR}/{slug}" data-name="{name}">
              {icon("quote", cls="")}
              <span class="btn-txt">Add to Quote</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="wrap">
      <div class="pd-block">
        {mini_cta(name)}
      </div>

      <div class="pd-block">
        <h2>More {cat['title']}</h2>
        <div class="related-grid">
          {related_html}
        </div>
      </div>
    </div>
  </section>
</main>

""" + footer(depth=depth) + "\n</body>\n</html>"

    with open(os.path.join(OUT, ITEM_DIR, slug), "w") as f:
        f.write(page)

gloves_cat = by_slug["gloves"]
for name, desc, slug in gloves_cat["items"]:
    gallery_items = [
        (f"{name} — Front View", "glove"),
        (f"{name} — Detail", "glove"),
        (f"{name} — Packaging", "packaging"),
    ]
    product_page(gloves_cat, name, desc, gallery_items, slug)

print(f"Generated {len(gloves_cat['items'])} Gloves product pages")

packaging_cat = by_slug["packaging-materials"]
for name, desc, slug in packaging_cat["items"]:
    gallery_items = [
        (f"{name} — Sample", "packaging"),
        (f"{name} — Detail", "packaging"),
    ]
    product_page(packaging_cat, name, desc, gallery_items, slug)

print(f"Generated {len(packaging_cat['items'])} Packaging Materials product pages")

abrasives_cat = by_slug["abrasives"]
for name, desc, slug in abrasives_cat["items"]:
    gallery_items = [
        (f"{name} — Sample", "abrasive"),
        (f"{name} — Detail", "abrasive"),
    ]
    product_page(abrasives_cat, name, desc, gallery_items, slug)

print(f"Generated {len(abrasives_cat['items'])} Abrasives product pages")

steel_cat = by_slug["tubing-structural-steel"]
for name, desc, slug in steel_cat["items"]:
    gallery_items = [
        (f"{name} — Sample", "tubing"),
        (f"{name} — Detail", "tubing"),
    ]
    product_page(steel_cat, name, desc, gallery_items, slug)

print(f"Generated {len(steel_cat['items'])} Tubing & Structural Steel product pages")

# =========================================================
# 5. Generate dedicated Brands page — flat logo wall, no grouping
# =========================================================
all_brand_tiles = "\n        ".join(brand_item_html(*b) for b in BRANDS_ORDERED)

brands_page = head("Brands We Carry", f"Genuine stock from established manufacturers {COMPANY} carries — FAG, Makita, Bosch, Phelps Dodge, and more.") + "\n" + header(active="brands") + f"""

<div class="breadcrumb">
  <div class="wrap"><a href="index.html">Home</a><span class="sep">/</span><span class="current">Brands</span></div>
</div>

<section class="cat-hero" style="padding:44px 0 52px;">
  <div class="wrap">
    <span class="group-code mono">Trusted Names</span>
    <h1 style="margin-top:8px;">Brands We Carry</h1>
    <p style="color:#C7D3C9;font-size:15px;margin-top:8px;max-width:560px;">Genuine stock from established manufacturers across our product lines &mdash; not generic substitutes.</p>
  </div>
</section>

<main>
  <section>
    <div class="wrap">
      <div class="brand-wall">
        {all_brand_tiles}
      </div>

      <div class="pd-block">
        {mini_cta("a specific brand")}
      </div>
    </div>
  </section>
</main>

""" + footer() + "\n</body>\n</html>"

with open(os.path.join(OUT, "brands.html"), "w") as f:
    f.write(brands_page)

print("Generated brands.html")

# =========================================================
# 5. Generate Who We Are page
# =========================================================
value_rows = [
    ('<path d="M12 2 3 7v10l9 5 9-5V7z"/><path d="M12 22V12M3 7l9 5 9-5"/>', "Top-Quality Materials", "Genuine, dependable stock across every category we carry."),
    ('<path d="M12 2 4 6v6c0 5 3.5 8.5 8 10 4.5-1.5 8-5 8-10V6z"/>', f"Trusted Since {ESTABLISHED_YEAR}", f"{YEARS_IN_BUSINESS}+ years supplying contractors and industrial buyers."),
    ('<circle cx="12" cy="8" r="5"/><path d="M8.5 13.5 6 21l6-3 6 3-2.5-7.5"/>', "Trusted Brands", "Sumotech, Sumoweld, G-Weld, Yanase, ABC, and more."),
    ('<path d="M20 6 9 17l-5-5"/>', "Exceptional Service", "Direct, responsive support and competitive trade pricing."),
]
value_rows_html = "\n        ".join(
    f'''<div class="row"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">{path}</svg><div><div class="label">{label}</div><div class="value">{val}</div></div></div>'''
    for path, label, val in value_rows
)

about_page = head("Who We Are", f"{COMPANY} has been a trusted wholesaler and retailer of quality industrial and construction materials since {ESTABLISHED_YEAR}.") + "\n" + header(active="about") + f"""

<div class="breadcrumb">
  <div class="wrap"><a href="index.html">Home</a><span class="sep">/</span><span class="current">Who We Are</span></div>
</div>

<section class="cat-hero" style="padding:44px 0 52px;">
  <div class="wrap">
    <span class="group-code mono">Est. {ESTABLISHED_YEAR}</span>
    <h1 style="margin-top:8px;">Who We Are</h1>
    <p style="color:#C7D3C9;font-size:15px;margin-top:8px;max-width:560px;">{TAGLINE}, serving contractors, fabricators, and industrial buyers since {ESTABLISHED_YEAR}.</p>
  </div>
</section>

<main>
  <section>
    <div class="wrap about">
      <div class="about-copy">
        <span class="kicker">Our Story</span>
        <h2>Proudly Serving Since {ESTABLISHED_YEAR}</h2>
        <p>Since {ESTABLISHED_YEAR}, {COMPANY} has been serving individuals, fabricators, contractors, and industrial buyers with quality industrial and construction materials. From welding supplies and abrasives to gloves, hardware, and safety equipment, we supply businesses across the Philippines with trusted brands, reliable stock, and competitive prices &mdash; backed by service you can count on.</p>
        <p>With a dedicated team built on service, quality, and trust, {COMPANY} has grown alongside our clients who depend on us for the right materials at the right value.</p>
      </div>
      <div class="stat-plate">
        <div class="stat"><h3>{ESTABLISHED_YEAR}</h3><p>Established</p></div>
        <div class="stat"><h3>{YEARS_IN_BUSINESS}+</h3><p>Years in Business</p></div>
        <div class="stat"><h3>{len(CATEGORIES)}</h3><p>Product Categories</p></div>
        <div class="stat" style="grid-column:span 2;"><h3 style="font-size:20px;">San Juan City</h3><p>Metro Manila, PH</p></div>
      </div>
    </div>
  </section>

  <section style="padding-top:0;">
    <div class="wrap about">
      <div class="about-copy">
        <span class="kicker">What We Stand For</span>
        <h2>The commitments behind every order.</h2>
        <p>These aren't slogans &mdash; they're how we've kept contractors and industrial buyers coming back since {ESTABLISHED_YEAR}.</p>
      </div>
      <div class="contact-plate">
        {value_rows_html}
      </div>
    </div>
  </section>

  <section style="padding-top:0;">
    <div class="wrap">
      {mini_cta(heading="Want to know more, or place an order?", sub="Call, message, or email us your requirements — we'll get back with pricing and availability.")}
    </div>
  </section>
</main>

""" + footer() + "\n</body>\n</html>"

with open(os.path.join(OUT, "who-we-are.html"), "w") as f:
    f.write(about_page)

print("Generated who-we-are.html")

# =========================================================
# 7. Generate the Request a Quote page
# =========================================================
# Item list, quantities, and the contact form are all rendered client-side
# from the localStorage cart (see the "Quote cart" section of site.js) —
# Python has no way to know what's in a visitor's browser at build time.
# This is just the static shell + empty containers for that JS to fill in.
quote_page = head("Request a Quote", f"Review your requested items and send {COMPANY} a quote request.",
                   extra_head=EMAILJS_TAG) + "\n" + header(active="quote") + f"""

<div class="breadcrumb">
  <div class="wrap"><a href="index.html">Home</a><span class="sep">/</span><span class="current">Request a Quote</span></div>
</div>

<section class="cat-hero" style="padding:44px 0 52px;">
  <div class="wrap">
    <span class="group-code mono">Quote Request</span>
    <h1 style="margin-top:8px;">Request a Quote</h1>
    <p style="color:#C7D3C9;font-size:15px;margin-top:8px;max-width:560px;">Review the items you've added, tell us how to reach you, and send your request &mdash; we'll get back with pricing and availability.</p>
  </div>
</section>

<main>
  <section>
    <div class="wrap" style="max-width:760px;">

      <div id="quoteEmptyState" hidden style="text-align:center;padding:32px 0 48px;">
        <p style="color:var(--steel);font-size:15px;margin-bottom:20px;">You haven't added any items to your quote yet.</p>
        <a href="products.html" class="btn btn-primary" style="display:inline-flex;">Browse Products</a>
      </div>

      <div id="quoteSuccessState" hidden style="text-align:center;padding:32px 0 48px;">
        <div class="icon-badge" style="margin:0 auto 20px;">{icon("quote", cls="")}</div>
        <h2 style="margin-bottom:10px;">Thank you!</h2>
        <p style="color:var(--steel);font-size:15px;max-width:420px;margin:0 auto 24px;">Your request for quotation has been submitted. We'll review it and get back to you shortly with pricing and availability.</p>
        <a href="products.html" class="btn btn-primary" style="display:inline-flex;">Browse More Products</a>
      </div>

      <div id="quoteForm">
        <div class="pd-block" style="margin-top:0;">
          <h2>Your Items</h2>
          <div id="quoteItems" class="quote-items"></div>
        </div>

        <div class="pd-block">
          <h2>Your Details</h2>
          <form id="quoteContactForm" class="quote-contact-form">
            <div class="qf-row">
              <label for="qfName">Full Name*</label>
              <input type="text" id="qfName" name="name" required>
            </div>
            <div class="qf-row">
              <label for="qfCompany">Company</label>
              <input type="text" id="qfCompany" name="company">
            </div>
            <div class="qf-row">
              <label for="qfPhone">Phone / Viber</label>
              <input type="tel" id="qfPhone" name="phone">
            </div>
            <div class="qf-row">
              <label for="qfEmail">Email</label>
              <input type="email" id="qfEmail" name="email">
            </div>
            <div class="qf-row">
              <label for="qfNotes">Additional Notes</label>
              <textarea id="qfNotes" name="notes" rows="3"></textarea>
            </div>
            <p class="qf-hint">Please provide a phone number or email so we can reach you.</p>
            <button type="submit" class="btn btn-primary" id="quoteSubmitBtn">Send Quote Request</button>
            <p id="quoteStatus" class="quote-status" hidden></p>
          </form>
        </div>
      </div>

    </div>
  </section>
</main>

""" + footer() + "\n</body>\n</html>"

with open(os.path.join(OUT, "request-quote.html"), "w") as f:
    f.write(quote_page)

print("Generated request-quote.html")
