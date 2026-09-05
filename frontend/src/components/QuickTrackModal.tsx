import { useState, useEffect } from 'react';
import { productsApi } from '../services/api';
import type { TrackedProduct, Product } from '../types';
import { X, Sparkles, Store } from 'lucide-react';
import PricePingProductView from './product/PricePingProductView';
import toast from 'react-hot-toast';

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

  const handleSearchNewInModal = async (newUrl: string) => {
    if (!newUrl.trim()) return;
    setLoading(true);
    try {
      let cleanQuery = newUrl.trim();
      if (!cleanQuery.startsWith('http://') && !cleanQuery.startsWith('https://')) {
        if (cleanQuery.includes('amazon.') || cleanQuery.includes('amzn.') || cleanQuery.includes('flipkart.') || cleanQuery.includes('myntra.') || cleanQuery.includes('ajio.') || cleanQuery.includes('nykaa.')) {
          cleanQuery = 'https://' + cleanQuery;
        }
      }
      const res = await productsApi.resolveUrl(cleanQuery);
      setProductData(res.data);
      if (onSuccessTrack) onSuccessTrack();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Could not resolve product. Please check the URL.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (initialProduct) {
      setProductData(initialProduct);
    } else if (searchedUrl) {
      handleSearchNewInModal(searchedUrl);
    }
  }, [initialProduct, searchedUrl]);

  // Handle ESC key to close modal
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      document.body.style.overflow = 'unset';
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const product: Product | undefined = productData?.product || productData;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/75 backdrop-blur-sm flex items-start justify-center p-2 sm:p-4 md:p-6 animate-in fade-in duration-200">
      {/* Click outside backdrop */}
      <div className="fixed inset-0" onClick={onClose} />

      {/* Main Modal Dialog Box */}
      <div className="relative w-full max-w-7xl bg-white rounded-3xl shadow-2xl border border-gray-200 my-4 sm:my-8 overflow-hidden z-10 animate-in zoom-in-95 duration-200">
        {/* Floating Close Button */}
        <button
          onClick={onClose}
          aria-label="Close modal"
          className="absolute top-4 right-4 sm:top-5 sm:right-6 z-40 bg-gray-900/80 hover:bg-gray-900 text-white rounded-full p-2.5 shadow-xl transition-all hover:scale-105 cursor-pointer flex items-center justify-center border border-white/20"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Content */}
        {loading ? (
          <div className="min-h-[500px] flex flex-col items-center justify-center p-8 text-center space-y-4 bg-[#f8fafc]">
            <div className="relative">
              <div className="w-16 h-16 rounded-full border-4 border-indigo-200 border-t-indigo-600 animate-spin" />
              <div className="absolute inset-0 flex items-center justify-center">
                <Store className="w-6 h-6 text-indigo-600 animate-pulse" />
              </div>
            </div>
            <div className="space-y-1">
              <h3 className="text-lg font-black text-gray-900">
                Scanning 5 Stores in Real-Time...
              </h3>
              <p className="text-xs text-gray-500 max-w-sm">
                Fetching verified prices from Amazon, Flipkart, Myntra, AJIO, and Nykaa to find you the lowest deal.
              </p>
            </div>
            <div className="flex items-center gap-2 text-xs font-bold text-gray-400">
              <span className="px-2.5 py-1 rounded-full bg-amber-50 text-amber-800 border border-amber-200">Amazon</span>
              <span className="px-2.5 py-1 rounded-full bg-blue-50 text-blue-800 border border-blue-200">Flipkart</span>
              <span className="px-2.5 py-1 rounded-full bg-rose-50 text-rose-800 border border-rose-200">Myntra</span>
              <span className="px-2.5 py-1 rounded-full bg-teal-50 text-teal-800 border border-teal-200">AJIO</span>
              <span className="px-2.5 py-1 rounded-full bg-pink-50 text-pink-800 border border-pink-200">Nykaa</span>
            </div>
          </div>
        ) : product ? (
          <div className="w-full">
            <PricePingProductView
              product={product}
              trackerId={productData?.id || productData?.tracker_id}
              crossStoreOffers={productData?.cross_store_offers || productData?.comparison || []}
              statistics={productData?.statistics}
              historyPoints={productData?.history_points || []}
              onSearchUrl={handleSearchNewInModal}
              isSearching={loading}
            />
          </div>
        ) : (
          <div className="min-h-[400px] flex flex-col items-center justify-center p-8 text-center space-y-3 bg-[#f8fafc]">
            <Sparkles className="w-10 h-10 text-indigo-600" />
            <h3 className="text-base font-bold text-gray-900">Product Not Found</h3>
            <p className="text-xs text-gray-500">Please paste a valid Amazon, Flipkart, Myntra, AJIO, or Nykaa product link.</p>
            <button
              onClick={onClose}
              className="mt-2 px-4 py-2 bg-indigo-600 text-white rounded-xl text-xs font-bold hover:bg-indigo-700"
            >
              Back to Home
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
