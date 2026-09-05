import { Trash2, X, AlertTriangle } from 'lucide-react';
import type { TrackedProduct } from '../../types';

interface DeleteTrackingModalProps {
  tracker: TrackedProduct | null;
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (trackerId: number) => Promise<void>;
  isLoading?: boolean;
}

export default function DeleteTrackingModal({
  tracker,
  isOpen,
  onClose,
  onConfirm,
  isLoading = false,
}: DeleteTrackingModalProps) {
  if (!isOpen || !tracker) return null;

  const productName = tracker.product?.product_name || 'this product';

  return (
    <div className="fixed inset-0 z-50 bg-navy-950/70 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto animate-fade-in">
      <div className="bg-white border border-gray-200 rounded-3xl max-w-md w-full p-6 sm:p-7 relative shadow-2xl space-y-5">
        <button
          onClick={onClose}
          disabled={isLoading}
          className="absolute top-5 right-5 w-8 h-8 rounded-full bg-gray-100 hover:bg-gray-200 text-gray-500 hover:text-navy-900 flex items-center justify-center transition-all cursor-pointer"
        >
          <X className="w-4 h-4" />
        </button>

        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-2xl bg-rose-50 border border-rose-100 flex items-center justify-center text-rose-600 flex-shrink-0">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-lg font-black text-navy-900 tracking-tight">
              Remove Tracked Product
            </h3>
            <p className="text-xs text-gray-400">Stop monitoring price drops</p>
          </div>
        </div>

        <div className="text-sm text-gray-600 leading-relaxed bg-gray-50/70 p-4 rounded-2xl border border-gray-100">
          <p className="font-medium">
            Remove <span className="font-bold text-navy-900 line-clamp-2 mt-1">"{productName}"</span> from your tracked products?
          </p>
          <p className="text-xs text-gray-400 mt-2">
            You will no longer receive price drop notifications for this item. Historical price data for this item is safely preserved.
          </p>
        </div>

        <div className="flex items-center justify-end gap-3 pt-2">
          <button
            type="button"
            onClick={onClose}
            disabled={isLoading}
            className="btn-secondary py-2.5 px-4 text-xs font-bold cursor-pointer"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={() => onConfirm(tracker.id)}
            disabled={isLoading}
            className="btn-danger py-2.5 px-5 text-xs font-bold inline-flex items-center gap-2 cursor-pointer shadow-sm hover:shadow-md"
          >
            {isLoading ? (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <Trash2 className="w-4 h-4" />
            )}
            <span>Remove Tracking</span>
          </button>
        </div>
      </div>
    </div>
  );
}
