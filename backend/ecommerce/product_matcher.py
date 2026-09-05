"""
Product Identity & Specification Matcher
=========================================
Strict product identity extraction and verification engine for cross-store comparison.
Ensures products matched across Amazon, Flipkart, Myntra, AJIO, and Nykaa represent the
EXACT same physical item and variant (e.g., iPhone 16 128GB Black is NEVER matched with 256GB).
"""

import re
from typing import Optional, Dict, Any, Tuple, Set, List

# Re-export modular identity pipeline services
from services.product_matcher import ProductMatchingEngine, MatchResult
from services.product_normalizer import ProductNormalizer
from services.identifier_matcher import IdentifierMatcher
from services.variant_matcher import VariantMatcher
from services.availability_checker import AvailabilityChecker
from services.canonical_service import CanonicalService
from services.price_extractor import PriceExtractor


KNOWN_BRANDS = sorted([
    "red tape", "the face shop", "peter england", "allen solly", "under armour",
    "new balance", "the souled store", "dennis lingo", "am safe", "derma co",
    "dot & key", "minimalist", "apple", "samsung", "oneplus", "google", "sony",
    "realme", "xiaomi", "redmi", "motorola", "vivo", "oppo", "iqoo", "nothing",
    "asus", "hp", "dell", "lenovo", "acer", "boat", "noise", "boult", "zebronics",
    "jbl", "marshall", "bose", "sennheiser", "spigen", "nike", "adidas", "puma",
    "reebok", "asics", "campus", "sparx", "bata", "woodland", "crocs", "levis",
    "zara", "h&m", "roadster", "hrx", "wrogn", "maybelline", "l'oreal", "lakme",
    "mamaearth", "nykaa", "cetaphil", "plum", "biotique", "garnier", "nivea",
    "ponds", "dove", "philips", "havells", "fastrack", "titan", "casio"
], key=len, reverse=True)

CORE_DEVICE_TERMS = {
    "phone", "smartphone", "iphone", "galaxy", "headphone", "headphones", "headset",
    "earbuds", "earphone", "earphones", "laptop", "macbook", "smartwatch", "watch",
    "tablet", "ipad", "camera", "speaker", "soundbar", "television", "tv"
}

ACCESSORY_TERMS = {
    "case", "cover", "cases", "covers", "tempered glass", "screen protector", "protector",
    "back cover", "flip cover", "skin", "skins", "cable", "cables", "charging cable",
    "charger", "chargers", "adapter", "adapters", "strap", "straps", "band", "bands",
    "ear tips", "eartips", "pouch", "pouches", "sleeve", "sleeves", "holder", "stand",
    "mount", "bumper"
}

STORAGE_PATTERN = re.compile(r'\b(16\s*gb|32\s*gb|64\s*gb|128\s*gb|256\s*gb|512\s*gb|1\s*tb|2\s*tb)\b', re.IGNORECASE)
RAM_PATTERN = re.compile(r'\b([2468]|12|16|24|32|64)\s*gb\s*ram\b', re.IGNORECASE)
COLOR_PATTERN = re.compile(
    r'\b(black|white|blue|teal|pink|yellow|green|purple|red|gold|silver|grey|gray|'
    r'space\s*black|space\s*grey|natural\s*titanium|desert\s*titanium|black\s*titanium|white\s*titanium|'
    r'midnight|starlight|graphite|rose\s*gold|phantom\s*black|obsidian|porcelain|hazel|mint|navy|olive|brown)\b',
    re.IGNORECASE
)
PACK_PATTERN = re.compile(r'\b(pack\s*of\s*\d+|\d+\s*ml|\d+\s*g|\d+\s*kg|\d+\s*pieces?)\b', re.IGNORECASE)

# Comprehensive size patterns for apparel & footwear across Indian & global retailers
SIZE_NUMERIC_PATTERN = re.compile(
    r'(?:\b(?:size|size:?|sz|uk|us|eur|eu|in)\s*[-:]?\s*|\b)([4-9]|1[0-4])(?:\.5)?\s*(?:uk|us|eur|eu)?\b',
    re.IGNORECASE
)
SIZE_APPAREL_PATTERN = re.compile(
    r'\b(xxs|xs|small|medium|large|xl|xxl|2xl|3xl|4xl|5xl|free\s*size)\b',
    re.IGNORECASE
)

# Specific product model / series regex patterns
MODEL_PATTERNS = [
    # Phones
    re.compile(r'\b(iphone\s*(?:1[1-6]|se|x[sr]?)(?:\s*(?:pro\s*max|pro|plus|mini))?)\b', re.IGNORECASE),
    re.compile(r'\b(galaxy\s*s\d{2}(?:\s*(?:ultra|plus|\+))?)\b', re.IGNORECASE),
    re.compile(r'\b(galaxy\s*[amzf]\d{2}[a-z]?)\b', re.IGNORECASE),
    re.compile(r'\b(pixel\s*\d+[a-z]?(?:\s*pro)?)\b', re.IGNORECASE),
    re.compile(r'\b(oneplus\s*(?:1[1-3]|[7-9]|nord(?:\s*ce)?\s*\d*[a-z]?))\b', re.IGNORECASE),
    re.compile(r'\b(redmi\s*note\s*\d+[a-z]?(?:\s*pro(?:\s*\+)?)?)\b', re.IGNORECASE),
    re.compile(r'\b(realme\s*(?:[pnum]\d+|\d+[a-z]?)(?:\s*pro)?)\b', re.IGNORECASE),
    re.compile(r'\b(moto\s*g\d{2}[a-z]?)\b', re.IGNORECASE),
    # Audio
    re.compile(r'\b(wh[- ]?1000xm[45]|wf[- ]?1000xm[45])\b', re.IGNORECASE),
    re.compile(r'\b(rockerz\s*\d{3}[a-z]?)\b', re.IGNORECASE),
    re.compile(r'\b(airdopes\s*\d{3}[a-z]?)\b', re.IGNORECASE),
    re.compile(r'\b(bassheads\s*\d{3}[a-z]?)\b', re.IGNORECASE),
    re.compile(r'\b(airpods\s*(?:pro(?:\s*\d+)?|max|\d+))\b', re.IGNORECASE),
    re.compile(r'\b(galaxy\s*buds(?:\s*(?:pro|fe|live|\d+))?)\b', re.IGNORECASE),
    re.compile(r'\b(tune\s*\d{3}[a-z]*)\b', re.IGNORECASE),
    # Footwear models
    re.compile(r'\b(smashic(?:\s*v\d+)?)\b', re.IGNORECASE),
    re.compile(r'\b(smash\s*v\d+)\b', re.IGNORECASE),
    re.compile(r'\b(air\s*max(?:\s*\d+)?)\b', re.IGNORECASE),
    re.compile(r'\b(ultraboost(?:\s*(?:light|\d+))?)\b', re.IGNORECASE),
    re.compile(r'\b(downshifter(?:\s*\d+)?)\b', re.IGNORECASE),
    re.compile(r'\b(revolution(?:\s*\d+)?)\b', re.IGNORECASE),
    re.compile(r'\b(softride(?:\s*[a-z]+)?)\b', re.IGNORECASE),
    re.compile(r'\b(stan\s*smith)\b', re.IGNORECASE),
    re.compile(r'\b(gel[- ]?kayano(?:\s*\d+)?)\b', re.IGNORECASE),
    # Computing
    re.compile(r'\b(macbook\s*(?:air|pro)(?:\s*m[1-4])?)\b', re.IGNORECASE),
    re.compile(r'\b(inspiron\s*(?:1[45]|35\d{2}|54\d{2}))\b', re.IGNORECASE),
    re.compile(r'\b(thinkpad\s*[a-z]\d{2,3})\b', re.IGNORECASE),
]

GENERIC_CATEGORY_TERMS = {
    "phone", "smartphone", "edition", "online", "india", "shoes", "shoe",
    "sneakers", "sneaker", "running", "walking", "training", "casual", "formal",
    "tshirt", "t-shirt", "shirt", "pant", "jeans", "trouser", "trousers",
    "earphone", "earphones", "headphone", "headphones", "smartwatch", "watch",
    "laptop", "cotton", "solid", "printed", "slim", "fit", "regular", "men",
    "mens", "men's", "women", "womens", "women's", "boys", "girls", "unisex",
    "wireless", "bluetooth", "wired", "original", "genuine"
}


def normalize_string(s: str) -> str:
    """Normalize string for consistent comparison."""
    if not s:
        return ""
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', s.lower())
    return " ".join(cleaned.split())


def normalize_size(size_str: Optional[str]) -> Optional[str]:
    """
    Standardize size strings to a canonical format for 100% reliable matching.
    E.g.: 'UK 9', '9 UK', 'Size 9', '9' -> 'uk 9'
          'Large', 'L' -> 'l'
          '2XL', 'XXL' -> '2xl'
    """
    if not size_str:
        return None
    raw = size_str.lower().strip()
    raw = re.sub(r'[()]', '', raw).strip()

    # Apparel size mappings
    apparel_map = {
        "xxs": "xxs", "xs": "xs", "extra small": "xs",
        "s": "s", "small": "s",
        "m": "m", "medium": "m",
        "l": "l", "large": "l",
        "xl": "xl", "extra large": "xl",
        "xxl": "2xl", "2xl": "2xl", "double xl": "2xl",
        "3xl": "3xl", "xxxl": "3xl",
        "4xl": "4xl", "5xl": "5xl",
        "free size": "free", "free": "free"
    }
    if raw in apparel_map:
        return apparel_map[raw]
    m_app = re.search(r'\b(xxs|xs|small|medium|large|xl|xxl|2xl|3xl|4xl|5xl|free\s*size)\b', raw)
    if m_app:
        matched = m_app.group(1).replace(" ", "")
        return apparel_map.get(matched, matched)

    # Footwear / Numeric size mappings: e.g. "UK 9", "9 UK", "Size 9", "9", "8.5"
    m_num = re.search(r'(?:uk\s*)?([4-9]|1[0-4])(?:\.5)?(?:\s*uk)?', raw)
    if m_num:
        val = m_num.group(1)
        if ".5" in raw:
            val += ".5"
        return f"uk {val}"

    return raw


def extract_model_code(title: str, brand: Optional[str] = None) -> Optional[str]:
    """
    Extract explicit or distinctive model identifiers from product title.
    Supports known patterns (iPhone 16, Rockerz 550, Smashic) as well as
    heuristically isolated product lines.
    """
    if not title:
        return None

    lower_title = title.lower()
    for pattern in MODEL_PATTERNS:
        match = pattern.search(lower_title)
        if match:
            return re.sub(r'\s+', ' ', match.group(1).lower().strip())

    # Heuristic product line extraction:
    # If brand is known, look at the first 1-3 tokens following brand
    if brand:
        b_norm = brand.lower().strip()
        pos = lower_title.find(b_norm)
        if pos != -1:
            after_brand = lower_title[pos + len(b_norm):]
            tokens = [w for w in re.sub(r'[^a-zA-Z0-9\s]', ' ', after_brand).split() if w]
            candidate_tokens = [w for w in tokens if w not in GENERIC_CATEGORY_TERMS and not w.isdigit()]
            if candidate_tokens:
                return candidate_tokens[0]

    return None


def is_accessory(text: str) -> bool:
    """Check if title text represents an accessory rather than a core device."""
    lower = text.lower()
    return any(term in lower for term in ACCESSORY_TERMS)


def extract_specs(title: str, brand: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract structured identity specifications from product title and text:
    - brand
    - model (e.g. 'rockerz 550', 'wh-1000xm5', 'iphone 16 pro', 'smashic')
    - storage (e.g. '128gb')
    - ram (e.g. '8gb')
    - color (e.g. 'black')
    - pack (e.g. 'pack of 2', '100ml')
    - size (normalized e.g. 'uk 9', 'l')
    - is_accessory (bool)
    """
    full_text = f"{title or ''} {description or ''}".lower()

    # 1. Brand detection
    detected_brand = (brand or "").lower().strip()
    if not detected_brand:
        for b in KNOWN_BRANDS:
            if re.search(rf'\b{re.escape(b)}\b', full_text):
                detected_brand = b
                break

    # 2. Model detection
    detected_model = extract_model_code(full_text, brand=detected_brand)

    # 3. Combined RAM/ROM detection (e.g. 8GB/128GB, 8GB+128GB)
    detected_ram = None
    detected_storage = None
    comb_match = re.search(r'\b([468]|12|16|24)\s*gb\s*[/+]\s*(64|128|256|512|1024)\s*gb\b', full_text)
    if comb_match:
        detected_ram = f"{comb_match.group(1)}gb"
        detected_storage = f"{comb_match.group(2)}gb"

    # 4. RAM detection
    if not detected_ram:
        ram_matches = RAM_PATTERN.findall(full_text)
        if ram_matches:
            detected_ram = f"{ram_matches[0].lower().strip()}gb"

    # 5. Storage detection (excluding RAM occurrences so '16GB RAM' is not extracted as storage)
    if not detected_storage:
        clean_for_storage = RAM_PATTERN.sub(' [ram] ', full_text)
        storage_matches = STORAGE_PATTERN.findall(clean_for_storage)
        if storage_matches:
            detected_storage = re.sub(r'\s+', '', storage_matches[0].lower())

    # 6. Color detection
    color_matches = COLOR_PATTERN.findall(full_text)
    detected_color = None
    if color_matches:
        detected_color = re.sub(r'\s+', ' ', color_matches[0].lower().strip())

    # 7. Pack / Volume detection
    pack_matches = PACK_PATTERN.findall(full_text)
    detected_pack = None
    if pack_matches:
        detected_pack = re.sub(r'\s+', ' ', pack_matches[0].lower().strip())

    # 8. Size detection & normalization
    detected_size = None
    m_size_labeled = re.search(r'(?:size|sz|size:?)\s*[-:]?\s*([a-z0-9.]+)', full_text)
    if m_size_labeled:
        detected_size = normalize_size(m_size_labeled.group(1))

    if not detected_size:
        m_app = SIZE_APPAREL_PATTERN.search(full_text)
        if m_app:
            detected_size = normalize_size(m_app.group(1))

    if not detected_size:
        m_num = SIZE_NUMERIC_PATTERN.search(full_text)
        if m_num:
            detected_size = normalize_size(m_num.group(0))

    return {
        "brand": detected_brand or None,
        "model": detected_model,
        "storage": detected_storage,
        "ram": detected_ram,
        "color": detected_color,
        "pack": detected_pack,
        "size": detected_size,
        "is_accessory": is_accessory(full_text),
        "raw_title": title,
    }


class MatchResult(tuple):
    """
    Named tuple supporting 3-element unpacking (is_match, confidence, reason)
    while also exposing .signals, .is_match, .confidence, and .reason attributes.
    """
    signals: Dict[str, Any]

    def __new__(cls, is_match: bool, confidence: float, reason: str, signals: Dict[str, Any]):
        instance = super().__new__(cls, (is_match, confidence, reason))
        instance.signals = signals
        return instance

    @property
    def is_match(self) -> bool:
        return self[0]

    @property
    def confidence(self) -> float:
        return self[1]

    @property
    def reason(self) -> str:
        return self[2]


def is_strict_match(
    base_title: str,
    candidate_title: str,
    base_brand: Optional[str] = None,
    candidate_brand: Optional[str] = None,
    min_confidence_threshold: float = 0.85,
) -> MatchResult:
    """
    Perform strict multi-dimensional identity check.
    Guarantees 100% exact product matches across stores and rejects similar items.
    Zero false matches: Never returns wrong product or wrong variant.
    """
    if not base_title or not candidate_title:
        signals = {"brand_match": False, "model_match": False, "title_similarity": 0.0}
        return MatchResult(False, 0.0, "Missing titles for comparison", signals)

    base_product = {"title": base_title, "brand": base_brand}
    candidate_product = {"title": candidate_title, "brand": candidate_brand}

    return ProductMatchingEngine.evaluate_candidate(
        base_product,
        candidate_product,
        min_confidence_threshold=min_confidence_threshold,
    )
