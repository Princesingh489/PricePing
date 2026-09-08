import { useState, useRef, useEffect } from 'react';
import { formatINR, ALERT_STATUS_LABELS, PLATFORM_LABELS, DEFAULT_PRODUCT_IMAGE, timeAgo } from '../../utils/helpers';
import type { PriceAlert } from '../../types';
import {
  Bell, BellOff, Trash2, ExternalLink, Target, Percent, TrendingDown,
  CheckCircle2, MoreVertical, Edit3, Zap, ShoppingBag
} from 'lucide-react';

interface AlertCardProps {
  alert: PriceAlert;
  onToggle: (alert: PriceAlert) => void;
  onDelete: (id: number) => void;
  onEdit?: (alert: PriceAlert) => void;
}

const ALERT_TYPE_ICONS: Record<string, any> = {
  below_price: Target,
  price_range: TrendingDown,
  percentage_drop: Percent,
};

const ALERT_TYPE_LABELS: Record<string, string> = {
  below_price: 'Price Target',
  price_range: 'Price Range',
  percentage_drop: '% Drop',
};

function getStatusStyle(status: string) {
  switch (status) {
    case 'active': return 'bg-emerald-100 text-emerald-700 border border-emerald-200';
    case 'triggered': return 'bg-amber-100 text-amber-700 border border-amber-200';
    case 'snoozed': return 'bg-sky-100 text-sky-700 border border-sky-200';
    case 'disabled': return 'bg-gray-100 text-gray-500 border border-gray-200';
    default: return 'bg-gray-100 text-gray-500 border border-gray-200';
  }
}

export default function AlertCard({ alert, onToggle, onDelete, onEdit }: AlertCardProps) {
  const product = alert.product;
  const isActive = alert.alert_status === 'active';
  const isTriggered = alert.alert_status === 'triggered';
  const platformInfo = product?.platform ? PLATFORM_LABELS[product.platform] : undefined;
  const Icon = ALERT_TYPE_ICONS[alert.alert_type] || Bell;

  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const curPrice = product?.current_price || 0;
  const target = alert.target_price || alert.minimum_price || 0;
  const isReached = curPrice > 0 && target > 0 && curPrice <= target;

  let progressPct = 0;
  if (curPrice > 0 && target > 0) {
    if (isReached) {
      progressPct = 100;
    } else {
      const base = alert.base_price || curPrice * 1.2;
      const totalSpan = Math.max(base - target, 1);
      const covered = Math.max(base - curPrice, 0);
      progressPct = Math.min(Math.round((covered / totalSpan) * 100), 95);
    }
  }

  const gapToTarget = target > 0 && curPrice > target ? curPrice - target : 0;
  const savedIfNow = isReached && product?.original_price ? product.original_price - curPrice : 0;

  const getAlertDescription = (): string => {
    if (alert.alert_type === 'below_price') return `Alert when ≤ ${formatINR(alert.target_price)}`;
    if (alert.alert_type === 'price_range') return `Range: ${formatINR(alert.minimum_price)} – ${formatINR(alert.maximum_price)}`;
    if (alert.alert_type === 'percentage_drop') return `Alert on ${alert.percentage_drop}% drop`;
    return 'Custom alert';
  };

  const notifyChannels = [
    alert.notify_email && { label: 'Email', emoji: '📧' },
    alert.notify_push && { label: 'Push', emoji: '🔔' },
    alert.notify_sms && { label: 'SMS', emoji: '📱' },
    alert.notify_in_app && { label: 'In-App', emoji: '🔵' },
  ].filter(Boolean) as { label: string; emoji: string }[];

  return (
    <div
      className={`group relative rounded-2xl border transition-all duration-300 overflow-hidden ${
        isTriggered
          ? 'border-amber-300 bg-gradient-to-r from-amber-50/80 to-yellow-50/60 shadow-lg shadow-amber-100'
          : isActive
          ? 'border-indigo-200/70 bg-white hover:border-indigo-400 hover:shadow-xl hover:shadow-indigo-100/60'
          : 'border-gray-200 bg-gray-50/70 opacity-75'
      }`}
    >
      {/* Top accent bar */}
      {isTriggered && (
        <div className="h-1 w-full bg-gradient-to-r from-amber-400 via-orange-400 to-yellow-400" />
      )}
      {isActive && !isTriggered && (
        <div className="h-1 w-full bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      )}

      <div className="p-5 sm:p-6">
        <div className="flex gap-4 items-start">
          {/* Product Image */}
          <div className={`w-16 h-16 sm:w-20 sm:h-20 rounded-2xl flex items-center justify-center p-2 flex-shrink-0 overflow-hidden border ${
            isActive ? 'bg-indigo-50/60 border-indigo-100' : 'bg-gray-50 border-gray-200'
          }`}>
            <img
              src={product?.product_image || DEFAULT_PRODUCT_IMAGE}
              alt={product?.product_name || 'Product'}
              className="w-full h-full object-contain"
              onError={(e) => { (e.target as HTMLImageElement).src = DEFAULT_PRODUCT_IMAGE; }}
            />
          </div>

          {/* Main Content */}
          <div className="flex-1 min-w-0">
            {/* Top row: badges + 3-dot menu */}
            <div className="flex items-start justify-between gap-2">
              <div className="flex flex-wrap items-center gap-1.5">
                <span className={`inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full ${getStatusStyle(alert.alert_status)}`}>
                  {isTriggered ? <Zap className="w-2.5 h-2.5" /> : isActive ? <Bell className="w-2.5 h-2.5" /> : <BellOff className="w-2.5 h-2.5" />}
                  {ALERT_STATUS_LABELS[alert.alert_status]?.label || alert.alert_status}
                </span>
                {platformInfo && (
                  <span className={`inline-flex items-center text-[10px] font-semibold px-2 py-0.5 rounded-full border ${platformInfo.bg} ${platformInfo.color}`}>
                    {platformInfo.name}
                  </span>
                )}
                <span className="inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-600 border border-indigo-200">
                  <Icon className="w-2.5 h-2.5" />
                  {ALERT_TYPE_LABELS[alert.alert_type]}
                </span>
              </div>

              {/* 3-dot menu */}
              <div className="relative flex-shrink-0" ref={menuRef}>
                <button
                  onClick={() => setMenuOpen((v) => !v)}
                  className="w-8 h-8 flex items-center justify-center rounded-xl text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 transition-all cursor-pointer"
                  title="More options"
                >
                  <MoreVertical className="w-4 h-4" />
                </button>
                {menuOpen && (
                  <div className="absolute right-0 top-9 z-50 w-44 bg-white rounded-2xl shadow-2xl border border-gray-100 py-1.5 overflow-hidden">
                    {product?.product_url && (
                      <a
                        href={product.product_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-indigo-50 hover:text-indigo-700 transition-colors"
                        onClick={() => setMenuOpen(false)}
                      >
                        <ShoppingBag className="w-4 h-4 text-indigo-500" /> Buy Now
                      </a>
                    )}
                    {onEdit && (
                      <button
                        onClick={() => { setMenuOpen(false); onEdit(alert); }}
                        className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-indigo-50 hover:text-indigo-700 transition-colors cursor-pointer"
                      >
                        <Edit3 className="w-4 h-4 text-indigo-500" /> Edit Alert
                      </button>
                    )}
                    <button
                      onClick={() => { setMenuOpen(false); onToggle(alert); }}
                      className={`w-full flex items-center gap-3 px-4 py-2.5 text-sm transition-colors cursor-pointer ${
                        isActive ? 'text-amber-700 hover:bg-amber-50' : 'text-emerald-700 hover:bg-emerald-50'
                      }`}
                    >
                      {isActive ? <BellOff className="w-4 h-4" /> : <Bell className="w-4 h-4" />}
                      {isActive ? 'Pause Alert' : 'Enable Alert'}
                    </button>
                    <div className="my-1 border-t border-gray-100" />
                    <button
                      onClick={() => { setMenuOpen(false); onDelete(alert.id); }}
                      className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 transition-colors cursor-pointer"
                    >
                      <Trash2 className="w-4 h-4" /> Delete Alert
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Product name */}
            <h3 className="font-bold text-sm sm:text-base text-gray-900 line-clamp-1 mt-2 mb-3">
              {product?.product_name || 'Unknown Product'}
            </h3>

            {/* Price comparison row */}
            <div className="flex flex-wrap items-end gap-4 mb-3">
              <div>
                <p className="text-[10px] text-gray-400 font-semibold uppercase tracking-wide mb-0.5">Current Price</p>
                <p className={`text-xl font-black ${isReached ? 'text-emerald-600' : 'text-gray-900'}`}>
                  {formatINR(curPrice) || '—'}
                </p>
              </div>
              {target > 0 && (
                <>
                  <div className="text-gray-300 text-lg mb-1">→</div>
                  <div>
                    <p className="text-[10px] text-indigo-500 font-semibold uppercase tracking-wide mb-0.5">Target Price</p>
                    <p className="text-lg font-black text-indigo-700">{formatINR(target)}</p>
                  </div>
                  {gapToTarget > 0 && (
                    <div className="ml-auto">
                      <p className="text-[10px] text-gray-400 font-semibold uppercase tracking-wide mb-0.5">Gap to Target</p>
                      <p className="text-sm font-bold text-rose-500">-{formatINR(gapToTarget)}</p>
                    </div>
                  )}
                  {isReached && savedIfNow > 0 && (
                    <div className="ml-auto">
                      <p className="text-[10px] text-emerald-600 font-semibold uppercase tracking-wide mb-0.5">You Save</p>
                      <p className="text-sm font-bold text-emerald-600">+{formatINR(savedIfNow)}</p>
                    </div>
                  )}
                </>
              )}
            </div>

            {/* Progress bar */}
            {target > 0 && (
              <div className="mb-3">
                <div className="flex justify-between items-center text-[10px] font-semibold mb-1.5">
                  <span className={isReached ? 'text-emerald-600 flex items-center gap-1' : 'text-gray-500'}>
                    {isReached ? <><CheckCircle2 className="w-3 h-3" /> 🎉 Target Reached!</> : 'Watching for price drop...'}
                  </span>
                  <span className={`${progressPct >= 80 ? 'text-emerald-600' : 'text-gray-400'}`}>
                    {progressPct}% to target
                  </span>
                </div>
                <div className="w-full h-2 rounded-full bg-gray-100 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-700 ease-out ${
                      isReached
                        ? 'bg-gradient-to-r from-emerald-400 to-emerald-500'
                        : progressPct >= 70
                        ? 'bg-gradient-to-r from-indigo-500 to-purple-500'
                        : 'bg-gradient-to-r from-indigo-400 to-blue-500'
                    }`}
                    style={{ width: `${progressPct}%` }}
                  />
                </div>
              </div>
            )}

            {/* Bottom row: alert description + notifications + time + buy */}
            <div className="flex flex-wrap items-center gap-2 justify-between">
              <div className="flex flex-wrap gap-2 items-center">
                <span className="text-[11px] font-semibold text-indigo-600 bg-indigo-50 px-2.5 py-1 rounded-lg border border-indigo-100">
                  {getAlertDescription()}
                </span>
                {notifyChannels.map((ch) => (
                  <span key={ch.label} className="text-[10px] font-semibold text-gray-500 bg-gray-100 px-2 py-0.5 rounded-lg">
                    {ch.emoji} {ch.label}
                  </span>
                ))}
                {alert.last_triggered_at && (
                  <span className="text-[10px] text-amber-600 font-semibold bg-amber-50 px-2 py-0.5 rounded-lg border border-amber-100">
                    ⚡ Triggered {timeAgo(alert.last_triggered_at)}
                  </span>
                )}
                <span className="text-[10px] text-gray-400">Set {timeAgo(alert.created_at)}</span>
              </div>
              {product?.product_url && (
                <a
                  href={product.product_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`inline-flex items-center gap-1.5 text-xs font-bold px-3 py-1.5 rounded-xl transition-all ${
                    isReached
                      ? 'bg-emerald-500 text-white hover:bg-emerald-600 shadow-md shadow-emerald-200'
                      : 'bg-gray-100 text-gray-600 hover:bg-indigo-50 hover:text-indigo-700'
                  }`}
                >
                  <ExternalLink className="w-3 h-3" />
                  {isReached ? 'Buy Now 🎉' : 'View'}
                </a>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
