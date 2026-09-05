interface SpeedometerGaugeProps {
  currentPrice: number | null;
  lowestPrice: number | null;
  averagePrice: number | null;
  highestPrice: number | null;
  recommendation?: string;
  recommendationReason?: string;
}

export default function SpeedometerGauge({
  currentPrice,
  lowestPrice,
  averagePrice,
  highestPrice,
  recommendation,
  recommendationReason,
}: SpeedometerGaugeProps) {
  const cur = currentPrice || 0;
  const low = lowestPrice || cur;
  const high = highestPrice || cur;
  const avg = averagePrice || cur;

  // Calculate needle angle (180deg = Low/Green, 90deg = Average/Yellow, 0deg = Peak/Red)
  let angle = 90; // Default center
  const span = Math.max(high - low, 1);

  if (cur <= low) {
    angle = 165; // Far left (Green)
  } else if (cur >= high) {
    angle = 15; // Far right (Red)
  } else if (avg && span > 0) {
    // Two-segment interpolation around average
    if (cur <= avg) {
      const subSpan = Math.max(avg - low, 1);
      const ratio = (cur - low) / subSpan;
      angle = 165 - ratio * 75; // 165 -> 90
    } else {
      const subSpan = Math.max(high - avg, 1);
      const ratio = (cur - avg) / subSpan;
      angle = 90 - ratio * 75; // 90 -> 15
    }
  }

  // Derive human-friendly status and recommendation badge
  let statusBadge = {
    title: 'Good time to buy!',
    sub: 'Currently at a good price',
    cls: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    dotCls: 'bg-emerald-500',
  };

  if (cur <= low * 1.02) {
    statusBadge = {
      title: 'Go Ahead & Buy now',
      sub: 'Currently at its lowest observed price',
      cls: 'bg-emerald-50 text-emerald-700 border-emerald-200',
      dotCls: 'bg-emerald-500',
    };
  } else if (cur >= high * 0.98) {
    statusBadge = {
      title: 'Consider Waiting',
      sub: 'Price is at or near its recorded peak',
      cls: 'bg-rose-50 text-rose-700 border-rose-200',
      dotCls: 'bg-rose-500',
    };
  } else if (cur <= (avg || cur)) {
    statusBadge = {
      title: 'Fair Price',
      sub: 'Trading below historical average',
      cls: 'bg-emerald-50 text-emerald-700 border-emerald-200',
      dotCls: 'bg-emerald-500',
    };
  } else {
    statusBadge = {
      title: 'Watch & Wait',
      sub: 'Trading above average price',
      cls: 'bg-amber-50 text-amber-700 border-amber-200',
      dotCls: 'bg-amber-500',
    };
  }

  if (recommendation === 'BUY_NOW') {
    statusBadge = {
      title: 'Go Ahead & Buy now',
      sub: recommendationReason || 'Currently at a good price',
      cls: 'bg-emerald-50 text-emerald-700 border-emerald-200',
      dotCls: 'bg-emerald-500',
    };
  } else if (recommendation === 'WAIT') {
    statusBadge = {
      title: 'Wait for Price Drop',
      sub: recommendationReason || 'Price is currently on the higher side',
      cls: 'bg-rose-50 text-rose-700 border-rose-200',
      dotCls: 'bg-rose-500',
    };
  } else if (recommendation === 'FAIR_PRICE') {
    statusBadge = {
      title: 'Fair Price',
      sub: recommendationReason || 'Close to average market price',
      cls: 'bg-amber-50 text-amber-700 border-amber-200',
      dotCls: 'bg-amber-500',
    };
  }

  return (
    <div className="flex flex-col items-center text-center space-y-3">
      <div className="text-xs font-black uppercase tracking-wider text-gray-500">
        Should you buy now?
      </div>

      {/* Semicircular Speedometer Arc */}
      <div className="relative w-48 h-28 flex items-center justify-center">
        <svg viewBox="0 0 200 120" className="w-full h-full overflow-visible">
          <defs>
            <linearGradient id="gaugeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#10b981" />
              <stop offset="50%" stopColor="#f59e0b" />
              <stop offset="100%" stopColor="#f43f5e" />
            </linearGradient>
          </defs>

          {/* Semicircle track background */}
          <path
            d="M 20 100 A 80 80 0 0 1 180 100"
            fill="none"
            stroke="#f1f5f9"
            strokeWidth="16"
            strokeLinecap="round"
          />

          {/* Colored gradient arc */}
          <path
            d="M 20 100 A 80 80 0 0 1 180 100"
            fill="none"
            stroke="url(#gaugeGrad)"
            strokeWidth="14"
            strokeLinecap="round"
          />

          {/* Needle Pointer */}
          <g
            transform={`translate(100, 100) rotate(${180 - angle})`}
            className="transition-transform duration-700 ease-out"
          >
            <line
              x1="0"
              y1="0"
              x2="-60"
              y2="0"
              stroke="#0f172a"
              strokeWidth="3.5"
              strokeLinecap="round"
            />
            <circle cx="0" cy="0" r="7" fill="#0f172a" />
            <circle cx="0" cy="0" r="3" fill="#ffffff" />
          </g>
        </svg>

        {/* Labels underneath the gauge */}
        <div className="absolute -bottom-1 left-2 text-[10px] font-black text-emerald-600 uppercase">
          Low
        </div>
        <div className="absolute -bottom-1 text-[10px] font-bold text-amber-600 uppercase">
          Average
        </div>
        <div className="absolute -bottom-1 right-2 text-[10px] font-black text-rose-600 uppercase">
          Peak
        </div>
      </div>

      {/* Recommendation Banner */}
      <div className={`w-full p-2.5 rounded-2xl border flex items-center justify-center gap-2 text-xs ${statusBadge.cls}`}>
        <span className={`w-2 h-2 rounded-full ${statusBadge.dotCls} animate-pulse`} />
        <div>
          <span className="font-black">{statusBadge.title}</span>
          <span className="text-[11px] opacity-80 block">{statusBadge.sub}</span>
        </div>
      </div>
    </div>
  );
}
