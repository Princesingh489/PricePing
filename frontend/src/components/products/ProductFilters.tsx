import { Search } from 'lucide-react';
import { PLATFORM_LABELS } from '../../utils/helpers';

interface ProductFiltersProps {
  search: string;
  onSearchChange: (val: string) => void;
  selectedPlatform: string;
  onPlatformChange: (val: string) => void;
  statusFilter?: string;
  onStatusChange?: (val: string) => void;
}

const PLATFORMS = ['all', 'amazon', 'flipkart', 'ajio', 'myntra', 'nykaa'];

export default function ProductFilters({
  search,
  onSearchChange,
  selectedPlatform,
  onPlatformChange,
  statusFilter,
  onStatusChange,
}: ProductFiltersProps) {
  return (
    <div className="flex flex-col lg:flex-row gap-4 items-stretch lg:items-center justify-between">
      {/* Search Input */}
      <div className="relative w-full lg:max-w-md">
        <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4.5 h-4.5 text-gray-400" />
        <input
          className="input pl-10"
          placeholder="Search tracked products by title..."
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
        />
      </div>

      {/* Platform Filter Pills */}
      <div className="flex gap-2 flex-wrap items-center">
        {PLATFORMS.map((pf) => {
          const isSelected = selectedPlatform === pf;
          const label = pf === 'all' ? 'All Stores' : PLATFORM_LABELS[pf as keyof typeof PLATFORM_LABELS]?.name || pf;
          return (
            <button
              key={pf}
              onClick={() => onPlatformChange(pf)}
              className={`btn-pill ${
                isSelected
                  ? 'bg-indigo-600 text-white shadow-xs'
                  : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
              }`}
            >
              {label}
            </button>
          );
        })}

        {statusFilter !== undefined && onStatusChange && (
          <select
            value={statusFilter}
            onChange={(e) => onStatusChange(e.target.value)}
            className="input !w-auto !py-1.5 !px-3 text-xs font-semibold bg-white border border-gray-200 rounded-full"
          >
            <option value="all">All Status</option>
            <option value="active">Active Only</option>
            <option value="paused">Paused Only</option>
          </select>
        )}
      </div>
    </div>
  );
}
