import { useState } from 'react';
import { productsApi } from '../../services/api';
import toast from 'react-hot-toast';
import {
  Search, Sparkles, Loader2, X, Store,
  Activity, LineChart, Bell, ArrowRight
} from 'lucide-react';
import QuickTrackModal from '../common/QuickTrackModal';
import { detectPlatform, PLATFORM_LABELS } from '../../utils/helpers';

interface Props {
  onProductTracked?: () => void;
}

export default function Hero({ onProductTracked }: Props) {
  const [urlInput, setUrlInput] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [activeModalProduct, setActiveModalProduct] = useState<any>(null);
  const [modalOpen, setModalOpen] = useState(false);

  const detectedStore = detectPlatform(urlInput);

  const handleSearchOrTrack = async (e: React.FormEvent) => {
    e.preventDefault();
    const query = urlInput.trim();
    if (!query) {
      toast.error('Please paste a product URL from Amazon, Flipkart, AJIO, Myntra, or Nykaa');
      return;
    }

    setIsSearching(true);
    try {
      const res = await productsApi.add({ product_url: query });
      const prod = res.data?.product || res.data;
      setActiveModalProduct(prod);
      setModalOpen(true);
      if (onProductTracked) onProductTracked();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Could not fetch product details. Please verify the URL.');
    } finally {
      setIsSearching(false);
    }
  };

  const handleStoreClick = (exampleDomain: string) => {
    toast(`Paste any link from ${exampleDomain} in the search box above to start tracking!`);
  };

  return (
    <>
      <section className="relative w-full overflow-hidden bg-gradient-hero text-white py-16 sm:py-20 lg:py-24">
        {/* Subtle decorative background glow */}
        <div className="absolute top-0 left-1/4 -translate-x-1/2 w-96 h-96 bg-indigo-500/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 right-1/4 translate-x-1/2 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl pointer-events-none" />

        {/* Hero Content Container */}
        <div className="relative z-10 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto text-center flex flex-col items-center">
          {/* Top Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/15 backdrop-blur-md border border-white/20 text-indigo-100 text-xs font-bold shadow-xs mb-6">
            <Sparkles className="w-3.5 h-3.5 text-amber-300 fill-amber-300" />
            <span>Smart Price Tracker for India</span>
          </div>

          {/* Main Heading */}
          <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black text-white tracking-tight leading-[1.12] max-w-4xl">
            Track prices. <br className="hidden sm:inline" />
            Buy when the price is <span className="bg-clip-text text-transparent bg-gradient-to-r from-amber-300 via-orange-300 to-pink-300">right.</span>
          </h1>

          {/* Supporting Text */}
          <p className="mt-4 text-base sm:text-lg text-indigo-100/90 font-normal max-w-2xl leading-relaxed">
            Track product prices, view price history and get notified when your favorite products reach your target price.
          </p>

          {/* Center Search / URL Input Box */}
          <form
            onSubmit={handleSearchOrTrack}
            className="w-full max-w-3xl mt-8 relative"
          >
            <div className="relative flex items-center bg-white rounded-2xl sm:rounded-full p-2 sm:p-2.5 shadow-2xl border border-white/40 focus-within:ring-4 focus-within:ring-indigo-400/30 transition-all text-navy-900">
              {/* Search Link Icon */}
              <div className="pl-3 sm:pl-4 text-gray-400">
                <Search className="w-5 h-5 text-indigo-600" />
              </div>

              {/* Input Field */}
              <input
                type="text"
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                placeholder="Paste an Amazon, Flipkart, AJIO, Myntra or Nykaa product link"
                className="w-full bg-transparent px-3 py-2 text-xs sm:text-sm md:text-base text-navy-900 placeholder-gray-400 font-medium focus:outline-none"
              />

              {/* Clear button if text */}
              {urlInput && (
                <button
                  type="button"
                  onClick={() => setUrlInput('')}
                  className="p-1 rounded-full text-gray-400 hover:text-gray-600 mr-1"
                >
                  <X className="w-4 h-4" />
                </button>
              )}

              {/* Detected store indicator */}
              {detectedStore !== 'unknown' && (
                <span className="hidden sm:inline-flex items-center px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-700 text-[11px] font-bold mr-2">
                  {PLATFORM_LABELS[detectedStore].name}
                </span>
              )}

              {/* Submit CTA Button */}
              <button
                type="submit"
                disabled={isSearching}
                className="btn-primary px-5 sm:px-7 py-3 rounded-xl sm:rounded-full text-xs sm:text-sm font-extrabold tracking-wide flex-shrink-0"
              >
                {isSearching ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Tracking...</span>
                  </>
                ) : (
                  <>
                    <span>Track This Price</span>
                    <ArrowRight className="w-4 h-4 hidden sm:inline" />
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Supported Stores Badge Pills */}
          <div className="mt-5 flex items-center justify-center gap-2 sm:gap-3 flex-wrap text-xs text-indigo-200">
            <span className="font-semibold text-white/80">Supported stores:</span>
            {[
              { id: 'amazon', name: 'Amazon' },
              { id: 'flipkart', name: 'Flipkart' },
              { id: 'ajio', name: 'AJIO' },
              { id: 'myntra', name: 'Myntra' },
              { id: 'nykaa', name: 'Nykaa' },
            ].map((st) => (
              <button
                key={st.id}
                type="button"
                onClick={() => handleStoreClick(st.name)}
                className="px-3 py-1 rounded-full bg-white/10 hover:bg-white/20 border border-white/15 text-white text-xs font-bold transition-all cursor-pointer"
              >
                {st.name}
              </button>
            ))}
          </div>

          {/* 4 Feature Stats Cards */}
          <div className="mt-12 grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 w-full max-w-4xl">
            {/* Stat 1: 5+ Stores */}
            <div className="p-4 rounded-2xl bg-white/10 backdrop-blur-md border border-white/15 text-left flex items-center gap-3.5">
              <div className="w-10 h-10 rounded-xl bg-white/15 text-amber-300 flex items-center justify-center flex-shrink-0">
                <Store className="w-5 h-5" />
              </div>
              <div>
                <div className="text-xl font-black text-white leading-tight">5+ Stores</div>
                <div className="text-[11px] text-indigo-200 font-medium">Top Indian Platforms</div>
              </div>
            </div>

            {/* Stat 2: Real-time Price Tracking */}
            <div className="p-4 rounded-2xl bg-white/10 backdrop-blur-md border border-white/15 text-left flex items-center gap-3.5">
              <div className="w-10 h-10 rounded-xl bg-white/15 text-emerald-300 flex items-center justify-center flex-shrink-0">
                <Activity className="w-5 h-5" />
              </div>
              <div>
                <div className="text-xl font-black text-white leading-tight">Real-Time</div>
                <div className="text-[11px] text-indigo-200 font-medium">Automated Scrapers</div>
              </div>
            </div>

            {/* Stat 3: Price History */}
            <div className="p-4 rounded-2xl bg-white/10 backdrop-blur-md border border-white/15 text-left flex items-center gap-3.5">
              <div className="w-10 h-10 rounded-xl bg-white/15 text-cyan-300 flex items-center justify-center flex-shrink-0">
                <LineChart className="w-5 h-5" />
              </div>
              <div>
                <div className="text-xl font-black text-white leading-tight">Price History</div>
                <div className="text-[11px] text-indigo-200 font-medium">Interactive Analytics</div>
              </div>
            </div>

            {/* Stat 4: Smart Price Alerts */}
            <div className="p-4 rounded-2xl bg-white/10 backdrop-blur-md border border-white/15 text-left flex items-center gap-3.5">
              <div className="w-10 h-10 rounded-xl bg-white/15 text-pink-300 flex items-center justify-center flex-shrink-0">
                <Bell className="w-5 h-5" />
              </div>
              <div>
                <div className="text-xl font-black text-white leading-tight">Smart Alerts</div>
                <div className="text-[11px] text-indigo-200 font-medium">Instant Notifications</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Quick Track Modal */}
      <QuickTrackModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        initialProduct={activeModalProduct}
        onSuccessTrack={onProductTracked}
      />
    </>
  );
}
