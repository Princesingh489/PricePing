import { Link2, Target, BellRing, ArrowRight } from 'lucide-react';

const STEPS = [
  {
    step: '01',
    title: 'Paste Product Link',
    description: 'Copy and paste any product URL from Amazon, Flipkart, AJIO, Myntra, or Nykaa into PricePing.',
    icon: Link2,
    gradient: 'from-indigo-600 to-indigo-800',
    color: 'text-indigo-600',
    bg: 'bg-indigo-50',
  },
  {
    step: '02',
    title: 'Set Your Target Price',
    description: 'Specify your dream price or preferred percentage drop discount you want to buy at.',
    icon: Target,
    gradient: 'from-purple-600 to-purple-800',
    color: 'text-purple-600',
    bg: 'bg-purple-50',
  },
  {
    step: '03',
    title: 'Get Alert When Price Drops',
    description: 'We track the price 24/7 and ping you instantly via Email, Push or SMS the moment the price hits your target.',
    icon: BellRing,
    gradient: 'from-pink-600 to-rose-800',
    color: 'text-rose-600',
    bg: 'bg-rose-50',
  },
];

export default function HowItWorks() {
  return (
    <section className="py-16 sm:py-20 bg-[#f8fafc]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-14">
          <span className="text-xs font-black uppercase tracking-wider text-indigo-600 bg-indigo-50 px-3 py-1 rounded-full border border-indigo-100">
            How It Works
          </span>
          <h2 className="text-3xl sm:text-4xl font-black text-navy-900 tracking-tight mt-3">
            Start saving in 3 simple steps
          </h2>
          <p className="text-gray-500 text-sm sm:text-base mt-2">
            No browser extensions required. PricePing works seamlessly across desktop and mobile.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
          {STEPS.map((item) => {
            const Icon = item.icon;
            return (
              <div
                key={item.step}
                className="card p-8 hover:border-indigo-300 hover:shadow-card-hover transition-all duration-300 relative group flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <span className="text-3xl font-black text-indigo-200 group-hover:text-indigo-400 transition-colors">
                      {item.step}
                    </span>
                    <div className={`w-12 h-12 rounded-2xl ${item.bg} ${item.color} flex items-center justify-center shadow-xs group-hover:scale-110 transition-transform duration-300`}>
                      <Icon className="w-6 h-6" />
                    </div>
                  </div>

                  <h3 className="text-xl font-black text-navy-900 mb-2.5 tracking-tight group-hover:text-indigo-600 transition-colors">
                    {item.title}
                  </h3>
                  <p className="text-gray-500 text-sm leading-relaxed">
                    {item.description}
                  </p>
                </div>

                <div className="pt-6 mt-6 border-t border-gray-100 flex items-center text-xs font-bold text-indigo-600 group-hover:translate-x-1 transition-transform">
                  <span>Step {item.step}</span>
                  <ArrowRight className="w-3.5 h-3.5 ml-1" />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
