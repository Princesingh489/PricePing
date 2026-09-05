import { Link } from 'react-router-dom';
import { PlusCircle, ShieldCheck } from 'lucide-react';

const STORES = [
  {
    id: 'amazon',
    name: 'Amazon India',
    domain: 'amazon.in',
    badge: 'badge-amazon',
    categories: 'Electronics, Mobiles, Home, Fashion',
    color: 'text-orange-600',
    bg: 'bg-orange-50 border-orange-200',
    logoLetter: 'A',
  },
  {
    id: 'flipkart',
    name: 'Flipkart',
    domain: 'flipkart.com',
    badge: 'badge-flipkart',
    categories: 'Electronics, Appliances, Fashion',
    color: 'text-blue-600',
    bg: 'bg-blue-50 border-blue-200',
    logoLetter: 'F',
  },
  {
    id: 'ajio',
    name: 'AJIO',
    domain: 'ajio.com',
    badge: 'badge-ajio',
    categories: 'Trendy Fashion, Footwear, Luxury',
    color: 'text-rose-600',
    bg: 'bg-rose-50 border-rose-200',
    logoLetter: 'Aj',
  },
  {
    id: 'myntra',
    name: 'Myntra',
    domain: 'myntra.com',
    badge: 'badge-myntra',
    categories: 'Apparel, Beauty, Shoes, Lifestyle',
    color: 'text-pink-600',
    bg: 'bg-pink-50 border-pink-200',
    logoLetter: 'M',
  },
  {
    id: 'nykaa',
    name: 'Nykaa',
    domain: 'nykaa.com',
    badge: 'badge-nykaa',
    categories: 'Cosmetics, Skincare, Fragrances',
    color: 'text-fuchsia-600',
    bg: 'bg-fuchsia-50 border-fuchsia-200',
    logoLetter: 'N',
  },
];

export default function SupportedStores() {
  return (
    <section className="py-16 sm:py-20 bg-white border-b border-gray-200/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <span className="text-xs font-black uppercase tracking-wider text-indigo-600 bg-indigo-50 px-3 py-1 rounded-full border border-indigo-100">
            Supported Stores
          </span>
          <h2 className="text-3xl sm:text-4xl font-black text-navy-900 tracking-tight mt-3">
            Track products from your favorite stores
          </h2>
          <p className="text-gray-500 text-sm sm:text-base mt-2">
            Seamless real-time integration with India's most popular shopping websites.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-5">
          {STORES.map((store) => (
            <div
              key={store.id}
              className="card p-6 flex flex-col justify-between hover:border-indigo-300 hover:shadow-card-hover transition-all duration-300 group text-center sm:text-left"
            >
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className={`w-12 h-12 rounded-2xl ${store.bg} ${store.color} flex items-center justify-center font-black text-lg shadow-xs group-hover:scale-110 transition-transform`}>
                    {store.logoLetter}
                  </div>
                  <span className="badge badge-success text-[10px]">
                    <ShieldCheck className="w-3 h-3" /> Supported
                  </span>
                </div>

                <h3 className="text-lg font-black text-navy-900 group-hover:text-indigo-600 transition-colors">
                  {store.name}
                </h3>
                <p className="text-xs text-gray-400 mt-0.5">{store.domain}</p>

                <p className="text-xs text-gray-500 mt-3 line-clamp-2">
                  {store.categories}
                </p>
              </div>

              <div className="pt-6 mt-6 border-t border-gray-100">
                <Link
                  to="/add-product"
                  className="btn-secondary w-full text-xs py-2 group-hover:border-indigo-300 group-hover:bg-indigo-50 group-hover:text-indigo-700"
                >
                  <PlusCircle className="w-3.5 h-3.5" />
                  Track Products
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
