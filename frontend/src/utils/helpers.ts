// Utility helpers for PricePing

import type { Platform, Availability, AlertStatus } from '../types';

/** Format price in Indian Rupee notation: ₹1,00,000 */
export function formatINR(price: number | undefined | null): string {
  if (price == null || isNaN(price)) return '—';
  const priceInt = Math.round(price);
  const str = priceInt.toString();
  if (str.length <= 3) return `₹${str}`;
  const lastThree = str.slice(-3);
  const rest = str.slice(0, -3);
  const formatted = rest.replace(/\B(?=(\d{2})+(?!\d))/g, ',');
  return `₹${formatted},${lastThree}`;
}

/** Get percentage change between two prices */
export function getPriceChangePercent(current: number, original: number): number {
  if (!original || original <= 0) return 0;
  return Math.round(((original - current) / original) * 100);
}

/** Format a date string relative to now */
export function timeAgo(dateStr: string | undefined | null): string {
  if (!dateStr) return '—';
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return '—';
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  if (diffMins < 1) return 'just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 30) return `${diffDays}d ago`;
  return date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}

/** Platform display names and colors */
export const PLATFORM_LABELS: Record<Platform, { name: string; color: string; bg: string; domain: string }> = {
  amazon: { name: 'Amazon India', color: 'text-orange-600', bg: 'bg-orange-50 border-orange-200', domain: 'amazon.in' },
  flipkart: { name: 'Flipkart', color: 'text-blue-600', bg: 'bg-blue-50 border-blue-200', domain: 'flipkart.com' },
  ajio: { name: 'AJIO', color: 'text-rose-600', bg: 'bg-rose-50 border-rose-200', domain: 'ajio.com' },
  myntra: { name: 'Myntra', color: 'text-pink-600', bg: 'bg-pink-50 border-pink-200', domain: 'myntra.com' },
  nykaa: { name: 'Nykaa', color: 'text-fuchsia-600', bg: 'bg-fuchsia-50 border-fuchsia-200', domain: 'nykaa.com' },
  unknown: { name: 'Store', color: 'text-gray-600', bg: 'bg-gray-50 border-gray-200', domain: 'store' },
};

export const AVAILABILITY_LABELS: Record<Availability, { label: string; className: string }> = {
  in_stock: { label: 'In Stock', className: 'badge-success' },
  low_stock: { label: 'Low Stock', className: 'badge-warning' },
  out_of_stock: { label: 'Out of Stock', className: 'badge-danger' },
  unavailable: { label: 'Unavailable', className: 'badge-danger' },
  unknown: { label: 'Tracked', className: 'badge-info' },
};

export const ALERT_STATUS_LABELS: Record<AlertStatus, { label: string; className: string }> = {
  active: { label: 'Active', className: 'badge-success' },
  triggered: { label: 'Triggered', className: 'badge-warning' },
  snoozed: { label: 'Snoozed', className: 'badge-info' },
  disabled: { label: 'Disabled', className: 'badge-danger' },
};

export function getPlatformBadgeClass(platform: Platform): string {
  const map: Record<Platform, string> = {
    amazon: 'badge-amazon',
    flipkart: 'badge-flipkart',
    ajio: 'badge-ajio',
    myntra: 'badge-myntra',
    nykaa: 'badge-nykaa',
    unknown: 'badge-info',
  };
  return map[platform] || 'badge-info';
}

export function detectPlatform(url: string): Platform {
  if (!url) return 'unknown';
  const l = url.toLowerCase();
  if (l.includes('amazon.in') || l.includes('amzn.in') || l.includes('amzn.to')) return 'amazon';
  if (l.includes('flipkart.com') || l.includes('fkrt.it')) return 'flipkart';
  if (l.includes('ajio.com')) return 'ajio';
  if (l.includes('myntra.com')) return 'myntra';
  if (l.includes('nykaa.com')) return 'nykaa';
  return 'unknown';
}
