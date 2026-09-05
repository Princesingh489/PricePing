export function ProductCardSkeleton() {
  return (
    <div className="card p-5 space-y-4">
      <div className="flex items-center justify-between">
        <div className="w-20 h-5 rounded-full skeleton" />
        <div className="w-16 h-5 rounded-full skeleton" />
      </div>
      <div className="flex gap-4">
        <div className="w-20 h-20 rounded-2xl skeleton flex-shrink-0" />
        <div className="flex-1 space-y-2">
          <div className="w-full h-4 rounded skeleton" />
          <div className="w-3/4 h-4 rounded skeleton" />
          <div className="w-1/2 h-6 rounded-lg skeleton mt-2" />
        </div>
      </div>
      <div className="flex gap-2 pt-2">
        <div className="flex-1 h-9 rounded-xl skeleton" />
        <div className="w-9 h-9 rounded-xl skeleton" />
        <div className="w-9 h-9 rounded-xl skeleton" />
      </div>
    </div>
  );
}

export function StatCardSkeleton() {
  return (
    <div className="card p-5 flex items-center gap-4">
      <div className="w-12 h-12 rounded-2xl skeleton flex-shrink-0" />
      <div className="space-y-2 flex-1">
        <div className="w-16 h-6 rounded skeleton" />
        <div className="w-24 h-3 rounded skeleton" />
      </div>
    </div>
  );
}

export function TableRowSkeleton() {
  return (
    <tr className="border-b border-gray-100">
      <td className="px-6 py-4"><div className="w-48 h-5 rounded skeleton" /></td>
      <td className="px-4 py-4"><div className="w-20 h-5 rounded-full skeleton" /></td>
      <td className="px-4 py-4"><div className="w-24 h-5 rounded skeleton" /></td>
      <td className="px-4 py-4"><div className="w-16 h-5 rounded-full skeleton" /></td>
      <td className="px-4 py-4 text-right"><div className="w-20 h-8 rounded-xl skeleton inline-block" /></td>
    </tr>
  );
}
