import { X } from 'lucide-react';
import type { Product } from '../../types';
import PriceHistoryChart from '../charts/PriceHistoryChart';

interface PriceHistoryModalProps {
  product: Product | null;
  onClose: () => void;
}

export default function PriceHistoryModal({ product, onClose }: PriceHistoryModalProps) {
  if (!product) return null;

  return (
    <div className="fixed inset-0 z-50 bg-navy-950/70 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto animate-fade-in">
      <div className="bg-white border border-gray-200 rounded-3xl max-w-4xl w-full p-6 sm:p-8 relative shadow-2xl max-h-[90vh] overflow-y-auto">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 w-9 h-9 rounded-full bg-gray-100 hover:bg-gray-200 text-gray-500 hover:text-navy-900 flex items-center justify-center transition-all z-10 cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>

        <PriceHistoryChart product={product} isStandalone={true} />
      </div>
    </div>
  );
}
