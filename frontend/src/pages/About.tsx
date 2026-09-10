import { Link } from 'react-router-dom';
import SEOHead from '../components/common/SEOHead';
import { ShieldCheck, Bell, History, ArrowRight, Store, CheckCircle, Info } from 'lucide-react';

export default function About() {
  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-12">
      <SEOHead
        title="About Price Ping – Multi-Store Price Comparison & Tracking Platform"
        description="Learn about Price Ping, India's dedicated price comparison and price tracking service helping shoppers compare prices across Amazon, Flipkart, Myntra, Ajio, and Nykaa."
        canonical="https://priceping.store/about"
        keywords="About Price Ping, Price Ping India, price comparison platform, online shopping tracker India"
      />

      {/* Breadcrumb Navigation */}
      <nav aria-label="Breadcrumb" className="text-xs text-slate-500 flex items-center gap-2">
        <Link to="/" className="hover:text-indigo-600 transition-colors">Home</Link>
        <span>/</span>
        <span className="text-slate-800 font-semibold">About Price Ping</span>
      </nav>

      {/* Hero Section */}
      <div className="space-y-4 text-center max-w-3xl mx-auto">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 text-xs font-bold">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>About Price Ping</span>
        </div>
        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black text-slate-900 tracking-tight">
          Empowering Smarter Shopping in India
        </h1>
        <p className="text-slate-600 text-base sm:text-lg leading-relaxed">
          <strong>Price Ping</strong> is a price comparison and price tracking platform created to bring total clarity to e-commerce pricing across India. We continuously monitor and verify live product prices across <strong>Amazon India, Flipkart, Myntra, Ajio, and Nykaa</strong> so you can buy with confidence.
        </p>
      </div>

      {/* Core Mission Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm space-y-4">
          <div className="w-12 h-12 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold">
            <Store className="w-6 h-6" />
          </div>
          <h2 className="text-xl font-bold text-slate-900">Multi-Store Price Comparison</h2>
          <p className="text-sm text-slate-600 leading-relaxed">
            The same product often sells at substantially different prices on different platforms due to seller promotions, exclusive offers, and algorithmic repricing. Price Ping aggregates verified store offers side-by-side so you can immediately see which platform offers the best overall deal without manual cross-checking.
          </p>
        </div>

        <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm space-y-4">
          <div className="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold">
            <Bell className="w-6 h-6" />
          </div>
          <h2 className="text-xl font-bold text-slate-900">Automated Price Drop Tracking</h2>
          <p className="text-sm text-slate-600 leading-relaxed">
            Never miss a flash discount or seasonal price reduction. Paste any supported product link into Price Ping and set your target buying price. When the product drops to or below your threshold, Price Ping delivers an alert to your dashboard and inbox.
          </p>
        </div>

        <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm space-y-4">
          <div className="w-12 h-12 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center font-bold">
            <History className="w-6 h-6" />
          </div>
          <h2 className="text-xl font-bold text-slate-900">Authentic Price History</h2>
          <p className="text-sm text-slate-600 leading-relaxed">
            We believe in honest data. Price Ping only visualizes historical price points that have been genuinely recorded and verified by our monitoring systems. We never fabricate price histories or inflate MRP figures to manufacture artificial discount percentages.
          </p>
        </div>

        <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm space-y-4">
          <div className="w-12 h-12 rounded-2xl bg-rose-50 text-rose-600 flex items-center justify-center font-bold">
            <CheckCircle className="w-6 h-6" />
          </div>
          <h2 className="text-xl font-bold text-slate-900">Verified Trending Deals</h2>
          <p className="text-sm text-slate-600 leading-relaxed">
            Our algorithmic deal engine scans thousands of live products to spotlight genuine price drops across consumer electronics, fashion, footwear, beauty, and appliances. Expired deals are automatically purged to preserve listing accuracy.
          </p>
        </div>
      </div>

      {/* Trust & E-E-A-T Transparency Section */}
      <div className="bg-slate-50 rounded-3xl p-8 border border-slate-200 space-y-4">
        <div className="flex items-center gap-2 text-indigo-700 font-bold text-base">
          <Info className="w-5 h-5" />
          <span>Our Transparency Commitment</span>
        </div>
        <p className="text-sm text-slate-600 leading-relaxed">
          Price Ping is an independent shopping utility. We do not sell products directly and are not an e-commerce merchant. All brand names, trademarks, logos, and product imagery are property of their respective owners and retailers. Prices on e-commerce platforms can change dynamically at any time without notice. While we strive for millisecond accuracy through automated store queries, final prices, shipping fees, and terms are governed by each respective retailer at checkout.
        </p>
      </div>

      {/* Call to Action */}
      <div className="text-center py-6">
        <Link
          to="/"
          className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-indigo-600 text-white text-sm font-bold shadow-lg shadow-indigo-600/30 hover:bg-indigo-700 transition-all hover:scale-105"
        >
          <span>Start Tracking Prices on Price Ping</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}
