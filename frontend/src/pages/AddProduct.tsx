import React, { useState } from 'react';
import { productsApi } from '../services/api';
import toast from 'react-hot-toast';
import { detectPlatform, PLATFORM_LABELS } from '../utils/helpers';
import type { Platform, StoreOffer, RealPriceStatistics, RealPriceHistoryPoint } from '../types';
import {
  Link2, Search, CheckCircle2, Loader2,
} from 'lucide-react';
import PricePingProductView from '../components/product/PricePingProductView';

const SUPPORTED_STORES = [
  { id: 'amazon', name: 'Amazon India' },
  { id: 'flipkart', name: 'Flipkart' },
  { id: 'ajio', name: 'AJIO' },
  { id: 'myntra', name: 'Myntra' },
  { id: 'nykaa', name: 'Nykaa' },
];

const PROGRESS_STAGES = [
  'Detecting store...',
  'Finding product...',
  'Fetching current price...',
  'Checking other stores...',
  'Loading verified price history...',
];

export default function AddProduct() {
  const [url, setUrl] = useState('');
  const [detectedPlatform, setDetectedPlatform] = useState<Platform>('unknown');
  const [fetchedProduct, setFetchedProduct] = useState<any | null>(null);
  const [crossStoreOffers, setCrossStoreOffers] = useState<StoreOffer[]>([]);
  const [statistics, setStatistics] = useState<RealPriceStatistics | null>(null);
  const [historyPoints, setHistoryPoints] = useState<RealPriceHistoryPoint[]>([]);
  const [coverageLabel, setCoverageLabel] = useState<string>('');
  const [step, setStep] = useState<'url' | 'fetching' | 'result'>('url');
  const [fetchStage, setFetchStage] = useState<number>(0);

  const handleUrlChange = (val: string) => {
    setUrl(val);
    setDetectedPlatform(detectPlatform(val));
  };

  const handleFetch = async (e?: React.FormEvent, customUrl?: string) => {
    if (e) e.preventDefault();
    const targetUrl = (customUrl || url).trim();
    if (!targetUrl) return;

    const plat = detectPlatform(targetUrl);
    if (plat === 'unknown') {
      toast.error('Unsupported platform. Please enter an Amazon, Flipkart, AJIO, Myntra, or Nykaa link.');
      return;
    }

    setStep('fetching');
    setFetchStage(0);

    const t1 = setTimeout(() => setFetchStage(1), 400);
    const t2 = setTimeout(() => setFetchStage(2), 900);
    const t3 = setTimeout(() => setFetchStage(3), 1600);
    const t4 = setTimeout(() => setFetchStage(4), 2200);

    try {
      // 1. Resolve product with complete multi-store comparison and verified statistics
      let resolvedData: any = null;
      try {
        const resolveRes = await productsApi.resolveUrl(targetUrl);
        resolvedData = resolveRes.data;
      } catch {
        // Fallback to productsApi.add
        const addRes = await productsApi.add({ product_url: targetUrl });
        resolvedData = {
          product: addRes.data?.product || addRes.data,
          comparison: [],
          statistics: null,
          tracker_id: addRes.data?.id,
        };
      }

      const prod = resolvedData.product;
      setFetchedProduct(resolvedData);

      if (resolvedData.comparison && resolvedData.comparison.length > 0) {
        setCrossStoreOffers(resolvedData.comparison);
      }
      if (resolvedData.statistics) {
        setStatistics(resolvedData.statistics);
      }

      // 2. Fetch full verified price history curve
      if (prod?.id) {
        try {
          const histRes = await productsApi.getPriceHistory(prod.id, 'all', 'all');
          if (histRes.data) {
            setHistoryPoints(histRes.data.data || []);
            setCoverageLabel(histRes.data.coverage_label || '');
            if (histRes.data.statistics && !resolvedData.statistics) {
              setStatistics(histRes.data.statistics);
            }
          }
        } catch (e) {
          console.warn('Could not load history points:', e);
        }
      }

      setStep('result');
      toast.success('Product details and live store comparison loaded! 🎉');
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Unable to fetch this product. Please check the URL.');
      setStep('url');
    } finally {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
      clearTimeout(t4);
    }
  };

  const product = fetchedProduct?.product || (fetchedProduct as any);

  // When result is loaded: render the Price Ping layout matching product
  if (step === 'result' && product) {
    return (
      <PricePingProductView
        product={product}
        trackerId={fetchedProduct?.id}
        crossStoreOffers={crossStoreOffers}
        canonicalProduct={fetchedProduct?.canonical_product}
        availabilitySummary={fetchedProduct?.availability_summary}
        statistics={statistics}
        historyPoints={historyPoints}
        coverageLabel={coverageLabel}
        onSearchUrl={(newUrl) => {
          setUrl(newUrl);
          handleFetch(undefined, newUrl);
        }}
        isSearching={false}
      />
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 space-y-8">
      {/* Heading */}
      <div className="text-center max-w-2xl mx-auto">
        <span className="text-xs font-black uppercase tracking-wider text-indigo-600 bg-indigo-50 px-3 py-1 rounded-full border border-indigo-100">
          Track New Item
        </span>
        <h1 className="text-3xl sm:text-4xl font-black text-navy-900 tracking-tight mt-2">
          Start tracking a product
        </h1>
        <p className="text-gray-500 text-sm mt-1.5">
          Paste any product link and we'll automatically track price drops, compare all stores, and show verified price history.
        </p>
      </div>

      {/* URL Input Box */}
      <div className="card p-6 sm:p-8 space-y-6 shadow-md border-gray-200">
        <div>
          <label className="label">Paste Product URL</label>
          <form onSubmit={(e) => handleFetch(e)} className="space-y-4">
            <div className="relative">
              <Link2 className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                className="input pl-12 pr-4 py-3.5 text-base font-medium"
                placeholder="https://www.amazon.in/dp/... or https://www.flipkart.com/..."
                value={url}
                onChange={(e) => handleUrlChange(e.target.value)}
                disabled={step === 'fetching'}
                required
                autoFocus
              />
            </div>

            {/* Supported stores strip */}
            <div className="flex flex-wrap items-center justify-between gap-2 pt-1 text-xs">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-gray-500 font-bold">Supported stores:</span>
                {SUPPORTED_STORES.map((s) => (
                  <span key={s.id} className={`badge badge-${s.id} text-[10px]`}>
                    {s.name}
                  </span>
                ))}
              </div>

              {detectedPlatform !== 'unknown' && url && (
                <span className="text-emerald-700 font-bold flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                  Detected: {PLATFORM_LABELS[detectedPlatform].name}
                </span>
              )}
            </div>

            {/* Progressive loading state */}
            {step === 'fetching' ? (
              <div className="p-5 rounded-2xl bg-indigo-50/70 border border-indigo-100 space-y-3 mt-4">
                <div className="flex items-center justify-between text-xs font-bold text-indigo-900">
                  <span className="flex items-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin text-indigo-600" />
                    {PROGRESS_STAGES[fetchStage]}
                  </span>
                  <span>Stage {fetchStage + 1} of 5</span>
                </div>
                <div className="w-full h-2 rounded-full bg-indigo-100 overflow-hidden">
                  <div
                    className="h-full bg-indigo-600 transition-all duration-300 rounded-full"
                    style={{ width: `${((fetchStage + 1) / 5) * 100}%` }}
                  />
                </div>
                <div className="grid grid-cols-5 gap-1 pt-1">
                  {PROGRESS_STAGES.map((st, i) => (
                    <div
                      key={i}
                      className={`text-[10px] text-center font-bold truncate ${
                        i <= fetchStage ? 'text-indigo-700' : 'text-gray-400'
                      }`}
                    >
                      {st.replace('...', '')}
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <button
                type="submit"
                disabled={detectedPlatform === 'unknown'}
                className="btn-primary w-full py-3.5 text-base font-extrabold shadow-md mt-4 cursor-pointer"
              >
                <Search className="w-5 h-5" />
                <span>Fetch Product & Compare Stores</span>
              </button>
            )}
          </form>
        </div>
      </div>
    </div>
  );
}
