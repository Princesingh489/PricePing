import { useEffect, useState, useMemo } from 'react';
import { alertsApi } from '../services/api';
import type { PriceAlert } from '../types';
import toast from 'react-hot-toast';
import {
  Bell, PlusCircle, Zap, CheckCircle2, PauseCircle, Activity
} from 'lucide-react';
import AlertCard from '../components/alerts/AlertCard';
import EmptyState from '../components/common/EmptyState';
import EditAlertModal from '../components/modals/EditAlertModal';
import { Link } from 'react-router-dom';

type FilterTab = 'all' | 'active' | 'triggered' | 'disabled';

const TABS: { id: FilterTab; label: string; emoji: string }[] = [
  { id: 'all', label: 'All Alerts', emoji: '🔔' },
  { id: 'active', label: 'Active', emoji: '✅' },
  { id: 'triggered', label: 'Triggered', emoji: '⚡' },
  { id: 'disabled', label: 'Paused', emoji: '⏸' },
];

export default function Alerts() {
  const [alerts, setAlerts] = useState<PriceAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<FilterTab>('all');
  const [editingAlert, setEditingAlert] = useState<PriceAlert | null>(null);

  const fetchAlerts = () => {
    setLoading(true);
    alertsApi.list()
      .then((res) => setAlerts(res.data || []))
      .catch(() => toast.error('Failed to load alerts'))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchAlerts();
  }, []);

  // Dynamic stat counts
  const stats = useMemo(() => {
    const active = alerts.filter((a) => a.alert_status === 'active').length;
    const triggered = alerts.filter((a) => a.alert_status === 'triggered').length;
    const disabled = alerts.filter((a) => a.alert_status === 'disabled' || a.alert_status === 'snoozed').length;
    // "Near target" = active + has target + current price within 15% of target
    const nearTarget = alerts.filter((a) => {
      if (a.alert_status !== 'active') return false;
      const cur = a.product?.current_price || 0;
      const tgt = a.target_price || a.minimum_price || 0;
      if (!cur || !tgt) return false;
      return cur <= tgt * 1.15 && cur > tgt;
    }).length;
    return { active, triggered, disabled, nearTarget };
  }, [alerts]);

  const filteredAlerts = useMemo(() => {
    if (activeTab === 'all') return alerts;
    if (activeTab === 'disabled') return alerts.filter((a) => a.alert_status === 'disabled' || a.alert_status === 'snoozed');
    return alerts.filter((a) => a.alert_status === activeTab);
  }, [alerts, activeTab]);

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this price alert?')) return;
    try {
      await alertsApi.delete(id);
      setAlerts((prev) => prev.filter((a) => a.id !== id));
      toast.success('Alert deleted');
    } catch {
      toast.error('Failed to delete alert');
    }
  };

  const handleToggle = async (alert: PriceAlert) => {
    const newStatus = alert.alert_status === 'active' ? 'disabled' : 'active';
    try {
      const res = await alertsApi.update(alert.id, { alert_status: newStatus });
      setAlerts((prev) => prev.map((a) => (a.id === alert.id ? res.data : a)));
      toast.success(newStatus === 'active' ? 'Alert enabled' : 'Alert paused');
    } catch {
      toast.error('Failed to update alert');
    }
  };

  const handleAlertUpdated = (updated: PriceAlert) => {
    setAlerts((prev) => prev.map((a) => (a.id === updated.id ? updated : a)));
  };

  const handleAlertDeletedFromModal = (id: number) => {
    setAlerts((prev) => prev.filter((a) => a.id !== id));
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10 space-y-6">
      {/* ===== Page Header ===== */}
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-black text-navy-900 tracking-tight">Price Alerts</h1>
          <p className="text-gray-500 text-sm mt-1">
            {stats.active} active alert{stats.active !== 1 ? 's' : ''} monitoring target drop thresholds
          </p>
        </div>
        <Link to="/add-product" className="btn-primary flex items-center gap-2 w-fit flex-shrink-0">
          <PlusCircle className="w-4 h-4" />
          <span>+ Create Price Alert</span>
        </Link>
      </div>

      {/* ===== Summary Stats Row ===== */}
      {!loading && alerts.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-emerald-100 flex items-center justify-center text-emerald-600 flex-shrink-0">
              <Activity className="w-4 h-4" />
            </div>
            <div>
              <p className="text-xl font-black text-emerald-700">{stats.active}</p>
              <p className="text-[11px] font-semibold text-emerald-600">Active</p>
            </div>
          </div>

          <div className="rounded-2xl border border-indigo-200 bg-indigo-50 px-4 py-3 flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-indigo-100 flex items-center justify-center text-indigo-600 flex-shrink-0">
              <Bell className="w-4 h-4" />
            </div>
            <div>
              <p className="text-xl font-black text-indigo-700">{stats.nearTarget}</p>
              <p className="text-[11px] font-semibold text-indigo-600">Near Target</p>
            </div>
          </div>

          <div className="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-amber-100 flex items-center justify-center text-amber-600 flex-shrink-0">
              <Zap className="w-4 h-4" />
            </div>
            <div>
              <p className="text-xl font-black text-amber-700">{stats.triggered}</p>
              <p className="text-[11px] font-semibold text-amber-600">Triggered</p>
            </div>
          </div>

          <div className="rounded-2xl border border-gray-200 bg-gray-50 px-4 py-3 flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-gray-100 flex items-center justify-center text-gray-500 flex-shrink-0">
              <PauseCircle className="w-4 h-4" />
            </div>
            <div>
              <p className="text-xl font-black text-gray-600">{stats.disabled}</p>
              <p className="text-[11px] font-semibold text-gray-500">Paused</p>
            </div>
          </div>
        </div>
      )}

      {/* ===== Filter Tabs ===== */}
      {!loading && alerts.length > 0 && (
        <div className="flex items-center gap-1.5 bg-gray-100/80 p-1 rounded-2xl w-fit">
          {TABS.map((tab) => {
            const count =
              tab.id === 'all' ? alerts.length :
              tab.id === 'active' ? stats.active :
              tab.id === 'triggered' ? stats.triggered :
              stats.disabled;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                  activeTab === tab.id
                    ? 'bg-white text-indigo-700 shadow-sm border border-indigo-100'
                    : 'text-gray-500 hover:text-gray-800'
                }`}
              >
                <span>{tab.emoji}</span>
                <span>{tab.label}</span>
                <span className={`text-[10px] font-black px-1.5 py-0.5 rounded-full ${
                  activeTab === tab.id ? 'bg-indigo-100 text-indigo-600' : 'bg-gray-200 text-gray-500'
                }`}>{count}</span>
              </button>
            );
          })}
        </div>
      )}

      {/* ===== Content ===== */}
      {loading ? (
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="rounded-2xl border border-gray-100 bg-gray-50 h-36 animate-pulse" />
          ))}
        </div>
      ) : alerts.length === 0 ? (
        <EmptyState
          icon={Bell}
          title="No price alerts yet"
          description="Track any product from Amazon, Flipkart, AJIO, Myntra or Nykaa and set target prices to receive instant notifications."
          actionText="Create Price Alert"
          actionHref="/add-product"
        />
      ) : filteredAlerts.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-gray-200 p-10 text-center">
          <CheckCircle2 className="w-10 h-10 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500 font-semibold text-sm">No alerts in this category</p>
          <button onClick={() => setActiveTab('all')} className="text-indigo-600 text-xs font-bold mt-2 hover:underline cursor-pointer">
            View all alerts
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredAlerts.map((alert) => (
            <AlertCard
              key={alert.id}
              alert={alert}
              onToggle={handleToggle}
              onDelete={handleDelete}
              onEdit={(a) => setEditingAlert(a)}
            />
          ))}
        </div>
      )}

      {/* ===== Edit Alert Modal ===== */}
      <EditAlertModal
        isOpen={!!editingAlert}
        onClose={() => setEditingAlert(null)}
        alert={editingAlert}
        onAlertUpdated={handleAlertUpdated}
        onAlertDeleted={handleAlertDeletedFromModal}
      />
    </div>
  );
}
