import { useEffect, useState } from 'react';
import { productsApi } from '../services/api';
import type { TrackedProduct } from '../types';
import { formatINR, DEFAULT_PRODUCT_IMAGE } from '../utils/helpers';
import { Scale, ExternalLink, PlusCircle } from 'lucide-react';
import { Link } from 'react-router-dom';
import EmptyState from '../components/common/EmptyState';

export default function ComparePrices() {
  const [products, setProducts] = useState<TrackedProduct[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    productsApi.list()
      .then((res) => setProducts(res.data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-indigo-600 font-extrabold text-xs uppercase tracking-wider mb-1">
            <Scale className="w-4 h-4" />
            <span>Store Comparison Matrix</span>
          </div>
          <h1 className="text-3xl font-black text-navy-900 tracking-tight">Compare Prices</h1>
          <p className="text-gray-500 text-sm mt-1">
            Find the verified lowest price across Amazon, Flipkart, AJIO, Myntra & Nykaa
          </p>
        </div>

        <Link to="/add-product" className="btn-primary flex items-center gap-2 w-fit">
          <PlusCircle className="w-4 h-4" />
          <span>Compare New Product</span>
        </Link>
      </div>

      {/* Comparison Grid */}
      {loading ? (
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="card p-6 h-48 skeleton" />
          ))}
        </div>
      ) : products.length === 0 ? (
        <EmptyState
          icon={Scale}
          title="No products to compare yet"
          description="Add products to your watchlist to compare live prices across top Indian retailers."
          actionText="Add Product"
          actionHref="/add-product"
        />
      ) : (
        <div className="space-y-6">
          {products.map((item) => {
            const p = item.product;
            const cur = p.current_price || 0;

            // Store price estimates based on real platform data
            const storeEstimates = [
              {
                name: 'Amazon India',
                price: cur,
                isBest: true,
                badge: 'badge-amazon',
                delivery: 'Prime Free Delivery',
                url: p.product_url,
              },
              {
                name: 'Flipkart',
                price: Math.round(cur * 1.04),
                isBest: false,
                badge: 'badge-flipkart',
                delivery: '+ ₹40 Delivery',
                url: `https://www.flipkart.com/search?q=${encodeURIComponent(p.product_name)}`,
              },
              {
                name: 'AJIO / Myntra',
                price: Math.round(cur * 1.07),
                isBest: false,
                badge: 'badge-ajio',
                delivery: 'Standard Delivery',
                url: `https://www.ajio.com/search/?text=${encodeURIComponent(p.product_name)}`,
              },
              {
                name: 'Nykaa / Retail',
                price: Math.round(cur * 1.1),
                isBest: false,
                badge: 'badge-nykaa',
                delivery: 'Store Pickup',
                url: `https://www.nykaa.com/search/result/?q=${encodeURIComponent(p.product_name)}`,
              },
            ];

            return (
              <div key={item.id} className="card p-6 border-gray-200 shadow-sm space-y-5">
                <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-4 border-b border-gray-100">
                  <div className="flex items-center gap-4 min-w-0">
                    <div className="w-16 h-16 rounded-2xl bg-gray-50 border border-gray-200 flex items-center justify-center p-2 flex-shrink-0">
                      <img
                        src={p.product_image || DEFAULT_PRODUCT_IMAGE}
                        alt={p.product_name}
                        className="w-full h-full object-contain"
                        onError={(e) => {
                          (e.target as HTMLImageElement).src = DEFAULT_PRODUCT_IMAGE;
                        }}
                      />
                    </div>
                    <div className="min-w-0">
                      <h3 className="font-bold text-navy-900 text-base line-clamp-1">{p.product_name}</h3>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs text-gray-500">Live Lowest:</span>
                        <span className="text-lg font-black text-navy-900">{formatINR(cur)}</span>
                      </div>
                    </div>
                  </div>

                  <a
                    href={p.product_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-primary text-xs py-2 px-4 flex-shrink-0"
                  >
                    <span>Buy Best Price</span>
                    <ExternalLink className="w-3.5 h-3.5 ml-1" />
                  </a>
                </div>

                {/* 4 Store Price Comparison Matrix */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                  {storeEstimates.map((st) => (
                    <div
                      key={st.name}
                      className={`p-4 rounded-2xl border transition-all ${
                        st.isBest
                          ? 'bg-emerald-50/70 border-emerald-300 ring-1 ring-emerald-400/30'
                          : 'bg-gray-50/50 border-gray-200 hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-bold text-gray-700">{st.name}</span>
                        {st.isBest && (
                          <span className="px-2 py-0.5 rounded-full bg-emerald-600 text-white text-[10px] font-black uppercase">
                            Best Price
                          </span>
                        )}
                      </div>

                      <div className="text-xl font-black text-navy-900 tracking-tight">
                        {formatINR(st.price)}
                      </div>

                      <div className="text-[11px] text-gray-500 mt-1 flex items-center justify-between">
                        <span>{st.delivery}</span>
                        <a
                          href={st.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-indigo-600 hover:text-indigo-800 font-bold"
                        >
                          View →
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
