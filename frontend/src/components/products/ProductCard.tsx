import { ExternalLink, Trash2, TrendingDown, TrendingUp, Star } from 'lucide-react';
import { Link } from 'react-router-dom';
import { formatINR, timeAgo, PLATFORM_LABELS, AVAILABILITY_LABELS, getPlatformBadgeClass } from '../../utils/helpers';
import type { TrackedProduct } from '../../types';

interface ProductCardProps {
  tracker: TrackedProduct;
  onViewHistory?: (tracker: TrackedProduct) => void;
  onRefresh?: (productId: number, trackerId: number) => void;
  onPause?: (trackerId: number) => void;
  onResume?: (trackerId: number) => void;
  onDelete?: (tracker: TrackedProduct) => void;
  isLoading?: boolean;
}

export default function ProductCard({
  tracker,
  onViewHistory: _onViewHistory,
  onRefresh: _onRefresh,
  onPause: _onPause,
  onResume: _onResume,
  onDelete,
  isLoading = false,
}: ProductCardProps) {
  const p = tracker.product;
  const platformInfo = PLATFORM_LABELS[p.platform];
  const availInfo = AVAILABILITY_LABELS[p.availability];
  const isPaused = tracker.tracking_status === 'paused';
  const hasDrop = p.original_price && p.current_price && p.current_price < p.original_price;

  return (
    <div className={`card-hover flex flex-col justify-between ${isPaused ? 'opacity-70 bg-gray-50/50' : 'bg-white'}`}>
      <div>
        {/* Top bar: platform badge + stock status */}
        <div className="p-3.5 sm:p-4 flex items-center justify-between border-b border-gray-100 bg-gray-50/40">
          <span className={`badge ${getPlatformBadgeClass(p.platform)} text-[11px]`}>
            {platformInfo?.name || p.platform}
          </span>
          <div className="flex items-center gap-1.5">
            <span className={`badge ${availInfo?.className || 'badge-info'} text-[11px]`}>
              {availInfo?.label || 'Tracked'}
            </span>
            {isPaused && (
              <span className="badge badge-warning text-[10px]">Paused</span>
            )}
          </div>
        </div>

        {/* Product image & metadata */}
        <div className="p-4 sm:p-5 flex gap-4">
          <Link
            to={`/product/${tracker.id}`}
            className="w-20 h-20 rounded-2xl bg-gray-50 border border-gray-200 flex items-center justify-center p-2 flex-shrink-0 shadow-2xs overflow-hidden cursor-pointer hover:border-indigo-300 transition-colors group/img"
            title="Click to view all details"
          >
            <img
              src={p.product_image || 'https://placehold.co/80x80/f8fafc/6366f1?text=Product'}
              alt={p.product_name}
              className="w-full h-full object-contain group-hover/img:scale-105 transition-transform"
              onError={(e) => {
                (e.target as HTMLImageElement).src = 'https://placehold.co/80x80/f8fafc/6366f1?text=Product';
              }}
            />
          </Link>

          <div className="flex-1 min-w-0">
            <Link
              to={`/product/${tracker.id}`}
              className="block group/title cursor-pointer"
              title="Click to view all details"
            >
              <h3 className="text-sm font-bold text-navy-900 line-clamp-2 leading-snug group-hover/title:text-indigo-600 transition-colors">
                {p.product_name}
              </h3>
            </Link>

            {/* Ratings */}
            {p.rating && p.rating > 0 && (
              <div className="flex items-center gap-1.5 mt-1.5 text-xs">
                <span className="flex items-center gap-1 bg-amber-50 border border-amber-200 px-1.5 py-0.5 rounded text-amber-700 font-extrabold text-[10px]">
                  <Star className="w-3 h-3 fill-amber-400 text-amber-400" />
                  {p.rating.toFixed(1)}
                </span>
                {p.rating_count && p.rating_count > 0 && (
                  <span className="text-gray-400 text-[10px] font-medium">
                    ({p.rating_count.toLocaleString('en-IN')})
                  </span>
                )}
              </div>
            )}

            {/* Price display */}
            <div className="mt-2">
              <div className="flex items-baseline gap-2 flex-wrap">
                <span className="text-xl font-black text-navy-900 tracking-tight">
                  {formatINR(p.current_price)}
                </span>
                {hasDrop && (
                  <span className="text-xs text-gray-400 line-through font-medium">
                    {formatINR(p.original_price)}
                  </span>
                )}
              </div>

              {hasDrop && (
                <div className="flex items-center gap-1.5 mt-1 flex-wrap">
                  {p.discount_percentage && p.discount_percentage > 0 && (
                    <span className="text-[10px] bg-emerald-100 text-emerald-800 border border-emerald-200 font-black px-1.5 py-0.5 rounded">
                      {p.discount_percentage.toFixed(0)}% OFF
                    </span>
                  )}
                  {(p.saved_amount || (p.original_price && p.current_price ? p.original_price - p.current_price : 0)) > 0 && (
                    <span className="text-[11px] text-emerald-700 font-bold">
                      Save {formatINR(p.saved_amount || (p.original_price! - p.current_price!))}
                    </span>
                  )}
                </div>
              )}
            </div>

            {/* Target Price */}
            {tracker.target_min_price && (
              <div className="text-xs text-gray-500 mt-1.5 font-medium">
                Target: <span className="text-navy-900 font-bold">{formatINR(tracker.target_min_price)}</span>
                {tracker.target_max_price ? ` – ${formatINR(tracker.target_max_price)}` : ''}
              </div>
            )}

            <div className="text-[11px] text-gray-400 mt-1">
              Checked: {p.last_checked ? timeAgo(p.last_checked) : 'Recently'}
            </div>
          </div>
        </div>

        {/* Low / High trend markers */}
        {(p.lowest_price || p.highest_price) && (
          <div className="px-5 pb-3.5 flex items-center gap-4 text-xs font-semibold">
            {p.lowest_price && (
              <span className="flex items-center gap-1 text-emerald-700">
                <TrendingDown className="w-3.5 h-3.5" /> Low: {formatINR(p.lowest_price)}
              </span>
            )}
            {p.highest_price && (
              <span className="flex items-center gap-1 text-rose-700">
                <TrendingUp className="w-3.5 h-3.5" /> High: {formatINR(p.highest_price)}
              </span>
            )}
          </div>
        )}
      </div>

      {/* Action buttons: Delete & Buy only */}
      <div className="p-3.5 sm:p-4 border-t border-gray-100 flex items-center gap-2.5 bg-gray-50/40">
        {onDelete && (
          <button
            onClick={() => onDelete(tracker)}
            disabled={isLoading}
            className="btn-secondary flex-1 text-xs py-2.5 px-3 flex items-center justify-center gap-1.5 text-rose-600 hover:text-rose-700 hover:bg-rose-50 hover:border-rose-300 font-bold transition-all cursor-pointer shadow-2xs"
            title="Remove from tracked products"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Delete</span>
          </button>
        )}

        <a
          href={p.product_url}
          target="_blank"
          rel="noopener noreferrer"
          className="btn-primary text-xs py-2.5 px-3 flex-1 flex items-center justify-center gap-1 font-bold shadow-sm"
        >
          <span>Buy</span>
          <ExternalLink className="w-3.5 h-3.5 ml-0.5" />
        </a>
      </div>
    </div>
  );
}
