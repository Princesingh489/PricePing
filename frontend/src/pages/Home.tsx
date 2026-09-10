import { Link } from 'react-router-dom';
import HeroTrackerSection from '../components/HeroTrackerSection';
import TrendingDealsSection from '../components/TrendingDealsSection';
import CrossStoreCompareSection from '../components/CrossStoreCompareSection';
import SEOHead from '../components/common/SEOHead';
import { ArrowRight, Store, History, Bell } from 'lucide-react';

export default function Home() {
  return (
    <div className="space-y-0">
      <SEOHead
        title="Price Ping – Compare Prices & Track Products Across Stores"
        description="Price Ping compares real-time product prices across Amazon, Flipkart, Myntra, Ajio, and Nykaa in India. Track products, explore genuine price history, and get alerted when prices drop."
        canonical="https://priceping.store/"
        keywords="Price Ping, Price Ping price comparison, Price Ping price tracker, Price Ping India, Price Ping compare prices, compare Amazon Flipkart prices, price drop alert"
        structuredData={[
          {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "Price Ping",
            "url": "https://priceping.store",
            "logo": "https://priceping.store/favicon.svg",
            "description": "Price Ping is India's multi-store price comparison and real-time price tracking platform across Amazon, Flipkart, Myntra, Ajio, and Nykaa."
          },
          {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "Price Ping",
            "url": "https://priceping.store",
            "potentialAction": {
              "@type": "SearchAction",
              "target": "https://priceping.store/compare?q={search_term_string}",
              "query-input": "required name=search_term_string"
            }
          }
        ]}
      />

      {/* 1. Hero Tracker Section with Festive / Wallpaper Backdrop */}
      <HeroTrackerSection />

      {/* 2. Main Sections Container */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12 py-8">
        {/* Trending Deals Across Stores (Real-time deals from Amazon, Flipkart, Myntra, AJIO, Nykaa) */}
        <div id="trending-deals">
          <TrendingDealsSection />
        </div>

        {/* Cross-Store Live Price Matrix (Comparing Amazon, Flipkart, Myntra, AJIO, Nykaa) */}
        <div id="cross-compare">
          <CrossStoreCompareSection />
        </div>

        {/* SEO & Informational Section for Brand Search & Internal Linking */}
        <section className="bg-gradient-to-br from-slate-900 via-slate-800 to-indigo-950 rounded-3xl p-8 sm:p-12 text-white shadow-xl border border-white/10">
          <div className="max-w-4xl mx-auto text-center space-y-4">
            <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-white">
              Why Indian Shoppers Rely on Price Ping
            </h2>
            <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
              Online prices in India fluctuate daily across major retail platforms. <strong>Price Ping</strong> monitors millions of price points directly from <strong>Amazon India, Flipkart, Myntra, Ajio, and Nykaa</strong> to ensure you never overpay.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-10">
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 p-6 rounded-2xl space-y-3">
              <div className="w-10 h-10 rounded-xl bg-indigo-500/20 text-indigo-400 flex items-center justify-center">
                <Store className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-white">Live Store Comparison</h3>
              <p className="text-xs text-slate-300 leading-relaxed">
                Compare verified prices across 5 major stores side-by-side with genuine offer links and stock availability.
              </p>
              <Link to="/price-comparison" className="inline-flex items-center gap-1 text-xs text-indigo-400 hover:text-indigo-300 font-bold">
                Learn how it works <ArrowRight className="w-3 h-3" />
              </Link>
            </div>

            <div className="bg-white/5 backdrop-blur-sm border border-white/10 p-6 rounded-2xl space-y-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
                <Bell className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-white">Price Drop Alerts</h3>
              <p className="text-xs text-slate-300 leading-relaxed">
                Set custom target price thresholds. Price Ping monitors price changes 24/7 and sends immediate alerts.
              </p>
              <Link to="/price-tracker" className="inline-flex items-center gap-1 text-xs text-emerald-400 hover:text-emerald-300 font-bold">
                Explore price tracker <ArrowRight className="w-3 h-3" />
              </Link>
            </div>

            <div className="bg-white/5 backdrop-blur-sm border border-white/10 p-6 rounded-2xl space-y-3">
              <div className="w-10 h-10 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center">
                <History className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-white">Authentic Price History</h3>
              <p className="text-xs text-slate-300 leading-relaxed">
                Analyze real price trends based strictly on observed market data. No fabricated charts or fake discounts.
              </p>
              <Link to="/history" className="inline-flex items-center gap-1 text-xs text-amber-400 hover:text-amber-300 font-bold">
                View price history <ArrowRight className="w-3 h-3" />
              </Link>
            </div>
          </div>

          {/* Popular Categories Links for Deep Crawlability */}
          <div className="mt-10 pt-8 border-t border-white/10 flex flex-wrap items-center justify-between gap-4 text-xs">
            <span className="text-slate-400 font-bold">Browse Popular Categories:</span>
            <div className="flex flex-wrap gap-2">
              <Link to="/category/mobiles" className="px-3 py-1.5 rounded-lg bg-white/10 text-slate-200 hover:bg-white/20 transition-all">Mobiles &amp; Smartphones</Link>
              <Link to="/category/laptops" className="px-3 py-1.5 rounded-lg bg-white/10 text-slate-200 hover:bg-white/20 transition-all">Laptops &amp; Computers</Link>
              <Link to="/category/electronics" className="px-3 py-1.5 rounded-lg bg-white/10 text-slate-200 hover:bg-white/20 transition-all">Consumer Electronics</Link>
              <Link to="/category/wearables" className="px-3 py-1.5 rounded-lg bg-white/10 text-slate-200 hover:bg-white/20 transition-all">Smartwatches &amp; Wearables</Link>
              <Link to="/category/audio" className="px-3 py-1.5 rounded-lg bg-white/10 text-slate-200 hover:bg-white/20 transition-all">Headphones &amp; Audio</Link>
              <Link to="/category/fashion" className="px-3 py-1.5 rounded-lg bg-white/10 text-slate-200 hover:bg-white/20 transition-all">Fashion &amp; Apparel</Link>
              <Link to="/category/beauty" className="px-3 py-1.5 rounded-lg bg-white/10 text-slate-200 hover:bg-white/20 transition-all">Beauty &amp; Personal Care</Link>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
