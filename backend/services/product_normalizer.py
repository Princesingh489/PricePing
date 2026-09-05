"""
PricePing Product Normalization Engine
======================================
Standardizes product titles, units, brand aliases, and structured attributes.
Enforces deterministic text normalization for exact cross-store identity matching.
"""
import re
from typing import Optional, Dict, Any, List, Set

# Known Brand Aliases mapping to canonical brand representations
BRAND_ALIASES: Dict[str, str] = {
    "the souled store": "the souled store",
    "tss": "the souled store",
    "the derma co": "the derma co",
    "derma co": "the derma co",
    "apple inc": "apple",
    "apple": "apple",
    "samsung electronics": "samsung",
    "samsung": "samsung",
    "oneplus technology": "oneplus",
    "1+": "oneplus",
    "oneplus": "oneplus",
    "xiaomi inc": "xiaomi",
    "mi": "xiaomi",
    "xiaomi": "xiaomi",
    "redmi": "redmi",
    "realme": "realme",
    "motorola": "motorola",
    "moto": "motorola",
    "boat lifestyle": "boat",
    "boat": "boat",
    "noise": "noise",
    "boult audio": "boult",
    "boult": "boult",
    "h&m": "h&m",
    "hennes & mauritz": "h&m",
    "levis": "levi's",
    "levi strauss": "levi's",
    "levi's": "levi's",
    "broadstar": "broadstar",
    "point cove": "point cove",
    "vaseline": "vaseline",
    "fastrack": "fastrack",
    "titan": "titan",
    "casio": "casio",
    "peter england": "peter england",
    "allen solly": "allen solly",
    "louis philippe": "louis philippe",
    "van heusen": "van heusen",
    "nike": "nike",
    "adidas": "adidas",
    "puma": "puma",
    "reebok": "reebok",
    "asics": "asics",
    "campus": "campus",
    "sparx": "sparx",
    "bata": "bata",
    "woodland": "woodland",
    "crocs": "crocs",
    "red tape": "red tape",
}

# Apparel size standardization map
APPAREL_SIZE_MAP = {
    "xxs": "xxs", "2xs": "xxs",
    "xs": "xs", "extra small": "xs",
    "s": "s", "small": "s",
    "m": "m", "medium": "m",
    "l": "l", "large": "l",
    "xl": "xl", "extra large": "xl",
    "xxl": "2xl", "2xl": "2xl", "double xl": "2xl",
    "3xl": "3xl", "xxxl": "3xl",
    "4xl": "4xl", "xxxxl": "4xl",
    "5xl": "5xl",
    "free size": "free", "free": "free", "onesize": "free", "one size": "free",
}

# Color aliases and groupings
COLOR_ALIASES = {
    "navy blue": "navy",
    "midnight blue": "navy",
    "dark blue": "navy",
    "deep blue": "navy",
    "sky blue": "light blue",
    "ice blue": "light blue",
    "baby blue": "light blue",
    "space grey": "grey",
    "space gray": "grey",
    "gray": "grey",
    "charcoal": "dark grey",
    "anthracite": "dark grey",
    "off white": "cream",
    "ivory": "cream",
    "beige": "beige",
    "khaki": "khaki",
    "olive green": "olive",
    "military green": "olive",
    "army green": "olive",
    "forest green": "dark green",
    "emerald green": "green",
    "mint green": "mint",
    "maroon": "maroon",
    "burgundy": "maroon",
    "wine": "maroon",
    "rose gold": "rose gold",
    "pitch black": "black",
    "matte black": "black",
    "jet black": "black",
    "phantom black": "black",
    "titanium black": "black",
    "pearl white": "white",
}

# Unit normalization patterns
UNIT_REPLACEMENTS = [
    (re.compile(r'\b(\d+)\s*(?:gb|gigabytes?)\b', re.I), r'\1gb'),
    (re.compile(r'\b(\d+)\s*(?:tb|terabytes?)\b', re.I), r'\1tb'),
    (re.compile(r'\b(\d+)\s*(?:mb|megabytes?)\b', re.I), r'\1mb'),
    (re.compile(r'\b(\d+)\s*(?:ml|milliliters?|millilitres?)\b', re.I), r'\1ml'),
    (re.compile(r'\b(\d+(?:\.\d+)?)\s*(?:l|liters?|litres?)\b', re.I), lambda m: f"{int(float(m.group(1)) * 1000)}ml"),
    (re.compile(r'\b(\d+(?:\.\d+)?)\s*(?:kg|kilograms?|kilos?)\b', re.I), lambda m: f"{int(float(m.group(1)) * 1000)}g"),
    (re.compile(r'\b(\d+)\s*(?:g|grams?|gms?)\b', re.I), r'\1g'),
    (re.compile(r'\bpack\s*of\s*(\d+)\b', re.I), r'pack-\1'),
    (re.compile(r'\b(\d+)\s*(?:pcs|pieces?|pack)\b', re.I), r'pack-\1'),
]


class ProductNormalizer:
    """Normalizes raw product text and extracts structured attributes."""

    @staticmethod
    def normalize_text(text: Optional[str]) -> str:
        """Lowercase, strip non-alphanumeric punctuation (keeping hyphens), normalize spaces."""
        if not text:
            return ""
        # Replace non-word chars with space except hyphens
        cleaned = re.sub(r'[^\w\s-]', ' ', text.lower())
        return " ".join(cleaned.split())

    @staticmethod
    def normalize_units(text: Optional[str]) -> str:
        """Standardize measurements and units (256 GB -> 256gb, 1 L -> 1000ml)."""
        if not text:
            return ""
        res = text
        for pat, repl in UNIT_REPLACEMENTS:
            res = pat.sub(repl, res)
        return res

    @staticmethod
    def normalize_brand(brand: Optional[str]) -> Optional[str]:
        """Map brand strings to canonical brand representations."""
        if not brand:
            return None
        norm = ProductNormalizer.normalize_text(brand)
        if norm in BRAND_ALIASES:
            return BRAND_ALIASES[norm]
        # Check sub-matches
        for alias, canon in BRAND_ALIASES.items():
            if norm == alias or norm.startswith(f"{alias} ") or norm.endswith(f" {alias}"):
                return canon
        return norm

    @staticmethod
    def normalize_color(color: Optional[str]) -> Optional[str]:
        """Map color names to canonical color strings with alias support."""
        if not color:
            return None
        norm = ProductNormalizer.normalize_text(color).strip()
        if norm in COLOR_ALIASES:
            return COLOR_ALIASES[norm]
        for alias, canon in COLOR_ALIASES.items():
            if alias in norm:
                return canon
        # Primary base colors
        for c in ["black", "white", "blue", "red", "green", "yellow", "pink", "purple",
                  "grey", "gray", "gold", "silver", "beige", "brown", "orange", "olive", "navy"]:
            if c in norm:
                return "grey" if c == "gray" else c
        return norm

    @staticmethod
    def normalize_size(size_str: Optional[str]) -> Optional[str]:
        """
        Standardize size strings to a canonical format.
        Apparel: 'XXL', '2XL' -> '2xl'; 'Small', 'S' -> 's'
        Footwear: 'UK 9', '9 UK', 'Size 9' -> 'uk 9'
        Waist: '32', '32 in', 'Size: 32' -> '32'
        """
        if not size_str:
            return None
        raw = size_str.lower().strip()
        raw = re.sub(r'[()]', '', raw).strip()

        # 1. Check apparel mapping
        if raw in APPAREL_SIZE_MAP:
            return APPAREL_SIZE_MAP[raw]
        m_app = re.search(r'\b(xxs|xs|small|medium|large|xl|xxl|2xl|3xl|4xl|5xl|free\s*size)\b', raw)
        if m_app:
            val = m_app.group(1).replace(" ", "")
            return APPAREL_SIZE_MAP.get(val, val)

        # 2. Check waist/trousers numeric size: e.g. "32", "30", "34", "36", "38"
        m_waist = re.search(r'\b(2[6-9]|3[0-9]|4[0-4])\b', raw)
        if m_waist and not any(kw in raw for kw in ["uk", "us", "eu", "yr", "year", "m", "g"]):
            return m_waist.group(1)

        # 3. Check footwear / UK numeric size: e.g. "UK 9", "9 UK", "Size 9", "9", "8.5"
        m_num = re.search(r'(?:uk\s*)?([4-9]|1[0-4])(?:\.5)?(?:\s*uk)?', raw)
        if m_num:
            val = m_num.group(1)
            if ".5" in raw:
                val += ".5"
            return f"uk {val}"

        return raw

    @staticmethod
    def normalize_storage(storage_str: Optional[str]) -> Optional[str]:
        if not storage_str:
            return None
        raw = storage_str.lower().replace(" ", "").strip()
        m = re.search(r'(16|32|64|128|256|512|1024)\s*gb|(1|2)\s*tb', raw)
        if m:
            val = m.group(0).replace(" ", "")
            return val
        return raw

    @staticmethod
    def normalize_ram(ram_str: Optional[str]) -> Optional[str]:
        if not ram_str:
            return None
        raw = ram_str.lower().replace(" ", "").strip()
        m = re.search(r'([2468]|12|16|24|32|64)\s*gb', raw)
        if m:
            return m.group(0).replace(" ", "")
        return raw

    @classmethod
    def extract_structured_attributes(
        cls,
        title: str,
        brand: Optional[str] = None,
        description: Optional[str] = None,
        variants: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Extract structured attributes using deterministic token normalization."""
        full_text = f"{title or ''} {description or ''}"
        norm_text = cls.normalize_units(cls.normalize_text(full_text))

        # Brand
        eff_brand = cls.normalize_brand(brand)
        if not eff_brand:
            for b in BRAND_ALIASES:
                if re.search(rf'\b{re.escape(b)}\b', norm_text):
                    eff_brand = BRAND_ALIASES[b]
                    break

        # Storage & RAM
        detected_storage = None
        detected_ram = None
        comb_match = re.search(r'\b([468]|12|16|24)gb\s*[/+]\s*(64|128|256|512|1024)gb\b', norm_text)
        if comb_match:
            detected_ram = f"{comb_match.group(1)}gb"
            detected_storage = f"{comb_match.group(2)}gb"
        else:
            ram_m = re.search(r'\b([2468]|12|16|24|32|64)gb\s*ram\b', norm_text)
            if ram_m:
                detected_ram = f"{ram_m.group(1)}gb"
            storage_m = re.search(r'\b(32|64|128|256|512|1024)gb\b|\b(1|2)tb\b', re.sub(r'\b\d+gb\s*ram\b', '', norm_text))
            if storage_m:
                detected_storage = storage_m.group(0)

        # Color
        detected_color = None
        for c in ["black", "white", "blue", "red", "green", "yellow", "pink", "purple",
                  "grey", "gray", "gold", "silver", "beige", "brown", "orange", "olive", "navy"]:
            if re.search(rf'\b{c}\b', norm_text):
                detected_color = cls.normalize_color(c)
                break

        # Size
        detected_size = None
        m_sz = re.search(r'(?:size|sz|waist)\s*[:=]?\s*([a-z0-9.]+)', norm_text)
        if m_sz:
            detected_size = cls.normalize_size(m_sz.group(1))
        if not detected_size:
            m_waist = re.search(r'\b(2[89]|3[0-8]|4[0-2])\b', norm_text)
            if m_waist and any(t in norm_text for t in ["pant", "trouser", "jean"]):
                detected_size = m_waist.group(1)

        # Pack / Volume
        detected_pack = None
        pack_m = re.search(r'\bpack-(\d+)\b', norm_text)
        if pack_m:
            detected_pack = int(pack_m.group(1))
        vol_m = re.search(r'\b(\d+ml)\b|\b(\d+g)\b', norm_text)
        detected_volume = vol_m.group(0) if vol_m else None

        # Category
        category = "general"
        if any(w in norm_text for w in ["shirt", "t-shirt", "tshirt", "trouser", "pant", "jeans", "dress", "kurti", "hoodie", "jacket"]):
            category = "apparel"
        elif any(w in norm_text for w in ["shoe", "shoes", "sneaker", "sneakers", "boot", "loafer", "sandal", "slipper", "clogs"]):
            category = "footwear"
        elif any(w in norm_text for w in ["phone", "smartphone", "iphone", "galaxy", "laptop", "tablet", "headphone", "earphone", "smartwatch"]):
            category = "electronics"
        elif any(w in norm_text for w in ["lotion", "serum", "cream", "shampoo", "facewash", "sunscreen", "lipstick", "perfume"]):
            category = "cosmetics"

        # Model identifier extraction
        model_code = None
        for pat in [
            r'\b(iphone\s*(?:1[1-6]|se|x[sr]?)(?:\s*(?:pro\s*max|pro|plus|mini))?)\b',
            r'\b(galaxy\s*s\d{2}(?:\s*(?:ultra|plus|\+))?)\b',
            r'\b(pixel\s*\d+[a-z]?(?:\s*pro)?)\b',
            r'\b(oneplus\s*(?:1[1-3]|[7-9]|nord(?:\s*ce)?\s*\d*[a-z]?))\b',
            r'\b(wh[- ]?1000xm[45]|wf[- ]?1000xm[45])\b',
            r'\b(rockerz\s*\d{3}[a-z]?)\b',
            r'\b(airdopes\s*\d{3}[a-z]?)\b',
            r'\b(smashic(?:\s*v\d+)?)\b',
            r'\b(air\s*max(?:\s*\d+)?)\b',
            r'\b(ultraboost(?:\s*(?:light|\d+))?)\b',
        ]:
            m = re.search(pat, norm_text)
            if m:
                model_code = re.sub(r'\s+', ' ', m.group(1)).strip()
                break

        return {
            "brand": eff_brand,
            "category": category,
            "model": model_code,
            "storage": detected_storage,
            "ram": detected_ram,
            "color": detected_color,
            "size": detected_size,
            "pack_count": detected_pack or 1,
            "volume": detected_volume,
            "normalized_title": norm_text,
        }
