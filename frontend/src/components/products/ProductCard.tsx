import { useState, useRef, useEffect } from 'react';
import {
  ExternalLink, TrendingDown, TrendingUp, Star, Bell, Check, MoreVertical,
  Trash2, History, Eye
} from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import {
  formatINR, timeAgo, PLATFORM_LABELS, AVAILABILITY_LABELS,
  getPlatformBadgeClass, DEFAULT_PRODUCT_IMAGE
} from '../../utils/helpers';
import type { TrackedProduct } from '../../types';

interface ProductCardProps {
  tracker: TrackedProduct;
  onSetAlert?: (tracker: TrackedProduct) => void;
  onViewHistory?: (tracker: TrackedProduct) => void;
  onRefresh?: (productId: number, trackerId: number) => void;
  onPause?: (trackerId: number) => void;
  onResume?: (trackerId: number) => void;
  onDelete?: (tracker: TrackedProduct) => void;
  isLoading?: boolean;
}

export default function ProductCard({
  tracker,
  onSetAlert,
  onViewHistory,
  onRefresh: _onRefresh,
  onPause: _onPause,
  onResume: _onResume,
  onDelete,
  isLoading = false,
}: ProductCardProps) {
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const p = tracker.product;
  const platformInfo = PLATFORM_LABELS[p.platform];
  const availInfo = AVAILABILITY_LABELS[p.availability];
  const isPaused = tracker.tracking_status === 'paused';
  const hasDrop = p.original_price && p.current_price && p.current_price < p.original_price;

  // Active alert detection: either from tracker.alert or tracker.target_min_price
  const hasActiveAlert = Boolean(
    (tracker.alert && tracker.alert.target_price && tracker.alert.alert_status === 'active') ||
    (tracker.target_min_price && tracker.target_min_price > 0)
  );

  const activeAlertTargetPrice = tracker.alert?.target_price ?? tracker.target_min_price ?? null;

  // Close 3-dot dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    };
    if (menuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [menuOpen]);

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
              src={p.product_image || DEFAULT_PRODUCT_IMAGE}
              alt={p.product_name}
              className="w-full h-full object-contain group-hover/img:scale-105 transition-transform"
              onError={(e) => {
                (e.target as HTMLImageElement).src = DEFAULT_PRODUCT_IMAGE;
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

            <div className="text-[11px] text-gray-400 mt-1">
              Checked: {p.last_checked ? timeAgo(p.last_checked) : 'Recently'}
            </div>
          </div>
        </div>

        {/* Low / High trend markers */}
        {(p.lowest_price || p.highest_price) && (
          <div className="px-5 pb-2.5 flex items-center gap-4 text-xs font-semibold">
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

        {/* Active Alert Indicator Badge */}
        {hasActiveAlert && activeAlertTargetPrice && (
          <div className="px-5 pb-3">
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-indigo-50/80 border border-indigo-200/80 text-indigo-700 text-xs font-bold shadow-2xs">
              <Bell className="w-3.5 h-3.5 text-indigo-600 stroke-[2.5]" />
              <span>Alert: {formatINR(activeAlertTargetPrice)}</span>
            </div>
          </div>
        )}
      </div>

      {/* Action Area: [ Set Alert / Alert Set ]  [ Buy ↗ ]  [ ⋮ ] */}
      <div className="p-3.5 sm:p-4 border-t border-gray-100 flex items-center gap-2 bg-gray-50/40">
        {/* Set Alert / Alert Set Button */}
        {hasActiveAlert ? (
          <button
            type="button"
            onClick={() => onSetAlert?.(tracker)}
            disabled={isLoading}
            className="flex-1 text-xs py-2.5 px-3 rounded-2xl flex items-center justify-center gap-1.5 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-300 font-bold transition-all cursor-pointer shadow-2xs active:scale-95"
            title="Click to modify active price alert"
          >
            <Check className="w-3.5 h-3.5 text-emerald-600 stroke-[2.5]" />
            <span>✓ Alert Set</span>
          </button>
        ) : (
          <button
            type="button"
            onClick={() => onSetAlert?.(tracker)}
            disabled={isLoading}
            className="flex-1 text-xs py-2.5 px-3 rounded-2xl flex items-center justify-center gap-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 hover:text-indigo-800 border border-indigo-200 font-bold transition-all cursor-pointer shadow-2xs active:scale-95"
            title="Set a price drop alert for this product"
          >
            <Bell className="w-3.5 h-3.5 text-indigo-600" />
            <span>Set Alert</span>
          </button>
        )}

        {/* Primary Buy CTA */}
        <a
          href={p.product_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-1 py-2.5 px-3 rounded-2xl bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white text-xs font-black text-center flex items-center justify-center gap-1 shadow-sm hover:shadow-md transition-all cursor-pointer active:scale-95"
          title={`Buy on ${platformInfo?.name || p.platform}`}
        >
          <span>Buy</span>
          <ExternalLink className="w-3.5 h-3.5 ml-0.5" />
        </a>

        {/* Three-Dot Menu (⋮) */}
        <div className="relative" ref={menuRef}>
          <button
            type="button"
            onClick={() => setMenuOpen(!menuOpen)}
            className={`w-9 h-9 rounded-2xl border transition-all flex items-center justify-center cursor-pointer shadow-2xs ${
              menuOpen
                ? 'bg-gray-200 border-gray-300 text-navy-900'
                : 'bg-white hover:bg-gray-100 border-gray-200 text-gray-600'
            }`}
            title="More product options"
            aria-label="More options"
          >
            <MoreVertical className="w-4 h-4" />
          </button>

          {/* Dropdown Menu */}
          {menuOpen && (
            <div className="absolute right-0 bottom-full mb-2 w-52 bg-white rounded-2xl shadow-xl border border-gray-200 p-1.5 z-40 animate-scale-in">
              <button
                type="button"
                onClick={() => {
                  setMenuOpen(false);
                  if (onDelete) onDelete(tracker);
                }}
                className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-bold text-rose-600 hover:bg-rose-50 rounded-xl transition-colors cursor-pointer text-left"
              >
                <Trash2 className="w-3.5 h-3.5 text-rose-500 flex-shrink-0" />
                <span>Remove from Tracking</span>
              </button>

              <button
                type="button"
                onClick={() => {
                  setMenuOpen(false);
                  if (onViewHistory) onViewHistory(tracker);
                }}
                className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-bold text-gray-700 hover:bg-gray-50 hover:text-navy-900 rounded-xl transition-colors cursor-pointer text-left"
              >
                <History className="w-3.5 h-3.5 text-indigo-600 flex-shrink-0" />
                <span>View Price History</span>
              </button>

              <button
                type="button"
                onClick={() => {
                  setMenuOpen(false);
                  navigate(`/product/${tracker.id}`);
                }}
                className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-bold text-gray-700 hover:bg-gray-50 hover:text-navy-900 rounded-xl transition-colors cursor-pointer text-left"
              >
                <Eye className="w-3.5 h-3.5 text-gray-500 flex-shrink-0" />
                <span>Open Product</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
