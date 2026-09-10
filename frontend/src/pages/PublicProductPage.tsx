import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { ChevronRight, Home, AlertCircle, ShoppingBag } from 'lucide-react';
import SEOHead from '../components/common/SEOHead';
import PricePingProductView from '../components/product/PricePingProductView';
import { ProductCardSkeleton } from '../components/common/SkeletonLoader';
import type { Product, StoreOffer, RealPriceStatistics, RealPriceHistoryPoint } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://65.0.199.91:8000';

interface PublicProductResponse {
  product: Product;
  cross_store_offers: StoreOffer[];
  statistics: RealPriceStatistics | null;
  price_history: RealPriceHistoryPoint[];
  canonical_url: string;
  meta_title: string;
  meta_description: string;
}

export default function PublicProductPage() {
  const { slug } = useParams<{ slug: string }>();
  const [data, setData] = useState<PublicProductResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!slug) return;
    let isMounted = true;
    setLoading(true);
    setError(null);

    axios
      .get<PublicProductResponse>(`${API_BASE_URL}/api/products/public/${encodeURIComponent(slug)}`, {
        timeout: 12000,
      })
      .then((res) => {
        if (isMounted) {
          setData(res.data);
        }
      })
      .catch((err) => {
        if (isMounted) {
          console.error('Public product load error:', err);
          setError(
            err.response?.status === 404
              ? 'We could not find this product in the Price Ping database.'
              : 'Unable to load real-time product details. Please try again in a moment.'
          );
        }
      })
      .finally(() => {
        if (isMounted) {
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [slug]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#07090e] text-white pt-24 pb-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="flex items-center gap-2 mb-6">
          <div className="h-4 w-24 bg-white/10 rounded animate-pulse" />
          <div className="h-4 w-4 bg-white/10 rounded animate-pulse" />
          <div className="h-4 w-32 bg-white/10 rounded animate-pulse" />
        </div>
        <ProductCardSkeleton />
      </div>
    );
  }

  if (error || !data || !data.product) {
    return (
      <div className="min-h-[70vh] bg-[#07090e] text-white pt-28 pb-16 px-4 flex items-center justify-center">
        <SEOHead
          title="Product Not Found – Price Ping"
          description="The requested product could not be found. Compare real prices across Amazon, Flipkart, Myntra, Ajio, and Nykaa on Price Ping."
          robots="noindex, nofollow"
        />
        <div className="max-w-md w-full text-center space-y-6 bg-white/[0.03] border border-white/10 p-8 rounded-3xl">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
            <AlertCircle className="w-8 h-8" />
          </div>
          <div className="space-y-2">
            <h1 className="text-xl font-bold text-white">Product Not Found</h1>
            <p className="text-sm text-slate-400">
              {error || 'This product is not currently listed or may have been renamed.'}
            </p>
          </div>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link
              to="/"
              className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm transition-all inline-flex items-center justify-center gap-2"
            >
              <Home className="w-4 h-4" /> Go to Price Ping Home
            </Link>
            <Link
              to="/deals"
              className="px-5 py-2.5 rounded-xl bg-white/10 hover:bg-white/15 text-white font-semibold text-sm transition-all inline-flex items-center justify-center gap-2"
            >
              <ShoppingBag className="w-4 h-4" /> Browse Live Deals
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const { product, cross_store_offers, statistics, price_history, canonical_url, meta_title, meta_description } = data;
  const canonicalPath = canonical_url || `https://priceping.store/product/${slug}`;
  const categoryName = product.category || 'Electronics';
  const categorySlug = categoryName.toLowerCase().replace(/[^a-z0-9]+/g, '-');
  const isProductInStock = product.in_stock ?? (product.availability === 'in_stock');

  // Schema.org BreadcrumbList
  const breadcrumbSchema = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      {
        '@type': 'ListItem',
        position: 1,
        name: 'Home',
        item: 'https://priceping.store/',
      },
      {
        '@type': 'ListItem',
        position: 2,
        name: categoryName,
        item: `https://priceping.store/category/${categorySlug}`,
      },
      {
        '@type': 'ListItem',
        position: 3,
        name: product.product_name,
        item: canonicalPath,
      },
    ],
  };

  // Schema.org Product (Aggregator / Comparison format - Price Ping is never marked as the seller)
  const offersList = (cross_store_offers && cross_store_offers.length > 0 ? cross_store_offers : [
    {
      store: product.platform,
      price: product.current_price,
      product_url: product.product_url,
      availability: isProductInStock ? 'InStock' : 'OutOfStock',
    }
  ]).map((o: any) => ({
    '@type': 'Offer',
    price: o.price,
    priceCurrency: 'INR',
    seller: {
      '@type': 'Organization',
      name: o.store || product.platform,
    },
    url: o.product_url || product.product_url,
    itemCondition: 'https://schema.org/NewCondition',
    availability: (o.availability === 'out_of_stock' || !isProductInStock)
      ? 'https://schema.org/OutOfStock'
      : 'https://schema.org/InStock',
    priceValidUntil: new Date(Date.now() + 86400000 * 7).toISOString().split('T')[0],
  }));

  const productSchema: Record<string, any> = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: product.product_name,
    image: product.product_image ? [product.product_image] : undefined,
    description: `Compare real prices for ${product.product_name} across Amazon, Flipkart, Myntra, Ajio, and Nykaa on Price Ping. Track price history and get alerts on price drops.`,
    url: canonicalPath,
    offers: offersList.length > 1
      ? {
          '@type': 'AggregateOffer',
          priceCurrency: 'INR',
          lowPrice: statistics?.lowest_price || product.current_price,
          highPrice: statistics?.highest_price || product.original_price || product.current_price,
          offerCount: offersList.length,
          offers: offersList,
        }
      : offersList[0],
  };

  // ONLY include rating & review count if legitimately sourced
  const legitimateReviews = product.review_count || product.rating_count;
  if (product.rating && Number(product.rating) > 0 && legitimateReviews && Number(legitimateReviews) > 0) {
    productSchema.aggregateRating = {
      '@type': 'AggregateRating',
      ratingValue: Number(product.rating).toFixed(1),
      reviewCount: Number(legitimateReviews),
      bestRating: '5',
      worstRating: '1',
    };
  }

  return (
    <>
      <SEOHead
        title={meta_title || `${product.product_name} Price Comparison & Tracking – Price Ping`}
        description={meta_description || `Compare ${product.product_name} prices across Amazon, Flipkart, Myntra, Ajio, and Nykaa with Price Ping. Current best price: ₹${product.current_price}.`}
        canonical={canonicalPath}
        ogType="product"
        ogImage={product.product_image}
        structuredData={[breadcrumbSchema, productSchema]}
      />

      <div className="min-h-screen bg-[#07090e] text-white pt-24 pb-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Breadcrumb Navigation */}
          <nav aria-label="Breadcrumb" className="mb-6 flex items-center gap-2 text-xs text-slate-400 overflow-x-auto whitespace-nowrap py-1">
            <Link to="/" className="flex items-center gap-1 hover:text-white transition-colors">
              <Home className="w-3.5 h-3.5" />
              <span>Price Ping</span>
            </Link>
            <ChevronRight className="w-3.5 h-3.5 text-slate-600 shrink-0" />
            <Link to="/categories" className="hover:text-white transition-colors">
              Categories
            </Link>
            <ChevronRight className="w-3.5 h-3.5 text-slate-600 shrink-0" />
            <Link to={`/category/${categorySlug}`} className="hover:text-white transition-colors">
              {categoryName}
            </Link>
            <ChevronRight className="w-3.5 h-3.5 text-slate-600 shrink-0" />
            <span className="text-slate-200 font-medium truncate max-w-xs sm:max-w-sm" title={product.product_name}>
              {product.product_name}
            </span>
          </nav>

          {/* Product View with Store Comparison & Honest Price History */}
          <PricePingProductView
            product={product}
            crossStoreOffers={cross_store_offers}
            statistics={statistics}
            historyPoints={price_history}
            coverageLabel={
              price_history && price_history.length >= 2
                ? `${price_history.length} verified price observations recorded by Price Ping.`
                : 'Initial observation recorded. Price history updates as ongoing store checks continue.'
            }
          />

          {/* Transparent E-E-A-T Guarantee Footnote */}
          <div className="mt-12 p-6 rounded-3xl bg-white/[0.02] border border-white/5 text-xs text-slate-400 space-y-2">
            <p className="font-semibold text-slate-300">
              ℹ️ Price Ping Verified Aggregator Disclosure:
            </p>
            <p className="leading-relaxed">
              Price Ping is an independent price comparison search engine and tracking tool. All product names, logos,
              and brands are property of their respective owners (Amazon, Flipkart, Myntra, Ajio, Nykaa). Prices and
              availability are collected directly from publicly accessible merchant pages and are subject to change by
              the merchant at any time. Price Ping never manufactures, sells, or ships products directly, and does not
              fabricate discounts or synthetic price history.
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
