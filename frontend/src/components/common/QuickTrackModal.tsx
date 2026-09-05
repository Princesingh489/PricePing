import { useState, useEffect } from 'react';
import { productsApi, alertsApi } from '../../services/api';
import toast from 'react-hot-toast';
import { formatINR, PLATFORM_LABELS, getPlatformBadgeClass } from '../../utils/helpers';
import type { TrackedProduct, Product } from '../../types';
import {
  X, Sparkles, Bell, CheckCircle2, Star, Loader2
} from 'lucide-react';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  initialProduct?: TrackedProduct | Product | null;
  searchedUrl?: string;
  onSuccessTrack?: () => void;
}

export default function QuickTrackModal({
  isOpen,
  onClose,
  initialProduct,
  searchedUrl,
  onSuccessTrack,
}: Props) {
  const [productData, setProductData] = useState<any>(initialProduct || null);
  const [loading, setLoading] = useState(false);
  const [alertType, setAlertType] = useState<'below_price' | 'percentage_drop' | 'none'>('below_price');
  const [targetPrice, setTargetPrice] = useState('');
  const [percentageDrop, setPercentageDrop] = useState('10');
  const [settingAlert, setSettingAlert] = useState(false);

  useEffect(() => {
    if (initialProduct) {
      setProductData(initialProduct);
    } else if (searchedUrl) {
      setLoading(true);
      productsApi.add({ product_url: searchedUrl })
        .then((res) => {
          setProductData(res.data?.product || res.data);
        })
        .catch((err) => {
          toast.error(err.response?.data?.detail || 'Failed to fetch product details');
        })
        .finally(() => setLoading(false));
    }
  }, [initialProduct, searchedUrl]);

  if (!isOpen) return null;

  const product: Product | undefined = productData?.product || productData;
  const platformInfo = product?.platform ? PLATFORM_LABELS[product.platform] : undefined;

  const handleCreateAlert = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!product) return;

    setSettingAlert(true);
    try {
      if (alertType !== 'none') {
        const payload: any = {
          product_id: product.id,
          alert_type: alertType,
          notify_email: true,
          notify_push: true,
          notify_in_app: true,
        };
        if (alertType === 'below_price') {
          payload.target_price = parseFloat(targetPrice) || (product.current_price ? Math.round(product.current_price * 0.9) : 0);
        } else if (alertType === 'percentage_drop') {
          payload.percentage_drop = parseFloat(percentageDrop) || 10;
        }
        await alertsApi.create(payload);
        toast.success('Price alert configured successfully! 🎯');
      } else {
        toast.success('Product added to your tracked products! 📦');
      }
      if (onSuccessTrack) onSuccessTrack();
      onClose();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to create alert');
    } finally {
      setSettingAlert(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-navy-950/70 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto animate-fade-in">
      <div className="bg-white border border-gray-200 rounded-3xl max-w-2xl w-full p-6 sm:p-8 relative shadow-2xl max-h-[90vh] overflow-y-auto">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 w-9 h-9 rounded-full bg-gray-100 hover:bg-gray-200 text-gray-500 hover:text-navy-900 flex items-center justify-center transition-all z-10 cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header */}
        <div className="flex items-center gap-3 mb-6">
          <div className="w-11 h-11 rounded-2xl bg-gradient-brand flex items-center justify-center text-white shadow-md shadow-indigo-500/25">
            <Sparkles className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-black text-navy-900 flex items-center gap-2">
              Track This Product
              <span className="text-[10px] font-extrabold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700 border border-emerald-200">
                Verified Store
              </span>
            </h2>
            <p className="text-xs text-gray-500">Live price comparison, tracker setup & drop notifications</p>
          </div>
        </div>

        {loading ? (
          <div className="py-16 text-center">
            <Loader2 className="w-10 h-10 text-indigo-600 animate-spin mx-auto mb-3" />
            <p className="text-sm font-bold text-navy-800">Fetching live product details & prices...</p>
            <p className="text-xs text-gray-400 mt-1">Connecting to store scrapers</p>
          </div>
        ) : product ? (
          <div className="space-y-6">
            {/* Product Card Overview */}
            <div className="p-4 sm:p-5 rounded-2xl bg-gray-50/80 border border-gray-200 flex flex-col sm:flex-row gap-4 sm:gap-5 items-start sm:items-center">
              <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-2xl bg-white border border-gray-200 flex items-center justify-center p-2 flex-shrink-0 shadow-2xs overflow-hidden">
                <img
                  src={product.product_image || 'https://placehold.co/120x120/f8fafc/6366f1?text=Product'}
                  alt={product.product_name}
                  className="w-full h-full object-contain"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = 'https://placehold.co/120x120/f8fafc/6366f1?text=Product';
                  }}
                />
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap mb-1">
                  {platformInfo && (
                    <span className={getPlatformBadgeClass(product.platform) + ' badge text-[11px]'}>
                      {platformInfo.name}
                    </span>
                  )}
                  {product.rating && product.rating > 0 && (
                    <span className="badge bg-amber-50 text-amber-700 border border-amber-200 text-[11px]">
                      <Star className="w-3 h-3 fill-amber-400 text-amber-400" />
                      {product.rating.toFixed(1)} ★
                    </span>
                  )}
                  <span className="badge badge-success text-[11px]">
                    <CheckCircle2 className="w-3 h-3" /> In Stock
                  </span>
                </div>

                <h3 className="text-sm sm:text-base font-bold text-navy-900 line-clamp-2 mb-1.5 leading-snug">
                  {product.product_name}
                </h3>

                <div className="flex items-baseline gap-2.5 flex-wrap">
                  <span className="text-2xl font-black text-navy-900 tracking-tight">
                    {formatINR(product.current_price)}
                  </span>
                  {product.original_price && product.original_price > (product.current_price || 0) && (
                    <>
                      <span className="text-xs sm:text-sm text-gray-400 line-through font-medium">
                        {formatINR(product.original_price)}
                      </span>
                      {product.discount_percentage && (
                        <span className="px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 border border-emerald-200 text-[10px] font-black">
                          {product.discount_percentage.toFixed(0)}% OFF
                        </span>
                      )}
                    </>
                  )}
                </div>
              </div>
            </div>

            {/* Set Price Alert Form */}
            <form onSubmit={handleCreateAlert} className="p-5 rounded-2xl bg-indigo-50/50 border border-indigo-200/80 space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-indigo-900 uppercase tracking-wider flex items-center gap-1.5">
                  <Bell className="w-4 h-4 text-indigo-600" />
                  Set Price Drop Alert
                </span>
                <span className="text-xs text-gray-500 font-medium">Instant notification triggers</span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                <button
                  type="button"
                  onClick={() => setAlertType('below_price')}
                  className={`p-3 rounded-xl border text-left transition-all cursor-pointer ${
                    alertType === 'below_price'
                      ? 'border-indigo-600 bg-white shadow-sm ring-2 ring-indigo-500/20'
                      : 'border-gray-200 bg-white/60 text-gray-700 hover:bg-white'
                  }`}
                >
                  <div className="text-xs font-black text-navy-900">Below Target Price</div>
                  <div className="text-[10px] text-gray-500 mt-0.5">Alert if drops under ₹X</div>
                </button>

                <button
                  type="button"
                  onClick={() => setAlertType('percentage_drop')}
                  className={`p-3 rounded-xl border text-left transition-all cursor-pointer ${
                    alertType === 'percentage_drop'
                      ? 'border-indigo-600 bg-white shadow-sm ring-2 ring-indigo-500/20'
                      : 'border-gray-200 bg-white/60 text-gray-700 hover:bg-white'
                  }`}
                >
                  <div className="text-xs font-black text-navy-900">% Drop Alert</div>
                  <div className="text-[10px] text-gray-500 mt-0.5">e.g. 10%, 20% off</div>
                </button>

                <button
                  type="button"
                  onClick={() => setAlertType('none')}
                  className={`p-3 rounded-xl border text-left transition-all cursor-pointer ${
                    alertType === 'none'
                      ? 'border-indigo-600 bg-white shadow-sm ring-2 ring-indigo-500/20'
                      : 'border-gray-200 bg-white/60 text-gray-700 hover:bg-white'
                  }`}
                >
                  <div className="text-xs font-black text-navy-900">Silent Track</div>
                  <div className="text-[10px] text-gray-500 mt-0.5">Log history only</div>
                </button>
              </div>

              {alertType === 'below_price' && (
                <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2">
                  <div className="relative w-full sm:w-48">
                    <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-500 font-bold text-sm">₹</span>
                    <input
                      type="number"
                      placeholder={product.current_price ? `${Math.round(product.current_price * 0.9)}` : 'Target price'}
                      value={targetPrice}
                      onChange={(e) => setTargetPrice(e.target.value)}
                      className="input pl-8 font-bold"
                    />
                  </div>
                  <span className="text-xs text-gray-600">Notify me immediately when price reaches or drops below this</span>
                </div>
              )}

              {alertType === 'percentage_drop' && (
                <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2">
                  <div className="relative w-full sm:w-36">
                    <input
                      type="number"
                      placeholder="10"
                      min="1"
                      max="90"
                      value={percentageDrop}
                      onChange={(e) => setPercentageDrop(e.target.value)}
                      className="input pr-8 font-bold"
                    />
                    <span className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-500 font-bold text-sm">%</span>
                  </div>
                  <span className="text-xs text-gray-600">Notify me when the price drops by this percentage</span>
                </div>
              )}

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={onClose}
                  className="btn-secondary text-xs py-2.5 px-4"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={settingAlert}
                  className="btn-primary text-xs py-2.5 px-6"
                >
                  {settingAlert ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" /> Saving...
                    </>
                  ) : (
                    <>
                      <Bell className="w-4 h-4" /> Start Tracking
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        ) : null}
      </div>
    </div>
  );
}
