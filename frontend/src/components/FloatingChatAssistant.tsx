import { useState } from 'react';
import {
  MessageSquare, X, Send, Bot, Loader2
} from 'lucide-react';

interface ChatMessage {
  id: string;
  sender: 'bot' | 'user';
  text: string;
  time: string;
  suggestions?: string[];
}

export default function FloatingChatAssistant() {
  const [isOpen, setIsOpen] = useState(false);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      sender: 'bot',
      text: 'Hi there! 👋 I am your PricePing Smart Shopping Assistant. Paste any Amazon / Flipkart product URL or ask me when is the best time to buy!',
      time: 'Just now',
      suggestions: [
        'Is iPhone 16 at all-time low?',
        'Best deals under ₹2,000',
        'Check Flipkart Big Billion dates',
        'How do price drop alerts work?',
      ],
    },
  ]);

  const handleSendMessage = (textToSend?: string) => {
    const query = (textToSend || inputText).trim();
    if (!query) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      text: query,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText('');
    setIsTyping(true);

    setTimeout(() => {
      let reply = '';
      let suggestions: string[] = [];

      const lower = query.toLowerCase();
      if (lower.includes('iphone') || lower.includes('apple')) {
        reply = '📱 iPhone 16 is currently ₹72,499 (down from ₹79,900). PricePing prediction shows this is within 4% of its lowest price. If you use ICICI card, you get an extra ₹4,000 instant discount!';
        suggestions = ['Track iPhone 16 Price', 'Compare with iPhone 15', 'Check Flipkart Price'];
      } else if (lower.includes('boat') || lower.includes('headphone') || lower.includes('sony')) {
        reply = '🎧 boAt Rockerz 550 is at ₹1,499 (70% OFF) and Sony WH-1000XM5 is at ₹26,990 (All-time low). Set a price alert so we ping you if they drop further!';
        suggestions = ['Set Alert on Sony XM5', 'View Bluetooth Earbuds Deals'];
      } else if (lower.includes('how') || lower.includes('alert') || lower.includes('work')) {
        reply = '🔔 PricePing monitors products every 60 seconds across Amazon, Flipkart, AJIO, Myntra & Nykaa. When the price drops below your target, you receive an instant in-app ping and email alert with zero spam!';
        suggestions = ['Paste a Product URL', 'View My Active Alerts'];
      } else if (lower.includes('http') || lower.includes('.com') || lower.includes('.in')) {
        reply = '🔗 Great product link! Our background worker is checking live buybox pricing and variant availability for you. Would you like to set a 10% price drop alert?';
        suggestions = ['Yes, Alert at 10% Drop', 'Check Price History'];
      } else {
        reply = `💡 Thanks for asking! I found 3 active price drop deals related to "${query}". We also have exclusive cashback coupons available today!`;
        suggestions = ['Show Top 5 Deals', 'Open Spend Lens'];
      }

      const botMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'bot',
        text: reply,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        suggestions,
      };

      setMessages((prev) => [...prev, botMsg]);
      setIsTyping(false);
    }, 750);
  };

  return (
    <>
      {/* Floating Chat Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-40 w-14 h-14 rounded-full bg-gradient-to-tr from-blue-600 via-indigo-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white flex items-center justify-center shadow-2xl shadow-indigo-600/50 hover:scale-110 active:scale-95 transition-all duration-300 group cursor-pointer"
        title="PricePing AI Shopping Assistant"
      >
        {isOpen ? (
          <X className="w-6 h-6" />
        ) : (
          <div className="relative flex items-center justify-center">
            <MessageSquare className="w-6 h-6" />
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-amber-400 rounded-full border-2 border-white animate-ping" />
          </div>
        )}
      </button>

      {/* Interactive Chat Window */}
      {isOpen && (
        <div className="fixed bottom-24 right-4 sm:right-6 z-50 w-[92vw] sm:w-96 bg-[#121626] border border-white/15 rounded-3xl shadow-2xl shadow-black/80 flex flex-col overflow-hidden animate-slide-in max-h-[550px] h-[520px]">
          {/* Chat Header */}
          <div className="p-4 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-700 text-white flex items-center justify-between shadow-md">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-white/20 backdrop-blur-md flex items-center justify-center text-white font-black text-sm">
                <Bot className="w-5 h-5" />
              </div>
              <div>
                <div className="font-extrabold text-sm flex items-center gap-1.5">
                  PricePing Assistant
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                </div>
                <div className="text-[11px] text-blue-100 font-medium">Live Deal & Price Drop Radar</div>
              </div>
            </div>

            <button
              onClick={() => setIsOpen(false)}
              className="p-1 rounded-full hover:bg-white/20 text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Messages Area */}
          <div className="flex-1 p-4 overflow-y-auto space-y-3.5 bg-black/30">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
              >
                <div
                  className={`p-3.5 rounded-2xl text-xs max-w-[85%] leading-relaxed ${
                    msg.sender === 'user'
                      ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-br-none shadow-md'
                      : 'bg-white/[0.08] text-gray-200 border border-white/10 rounded-bl-none shadow-sm'
                  }`}
                >
                  {msg.text}
                </div>
                <span className="text-[10px] text-gray-500 mt-1 px-1">{msg.time}</span>

                {/* Suggestions Pills */}
                {msg.suggestions && msg.suggestions.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-2 max-w-[90%]">
                    {msg.suggestions.map((sug, i) => (
                      <button
                        key={i}
                        onClick={() => handleSendMessage(sug)}
                        className="px-2.5 py-1 rounded-full bg-indigo-500/15 hover:bg-indigo-500/30 text-indigo-300 border border-indigo-500/30 text-[11px] font-bold text-left transition-colors cursor-pointer"
                      >
                        {sug}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {isTyping && (
              <div className="flex items-center gap-2 p-3 rounded-2xl bg-white/[0.05] text-gray-400 text-xs w-fit border border-white/10">
                <Loader2 className="w-3.5 h-3.5 animate-spin text-indigo-400" />
                <span>Checking price trends & coupons...</span>
              </div>
            )}
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
              placeholder="Ask anything or paste product URL..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              className="flex-1 bg-white/[0.06] border border-white/10 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500"
            />
            <button
              type="submit"
              className="p-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-md transition-all hover:scale-105 active:scale-95 cursor-pointer"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      )}
    </>
  );
}
