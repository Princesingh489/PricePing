import { Link } from 'react-router-dom';
import SEOHead from '../components/common/SEOHead';
import { Bell, ShieldCheck, Zap, ArrowRight, CheckCircle2, TrendingDown } from 'lucide-react';

export default function PriceTrackerInfo() {
  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-12">
      <SEOHead
        title="Price Tracker India – Track Product Prices Across Stores with Price Ping"
        description="Monitor price drops on Amazon, Flipkart, Myntra, Ajio, and Nykaa with Price Ping's real-time price tracker. Set custom alerts and receive instant notifications."
        canonical="https://priceping.store/price-tracker"
        keywords="Price Ping price tracker, price tracker India, track Amazon prices, track Flipkart prices, price drop alert India"
      />

      <nav aria-label="Breadcrumb" className="text-xs text-slate-500 flex items-center gap-2">
        <Link to="/" className="hover:text-indigo-600 transition-colors">Home</Link>
        <span>/</span>
        <span className="text-slate-800 font-semibold">Price Tracker</span>
      </nav>

      <div className="text-center max-w-3xl mx-auto space-y-4">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-bold">
          <Bell className="w-3.5 h-3.5" />
          <span>Real-Time E-Commerce Tracker</span>
        </div>
        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black text-slate-900 tracking-tight">
          Price Ping Price Tracker for Indian Stores
        </h1>
        <p className="text-slate-600 text-base sm:text-lg leading-relaxed">
          Track any product URL across <strong>Amazon India, Flipkart, Myntra, Ajio, and Nykaa</strong>. Price Ping watches prices day and night so you can purchase at the ideal moment.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm space-y-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold">
            <Zap className="w-5 h-5" />
          </div>
          <h2 className="text-lg font-bold text-slate-900">Immediate URL Sync</h2>
          <p className="text-xs text-slate-600 leading-relaxed">
            Simply paste your link into the tracker. Price Ping instantly extracts product specifications and initializes your monitoring record.
          </p>
        </div>

        <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm space-y-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold">
            <TrendingDown className="w-5 h-5" />
          </div>
          <h2 className="text-lg font-bold text-slate-900">Custom Price Targets</h2>
          <p className="text-xs text-slate-600 leading-relaxed">
            Define a precise target price (e.g. ₹49,999 for iPhone 15) or an automatic percentage reduction threshold (e.g. 15% off).
          </p>
        </div>

        <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm space-y-3">
          <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center font-bold">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <h2 className="text-lg font-bold text-slate-900">Real Verified Observations</h2>
          <p className="text-xs text-slate-600 leading-relaxed">
            Every tracked point is saved as an authenticated price record. You can visualize price movements over days, weeks, and months.
          </p>
        </div>
      </div>

      <div className="bg-slate-50 rounded-3xl p-8 border border-slate-200 space-y-4">
        <h2 className="text-xl font-bold text-slate-900">How to Start Tracking a Product</h2>
        <ul className="space-y-3 text-sm text-slate-700">
          <li className="flex items-start gap-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
            <span>Copy the web address of your chosen item from Amazon, Flipkart, Myntra, Ajio, or Nykaa.</span>
          </li>
          <li className="flex items-start gap-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
            <span>Paste it into the Price Ping tracker bar on the homepage or dashboard.</span>
          </li>
          <li className="flex items-start gap-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
            <span>Click &quot;Track Product&quot; to begin 24/7 background price surveillance.</span>
          </li>
        </ul>
      </div>

      <div className="text-center py-6">
        <Link
          to="/"
          className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-emerald-600 text-white text-sm font-bold shadow-lg shadow-emerald-600/30 hover:bg-emerald-700 transition-all hover:scale-105"
        >
          <span>Open Price Ping Tracker</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}
