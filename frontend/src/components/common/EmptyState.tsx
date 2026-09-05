import { Link } from 'react-router-dom';
import type { LucideIcon } from 'lucide-react';
import { PlusCircle } from 'lucide-react';

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  actionText?: string;
  actionHref?: string;
  onAction?: () => void;
}

export default function EmptyState({
  icon: Icon,
  title,
  description,
  actionText,
  actionHref,
  onAction,
}: EmptyStateProps) {
  return (
    <div className="card p-12 sm:p-16 text-center">
      <div className="w-16 h-16 rounded-3xl bg-indigo-50 border border-indigo-100 flex items-center justify-center mx-auto mb-4 text-indigo-600 shadow-xs">
        <Icon className="w-8 h-8" />
      </div>
      <h3 className="text-xl font-black text-navy-900 mb-2 tracking-tight">{title}</h3>
      <p className="text-gray-500 mb-6 text-sm max-w-sm mx-auto leading-relaxed">
        {description}
      </p>

      {actionText && (
        <div>
          {actionHref ? (
            <Link to={actionHref} className="btn-primary inline-flex items-center gap-2">
              <PlusCircle className="w-4 h-4" />
              {actionText}
            </Link>
          ) : onAction ? (
            <button onClick={onAction} className="btn-primary inline-flex items-center gap-2">
              <PlusCircle className="w-4 h-4" />
              {actionText}
            </button>
          ) : null}
        </div>
      )}
    </div>
  );
}
