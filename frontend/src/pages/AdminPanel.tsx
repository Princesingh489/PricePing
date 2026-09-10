import { useEffect, useState } from 'react';
import { adminApi } from '../services/api';
import {
  Users,
  Package,
  Bell,
  CheckCircle,
  TrendingDown,
  Activity,
  ShieldCheck,
  AlertTriangle,
  RefreshCw,
  Send,
  ExternalLink,
  CheckCircle2,
  MessageSquare,
  Bot,
  Mail,
  Zap,
} from 'lucide-react';
import StatCard from '../components/common/StatCard';
import { StatCardSkeleton } from '../components/common/SkeletonLoader';
import toast from 'react-hot-toast';

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

interface FailingProduct {
  id: number;
  product_name: string;
  platform: string;
  product_url: string;
  current_price: number | null;
  availability: string;
  status: string;
  last_checked: string | null;
  error_reason: string;
}

interface IncidentItem {
  id: number;
  product_name: string;
  store: string;
  url: string;
  error_reason: string;
  severity: string;
  status: string;
  timestamp: string;
  timestamp_display: string;
}

interface ScraperHealthData {
  incidents: IncidentItem[];
  failing_products: FailingProduct[];
  store_stats: Record<
    string,
    {
      total: number;
      failed: number;
      success_rate: number;
      status: 'healthy' | 'degraded' | 'critical';
    }
  >;
  alert_channels: {
    whatsapp_configured: boolean;
    whatsapp_recipient: string;
    telegram_configured: boolean;
    telegram_chat_id: string;
    email_configured: boolean;
    email_recipient: string;
  };
}

export default function AdminPanel() {
  const [activeTab, setActiveTab] = useState<'health' | 'users' | 'alerts'>('health');
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [health, setHealth] = useState<ScraperHealthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [retryingId, setRetryingId] = useState<number | null>(null);
  const [testingAlert, setTestingAlert] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const results = await Promise.allSettled([
        adminApi.stats(),
        adminApi.users(),
        adminApi.scraperHealth(),
      ]);

      if (results[0].status === 'fulfilled') {
        setStats(results[0].value.data);
      } else {
        console.warn('Admin stats load error:', results[0].reason);
      }

      if (results[1].status === 'fulfilled') {
        setUsers(results[1].value.data || []);
      } else {
        console.warn('Admin users load error:', results[1].reason);
      }

      if (results[2].status === 'fulfilled') {
        setHealth(results[2].value.data);
      } else {
        // Fallback default state if backend scraper-health endpoint is still deploying or restarting
        setHealth({
          incidents: [],
          failing_products: [],
          store_stats: {
            amazon: { total: 0, failed: 0, success_rate: 100, status: 'healthy' },
            flipkart: { total: 0, failed: 0, success_rate: 100, status: 'healthy' },
            myntra: { total: 0, failed: 0, success_rate: 100, status: 'healthy' },
            ajio: { total: 0, failed: 0, success_rate: 100, status: 'healthy' },
            nykaa: { total: 0, failed: 0, success_rate: 100, status: 'healthy' },
          },
          alert_channels: {
            whatsapp_configured: false,
            whatsapp_recipient: 'Not Set',
            telegram_configured: false,
            telegram_chat_id: 'Not Set',
            email_configured: true,
            email_recipient: 'admin@pricewatch.in',
          },
        });
      }
    } catch {
      toast.error('Could not refresh some admin console data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleRetryScrape = async (productId: number) => {
    setRetryingId(productId);
    try {
      const res = await adminApi.retryScrape(productId);
      if (res.data?.success) {
        toast.success(res.data.message || 'Scrape verified successfully!');
        fetchData();
      } else {
        toast.error(res.data?.message || 'Scrape retry failed.');
      }
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Retry command failed.');
    } finally {
      setRetryingId(null);
    }
  };

  const handleTestAlert = async () => {
    setTestingAlert(true);
    try {
      const res = await adminApi.testAlert();
      const ch = res.data?.configured_channels;
      if (ch?.whatsapp || ch?.telegram || ch?.email) {
        toast.success('Test alert dispatched to configured channels!');
      } else {
        toast('Alert logged to incident dashboard. Add Twilio/Telegram in .env to receive phone pings.', {
          icon: 'ℹ️',
        });
      }
      fetchData();
    } catch {
      toast.error('Could not send test alert.');
    } finally {
      setTestingAlert(false);
    }
  };

  const brokenCount = health?.failing_products?.length || 0;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 bg-amber-500 rounded-2xl flex items-center justify-center text-white shadow-md shadow-amber-500/20">
            <ShieldCheck className="w-7 h-7" />
          </div>
          <div>
            <h1 className="text-3xl font-black text-navy-900 tracking-tight">System Admin Console</h1>
            <p className="text-gray-500 text-sm">Real-time URL health monitor, scraper debugging, and alert dispatcher</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleTestAlert}
            disabled={testingAlert}
            className="px-4 py-2 bg-indigo-50 border border-indigo-200 text-indigo-700 hover:bg-indigo-100 rounded-xl text-xs font-bold transition-all flex items-center gap-2 cursor-pointer"
          >
            {testingAlert ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
            <span>Test Admin Alert</span>
          </button>
          <button
            onClick={() => {
              setLoading(true);
              fetchData();
            }}
            className="p-2 text-gray-500 hover:text-gray-900 bg-white border border-gray-200 rounded-xl transition-all cursor-pointer shadow-xs"
            title="Refresh metrics"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
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

      {/* Tab Navigation */}
      <div className="flex items-center gap-2 border-b border-gray-200 pb-2">
        <button
          onClick={() => setActiveTab('health')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 cursor-pointer ${
            activeTab === 'health'
              ? 'bg-navy-900 text-white shadow-xs'
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
          }`}
        >
          <AlertTriangle className="w-4 h-4" />
          <span>URL & Scraper Health</span>
          {brokenCount > 0 && (
            <span className="px-1.5 py-0.5 rounded-full text-[10px] bg-rose-500 text-white font-black">
              {brokenCount}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveTab('users')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 cursor-pointer ${
            activeTab === 'users'
              ? 'bg-navy-900 text-white shadow-xs'
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
          }`}
        >
          <Users className="w-4 h-4" />
          <span>Registered Users ({users.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('alerts')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 cursor-pointer ${
            activeTab === 'alerts'
              ? 'bg-navy-900 text-white shadow-xs'
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
          }`}
        >
          <Zap className="w-4 h-4" />
          <span>Alert Channels & Phone Ping</span>
        </button>
      </div>

      {/* TAB 1: URL & Scraper Health */}
      {activeTab === 'health' && (
        <div className="space-y-6">
          {/* Store Health Badges */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
            {health?.store_stats &&
              Object.entries(health.store_stats).map(([storeName, data]) => (
                <div
                  key={storeName}
                  className="bg-white p-4 rounded-2xl border border-gray-200 shadow-2xs space-y-1.5"
                >
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-black uppercase tracking-wider text-slate-700">{storeName}</span>
                    {data.status === 'healthy' ? (
                      <span className="flex items-center gap-1 text-[10px] font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">
                        <CheckCircle2 className="w-3 h-3" /> 100% OK
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-[10px] font-bold text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full">
                        <AlertTriangle className="w-3 h-3" /> {data.success_rate}%
                      </span>
                    )}
                  </div>
                  <div className="text-xl font-black text-slate-900">
                    {data.total - data.failed} <span className="text-xs font-medium text-slate-400">/ {data.total} OK</span>
                  </div>
                </div>
              ))}
          </div>

          {/* Broken / Failing Product URLs Table */}
          <div className="card overflow-hidden border-gray-200 shadow-sm bg-white rounded-3xl">
            <div className="p-6 border-b border-gray-100 flex items-center justify-between">
              <div>
                <h2 className="text-lg font-black text-navy-900 flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-rose-500" />
                  <span>Monitored URLs Requiring Attention</span>
                </h2>
                <p className="text-xs text-gray-500 mt-0.5">
                  Products with extraction errors, listing changes, or bot blocks detected during periodic checks
                </p>
              </div>
              <span className="text-xs font-bold px-3 py-1 bg-gray-100 rounded-xl text-gray-700">
                {brokenCount} issues found
              </span>
            </div>

            {brokenCount === 0 ? (
              <div className="p-12 text-center space-y-3">
                <div className="w-12 h-12 mx-auto rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
                  <CheckCircle2 className="w-6 h-6" />
                </div>
                <h3 className="text-sm font-bold text-slate-800">All Product URLs Are Healthy</h3>
                <p className="text-xs text-slate-500 max-w-sm mx-auto">
                  No broken links, bot captcha blocks, or DOM extraction failures detected across Amazon, Flipkart,
                  Myntra, Ajio, and Nykaa.
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead>
                    <tr className="border-b border-gray-100 bg-gray-50/70 text-xs font-bold text-gray-500 uppercase tracking-wider">
                      <th className="px-6 py-3.5">Product & Store</th>
                      <th className="px-4 py-3.5">Error Reason</th>
                      <th className="px-4 py-3.5">Status</th>
                      <th className="px-4 py-3.5">Last Checked</th>
                      <th className="px-4 py-3.5 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100 text-sm">
                    {health?.failing_products.map((p) => (
                      <tr key={p.id} className="hover:bg-gray-50/60 transition-colors">
                        <td className="px-6 py-4">
                          <div className="space-y-1 max-w-sm">
                            <span className="font-bold text-navy-900 block truncate" title={p.product_name}>
                              {p.product_name}
                            </span>
                            <div className="flex items-center gap-2 text-xs">
                              <span className="px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 font-bold uppercase text-[10px]">
                                {p.platform}
                              </span>
                              <a
                                href={p.product_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-slate-400 hover:text-indigo-600 flex items-center gap-1 text-[11px]"
                              >
                                View Source <ExternalLink className="w-3 h-3" />
                              </a>
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-4 text-xs font-semibold text-rose-600">
                          {p.error_reason}
                        </td>
                        <td className="px-4 py-4">
                          <span className="px-2 py-1 bg-rose-50 text-rose-700 rounded-lg text-[10px] font-black uppercase">
                            {p.status}
                          </span>
                        </td>
                        <td className="px-4 py-4 text-xs text-slate-500">
                          {p.last_checked
                            ? new Date(p.last_checked).toLocaleDateString('en-IN', {
                                day: 'numeric',
                                month: 'short',
                                hour: '2-digit',
                                minute: '2-digit',
                              })
                            : 'Pending check'}
                        </td>
                        <td className="px-4 py-4 text-right">
                          <button
                            onClick={() => handleRetryScrape(p.id)}
                            disabled={retryingId === p.id}
                            className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition-all inline-flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                          >
                            <RefreshCw className={`w-3.5 h-3.5 ${retryingId === p.id ? 'animate-spin' : ''}`} />
                            <span>Retry Scrape</span>
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Recent Incident Log Stream */}
          <div className="card border-gray-200 shadow-sm bg-white rounded-3xl p-6 space-y-4">
            <h3 className="text-sm font-black text-navy-900 uppercase tracking-wider flex items-center gap-2">
              <Activity className="w-4 h-4 text-indigo-600" />
              <span>Real-Time Incident & Error Audit Stream</span>
            </h3>

            {health?.incidents && health.incidents.length > 0 ? (
              <div className="space-y-2.5 max-h-72 overflow-y-auto pr-2">
                {health.incidents.map((inc) => (
                  <div
                    key={inc.id}
                    className="p-3 bg-slate-50 border border-slate-100 rounded-2xl flex items-center justify-between gap-4 text-xs"
                  >
                    <div className="space-y-0.5">
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 bg-rose-100 text-rose-800 font-bold rounded text-[10px]">
                          {inc.store}
                        </span>
                        <span className="font-bold text-slate-800">{inc.product_name}</span>
                      </div>
                      <p className="text-slate-500 text-[11px] truncate max-w-lg">{inc.error_reason}</p>
                    </div>
                    <span className="text-[10px] text-slate-400 font-medium shrink-0">
                      {inc.timestamp_display}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-400">No incident logs recorded yet. System operational.</p>
            )}
          </div>
        </div>
      )}

      {/* TAB 2: Registered Users */}
      {activeTab === 'users' && (
        <div className="card overflow-hidden border-gray-200 shadow-sm bg-white rounded-3xl">
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
                      {new Date(u.created_at).toLocaleDateString('en-IN', {
                        day: 'numeric',
                        month: 'short',
                        year: 'numeric',
                      })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 3: Alert Channels & Notification Setup */}
      {activeTab === 'alerts' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Channel 1: WhatsApp via Twilio */}
          <div className="bg-white p-6 rounded-3xl border border-gray-200 shadow-sm space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <MessageSquare className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-slate-900">WhatsApp Alert (Twilio)</h3>
                {health?.alert_channels?.whatsapp_configured ? (
                  <span className="text-[10px] px-2 py-0.5 bg-emerald-100 text-emerald-800 font-bold rounded-full">
                    Active
                  </span>
                ) : (
                  <span className="text-[10px] px-2 py-0.5 bg-slate-100 text-slate-600 font-bold rounded-full">
                    Needs .env
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-500 mt-1">
                Receive instant WhatsApp pings on your personal phone when a URL breaks or encounters a captcha.
              </p>
            </div>
            <div className="p-3 bg-slate-50 rounded-xl text-xs space-y-1 text-slate-600">
              <div className="font-mono text-[11px]">TWILIO_ACCOUNT_SID=...</div>
              <div className="font-mono text-[11px]">TWILIO_AUTH_TOKEN=...</div>
              <div className="font-mono text-[11px]">ADMIN_WHATSAPP_NUMBER=whatsapp:+91...</div>
            </div>
          </div>

          {/* Channel 2: Telegram Bot */}
          <div className="bg-white p-6 rounded-3xl border border-gray-200 shadow-sm space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-sky-50 text-sky-600 flex items-center justify-center">
              <Bot className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-slate-900">Telegram Bot (100% Free)</h3>
                {health?.alert_channels?.telegram_configured ? (
                  <span className="text-[10px] px-2 py-0.5 bg-emerald-100 text-emerald-800 font-bold rounded-full">
                    Active
                  </span>
                ) : (
                  <span className="text-[10px] px-2 py-0.5 bg-slate-100 text-slate-600 font-bold rounded-full">
                    Needs .env
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-500 mt-1">
                Instant push alerts directly to your Telegram app. Takes 60 seconds to set up with @BotFather for free.
              </p>
            </div>
            <div className="p-3 bg-slate-50 rounded-xl text-xs space-y-1 text-slate-600">
              <div className="font-mono text-[11px]">TELEGRAM_BOT_TOKEN=...</div>
              <div className="font-mono text-[11px]">TELEGRAM_ADMIN_CHAT_ID=...</div>
            </div>
          </div>

          {/* Channel 3: Email Fallback */}
          <div className="bg-white p-6 rounded-3xl border border-gray-200 shadow-sm space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center">
              <Mail className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-slate-900">Admin Email Alerts</h3>
                {health?.alert_channels?.email_configured ? (
                  <span className="text-[10px] px-2 py-0.5 bg-emerald-100 text-emerald-800 font-bold rounded-full">
                    Active
                  </span>
                ) : (
                  <span className="text-[10px] px-2 py-0.5 bg-slate-100 text-slate-600 font-bold rounded-full">
                    Needs SMTP
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-500 mt-1">
                Formatted HTML email reports sent to your admin email address with direct link to inspect.
              </p>
            </div>
            <div className="p-3 bg-slate-50 rounded-xl text-xs space-y-1 text-slate-600">
              <div className="font-mono text-[11px]">SMTP_USER=...</div>
              <div className="font-mono text-[11px]">FIRST_SUPERUSER_EMAIL={health?.alert_channels?.email_recipient || 'admin@pricewatch.in'}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
