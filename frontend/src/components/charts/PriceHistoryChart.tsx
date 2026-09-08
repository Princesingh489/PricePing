import { useState, useMemo, useEffect } from 'react';
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
  Share2,
  ExternalLink,
  ShieldCheck,
  Clock,
  CheckCircle2,
} from 'lucide-react';
import toast from 'react-hot-toast';
import { formatINR, PLATFORM_LABELS, DEFAULT_PRODUCT_IMAGE } from '../../utils/helpers';
import type { Product, PriceHistory, RealPriceHistoryPoint, RealPriceHistoryResponse } from '../../types';
import { productsApi } from '../../services/api';

interface PriceHistoryChartProps {
  product: Product;
  history?: PriceHistory[];
  isStandalone?: boolean;
}

export default function PriceHistoryChart({ product }: PriceHistoryChartProps) {
  const [historyResponse, setHistoryResponse] = useState<RealPriceHistoryResponse | null>(null);
  const [timeFilter, setTimeFilter] = useState<'All' | '1Y' | '6M' | '3M' | '1M'>('All');
  const [loading, setLoading] = useState<boolean>(true);

  // Fetch genuine price history whenever product or time filter changes
  useEffect(() => {
    if (!product?.id) return;
    let isCancelled = false;
    setLoading(true);

    const periodParam = timeFilter.toLowerCase();
    productsApi
      .getPriceHistory(product.id, 'all', periodParam)
      .then((res) => {
        if (!isCancelled && res.data) {
          setHistoryResponse(res.data);
        }
      })
      .catch((err) => {
        console.error('Failed to load verified price history:', err);
      })
      .finally(() => {
        if (!isCancelled) setLoading(false);
      });

    return () => {
      isCancelled = true;
    };
  }, [product?.id, timeFilter]);

  const platformInfo = product?.platform ? PLATFORM_LABELS[product.platform] : undefined;
  const rawPoints = historyResponse?.data || [];

  // Strictly REAL data points only. NEVER fake or simulation points.
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

  // Statistics calculation strictly from the SAME filtered observation dataset
  const stats = useMemo(() => {
    const prices = chartPoints.map((p) => p.price).filter((p) => p > 0);
    const cur = product.current_price || (prices.length > 0 ? prices[prices.length - 1] : null);

    if (prices.length === 0) {
      return {
        current: cur,
        lowest: null,
        highest: null,
        average: null,
        potentialSaving: 0,
        observationCount: 0,
        isCorrupted: false,
      };
    }

    if (prices.length === 1) {
      const p = prices[0];
      return {
        current: cur || p,
        lowest: p,
        highest: p,
        average: p,
        potentialSaving: cur && p > cur ? p - cur : 0,
        observationCount: 1,
        isCorrupted: false,
      };
    }

    const lowest = Math.min(...prices);
    const highest = Math.max(...prices);
    const sum = prices.reduce((acc, val) => acc + val, 0);
    const avg = Math.round(sum / prices.length);
    const saving = cur && highest > cur ? highest - cur : 0;

    // Safety validation: LOWEST <= AVERAGE <= HIGHEST
    const isCorrupted = lowest > avg || avg > highest || lowest > highest;
    if (isCorrupted) {
      console.warn('Mathematical invariant violated in PriceHistoryChart stats:', { lowest, avg, highest });
    }

    return {
      current: cur,
      lowest,
      highest,
      average: avg,
      potentialSaving: saving,
      observationCount: prices.length,
      isCorrupted,
    };
  }, [chartPoints, product.current_price]);

  const handleShare = () => {
    if (navigator.share) {
      navigator
        .share({
          title: product.product_name,
          text: `Check price history of ${product.product_name} on PricePing! Current: ${formatINR(product.current_price)}`,
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
    <div className="space-y-6 w-full">
      {/* Product & Stats Overview Card */}
      <div className="card p-6 shadow-sm border border-gray-200">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 pb-6 border-b border-gray-100">
          <div className="flex gap-4 items-center min-w-0">
            <div className="w-16 h-16 rounded-2xl bg-gray-50 border border-gray-200 flex items-center justify-center p-2 flex-shrink-0 shadow-2xs overflow-hidden">
              <img
                src={product.product_image || DEFAULT_PRODUCT_IMAGE}
                alt={product.product_name}
                className="w-full h-full object-contain"
                onError={(e) => {
                  (e.target as HTMLImageElement).src = DEFAULT_PRODUCT_IMAGE;
                }}
              />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2 mb-1">
                {platformInfo && (
                  <span className="badge badge-info text-[10px]">
                    {platformInfo.name}
                  </span>
                )}
                <span className="text-xs text-gray-400 font-semibold flex items-center gap-1">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" /> Verified Observations
                </span>
              </div>
              <h2 className="text-base sm:text-lg font-black text-navy-900 truncate tracking-tight">
                {product.product_name}
              </h2>
            </div>
          </div>

          <div className="flex items-center gap-3 w-full lg:w-auto justify-between lg:justify-end">
            <div className="text-left lg:text-right">
              <div className="text-xs text-gray-400 font-bold uppercase tracking-wider">Live Observed Price</div>
              <div className="text-2xl font-black text-navy-900 tracking-tight">
                {formatINR(product.current_price)}
              </div>
            </div>
            <a
              href={product.product_url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-primary text-xs py-2.5 px-4 inline-flex items-center gap-1.5"
            >
              <span>Visit Store</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>
        </div>

        {/* Real Statistics Metric Blocks */}
        {stats.isCorrupted ? (
          <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-800 text-xs font-bold mt-6 text-center">
            Price statistics temporarily unavailable.
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6">
            <div className="p-4 rounded-2xl bg-gray-50/70 border border-gray-100">
              <div className="text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-0.5">
                Lowest Recorded
              </div>
              <div className="text-xl font-black text-emerald-600">
                {stats.lowest !== null ? formatINR(stats.lowest) : '—'}
              </div>
              <div className="text-[10px] text-gray-400 mt-1">In selected period</div>
            </div>

            <div className="p-4 rounded-2xl bg-gray-50/70 border border-gray-100">
              <div className="text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-0.5">
                Average Price
              </div>
              <div className="text-xl font-black text-amber-600">
                {stats.average !== null ? formatINR(stats.average) : '—'}
              </div>
              <div className="text-[10px] text-gray-400 mt-1">
                {stats.observationCount > 0 ? `From ${stats.observationCount} observations` : 'No data yet'}
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-gray-50/70 border border-gray-100">
              <div className="text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-0.5">
                Highest Recorded
              </div>
              <div className="text-xl font-black text-rose-600">
                {stats.highest !== null ? formatINR(stats.highest) : '—'}
              </div>
              <div className="text-[10px] text-gray-400 mt-1">In selected period</div>
            </div>
          </div>
        )}
      </div>

      {/* Chart Section */}
      <div className="card p-6 shadow-sm border border-gray-200 space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-3 border-b border-gray-100">
          <div>
            <h3 className="text-base font-black text-navy-900 tracking-tight flex items-center gap-2">
              <span>Price Trend History</span>
            </h3>
            <p className="text-xs text-gray-400">
              {historyResponse?.coverage_label || 'Verified authentic price history.'}
            </p>
          </div>

          <div className="flex items-center gap-2 self-stretch sm:self-auto justify-between">
            <div className="flex p-1 bg-gray-100 rounded-xl gap-1">
              {(['1M', '3M', '6M', '1Y', 'All'] as const).map((filter) => (
                <button
                  key={filter}
                  onClick={() => setTimeFilter(filter)}
                  className={`text-xs font-black px-2.5 py-1 rounded-lg transition-all cursor-pointer ${
                    timeFilter === filter
                      ? 'bg-white text-navy-900 shadow-xs'
                      : 'text-gray-500 hover:text-navy-900'
                  }`}
                >
                  {filter}
                </button>
              ))}
            </div>

            <button
              onClick={handleShare}
              className="btn-secondary p-2 rounded-xl text-gray-500 hover:text-navy-900 cursor-pointer"
              title="Share"
            >
              <Share2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Chart View or Genuine Missing History State */}
        <div className="h-72 w-full pt-2">
          {loading ? (
            <div className="h-full flex flex-col items-center justify-center gap-3">
              <div className="w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
              <p className="text-xs text-gray-400 font-semibold">Loading verified price history...</p>
            </div>
          ) : !hasChartableHistory ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-6 rounded-2xl bg-gray-50/50 border border-dashed border-gray-200 space-y-2.5">
              <div className="w-10 h-10 rounded-2xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600">
                <Clock className="w-5 h-5" />
              </div>
              <h4 className="text-sm font-black text-navy-900">
                No verified historical price data available yet.
              </h4>
              <p className="text-xs text-gray-400 max-w-sm leading-relaxed">
                PricePing will start tracking this product and build its price history automatically.
                No artificial or estimated points are rendered.
              </p>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartPoints} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="modalPriceGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#6366f1" stopOpacity={0.25} />
                    <stop offset="100%" stopColor="#6366f1" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis
                  dataKey="date"
                  tick={{ fill: '#94a3b8', fontSize: 10, fontWeight: 700 }}
                  tickLine={false}
                  axisLine={{ stroke: '#e2e8f0' }}
                />
                <YAxis
                  tick={{ fill: '#94a3b8', fontSize: 10, fontWeight: 700 }}
                  tickLine={false}
                  axisLine={false}
                  domain={['dataMin - 100', 'dataMax + 100']}
                  tickFormatter={(val) => `₹${(val / 1000).toFixed(0)}k`}
                />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const pt = payload[0].payload;
                      return (
                        <div className="bg-navy-950 border border-gray-800 p-3 rounded-xl shadow-xl text-xs space-y-1 text-white">
                          <div className="flex items-center justify-between gap-3 text-gray-400 text-[10px]">
                            <span>{pt.date}</span>
                            <span className="uppercase font-black text-indigo-400">{pt.store}</span>
                          </div>
                          <div className="text-base font-black text-white">{formatINR(pt.price)}</div>
                          <div className="text-[10px] text-emerald-400 flex items-center gap-1 font-semibold">
                            <CheckCircle2 className="w-3 h-3" />
                            <span>Verified Observation</span>
                          </div>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                {stats.lowest !== null && (
                  <ReferenceLine
                    y={stats.lowest}
                    stroke="#10b981"
                    strokeDasharray="3 3"
                    label={{
                      value: `Low: ₹${stats.lowest}`,
                      fill: '#10b981',
                      fontSize: 10,
                      position: 'insideBottomRight',
                    }}
                  />
                )}
                {stats.average !== null && (
                  <ReferenceLine
                    y={stats.average}
                    stroke="#f59e0b"
                    strokeDasharray="3 3"
                    label={{
                      value: `Avg: ₹${stats.average}`,
                      fill: '#f59e0b',
                      fontSize: 10,
                      position: 'insideTopLeft',
                    }}
                  />
                )}
                <Area
                  type="monotone"
                  dataKey="price"
                  stroke="#6366f1"
                  strokeWidth={2.5}
                  fill="url(#modalPriceGrad)"
                  activeDot={{ r: 5, fill: '#6366f1', stroke: '#ffffff', strokeWidth: 2 }}
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
}
