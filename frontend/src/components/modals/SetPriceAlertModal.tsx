import React, { useState, useEffect } from 'react';
import { X, Bell, Mail, MessageSquare, Check, Sparkles, Loader2, Trash2 } from 'lucide-react';
import type { TrackedProduct, PriceAlert } from '../../types';
import { formatINR, DEFAULT_PRODUCT_IMAGE, PLATFORM_LABELS, getPlatformBadgeClass } from '../../utils/helpers';
import { alertsApi } from '../../services/api';
import toast from 'react-hot-toast';

interface SetPriceAlertModalProps {
  isOpen: boolean;
  onClose: () => void;
  tracker: TrackedProduct | null;
  onAlertSaved: (updatedAlert: PriceAlert) => void;
  onAlertRemoved?: (productId: number) => void;
}

export default function SetPriceAlertModal({
  isOpen,
  onClose,
  tracker,
  onAlertSaved,
  onAlertRemoved,
}: SetPriceAlertModalProps) {
  if (!isOpen || !tracker) return null;

  const product = tracker.product;
  const existingAlert = tracker.alert;
  const currentPrice = product.current_price || 0;
  const platformInfo = PLATFORM_LABELS[product.platform];

  // Initialize form state
  const [targetPrice, setTargetPrice] = useState<string>('');
  const [notifyPush, setNotifyPush] = useState<boolean>(true);
  const [notifyEmail, setNotifyEmail] = useState<boolean>(true);
  const [notifySms, setNotifySms] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [deleting, setDeleting] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string>('');

  useEffect(() => {
    if (existingAlert && existingAlert.target_price) {
      setTargetPrice(String(existingAlert.target_price));
      setNotifyPush(existingAlert.notify_push ?? true);
      setNotifyEmail(existingAlert.notify_email ?? true);
      setNotifySms(existingAlert.notify_sms ?? false);
    } else if (tracker.target_min_price) {
      setTargetPrice(String(tracker.target_min_price));
      setNotifyPush(true);
      setNotifyEmail(true);
      setNotifySms(false);
    } else if (currentPrice > 0) {
      // Default suggested target price is ~10% below current price rounded down to nearest 50
      const suggested = Math.max(1, Math.floor((currentPrice * 0.9) / 10) * 10);
      setTargetPrice(String(suggested));
      setNotifyPush(true);
      setNotifyEmail(true);
      setNotifySms(false);
    } else {
      setTargetPrice('');
    }
    setErrorMsg('');
  }, [tracker, existingAlert, currentPrice]);

  const handleQuickDiscount = (percentage: number) => {
    if (currentPrice > 0) {
      const discounted = Math.max(1, Math.round(currentPrice * (1 - percentage / 100)));
      setTargetPrice(String(discounted));
      setErrorMsg('');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const numPrice = parseFloat(targetPrice.replace(/,/g, '').trim());

    if (isNaN(numPrice) || numPrice <= 0) {
      setErrorMsg('Please enter a valid target price.');
      return;
    }

    if (!notifyPush && !notifyEmail && !notifySms) {
      setErrorMsg('Please select at least one notification channel.');
      return;
    }

    setLoading(true);
    setErrorMsg('');

    try {
      const payload = {
        product_id: product.id,
        alert_type: 'below_price',
        target_price: numPrice,
        notify_push: notifyPush,
        notify_email: notifyEmail,
        notify_sms: notifySms,
        notify_in_app: true,
      };

      const res = await alertsApi.setForProduct(product.id, payload);
      const savedAlert: PriceAlert = res.data;

      toast.success('Price alert set successfully.', {
        icon: '🔔',
        duration: 3500,
      });

      onAlertSaved(savedAlert);
      onClose();
    } catch (err: any) {
      console.error('Failed to set price alert:', err);
      const message = err?.response?.data?.detail || 'Unable to set price alert. Please try again.';
      setErrorMsg(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveAlert = async () => {
    if (!onAlertRemoved) return;
    setDeleting(true);
    try {
      if (existingAlert?.id) {
        await alertsApi.delete(existingAlert.id);
      } else {
        await alertsApi.deleteForProduct(product.id);
      }
      toast.success('Price alert removed.');
      onAlertRemoved(product.id);
      onClose();
    } catch (err: any) {
      console.error('Failed to remove price alert:', err);
      toast.error('Unable to remove price alert.');
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-navy-950/70 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto animate-fade-in">
      <div className="bg-white border border-gray-200 rounded-3xl max-w-md w-full p-6 sm:p-7 relative shadow-2xl space-y-5 animate-scale-in">
        {/* Close Button */}
        <button
          type="button"
          onClick={onClose}
          disabled={loading || deleting}
          className="absolute top-5 right-5 w-8 h-8 rounded-full bg-gray-100 hover:bg-gray-200 text-gray-500 hover:text-navy-900 flex items-center justify-center transition-all cursor-pointer"
          title="Close"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Modal Header */}
        <div className="flex items-center gap-3.5 pr-8">
          <div className="w-12 h-12 rounded-2xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600 flex-shrink-0 shadow-2xs">
            <Bell className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-xl font-black text-navy-900 tracking-tight">
              {existingAlert ? 'Edit Price Alert' : 'Set Price Alert'}
            </h3>
            <p className="text-xs text-gray-500 mt-0.5">
              Get notified the moment this item drops to your budget
            </p>
          </div>
        </div>

        {/* Dynamic Product Snapshot */}
        <div className="flex gap-3.5 p-3.5 rounded-2xl bg-gray-50 border border-gray-100">
          <div className="w-16 h-16 rounded-xl bg-white border border-gray-200 p-1 flex-shrink-0 overflow-hidden flex items-center justify-center shadow-2xs">
            <img
              src={product.product_image || DEFAULT_PRODUCT_IMAGE}
              alt={product.product_name}
              className="w-full h-full object-contain"
              onError={(e) => {
                (e.target as HTMLImageElement).src = DEFAULT_PRODUCT_IMAGE;
              }}
            />
          </div>
          <div className="min-w-0 flex-1 flex flex-col justify-center">
            <div className="flex items-center gap-2 mb-1">
              <span className={`badge ${getPlatformBadgeClass(product.platform)} text-[10px] py-0 px-2`}>
                {platformInfo?.name || product.platform}
              </span>
            </div>
            <p className="text-xs font-bold text-navy-900 line-clamp-1 leading-snug">
              {product.product_name}
            </p>
            <p className="text-xs text-gray-500 font-medium mt-1">
              Current price: <strong className="text-navy-900 font-black text-sm">{formatINR(currentPrice)}</strong>
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Target Price Input */}
          <div>
            <label htmlFor="target-price-input" className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-2">
              Alert me when price reaches:
            </label>
            <div className="relative rounded-2xl shadow-2xs">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-500 font-black text-base">
                ₹
              </div>
              <input
                id="target-price-input"
                type="number"
                min="1"
                step="1"
                required
                value={targetPrice}
                onChange={(e) => {
                  setTargetPrice(e.target.value);
                  setErrorMsg('');
                }}
                placeholder={currentPrice > 0 ? String(Math.round(currentPrice * 0.9)) : '1000'}
                className="w-full pl-9 pr-4 py-3 bg-white border border-gray-300 rounded-2xl text-base font-extrabold text-navy-900 focus:outline-none focus:ring-2 focus:ring-indigo-500/30 focus:border-indigo-600 transition-all placeholder:text-gray-300"
              />
            </div>

            {/* Quick Discount Presets */}
            {currentPrice > 0 && (
              <div className="flex items-center gap-1.5 mt-2 flex-wrap">
                <span className="text-[11px] text-gray-400 font-medium mr-1 flex items-center gap-0.5">
                  <Sparkles className="w-3 h-3 text-amber-500" /> Quick targets:
                </span>
                {[5, 10, 15, 20].map((pct) => {
                  const val = Math.round(currentPrice * (1 - pct / 100));
                  const isSelected = targetPrice === String(val);
                  return (
                    <button
                      key={pct}
                      type="button"
                      onClick={() => handleQuickDiscount(pct)}
                      className={`text-[11px] px-2.5 py-1 rounded-lg border font-bold transition-all cursor-pointer ${
                        isSelected
                          ? 'bg-indigo-600 text-white border-indigo-600 shadow-2xs'
                          : 'bg-white hover:bg-gray-50 text-gray-600 border-gray-200'
                      }`}
                    >
                      {pct}% OFF ({formatINR(val)})
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          {/* Notification Preferences */}
          <div className="pt-2 border-t border-gray-100">
            <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-2.5">
              Notification preferences:
            </label>
            <div className="space-y-2">
              {/* Push Notification */}
              <label className="flex items-center gap-3 p-2.5 rounded-xl border border-gray-200 hover:border-indigo-200 hover:bg-indigo-50/30 transition-all cursor-pointer group">
                <input
                  type="checkbox"
                  checked={notifyPush}
                  onChange={(e) => setNotifyPush(e.target.checked)}
                  className="w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500 border-gray-300 cursor-pointer"
                />
                <Bell className="w-4 h-4 text-indigo-600" />
                <span className="text-xs font-bold text-gray-800 group-hover:text-indigo-950 flex-1">
                  Push Notification
                </span>
                <span className="text-[10px] text-indigo-600 font-semibold bg-indigo-50 px-2 py-0.5 rounded-full border border-indigo-100">
                  Instant
                </span>
              </label>

              {/* Email */}
              <label className="flex items-center gap-3 p-2.5 rounded-xl border border-gray-200 hover:border-indigo-200 hover:bg-indigo-50/30 transition-all cursor-pointer group">
                <input
                  type="checkbox"
                  checked={notifyEmail}
                  onChange={(e) => setNotifyEmail(e.target.checked)}
                  className="w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500 border-gray-300 cursor-pointer"
                />
                <Mail className="w-4 h-4 text-purple-600" />
                <span className="text-xs font-bold text-gray-800 group-hover:text-purple-950 flex-1">
                  Email
                </span>
                <span className="text-[10px] text-gray-500 font-medium">
                  Daily digest & drops
                </span>
              </label>

              {/* WhatsApp / SMS */}
              <label className="flex items-center gap-3 p-2.5 rounded-xl border border-gray-200 hover:border-indigo-200 hover:bg-indigo-50/30 transition-all cursor-pointer group">
                <input
                  type="checkbox"
                  checked={notifySms}
                  onChange={(e) => setNotifySms(e.target.checked)}
                  className="w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500 border-gray-300 cursor-pointer"
                />
                <MessageSquare className="w-4 h-4 text-emerald-600" />
                <span className="text-xs font-bold text-gray-800 group-hover:text-emerald-950 flex-1">
                  WhatsApp / SMS
                </span>
                <span className="text-[10px] text-emerald-600 font-semibold bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-100">
                  High Priority
                </span>
              </label>
            </div>
          </div>

          {/* Error Message */}
          {errorMsg && (
            <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-700 font-semibold">
              {errorMsg}
            </div>
          )}

          {/* Modal Action Buttons */}
          <div className="flex items-center justify-between gap-3 pt-3 border-t border-gray-100">
            {existingAlert && onAlertRemoved ? (
              <button
                type="button"
                onClick={handleRemoveAlert}
                disabled={loading || deleting}
                className="text-xs font-bold text-rose-600 hover:text-rose-700 flex items-center gap-1.5 py-2 px-2 hover:bg-rose-50 rounded-xl transition-all cursor-pointer disabled:opacity-50"
                title="Remove active alert"
              >
                {deleting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Trash2 className="w-3.5 h-3.5" />}
                <span>Remove Alert</span>
              </button>
            ) : (
              <div />
            )}

            <div className="flex items-center gap-2.5">
              <button
                type="button"
                onClick={onClose}
                disabled={loading || deleting}
                className="btn-secondary py-2.5 px-4 text-xs font-bold cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading || deleting}
                className="btn-primary py-2.5 px-5 text-xs font-bold inline-flex items-center gap-2 cursor-pointer shadow-md hover:shadow-lg"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Saving...</span>
                  </>
                ) : (
                  <>
                    {existingAlert ? <Check className="w-4 h-4" /> : <Bell className="w-4 h-4" />}
                    <span>{existingAlert ? 'Save Changes' : 'Set Price Alert'}</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
