import { useEffect, useState } from 'react';
import { productsApi } from '../services/api';
import type { TrackedProduct } from '../types';
import PriceHistoryChart from '../components/charts/PriceHistoryChart';
import { LineChart, PlusCircle } from 'lucide-react';
import { Link } from 'react-router-dom';
import EmptyState from '../components/common/EmptyState';

export default function PriceHistoryPage() {
  const [products, setProducts] = useState<TrackedProduct[]>([]);
  const [selectedProductId, setSelectedProductId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    productsApi.list()
      .then((res) => {
        const list = res.data || [];
        setProducts(list);
        if (list.length > 0) {
          setSelectedProductId(list[0].id);
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const selectedTracker = products.find((p) => p.id === selectedProductId) || products[0];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-indigo-600 font-extrabold text-xs uppercase tracking-wider mb-1">
            <LineChart className="w-4 h-4" />
            <span>Price Intelligence</span>
          </div>
          <h1 className="text-3xl font-black text-navy-900 tracking-tight">Price History Analytics</h1>
          <p className="text-gray-500 text-sm mt-1">
            Historical price trends and buying opportunities for your tracked products
          </p>
        </div>

        <Link to="/add-product" className="btn-primary flex items-center gap-2 w-fit">
          <PlusCircle className="w-4 h-4" />
          <span>Track New Product</span>
        </Link>
      </div>

      {/* Product Selector Bar */}
      {products.length > 1 && (
        <div className="flex items-center gap-3 overflow-x-auto pb-2">
          {products.map((item) => {
            const isSelected = item.id === selectedProductId;
            return (
              <button
                key={item.id}
                onClick={() => setSelectedProductId(item.id)}
                className={`p-3 rounded-2xl border text-left flex items-center gap-3 flex-shrink-0 transition-all cursor-pointer ${
                  isSelected
                    ? 'border-indigo-600 bg-white shadow-sm ring-2 ring-indigo-500/20'
                    : 'border-gray-200 bg-gray-50/70 hover:bg-white text-gray-700'
                }`}
              >
                <img
                  src={item.product.product_image || 'https://placehold.co/40x40/f8fafc/6366f1?text=Product'}
                  alt=""
                  className="w-8 h-8 rounded-lg object-contain bg-white border border-gray-200 p-0.5 flex-shrink-0"
                />
                <span className="text-xs font-bold text-navy-900 max-w-[160px] truncate">
                  {item.product.product_name}
                </span>
              </button>
            );
          })}
        </div>
      )}

      {/* Main Chart Section */}
      {loading ? (
        <div className="card p-8 h-96 skeleton" />
      ) : !selectedTracker ? (
        <EmptyState
          icon={LineChart}
          title="No price history tracked yet"
          description="Add a product link to start building historical price charts and trend insights."
          actionText="Track a Product"
          actionHref="/add-product"
        />
      ) : (
        <PriceHistoryChart product={selectedTracker.product} />
      )}
    </div>
  );
}
