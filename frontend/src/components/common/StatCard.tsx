import type { LucideIcon } from 'lucide-react';

interface StatCardProps {
  icon: LucideIcon;
  label: string;
  value: number | string;
  gradient?: string;
  sublabel?: string;
  trend?: string;
  trendPositive?: boolean;
}

export default function StatCard({
  icon: Icon,
  label,
  value,
  gradient = 'bg-gradient-brand',
  sublabel,
  trend,
  trendPositive,
}: StatCardProps) {
  return (
    <div className="card p-5 flex items-center gap-4 group hover:border-indigo-300 hover:shadow-card-hover transition-all duration-300">
      <div className={`w-12 h-12 rounded-2xl ${gradient} flex items-center justify-center flex-shrink-0 shadow-md shadow-indigo-500/15 group-hover:scale-105 transition-transform duration-300 text-white`}>
        <Icon className="w-6 h-6" />
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-baseline gap-2">
          <div className="text-2xl font-black text-navy-900 tracking-tight">{value}</div>
          {trend && (
            <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
              trendPositive ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'
            }`}>
              {trend}
            </span>
          )}
        </div>
        <div className="text-xs font-bold text-gray-500 truncate">{label}</div>
        {sublabel && <div className="text-[10px] text-gray-400 mt-0.5 font-medium">{sublabel}</div>}
      </div>
    </div>
  );
}
