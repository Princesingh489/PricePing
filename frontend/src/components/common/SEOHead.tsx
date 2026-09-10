import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

interface SEOHeadProps {
  title?: string;
  description?: string;
  canonical?: string;
  robots?: string;
  ogType?: string;
  ogImage?: string;
  keywords?: string;
  structuredData?: Record<string, any> | Record<string, any>[];
}

const DEFAULT_TITLE = "Price Ping – Compare Prices & Track Products Across Stores";
const DEFAULT_DESCRIPTION =
  "Price Ping compares real-time product prices across Amazon, Flipkart, Myntra, Ajio, and Nykaa in India. Track products, explore genuine price history, and get alerts on price drops.";
const DEFAULT_IMAGE = "https://priceping.store/hero-festive.jpg";
const BASE_DOMAIN = "https://priceping.store";

export default function SEOHead({
  title = DEFAULT_TITLE,
  description = DEFAULT_DESCRIPTION,
  canonical,
  robots = "index, follow",
  ogType = "website",
  ogImage = DEFAULT_IMAGE,
  keywords,
  structuredData,
}: SEOHeadProps) {
  const location = useLocation();
  const canonicalUrl = canonical || `${BASE_DOMAIN}${location.pathname}`;

  useEffect(() => {
    // 1. Update Title
    document.title = title;

    // Helper to create or update meta tag
    const setMeta = (nameAttr: 'name' | 'property', attrValue: string, content: string) => {
      let elem = document.querySelector(`meta[${nameAttr}="${attrValue}"]`);
      if (!elem) {
        elem = document.createElement('meta');
        elem.setAttribute(nameAttr, attrValue);
        document.head.appendChild(elem);
      }
      elem.setAttribute('content', content);
    };

    // 2. Standard Meta Tags
    setMeta('name', 'description', description);
    setMeta('name', 'robots', robots);
    if (keywords) {
      setMeta('name', 'keywords', keywords);
    }

    // 3. Open Graph Tags
    setMeta('property', 'og:title', title);
    setMeta('property', 'og:description', description);
    setMeta('property', 'og:url', canonicalUrl);
    setMeta('property', 'og:type', ogType);
    setMeta('property', 'og:site_name', 'Price Ping');
    setMeta('property', 'og:image', ogImage);

    // 4. Twitter Card Tags
    setMeta('name', 'twitter:card', 'summary_large_image');
    setMeta('name', 'twitter:title', title);
    setMeta('name', 'twitter:description', description);
    setMeta('name', 'twitter:image', ogImage);
    setMeta('name', 'twitter:url', canonicalUrl);

    // 5. Canonical Link Tag
    let canonicalElem = document.querySelector('link[rel="canonical"]');
    if (!canonicalElem) {
      canonicalElem = document.createElement('link');
      canonicalElem.setAttribute('rel', 'canonical');
      document.head.appendChild(canonicalElem);
    }
    canonicalElem.setAttribute('href', canonicalUrl);

    // 6. JSON-LD Structured Data
    const SCRIPT_ID = 'seo-dynamic-structured-data';
    const oldScript = document.getElementById(SCRIPT_ID);
    if (oldScript) {
      oldScript.remove();
    }

    if (structuredData) {
      const script = document.createElement('script');
      script.id = SCRIPT_ID;
      script.type = 'application/ld+json';
      script.text = JSON.stringify(structuredData);
      document.head.appendChild(script);
    }

    return () => {
      const currentScript = document.getElementById(SCRIPT_ID);
      if (currentScript) {
        currentScript.remove();
      }
    };
  }, [title, description, canonicalUrl, robots, ogType, ogImage, keywords, structuredData]);

  return null;
}
