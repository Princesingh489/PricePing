import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import SEOHead from '../components/common/SEOHead';
import { CATEGORIES_DATA } from './CategoriesPage';
import { ExternalLink, ArrowRight, Tag } from 'lucide-react';
import { formatINR } from '../utils/helpers';
import api from '../services/api';

export default function CategoryDetailPage() {
  const { category } = useParams<{ category: string }>();
  const [deals, setDeals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const matchedCat = CATEGORIES_DATA.find((c) => c.slug === category?.toLowerCase()) || {
    slug: category || 'products',
    name: (category ? category.charAt(0).toUpperCase() + category.slice(1) : 'Products'),
    description: `Compare prices on top ${category} across Amazon India, Flipkart, Myntra, Ajio, and Nykaa.`,
    popularItems: [],
  };

  useEffect(() => {
    const fetchCategoryDeals = async () => {
      setLoading(true);
      try {
        const res = await api.get(`/api/trending-deals?category=${encodeURIComponent(matchedCat.name)}`);
        if (res.data?.deals?.length > 0) {
          setDeals(res.data.deals);
        } else {
          // Fallback: fetch all deals and filter
          const allRes = await api.get('/api/trending-deals');
          const all = allRes.data?.deals || [];
          const filtered = all.filter((d: any) =>
            (d.category && d.category.toLowerCase().includes(matchedCat.slug.toLowerCase())) ||
            (d.title && matchedCat.popularItems.some((item) => d.title.toLowerCase().includes(item.toLowerCase())))
          );
          setDeals(filtered.length > 0 ? filtered : all.slice(0, 6));
        }
      } catch {
        setDeals([]);
      } finally {
        setLoading(false);
      }
    };
    fetchCategoryDeals();
  }, [category, matchedCat.name, matchedCat.slug]);

  const breadcrumbSchema = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {
        "@type": "ListItem",
        "position": 1,
        "name": "Home",
        "item": "https://priceping.store/"
      },
      {
        "@type": "ListItem",
        "position": 2,
        "name": "Categories",
        "item": "https://priceping.store/categories"
      },
      {
        "@type": "ListItem",
        "position": 3,
        "name": matchedCat.name,
        "item": `https://priceping.store/category/${matchedCat.slug}`
      }
    ]
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-10">
      <SEOHead
        title={`Compare ${matchedCat.name} Prices in India – Price Ping`}
        description={`Find the lowest prices and best verified deals on ${matchedCat.name} across Amazon, Flipkart, Myntra, Ajio, and Nykaa with Price Ping.`}
        canonical={`https://priceping.store/category/${matchedCat.slug}`}
        keywords={`compare ${matchedCat.name}, ${matchedCat.slug} price tracker, lowest price ${matchedCat.name}, Price Ping ${matchedCat.slug}`}
        structuredData={breadcrumbSchema}
      />

      {/* Breadcrumbs */}
      <nav aria-label="Breadcrumb" className="text-xs text-slate-500 flex items-center gap-2">
        <Link to="/" className="hover:text-indigo-600 transition-colors">Home</Link>
        <span>/</span>
        <Link to="/categories" className="hover:text-indigo-600 transition-colors">Categories</Link>
        <span>/</span>
        <span className="text-slate-800 font-semibold">{matchedCat.name}</span>
      </nav>

      {/* Category Header */}
      <div className="space-y-3">
        <h1 className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight">
          Compare {matchedCat.name} Prices Across Stores
        </h1>
        <p className="text-slate-600 text-sm sm:text-base max-w-3xl leading-relaxed">
          {matchedCat.description} Real-time price verification directly from <strong>Amazon India, Flipkart, Myntra, Ajio, and Nykaa</strong>.
        </p>
      </div>

      {/* Deals / Products Grid */}
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((n) => (
            <div key={n} className="bg-white rounded-3xl p-6 border border-slate-200 animate-pulse h-80 space-y-4">
              <div className="bg-slate-100 h-44 rounded-2xl w-full" />
              <div className="bg-slate-100 h-4 rounded w-3/4" />
              <div className="bg-slate-100 h-6 rounded w-1/2" />
            </div>
          ))}
        </div>
      ) : deals.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {deals.map((deal) => {
            const slug = deal.title
              .toLowerCase()
              .replace(/[^a-z0-9]+/g, '-')
              .replace(/^-|-$/g, '');
            return (
              <div
                key={deal.deal_key || deal.id || deal.title}
                className="group bg-white rounded-3xl p-5 border border-slate-200 shadow-sm hover:shadow-md transition-all flex flex-col justify-between space-y-4"
              >
                <div className="space-y-3">
                  <div className="relative aspect-square w-full rounded-2xl overflow-hidden bg-slate-50 flex items-center justify-center p-4">
                    <img
                      src={deal.image_url}
                      alt={`${deal.title} price comparison`}
                      className="max-h-full max-w-full object-contain group-hover:scale-105 transition-transform duration-300"
                      loading="lazy"
                    />
                    <div className="absolute top-2.5 left-2.5 px-2.5 py-1 rounded-full text-[10px] font-black uppercase bg-slate-900 text-white tracking-wider">
                      {deal.store}
                    </div>
                    {deal.discount_percent > 0 && (
                      <div className="absolute top-2.5 right-2.5 px-2 py-1 rounded-full text-[10px] font-black bg-emerald-500 text-white">
                        {deal.discount_percent}% OFF
                      </div>
                    )}
                  </div>

                  <h2 className="text-sm font-bold text-slate-900 line-clamp-2 leading-snug">
                    {deal.title}
                  </h2>

                  <div className="flex items-baseline gap-2">
                    <span className="text-lg font-black text-slate-900">
                      {formatINR(deal.price)}
                    </span>
                    {deal.mrp > deal.price && (
                      <span className="text-xs text-slate-400 line-through">
                        {formatINR(deal.mrp)}
                      </span>
                    )}
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
                  <Link
                    to={`/product/${slug}`}
                    className="flex-1 py-2 px-3 rounded-xl bg-indigo-50 text-indigo-700 hover:bg-indigo-100 text-xs font-bold text-center transition-colors"
                  >
                    Compare Stores
                  </Link>
                  <a
                    href={deal.product_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 rounded-xl bg-slate-100 text-slate-700 hover:bg-slate-200 transition-colors"
                    aria-label={`Visit ${deal.store}`}
                  >
                    <ExternalLink className="w-4 h-4" />
                  </a>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="bg-slate-50 rounded-3xl p-10 text-center space-y-4 border border-slate-200">
          <Tag className="w-10 h-10 text-slate-400 mx-auto" />
          <h3 className="text-base font-bold text-slate-800">No active deals found in this category</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            You can still paste any product URL from Amazon, Flipkart, Myntra, Ajio, or Nykaa to track it instantly on Price Ping.
          </p>
          <Link
            to="/"
            className="inline-flex items-center gap-1.5 px-5 py-2.5 rounded-full bg-indigo-600 text-white text-xs font-bold hover:bg-indigo-700"
          >
            Paste Product URL <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      )}

      {/* Internal Linking to other categories */}
      <div className="pt-8 border-t border-slate-200 space-y-4">
        <h3 className="text-sm font-bold text-slate-900">Explore Other Categories:</h3>
        <div className="flex flex-wrap gap-2">
          {CATEGORIES_DATA.filter((c) => c.slug !== matchedCat.slug).map((c) => (
            <Link
              key={c.slug}
              to={`/category/${c.slug}`}
              className="px-3.5 py-1.5 rounded-xl bg-white border border-slate-200 text-xs font-semibold text-slate-700 hover:border-indigo-400 hover:text-indigo-600 transition-all shadow-sm"
            >
              {c.name}
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
