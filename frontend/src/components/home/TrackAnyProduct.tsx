import { Link } from 'react-router-dom';
import { CheckCircle2, ArrowRight, Bell, Sparkles } from 'lucide-react';
import { formatINR, DEFAULT_PRODUCT_IMAGE } from '../../utils/helpers';

export default function TrackAnyProduct() {
  return (
    <section className="py-16 sm:py-20 bg-white border-y border-gray-200/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          {/* Left Column: Product Tracking Card Preview */}
          <div className="lg:col-span-6 relative">
            <div className="absolute -inset-4 bg-gradient-to-r from-indigo-500/10 to-purple-500/10 rounded-3xl blur-xl -z-10" />
            
            <div className="card p-6 sm:p-8 border-gray-200 shadow-xl space-y-6">
              <div className="flex items-center justify-between">
                <span className="badge badge-amazon">Amazon India</span>
                <span className="badge badge-success">● Active Monitor</span>
              </div>

              <div className="flex gap-4 items-center">
                <div className="w-20 h-20 rounded-2xl bg-indigo-50/60 border border-indigo-100 flex items-center justify-center p-2 flex-shrink-0">
                  <img
                    src="https://m.media-amazon.com/images/I/71d7rfSl0wL._SX679_.jpg"
                    alt="iPhone 15"
                    className="w-full h-full object-contain mix-blend-multiply"
                    onError={(e) => {
                      (e.target as HTMLImageElement).src = DEFAULT_PRODUCT_IMAGE;
                    }}
                  />
                </div>
                <div className="min-w-0">
                  <h4 className="font-bold text-navy-900 text-base leading-snug line-clamp-1">
                    Apple iPhone 15 (128 GB) - Blue
                  </h4>
                  <div className="flex items-baseline gap-2 mt-1">
                    <span className="text-2xl font-black text-navy-900">{formatINR(69999)}</span>
                    <span className="text-xs text-gray-400 line-through">{formatINR(79900)}</span>
                    <span className="text-[11px] font-black text-emerald-700 bg-emerald-100 px-1.5 py-0.5 rounded">
                      12% OFF
                    </span>
                  </div>
                </div>
              </div>

              {/* Target Tracker Slider Box */}
              <div className="p-4 rounded-2xl bg-indigo-50/60 border border-indigo-100 space-y-3">
                <div className="flex items-center justify-between text-xs font-bold">
                  <span className="text-indigo-900 flex items-center gap-1.5">
                    <Bell className="w-3.5 h-3.5 text-indigo-600" />
                    Target Drop Price:
                  </span>
                  <span className="text-indigo-700 font-extrabold text-sm">{formatINR(64999)}</span>
                </div>

                <div className="w-full h-2 rounded-full bg-indigo-200/80 relative">
                  <div className="w-4/5 h-full rounded-full bg-gradient-brand" />
                  <div className="absolute right-[20%] -top-1 w-4 h-4 rounded-full bg-white border-2 border-indigo-600 shadow-md" />
                </div>

                <div className="flex items-center justify-between text-[11px] text-gray-500 font-medium">
                  <span>Current: ₹69,999</span>
                  <span className="text-emerald-700 font-bold">Save ₹5,000 when hit</span>
                </div>
              </div>

              {/* Status capsule */}
              <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-900 font-semibold flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-emerald-600" />
                <span>Price checked every 15 minutes • Auto-alert enabled</span>
              </div>
            </div>
          </div>

          {/* Right Column: Heading & Features List */}
          <div className="lg:col-span-6 space-y-6">
            <div>
              <span className="text-xs font-black uppercase tracking-wider text-indigo-600 bg-indigo-50 px-3 py-1 rounded-full border border-indigo-100">
                Track Any Product
              </span>
              <h2 className="text-3xl sm:text-4xl font-black text-navy-900 tracking-tight mt-3 leading-tight">
                Know when the price is right
              </h2>
              <p className="text-gray-500 text-sm sm:text-base mt-3 leading-relaxed">
                Never second-guess online sales. Paste any link to lock in your desired buying price, and we'll keep an automated watch so you buy at the all-time lowest.
              </p>
            </div>

            {/* Checklist */}
            <div className="space-y-3.5 pt-2">
              {[
                'Track current price across 5+ major stores',
                'Set custom below-price target thresholds',
                'Set price range filters to catch flash deals',
                'Track percentage drops (e.g., alert on 20% drop)',
                'Automatically monitor price fluctuations 24/7',
              ].map((text) => (
                <div key={text} className="flex items-center gap-3">
                  <div className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center flex-shrink-0">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                  </div>
                  <span className="text-sm font-bold text-navy-800">{text}</span>
                </div>
              ))}
            </div>

            {/* CTA */}
            <div className="pt-4">
              <Link
                to="/add-product"
                className="btn-primary text-sm py-3.5 px-8 inline-flex items-center gap-2 shadow-lg"
              >
                <span>Start Tracking</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
