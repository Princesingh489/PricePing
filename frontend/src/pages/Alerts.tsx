import { useEffect, useState } from 'react';
import { alertsApi } from '../services/api';
import type { PriceAlert } from '../types';
import toast from 'react-hot-toast';
import { Bell, PlusCircle } from 'lucide-react';
import AlertCard from '../components/alerts/AlertCard';
import EmptyState from '../components/common/EmptyState';
import { Link } from 'react-router-dom';

export default function Alerts() {
  const [alerts, setAlerts] = useState<PriceAlert[]>([]);
  const [loading, setLoading] = useState(true);

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

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-black text-navy-900 tracking-tight">Price Alerts</h1>
          <p className="text-gray-500 text-sm mt-1">
            {alerts.length} active alert{alerts.length !== 1 ? 's' : ''} monitoring target drop thresholds
          </p>
        </div>

        <Link to="/add-product" className="btn-primary flex items-center gap-2 w-fit">
          <PlusCircle className="w-4 h-4" />
          <span>Create Price Alert</span>
        </Link>
      </div>

      {/* Alerts List */}
      {loading ? (
        <div className="space-y-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="card p-6 h-32 skeleton" />
          ))}
        </div>
      ) : alerts.length === 0 ? (
        <EmptyState
          icon={Bell}
          title="No active price alerts yet"
          description="Track any product from Amazon, Flipkart, AJIO, Myntra or Nykaa and set target prices to receive notifications."
          actionText="Create Price Alert"
          actionHref="/add-product"
        />
      ) : (
        <div className="space-y-4">
          {alerts.map((alert) => (
            <AlertCard
              key={alert.id}
              alert={alert}
              onToggle={handleToggle}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}
    </div>
  );
}
