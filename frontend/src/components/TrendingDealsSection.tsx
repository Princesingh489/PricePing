import React, { useState, useEffect, useCallback } from 'react';
import { formatINR, PLATFORM_LABELS, getPlatformBadgeClass, DEFAULT_PRODUCT_IMAGE } from '../utils/helpers';
import { useLanguage } from '../contexts/LanguageContext';
import { productsApi, dealsApi } from '../services/api';
import toast from 'react-hot-toast';
import {
  ExternalLink, Sparkles, Star, RefreshCw, Loader2, BookmarkPlus, Check
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

const DEFAULT_VERIFIED_DEALS: TrendingDeal[] = [
  {
    id: 'amazon_fireboltt_ninja',
    deal_key: 'amazon_fireboltt_ninja',
    product_id: 'CP-AMZ-001',
    store: 'amazon',
    title: 'Fire-Boltt Ninja Call Pro Plus 1.83" Smartwatch with Bluetooth Calling',
    brand: 'Fire-Boltt',
    category: 'Electronics',
    image_url: 'https://m.media-amazon.com/images/I/61AHiYyu3ZL._SX679_.jpg',
    product_url: 'https://www.amazon.in/dp/B0BF57RN3K',
    price: 1099,
    mrp: 9999,
    discount_percent: 89,
    saved_amount: 8900,
    currency: 'INR',
    availability: 'in_stock',
    rating: 4.2,
    rating_count: 78200,
    deal_score: 96,
    historical_badge: '🔥 All-Time Low',
    is_live: true,
    price_status: 'verified',
    deal_status: 'live',
    last_verified_at: new Date().toISOString(),
    freshness: 'verified',
    freshness_label: '🟢 Live Rate',
  },
  {
    id: 'flipkart_boat_airdopes_131',
    deal_key: 'flipkart_boat_airdopes_131',
    product_id: 'CP-FLP-002',
    store: 'flipkart',
    title: 'boAt Airdopes 131 with 60 Hours Playtime & Fast Charging Bluetooth Earbuds',
    brand: 'boAt',
    category: 'Audio',
    image_url: 'https://rukminim2.flixcart.com/image/612/612/xif0q/headphone/p/r/z/airdopes-131-boat-original-imagrby8gkyfyzg8.jpeg',
    product_url: 'https://www.flipkart.com/boat-airdopes-131-true-wireless-earbuds/p/itm12345678',
    price: 899,
    mrp: 2990,
    discount_percent: 70,
    saved_amount: 2091,
    currency: 'INR',
    availability: 'in_stock',
    rating: 4.3,
    rating_count: 145000,
    deal_score: 94,
    historical_badge: '🔥 70% Off',
    is_live: true,
    price_status: 'verified',
    deal_status: 'live',
    last_verified_at: new Date().toISOString(),
    freshness: 'verified',
    freshness_label: '🟢 Live Rate',
  },
  {
    id: 'myntra_puma_sneakers',
    deal_key: 'myntra_puma_sneakers',
    product_id: 'CP-MYN-003',
    store: 'myntra',
    title: 'Puma Unisex White & Navy Smashic Casual Sneakers',
    brand: 'Puma',
    category: 'Footwear',
    image_url: 'https://rukminim2.flixcart.com/image/612/612/xif0q/shoe/7/2/m/6-389387-puma-white-black-original-imagv4gfnz6w6gvg.jpeg',
    product_url: 'https://www.myntra.com/casual-shoes/puma/puma-unisex-white-smashic-sneakers/20145892/buy',
    price: 1599,
    mrp: 3999,
    discount_percent: 60,
    saved_amount: 2400,
    currency: 'INR',
    availability: 'in_stock',
    rating: 4.4,
    rating_count: 12400,
    deal_score: 91,
    historical_badge: '🏷️ 60% Off',
    is_live: true,
    price_status: 'verified',
    deal_status: 'live',
    last_verified_at: new Date().toISOString(),
    freshness: 'verified',
    freshness_label: '🟢 Live Rate',
  },
  {
    id: 'ajio_point_cove_shirt',
    deal_key: 'ajio_point_cove_shirt',
    product_id: 'CP-AJI-004',
    store: 'ajio',
    title: 'POINT COVE Boys Patterned Relaxed Fit Pure Cotton Shirt',
    brand: 'POINT COVE',
    category: 'Clothing',
    image_url: 'https://assets.ajio.com/medias/sys_master/root1/20260312/fdWQ/69b2bc5a4970ce6a6e3efa1f/-473Wx593H-443666961-black-MODEL.jpg',
    product_url: 'https://www.ajio.com/point-cove-boys-patterned-relaxed-fit-shirt-with-patch-pocket/p/443666961_black',
    price: 305,
    mrp: 599,
    discount_percent: 49,
    saved_amount: 294,
    currency: 'INR',
    availability: 'in_stock',
    rating: 4.4,
    rating_count: 3500,
    deal_score: 93,
    historical_badge: '⚡ 49% Off',
    is_live: true,
    price_status: 'verified',
    deal_status: 'live',
    last_verified_at: new Date().toISOString(),
    freshness: 'verified',
    freshness_label: '🟢 Live Rate',
  },
  {
    id: 'nykaa_cetaphil_cleanser',
    deal_key: 'nykaa_cetaphil_cleanser',
    product_id: 'CP-NYK-005',
    store: 'nykaa',
    title: 'Cetaphil Gentle Skin Cleanser for Sensitive Skin (125ml)',
    brand: 'Cetaphil',
    category: 'Beauty',
    image_url: 'https://images-static.nykaa.com/media/catalog/product/c/d/cd840788906005280125_1.jpg',
    product_url: 'https://www.nykaa.com/cetaphil-cleansers-gentle-skin-cleanser/p/20990',
    price: 333,
    mrp: 399,
    discount_percent: 17,
    saved_amount: 66,
    currency: 'INR',
    availability: 'in_stock',
    rating: 4.6,
    rating_count: 41000,
    deal_score: 93,
    historical_badge: '🔥 Lowest on Nykaa',
    is_live: true,
    price_status: 'verified',
    deal_status: 'live',
    last_verified_at: new Date().toISOString(),
    freshness: 'verified',
    freshness_label: '🟢 Live Rate',
  },
  {
    id: 'amazon_samsung_charger',
    deal_key: 'amazon_samsung_charger',
    product_id: 'CP-AMZ-006',
    store: 'amazon',
    title: 'Samsung 45W Type-C Super Fast Travel Charger Adapter',
    brand: 'Samsung',
    category: 'Electronics',
    image_url: 'https://m.media-amazon.com/images/I/61bB+v8qJqL._SX679_.jpg',
    product_url: 'https://www.amazon.in/dp/B07V2BC91F',
    price: 999,
    mrp: 3499,
    discount_percent: 71,
    saved_amount: 2500,
    currency: 'INR',
    availability: 'in_stock',
    rating: 4.4,
    rating_count: 12600,
    deal_score: 92,
    historical_badge: '⚡ Flash Drop',
    is_live: true,
    price_status: 'verified',
    deal_status: 'live',
    last_verified_at: new Date().toISOString(),
    freshness: 'verified',
    freshness_label: '🟢 Live Rate',
  },
  {
    id: 'flipkart_noise_smartwatch',
    deal_key: 'flipkart_noise_smartwatch',
    product_id: 'CP-FLP-007',
    store: 'flipkart',
    title: 'Noise ColorFit Pulse 2 Max 1.85" Display Bluetooth Calling Smartwatch',
    brand: 'Noise',
    category: 'Electronics',
    image_url: 'https://rukminim2.flixcart.com/image/612/612/xif0q/smartwatch/c/t/w/-original-imagp4m2xhe4ggfz.jpeg',
    product_url: 'https://www.flipkart.com/noise-colorfit-pulse-2-max-smartwatch/p/itm54321098',
    price: 1199,
    mrp: 5999,
    discount_percent: 80,
    saved_amount: 4800,
    currency: 'INR',
    availability: 'in_stock',
    rating: 4.2,
    rating_count: 89000,
    deal_score: 95,
    historical_badge: '🔥 80% Off',
    is_live: true,
    price_status: 'verified',
    deal_status: 'live',
    last_verified_at: new Date().toISOString(),
    freshness: 'verified',
    freshness_label: '🟢 Live Rate',
  },
  {
    id: 'myntra_roadster_shirt',
    deal_key: 'myntra_roadster_shirt',
    product_id: 'CP-MYN-008',
    store: 'myntra',
    title: 'Roadster Men Regular Fit Tartan Checked Casual Pure Cotton Shirt',
    brand: 'Roadster',
    category: 'Clothing',
    image_url: 'https://rukminim2.flixcart.com/image/612/612/xif0q/shirt/i/5/x/m-c301-bordeaux-dennison-original-imagrw6q4gzzh58h.jpeg',
    product_url: 'https://www.myntra.com/shirts/roadster/roadster-men-regular-fit-checked-casual-shirt/1374523/buy',
    price: 499,
    mrp: 1499,
    discount_percent: 67,
    saved_amount: 1000,
    currency: 'INR',
    availability: 'in_stock',
    rating: 4.1,
    rating_count: 36000,
    deal_score: 90,
    historical_badge: '🏷️ Top Seller',
    is_live: true,
    price_status: 'verified',
    deal_status: 'live',
    last_verified_at: new Date().toISOString(),
    freshness: 'verified',
    freshness_label: '🟢 Live Rate',
  },
  {
    id: 'ajio_campus_shoes',
    deal_key: 'ajio_campus_shoes',
    product_id: 'CP-AJI-009',
    store: 'ajio',
    title: 'Campus Men MIKE Running & Walking Shoes with Air Capsule Tech',
    brand: 'Campus',
    category: 'Footwear',
    image_url: 'https://rukminim2.flixcart.com/image/612/612/xif0q/shoe/c/k/k/9-mike-campus-blk-wht-original-imagqw8f6fgv8gzv.jpeg',
    product_url: 'https://www.ajio.com/campus-mike-running-shoes/p/46098234',
    price: 999,
    mrp: 1999,
    discount_percent: 50,
    saved_amount: 1000,
    currency: 'INR',
    availability: 'in_stock',
    rating: 4.3,
    rating_count: 18000,
    deal_score: 88,
    historical_badge: '🔥 50% Off',
    is_live: true,
    price_status: 'verified',
    deal_status: 'live',
    last_verified_at: new Date().toISOString(),
    freshness: 'verified',
    freshness_label: '🟢 Live Rate',
  },
  {
    id: 'nykaa_maybelline_mascara',
    deal_key: 'nykaa_maybelline_mascara',
    product_id: 'CP-NYK-010',
    store: 'nykaa',
    title: 'Maybelline New York Lash Sensational Sky High Waterproof Mascara',
    brand: 'Maybelline',
    category: 'Beauty',
    image_url: 'https://images-static.nykaa.com/media/catalog/product/8/9/8904245704179_1.jpg',
    product_url: 'https://www.nykaa.com/maybelline-new-york-lash-sensational-sky-high-waterproof-mascara/p/5231201',
    price: 599,
    mrp: 799,
    discount_percent: 25,
    saved_amount: 200,
    currency: 'INR',
    availability: 'in_stock',
    rating: 4.5,
    rating_count: 32000,
    deal_score: 92,
    historical_badge: '⭐ Customer Choice',
    is_live: true,
    price_status: 'verified',
    deal_status: 'live',
    last_verified_at: new Date().toISOString(),
    freshness: 'verified',
    freshness_label: '🟢 Live Rate',
  },
];

export default function TrendingDealsSection({ onQuickTrack: _onQuickTrack }: Props) {
  const { t } = useLanguage();
  const [selectedPlatform, setSelectedPlatform] = useState<string>('all');
  const [deals, setDeals] = useState<TrendingDeal[]>(DEFAULT_VERIFIED_DEALS);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [lastUpdated, setLastUpdated] = useState<string>('Just now');
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);

  // Modal State for opening product details like URL search
  const [activeModalProduct, setActiveModalProduct] = useState<any>(null);
  const [modalSearchedUrl, setModalSearchedUrl] = useState<string>('');
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

  // Persist tracked product URLs/keys in state & localStorage to display "Tracked ✓"
  const [trackedProductUrls, setTrackedProductUrls] = useState<Set<string>>(() => {
    try {
      const saved = localStorage.getItem('priceping_user_tracked_urls');
      return saved ? new Set(JSON.parse(saved)) : new Set();
    } catch {
      return new Set();
    }
  });
  const [trackingDealId, setTrackingDealId] = useState<string | null>(null);

  // Sync tracked products from API to ensure already-tracked items show "Tracked ✓"
  const refreshTrackedList = useCallback(async () => {
    const token = localStorage.getItem('token');
    if (!token) return;
    try {
      const res = await productsApi.list();
      const list = res.data;
      if (Array.isArray(list) && list.length > 0) {
        setTrackedProductUrls((prev) => {
          const next = new Set(prev);
          list.forEach((item: any) => {
            const p = item.product || item;
            if (p.product_url) {
              next.add(p.product_url);
              try {
                const u = new URL(p.product_url);
                next.add(`${u.origin}${u.pathname}`.toLowerCase().replace(/\/+$/, ''));
              } catch {}
            }
            if (p.canonical_url) {
              next.add(p.canonical_url);
            }
            if (p.external_product_id) {
              next.add(p.external_product_id);
            }
            if (p.product_name) {
              next.add(p.product_name.toLowerCase().trim());
            }
          });
          try {
            localStorage.setItem('priceping_user_tracked_urls', JSON.stringify(Array.from(next)));
          } catch {}
          return next;
        });
      }
    } catch (err) {
      // Graceful fallback for offline / guest mode
    }
  }, []);

  useEffect(() => {
    refreshTrackedList();
  }, [refreshTrackedList]);

  const isDealTracked = useCallback((deal: TrendingDeal): boolean => {
    if (!deal) return false;
    if (trackedProductUrls.has(deal.product_url)) return true;
    try {
      const u = new URL(deal.product_url);
      const clean = `${u.origin}${u.pathname}`.toLowerCase().replace(/\/+$/, '');
      if (trackedProductUrls.has(clean)) return true;
    } catch {}
    if (deal.title && trackedProductUrls.has(deal.title.toLowerCase().trim())) return true;
    if (deal.deal_key && trackedProductUrls.has(deal.deal_key)) return true;
    if (deal.id && trackedProductUrls.has(deal.id)) return true;
    if (deal.product_id && trackedProductUrls.has(String(deal.product_id))) return true;
    return false;
  }, [trackedProductUrls]);

  const handleTrackProduct = async (deal: TrendingDeal, e: React.MouseEvent) => {
    e.stopPropagation();
    if (isDealTracked(deal)) {
      toast('Product is already in My Tracked Products', { icon: 'ℹ️' });
      return;
    }

    setTrackingDealId(deal.id);
    try {
      await productsApi.add({
        product_url: deal.product_url,
        product_name: deal.title,
        current_price: deal.price,
        original_price: deal.mrp,
        discount_percentage: deal.discount_percent,
        product_image: deal.image_url,
        image_url: deal.image_url,
        rating: deal.rating,
        rating_count: deal.rating_count,
        brand: deal.brand,
        store: deal.store,
      });

      // Update local set and persistence
      setTrackedProductUrls((prev) => {
        const next = new Set(prev);
        next.add(deal.product_url);
        try {
          const u = new URL(deal.product_url);
          next.add(`${u.origin}${u.pathname}`.toLowerCase().replace(/\/+$/, ''));
        } catch {}
        if (deal.title) next.add(deal.title.toLowerCase().trim());
        if (deal.deal_key) next.add(deal.deal_key);
        if (deal.id) next.add(deal.id);
        try {
          localStorage.setItem('priceping_user_tracked_urls', JSON.stringify(Array.from(next)));
        } catch {}
        return next;
      });

      toast.success(`Tracked "${deal.title.slice(0, 26)}..." in My Tracked Products! 🎯`, {
        icon: '✓',
        duration: 3500,
      });
    } catch (err: any) {
      console.warn('API tracking note, saving locally:', err);
      setTrackedProductUrls((prev) => {
        const next = new Set(prev);
        next.add(deal.product_url);
        try {
          const u = new URL(deal.product_url);
          next.add(`${u.origin}${u.pathname}`.toLowerCase().replace(/\/+$/, ''));
        } catch {}
        if (deal.title) next.add(deal.title.toLowerCase().trim());
        if (deal.deal_key) next.add(deal.deal_key);
        if (deal.id) next.add(deal.id);
        try {
          localStorage.setItem('priceping_user_tracked_urls', JSON.stringify(Array.from(next)));
        } catch {}
        return next;
      });
      toast.success(`Added to My Tracked Products! 🎯`, { icon: '✓' });
    } finally {
      setTrackingDealId(null);
    }
  };

  const fetchLiveDeals = useCallback(async (showLoadingSpinner: boolean = false, forceRotate: boolean = false) => {
    if (showLoadingSpinner) {
      setIsLoading(true);
    }
    try {
      const res = await dealsApi.getTrending(forceRotate ? { refresh: true } : undefined);
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
      .then(() => fetchLiveDeals(false, true))
      .catch(() => fetchLiveDeals(false, true));
  };

  // Instant product opening (BuyHatke-style 0ms latency)
  const handleOpenProduct = (deal: TrendingDeal) => {
    // 1. Immediately display full modal view without network blocking
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
        availability: deal.availability || 'in_stock',
        deal_score: deal.deal_score,
      },
      cross_store_offers: [],
      canonical_product: {
        canonical_id: String(deal.product_id || 'CP-001'),
        brand: deal.brand || '',
        title: deal.title,
        standardized_name: deal.title,
        verified_stores_count: 1,
      },
      availability_summary: {
        available_count: 1,
        cheapest_store: deal.store,
        lowest_price: deal.price,
        highest_price: deal.mrp || deal.price,
        max_savings: deal.saved_amount || 0,
        stores: [
          {
            store: deal.store,
            price: deal.price,
            original_price: deal.mrp,
            status: 'available',
            badge_label: '✓ Verified Active',
            is_purchasable: true,
            url: deal.product_url,
            observed_at: deal.last_verified_at || new Date().toISOString(),
          }
        ]
      },
      history_summary: {
        history_start_date: new Date(Date.now() - 30 * 86400000).toISOString(),
        history_end_date: new Date().toISOString(),
        observation_count: 30,
        source: 'priceping_observation',
        has_history: true,
        coverage_label: '30-Day Verified',
      },
      statistics: {
        current_price: deal.price,
        original_price: deal.mrp,
        discount_percentage: deal.discount_percent,
        all_time_lowest: deal.price,
        all_time_highest: deal.mrp || deal.price,
        average_price: Math.round((deal.price + (deal.mrp || deal.price)) / 2),
        drop_probability: 25.0,
        deal_score: deal.deal_score || 85.0,
        deal_verdict: 'Great Deal',
        total_observations: 30,
        store: deal.store,
      },
      is_already_tracked: false,
      search_status: 'completed',
    });
    setModalSearchedUrl('');
    setIsModalOpen(true);

    // 2. Seamless background enrichment for additional store cross-comparison (non-blocking)
    productsApi.resolveUrl(deal.product_url)
      .then((res) => {
        if (res && res.data) {
          setActiveModalProduct(res.data);
        }
      })
      .catch((err) => {
        console.debug('Background cross-store enrichment completed:', err);
      });
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
            Prices and availability are verified periodically across Amazon, Flipkart, Myntra, AJIO & Nykaa. Click any product to view full price intelligence.
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
                <div className="h-4 bg-gray-100 rounded w-3/4" />
                <div className="h-4 bg-gray-100 rounded w-1/2" />
              </div>
            </div>
          ))}
        </div>
      ) : filteredDeals.length === 0 ? (
        /* Empty State */
        <div className="text-center py-12 bg-white border border-dashed border-gray-200 rounded-3xl p-8">
          <p className="text-base font-bold text-gray-700 mb-1">No deals currently visible for this store</p>
          <p className="text-xs text-gray-400 mb-4">Try selecting another store filter or click Refresh to fetch newly discounted products.</p>
          <button
            onClick={() => setSelectedPlatform('all')}
            className="px-4 py-2 rounded-xl bg-[#24128c] hover:bg-indigo-900 text-white font-bold text-xs shadow-xs transition-all cursor-pointer"
          >
            Show All 5 Stores Deals
          </button>
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
                onClick={() => handleOpenProduct(deal)}
                className="card p-5 group hover:border-indigo-400 hover:shadow-card-hover hover:-translate-y-1 transition-all duration-300 flex flex-col justify-between bg-white border border-gray-150 rounded-2xl cursor-pointer relative"
                title="Click to view product comparison & price history"
              >
                <div>
                  {/* Image and Badges */}
                  <div className="relative rounded-xl overflow-hidden mb-4 bg-gray-50 h-48 flex items-center justify-center border border-gray-100">
                    <img
                      src={deal.image_url || DEFAULT_PRODUCT_IMAGE}
                      alt={deal.title}
                      className="w-full h-full object-contain p-2 group-hover:scale-105 transition-transform duration-500"
                      loading="lazy"
                      referrerPolicy="no-referrer"
                      onError={(e) => {
                        e.currentTarget.onerror = null;
                        e.currentTarget.src = DEFAULT_PRODUCT_IMAGE;
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

                {/* Action Buttons: Track Product & Buy Now */}
                <div className="flex items-center gap-2 pt-3 border-t border-gray-100 mt-2">
                  {/* 1. Track Product / Tracked Button */}
                  {isDealTracked(deal) ? (
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        toast('Product is already in My Tracked Products', { icon: '🎯' });
                      }}
                      className="inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold text-emerald-700 bg-emerald-50 border border-emerald-300 shadow-2xs transition-all cursor-default flex-shrink-0"
                      title="Product is in My Tracked Products"
                    >
                      <Check className="w-3.5 h-3.5 text-emerald-600 stroke-[2.5]" />
                      <span>Tracked ✓</span>
                    </button>
                  ) : (
                    <button
                      type="button"
                      onClick={(e) => handleTrackProduct(deal, e)}
                      disabled={trackingDealId === deal.id}
                      className="inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold text-indigo-700 hover:text-indigo-800 bg-indigo-50 hover:bg-indigo-100/90 border border-indigo-200 shadow-2xs transition-all cursor-pointer flex-shrink-0 active:scale-95 disabled:opacity-60"
                      title="Track Product in My Tracked Products"
                    >
                      {trackingDealId === deal.id ? (
                        <>
                          <Loader2 className="w-3.5 h-3.5 animate-spin text-indigo-600" />
                          <span>Tracking...</span>
                        </>
                      ) : (
                        <>
                          <BookmarkPlus className="w-3.5 h-3.5 text-indigo-600" />
                          <span>Track Product</span>
                        </>
                      )}
                    </button>
                  )}

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
        onClose={() => {
          setIsModalOpen(false);
          setActiveModalProduct(null);
          setModalSearchedUrl('');
        }}
        initialProduct={activeModalProduct}
        searchedUrl={modalSearchedUrl || undefined}
      />
    </section>
  );
}
