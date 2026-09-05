import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Bell, Target, TrendingDown, Percent } from 'lucide-react';

export default function PriceAlertPreview() {
  const [selectedType, setSelectedType] = useState<'below_price' | 'price_range' | 'percentage_drop'>('below_price');

  return (
    <section className="py-16 sm:py-20 bg-white border-y border-gray-200/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-14">
          <span className="text-xs font-black uppercase tracking-wider text-indigo-600 bg-indigo-50 px-3 py-1 rounded-full border border-indigo-100">
            Smart Alerts
          </span>
          <h2 className="text-3xl sm:text-4xl font-black text-navy-900 tracking-tight mt-3">
            Never miss the right price
          </h2>
          <p className="text-gray-500 text-sm sm:text-base mt-2">
            Configure flexible price drop rules. We'll monitor the product round-the-clock and notify you instantly.
          </p>
        </div>

        <div className="max-w-4xl mx-auto card p-6 sm:p-10 border-gray-200 shadow-lg">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            {/* Rule 1: Below Target Price */}
            <button
              type="button"
              onClick={() => setSelectedType('below_price')}
              className={`p-5 rounded-2xl border text-left transition-all cursor-pointer ${
                selectedType === 'below_price'
                  ? 'border-indigo-600 bg-indigo-50/70 shadow-sm ring-2 ring-indigo-500/20'
                  : 'border-gray-200 bg-white hover:border-gray-300'
              }`}
            >
              <div className="w-10 h-10 rounded-xl bg-indigo-100 text-indigo-700 flex items-center justify-center mb-3">
                <Target className="w-5 h-5" />
              </div>
              <h4 className="font-bold text-navy-900 text-sm">Below Target Price</h4>
              <p className="text-xs text-gray-500 mt-1">Alert immediately when the price drops below ₹X</p>
            </button>

            {/* Rule 2: Price Range */}
            <button
              type="button"
              onClick={() => setSelectedType('price_range')}
              className={`p-5 rounded-2xl border text-left transition-all cursor-pointer ${
                selectedType === 'price_range'
                  ? 'border-indigo-600 bg-indigo-50/70 shadow-sm ring-2 ring-indigo-500/20'
                  : 'border-gray-200 bg-white hover:border-gray-300'
              }`}
            >
              <div className="w-10 h-10 rounded-xl bg-purple-100 text-purple-700 flex items-center justify-center mb-3">
                <TrendingDown className="w-5 h-5" />
              </div>
              <h4 className="font-bold text-navy-900 text-sm">Price Range Window</h4>
              <p className="text-xs text-gray-500 mt-1">Alert when price lands between ₹Min and ₹Max</p>
            </button>

            {/* Rule 3: Percentage Drop */}
            <button
              type="button"
              onClick={() => setSelectedType('percentage_drop')}
              className={`p-5 rounded-2xl border text-left transition-all cursor-pointer ${
                selectedType === 'percentage_drop'
                  ? 'border-indigo-600 bg-indigo-50/70 shadow-sm ring-2 ring-indigo-500/20'
                  : 'border-gray-200 bg-white hover:border-gray-300'
              }`}
            >
              <div className="w-10 h-10 rounded-xl bg-pink-100 text-pink-700 flex items-center justify-center mb-3">
                <Percent className="w-5 h-5" />
              </div>
              <h4 className="font-bold text-navy-900 text-sm">Percentage Drop</h4>
              <p className="text-xs text-gray-500 mt-1">Alert on any 10%, 20%, or 30% discount drop</p>
            </button>
          </div>

          {/* Interactive Preview Display */}
          <div className="p-6 rounded-2xl bg-gray-50 border border-gray-200 flex flex-col sm:flex-row items-center justify-between gap-6">
            <div className="space-y-2 text-center sm:text-left">
              <div className="text-xs font-black uppercase tracking-wider text-indigo-700">Configured Notification Channels</div>
              <div className="flex flex-wrap items-center justify-center sm:justify-start gap-2 pt-1">
                <span className="px-3 py-1 rounded-full bg-white border border-gray-200 text-xs font-bold text-navy-800 shadow-2xs">
                  📧 Email Digest
                </span>
                <span className="px-3 py-1 rounded-full bg-white border border-gray-200 text-xs font-bold text-navy-800 shadow-2xs">
                  🔔 Browser Push
                </span>
                <span className="px-3 py-1 rounded-full bg-white border border-gray-200 text-xs font-bold text-navy-800 shadow-2xs">
                  📱 SMS / WhatsApp
                </span>
                <span className="px-3 py-1 rounded-full bg-white border border-gray-200 text-xs font-bold text-navy-800 shadow-2xs">
                  🔵 In-App Notification
                </span>
              </div>
            </div>

            <Link
              to="/add-product"
              className="btn-primary text-xs py-3 px-6 whitespace-nowrap flex-shrink-0"
            >
              <Bell className="w-4 h-4" />
              <span>Create Price Alert</span>
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
