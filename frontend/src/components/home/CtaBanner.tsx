import { Link } from 'react-router-dom';
import { ArrowRight, Sparkles, ShieldCheck } from 'lucide-react';

export default function CtaBanner() {
  return (
    <section className="py-16 sm:py-20 bg-gradient-hero text-white relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-purple-500/20 via-transparent to-transparent pointer-events-none" />

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10 space-y-6">
        <div className="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full bg-white/15 backdrop-blur-md border border-white/20 text-indigo-100 text-xs font-bold">
          <Sparkles className="w-3.5 h-3.5 text-amber-300 fill-amber-300" />
          <span>Save Money Every Time You Shop</span>
        </div>

        <h2 className="text-3xl sm:text-4xl lg:text-5xl font-black text-white tracking-tight leading-tight max-w-3xl mx-auto">
          Start tracking prices and never overpay online again.
        </h2>

        <p className="text-indigo-100 text-sm sm:text-base max-w-xl mx-auto font-normal">
          Join shoppers across India tracking products on Amazon, Flipkart, AJIO, Myntra & Nykaa for free.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
          <Link
            to="/add-product"
            className="btn-primary w-full sm:w-auto text-sm py-3.5 px-8 shadow-xl"
          >
            <span>Track Your First Product</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            to="/register"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-white/10 hover:bg-white/20 text-white font-bold px-6 py-3.5 rounded-xl border border-white/20 text-sm transition-all"
          >
            <span>Create Free Account</span>
          </Link>
        </div>

        <div className="pt-4 flex items-center justify-center gap-6 text-xs text-indigo-200">
          <span className="flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-300" />
            100% Free Service
          </span>
          <span className="flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-300" />
            Zero Spam Guarantee
          </span>
        </div>
      </div>
    </section>
  );
}
