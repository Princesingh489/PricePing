// Shared TypeScript types for PriceWatch India

export type Platform = 'amazon' | 'flipkart' | 'ajio' | 'myntra' | 'nykaa' | 'unknown';
export type Availability = 'in_stock' | 'low_stock' | 'out_of_stock' | 'unavailable' | 'unknown';
export type TrackingStatus = 'active' | 'paused' | 'deleted';
export type AlertType = 'below_price' | 'price_range' | 'percentage_drop';
export type AlertStatus = 'active' | 'triggered' | 'snoozed' | 'disabled';
export type NotificationType = 'email' | 'push' | 'sms' | 'in_app' | 'call';
export type NotificationStatus = 'pending' | 'sent' | 'failed' | 'read';

export interface User {
  id: number;
  name: string;
  email: string;
  phone_number?: string;
  is_admin: boolean;
  email_notifications: boolean;
  push_notifications: boolean;
  sms_notifications: boolean;
  created_at: string;
}

export interface ColorSwatch {
  name: string;
  thumbnail?: string | null;
  price?: number | null;
  mrp?: number | null;
  in_stock: boolean;
  product_url?: string | null;
}

export interface ProductVariant {
  size?: string | null;
  color?: string | null;
  color_thumbnail?: string | null;
  product_url?: string | null;
  price: number;
  mrp?: number | null;
  discount_percentage?: number | null;
  in_stock: boolean;
  sku?: string | null;
}

export interface Product {
  id: number;
  platform: Platform;
  store?: string;
  external_product_id?: string;
  product_name: string;
  product_url: string;
  product_image?: string;
  images?: string[];
  colors?: ColorSwatch[];
  selected_color?: string | null;
  selected_size?: string | null;
  brand?: string;
  model?: string;
  variant?: string;
  variants?: ProductVariant[];
  current_price?: number;
  original_price?: number;
  discount_percentage?: number;
  saved_amount?: number;
  lowest_price?: number;
  highest_price?: number;
  rating?: number;
  rating_count?: number;
  review_count?: number;
  currency?: string;
  availability: Availability;
  observed_at?: string | null;
  last_checked?: string;
  created_at: string;
}

export interface TrackedProduct {
  id: number;
  user_id: number;
  product_id: number;
  tracking_status: TrackingStatus;
  target_min_price?: number;
  target_max_price?: number;
  notes?: string;
  created_at: string;
  tracked_at?: string;
  product: Product;
}

export interface TrackedProductsResponse {
  items: TrackedProduct[];
  total: number;
}

export interface PriceHistory {
  id: number;
  product_id: number;
  store?: string;
  price: number;
  original_price?: number;
  availability: Availability;
  source?: string;
  verified?: boolean;
  checked_at: string;
}

export interface MatchAudit {
  brand_match?: boolean | null;
  model_match?: boolean | null;
  gtin_match?: boolean | null;
  color_match?: boolean | null;
  size_match?: boolean | null;
  storage_match?: boolean | null;
  ram_match?: boolean | null;
  title_similarity?: number;
  variant_match?: boolean | null;
  match_confidence?: number;
  match_reason?: string | null;
}

export interface CanonicalProduct {
  canonical_product_id: string;
  brand?: string | null;
  product_name?: string | null;
  category?: string | null;
  model?: string | null;
  mpn?: string | null;
  gtin?: string | null;
  ean?: string | null;
  upc?: string | null;
  gender?: string | null;
  color?: string | null;
  size?: string | null;
  storage?: string | null;
  ram?: string | null;
  pack_count?: number;
  images?: string[];
  attributes?: Record<string, any>;
}

export interface AvailabilitySummary {
  all_available: boolean;
  available_count: number;
  total_stores: number;
  verified_match_count: number;
  message: string;
  status: 'all_available' | 'partially_available' | 'unavailable';
}

export interface StoreOffer {
  store: string;
  store_name: string;
  logo: string;
  price: number | null;
  original_price?: number | null;
  shipping_price: number;
  delivery_text?: string | null;
  coupon_text?: string | null;
  url?: string | null;
  availability: string;
  is_verified_match: boolean;
  match_status?: 'verified_match' | 'possible_match' | 'no_verified_match';
  status: 'available' | 'unavailable' | 'pending' | 'no_match';
  match_confidence?: number | null;
  match_signals?: Record<string, any> | null;
  audit?: MatchAudit | null;
  match_reason?: string | null;
  badge_label?: string | null;
  is_purchasable?: boolean;
  variants?: ProductVariant[];
  observed_at?: string | null;
}

export interface RealPriceHistoryPoint {
  timestamp: string;
  date: string;
  price: number;
  original_price?: number | null;
  store: string;
  source: string;
  availability: string;
}

export interface RealPriceStatistics {
  current_price: number | null;
  highest_price: number | null;
  lowest_price: number | null;
  average_price: number | null;
  median_price: number | null;
  price_change: number | null;
  percentage_change: number | null;
  potential_saving?: number | null;
  lowest_price_date: string | null;
  highest_price_date: string | null;
  days_since_lowest: number | null;
  days_since_highest: number | null;
  observation_count: number;
  is_reliable: boolean;
  recommendation: string;
  recommendation_reason: string;
}

export interface RealPriceHistoryResponse {
  product_id: number;
  store: string;
  currency: string;
  history_start_date: string | null;
  history_end_date: string | null;
  observation_count: number;
  source: string;
  has_history: boolean;
  coverage_label: string;
  data: RealPriceHistoryPoint[];
  store_histories?: Record<string, RealPriceHistoryPoint[]>;
  statistics?: RealPriceStatistics | null;
}

export interface CrossStoreComparison {
  product_id: number;
  product_name: string;
  lowest_store: string | null;
  lowest_price: number | null;
  highest_price: number | null;
  max_savings: number | null;
  stores: StoreOffer[];
}

export interface ResolveUrlResponse {
  detected_store: string;
  extracted_product_id: string | null;
  product: Product;
  canonical_product?: CanonicalProduct | null;
  comparison: StoreOffer[];
  availability_summary?: AvailabilitySummary | null;
  statistics: RealPriceStatistics;
  history_summary: {
    history_start_date: string | null;
    history_end_date: string | null;
    observation_count: number;
    source: string;
    has_history: boolean;
    coverage_label: string;
  };
  is_already_tracked: boolean;
  tracker_id: number | null;
  search_status?: string;
}

export interface PriceAlert {
  id: number;
  user_id: number;
  product_id: number;
  alert_type: AlertType;
  target_price?: number;
  minimum_price?: number;
  maximum_price?: number;
  percentage_drop?: number;
  base_price?: number;
  alert_status: AlertStatus;
  notify_email: boolean;
  notify_push: boolean;
  notify_sms: boolean;
  notify_in_app: boolean;
  last_triggered_at?: string;
  created_at: string;
  product: Product;
}

export interface Notification {
  id: number;
  user_id: number;
  product_id?: number;
  notification_type: NotificationType;
  title: string;
  message: string;
  status: NotificationStatus;
  sent_at?: string;
  read_at?: string;
  created_at: string;
}

export interface DashboardStats {
  total_tracked: number;
  active_alerts: number;
  alerts_triggered_today: number;
  products_in_stock: number;
  products_out_of_stock: number;
  unread_notifications: number;
}

export type DealRecommendation = 'BUY_NOW' | 'WAIT' | 'WATCH' | 'INSUFFICIENT_DATA' | 'FAIR_PRICE';

export interface DealScore {
  recommendation: DealRecommendation;
  confidence: number;
  percentile: number | null;
  avg_price: number | null;
  lowest_price: number | null;
  highest_price: number | null;
  data_points: number;
  tracking_days: number;
  message: string;
}

export interface PriceStats {
  lowest_ever: number | null;
  highest_ever: number | null;
  average_price: number | null;
  data_points: number;
  tracking_days: number;
}

export interface ProductDetail {
  tracker_id: number;
  product: Product;
  price_history: PriceHistory[];
  deal_score: DealScore;
  stats: PriceStats;
  real_statistics?: RealPriceStatistics;
  cross_store_offers?: StoreOffer[];
  canonical_product?: CanonicalProduct | null;
  availability_summary?: AvailabilitySummary | null;
  history_metadata?: {
    history_start_date: string | null;
    history_end_date: string | null;
    observation_count: number;
    source: string;
    has_history: boolean;
    coverage_label: string;
    store_histories?: Record<string, RealPriceHistoryPoint[]>;
  };
  existing_alert: PriceAlert | null;
}

export interface TrendingDeal {
  id: string;
  product_id: string;
  store: Platform;
  title: string;
  brand?: string | null;
  category: string;
  image_url: string;
  product_url: string;
  price: number;
  mrp?: number | null;
  discount_percent: number;
  saved_amount: number;
  currency: string;
  availability: string;
  variant?: Record<string, any> | null;
  rating?: number | null;
  rating_count?: number | null;
  deal_score: number;
  historical_badge?: string | null;
  is_live: boolean;
  price_status: string;
  deal_status: string;
  last_verified_at: string;
  freshness: string;
  freshness_label: string;
}

export interface TrendingDealsResponse {
  updated_at: string;
  total_deals: number;
  stores_represented: string[];
  deals: TrendingDeal[];
}
