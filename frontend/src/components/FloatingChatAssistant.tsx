import { useState, useRef, useEffect } from 'react';
import {
  X,
  Send,
  Bot,
  Loader2,
  ExternalLink,
  Bell,
  BarChart2,
  Sparkles,
  ShoppingBag,
  ArrowUpDown,
  Clock,
  Maximize2,
  Minimize2,
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
} from 'recharts';
import {
  processAssistantQuery,
  formatINR,
  type AssistantMessage,
  type AssistantSessionContext,
  type AssistantProduct,
  type VerifiedStoreOffer,
  type TrendingDealCard,
} from '../services/assistantEngine';

export default function FloatingChatAssistant() {
  const [isOpen, setIsOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  // Conversational Memory / Context
  const [sessionContext, setSessionContext] = useState<AssistantSessionContext>({});

  // Messages list with official welcome message
  const [messages, setMessages] = useState<AssistantMessage[]>([
    {
      id: 'welcome-1',
      sender: 'bot',
      text: "Hi there! 👋 I am your PricePing Smart Shopping Assistant. Paste any supported product URL or ask me when it's the best time to buy!",
      time: 'Just now',
      suggestions: [
        '🔎 Find Best Price',
        '📉 Check Price History',
        '⚖️ Compare Stores',
        '🔥 Best Deals under ₹2,000',
        '🔔 Set Price Alert',
        '🛒 Should I Buy Now?',
      ],
    },
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll on new messages
  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isTyping, isOpen]);

  const handleSendMessage = async (textToSend?: string) => {
    const query = (textToSend || inputText).trim();
    if (!query || isTyping) return;

    const userMsg: AssistantMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: query,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText('');
    setIsTyping(true);

    try {
      const { response: botMsg, updatedContext } = await processAssistantQuery(query, sessionContext);
      setSessionContext(updatedContext);
      setMessages((prev) => [...prev, botMsg]);
    } catch {
      const fallbackMsg: AssistantMessage = {
        id: `err-${Date.now()}`,
        sender: 'bot',
        text: "⚠️ I couldn't process that right now. Please verify the link or try again in a moment.",
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        suggestions: ['🔥 Best Deals under ₹2,000', 'Paste another URL'],
      };
      setMessages((prev) => [...prev, fallbackMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  // Dynamic quick action chips based on context
  const getContextualQuickActions = () => {
    if (sessionContext.selectedProduct) {
      return [
        { label: '📉 Price History', query: 'Show price history' },
        { label: '⚖️ Compare Prices', query: 'Compare stores for this' },
        { label: '🛒 Should I Buy?', query: 'Should I buy now or wait?' },
        {
          label: `🔔 Set Alert below ${formatINR(Math.round(sessionContext.selectedProduct.current_price * 0.9))}`,
          query: `Alert me when this goes below ${formatINR(Math.round(sessionContext.selectedProduct.current_price * 0.9))}`,
        },
        { label: '🔥 Cheaper Alternatives', query: 'Show cheaper alternatives' },
      ];
    }
    return [
      { label: '🔎 Find Best Price', query: 'Where is boAt Rockerz 558 cheapest?' },
      { label: '📉 Check Price History', query: 'Show price history for boAt headphones' },
      { label: '⚖️ Compare Stores', query: 'Compare prices across Amazon and Flipkart' },
      { label: '🔥 Best Deals under ₹2,000', query: 'Best deals under ₹2,000' },
      { label: '🔔 Set Price Alert', query: 'How do I set a price drop alert?' },
      { label: '🛒 Should I Buy Now?', query: 'Is iPhone 16 a good deal right now?' },
    ];
  };

  return (
    <>
      {/* Floating Chat Launcher Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-20 right-4 sm:bottom-6 sm:right-6 z-40 w-12 h-12 sm:w-14 sm:h-14 rounded-full bg-gradient-to-tr from-blue-600 via-indigo-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white flex items-center justify-center shadow-2xl shadow-indigo-600/50 hover:scale-110 active:scale-95 transition-all duration-300 group cursor-pointer"
        title="PricePing Assistant – Live Deal & Price Drop Radar"
        id="priceping-assistant-toggle-btn"
      >
        {isOpen ? (
          <X className="w-5 h-5 sm:w-6 sm:h-6" />
        ) : (
          <div className="relative flex items-center justify-center">
            <Bot className="w-5 h-5 sm:w-6 sm:h-6" />
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-400 rounded-full border-2 border-[#121626] animate-pulse" />
          </div>
        )}
      </button>

      {/* Main Assistant Modal / Flyout */}
      {isOpen && (
        <div
          className={`fixed z-50 bg-[#0f1322] border border-indigo-500/20 rounded-3xl shadow-2xl shadow-black/80 flex flex-col overflow-hidden transition-all duration-300 animate-slide-in ${
            isExpanded
              ? 'bottom-20 sm:bottom-4 right-2 sm:right-6 w-[95vw] sm:w-[540px] h-[75vh] sm:h-[85vh] max-h-[760px]'
              : 'bottom-20 sm:bottom-24 right-2 sm:right-6 w-[95vw] sm:w-[420px] h-[520px] sm:h-[580px] max-h-[620px]'
          }`}
          id="priceping-assistant-container"
        >
          {/* Header */}
          <div className="px-4 py-3.5 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-700 text-white flex items-center justify-between shadow-md border-b border-white/10 select-none">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-full bg-white/20 backdrop-blur-md flex items-center justify-center text-white font-black shadow-inner">
                <Bot className="w-5 h-5" />
              </div>
              <div>
                <div className="font-extrabold text-sm flex items-center gap-1.5 tracking-tight">
                  PricePing Assistant
                  <span className="flex items-center gap-1 text-[10px] font-bold bg-emerald-500/30 text-emerald-200 px-1.5 py-0.5 rounded-full border border-emerald-400/30">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                    LIVE
                  </span>
                </div>
                <div className="text-[11px] text-blue-100 font-medium">
                  Live Deal &amp; Price Drop Radar
                </div>
              </div>
            </div>

            <div className="flex items-center gap-1">
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="p-1.5 rounded-lg hover:bg-white/15 text-white/80 hover:text-white transition-colors cursor-pointer"
                title={isExpanded ? 'Collapse' : 'Expand'}
              >
                {isExpanded ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 rounded-lg hover:bg-white/15 text-white/80 hover:text-white transition-colors cursor-pointer"
                title="Close Assistant"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Active Product Radar Header Strip (When a product is detected in context) */}
          {sessionContext.selectedProduct && (
            <div className="px-3 py-1.5 bg-indigo-950/70 border-b border-indigo-500/20 flex items-center justify-between text-[11px] text-indigo-200">
              <div className="flex items-center gap-1.5 truncate max-w-[75%]">
                <span className="w-2 h-2 rounded-full bg-emerald-400" />
                <span className="font-medium text-gray-400">Context:</span>
                <span className="font-bold text-white truncate">
                  {sessionContext.selectedProduct.product_name}
                </span>
              </div>
              <div className="font-extrabold text-emerald-400 shrink-0">
                {formatINR(sessionContext.selectedProduct.current_price)}
              </div>
            </div>
          )}

          {/* Messages Scroll Area */}
          <div className="flex-1 p-3.5 sm:p-4 overflow-y-auto space-y-4 bg-[#0a0d18] scrollbar-thin scrollbar-thumb-white/10">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
              >
                {/* Text Bubble */}
                <div
                  className={`p-3.5 rounded-2xl text-xs leading-relaxed max-w-[90%] shadow-sm ${
                    msg.sender === 'user'
                      ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-br-none shadow-indigo-600/30 font-medium'
                      : 'bg-[#15192c] text-gray-200 border border-white/10 rounded-bl-none'
                  }`}
                >
                  <div className="whitespace-pre-wrap font-sans text-[12px]">{msg.text}</div>

                  {/* 1. Compact Product Radar Card */}
                  {msg.productCard && (
                    <ProductRadarCard
                      product={msg.productCard}
                      onCompare={() => handleSendMessage('Compare stores for this product')}
                      onHistory={() => handleSendMessage('Show price history')}
                      onAlert={() =>
                        handleSendMessage(
                          `Alert me when this goes below ${formatINR(Math.round(msg.productCard!.current_price * 0.9))}`
                        )
                      }
                    />
                  )}

                  {/* 2. Store Comparison Offer List */}
                  {msg.comparisonOffers && msg.comparisonOffers.length > 0 && (
                    <ComparisonListCard offers={msg.comparisonOffers} />
                  )}

                  {/* 3. Mini Price History Chart */}
                  {msg.historyPoints && msg.historyPoints.length > 0 && (
                    <MiniHistoryChart points={msg.historyPoints} stats={msg.statistics} />
                  )}

                  {/* 4. Trending Deal Discovery Cards */}
                  {msg.dealResults && msg.dealResults.length > 0 && (
                    <div className="mt-3 space-y-2">
                      <div className="text-[11px] font-bold text-amber-300 flex items-center gap-1">
                        <Sparkles className="w-3.5 h-3.5" />
                        Verified Deals
                      </div>
                      {msg.dealResults.map((deal) => (
                        <DealItemCard
                          key={deal.id}
                          deal={deal}
                          onInspect={() => handleSendMessage(`Inspect ${deal.title}`)}
                        />
                      ))}
                    </div>
                  )}

                  {/* 5. Alert Confirmation Pill */}
                  {msg.alertConfirmation && (
                    <div
                      className={`mt-2.5 p-2.5 rounded-xl text-[11px] flex items-center gap-2 border ${
                        msg.alertConfirmation.status === 'created'
                          ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-200'
                          : msg.alertConfirmation.status === 'session_tracked'
                          ? 'bg-amber-500/10 border-amber-500/30 text-amber-200'
                          : 'bg-rose-500/10 border-rose-500/30 text-rose-200'
                      }`}
                    >
                      <Bell className="w-4 h-4 shrink-0 text-amber-400 animate-bounce" />
                      <div className="flex-1 leading-tight">
                        <div className="font-bold">
                          {msg.alertConfirmation.status === 'created'
                            ? '🔔 Live Radar Activated'
                            : msg.alertConfirmation.status === 'session_tracked'
                            ? '🔔 Session Radar Configured'
                            : '⚠️ Radar Alert Notice'}
                        </div>
                        <div className="text-[10px] opacity-85 mt-0.5">
                          {msg.alertConfirmation.message}
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                <span className="text-[10px] text-gray-500 mt-1 px-1">{msg.time}</span>

                {/* Suggestions / Follow-up Action Chips */}
                {msg.suggestions && msg.suggestions.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-2 max-w-[95%]">
                    {msg.suggestions.map((sug, i) => (
                      <button
                        key={i}
                        onClick={() => handleSendMessage(sug)}
                        className="px-2.5 py-1 rounded-full bg-indigo-500/15 hover:bg-indigo-500/30 text-indigo-300 border border-indigo-500/30 text-[11px] font-bold text-left transition-all hover:scale-102 active:scale-98 cursor-pointer flex items-center gap-1"
                      >
                        {sug}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {/* Typing / Querying Backend Indicator */}
            {isTyping && (
              <div className="flex items-center gap-2 p-3 rounded-2xl bg-[#15192c] text-indigo-300 text-xs w-fit border border-indigo-500/20 shadow-md">
                <Loader2 className="w-3.5 h-3.5 animate-spin text-indigo-400" />
                <span className="font-medium">Connecting to live stores &amp; verified history...</span>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Dynamic Quick Actions Bar */}
          <div className="px-3 py-2 bg-[#0c0f1b] border-t border-white/10 flex items-center gap-1.5 overflow-x-auto scrollbar-none">
            {getContextualQuickActions().map((action, i) => (
              <button
                key={i}
                onClick={() => handleSendMessage(action.query)}
                className="shrink-0 px-2.5 py-1 rounded-lg bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white border border-white/10 text-[10px] font-semibold transition-colors cursor-pointer whitespace-nowrap"
              >
                {action.label}
              </button>
            ))}
          </div>

          {/* Input Box */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="p-3 bg-[#0d101d] border-t border-white/10 flex items-center gap-2"
          >
            <input
              type="text"
              placeholder="Paste product URL or ask: 'Where is this cheapest?'"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              disabled={isTyping}
              className="flex-1 bg-white/[0.06] border border-white/10 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500 transition-colors"
            />
            <button
              type="submit"
              disabled={isTyping || !inputText.trim()}
              className="p-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 text-white shadow-md transition-all hover:scale-105 active:scale-95 cursor-pointer shrink-0"
              title="Send to PricePing Assistant"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      )}
    </>
  );
}

// ======================================================================
// COMPONENT: Product Radar Card (Section 19)
// ======================================================================
function ProductRadarCard({
  product,
  onCompare,
  onHistory,
  onAlert,
}: {
  product: AssistantProduct;
  onCompare: () => void;
  onHistory: () => void;
  onAlert: () => void;
}) {
  const storeBadgeColor =
    product.store.toLowerCase() === 'amazon'
      ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
      : product.store.toLowerCase() === 'flipkart'
      ? 'bg-blue-500/20 text-blue-300 border-blue-500/40'
      : product.store.toLowerCase() === 'myntra'
      ? 'bg-pink-500/20 text-pink-300 border-pink-500/40'
      : product.store.toLowerCase() === 'ajio'
      ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
      : 'bg-purple-500/20 text-purple-300 border-purple-500/40';

  const recBadgeColor =
    product.recommendation === 'BUY'
      ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
      : product.recommendation === 'WAIT'
      ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
      : 'bg-rose-500/20 text-rose-300 border-rose-500/40';

  return (
    <div className="mt-3 p-3 rounded-2xl bg-[#0c1020] border border-indigo-500/30 shadow-lg text-white">
      <div className="flex gap-3">
        {/* Product Image */}
        <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-xl bg-white/5 border border-white/10 overflow-hidden shrink-0 flex items-center justify-center p-1">
          {product.product_image ? (
            <img
              src={product.product_image}
              alt={product.product_name}
              className="w-full h-full object-contain"
              onError={(e) => {
                (e.target as HTMLElement).style.display = 'none';
              }}
            />
          ) : (
            <ShoppingBag className="w-8 h-8 text-gray-500" />
          )}
        </div>

        {/* Info & Metrics */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5 flex-wrap">
            <span
              className={`px-2 py-0.5 rounded-md text-[10px] font-extrabold uppercase border ${storeBadgeColor}`}
            >
              {product.store}
            </span>
            {product.recommendation && (
              <span
                className={`px-2 py-0.5 rounded-md text-[10px] font-bold border ${recBadgeColor}`}
              >
                {product.recommendation === 'BUY'
                  ? '🟢 BUY NOW'
                  : product.recommendation === 'WAIT'
                  ? '🟡 WAIT'
                  : '🔴 AVOID'}
              </span>
            )}
            {product.deal_score !== undefined && (
              <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30">
                Score: {product.deal_score}/100 🔥
              </span>
            )}
          </div>

          <h4 className="text-xs font-bold text-white mt-1 line-clamp-2 leading-snug">
            {product.product_name}
          </h4>

          {/* Pricing & Verification */}
          <div className="flex items-baseline gap-2 mt-1.5 flex-wrap">
            <span className="text-sm sm:text-base font-black text-emerald-400">
              {formatINR(product.current_price)}
            </span>
            {product.original_price && product.original_price > product.current_price && (
              <span className="text-[10px] text-gray-500 line-through">
                {formatINR(product.original_price)}
              </span>
            )}
            {product.discount_percentage && product.discount_percentage > 0 && (
              <span className="text-[10px] font-extrabold text-emerald-400 bg-emerald-500/15 px-1.5 py-0.2 rounded">
                -{product.discount_percentage}%
              </span>
            )}
          </div>

          <div className="text-[10px] text-gray-400 flex items-center gap-1 mt-0.5">
            <Clock className="w-3 h-3 text-indigo-400" />
            <span>{product.freshness_text}</span>
          </div>
        </div>
      </div>

      {/* Action Buttons Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-1.5 mt-3 pt-2.5 border-t border-white/10 text-[11px]">
        <button
          onClick={onCompare}
          className="flex items-center justify-center gap-1 px-2 py-1.5 rounded-xl bg-white/5 hover:bg-indigo-600/30 text-gray-200 hover:text-white border border-white/10 transition-colors cursor-pointer"
          title="Compare cross-store prices"
        >
          <ArrowUpDown className="w-3.5 h-3.5 text-indigo-400" />
          <span>Compare</span>
        </button>
        <button
          onClick={onHistory}
          className="flex items-center justify-center gap-1 px-2 py-1.5 rounded-xl bg-white/5 hover:bg-indigo-600/30 text-gray-200 hover:text-white border border-white/10 transition-colors cursor-pointer"
          title="Inspect verified price history"
        >
          <BarChart2 className="w-3.5 h-3.5 text-cyan-400" />
          <span>History</span>
        </button>
        <button
          onClick={onAlert}
          className="flex items-center justify-center gap-1 px-2 py-1.5 rounded-xl bg-white/5 hover:bg-indigo-600/30 text-gray-200 hover:text-white border border-white/10 transition-colors cursor-pointer"
          title="Set price drop alert"
        >
          <Bell className="w-3.5 h-3.5 text-amber-400" />
          <span>Alert</span>
        </button>
        <a
          href={product.product_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-center gap-1 px-2 py-1.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold transition-all cursor-pointer"
          title="Open product on store"
        >
          <span>Store</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </a>
      </div>
    </div>
  );
}

// ======================================================================
// COMPONENT: Comparison List (Section 5)
// ======================================================================
function ComparisonListCard({ offers }: { offers: VerifiedStoreOffer[] }) {
  const verifiedOffers = offers.filter(
    (o) => o.price !== null && o.price !== undefined && o.is_verified_match
  );
  verifiedOffers.sort((a, b) => (a.price || 0) - (b.price || 0));

  if (!verifiedOffers.length) return null;

  return (
    <div className="mt-3 p-3 rounded-2xl bg-[#0c1020] border border-white/10 text-white">
      <div className="text-[11px] font-bold text-gray-300 flex items-center justify-between mb-2">
        <span className="flex items-center gap-1">
          <ArrowUpDown className="w-3.5 h-3.5 text-indigo-400" />
          Verified Store Comparison
        </span>
        <span className="text-[10px] text-emerald-400 font-extrabold">
          {verifiedOffers.length} Stores Verified
        </span>
      </div>

      <div className="space-y-1.5">
        {verifiedOffers.map((offer, index) => {
          const isBest = index === 0;
          return (
            <div
              key={offer.store}
              className={`p-2 rounded-xl flex items-center justify-between text-xs border ${
                isBest
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-white'
                  : 'bg-white/5 border-white/5 text-gray-300'
              }`}
            >
              <div className="flex items-center gap-2">
                <span className="font-extrabold uppercase text-[11px] tracking-wide">
                  {offer.store}
                </span>
                {isBest && (
                  <span className="text-[10px] font-black bg-emerald-500 text-black px-1.5 py-0.2 rounded-full flex items-center gap-0.5">
                    🏆 BEST
                  </span>
                )}
              </div>

              <div className="flex items-center gap-2">
                <span className={`font-extrabold ${isBest ? 'text-emerald-400' : 'text-white'}`}>
                  {formatINR(offer.price)}
                </span>
                {offer.url && (
                  <a
                    href={offer.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-1 rounded-md hover:bg-white/20 text-gray-400 hover:text-white transition-colors cursor-pointer"
                    title={`Buy on ${offer.store}`}
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ======================================================================
// COMPONENT: Mini Price History Chart (Section 20)
// ======================================================================
function MiniHistoryChart({
  points,
  stats,
}: {
  points: { date: string; price: number }[];
  stats?: { lowest_ever: number | null; average_price: number | null; highest_ever: number | null };
}) {
  if (!points || points.length === 0) return null;

  const chartData = points.map((p) => ({
    time: new Date(p.date).toLocaleDateString([], { month: 'short', day: 'numeric' }),
    price: p.price,
  }));

  return (
    <div className="mt-3 p-3 rounded-2xl bg-[#0c1020] border border-cyan-500/30 text-white">
      <div className="flex items-center justify-between mb-2">
        <span className="text-[11px] font-bold text-cyan-300 flex items-center gap-1">
          <BarChart2 className="w-3.5 h-3.5" />
          Verified Price Curve
        </span>
        {stats?.lowest_ever && (
          <span className="text-[10px] text-emerald-400 font-bold">
            All-Time Low: {formatINR(stats.lowest_ever)}
          </span>
        )}
      </div>

      {/* Chart Box */}
      <div className="h-28 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.5} />
                <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <XAxis dataKey="time" stroke="#475569" fontSize={9} tickLine={false} />
            <YAxis
              stroke="#475569"
              fontSize={9}
              tickLine={false}
              domain={['dataMin - 100', 'dataMax + 100']}
              tickFormatter={(v) => `₹${v}`}
            />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  return (
                    <div className="p-1.5 rounded-lg bg-[#1e293b] border border-cyan-500/40 text-[10px] text-white shadow-md">
                      <div className="font-bold text-cyan-400">
                        {formatINR(payload[0].value as number)}
                      </div>
                      <div className="text-gray-400">{payload[0].payload.time}</div>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Area
              type="monotone"
              dataKey="price"
              stroke="#06b6d4"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#priceGradient)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Stats Summary Strip */}
      {stats && (
        <div className="grid grid-cols-3 gap-1 mt-2 pt-2 border-t border-white/10 text-center text-[10px]">
          <div>
            <div className="text-gray-400">Low</div>
            <div className="font-bold text-emerald-400">{formatINR(stats.lowest_ever)}</div>
          </div>
          <div>
            <div className="text-gray-400">Average</div>
            <div className="font-bold text-amber-400">{formatINR(stats.average_price)}</div>
          </div>
          <div>
            <div className="text-gray-400">High</div>
            <div className="font-bold text-rose-400">{formatINR(stats.highest_ever)}</div>
          </div>
        </div>
      )}
    </div>
  );
}

// ======================================================================
// COMPONENT: Deal Item Card (Section 8)
// ======================================================================
function DealItemCard({
  deal,
  onInspect,
}: {
  deal: TrendingDealCard;
  onInspect: () => void;
}) {
  return (
    <div className="p-2.5 rounded-xl bg-white/5 hover:bg-white/[0.08] border border-white/10 flex items-center justify-between gap-2.5 transition-colors">
      <div className="w-12 h-12 rounded-lg bg-white/5 border border-white/10 overflow-hidden shrink-0 flex items-center justify-center p-0.5">
        <img
          src={deal.image_url}
          alt={deal.title}
          className="w-full h-full object-contain"
          onError={(e) => {
            (e.target as HTMLElement).style.display = 'none';
          }}
        />
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1">
          <span className="text-[9px] font-black uppercase text-amber-400">
            {deal.store}
          </span>
          <span className="text-[9px] text-gray-500">•</span>
          <span className="text-[9px] text-emerald-400 font-bold">
            Score: {deal.deal_score}/100 🔥
          </span>
        </div>
        <h5 className="text-[11px] font-bold text-white truncate">{deal.title}</h5>
        <div className="flex items-baseline gap-1.5">
          <span className="text-xs font-black text-emerald-400">{formatINR(deal.price)}</span>
          <span className="text-[9px] text-gray-500 line-through">{formatINR(deal.mrp)}</span>
          <span className="text-[9px] font-bold text-emerald-400">-{deal.discount_percent}%</span>
        </div>
      </div>

      <div className="flex flex-col gap-1 shrink-0">
        <button
          onClick={onInspect}
          className="px-2 py-1 rounded-lg bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-300 border border-indigo-500/30 text-[10px] font-bold transition-colors cursor-pointer"
        >
          Inspect
        </button>
        <a
          href={deal.product_url}
          target="_blank"
          rel="noopener noreferrer"
          className="p-1 rounded-lg bg-white/5 hover:bg-white/15 text-gray-400 hover:text-white text-center transition-colors cursor-pointer"
          title="Direct Buy Link"
        >
          <ExternalLink className="w-3.5 h-3.5 mx-auto" />
        </a>
      </div>
    </div>
  );
}
