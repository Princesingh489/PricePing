import { Link } from 'react-router-dom';
import SEOHead from '../components/common/SEOHead';
import TrendingDealsSection from '../components/TrendingDealsSection';
import { Sparkles } from 'lucide-react';

export default function DealsPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <SEOHead
        title="Trending Deals Across Stores – Real Discounts on Price Ping"
        description="Browse verified real-time deals across Amazon India, Flipkart, Myntra, Ajio, and Nykaa on Price Ping. Genuine discount percentages and authenticated product offers."
        canonical="https://priceping.store/deals"
        keywords="Price Ping deals, trending deals India, Amazon discounts, Flipkart deals, Myntra sales, real price drops"
      />

      {/* Breadcrumb Navigation */}
      <nav aria-label="Breadcrumb" className="text-xs text-slate-500 flex items-center gap-2">
        <Link to="/" className="hover:text-indigo-600 transition-colors">Home</Link>
        <span>/</span>
        <span className="text-slate-800 font-semibold">Trending Deals</span>
      </nav>

      <div className="space-y-2">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-50 border border-rose-200 text-rose-700 text-xs font-bold">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Real-Time Store Deals</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight">
          Trending Deals Across Stores
        </h1>
        <p className="text-slate-600 text-sm sm:text-base max-w-3xl leading-relaxed">
          Every deal listed on <strong>Price Ping</strong> is dynamically verified for real stock and genuine discount rates across <strong>Amazon India, Flipkart, Myntra, Ajio, and Nykaa</strong>.
        </p>
      </div>

      <TrendingDealsSection />
    </div>
  );
}
