import React, { useState, useEffect } from "react";
import { X, Bell, Mail, MessageSquare, Check, Sparkles, Loader2, Trash2 } from "lucide-react";
import type { PriceAlert } from "../../types";
import { formatINR, DEFAULT_PRODUCT_IMAGE, PLATFORM_LABELS, getPlatformBadgeClass } from "../../utils/helpers";
import { alertsApi } from "../../services/api";
import toast from "react-hot-toast";

interface EditAlertModalProps {
  isOpen: boolean;
  onClose: () => void;
  alert: PriceAlert | null;
  onAlertUpdated: (updated: PriceAlert) => void;
  onAlertDeleted: (id: number) => void;
}

export default function EditAlertModal({
  isOpen,
  onClose,
  alert: alertData,
  onAlertUpdated,
  onAlertDeleted,
}: EditAlertModalProps) {
  const [targetPrice, setTargetPrice] = useState<string>("");
  const [notifyPush, setNotifyPush] = useState<boolean>(true);
  const [notifyEmail, setNotifyEmail] = useState<boolean>(true);
  const [notifySms, setNotifySms] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [deleting, setDeleting] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string>("");

  useEffect(() => {
    if (alertData) {
      setTargetPrice(
        alertData.target_price ? String(alertData.target_price) :
        alertData.minimum_price ? String(alertData.minimum_price) : ""
      );
      setNotifyPush(alertData.notify_push ?? true);
      setNotifyEmail(alertData.notify_email ?? true);
      setNotifySms(alertData.notify_sms ?? false);
      setErrorMsg("");
    }
  }, [alertData]);

  if (!isOpen || !alertData) return null;

  const product = alertData.product;
  const currentPrice = product?.current_price || 0;
  const platformInfo = product?.platform ? PLATFORM_LABELS[product.platform] : undefined;

  const handleQuickDiscount = (percentage: number) => {
    if (currentPrice > 0) {
      const discounted = Math.max(1, Math.round(currentPrice * (1 - percentage / 100)));
      setTargetPrice(String(discounted));
      setErrorMsg("");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const numPrice = parseFloat(targetPrice.replace(/,/g, "").trim());
    if (isNaN(numPrice) || numPrice <= 0) {
      setErrorMsg("Please enter a valid target price.");
      return;
    }
    if (!notifyPush && !notifyEmail && !notifySms) {
      setErrorMsg("Please select at least one notification channel.");
      return;
    }
    setLoading(true);
    setErrorMsg("");
    try {
      const payload = {
        target_price: numPrice,
        notify_push: notifyPush,
        notify_email: notifyEmail,
        notify_sms: notifySms,
        notify_in_app: true,
      };
      const res = await alertsApi.update(alertData.id, payload);
      toast.success("Alert updated successfully.", { icon: "??", duration: 3000 });
      onAlertUpdated(res.data);
      onClose();
    } catch (err: any) {
      const message = err?.response?.data?.detail || "Unable to update alert.";
      setErrorMsg(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm("Delete this alert?")) return;
    setDeleting(true);
    try {
      await alertsApi.delete(alertData.id);
      toast.success("Alert deleted.");
      onAlertDeleted(alertData.id);
      onClose();
    } catch {
      toast.error("Unable to delete alert.");
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-navy-950/70 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-white border border-gray-200 rounded-3xl max-w-md w-full p-6 sm:p-7 relative shadow-2xl space-y-5">
        <button
          type="button"
          onClick={onClose}
          disabled={loading || deleting}
          className="absolute top-5 right-5 w-8 h-8 rounded-full bg-gray-100 hover:bg-gray-200 text-gray-500 hover:text-navy-900 flex items-center justify-center transition-all cursor-pointer"
        >
          <X className="w-4 h-4" />
        </button>

        <div className="flex items-center gap-3.5 pr-8">
          <div className="w-12 h-12 rounded-2xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600 flex-shrink-0">
            <Bell className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-xl font-black text-navy-900 tracking-tight">Edit Price Alert</h3>
            <p className="text-xs text-gray-500 mt-0.5">Update your target price or notification settings</p>
          </div>
        </div>

        {product && (
          <div className="flex gap-3.5 p-3.5 rounded-2xl bg-gray-50 border border-gray-100">
            <div className="w-16 h-16 rounded-xl bg-white border border-gray-200 p-1 flex-shrink-0 overflow-hidden flex items-center justify-center">
              <img
                src={product.product_image || DEFAULT_PRODUCT_IMAGE}
                alt={product.product_name}
                className="w-full h-full object-contain"
                onError={(e) => { (e.target as HTMLImageElement).src = DEFAULT_PRODUCT_IMAGE; }}
              />
            </div>
            <div className="min-w-0 flex-1 flex flex-col justify-center">
              {platformInfo && (
                <span className={`badge ${getPlatformBadgeClass(product.platform)} text-[10px] py-0 px-2 mb-1 w-fit`}>
                  {platformInfo.name}
                </span>
              )}
              <p className="text-xs font-bold text-navy-900 line-clamp-1 leading-snug">{product.product_name}</p>
              <p className="text-xs text-gray-500 font-medium mt-1">
                Current: <strong className="text-navy-900 font-black text-sm">{formatINR(currentPrice)}</strong>
              </p>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="edit-target-price" className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-2">
              Alert me when price reaches:
            </label>
            <div className="relative rounded-2xl shadow-2xs">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-500 font-black text-base">?</div>
              <input
                id="edit-target-price"
                type="number"
                min="1"
                step="1"
                required
                value={targetPrice}
                onChange={(e) => { setTargetPrice(e.target.value); setErrorMsg(""); }}
                placeholder={currentPrice > 0 ? String(Math.round(currentPrice * 0.9)) : "1000"}
                className="w-full pl-9 pr-4 py-3 bg-white border border-gray-300 rounded-2xl text-base font-extrabold text-navy-900 focus:outline-none focus:ring-2 focus:ring-indigo-500/30 focus:border-indigo-600 transition-all placeholder:text-gray-300"
              />
            </div>
            {currentPrice > 0 && (
              <div className="flex items-center gap-1.5 mt-2 flex-wrap">
                <span className="text-[11px] text-gray-400 font-medium mr-1 flex items-center gap-0.5">
                  <Sparkles className="w-3 h-3 text-amber-500" /> Quick:
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
                        isSelected ? "bg-indigo-600 text-white border-indigo-600" : "bg-white hover:bg-gray-50 text-gray-600 border-gray-200"
                      }`}
                    >
                      {pct}% OFF ({formatINR(val)})
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          <div className="pt-2 border-t border-gray-100">
            <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-2.5">Notification preferences:</label>
            <div className="space-y-2">
              <label className="flex items-center gap-3 p-2.5 rounded-xl border border-gray-200 hover:border-indigo-200 hover:bg-indigo-50/30 transition-all cursor-pointer group">
                <input type="checkbox" checked={notifyPush} onChange={(e) => setNotifyPush(e.target.checked)} className="w-4 h-4 rounded text-indigo-600 cursor-pointer" />
                <Bell className="w-4 h-4 text-indigo-600" />
                <span className="text-xs font-bold text-gray-800 flex-1">Push Notification</span>
                <span className="text-[10px] text-indigo-600 font-semibold bg-indigo-50 px-2 py-0.5 rounded-full border border-indigo-100">Instant</span>
              </label>
              <label className="flex items-center gap-3 p-2.5 rounded-xl border border-gray-200 hover:border-indigo-200 hover:bg-indigo-50/30 transition-all cursor-pointer group">
                <input type="checkbox" checked={notifyEmail} onChange={(e) => setNotifyEmail(e.target.checked)} className="w-4 h-4 rounded text-indigo-600 cursor-pointer" />
                <Mail className="w-4 h-4 text-purple-600" />
                <span className="text-xs font-bold text-gray-800 flex-1">Email</span>
              </label>
              <label className="flex items-center gap-3 p-2.5 rounded-xl border border-gray-200 hover:border-indigo-200 hover:bg-indigo-50/30 transition-all cursor-pointer group">
                <input type="checkbox" checked={notifySms} onChange={(e) => setNotifySms(e.target.checked)} className="w-4 h-4 rounded text-indigo-600 cursor-pointer" />
                <MessageSquare className="w-4 h-4 text-emerald-600" />
                <span className="text-xs font-bold text-gray-800 flex-1">WhatsApp / SMS</span>
                <span className="text-[10px] text-emerald-600 font-semibold bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-100">High Priority</span>
              </label>
            </div>
          </div>

          {errorMsg && (
            <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-700 font-semibold">{errorMsg}</div>
          )}

          <div className="flex items-center justify-between gap-3 pt-3 border-t border-gray-100">
            <button
              type="button"
              onClick={handleDelete}
              disabled={loading || deleting}
              className="text-xs font-bold text-rose-600 hover:text-rose-700 flex items-center gap-1.5 py-2 px-2 hover:bg-rose-50 rounded-xl transition-all cursor-pointer disabled:opacity-50"
            >
              {deleting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Trash2 className="w-3.5 h-3.5" />}
              Delete Alert
            </button>
            <div className="flex items-center gap-2.5">
              <button type="button" onClick={onClose} disabled={loading || deleting} className="btn-secondary py-2.5 px-4 text-xs font-bold cursor-pointer">
                Cancel
              </button>
              <button type="submit" disabled={loading || deleting} className="btn-primary py-2.5 px-5 text-xs font-bold inline-flex items-center gap-2 cursor-pointer shadow-md hover:shadow-lg">
                {loading ? <><Loader2 className="w-4 h-4 animate-spin" /><span>Saving...</span></> : <><Check className="w-4 h-4" /><span>Save Changes</span></>}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
