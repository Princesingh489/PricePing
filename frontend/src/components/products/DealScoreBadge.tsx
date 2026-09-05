import React from 'react';
import type { DealRecommendation } from '../../types';
import { TrendingDown, Clock, Eye, BarChart2 } from 'lucide-react';

interface DealScoreBadgeProps {
  recommendation: DealRecommendation;
  confidence: number;
  percentile?: number | null;
  message?: string;
  compact?: boolean;
}

const CONFIG: Record<DealRecommendation, {
  label: string;
  subLabel: string;
  icon: React.ComponentType<{ className?: string }>;
  bg: string;
  text: string;
  border: string;
  glow: string;
  dot: string;
}> = {
  BUY_NOW: {
    label: 'Buy Now',
    subLabel: 'Near All-Time Low',
    icon: TrendingDown,
    bg: 'bg-emerald-50',
    text: 'text-emerald-800',
    border: 'border-emerald-200',
    glow: 'shadow-emerald-100',
    dot: 'bg-emerald-500',
  },
  WATCH: {
    label: 'Watch',
    subLabel: 'Below Average Price',
    icon: Eye,
    bg: 'bg-blue-50',
    text: 'text-blue-800',
    border: 'border-blue-200',
    glow: 'shadow-blue-100',
    dot: 'bg-blue-500',
  },
  WAIT: {
    label: 'Wait',
    subLabel: 'Higher Than Usual',
    icon: Clock,
    bg: 'bg-amber-50',
    text: 'text-amber-800',
    border: 'border-amber-200',
    glow: 'shadow-amber-100',
    dot: 'bg-amber-500',
  },
  FAIR_PRICE: {
    label: 'Fair Price',
    subLabel: 'Near Average',
    icon: BarChart2,
    bg: 'bg-cyan-50',
    text: 'text-cyan-800',
    border: 'border-cyan-200',
    glow: 'shadow-cyan-100',
    dot: 'bg-cyan-500',
  },
  INSUFFICIENT_DATA: {
    label: 'Building History',
    subLabel: 'Need More Data',
    icon: BarChart2,
    bg: 'bg-gray-50',
    text: 'text-gray-600',
    border: 'border-gray-200',
    glow: 'shadow-gray-100',
    dot: 'bg-gray-400',
  },
};

export default function DealScoreBadge({
  recommendation,
  confidence,
  percentile,
  message,
  compact = false,
}: DealScoreBadgeProps) {
  const cfg = CONFIG[recommendation];
  const Icon = cfg.icon;

  if (compact) {
    return (
      <span
        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold border ${cfg.bg} ${cfg.text} ${cfg.border}`}
      >
        <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot} animate-pulse`} />
        {cfg.label}
      </span>
    );
  }

  return (
    <div className={`rounded-2xl border p-4 ${cfg.bg} ${cfg.border} shadow-sm ${cfg.glow}`}>
      {/* Header Row */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${cfg.bg} border ${cfg.border}`}>
            <Icon className={`w-4.5 h-4.5 ${cfg.text}`} />
          </div>
          <div>
            <p className={`text-sm font-black tracking-tight ${cfg.text}`}>{cfg.label}</p>
            <p className={`text-xs font-semibold opacity-70 ${cfg.text}`}>{cfg.subLabel}</p>
          </div>
        </div>

        {/* Confidence meter */}
        {recommendation !== 'INSUFFICIENT_DATA' && (
          <div className="text-right flex-shrink-0">
            <p className={`text-xl font-black leading-none ${cfg.text}`}>{confidence}%</p>
            <p className={`text-xs font-semibold opacity-60 ${cfg.text}`}>confidence</p>
          </div>
        )}
      </div>

      {/* Percentile bar */}
      {recommendation !== 'INSUFFICIENT_DATA' && percentile !== null && percentile !== undefined && (
        <div className="mt-3">
          <div className="flex justify-between text-[10px] font-bold mb-1 opacity-60">
            <span className={cfg.text}>Lowest</span>
            <span className={cfg.text}>Highest</span>
          </div>
          <div className="w-full h-1.5 rounded-full bg-white/60 relative overflow-hidden">
            <div
              className="absolute left-0 top-0 h-full rounded-full transition-all duration-700"
              style={{
                width: `${percentile}%`,
                background:
                  recommendation === 'BUY_NOW'
                    ? 'linear-gradient(90deg, #10b981, #34d399)'
                    : recommendation === 'WATCH'
                    ? 'linear-gradient(90deg, #3b82f6, #60a5fa)'
                    : 'linear-gradient(90deg, #f59e0b, #fbbf24)',
              }}
            />
            {/* Current price marker */}
            <div
              className={`absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full border-2 border-white shadow ${cfg.dot}`}
              style={{ left: `calc(${percentile}% - 6px)` }}
            />
          </div>
          <p className={`text-[10px] font-semibold mt-1 opacity-60 ${cfg.text}`}>
            Current price is in the {percentile.toFixed(0)}th percentile of tracked prices
          </p>
        </div>
      )}

      {/* Message */}
      {message && (
        <p className={`text-xs leading-relaxed mt-3 pt-3 border-t font-medium opacity-80 ${cfg.text} border-current/10`}>
          {message}
        </p>
      )}
    </div>
  );
}
