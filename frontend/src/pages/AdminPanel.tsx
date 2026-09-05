import { useEffect, useState } from 'react';
import { adminApi } from '../services/api';
import { Users, Package, Bell, CheckCircle, TrendingDown, Activity, ShieldCheck } from 'lucide-react';
import StatCard from '../components/common/StatCard';
import { StatCardSkeleton } from '../components/common/SkeletonLoader';

interface AdminStats {
  total_users: number;
  total_products: number;
  total_tracked: number;
  total_active_alerts: number;
  total_notifications_sent: number;
  price_drops_today: number;
  alerts_triggered_today: number;
}

interface AdminUser {
  id: number;
  name: string;
  email: string;
  is_admin: boolean;
  is_active: boolean;
  created_at: string;
}

export default function AdminPanel() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([adminApi.stats(), adminApi.users()])
      .then(([statsRes, usersRes]) => {
        setStats(statsRes.data);
        setUsers(usersRes.data || []);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10 space-y-8">
      <div className="flex items-center gap-3.5">
        <div className="w-12 h-12 bg-amber-500 rounded-2xl flex items-center justify-center text-white shadow-md shadow-amber-500/20">
          <ShieldCheck className="w-7 h-7" />
        </div>
        <div>
          <h1 className="text-3xl font-black text-navy-900 tracking-tight">System Admin Console</h1>
          <p className="text-gray-500 text-sm">Platform metrics, user accounts, and system scraper health</p>
        </div>
      </div>

      {/* Metrics Grid */}
      {loading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          {[...Array(6)].map((_, i) => (
            <StatCardSkeleton key={i} />
          ))}
        </div>
      ) : stats ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          <StatCard icon={Users} label="Total Users" value={stats.total_users} gradient="bg-gradient-brand" />
          <StatCard icon={Package} label="Catalog Items" value={stats.total_products} gradient="bg-gradient-cool" />
          <StatCard icon={Activity} label="Active Trackers" value={stats.total_tracked} gradient="bg-gradient-success" />
          <StatCard icon={Bell} label="Active Alerts" value={stats.total_active_alerts} gradient="bg-gradient-warm" />
          <StatCard icon={CheckCircle} label="Notifications" value={stats.total_notifications_sent} gradient="bg-gradient-sunset" />
          <StatCard icon={TrendingDown} label="Drops Today" value={stats.alerts_triggered_today} gradient="bg-gradient-danger" />
        </div>
      ) : null}

      {/* Users Table */}
      <div className="card overflow-hidden border-gray-200 shadow-sm">
        <div className="p-6 border-b border-gray-100 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-black text-navy-900">Registered Accounts</h2>
            <p className="text-xs text-gray-500 mt-0.5">{users.length} registered accounts across PricePing</p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-gray-100 bg-gray-50/70 text-xs font-bold text-gray-500 uppercase tracking-wider">
                <th className="px-6 py-3.5">User</th>
                <th className="px-4 py-3.5">Email</th>
                <th className="px-4 py-3.5">Role</th>
                <th className="px-4 py-3.5">Status</th>
                <th className="px-4 py-3.5">Joined</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-sm">
              {users.map((u) => (
                <tr key={u.id} className="hover:bg-gray-50/60 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-xl bg-gradient-brand flex items-center justify-center text-white font-bold text-xs shadow-2xs">
                        {u.name?.charAt(0).toUpperCase() || 'U'}
                      </div>
                      <span className="font-bold text-navy-900">{u.name}</span>
                    </div>
                  </td>
                  <td className="px-4 py-4 text-gray-600 font-medium">{u.email}</td>
                  <td className="px-4 py-4">
                    <span className={`badge ${u.is_admin ? 'badge-warning' : 'badge-info'} text-[10px]`}>
                      {u.is_admin ? '🛡️ Admin' : '👤 User'}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <span className={`badge ${u.is_active ? 'badge-success' : 'badge-danger'} text-[10px]`}>
                      {u.is_active ? '● Active' : '● Inactive'}
                    </span>
                  </td>
                  <td className="px-4 py-4 text-xs text-gray-500 font-medium">
                    {new Date(u.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
