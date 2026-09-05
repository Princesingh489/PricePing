import { formatINR, ALERT_STATUS_LABELS, PLATFORM_LABELS } from '../../utils/helpers';
import type { PriceAlert } from '../../types';
import { Bell, BellOff, Trash2, ExternalLink, TrendingDown, Target, Percent, CheckCircle2 } from 'lucide-react';

interface AlertCardProps {
  alert: PriceAlert;
  onToggle: (alert: PriceAlert) => void;
  onDelete: (id: number) => void;
}

const ALERT_TYPE_ICONS: Record<string, any> = {
  below_price: Target,
  price_range: TrendingDown,
  percentage_drop: Percent,
};

const ALERT_TYPE_LABELS: Record<string, string> = {
  below_price: 'Below Target',
  price_range: 'Price Range',
  percentage_drop: '% Drop Alert',
};

export default function AlertCard({ alert, onToggle, onDelete }: AlertCardProps) {
  const product = alert.product;
  const statusInfo = ALERT_STATUS_LABELS[alert.alert_status];
  const Icon = ALERT_TYPE_ICONS[alert.alert_type] || Bell;
  const isActive = alert.alert_status === 'active';
  const platformInfo = product?.platform ? PLATFORM_LABELS[product.platform] : undefined;

  // Calculate target progress
  const curPrice = product?.current_price || 0;
  const target = alert.target_price || alert.minimum_price || 0;
  const isReached = curPrice > 0 && target > 0 && curPrice <= target;

  let progressPct = 0;
  if (curPrice > 0 && target > 0) {
    if (isReached) {
      progressPct = 100;
    } else {
      const base = alert.base_price || curPrice * 1.15;
      const totalSpan = Math.max(base - target, 1);
      const covered = Math.max(base - curPrice, 0);
      progressPct = Math.min(Math.round((covered / totalSpan) * 100), 95);
    }
  }

  const getAlertDescription = (): string => {
    if (alert.alert_type === 'below_price') return `Target: ${formatINR(alert.target_price)}`;
    if (alert.alert_type === 'price_range') return `Range: ${formatINR(alert.minimum_price)} – ${formatINR(alert.maximum_price)}`;
    if (alert.alert_type === 'percentage_drop') return `Alert on ${alert.percentage_drop}% drop`;
    return 'Custom alert';
  };

  return (
    <div className={`card p-5 sm:p-6 flex flex-col lg:flex-row gap-5 items-start lg:items-center justify-between transition-all ${
      !isActive ? 'opacity-70 bg-gray-50/60' : 'bg-white hover:border-indigo-300 hover:shadow-card-hover'
    }`}>
      {/* Product & Alert Info */}
      <div className="flex gap-4 items-start min-w-0 flex-1">
        <div className="w-16 h-16 rounded-2xl bg-gray-50 border border-gray-200 flex items-center justify-center p-2 flex-shrink-0 overflow-hidden">
          <img
            src={product?.product_image || 'https://placehold.co/64x64/f8fafc/6366f1?text=Product'}
            alt={product?.product_name || 'Product'}
            className="w-full h-full object-contain"
            onError={(e) => {
              (e.target as HTMLImageElement).src = 'https://placehold.co/64x64/f8fafc/6366f1?text=Product';
            }}
          />
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2 mb-1.5">
            {platformInfo && (
              <span className={`badge ${platformInfo.bg} ${platformInfo.color} text-[10px]`}>
                {platformInfo.name}
              </span>
            )}
            <span className={`badge ${statusInfo.className} text-[10px]`}>
              {statusInfo.label}
            </span>
            <span className="badge bg-indigo-50 text-indigo-700 border border-indigo-200 text-[10px]">
              <Icon className="w-3 h-3" /> {ALERT_TYPE_LABELS[alert.alert_type]}
            </span>
          </div>

          <h3 className="font-bold text-navy-900 text-sm sm:text-base line-clamp-1">
            {product?.product_name}
          </h3>

          {/* Current vs Target */}
          <div className="flex items-center gap-4 mt-2 text-xs flex-wrap">
            <span className="text-gray-500">
              Current: <strong className="text-navy-900 text-sm font-black">{formatINR(product?.current_price)}</strong>
            </span>
            <span className="text-indigo-600 font-bold">
              {getAlertDescription()}
            </span>
          </div>

          {/* Target Progress Bar */}
          {target > 0 && (
            <div className="mt-3 max-w-md">
              <div className="flex items-center justify-between text-[11px] mb-1 font-semibold">
                <span className={isReached ? 'text-emerald-700 font-bold flex items-center gap-1' : 'text-gray-500'}>
                  {isReached ? (
                    <>
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                      🎉 Target Price Reached!
                    </>
                  ) : (
                    'Waiting for price drop'
                  )}
                </span>
                <span className="text-gray-400">{progressPct}% toward target</span>
              </div>

              <div className="w-full h-2 rounded-full bg-gray-100 overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    isReached ? 'bg-emerald-500' : 'bg-gradient-brand'
                  }`}
                  style={{ width: `${progressPct}%` }}
                />
              </div>
            </div>
          )}

          {/* Active notification channels */}
          <div className="flex flex-wrap gap-1.5 mt-3 text-[10px] font-semibold text-gray-500">
            {alert.notify_email && <span className="bg-gray-100 px-2 py-0.5 rounded-md">📧 Email</span>}
            {alert.notify_push && <span className="bg-gray-100 px-2 py-0.5 rounded-md">🔔 Push</span>}
            {alert.notify_sms && <span className="bg-gray-100 px-2 py-0.5 rounded-md">📱 SMS</span>}
            {alert.notify_in_app && <span className="bg-gray-100 px-2 py-0.5 rounded-md">🔵 In-App</span>}
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex sm:flex-row lg:flex-col items-center gap-2 w-full lg:w-auto justify-end border-t lg:border-t-0 pt-3 lg:pt-0 border-gray-100">
        {product?.product_url && (
          <a
            href={product.product_url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-secondary text-xs py-2 px-3 flex-1 lg:flex-initial"
          >
            <ExternalLink className="w-3.5 h-3.5" /> Buy Store
          </a>
        )}

        <button
          onClick={() => onToggle(alert)}
          className={`text-xs py-2 px-3 rounded-xl border flex items-center justify-center gap-1.5 font-bold transition-all flex-1 lg:flex-initial cursor-pointer ${
            isActive
              ? 'bg-amber-50 text-amber-700 border-amber-200 hover:bg-amber-100'
              : 'bg-emerald-50 text-emerald-700 border-emerald-200 hover:bg-emerald-100'
          }`}
        >
          {isActive ? <BellOff className="w-3.5 h-3.5" /> : <Bell className="w-3.5 h-3.5" />}
          {isActive ? 'Pause' : 'Enable'}
        </button>

        <button
          onClick={() => onDelete(alert.id)}
          className="btn-danger-outline py-2 px-3 flex-1 lg:flex-initial"
          title="Delete alert"
        >
          <Trash2 className="w-3.5 h-3.5" /> Delete
        </button>
      </div>
    </div>
  );
}
