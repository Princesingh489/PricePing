import { useState } from 'react';
import { formatINR } from '../utils/helpers';
import {
  Sparkles, PiggyBank, Smartphone, Shirt, ShoppingCart, Plane
} from 'lucide-react';
import toast from 'react-hot-toast';

export default function SpendLensSection() {
  const [monthlySpend, setMonthlySpend] = useState<number>(25000);

  // Computed savings models
  const annualSpend = monthlySpend * 12;
  const estimatedSavingsPercentage = 18; // Average 18% savings with PricePing price drop alerts
  const annualSavings = Math.round((annualSpend * estimatedSavingsPercentage) / 100);
  const monthlySavings = Math.round(annualSavings / 12);

  const categoryDistribution = [
    { name: 'Electronics & Mobiles', share: 40, icon: Smartphone, color: 'from-blue-500 to-indigo-600', savings: Math.round(annualSavings * 0.4) },
    { name: 'Fashion & Apparel', share: 30, icon: Shirt, color: 'from-pink-500 to-rose-600', savings: Math.round(annualSavings * 0.3) },
    { name: 'Quick Grocery & Food', share: 20, icon: ShoppingCart, color: 'from-emerald-500 to-teal-600', savings: Math.round(annualSavings * 0.2) },
    { name: 'Travel & Flights', share: 10, icon: Plane, color: 'from-amber-500 to-orange-600', savings: Math.round(annualSavings * 0.1) },
  ];

  return (
    <section id="spend-lens" className="my-10 p-6 sm:p-10 rounded-3xl bg-gradient-to-br from-[#1a102f] via-[#130d24] to-[#0d0a18] border border-purple-500/25 shadow-2xl relative overflow-hidden">
      {/* Background ambient glow */}
      <div className="absolute -top-24 -right-24 w-96 h-96 bg-purple-600/20 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-pink-600/15 rounded-full blur-3xl pointer-events-none" />

      {/* Header */}
      <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30 text-xs font-black uppercase tracking-wider mb-2">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            Price Ping Spend Lens™ Feature
          </div>
          <h2 className="text-2xl sm:text-4xl font-black text-white tracking-tight">
            Where Did Your Money Go?
          </h2>
          <p className="text-sm sm:text-base text-gray-300 mt-1 max-w-xl">
            See exactly how much you can pocket back on your everyday online purchases with PricePing automatic price drop tracking.
          </p>
        </div>

        <div className="p-4 rounded-2xl bg-white/[0.05] border border-white/10 flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-emerald-500 to-teal-500 flex items-center justify-center text-white shadow-lg shadow-emerald-500/30 flex-shrink-0">
            <PiggyBank className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs text-gray-400 font-bold uppercase tracking-wider">Estimated Annual Savings</div>
            <div className="text-2xl sm:text-3xl font-black text-emerald-400 tracking-tight">{formatINR(annualSavings)}/yr</div>
          </div>
        </div>
      </div>

      {/* Interactive Spend Calculator */}
      <div className="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
        {/* Left Slider & Input */}
        <div className="lg:col-span-6 p-6 rounded-2xl bg-white/[0.03] border border-white/10 space-y-6">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-gray-300 uppercase tracking-wider">Your Monthly Online Spend</span>
              <span className="text-2xl font-black text-white">{formatINR(monthlySpend)}</span>
            </div>
            <input
              type="range"
              min="5000"
              max="150000"
              step="2500"
              value={monthlySpend}
              onChange={(e) => setMonthlySpend(Number(e.target.value))}
              className="w-full h-2.5 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-purple-500"
            />
            <div className="flex justify-between text-[11px] text-gray-500 font-semibold mt-1.5">
              <span>₹5,000</span>
              <span>₹50,000</span>
              <span>₹1,00,000</span>
              <span>₹1,50,000+</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="p-4 rounded-xl bg-purple-500/10 border border-purple-500/20">
              <div className="text-[11px] font-bold text-purple-300 uppercase">Monthly Savings</div>
              <div className="text-xl font-black text-white mt-1">{formatINR(monthlySavings)}</div>
              <div className="text-[10px] text-purple-200 mt-0.5">Average 18% price drop savings</div>
            </div>

            <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
              <div className="text-[11px] font-bold text-emerald-300 uppercase">5-Year Wealth Compounded</div>
              <div className="text-xl font-black text-white mt-1">{formatINR(annualSavings * 5 * 1.12)}</div>
              <div className="text-[10px] text-emerald-200 mt-0.5">If invested @ 12% CAGR</div>
            </div>
          </div>

          <button
            onClick={() => toast.success('Spend Lens tracking enabled! Add products to start saving.')}
            className="btn-primary w-full py-3 text-sm shadow-lg shadow-purple-500/30"
          >
            <Sparkles className="w-4 h-4" />
            Enable Automatic Spend Lens Tracker
          </button>
        </div>

        {/* Right Category Breakdown */}
        <div className="lg:col-span-6 space-y-3.5">
          <div className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Category-Wise Potential Savings</div>
          {categoryDistribution.map((cat) => {
            const Icon = cat.icon;
            return (
              <div key={cat.name} className="p-3.5 rounded-2xl bg-white/[0.03] border border-white/10 flex items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-xl bg-gradient-to-tr ${cat.color} text-white flex items-center justify-center shadow-md`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="font-bold text-sm text-white">{cat.name}</div>
                    <div className="text-xs text-gray-400">{cat.share}% of monthly basket</div>
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-base font-black text-emerald-400">+{formatINR(cat.savings)}/yr</div>
                  <div className="text-[10px] text-gray-500">Instant Alert Drops</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
