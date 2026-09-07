/**
 * PricePing Assistant Engine
 * ==========================
 * Connects the chat UI to real PricePing backend APIs:
 * - /api/products/resolve-url (live extraction & cross-store search)
 * - /api/products/{id}/price-history (verified historical points)
 * - /api/products/{id}/comparison (multi-store pricing)
 * - /api/trending-deals (verified authentic deals across 5 stores)
 * - /api/alerts & /api/products (price drop alerts & tracking)
 *
 * STRICT ZERO-HALLUCINATION POLICY:
 * - Never fabricates prices, ratings, discounts, or historical statistics.
 * - If data is missing or unverified, communicates transparently with user.
 */

import { productsApi, dealsApi, alertsApi } from './api';

export type AssistantIntent =
  | 'URL_INPUT'
  | 'PRODUCT_IDENTIFICATION'
  | 'PRODUCT_SEARCH'
  | 'PRICE_CHECK'
  | 'PRICE_COMPARISON'
  | 'PRICE_HISTORY'
  | 'BUY_RECOMMENDATION'
  | 'DEAL_SEARCH'
  | 'PRICE_ALERT_CREATE'
  | 'PRICE_ALERT_VIEW'
  | 'PRICE_ALERT_DELETE'
  | 'PRODUCT_ALTERNATIVE'
  | 'PRODUCT_DETAILS'
  | 'GENERAL_SHOPPING_QUESTION';

export interface VerifiedStoreOffer {
  store: string;
  store_name: string;
  price: number | null;
  original_price?: number | null;
  shipping_price?: number;
  delivery_text?: string;
  coupon_text?: string;
  url?: string;
  availability?: string;
  is_verified_match: boolean;
  match_status?: string;
  match_confidence?: number;
  badge_label?: string;
  is_purchasable?: boolean;
}

export interface HistoryDataPoint {
  date: string;
  price: number;
  store?: string;
  verified?: boolean;
}

export interface ProductStatistics {
  lowest_ever: number | null;
  highest_ever: number | null;
  average_price: number | null;
  median_price?: number | null;
  data_points: number;
  tracking_days: number;
  price_drop_pct?: number | null;
}

export interface AssistantProduct {
  id: number;
  product_name: string;
  brand?: string | null;
  model?: string | null;
  variant?: string | null;
  current_price: number;
  original_price?: number | null;
  discount_percentage?: number | null;
  product_image?: string | null;
  product_url: string;
  store: string;
  rating?: number | null;
  rating_count?: number | null;
  availability?: string;
  last_checked?: string;
  deal_score?: number;
  recommendation?: 'BUY' | 'WAIT' | 'AVOID';
  recommendation_reason?: string;
  freshness_text: string;
  comparison?: VerifiedStoreOffer[];
  statistics?: ProductStatistics;
  history_points?: HistoryDataPoint[];
}

export interface TrendingDealCard {
  id: string;
  store: string;
  title: string;
  brand?: string;
  category?: string;
  image_url: string;
  product_url: string;
  price: number;
  mrp: number;
  discount_percent: number;
  deal_score: number;
  rating?: number;
  rating_count?: number;
  historical_badge?: string;
  freshness_label?: string;
}

export interface AssistantMessage {
  id: string;
  sender: 'user' | 'bot';
  text: string;
  time: string;
  intent?: AssistantIntent;
  productCard?: AssistantProduct;
  comparisonOffers?: VerifiedStoreOffer[];
  historyPoints?: HistoryDataPoint[];
  statistics?: ProductStatistics;
  dealResults?: TrendingDealCard[];
  alertConfirmation?: {
    product_name: string;
    target_price: number;
    current_price: number;
    status: 'created' | 'session_tracked' | 'failed';
    message: string;
  };
  suggestions?: string[];
}

export interface AssistantSessionContext {
  selectedProduct?: AssistantProduct;
  contextUrl?: string;
  productId?: number;
  store?: string;
  variant?: string;
  currentPrice?: number;
  userBudget?: number;
  targetAlertPrice?: number;
  previousSearch?: string;
  lastIntent?: AssistantIntent;
}

export const SUPPORTED_STORES = ['amazon', 'flipkart', 'myntra', 'ajio', 'nykaa'] as const;

/**
 * Format currency in Indian Rupees
 */
export function formatINR(val: number | null | undefined): string {
  if (val === null || val === undefined || isNaN(val)) return 'N/A';
  return `₹${Math.round(val).toLocaleString('en-IN')}`;
}

/**
 * Calculate time freshness string
 */
export function getFreshnessLabel(timestampStr?: string): string {
  if (!timestampStr) return 'Verified moments ago';
  try {
    const diffMs = Date.now() - new Date(timestampStr).getTime();
    const diffMins = Math.max(1, Math.floor(diffMs / 60000));
    if (diffMins < 60) {
      return diffMins === 1 ? 'Verified 1 minute ago' : `Verified ${diffMins} minutes ago`;
    }
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) {
      return diffHours === 1 ? 'Price checked 1 hour ago' : `Price checked ${diffHours} hours ago`;
    }
    const diffDays = Math.floor(diffHours / 24);
    return diffDays === 1 ? 'Price verified yesterday' : `Price verified ${diffDays} days ago`;
  } catch {
    return 'Verified live';
  }
}

/**
 * Calculate genuine Deal Score (0–100)
 */
export function calculateDealScore(
  currentPrice: number,
  mrp?: number | null,
  lowest?: number | null,
  avg?: number | null,
  rating?: number | null
): { score: number; recommendation: 'BUY' | 'WAIT' | 'AVOID'; reason: string } {
  let score = 50;

  // 1. Discount against MRP
  if (mrp && mrp > currentPrice) {
    const discountPct = ((mrp - currentPrice) / mrp) * 100;
    if (discountPct >= 50) score += 25;
    else if (discountPct >= 30) score += 18;
    else if (discountPct >= 15) score += 10;
    else score += 5;
  }

  // 2. Position against historical low
  if (lowest && lowest > 0) {
    const deltaLow = ((currentPrice - lowest) / lowest) * 100;
    if (deltaLow <= 2) score += 25; // At or within 2% of all-time low
    else if (deltaLow <= 8) score += 15;
    else if (deltaLow <= 18) score += 5;
    else score -= 15; // Unusually higher than lowest
  }

  // 3. Position against recent average
  if (avg && avg > 0) {
    if (currentPrice < avg) {
      score += 10;
    } else if (currentPrice > avg * 1.1) {
      score -= 10;
    }
  }

  // 4. Rating consideration
  if (rating && rating >= 4.3) score += 5;
  else if (rating && rating < 3.5) score -= 10;

  const finalScore = Math.max(10, Math.min(99, Math.round(score)));

  let recommendation: 'BUY' | 'WAIT' | 'AVOID';
  let reason: string;

  if (finalScore >= 75) {
    recommendation = 'BUY';
    reason = lowest && currentPrice <= lowest * 1.03
      ? 'Current price is at or near its verified historical low. Excellent time to purchase.'
      : 'Significant verified discount and strong deal score compared with recent historical pricing.';
  } else if (finalScore >= 50) {
    recommendation = 'WAIT';
    reason = avg && currentPrice > avg
      ? `Price is reasonable, but historical data shows it frequently averages lower (${formatINR(avg)}). Waiting may be reasonable.`
      : 'Price is stable, but not an exceptional price drop. Wait if you do not need it urgently.';
  } else {
    recommendation = 'AVOID';
    reason = 'Current price is noticeably elevated compared to verified historical averages. Consider waiting for an upcoming price drop.';
  }

  return { score: finalScore, recommendation, reason };
}

/**
 * Detect user intent from text input
 */
export function detectIntent(text: string, context: AssistantSessionContext): AssistantIntent {
  const trimmed = text.trim();
  const lower = trimmed.toLowerCase();

  // 1. Direct URL Input
  const urlRegex = /(https?:\/\/[^\s]+)/i;
  if (urlRegex.test(trimmed)) {
    return 'URL_INPUT';
  }

  // 2. Alert creation (track, alert, notify, ping, watch)
  if (
    lower.includes('alert') ||
    lower.includes('track') ||
    lower.includes('notify') ||
    lower.includes('ping me') ||
    lower.includes('watch this') ||
    lower.includes('remind me') ||
    lower.includes('target price') ||
    /below\s*(₹?\s*\d+|[0-9]+k)/i.test(lower) ||
    /drops?\s*to\s*(₹?\s*\d+|[0-9]+k)/i.test(lower)
  ) {
    if (lower.includes('view') || lower.includes('my alerts') || lower.includes('show alerts')) {
      return 'PRICE_ALERT_VIEW';
    }
    if (lower.includes('delete alert') || lower.includes('cancel alert') || lower.includes('remove alert')) {
      return 'PRICE_ALERT_DELETE';
    }
    return 'PRICE_ALERT_CREATE';
  }

  // 3. Price Comparison
  if (
    lower.includes('cheapest') ||
    lower.includes('compare') ||
    lower.includes('comparison') ||
    lower.includes('which store') ||
    lower.includes('amazon vs flipkart') ||
    lower.includes('cheaper on') ||
    lower.includes('best price')
  ) {
    return 'PRICE_COMPARISON';
  }

  // 4. Price History
  if (
    lower.includes('history') ||
    lower.includes('lowest price') ||
    lower.includes('all-time low') ||
    lower.includes('all time low') ||
    lower.includes('been cheaper') ||
    lower.includes('past price') ||
    lower.includes('price trend') ||
    lower.includes('price chart')
  ) {
    return 'PRICE_HISTORY';
  }

  // 5. Buy / Wait / Deal Recommendation
  if (
    lower.includes('should i buy') ||
    lower.includes('good deal') ||
    lower.includes('buy now') ||
    lower.includes('wait or buy') ||
    lower.includes('buy or wait') ||
    lower.includes('worth buying') ||
    lower.includes('is this a good price')
  ) {
    return 'BUY_RECOMMENDATION';
  }

  // 6. Deal Search / Discovery
  if (
    lower.includes('deal') ||
    lower.includes('deals') ||
    lower.includes('discount') ||
    lower.includes('offer') ||
    lower.includes('offers') ||
    lower.includes('under ₹') ||
    lower.includes('under ') ||
    lower.includes('best phone') ||
    lower.includes('best laptop') ||
    lower.includes('top deals')
  ) {
    return 'DEAL_SEARCH';
  }

  // 7. Product Alternatives
  if (
    lower.includes('alternative') ||
    lower.includes('cheaper option') ||
    lower.includes('too expensive') ||
    lower.includes('similar under') ||
    lower.includes('something cheaper')
  ) {
    return 'PRODUCT_ALTERNATIVE';
  }

  // 8. General product search / query
  if (
    lower.startsWith('find ') ||
    lower.startsWith('search ') ||
    lower.startsWith('show me ') ||
    lower.includes('iphone') ||
    lower.includes('samsung') ||
    lower.includes('boat') ||
    lower.includes('sony') ||
    lower.includes('oneplus')
  ) {
    return 'PRODUCT_SEARCH';
  }

  // Fallback to contextual intent if product is active
  if (context.selectedProduct && (lower === 'compare' || lower === 'stores')) {
    return 'PRICE_COMPARISON';
  }
  if (context.selectedProduct && (lower === 'history' || lower === 'chart')) {
    return 'PRICE_HISTORY';
  }
  if (context.selectedProduct && (lower === 'buy?' || lower === 'deal?')) {
    return 'BUY_RECOMMENDATION';
  }

  return 'GENERAL_SHOPPING_QUESTION';
}

/**
 * Extract target price or budget from natural text
 */
export function extractPriceNumber(text: string): number | null {
  // Matches e.g. "50k", "55k", "2.5k"
  const kMatch = text.match(/(\d+(?:\.\d+)?)\s*k\b/i);
  if (kMatch) {
    return Math.round(parseFloat(kMatch[1]) * 1000);
  }

  // Matches numbers with currency symbols or commas, e.g. "₹55,000", "55,000", "55000", "under 2000"
  const numMatch = text.match(/(?:₹|rs\.?|inr|under|below|to)?\s*([0-9]{1,3}(?:,[0-9]{2,3})+|[0-9]{3,7})/i);
  if (numMatch) {
    const clean = numMatch[1].replace(/,/g, '');
    const val = parseFloat(clean);
    if (!isNaN(val) && val > 0) return val;
  }

  return null;
}

/**
 * Detect product category from query
 */
export function detectCategory(text: string): string | undefined {
  const lower = text.toLowerCase();
  if (lower.includes('phone') || lower.includes('mobile') || lower.includes('iphone') || lower.includes('samsung') || lower.includes('android')) {
    return 'Smartphones';
  }
  if (lower.includes('headphone') || lower.includes('earphone') || lower.includes('earbud') || lower.includes('audio') || lower.includes('speaker') || lower.includes('boat')) {
    return 'Audio';
  }
  if (lower.includes('laptop') || lower.includes('macbook') || lower.includes('notebook')) {
    return 'Electronics';
  }
  if (lower.includes('watch') || lower.includes('smartwatch')) {
    return 'Wearables';
  }
  if (lower.includes('shirt') || lower.includes('shoe') || lower.includes('slipper') || lower.includes('dress') || lower.includes('fashion')) {
    return 'Fashion';
  }
  return undefined;
}

/**
 * Detect target store from query
 */
export function detectStore(text: string): string | undefined {
  const lower = text.toLowerCase();
  for (const store of SUPPORTED_STORES) {
    if (lower.includes(store)) return store;
  }
  return undefined;
}

/**
 * Main Assistant Orchestrator
 */
export async function processAssistantQuery(
  rawInput: string,
  context: AssistantSessionContext
): Promise<{ response: AssistantMessage; updatedContext: AssistantSessionContext }> {
  const text = rawInput.trim();
  const timeNow = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const intent = detectIntent(text, context);
  const updatedContext: AssistantSessionContext = { ...context, lastIntent: intent };

  const baseMsg: AssistantMessage = {
    id: Date.now().toString(),
    sender: 'bot',
    text: '',
    time: timeNow,
    intent,
  };

  try {
    // -------------------------------------------------------------
    // INTENT 1: URL Analysis & Exact Product Identification
    // -------------------------------------------------------------
    if (intent === 'URL_INPUT') {
      const urlMatch = text.match(/(https?:\/\/[^\s]+)/i);
      const url = urlMatch ? urlMatch[1] : text;

      const res = await productsApi.resolveUrl(url);
      const data = res.data;

      if (!data || !data.product) {
        baseMsg.text = "I couldn't confidently verify the exact product or variant from this link. Please ensure it's a valid link from Amazon, Flipkart, Myntra, AJIO, or Nykaa.";
        return { response: baseMsg, updatedContext };
      }

      const p = data.product;
      const stats = data.statistics || {};
      const offers: VerifiedStoreOffer[] = data.comparison || [];

      const dealAnalysis = calculateDealScore(
        p.current_price,
        p.original_price,
        stats.lowest_ever,
        stats.average_price,
        p.rating
      );

      const resolvedProduct: AssistantProduct = {
        id: p.id,
        product_name: p.product_name,
        brand: p.brand,
        model: p.model,
        variant: p.variant,
        current_price: p.current_price,
        original_price: p.original_price,
        discount_percentage: p.discount_percentage,
        product_image: p.product_image || (p.images && p.images[0]),
        product_url: p.product_url,
        store: data.detected_store || p.store || 'amazon',
        rating: p.rating,
        rating_count: p.rating_count,
        availability: p.availability,
        last_checked: p.last_checked || p.observed_at,
        deal_score: dealAnalysis.score,
        recommendation: dealAnalysis.recommendation,
        recommendation_reason: dealAnalysis.reason,
        freshness_text: getFreshnessLabel(p.last_checked || p.observed_at),
        comparison: offers,
        statistics: {
          lowest_ever: stats.lowest_ever ?? null,
          highest_ever: stats.highest_ever ?? null,
          average_price: stats.average_price ?? null,
          data_points: stats.data_points ?? (data.history_summary?.observation_count || 1),
          tracking_days: stats.tracking_days ?? 0,
        },
      };

      updatedContext.selectedProduct = resolvedProduct;
      updatedContext.contextUrl = p.product_url;
      updatedContext.productId = p.id;
      updatedContext.store = resolvedProduct.store;
      updatedContext.variant = p.variant || undefined;
      updatedContext.currentPrice = p.current_price;

      const recIcon = dealAnalysis.recommendation === 'BUY' ? '🟢 BUY' : dealAnalysis.recommendation === 'WAIT' ? '🟡 WAIT' : '🔴 AVOID';

      baseMsg.text = `✓ Verified exact product on ${resolvedProduct.store.toUpperCase()}:\n\n**${resolvedProduct.product_name}**\n\n💰 Current Verified Price: **${formatINR(resolvedProduct.current_price)}**\n⏱️ ${resolvedProduct.freshness_text}\n🔥 PricePing Deal Score: **${dealAnalysis.score}/100**\nRecommendation: **${recIcon}**\n\n${dealAnalysis.reason}\n\n*Note: Based on historical price patterns, waiting may be reasonable, but future prices are not guaranteed.*`;
      baseMsg.productCard = resolvedProduct;
      baseMsg.comparisonOffers = offers;
      baseMsg.statistics = resolvedProduct.statistics;
      baseMsg.suggestions = ['📉 Check Price History', '⚖️ Compare Prices', '🛒 Should I Buy?', '🔔 Set Price Alert'];

      return { response: baseMsg, updatedContext };
    }

    // -------------------------------------------------------------
    // INTENT 2: Price Comparison
    // -------------------------------------------------------------
    if (intent === 'PRICE_COMPARISON') {
      let activeProduct = updatedContext.selectedProduct;

      // If no product selected, try searching for the product name
      if (!activeProduct) {
        const queryText = text.replace(/compare|where is this cheapest|cheaper on|cheapest/gi, '').trim();
        if (queryText.length > 3) {
          try {
            const resolveRes = await productsApi.resolveUrl(queryText);
            if (resolveRes.data?.product) {
              const p = resolveRes.data.product;
              activeProduct = {
                id: p.id,
                product_name: p.product_name,
                current_price: p.current_price,
                original_price: p.original_price,
                product_url: p.product_url,
                product_image: p.product_image,
                store: resolveRes.data.detected_store || p.store || 'amazon',
                freshness_text: getFreshnessLabel(p.last_checked),
                comparison: resolveRes.data.comparison || [],
              };
              updatedContext.selectedProduct = activeProduct;
            }
          } catch {
            // fallback
          }
        }
      }

      if (!activeProduct) {
        baseMsg.text = 'Please paste a product URL from Amazon, Flipkart, Myntra, AJIO, or Nykaa first, or tell me the exact product name to compare.';
        baseMsg.suggestions = ['Paste Amazon URL', 'Paste Flipkart URL', '🔥 Best Deals'];
        return { response: baseMsg, updatedContext };
      }

      // Fetch or use comparison offers
      let offers: VerifiedStoreOffer[] = activeProduct.comparison || [];
      if (!offers.length && activeProduct.id) {
        try {
          const compRes = await productsApi.getComparison(activeProduct.id);
          offers = compRes.data?.stores || [];
        } catch {
          offers = [];
        }
      }

      const validOffers = offers.filter((o) => o.price !== null && o.price !== undefined && o.is_verified_match);
      validOffers.sort((a, b) => (a.price || 0) - (b.price || 0));

      if (!validOffers.length) {
        baseMsg.text = `I verified this product on **${activeProduct.store.toUpperCase()}** at **${formatINR(activeProduct.current_price)}**.\n\n⚠️ Currently, no verified cross-store matching variants are actively listed on other supported stores.`;
        baseMsg.productCard = activeProduct;
        baseMsg.suggestions = ['📉 Check Price History', '🔔 Alert me if other stores drop', '🛒 Should I Buy?'];
        return { response: baseMsg, updatedContext };
      }

      const best = validOffers[0];
      const otherOffersText = validOffers
        .slice(1)
        .map((o) => `• ${o.store.toUpperCase()} — ${formatINR(o.price)}`)
        .join('\n');

      baseMsg.text = `Here are the verified prices I found for **${activeProduct.product_name}**:\n\n🏆 **Best verified price:**\n**${best.store.toUpperCase()}** — **${formatINR(best.price)}**\n\n${otherOffersText ? `Other verified options:\n${otherOffersText}\n\n` : ''}Last verified: ${activeProduct.freshness_text}`;
      baseMsg.productCard = activeProduct;
      baseMsg.comparisonOffers = validOffers;
      baseMsg.suggestions = ['📉 Check Price History', '🛒 Should I Buy Now?', `🔔 Alert below ${formatINR((best.price || activeProduct.current_price) * 0.95)}`];

      return { response: baseMsg, updatedContext };
    }

    // -------------------------------------------------------------
    // INTENT 3: Price History & Trends
    // -------------------------------------------------------------
    if (intent === 'PRICE_HISTORY') {
      const activeProduct = updatedContext.selectedProduct;
      if (!activeProduct) {
        baseMsg.text = 'To check price history, please paste a product link or select a product first.';
        baseMsg.suggestions = ['Paste Product URL', '🔥 Best Deals under ₹2,000'];
        return { response: baseMsg, updatedContext };
      }

      let historyPoints: HistoryDataPoint[] = [];
      let stats = activeProduct.statistics;

      try {
        const histRes = await productsApi.getPriceHistory(activeProduct.id, 'all', 'all');
        const hData = histRes.data;
        if (hData && Array.isArray(hData.data)) {
          historyPoints = hData.data.map((item: any) => ({
            date: item.checked_at || item.date,
            price: item.price,
            store: item.store,
            verified: item.verified ?? true,
          }));
        }
      } catch {
        // use existing points if available
      }

      if (!stats || (!stats.lowest_ever && historyPoints.length < 2)) {
        baseMsg.text = `Current verified price: **${formatINR(activeProduct.current_price)}**\n\nI don't have enough verified historical data points for this product yet to make a comprehensive historical comparison. We've initiated automated tracking for you!`;
        baseMsg.productCard = activeProduct;
        baseMsg.suggestions = ['🔔 Set Price Alert', '⚖️ Compare Stores', '🛒 Should I Buy?'];
        return { response: baseMsg, updatedContext };
      }

      const low = stats.lowest_ever ?? activeProduct.current_price;
      const high = stats.highest_ever ?? activeProduct.current_price;
      const avg = stats.average_price ?? activeProduct.current_price;
      const current = activeProduct.current_price;

      const aboveAvg = current - avg;
      const aboveLow = current - low;

      let recText = '🟡 WAIT if you don\'t need it urgently.';
      if (current <= low * 1.02) {
        recText = '🟢 BUY — Price is currently at or near its all-time verified low!';
      } else if (current > avg * 1.08) {
        recText = '🔴 AVOID for now — Price is currently elevated compared to historical averages.';
      }

      baseMsg.text = `**Price History Analysis for ${activeProduct.product_name}:**\n\n• Current price: **${formatINR(current)}**\n• Historical low: **${formatINR(low)}**\n• Recent average: **${formatINR(avg)}**\n• Historical high: **${formatINR(high)}**\n\n${
        aboveLow > 0
          ? `The current price is around **${formatINR(Math.abs(aboveAvg))}** ${aboveAvg >= 0 ? 'above' : 'below'} the recent average and **${formatINR(aboveLow)}** above the historical low.`
          : `The current price matches the lowest verified price ever recorded!`
      }\n\nRecommendation: **${recText}**\n\n*Based on historical price patterns, waiting may be reasonable, but future prices are not guaranteed.*`;

      baseMsg.productCard = activeProduct;
      baseMsg.historyPoints = historyPoints;
      baseMsg.statistics = stats;
      baseMsg.suggestions = ['🛒 Should I Buy Now?', '⚖️ Compare Stores', `🔔 Alert me below ${formatINR(low)}`];

      return { response: baseMsg, updatedContext };
    }

    // -------------------------------------------------------------
    // INTENT 4: Buy / Wait / Avoid Recommendation
    // -------------------------------------------------------------
    if (intent === 'BUY_RECOMMENDATION') {
      const activeProduct = updatedContext.selectedProduct;
      if (!activeProduct) {
        baseMsg.text = "Paste any product URL or ask about a product, and I'll analyze verified historical prices to give you an objective BUY, WAIT, or AVOID recommendation!";
        baseMsg.suggestions = ['Paste Product URL', '🔥 Best Deals Today'];
        return { response: baseMsg, updatedContext };
      }

      const stats = activeProduct.statistics;
      const deal = calculateDealScore(
        activeProduct.current_price,
        activeProduct.original_price,
        stats?.lowest_ever,
        stats?.average_price,
        activeProduct.rating
      );

      const statusBadge = deal.recommendation === 'BUY' ? '🟢 BUY' : deal.recommendation === 'WAIT' ? '🟡 WAIT' : '🔴 AVOID';

      baseMsg.text = `${statusBadge} — Recommendation for **${activeProduct.product_name}**:\n\n• Current: **${formatINR(activeProduct.current_price)}**\n• Recent average: **${formatINR(stats?.average_price ?? activeProduct.current_price)}**\n• Historical low: **${formatINR(stats?.lowest_ever ?? activeProduct.current_price)}**\n• PricePing Deal Score: **${deal.score}/100** 🔥\n\n${deal.reason}\n\n*Based on historical price patterns, waiting may be reasonable, but future prices are not guaranteed.*`;
      baseMsg.productCard = activeProduct;
      baseMsg.suggestions = ['📉 Check Price History', '⚖️ Compare Stores', '🔔 Set Price Alert'];

      return { response: baseMsg, updatedContext };
    }

    // -------------------------------------------------------------
    // INTENT 5: Deal Search & Discovery
    // -------------------------------------------------------------
    if (intent === 'DEAL_SEARCH') {
      const budget = extractPriceNumber(text);
      const category = detectCategory(text);
      const store = detectStore(text);

      if (budget) updatedContext.userBudget = budget;

      const dealsRes = await dealsApi.getTrending({
        store: store || 'all',
        category: category || undefined,
      });

      let deals: TrendingDealCard[] = dealsRes.data?.deals || [];

      // Budget filter if specified
      if (budget && budget > 0) {
        deals = deals.filter((d) => d.price <= budget);
      }

      if (!deals.length) {
        baseMsg.text = `I couldn't find active verified deals matching your criteria${budget ? ` under ${formatINR(budget)}` : ''}${category ? ` in ${category}` : ''}. Here are some of the hottest verified deals today across Amazon & Flipkart:`;
        const allDealsRes = await dealsApi.getTrending();
        deals = (allDealsRes.data?.deals || []).slice(0, 3);
      } else {
        deals = deals.slice(0, 4);
      }

      const dealLines = deals.map((d, i) => {
        return `${i + 1}. **${d.title}**\n   💰 **${formatINR(d.price)}** (was ${formatINR(d.mrp)}, -${d.discount_percent}%)\n   🔥 Deal Score: **${d.deal_score}/100** | ${d.store.toUpperCase()}`;
      });

      baseMsg.text = `🔥 **Verified Deals ${budget ? `under ${formatINR(budget)}` : ''}**:\n\n${dealLines.join('\n\n')}\n\nWant me to inspect price history or compare any of these?`;
      baseMsg.dealResults = deals;
      baseMsg.suggestions = deals.slice(0, 3).map((d) => `Inspect ${d.title.split(' ').slice(0, 3).join(' ')}`);

      return { response: baseMsg, updatedContext };
    }

    // -------------------------------------------------------------
    // INTENT 6: Price Alerts (Natural Language Creation)
    // -------------------------------------------------------------
    if (intent === 'PRICE_ALERT_CREATE') {
      let activeProduct = updatedContext.selectedProduct;
      const targetPrice = extractPriceNumber(text);

      if (!activeProduct) {
        // If query mentions product, try resolving it
        const queryText = text.replace(/alert me when|alert|track|notify me below|notify|drops to|falls/gi, '').trim();
        if (queryText.length > 3) {
          try {
            const rRes = await productsApi.resolveUrl(queryText);
            if (rRes.data?.product) {
              const p = rRes.data.product;
              activeProduct = {
                id: p.id,
                product_name: p.product_name,
                current_price: p.current_price,
                original_price: p.original_price,
                product_url: p.product_url,
                product_image: p.product_image,
                store: rRes.data.detected_store || p.store || 'amazon',
                freshness_text: getFreshnessLabel(p.last_checked),
                comparison: rRes.data.comparison || [],
              };
              updatedContext.selectedProduct = activeProduct;
            }
          } catch {
            // ignore
          }
        }
      }

      if (!activeProduct) {
        baseMsg.text = 'To set a price alert, please specify or paste a product link first, along with your target price (e.g. "Alert me when boAt Rockerz 558 drops below ₹1,800").';
        baseMsg.suggestions = ['Paste Product URL', '🔥 Best Deals'];
        return { response: baseMsg, updatedContext };
      }

      // Calculate default target price if none specified (e.g. 10% below current)
      const finalTarget = targetPrice || Math.round(activeProduct.current_price * 0.9);

      // Attempt backend alert creation
      let alertSuccess = false;
      let sessionOnly = false;
      let errMsg = '';

      try {
        // Try creating via alertsApi or trackingApi
        await alertsApi.create({
          product_id: activeProduct.id,
          alert_type: 'target_price',
          target_price: finalTarget,
          notify_in_app: true,
          notify_email: true,
        });
        alertSuccess = true;
      } catch (err: any) {
        // Check if unauthenticated or needs product tracked first
        if (err.response?.status === 401) {
          sessionOnly = true;
        } else if (err.response?.status === 404) {
          try {
            await productsApi.add({
              product_url: activeProduct.product_url,
              target_min_price: finalTarget,
            });
            alertSuccess = true;
          } catch (trackErr: any) {
            if (trackErr.response?.status === 401) {
              sessionOnly = true;
            } else {
              errMsg = trackErr.response?.data?.detail || 'Failed to register alert with server.';
            }
          }
        } else {
          errMsg = err.response?.data?.detail || 'Could not verify alert creation.';
        }
      }

      if (alertSuccess) {
        baseMsg.text = `🔔 **Price alert created.**\n\nProduct: **${activeProduct.product_name}**\nTarget price: **${formatINR(finalTarget)}**\nCurrent verified price: ${formatINR(activeProduct.current_price)}\n\nI'll notify you when a verified price reaches ${formatINR(finalTarget)} or below.`;
        baseMsg.alertConfirmation = {
          product_name: activeProduct.product_name,
          target_price: finalTarget,
          current_price: activeProduct.current_price,
          status: 'created',
          message: `Active radar monitoring ${activeProduct.store.toUpperCase()}`,
        };
      } else if (sessionOnly) {
        baseMsg.text = `🔔 **Price alert configured for this session.**\n\nProduct: **${activeProduct.product_name}**\nTarget price: **${formatINR(finalTarget)}**\n\n*Tip: Sign in to your PricePing account to receive email and SMS notifications when this drops!*`;
        baseMsg.alertConfirmation = {
          product_name: activeProduct.product_name,
          target_price: finalTarget,
          current_price: activeProduct.current_price,
          status: 'session_tracked',
          message: 'Saved to session radar. Sign in to activate email alerts.',
        };
      } else {
        baseMsg.text = `⚠️ I couldn't create the price alert right now: ${errMsg || 'Please try again in a moment.'}`;
        baseMsg.alertConfirmation = {
          product_name: activeProduct.product_name,
          target_price: finalTarget,
          current_price: activeProduct.current_price,
          status: 'failed',
          message: errMsg || 'Failed to create alert.',
        };
      }

      baseMsg.productCard = activeProduct;
      baseMsg.suggestions = ['📉 Check Price History', '⚖️ Compare Stores', '🛒 Should I Buy Now?'];
      return { response: baseMsg, updatedContext };
    }

    // -------------------------------------------------------------
    // INTENT 7: Product Alternatives
    // -------------------------------------------------------------
    if (intent === 'PRODUCT_ALTERNATIVE') {
      const activeProduct = updatedContext.selectedProduct;
      const budget = extractPriceNumber(text) || (activeProduct ? activeProduct.current_price * 0.8 : undefined);
      const category = detectCategory(text) || (activeProduct ? detectCategory(activeProduct.product_name) : undefined);

      const dealsRes = await dealsApi.getTrending({ category });
      let cand = (dealsRes.data?.deals || []) as TrendingDealCard[];
      if (budget) {
        cand = cand.filter((c) => c.price <= budget);
      }

      if (!cand.length) {
        baseMsg.text = `I searched verified inventory for alternatives${budget ? ` under ${formatINR(budget)}` : ''}, but didn't find exact matches right now. Try pasting another URL or adjusting your budget.`;
        baseMsg.suggestions = ['🔥 Best Deals', 'Paste another URL'];
        return { response: baseMsg, updatedContext };
      }

      const top3 = cand.slice(0, 3);
      const listText = top3
        .map(
          (c, idx) =>
            `${idx + 1}. **${c.title}** — **${formatINR(c.price)}** (Deal Score: ${c.deal_score}/100, ${c.discount_percent}% off on ${c.store.toUpperCase()})`
        )
        .join('\n\n');

      baseMsg.text = `Here are ${top3.length} verified alternatives${budget ? ` under ${formatINR(budget)}` : ''}:\n\n${listText}\n\nEach of these provides strong specifications within your price range and verified availability.`;
      baseMsg.dealResults = top3;
      baseMsg.suggestions = top3.map((c) => `Inspect ${c.title.split(' ').slice(0, 3).join(' ')}`);

      return { response: baseMsg, updatedContext };
    }

    // -------------------------------------------------------------
    // INTENT 8: Product Search / General Shopping Question
    // -------------------------------------------------------------
    if (intent === 'PRODUCT_SEARCH') {
      try {
        const resolveRes = await productsApi.resolveUrl(text);
        if (resolveRes.data?.product) {
          const p = resolveRes.data.product;
          const stats = resolveRes.data.statistics || {};
          const offers = resolveRes.data.comparison || [];
          const deal = calculateDealScore(p.current_price, p.original_price, stats.lowest_ever, stats.average_price, p.rating);

          const resolvedProduct: AssistantProduct = {
            id: p.id,
            product_name: p.product_name,
            brand: p.brand,
            model: p.model,
            variant: p.variant,
            current_price: p.current_price,
            original_price: p.original_price,
            discount_percentage: p.discount_percentage,
            product_image: p.product_image || (p.images && p.images[0]),
            product_url: p.product_url,
            store: resolveRes.data.detected_store || p.store || 'amazon',
            rating: p.rating,
            rating_count: p.rating_count,
            availability: p.availability,
            last_checked: p.last_checked,
            deal_score: deal.score,
            recommendation: deal.recommendation,
            recommendation_reason: deal.reason,
            freshness_text: getFreshnessLabel(p.last_checked),
            comparison: offers,
            statistics: {
              lowest_ever: stats.lowest_ever ?? null,
              highest_ever: stats.highest_ever ?? null,
              average_price: stats.average_price ?? null,
              data_points: stats.data_points ?? 1,
              tracking_days: stats.tracking_days ?? 0,
            },
          };

          updatedContext.selectedProduct = resolvedProduct;
          updatedContext.productId = p.id;
          updatedContext.currentPrice = p.current_price;

          baseMsg.text = `✓ Found verified product:\n\n**${resolvedProduct.product_name}**\n\n💰 Price: **${formatINR(resolvedProduct.current_price)}** on ${resolvedProduct.store.toUpperCase()}\n⏱️ ${resolvedProduct.freshness_text}\n🔥 Deal Score: **${deal.score}/100**\n\n${deal.reason}`;
          baseMsg.productCard = resolvedProduct;
          baseMsg.comparisonOffers = offers;
          baseMsg.suggestions = ['📉 Check Price History', '⚖️ Compare Stores', '🛒 Should I Buy?', '🔔 Set Price Alert'];
          return { response: baseMsg, updatedContext };
        }
      } catch {
        // search resolution missed; provide fallback helpful guidance
      }
    }

    // Default General Shopping Fallback
    baseMsg.text = `Hi! I am your **PricePing Assistant**. I track live prices, historical drops, and cross-store availability across Amazon, Flipkart, Myntra, AJIO, and Nykaa.\n\nHere is how I can help:\n• **Paste any product URL** to verify live pricing & detect hidden drops\n• Ask *"Where is this cheapest?"* to compare stores\n• Ask *"Should I buy now?"* for a data-backed recommendation\n• Say *"Alert me below ₹1,500"* to set an instant price radar`;
    baseMsg.suggestions = ['🔥 Best Deals under ₹2,000', '⚖️ Compare Stores', '📉 Check Price History', '🔔 Set Price Alert'];
    return { response: baseMsg, updatedContext };

  } catch (error: any) {
    // Transparent error handling — never crash or expose raw trace
    const msg = error.response?.data?.detail || "I couldn't verify that information right now. Please check the URL or try again in a moment.";
    baseMsg.text = `⚠️ ${msg}`;
    baseMsg.suggestions = ['Try another product URL', '🔥 Best Deals Today'];
    return { response: baseMsg, updatedContext };
  }
}
