import HeroTrackerSection from '../components/HeroTrackerSection';
import TrendingDealsSection from '../components/TrendingDealsSection';
import CrossStoreCompareSection from '../components/CrossStoreCompareSection';

export default function Home() {
  return (
    <div className="space-y-0">
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
      </div>
    </div>
  );
}

