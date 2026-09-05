import React, { useState, useMemo, useEffect } from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  CartesianGrid,
} from 'recharts';
import {
  Clock,
  ShieldCheck,
  CheckCircle2,
  TrendingDown,
  Share2,
} from 'lucide-react';
import toast from 'react-hot-toast';
import { formatINR } from '../utils/helpers';
import type { Product, RealPriceHistoryPoint, RealPriceHistoryResponse } from '../types';
import { productsApi } from '../services/api';

interface PriceHistoryCardProps {
  product: Product;
}

const STORE_TABS = [
  { id: 'all', label: 'All Stores' },
  { id: 'amazon', label: 'Amazon' },
  { id: 'flipkart', label: 'Flipkart' },
  { id: 'myntra', label: 'Myntra' },
  { id: 'ajio', label: 'AJIO' },
  { id: 'nykaa', label: 'Nykaa' },
];

const PERIOD_TABS = [
  { id: '1m', label: '1 Month' },
  { id: '3m', label: '3 Month' },
  { id: '6m', label: '6 Month' },
  { id: '1y', label: '1 Year' },
  { id: 'all', label: 'Max' },
];

export const PriceHistoryCard: React.FC<PriceHistoryCardProps> = ({ product }) => {
  const [selectedStore, setSelectedStore] = useState<string>('all');
  const [selectedPeriod, setSelectedPeriod] = useState<string>('all');
  const [historyResponse, setHistoryResponse] = useState<RealPriceHistoryResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Fetch genuine price history whenever store or period changes
  useEffect(() => {
    if (!product?.id) return;
    let isCancelled = false;
    setLoading(true);

    productsApi
      .getPriceHistory(product.id, selectedStore, selectedPeriod)
      .then((res) => {
        if (!isCancelled && res.data) {
          setHistoryResponse(res.data);
        }
      })
      .catch((err) => {
        console.error('Failed to load real price history:', err);
      })
      .finally(() => {
        if (!isCancelled) setLoading(false);
      });

    return () => {
      isCancelled = true;
    };
  }, [product?.id, selectedStore, selectedPeriod]);

  const rawPoints = historyResponse?.data || [];

  // Format real points for Recharts (STRICTLY REAL DATA, NEVER FAKE)
  const chartPoints = useMemo(() => {
    return rawPoints.map((pt: RealPriceHistoryPoint) => {
      const dt = new Date(pt.timestamp);
      return {
        date: pt.date || dt.toLocaleDateString('en-IN', { month: 'short', day: 'numeric' }),
        rawDate: dt,
        price: pt.price,
        original_price: pt.original_price,
        store: pt.store,
        source: pt.source,
      };
    });
  }, [rawPoints]);

  // Single source of truth: compute stats strictly from verified filtered history
  const stats = useMemo(() => {
    const s = historyResponse?.statistics;
    const prices = chartPoints.map((p) => p.price).filter((p) => p > 0);
    const cur = product.current_price || (prices.length > 0 ? prices[prices.length - 1] : null);

    const lowest = s?.lowest_price ?? (prices.length > 0 ? Math.min(...prices) : null);
    const highest = s?.highest_price ?? (prices.length > 0 ? Math.max(...prices) : null);
    const avg = s?.average_price ?? (prices.length > 0 ? Math.round(prices.reduce((a, b) => a + b, 0) / prices.length) : null);
    const count = s?.observation_count ?? prices.length;
    const saving = s?.potential_saving ?? (cur && highest && highest > cur ? highest - cur : 0);

    const isCorrupted = lowest !== null && avg !== null && highest !== null && (lowest > avg || avg > highest || lowest > highest);
    if (isCorrupted) {
      console.warn('Mathematical invariant violated in PriceHistoryCard:', { lowest, avg, highest });
    }

    return {
      current: cur,
      lowest,
      highest,
      average: avg,
      potentialSaving: saving,
      observationCount: count,
      isCorrupted,
    };
  }, [historyResponse?.statistics, chartPoints, product.current_price]);

  const handleShare = () => {
    if (navigator.share) {
      navigator
        .share({
          title: product.product_name,
          text: `Check real verified price history of ${product.product_name} on PricePing! Current: ${formatINR(product.current_price)}`,
          url: product.product_url,
        })
        .catch(() => {});
    } else {
      navigator.clipboard.writeText(product.product_url);
      toast.success('Product link copied to clipboard!');
    }
  };

  const hasChartableHistory = chartPoints.length >= 2;

  return (
    <div className="space-y-6 w-full mt-6">
      {/* 1. Header & Controls Card */}
      <div className="card p-6 shadow-xl relative overflow-hidden backdrop-blur-md">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-white/[0.08]">
          <div>
            <div className="flex items-center gap-2 text-cyan-400 font-extrabold text-xs uppercase tracking-wider mb-1">
              <TrendingDown className="w-4 h-4" />
              Real Price History Intelligence
            </div>
            <h2 className="text-xl sm:text-2xl font-black text-white tracking-tight">
              Verified Price History
            </h2>
            <p className="text-xs text-gray-400 mt-1">
              100% authentic observations recorded by PricePing. No artificial or interpolated points.
            </p>
          </div>

          {/* Store Tabs */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0">
            {STORE_TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setSelectedStore(tab.id)}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold whitespace-nowrap transition-all cursor-pointer ${
                  selectedStore === tab.id
                    ? 'bg-cyan-500 text-black shadow-md shadow-cyan-500/20'
                    : 'bg-white/[0.05] text-gray-400 hover:text-white hover:bg-white/[0.1]'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Coverage Metadata Badge */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-4">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-xs font-bold text-emerald-400">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>
              {historyResponse?.coverage_label || 'Tracking product price observations in real time.'}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleShare}
              className="p-1.5 rounded-xl bg-white/[0.04] hover:bg-white/[0.1] border border-white/10 text-gray-400 hover:text-white transition-all cursor-pointer"
              title="Share price history"
            >
              <Share2 className="w-3.5 h-3.5" />
            </button>

            {/* Period Tabs */}
          <div className="flex items-center gap-1 bg-white/[0.04] p-1 rounded-xl border border-white/[0.08]">
            {PERIOD_TABS.map((p) => (
              <button
                key={p.id}
                onClick={() => setSelectedPeriod(p.id)}
                className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                  selectedPeriod === p.id
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>
      </div>

        {/* 2. Chart or Genuine Missing History Notice */}
        <div className="mt-6">
          {loading ? (
            <div className="h-72 flex flex-col items-center justify-center gap-3">
              <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
              <p className="text-xs text-gray-400 font-semibold">Loading verified observations...</p>
            </div>
          ) : !hasChartableHistory ? (
            /* Genuine Missing History State: NEVER FAKE A GRAPH */
            <div className="h-72 flex flex-col items-center justify-center text-center p-6 rounded-2xl bg-white/[0.02] border border-dashed border-white/[0.12] space-y-3">
              <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
                <Clock className="w-6 h-6" />
              </div>
              <div className="max-w-md">
                <h3 className="text-base font-black text-white">
                  No verified price history is available for this product yet.
                </h3>
                <p className="text-xs text-gray-400 mt-1.5 leading-relaxed">
                  PricePing will start tracking this product and build its price history automatically.
                  We adhere strictly to real data and will never draw a graph using manufactured points.
                </p>
              </div>
              <div className="flex items-center gap-3 pt-2 text-xs font-bold">
                <span className="px-3 py-1 rounded-lg bg-white/[0.05] text-gray-300 border border-white/10">
                  Current Observed Price: {formatINR(product.current_price)}
                </span>
                <span className="px-3 py-1 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                  {stats.observationCount} / 2 required points for trendline
                </span>
              </div>
            </div>
          ) : (
            /* Genuine Recharts Graph */
            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartPoints} margin={{ top: 15, right: 15, left: 10, bottom: 0 }}>
                  <defs>
                    <linearGradient id="realPriceGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#06b6d4" stopOpacity={0.35} />
                      <stop offset="100%" stopColor="#06b6d4" stopOpacity={0.02} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                  <XAxis
                    dataKey="date"
                    tick={{ fill: '#94a3b8', fontSize: 11, fontWeight: 600 }}
                    tickLine={false}
                    axisLine={{ stroke: '#ffffff15' }}
                  />
                  <YAxis
                    tick={{ fill: '#94a3b8', fontSize: 11, fontWeight: 600 }}
                    tickLine={false}
                    axisLine={false}
                    domain={['dataMin - 200', 'dataMax + 200']}
                    tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}k`}
                    width={48}
                  />
                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const pt = payload[0].payload;
                        return (
                          <div className="bg-[#0f1422] border border-cyan-500/30 p-3 rounded-xl shadow-2xl text-xs space-y-1">
                            <div className="flex items-center justify-between gap-4 text-gray-400 font-semibold">
                              <span>{pt.date}</span>
                              <span className="uppercase text-[10px] px-1.5 py-0.5 rounded bg-white/[0.06] text-cyan-300 font-bold">
                                {pt.store}
                              </span>
                            </div>
                            <div className="text-white font-black text-base">{formatINR(pt.price)}</div>
                            {pt.original_price && pt.original_price > pt.price && (
                              <div className="text-gray-500 text-xs line-through">
                                MRP: {formatINR(pt.original_price)}
                              </div>
                            )}
                            <div className="text-[10px] text-emerald-400 font-medium flex items-center gap-1 pt-0.5">
                              <CheckCircle2 className="w-3 h-3" />
                              <span>Verified {pt.source.replace('_', ' ')}</span>
                            </div>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  {stats.lowest && (
                    <ReferenceLine
                      y={stats.lowest}
                      stroke="#10b981"
                      strokeDasharray="4 4"
                      label={{
                        value: `Lowest: ₹${stats.lowest}`,
                        fill: '#34d399',
                        fontSize: 10,
                        position: 'insideBottomRight',
                      }}
                    />
                  )}
                  {stats.average && (
                    <ReferenceLine
                      y={stats.average}
                      stroke="#f59e0b"
                      strokeDasharray="3 3"
                      label={{
                        value: `Avg: ₹${stats.average}`,
                        fill: '#fbbf24',
                        fontSize: 10,
                        position: 'insideTopLeft',
                      }}
                    />
                  )}
                  <Area
                    type="monotone"
                    dataKey="price"
                    stroke="#06b6d4"
                    strokeWidth={2.5}
                    fill="url(#realPriceGrad)"
                    isAnimationActive={true}
                    animationDuration={600}
                    activeDot={{ r: 6, fill: '#06b6d4', stroke: '#ffffff', strokeWidth: 2 }}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* 3. Real Price Summary Metric Blocks */}
        {stats.isCorrupted ? (
          <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs font-bold text-center mt-6">
            Price statistics temporarily unavailable.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6 pt-6 border-t border-white/[0.08]">
            <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/[0.06]">
              <div className="text-xs uppercase tracking-wider text-gray-400 font-bold mb-1">
                Lowest Recorded
              </div>
              <div className="text-2xl font-black text-emerald-400 tracking-tight">
                {stats.lowest !== null ? formatINR(stats.lowest) : '—'}
              </div>
              <div className="text-xs text-gray-400 mt-1">
                {stats.lowest !== null ? 'Verified genuine low' : 'No data yet'}
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/[0.06]">
              <div className="text-xs uppercase tracking-wider text-gray-400 font-bold mb-1">
                Average Price
              </div>
              <div className="text-2xl font-black text-amber-400 tracking-tight">
                {stats.average !== null ? formatINR(stats.average) : '—'}
              </div>
              <div className="text-xs text-gray-400 mt-1">
                {stats.observationCount > 0 ? `Based on ${stats.observationCount} genuine checks` : 'No data yet'}
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/[0.06]">
              <div className="text-xs uppercase tracking-wider text-gray-400 font-bold mb-1">
                Highest Recorded
              </div>
              <div className="text-2xl font-black text-rose-400 tracking-tight">
                {stats.highest !== null ? formatINR(stats.highest) : '—'}
              </div>
              <div className="text-xs text-gray-400 mt-1">
                {stats.highest !== null ? 'Peak retail observation' : 'No data yet'}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PriceHistoryCard;
