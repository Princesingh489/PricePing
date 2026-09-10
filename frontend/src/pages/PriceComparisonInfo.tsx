import { Link } from 'react-router-dom';
import SEOHead from '../components/common/SEOHead';
import { Scale, ArrowRight, Store, TrendingDown, Layers } from 'lucide-react';

export default function PriceComparisonInfo() {
  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-12">
      <SEOHead
        title="Price Comparison India – Compare Amazon, Flipkart, Myntra, Ajio & Nykaa"
        description="Compare product prices across Amazon, Flipkart, Myntra, Ajio, and Nykaa on Price Ping. Discover live store price disparities and find the lowest price in India."
        canonical="https://priceping.store/price-comparison"
        keywords="Price Ping price comparison, compare prices India, compare Amazon and Flipkart, online shopping price comparison, Price Ping compare"
      />

      <nav aria-label="Breadcrumb" className="text-xs text-slate-500 flex items-center gap-2">
        <Link to="/" className="hover:text-indigo-600 transition-colors">Home</Link>
        <span>/</span>
        <span className="text-slate-800 font-semibold">Price Comparison</span>
      </nav>

      <div className="text-center max-w-3xl mx-auto space-y-4">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 text-xs font-bold">
          <Scale className="w-3.5 h-3.5" />
          <span>Multi-Store Comparison</span>
        </div>
        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black text-slate-900 tracking-tight">
          Compare Prices Across India&apos;s Top Stores
        </h1>
        <p className="text-slate-600 text-base sm:text-lg leading-relaxed">
          E-commerce stores frequently offer different prices for identical items. <strong>Price Ping</strong> queries <strong>Amazon India, Flipkart, Myntra, Ajio, and Nykaa</strong> simultaneously to ensure you always spot the best deal.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm space-y-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold">
            <Store className="w-5 h-5" />
          </div>
          <h2 className="text-lg font-bold text-slate-900">5 Major Platforms</h2>
          <p className="text-xs text-slate-600 leading-relaxed">
            Directly compare Amazon India, Flipkart, Myntra, Ajio, and Nykaa without opening multiple browser tabs or apps.
          </p>
        </div>

        <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm space-y-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold">
            <Layers className="w-5 h-5" />
          </div>
          <h2 className="text-lg font-bold text-slate-900">Exact Variant Matching</h2>
          <p className="text-xs text-slate-600 leading-relaxed">
            Our identity engine checks exact specifications—including storage, RAM, color, and size—so you never compare mismatched products.
          </p>
        </div>

        <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm space-y-3">
          <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center font-bold">
            <TrendingDown className="w-5 h-5" />
          </div>
          <h2 className="text-lg font-bold text-slate-900">Real-Time Verification</h2>
          <p className="text-xs text-slate-600 leading-relaxed">
            Prices and stock availability are checked dynamically to prevent outdated prices or misleading out-of-stock deals.
          </p>
        </div>
      </div>

      <div className="text-center py-6">
        <Link
          to="/compare"
          className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-indigo-600 text-white text-sm font-bold shadow-lg shadow-indigo-600/30 hover:bg-indigo-700 transition-all hover:scale-105"
        >
          <span>Launch Price Comparison Tool</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}
