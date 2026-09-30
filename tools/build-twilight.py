#!/usr/bin/env python3
"""Regenerates the luxe-specific parts of twilight.json (settings + components).
Run: python3 tools/build-twilight.py   (keeps JSON valid; edit here, not by hand)"""
import json, uuid, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
d = json.loads((root / "twilight.json").read_text())

def sw(id, ar, en, default=True, desc=None):
    return {"type": "boolean", "icon": "sicon-toggle-off", "label": ar, "description": desc,
            "id": id, "format": "switch", "required": False, "value": default, "selected": default}

def title(id, text):
    return {"type": "static", "format": "title", "id": id, "variant": "h6",
            "value": f"<div class='rounded-lg' style='background-color:#1c1917;padding:14px;margin-bottom:16px'><h6 style='color:#fff;font-size:15px;font-weight:bold'>{text}</h6></div>"}

def text(id, label, value="", fmt="text", ml=True, maxlen=120, req=False):
    return {"type": "string", "icon": "sicon-format-text-alt", "label": label, "multilanguage": ml,
            "id": id, "value": value, "required": req, "format": fmt, "placeholder": None,
            "description": None, "minLength": 0, "maxLength": maxlen}

def image(id, label, value, w=1600, h=1000):
    return {"type": "string", "icon": "sicon-image", "label": label, "id": id, "format": "image",
            "value": value, "required": False, "description": None, "placeholder": None,
            "settings": {"width": w, "height": h}}

def color(id, label, value):
    # Only formats proven in the reference theme are used: hex typed as plain text.
    return {"type": "string", "icon": "sicon-format-text-alt", "label": label + " (HEX)", "id": id, "format": "text",
            "value": value, "required": False, "description": "مثال: " + value, "placeholder": value,
            "multilanguage": False, "minLength": 0, "maxLength": 9}

def link(id, label):
    return {"type": "items", "icon": "sicon-link", "label": label, "id": id, "value": [],
            "required": False, "format": "variable-list", "searchable": True, "source": "custom",
            "description": None,
            "sources": [{"label": l, "key": k, "value": k} for l, k in [
                ("منتج", "products"), ("تصنيف", "categories"), ("ماركة تجارية", "brands"),
                ("صفحة تعريفية", "pages"), ("التخفيضات", "offers_link"),
                ("المدونة", "blog_link"), ("رابط خارجي", "custom")]]}

def products(id, label, mx=8):
    return {"type": "items", "icon": "sicon-keyboard_arrow_down", "label": label, "id": id,
            "format": "dropdown-list", "selected": [], "options": [], "required": False,
            "multichoice": True, "source": "products", "searchable": True,
            "maxLength": mx, "minLength": 0, "value": [], "description": None}

def collection(id, item_label, value, fields, mn=1, mx=12):
    # Salla requires sub-field ids to be prefixed with the collection id ("items.image"),
    # matching the keys used in `value`; sub-field defaults live in `value`, so they are null here.
    fields = [dict(f, id=f"{id}.{f['id']}", **({"value": None} if f["type"] in ("string", "items") else {})) for f in fields]
    return {"id": id, "type": "collection", "format": "collection", "required": True,
            "minLength": mn, "maxLength": mx, "label": None, "item_label": item_label,
            "value": value, "fields": fields}

def comp(name_en, name_ar, path, icon, fields):
    return {"key": str(uuid.uuid5(uuid.NAMESPACE_URL, "luxe/" + path)),
            "title": {"en": name_en, "ar": name_ar}, "icon": icon, "path": path, "fields": fields}

IMG = "https://images.unsplash.com/photo-{}?auto=format&fit=crop&w={}&q=80"
def u(id, w=1600): return IMG.format(id, w)

# ---- settings: keep functional ones Raed's JS/Twig reads, add luxe ones ----
keep = {"header_is_sticky", "topnav_is_dark", "important_links", "enable_more_menu", "footer_is_dark",
        "product_show_breadcrumbs", "product_index_show_breadcrumbs", "enable_add_product_toast",
        "notify_when_available_in_card", "sticky_add_to_cart", "show_tags", "imageZoom",
        "is_more_button_enabled", "vertical_fixed_products"}
base = [s for s in d["settings"] if s.get("id") in keep]
for s in base:
    if s["id"] == "sticky_add_to_cart":
        s["value"] = s["selected"] = True

luxe = [
    {"type": "static", "id": "luxe-line", "format": "line"},
    title("luxe-title-colors", "الألوان — Colors"),
    color("luxe_bg", "لون الخلفية", "#f2ece1"),
    color("luxe_surface", "لون البطاقات", "#fbf8f2"),
    color("luxe_text", "لون النص", "#16120e"),
    color("luxe_muted", "لون النص الثانوي", "#6f665b"),
    color("luxe_accent", "لون التمييز (Secondary)", "#c4532d"),
    color("luxe_ink", "اللون الداكن للأقسام (Ink)", "#1e3a2f"),
    title("luxe-title-font", "الخط — Typography"),
    text("luxe_font_url", "رابط ملف خط GE SS Two (woff2) — اختياري، يتطلب ترخيصاً", "", ml=False, maxlen=400),
    sw("luxe_cursor", "مؤشر ماوس مخصص", "Custom cursor", True),
    title("luxe-title-motion", "الحركة — Animations"),
    sw("luxe_animations", "تفعيل الحركات", "Enable animations", True),
    {"id": "luxe_motion_intensity", "type": "items", "format": "dropdown-list", "label": "شدة الحركة",
     "icon": "sicon-list", "required": True, "source": "Manual", "description": None, "labelHTML": None,
     "selected": [{"label": "متوسطة (Medium)", "value": "medium", "key": "luxe-motion-medium"}],
     "options": [{"label": "خفيفة (Subtle)", "value": "subtle", "key": "luxe-motion-subtle"},
                 {"label": "متوسطة (Medium)", "value": "medium", "key": "luxe-motion-medium"},
                 {"label": "قوية (Bold)", "value": "bold", "key": "luxe-motion-bold"}]},
    sw("luxe_parallax", "تفعيل تأثير Parallax", "Enable parallax", True),
    sw("luxe_page_transition", "حركة دخول الصفحة", "Page entrance", True),
    title("luxe-title-header", "الرأس والسلة — Header & cart"),
    sw("luxe_announcement_on", "إظهار شريط الإعلان", "Announcement bar", True),
    text("luxe_announcement", "نص شريط الإعلان", "شحن مجاني للطلبات فوق 300 ر.س", maxlen=140),
    link("luxe_announcement_link", "رابط شريط الإعلان"),
    sw("luxe_cart_drawer", "استخدام درج السلة الجانبي", "Cart drawer", True),
    text("luxe_newsletter_action", "رابط نموذج النشرة (Mailchimp/Klaviyo Form Action)", "", ml=False, maxlen=300),
    text("luxe_newsletter_field", "اسم حقل البريد في النموذج", "EMAIL", ml=False, maxlen=40),
    sw("luxe_quick_view", "زر المعاينة السريعة في البطاقات", "Quick view on cards", True),
]
d["settings"] = base + luxe

# ---- components (home sections) ----
enable = sw("enabled", "إظهار القسم", "", True)
c = []

c.append(comp("Luxe Hero", "الواجهة الرئيسية (Hero)", "home.hero", "sicon-image-carousel", [
    enable,
    image("image", "صورة الواجهة (تظهر داخل قوس)", u("1441986300917-64674bd600d8", 1400), 1200, 1500),
    text("eyebrow", "عنوان صغير", "المجموعة الجديدة ٢٠٢٦"),
    text("title", "العنوان الرئيسي", "أناقة تُصنع بإتقان", maxlen=60),
    text("description", "النص التوضيحي", "قطع مختارة بعناية تجمع بين الفخامة والبساطة.", fmt="textarea", maxlen=240),
    text("cta_label", "نص الزر الأول", "تسوّق الآن", maxlen=30),
    link("cta_url", "رابط الزر الأول"),
    text("cta2_label", "نص الزر الثاني", "اكتشف القصة", maxlen=30),
    link("cta2_url", "رابط الزر الثاني"),
    text("badge", "نص الشارة الدوّارة", "توصيل مجاني • جودة مضمونة • ", maxlen=50),
    text("chip", "بطاقة عائمة", "✦ وصل حديثاً", maxlen=30),
]))

c.append(comp("Marquee", "شريط نصوص متحرك", "home.marquee", "sicon-list-play", [
    enable,
    text("text", "الكلمات (افصل بينها بـ |)", "شحن سريع | جودة فاخرة | إرجاع مجاني | تصاميم حصرية", maxlen=300),
    sw("invert", "خلفية داكنة", "", True),
]))

c.append(comp("Featured Categories", "التصنيفات المميزة", "home.featured-categories", "sicon-layout-grid-rearrange", [
    enable,
    text("title", "العنوان", "تسوّق حسب التصنيف"),
    {"id": "categories", "type": "items", "format": "dropdown-list", "label": "حدد التصنيفات",
     "icon": "sicon-keyboard_arrow_down", "selected": [], "options": [], "source": "categories",
     "multichoice": True, "searchable": True, "required": False, "labelHTML": None, "description": None,
     "maxLength": 6, "minLength": 0, "value": []},
]))

c.append(comp("Featured Products", "منتجات مميزة", "home.featured-products", "sicon-star", [
    enable,
    text("eyebrow", "عنوان صغير", "الأكثر طلباً"),
    text("title", "العنوان", "منتجات مختارة"),
    products("products", "المنتجات", 8),
    link("display_all_url", "رابط عرض الكل"),
]))

c.append(comp("Brand Story", "قصة العلامة", "home.brand-story", "sicon-image", [
    enable,
    image("image", "صورة الخلفية (Parallax)", u("1490481651871-ab68de25d43d", 2000), 2000, 1200),
    text("eyebrow", "عنوان صغير", "قصتنا"),
    text("title", "العنوان", "حرفة تتوارثها الأجيال", maxlen=100),
    text("description", "النص", "نؤمن بأن الجمال في التفاصيل. كل قطعة نقدمها تحمل قصة من الإتقان والاهتمام.", fmt="textarea", maxlen=400),
    text("cta_label", "نص الزر", "اقرأ المزيد", maxlen=30),
    link("cta_url", "رابط الزر"),
    text("stat1_value", "إحصائية ١ — رقم", "12", ml=False, maxlen=8), text("stat1_label", "إحصائية ١ — وصف", "سنة خبرة", maxlen=30),
    text("stat2_value", "إحصائية ٢ — رقم", "48", ml=False, maxlen=8), text("stat2_label", "إحصائية ٢ — وصف", "ألف عميل", maxlen=30),
    text("stat3_value", "إحصائية ٣ — رقم", "300", ml=False, maxlen=8), text("stat3_label", "إحصائية ٣ — وصف", "قطعة حصرية", maxlen=30),
]))

c.append(comp("Collection Slider", "شريط المجموعات", "home.collection-slider", "sicon-list-play", [
    enable,
    text("title", "العنوان", "المجموعات"),
    collection("items", "مجموعة", [
        {"items.image": u("1445205170230-053b83016050", 900), "items.title": "الربيع", "items.subtitle": "٢٤ قطعة"},
        {"items.image": u("1483985988355-763728e1935b", 900), "items.title": "الأساسيات", "items.subtitle": "١٢ قطعة"},
        {"items.image": u("1469334031218-e382a71b716b", 900), "items.title": "المناسبات", "items.subtitle": "١٨ قطعة"},
        {"items.image": u("1490481651871-ab68de25d43d", 900), "items.title": "الإكسسوارات", "items.subtitle": "٣٠ قطعة"},
    ], [
        image("image", "الصورة", u("1445205170230-053b83016050", 900), 900, 1200),
        text("title", "العنوان", "", maxlen=50),
        text("subtitle", "نص فرعي", "", maxlen=50),
        link("url", "الرابط"),
    ], 2, 12),
]))

c.append(comp("Luxe Testimonials", "آراء العملاء", "home.luxe-testimonials", "sicon-comment-alt-quote", [
    enable,
    text("title", "العنوان", "ماذا يقول عملاؤنا"),
    collection("items", "رأي", [
        {"items.name": "سارة", "items.role": "عميلة", "items.text": "جودة استثنائية وتغليف فاخر. تجربة شراء لا تُنسى.", "items.stars": 5},
        {"items.name": "محمد", "items.role": "عميل", "items.text": "توصيل سريع وخدمة راقية. سأكرر الطلب بالتأكيد.", "items.stars": 5},
        {"items.name": "نورة", "items.role": "عميلة", "items.text": "تصاميم أنيقة وأسعار مناسبة.", "items.stars": 4},
    ], [
        text("name", "الاسم", "", maxlen=40),
        text("role", "الصفة", "", maxlen=40),
        text("text", "الرأي", "", fmt="textarea", maxlen=240),
        {"type": "number", "icon": "sicon-star", "label": "التقييم (1-5)", "id": "stars", "format": "integer",
         "value": 5, "required": False, "description": None, "minimum": 1, "maximum": 5, "labelHTML": "من 1 إلى 5", "placeholder": "القيمة"},
    ], 1, 10),
]))

c.append(comp("Social Grid", "شبكة السوشيال / إنستغرام", "home.social-grid", "sicon-social-instagram", [
    enable,
    text("title", "العنوان", "تابعنا على إنستغرام"),
    text("handle", "اسم الحساب", "@yourstore", maxlen=40),
    link("profile_url", "رابط الحساب"),
    collection("items", "صورة", [
        {"items.image": u("1441984904996-e0b6ba687e04", 700)},
        {"items.image": u("1483985988355-763728e1935b", 700)},
        {"items.image": u("1469334031218-e382a71b716b", 700)},
        {"items.image": u("1445205170230-053b83016050", 700)},
        {"items.image": u("1490481651871-ab68de25d43d", 700)},
        {"items.image": u("1441986300917-64674bd600d8", 700)},
    ], [image("image", "الصورة", u("1441984904996-e0b6ba687e04", 700), 700, 700), link("url", "الرابط")], 3, 8),
]))

c.append(comp("Newsletter", "النشرة البريدية", "home.newsletter", "sicon-email", [
    enable,
    text("title", "العنوان", "انضم إلى قائمتنا"),
    text("description", "النص", "اشترك ليصلك كل جديد وعروض حصرية.", fmt="textarea", maxlen=200),
    image("image", "صورة جانبية", u("1441986300917-64674bd600d8", 1000), 1000, 800),
]))

d["components"] = c
d["name"] = {"ar": "لوكس", "en": "Luxe"}
d["repository"] = "https://github.com/markeradvagency-dev/salla"
d["author_name"] = "Luxe"
d["author_email"] = "askar@reachi.ai"
d["support_url"] = "https://salla.dev"
d["description"] = {"ar": "قالب فاخر بحركات سلسة وتصميم عصري", "en": "A luxury, motion-rich Salla theme"}
(root / "twilight.json").write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n")
print("components:", len(c), "settings:", len(d["settings"]))
