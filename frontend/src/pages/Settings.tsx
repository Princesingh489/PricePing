import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { authApi } from '../services/api';
import toast from 'react-hot-toast';
import { User, Bell, Lock, Save, Loader2 } from 'lucide-react';

export default function Settings() {
  const { user, updateUser } = useAuth();
  const [tab, setTab] = useState<'profile' | 'notifications' | 'security'>('profile');

  // Profile form
  const [profileForm, setProfileForm] = useState({
    name: user?.name || '',
    phone_number: user?.phone_number || '',
  });
  const [profileLoading, setProfileLoading] = useState(false);

  // Notifications form
  const [notifForm, setNotifForm] = useState({
    email_notifications: user?.email_notifications ?? true,
    push_notifications: user?.push_notifications ?? true,
    sms_notifications: user?.sms_notifications ?? false,
  });
  const [notifLoading, setNotifLoading] = useState(false);

  // Password form
  const [passForm, setPassForm] = useState({ old_password: '', new_password: '', confirm_password: '' });
  const [passLoading, setPassLoading] = useState(false);

  const handleProfileSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setProfileLoading(true);
    try {
      const res = await authApi.updateMe(profileForm);
      updateUser(res.data);
      toast.success('Profile details updated! ✅');
    } catch {
      toast.error('Failed to update profile');
    } finally {
      setProfileLoading(false);
    }
  };

  const handleNotifSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setNotifLoading(true);
    try {
      const res = await authApi.updateMe(notifForm);
      updateUser(res.data);
      toast.success('Notification preferences saved! 🔔');
    } catch {
      toast.error('Failed to update preferences');
    } finally {
      setNotifLoading(false);
    }
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    if (passForm.new_password !== passForm.confirm_password) {
      toast.error('New passwords do not match');
      return;
    }
    setPassLoading(true);
    try {
      await authApi.changePassword(passForm.old_password, passForm.new_password);
      toast.success('Password updated successfully! 🔒');
      setPassForm({ old_password: '', new_password: '', confirm_password: '' });
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to update password');
    } finally {
      setPassLoading(false);
    }
  };

  const TABS = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Lock },
  ];

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 py-8 sm:py-12 space-y-8">
      <div>
        <h1 className="text-3xl font-black text-navy-900 tracking-tight">Account Settings</h1>
        <p className="text-gray-500 text-sm mt-1">Manage your account profile, notification alerts, and security</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 bg-gray-100 p-1.5 rounded-2xl border border-gray-200/80">
        {TABS.map(({ id, label, icon: Icon }) => {
          const isSelected = tab === id;
          return (
            <button
              key={id}
              onClick={() => setTab(id as any)}
              className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl text-xs sm:text-sm font-bold transition-all cursor-pointer ${
                isSelected
                  ? 'bg-white text-indigo-700 shadow-sm'
                  : 'text-gray-600 hover:text-navy-900 hover:bg-white/50'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{label}</span>
            </button>
          );
        })}
      </div>

      {/* Profile Tab */}
      {tab === 'profile' && (
        <form onSubmit={handleProfileSave} className="card p-6 sm:p-8 space-y-6 shadow-sm border-gray-200 animate-fade-in">
          <div>
            <h2 className="text-lg font-black text-navy-900">Profile Information</h2>
            <p className="text-xs text-gray-500 mt-0.5">Update your contact details for price drop alerts</p>
          </div>

          <div className="flex items-center gap-4 p-4 bg-indigo-50/50 border border-indigo-100 rounded-2xl">
            <div className="w-12 h-12 bg-gradient-brand rounded-2xl flex items-center justify-center text-white text-xl font-black shadow-md shadow-indigo-500/20">
              {user?.name?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div>
              <div className="font-bold text-navy-900 text-sm">{user?.name}</div>
              <div className="text-xs text-gray-500">{user?.email}</div>
              {user?.is_admin && <span className="badge badge-warning mt-1 text-[10px]">System Administrator</span>}
            </div>
          </div>

          <div>
            <label className="label">Full Name</label>
            <input
              className="input font-semibold"
              value={profileForm.name}
              onChange={(e) => setProfileForm({ ...profileForm, name: e.target.value })}
              required
            />
          </div>

          <div>
            <label className="label">Phone Number (For SMS Alerts)</label>
            <input
              className="input font-semibold"
              placeholder="+91 98765 43210"
              value={profileForm.phone_number}
              onChange={(e) => setProfileForm({ ...profileForm, phone_number: e.target.value })}
            />
          </div>

          <button
            type="submit"
            disabled={profileLoading}
            className="btn-primary w-full py-3 text-sm font-extrabold shadow-md"
          >
            {profileLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            <span>Save Profile</span>
          </button>
        </form>
      )}

      {/* Notifications Tab */}
      {tab === 'notifications' && (
        <form onSubmit={handleNotifSave} className="card p-6 sm:p-8 space-y-6 shadow-sm border-gray-200 animate-fade-in">
          <div>
            <h2 className="text-lg font-black text-navy-900">Notification Preferences</h2>
            <p className="text-xs text-gray-500 mt-0.5">Choose how you want to receive price drop notifications</p>
          </div>

          <div className="space-y-3">
            {[
              { key: 'email_notifications', label: 'Email Alerts', desc: 'Instant digests sent to your inbox when prices drop', icon: '📧' },
              { key: 'push_notifications', label: 'Browser Push', desc: 'Real-time desktop and mobile push notifications', icon: '🔔' },
              { key: 'sms_notifications', label: 'SMS / WhatsApp', desc: 'Urgent price drop text alerts directly to your phone', icon: '📱' },
            ].map(({ key, label, desc, icon }) => {
              const isEnabled = (notifForm as any)[key];
              return (
                <div
                  key={key}
                  className="flex items-center justify-between p-4 rounded-2xl bg-gray-50 border border-gray-200 hover:border-gray-300 transition-all"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-xl">{icon}</span>
                    <div>
                      <div className="font-bold text-navy-900 text-sm">{label}</div>
                      <div className="text-xs text-gray-500 mt-0.5">{desc}</div>
                    </div>
                  </div>

                  <div
                    onClick={() => setNotifForm({ ...notifForm, [key]: !isEnabled })}
                    className={`w-12 h-6.5 rounded-full transition-all duration-200 cursor-pointer relative p-0.5 flex items-center ${
                      isEnabled ? 'bg-indigo-600' : 'bg-gray-300'
                    }`}
                  >
                    <div
                      className={`w-5 h-5 bg-white rounded-full shadow-md transition-transform duration-200 ${
                        isEnabled ? 'translate-x-5.5' : 'translate-x-0.5'
                      }`}
                    />
                  </div>
                </div>
              );
            })}
          </div>

          <button
            type="submit"
            disabled={notifLoading}
            className="btn-primary w-full py-3 text-sm font-extrabold shadow-md"
          >
            {notifLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            <span>Save Preferences</span>
          </button>
        </form>
      )}

      {/* Security Tab */}
      {tab === 'security' && (
        <form onSubmit={handlePasswordChange} className="card p-6 sm:p-8 space-y-5 shadow-sm border-gray-200 animate-fade-in">
          <div>
            <h2 className="text-lg font-black text-navy-900">Security & Password</h2>
            <p className="text-xs text-gray-500 mt-0.5">Update your password to keep your PricePing account secure</p>
          </div>

          <div>
            <label className="label">Current Password</label>
            <input
              type="password"
              className="input"
              value={passForm.old_password}
              onChange={(e) => setPassForm({ ...passForm, old_password: e.target.value })}
              required
            />
          </div>

          <div>
            <label className="label">New Password</label>
            <input
              type="password"
              className="input"
              placeholder="Min. 8 characters"
              value={passForm.new_password}
              onChange={(e) => setPassForm({ ...passForm, new_password: e.target.value })}
              required
            />
          </div>

          <div>
            <label className="label">Confirm New Password</label>
            <input
              type="password"
              className="input"
              value={passForm.confirm_password}
              onChange={(e) => setPassForm({ ...passForm, confirm_password: e.target.value })}
              required
            />
          </div>

          <button
            type="submit"
            disabled={passLoading}
            className="btn-primary w-full py-3 text-sm font-extrabold shadow-md"
          >
            {passLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Lock className="w-4 h-4" />}
            <span>Update Password</span>
          </button>
        </form>
      )}
    </div>
  );
}
