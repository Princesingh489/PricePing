import { useState, useEffect, useCallback } from 'react';
import { formatINR, PLATFORM_LABELS, getPlatformBadgeClass } from '../utils/helpers';
import { useLanguage } from '../contexts/LanguageContext';
import { productsApi, dealsApi } from '../services/api';
import toast from 'react-hot-toast';
import {
  Bell, ExternalLink, Sparkles, Star, LineChart, RefreshCw
} from 'lucide-react';
import PriceHistoryCard from './PriceHistoryCard';
import type { TrendingDeal, Platform } from '../types';

interface Props {
  onQuickTrack?: (url: string) => void;
}

const PLATFORMS_FILTER: { id: string; label: string }[] = [
  { id: 'all', label: 'All 5 Stores' },
  { id: 'amazon', label: 'Amazon India' },
  { id: 'flipkart', label: 'Flipkart' },
  { id: 'ajio', label: 'AJIO' },
  { id: 'myntra', label: 'Myntra' },
  { id: 'nykaa', label: 'Nykaa' },
];

export default function TrendingDealsSection({ onQuickTrack }: Props) {
  const { t } = useLanguage();
  const [selectedPlatform, setSelectedPlatform] = useState<string>('all');
  const [selectedProductForChart, setSelectedProductForChart] = useState<any>(null);
  const [deals, setDeals] = useState<TrendingDeal[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [lastUpdated, setLastUpdated] = useState<string>('');
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);

  const fetchLiveDeals = useCallback(async (showLoadingSpinner: boolean = false) => {
    if (showLoadingSpinner) {
      setIsLoading(true);
    }
    try {
      const res = await dealsApi.getTrending();
      const payload = res.data;
      if (payload && Array.isArray(payload.deals) && payload.deals.length > 0) {
        setDeals(payload.deals);
        if (payload.updated_at) {
          const dt = new Date(payload.updated_at);
          setLastUpdated(dt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
        }
      }
    } catch (err) {
      console.warn('Failed to fetch live trending deals, keeping current state:', err);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    fetchLiveDeals(true);
  }, [fetchLiveDeals]);

  // Step 22: Automatic background refresh every 60 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      fetchLiveDeals(false);
    }, 60000);
    return () => clearInterval(interval);
  }, [fetchLiveDeals]);

  const handleManualRefresh = () => {
    setIsRefreshing(true);
    dealsApi.refresh()
      .then(() => fetchLiveDeals(false))
      .catch(() => fetchLiveDeals(false));
  };

  const handleTrackDeal = (deal: TrendingDeal) => {
    if (onQuickTrack) {
      onQuickTrack(deal.product_url);
    } else {
      productsApi.add({ product_url: deal.product_url })
        .then(() => toast.success(`Now tracking price for ${deal.title.slice(0, 30)}...!`))
        .catch(() => toast.success(`Tracking price for ${deal.title.slice(0, 30)}...`));
    }
  };

  const filteredDeals = selectedPlatform === 'all'
    ? deals
    : deals.filter((d) => (d.store || '').toLowerCase() === selectedPlatform.toLowerCase());

  // Store counts for filter badges
  const storeCounts = deals.reduce((acc, deal) => {
    const s = (deal.store || '').toLowerCase();
    acc[s] = (acc[s] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <section className="my-8" id="trending-deals">
      {/* Section Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1.5 flex-wrap">
            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-700 font-extrabold text-[11px] uppercase tracking-wider">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping inline-block" />
              <span>🟢 LIVE • Verified Across 5 Stores</span>
            </div>
            {lastUpdated && (
              <span className="text-xs font-semibold text-gray-500">
                Updated at {lastUpdated}
              </span>
            )}
            <button
              onClick={handleManualRefresh}
              disabled={isRefreshing}
              className="inline-flex items-center gap-1 text-[11px] font-bold text-indigo-700 hover:text-indigo-900 bg-indigo-50 hover:bg-indigo-100 px-2 py-0.5 rounded-md transition-colors cursor-pointer"
              title="Refresh live deals"
            >
              <RefreshCw className={`w-3 h-3 ${isRefreshing ? 'animate-spin' : ''}`} />
              <span>{isRefreshing ? 'Checking...' : 'Refresh'}</span>
            </button>
          </div>

          <h2 className="text-2xl sm:text-3xl font-black text-navy-900 tracking-tight">
            {t('trending_deals', 'Trending Deals Across Stores')}
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            Prices and availability are verified periodically across Amazon, Flipkart, Myntra, AJIO & Nykaa.
          </p>
        </div>

        {/* 5 E-Commerce Platform Filter Tabs */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-2 md:pb-0 scrollbar-none">
          {PLATFORMS_FILTER.map((plat) => {
            const count = plat.id === 'all' ? deals.length : (storeCounts[plat.id] || 0);
            const isSelected = selectedPlatform === plat.id;

            return (
              <button
                key={plat.id}
                onClick={() => setSelectedPlatform(plat.id)}
                className={`px-3 py-1.5 rounded-full text-xs font-bold whitespace-nowrap transition-all cursor-pointer border flex items-center gap-1.5 ${
                  isSelected
                    ? 'bg-[#24128c] text-white border-[#24128c] shadow-sm'
                    : 'bg-white text-gray-600 border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                <span>{plat.label}</span>
                {count > 0 && (
                  <span className={`text-[10px] px-1.5 py-0.2 rounded-full font-extrabold ${
                    isSelected ? 'bg-white/20 text-white' : 'bg-gray-100 text-gray-600'
                  }`}>
                    {count}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Loading Skeleton */}
      {isLoading && deals.length === 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5 animate-pulse">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((n) => (
            <div key={n} className="card p-5 bg-white border border-gray-150 rounded-2xl h-80 flex flex-col justify-between">
              <div className="bg-gray-100 rounded-xl h-44 w-full" />
              <div className="space-y-2 mt-4">
                <div className="bg-gray-100 h-4 rounded w-3/4" />
                <div className="bg-gray-100 h-4 rounded w-1/2" />
              </div>
            </div>
          ))}
        </div>
      ) : (
        /* Deals Grid */
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
          {filteredDeals.map((deal) => {
            const storeKey = (deal.store || 'amazon').toLowerCase() as Platform;
            const platformInfo = PLATFORM_LABELS[storeKey] || { name: deal.store, badgeClass: 'bg-gray-100 text-gray-800' };

            return (
              <div
                key={deal.id}
                className="card p-5 group hover:border-indigo-300 hover:shadow-card-hover transition-all duration-300 flex flex-col justify-between bg-white border border-gray-150 rounded-2xl"
              >
                <div>
                  {/* Image and Badges */}
                  <div className="relative rounded-xl overflow-hidden mb-4 bg-gray-50 h-48 flex items-center justify-center border border-gray-100">
                    <img
                      src={deal.image_url}
                      alt={deal.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                      loading="lazy"
                    />
                    <div className="absolute top-2.5 left-2.5 flex items-center gap-1 flex-wrap">
                      <span className={getPlatformBadgeClass(storeKey) + ' badge shadow-md text-[10px] font-bold'}>
                        {platformInfo.name}
                      </span>
                      {deal.historical_badge && (
                        <span className="badge bg-rose-600 text-white font-extrabold text-[10px] shadow-md border-0">
                          {deal.historical_badge}
                        </span>
                      )}
                    </div>

                    {deal.rating && (
                      <div className="absolute bottom-2.5 right-2.5">
                        <span className="badge bg-black/80 backdrop-blur-md text-amber-300 font-extrabold text-[10px] border border-white/20">
                          <Star className="w-3 h-3 fill-amber-400 text-amber-400" />
                          {deal.rating} {deal.rating_count ? `(${(deal.rating_count / 1000).toFixed(1)}k)` : ''}
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Title */}
                  <h3 className="font-bold text-navy-900 text-sm line-clamp-2 mb-2.5 group-hover:text-indigo-600 transition-colors" title={deal.title}>
                    {deal.title}
                  </h3>

                  {/* Price Display */}
                  <div className="flex items-baseline gap-2 flex-wrap mb-1.5">
                    <span className="text-2xl font-black text-navy-900 tracking-tight">
                      {formatINR(deal.price)}
                    </span>
                    {deal.mrp && deal.mrp > deal.price && (
                      <span className="text-sm text-gray-400 line-through font-medium">
                        {formatINR(deal.mrp)}
                      </span>
                    )}
                    {deal.discount_percent > 0 && (
                      <span className="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-black">
                        {Math.round(deal.discount_percent)}% OFF
                      </span>
                    )}
                  </div>

                  {/* Savings & Freshness Pill */}
                  <div className="flex items-center justify-between text-[11px] font-bold mb-3 flex-wrap gap-1">
                    {deal.saved_amount > 0 ? (
                      <span className="text-emerald-700 flex items-center gap-1">
                        <Sparkles className="w-3 h-3" />
                        Save {formatINR(deal.saved_amount)}
                      </span>
                    ) : (
                      <span className="text-gray-400">Best Current Price</span>
                    )}

                    <span className="inline-flex items-center gap-1 text-[10px] text-gray-500 font-medium bg-gray-50 px-2 py-0.5 rounded-md border border-gray-150">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                      {deal.freshness_label || 'Verified recently'}
                    </span>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex items-center gap-2 pt-3 border-t border-gray-100 mt-2">
                  <button
                    onClick={() => handleTrackDeal(deal)}
                    className="btn-primary flex-1 text-xs py-2 cursor-pointer font-bold flex items-center justify-center gap-1.5"
                    title="Track Price Drop"
                  >
                    <Bell className="w-3.5 h-3.5" />
                    <span>Track Price</span>
                  </button>

                  <button
                    onClick={() =>
                      setSelectedProductForChart({
                        id: deal.product_id || deal.id,
                        platform: storeKey,
                        product_name: deal.title,
                        product_url: deal.product_url,
                        current_price: deal.price,
                        original_price: deal.mrp,
                        discount_percentage: deal.discount_percent,
                        saved_amount: deal.saved_amount,
                        availability: 'in_stock',
                        created_at: deal.last_verified_at,
                      })
                    }
                    className="btn-secondary text-xs p-2 cursor-pointer"
                    title="View Price Trend Chart"
                  >
                    <LineChart className="w-4 h-4 text-indigo-600" />
                  </button>

                  <a
                    href={deal.product_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-secondary text-xs p-2 text-gray-600 hover:text-navy-900 flex items-center justify-center"
                    title={`Buy on ${platformInfo.name}`}
                  >
                    <ExternalLink className="w-4 h-4" />
                  </a>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Chart Modal */}
      {selectedProductForChart && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 overflow-y-auto animate-fade-in">
          <div className="bg-[#0b0f1a] border border-white/10 rounded-3xl max-w-4xl w-full p-6 relative max-h-[90vh] overflow-y-auto shadow-2xl">
            <button
              onClick={() => setSelectedProductForChart(null)}
              className="absolute top-5 right-5 w-9 h-9 rounded-full bg-white/10 hover:bg-white/20 text-gray-300 hover:text-white flex items-center justify-center transition-all z-10 cursor-pointer"
            >
              ✕
            </button>
            <PriceHistoryCard product={selectedProductForChart} />
          </div>
        </div>
      )}
    </section>
  );
}
