import { useEffect, useState } from 'react';
import { notificationsApi } from '../services/api';
import type { Notification } from '../types';
import { timeAgo } from '../utils/helpers';
import toast from 'react-hot-toast';
import { Bell, CheckCheck, Mail, MessageSquare, Smartphone } from 'lucide-react';
import EmptyState from '../components/common/EmptyState';

const TYPE_ICONS: Record<string, any> = {
  email: Mail,
  push: Smartphone,
  sms: MessageSquare,
  in_app: Bell,
  call: Bell,
};

export default function Notifications() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchNotifications = () => {
    setLoading(true);
    notificationsApi.list()
      .then((res) => setNotifications(res.data || []))
      .catch(() => toast.error('Failed to load notifications'))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchNotifications();
  }, []);

  const handleMarkAllRead = async () => {
    try {
      await notificationsApi.markAllRead();
      setNotifications((prev) =>
        prev.map((n) => ({ ...n, read_at: new Date().toISOString(), status: 'read' as const }))
      );
      toast.success('All notifications marked as read');
    } catch {
      toast.error('Failed to mark notifications as read');
    }
  };

  const handleMarkRead = async (id: number) => {
    try {
      await notificationsApi.markRead(id);
      setNotifications((prev) =>
        prev.map((n) =>
          n.id === id ? { ...n, read_at: new Date().toISOString(), status: 'read' as const } : n
        )
      );
    } catch {}
  };

  const unreadCount = notifications.filter((n) => !n.read_at).length;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-black text-navy-900 tracking-tight">Notification Center</h1>
          <p className="text-gray-500 text-sm mt-1">
            {unreadCount > 0 ? (
              <span className="text-indigo-600 font-bold">{unreadCount} unread alert{unreadCount !== 1 ? 's' : ''}</span>
            ) : (
              'All notifications caught up!'
            )}
          </p>
        </div>

        {unreadCount > 0 && (
          <button
            onClick={handleMarkAllRead}
            className="btn-secondary text-xs flex items-center gap-1.5 w-fit"
          >
            <CheckCheck className="w-4 h-4 text-emerald-600" />
            <span>Mark All as Read</span>
          </button>
        )}
      </div>

      {/* Notifications List */}
      {loading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="card p-5 h-20 skeleton" />
          ))}
        </div>
      ) : notifications.length === 0 ? (
        <EmptyState
          icon={Bell}
          title="You're all caught up!"
          description="Price drop alerts, stock changes, and target triggers will appear here in real time."
        />
      ) : (
        <div className="space-y-3">
          {notifications.map((notif) => {
            const Icon = TYPE_ICONS[notif.notification_type] || Bell;
            const isUnread = !notif.read_at;

            return (
              <div
                key={notif.id}
                onClick={() => isUnread && handleMarkRead(notif.id)}
                className={`card p-4 sm:p-5 flex gap-4 items-start cursor-pointer transition-all duration-200 ${
                  isUnread
                    ? 'border-indigo-300 bg-indigo-50/40 shadow-xs'
                    : 'bg-white hover:border-gray-300'
                }`}
              >
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 shadow-2xs ${
                  isUnread
                    ? 'bg-gradient-brand text-white shadow-indigo-500/25'
                    : 'bg-gray-100 text-gray-500'
                }`}>
                  <Icon className="w-5 h-5" />
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <h4 className={`text-sm font-bold truncate ${isUnread ? 'text-navy-900 font-extrabold' : 'text-gray-700'}`}>
                      {notif.title}
                    </h4>
                    {isUnread && (
                      <span className="w-2.5 h-2.5 bg-indigo-600 rounded-full flex-shrink-0" />
                    )}
                  </div>
                  <p className="text-xs text-gray-600 mt-1 leading-relaxed">{notif.message}</p>
                  <div className="text-[11px] text-gray-400 mt-2 font-medium">{timeAgo(notif.created_at)}</div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
