import React, { useState, useEffect, useCallback } from 'react';
import { formatINR, PLATFORM_LABELS, getPlatformBadgeClass } from '../utils/helpers';
import { useLanguage } from '../contexts/LanguageContext';
import { productsApi, dealsApi } from '../services/api';
import toast from 'react-hot-toast';
import {
  ExternalLink, Sparkles, Star, RefreshCw, Trash2, Loader2, RotateCcw
} from 'lucide-react';
import QuickTrackModal from './QuickTrackModal';
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

export default function TrendingDealsSection({ onQuickTrack: _onQuickTrack }: Props) {
  const { t } = useLanguage();
  const [selectedPlatform, setSelectedPlatform] = useState<string>('all');
  const [deals, setDeals] = useState<TrendingDeal[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [lastUpdated, setLastUpdated] = useState<string>('');
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);

  // Modal State for opening product details like URL search
  const [activeModalProduct, setActiveModalProduct] = useState<any>(null);
  const [modalSearchedUrl, setModalSearchedUrl] = useState<string>('');
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [resolvingDealId, setResolvingDealId] = useState<string | null>(null);

  // Persist dismissed/deleted deals in localStorage so they do not reappear
  const [dismissedDealIds, setDismissedDealIds] = useState<Set<string>>(() => {
    try {
      const saved = localStorage.getItem('priceping_dismissed_deals');
      return saved ? new Set(JSON.parse(saved)) : new Set();
    } catch {
      return new Set();
    }
  });

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

  // Automatic background refresh every 60 seconds for dynamic rotating deals
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

  // Delete/dismiss a deal from user's view
  const handleDeleteDeal = (dealId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setDismissedDealIds((prev) => {
      const next = new Set(prev);
      next.add(dealId);
      try {
        localStorage.setItem('priceping_dismissed_deals', JSON.stringify(Array.from(next)));
      } catch (err) {
        console.warn('Could not persist dismissed deal to localStorage', err);
      }
      return next;
    });
    toast.success('Deal removed from trending', { icon: '🗑️' });
  };

  // Restore dismissed deals if needed
  const handleRestoreDismissed = () => {
    setDismissedDealIds(new Set());
    localStorage.removeItem('priceping_dismissed_deals');
    toast.success('Restored all deleted deals');
  };

  // Problem 1: Clicking Product or Title opens full comparison modal identical to URL search
  const handleOpenProduct = async (deal: TrendingDeal) => {
    setResolvingDealId(deal.id);
    try {
      const res = await productsApi.resolveUrl(deal.product_url);
      setActiveModalProduct(res.data);
      setModalSearchedUrl(deal.product_url);
      setIsModalOpen(true);
    } catch (err: any) {
      console.warn('Direct resolve failed, fallback to structured product representation:', err);
      // Fallback gracefully to product representation so the user always sees the product view
      setActiveModalProduct({
        product: {
          id: deal.product_id ? parseInt(String(deal.product_id).replace(/\D/g, '')) || 1 : 1,
          product_name: deal.title,
          platform: deal.store,
          product_url: deal.product_url,
          current_price: deal.price,
          original_price: deal.mrp,
          discount_percentage: deal.discount_percent,
          product_image: deal.image_url,
          rating: deal.rating,
          rating_count: deal.rating_count,
          brand: deal.brand,
          store: deal.store,
          currency: 'INR',
          availability: 'in_stock',
          deal_score: deal.deal_score,
        },
        cross_store_offers: [],
        canonical_product: null,
        statistics: null,
        history_points: [],
      });
      setModalSearchedUrl(deal.product_url);
      setIsModalOpen(true);
    } finally {
      setResolvingDealId(null);
    }
  };

  // Filter out deleted deals
  const activeDeals = deals.filter((d) => !dismissedDealIds.has(d.id));

  const filteredDeals = selectedPlatform === 'all'
    ? activeDeals
    : activeDeals.filter((d) => (d.store || '').toLowerCase() === selectedPlatform.toLowerCase());

  // Store counts for filter badges
  const storeCounts = activeDeals.reduce((acc, deal) => {
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

            {dismissedDealIds.size > 0 && (
              <button
                onClick={handleRestoreDismissed}
                className="inline-flex items-center gap-1 text-[11px] font-bold text-gray-600 hover:text-gray-900 bg-gray-100 hover:bg-gray-200 px-2 py-0.5 rounded-md transition-colors cursor-pointer"
                title="Restore all deleted deals"
              >
                <RotateCcw className="w-3 h-3" />
                <span>Restore ({dismissedDealIds.size})</span>
              </button>
            )}
          </div>

          <h2 className="text-2xl sm:text-3xl font-black text-navy-900 tracking-tight">
            {t('trending_deals', 'Trending Deals Across Stores')}
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            Prices and availability are verified periodically across Amazon, Flipkart, Myntra, AJIO & Nykaa. Click any product to view full price intelligence.
          </p>
        </div>

        {/* 5 E-Commerce Platform Filter Tabs */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-2 md:pb-0 scrollbar-none">
          {PLATFORMS_FILTER.map((plat) => {
            const count = plat.id === 'all' ? activeDeals.length : (storeCounts[plat.id] || 0);
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
      {isLoading && activeDeals.length === 0 ? (
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
      ) : filteredDeals.length === 0 ? (
        /* Empty State */
        <div className="text-center py-12 bg-white border border-dashed border-gray-200 rounded-3xl p-8">
          <p className="text-base font-bold text-gray-700 mb-1">No deals currently visible in this view</p>
          <p className="text-xs text-gray-400 mb-4">You may have deleted these deals or selected an empty store filter.</p>
          {dismissedDealIds.size > 0 && (
            <button
              onClick={handleRestoreDismissed}
              className="btn-secondary text-xs px-4 py-2 cursor-pointer font-bold inline-flex items-center gap-1.5"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Restore Deleted Deals</span>
            </button>
          )}
        </div>
      ) : (
        /* Deals Grid */
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
          {filteredDeals.map((deal) => {
            const storeKey = (deal.store || 'amazon').toLowerCase() as Platform;
            const platformInfo = PLATFORM_LABELS[storeKey] || { name: deal.store, badgeClass: 'bg-gray-100 text-gray-800' };
            const isResolvingThis = resolvingDealId === deal.id;

            return (
              <div
                key={deal.id}
                onClick={() => handleOpenProduct(deal)}
                className="card p-5 group hover:border-indigo-400 hover:shadow-card-hover hover:-translate-y-1 transition-all duration-300 flex flex-col justify-between bg-white border border-gray-150 rounded-2xl cursor-pointer relative"
                title="Click to view product comparison & price history"
              >
                {/* Resolving Spinner Overlay */}
                {isResolvingThis && (
                  <div className="absolute inset-0 bg-white/85 backdrop-blur-xs z-30 rounded-2xl flex flex-col items-center justify-center gap-2">
                    <Loader2 className="w-7 h-7 text-indigo-600 animate-spin" />
                    <span className="text-xs font-bold text-gray-800">Opening Product...</span>
                  </div>
                )}

                <div>
                  {/* Image and Badges */}
                  <div className="relative rounded-xl overflow-hidden mb-4 bg-gray-50 h-48 flex items-center justify-center border border-gray-100">
                    <img
                      src={deal.image_url}
                      alt={deal.title}
                      className="w-full h-full object-contain p-2 group-hover:scale-105 transition-transform duration-500"
                      loading="lazy"
                      referrerPolicy="no-referrer"
                      onError={(e) => {
                        e.currentTarget.onerror = null;
                        const cat = (deal.category || '').toLowerCase();
                        if (cat.includes('audio') || cat.includes('headphone')) {
                          e.currentTarget.src = 'https://m.media-amazon.com/images/I/61L4SkS7w2L._SX679_.jpg';
                        } else if (cat.includes('footwear') || cat.includes('shoe') || cat.includes('slipper')) {
                          e.currentTarget.src = 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&auto=format&fit=crop&q=80';
                        } else if (cat.includes('smart') || cat.includes('phone')) {
                          e.currentTarget.src = 'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=500&auto=format&fit=crop&q=80';
                        } else if (cat.includes('beauty')) {
                          e.currentTarget.src = 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=500&auto=format&fit=crop&q=80';
                        } else {
                          e.currentTarget.src = 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&auto=format&fit=crop&q=80';
                        }
                      }}
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
                  <h3
                    className="font-bold text-navy-900 text-sm line-clamp-2 mb-2.5 group-hover:text-indigo-600 transition-colors"
                    title={deal.title}
                  >
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

                {/* Action Buttons: Only 2 Buttons (Delete & Buy as requested) */}
                <div className="flex items-center gap-2 pt-3 border-t border-gray-100 mt-2">
                  {/* 1. Delete Button */}
                  <button
                    type="button"
                    onClick={(e) => handleDeleteDeal(deal.id, e)}
                    className="inline-flex items-center justify-center gap-1 px-3 py-2 rounded-xl text-xs font-bold text-rose-600 hover:text-rose-700 bg-rose-50 hover:bg-rose-100/80 border border-rose-200/60 transition-all cursor-pointer flex-shrink-0"
                    title="Delete deal from list"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    <span>Delete</span>
                  </button>

                  {/* 2. Buy Button */}
                  <a
                    href={deal.product_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={(e) => e.stopPropagation()}
                    className="btn-primary flex-1 py-2 text-xs font-bold flex items-center justify-center gap-1.5 shadow-sm hover:shadow transition-all"
                    title={`Buy on ${platformInfo.name}`}
                  >
                    <span>Buy Now</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* QuickTrackModal for in-app product comparison & intelligence (same as URL input) */}
      <QuickTrackModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        initialProduct={activeModalProduct}
        searchedUrl={modalSearchedUrl}
      />
    </section>
  );
}
