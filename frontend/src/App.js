import { useState, useEffect, useCallback } from "react";
import "@/App.css";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Search, 
  MessageSquare, 
  Heart, 
  X, 
  Send, 
  Loader2,
  Cog,
  Zap,
  Car,
  Wind,
  Disc,
  Package,
  ChevronRight,
  Star,
  MapPin,
  ExternalLink,
  Filter,
  Trash2,
  Menu,
  Home,
  Users
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Toaster, toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Category icons mapping
const categoryIcons = {
  engine: Cog,
  brakes: Disc,
  suspension: Car,
  electrical: Zap,
  transmission: Cog,
  exhaust: Wind,
};

// Generate session ID for chat
const getSessionId = () => {
  let sessionId = localStorage.getItem("ezparts_session");
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem("ezparts_session", sessionId);
  }
  return sessionId;
};

// Navbar Component
const Navbar = ({ onNavigate, currentPage, favoritesCount }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <nav className="navbar-glass sticky top-0 z-50" data-testid="navbar">
      <div className="max-w-7xl mx-auto px-4 md:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <button 
            onClick={() => onNavigate("home")}
            className="flex items-center gap-3 group"
            data-testid="logo-btn"
          >
            <div className="w-10 h-10 bg-red-600 flex items-center justify-center">
              <Package className="w-6 h-6 text-white" />
            </div>
            <span className="font-heading text-xl tracking-tight">EzParts</span>
          </button>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-6">
            <button 
              onClick={() => onNavigate("home")}
              className={`text-sm font-medium transition-colors ${currentPage === "home" ? "text-red-500" : "text-zinc-400 hover:text-white"}`}
              data-testid="nav-home"
            >
              Home
            </button>
            <button 
              onClick={() => onNavigate("parts")}
              className={`text-sm font-medium transition-colors ${currentPage === "parts" ? "text-red-500" : "text-zinc-400 hover:text-white"}`}
              data-testid="nav-parts"
            >
              All Parts
            </button>
            <button 
              onClick={() => onNavigate("suppliers")}
              className={`text-sm font-medium transition-colors ${currentPage === "suppliers" ? "text-red-500" : "text-zinc-400 hover:text-white"}`}
              data-testid="nav-suppliers"
            >
              Suppliers
            </button>
            <button 
              onClick={() => onNavigate("favorites")}
              className="relative text-sm font-medium text-zinc-400 hover:text-white transition-colors flex items-center gap-1"
              data-testid="nav-favorites"
            >
              <Heart className="w-4 h-4" />
              Saved
              {favoritesCount > 0 && (
                <span className="absolute -top-2 -right-3 bg-red-600 text-white text-xs w-5 h-5 rounded-full flex items-center justify-center font-mono">
                  {favoritesCount}
                </span>
              )}
            </button>
          </div>

          {/* Mobile Menu */}
          <Sheet open={mobileMenuOpen} onOpenChange={setMobileMenuOpen}>
            <SheetTrigger asChild className="md:hidden">
              <Button variant="ghost" size="icon" data-testid="mobile-menu-btn">
                <Menu className="w-5 h-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="bg-zinc-900 border-zinc-800">
              <div className="flex flex-col gap-6 mt-8">
                <button 
                  onClick={() => { onNavigate("home"); setMobileMenuOpen(false); }}
                  className="flex items-center gap-3 text-lg font-medium"
                  data-testid="mobile-nav-home"
                >
                  <Home className="w-5 h-5" /> Home
                </button>
                <button 
                  onClick={() => { onNavigate("parts"); setMobileMenuOpen(false); }}
                  className="flex items-center gap-3 text-lg font-medium"
                  data-testid="mobile-nav-parts"
                >
                  <Package className="w-5 h-5" /> All Parts
                </button>
                <button 
                  onClick={() => { onNavigate("suppliers"); setMobileMenuOpen(false); }}
                  className="flex items-center gap-3 text-lg font-medium"
                  data-testid="mobile-nav-suppliers"
                >
                  <Users className="w-5 h-5" /> Suppliers
                </button>
                <button 
                  onClick={() => { onNavigate("favorites"); setMobileMenuOpen(false); }}
                  className="flex items-center gap-3 text-lg font-medium"
                  data-testid="mobile-nav-favorites"
                >
                  <Heart className="w-5 h-5" /> Saved ({favoritesCount})
                </button>
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </nav>
  );
};

// Part Card Component
const PartCard = ({ part, onFavorite, isFavorite, onClick }) => {
  const IconComponent = categoryIcons[part.category?.toLowerCase()] || Package;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-industrial bg-zinc-900 p-6 cursor-pointer group"
      onClick={onClick}
      data-testid={`part-card-${part.id}`}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-zinc-800 flex items-center justify-center">
            <IconComponent className="w-5 h-5 text-zinc-400 group-hover:text-red-500 transition-colors" />
          </div>
          <div>
            <Badge 
              className={`badge-industrial ${part.type === "OEM" ? "bg-blue-600/20 text-blue-400 border border-blue-600/30" : "bg-orange-600/20 text-orange-400 border border-orange-600/30"}`}
            >
              {part.type}
            </Badge>
          </div>
        </div>
        <button
          onClick={(e) => { e.stopPropagation(); onFavorite(part.id); }}
          className="p-2 hover:bg-zinc-800 rounded transition-colors"
          data-testid={`favorite-btn-${part.id}`}
        >
          <Heart className={`w-5 h-5 ${isFavorite ? "fill-red-500 text-red-500" : "text-zinc-500"}`} />
        </button>
      </div>

      {/* Content */}
      <h3 className="font-heading text-lg mb-2 group-hover:text-red-500 transition-colors line-clamp-2">
        {part.name}
      </h3>
      <p className="font-mono text-sm text-zinc-500 mb-3">{part.part_number}</p>
      <p className="text-sm text-zinc-400 mb-4 line-clamp-2">{part.description}</p>

      {/* Footer */}
      <div className="flex items-center justify-between pt-4 border-t border-zinc-800">
        <div>
          <p className="font-mono text-2xl font-bold text-white">${part.price.toFixed(2)}</p>
          <p className="text-xs text-zinc-500">{part.brand}</p>
        </div>
        <div className="text-right">
          <p className="text-xs text-zinc-500">{part.supplier}</p>
          <p className={`text-xs font-mono ${part.in_stock ? "text-green-500" : "text-red-500"}`}>
            {part.in_stock ? "IN STOCK" : "OUT OF STOCK"}
          </p>
        </div>
      </div>
    </motion.div>
  );
};

// Part Detail Modal
const PartDetail = ({ part, onClose, onFavorite, isFavorite }) => {
  if (!part) return null;
  const IconComponent = categoryIcons[part.category?.toLowerCase()] || Package;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4"
      onClick={onClose}
      data-testid="part-detail-modal"
    >
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        className="bg-zinc-900 border border-zinc-800 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-6 border-b border-zinc-800 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-zinc-800 flex items-center justify-center">
              <IconComponent className="w-6 h-6 text-red-500" />
            </div>
            <div>
              <Badge 
                className={`badge-industrial ${part.type === "OEM" ? "bg-blue-600/20 text-blue-400 border border-blue-600/30" : "bg-orange-600/20 text-orange-400 border border-orange-600/30"}`}
              >
                {part.type}
              </Badge>
              <p className="font-mono text-sm text-zinc-500 mt-1">{part.part_number}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-zinc-800 rounded" data-testid="close-detail-btn">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          <h2 className="font-heading text-2xl mb-4">{part.name}</h2>
          <p className="text-zinc-400 mb-6">{part.description}</p>

          {/* Price & Stock */}
          <div className="bg-zinc-800/50 p-4 mb-6 flex items-center justify-between">
            <div>
              <p className="text-sm text-zinc-500">Price</p>
              <p className="font-mono text-3xl font-bold">${part.price.toFixed(2)}</p>
            </div>
            <div className="text-right">
              <p className={`font-mono font-bold ${part.in_stock ? "text-green-500" : "text-red-500"}`}>
                {part.in_stock ? "IN STOCK" : "OUT OF STOCK"}
              </p>
              <p className="text-sm text-zinc-500">{part.brand}</p>
            </div>
          </div>

          {/* Specifications */}
          {part.specifications && Object.keys(part.specifications).length > 0 && (
            <div className="mb-6">
              <h3 className="font-heading text-sm text-zinc-500 mb-3">SPECIFICATIONS</h3>
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(part.specifications).map(([key, value]) => (
                  <div key={key} className="bg-zinc-800/30 p-3">
                    <p className="text-xs text-zinc-500 uppercase">{key.replace(/_/g, " ")}</p>
                    <p className="font-mono text-sm">{value}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Compatibility */}
          {part.compatibility && part.compatibility.length > 0 && (
            <div className="mb-6">
              <h3 className="font-heading text-sm text-zinc-500 mb-3">COMPATIBILITY</h3>
              <div className="flex flex-wrap gap-2">
                {part.compatibility.map((vehicle, idx) => (
                  <Badge key={idx} className="badge-industrial bg-zinc-800 text-zinc-300">
                    {vehicle}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Supplier */}
          <div className="bg-zinc-800/30 p-4 flex items-center justify-between">
            <div>
              <p className="text-sm text-zinc-500">Supplier</p>
              <p className="font-medium">{part.supplier}</p>
              <p className="text-xs text-zinc-500 flex items-center gap-1 mt-1">
                <MapPin className="w-3 h-3" /> {part.supplier_location}
              </p>
            </div>
            <Button
              onClick={() => onFavorite(part.id)}
              variant={isFavorite ? "default" : "outline"}
              className={`btn-industrial ${isFavorite ? "bg-red-600 hover:bg-red-700" : ""}`}
              data-testid="detail-favorite-btn"
            >
              <Heart className={`w-4 h-4 mr-2 ${isFavorite ? "fill-white" : ""}`} />
              {isFavorite ? "Saved" : "Save Part"}
            </Button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

// AI Chat Component
const AIChat = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(getSessionId);

  useEffect(() => {
    if (isOpen) {
      loadChatHistory();
    }
  }, [isOpen]);

  const loadChatHistory = async () => {
    try {
      const response = await axios.get(`${API}/chat/${sessionId}`);
      setMessages(response.data);
    } catch (error) {
      console.error("Error loading chat history:", error);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages(prev => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);

    try {
      const response = await axios.post(`${API}/chat`, {
        session_id: sessionId,
        message: userMessage
      });
      setMessages(prev => [...prev, { role: "assistant", content: response.data.response }]);
    } catch (error) {
      console.error("Chat error:", error);
      toast.error("Failed to get response. Please try again.");
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setLoading(false);
    }
  };

  const clearChat = async () => {
    try {
      await axios.delete(`${API}/chat/${sessionId}`);
      setMessages([]);
      toast.success("Chat history cleared");
    } catch (error) {
      console.error("Error clearing chat:", error);
    }
  };

  if (!isOpen) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 20, scale: 0.95 }}
      className="fixed bottom-36 right-4 md:bottom-24 md:right-52 w-[90vw] md:w-[400px] h-[500px] bg-zinc-900 border border-zinc-800 shadow-2xl flex flex-col z-[99]"
      data-testid="ai-chat-panel"
    >
      {/* Header */}
      <div className="p-4 border-b border-zinc-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-red-600 flex items-center justify-center">
            <MessageSquare className="w-4 h-4 text-white" />
          </div>
          <div>
            <h3 className="font-heading text-sm">EZPARTS ASSISTANT</h3>
            <p className="text-xs text-zinc-500">AI-powered parts advisor</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={clearChat} className="p-2 hover:bg-zinc-800 rounded" data-testid="clear-chat-btn">
            <Trash2 className="w-4 h-4 text-zinc-500" />
          </button>
          <button onClick={onClose} className="p-2 hover:bg-zinc-800 rounded" data-testid="close-chat-btn">
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 p-4 chat-container">
        {messages.length === 0 && (
          <div className="text-center py-8">
            <MessageSquare className="w-12 h-12 text-zinc-700 mx-auto mb-4" />
            <p className="text-zinc-500 text-sm">Ask me about parts, compatibility, or recommendations!</p>
            <div className="mt-4 flex flex-wrap gap-2 justify-center">
              {["Best brake pads for F-150?", "OEM vs Aftermarket?", "Find suspension parts"].map((q) => (
                <button
                  key={q}
                  onClick={() => setInput(q)}
                  className="text-xs bg-zinc-800 px-3 py-1.5 rounded hover:bg-zinc-700 transition-colors"
                  data-testid={`quick-question-${q.slice(0, 10)}`}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((msg, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`mb-4 ${msg.role === "user" ? "text-right" : ""}`}
          >
            <div
              className={`inline-block max-w-[85%] p-3 text-sm ${
                msg.role === "user"
                  ? "bg-red-600 text-white"
                  : "bg-zinc-800 text-zinc-200"
              }`}
            >
              {msg.content}
            </div>
          </motion.div>
        ))}
        {loading && (
          <div className="flex items-center gap-2 text-zinc-500">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span className="text-sm">Thinking...</span>
          </div>
        )}
      </ScrollArea>

      {/* Input */}
      <div className="p-4 border-t border-zinc-800">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Ask about parts..."
            className="input-industrial flex-1"
            data-testid="chat-input"
          />
          <Button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="btn-industrial bg-red-600 hover:bg-red-700 px-4"
            data-testid="send-message-btn"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </motion.div>
  );
};

// Home Page Component
const HomePage = ({ categories, onSearch, onCategoryClick }) => {
  const [searchQuery, setSearchQuery] = useState("");

  const handleSearch = () => {
    if (searchQuery.trim()) {
      onSearch(searchQuery);
    }
  };

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative py-20 md:py-32 px-4 md:px-8">
        <div className="absolute inset-0 overflow-hidden">
          <div 
            className="absolute inset-0 bg-cover bg-center opacity-20"
            style={{ backgroundImage: `url(https://images.unsplash.com/photo-1767339736147-676bd47eddb6?w=1920)` }}
          />
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-zinc-900/50 to-zinc-900" />
        </div>
        
        <div className="relative max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="font-heading text-4xl md:text-6xl lg:text-7xl mb-6">
              Find the <span className="text-red-500">Right Part</span>
              <br />Every Time
            </h1>
            <p className="text-lg md:text-xl text-zinc-400 mb-10 max-w-2xl mx-auto">
              Search thousands of OEM and Aftermarket parts from trusted US suppliers. 
              Get AI-powered recommendations tailored to your vehicle.
            </p>
          </motion.div>

          {/* Search Bar */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="flex flex-col md:flex-row gap-4 max-w-2xl mx-auto"
          >
            <div className="relative flex-1">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500" />
              <Input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                placeholder="Search by part name, number, or vehicle..."
                className="input-industrial w-full pl-12"
                data-testid="hero-search-input"
              />
            </div>
            <Button
              onClick={handleSearch}
              className="btn-industrial bg-red-600 hover:bg-red-700 md:w-auto"
              data-testid="hero-search-btn"
            >
              Search Parts
            </Button>
          </motion.div>
        </div>
      </section>

      {/* Categories Grid */}
      <section className="py-16 px-4 md:px-8 max-w-7xl mx-auto">
        <h2 className="font-heading text-2xl mb-8">BROWSE BY CATEGORY</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {categories.map((cat, idx) => {
            const IconComponent = categoryIcons[cat.id] || Package;
            return (
              <motion.button
                key={cat.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.1 }}
                onClick={() => onCategoryClick(cat.name)}
                className="card-industrial bg-zinc-900 p-6 text-left group"
                data-testid={`category-${cat.id}`}
              >
                <div className="w-12 h-12 bg-zinc-800 flex items-center justify-center mb-4 group-hover:bg-red-600/20 transition-colors">
                  <IconComponent className="w-6 h-6 text-zinc-400 group-hover:text-red-500 transition-colors" />
                </div>
                <h3 className="font-heading text-sm mb-1">{cat.name}</h3>
                <p className="font-mono text-xs text-zinc-500">{cat.count} parts</p>
              </motion.button>
            );
          })}
        </div>
      </section>

      {/* Features */}
      <section className="py-16 px-4 md:px-8 bg-zinc-900/50">
        <div className="max-w-7xl mx-auto grid md:grid-cols-3 gap-8">
          <div className="p-6">
            <div className="w-12 h-12 bg-red-600/20 flex items-center justify-center mb-4">
              <Package className="w-6 h-6 text-red-500" />
            </div>
            <h3 className="font-heading text-lg mb-2">OEM & AFTERMARKET</h3>
            <p className="text-zinc-400 text-sm">Find both factory-spec OEM parts and performance aftermarket upgrades in one place.</p>
          </div>
          <div className="p-6">
            <div className="w-12 h-12 bg-red-600/20 flex items-center justify-center mb-4">
              <MapPin className="w-6 h-6 text-red-500" />
            </div>
            <h3 className="font-heading text-lg mb-2">US SUPPLIERS</h3>
            <p className="text-zinc-400 text-sm">All parts sourced from trusted American suppliers with verified inventory.</p>
          </div>
          <div className="p-6">
            <div className="w-12 h-12 bg-red-600/20 flex items-center justify-center mb-4">
              <MessageSquare className="w-6 h-6 text-red-500" />
            </div>
            <h3 className="font-heading text-lg mb-2">AI ASSISTANT</h3>
            <p className="text-zinc-400 text-sm">Get instant recommendations and compatibility advice from our AI parts expert.</p>
          </div>
        </div>
      </section>
    </div>
  );
};

// Parts List Page
const PartsPage = ({ parts, loading, favorites, onFavorite, onPartClick, searchQuery, onSearch }) => {
  const [typeFilter, setTypeFilter] = useState("all");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [localSearch, setLocalSearch] = useState(searchQuery);

  const filteredParts = parts.filter(part => {
    if (typeFilter !== "all" && part.type !== typeFilter) return false;
    if (categoryFilter !== "all" && part.category.toLowerCase() !== categoryFilter) return false;
    return true;
  });

  const categories = [...new Set(parts.map(p => p.category))];

  return (
    <div className="min-h-screen py-8 px-4 md:px-8 max-w-7xl mx-auto">
      {/* Search & Filters */}
      <div className="mb-8">
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500" />
            <Input
              value={localSearch}
              onChange={(e) => setLocalSearch(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && onSearch(localSearch)}
              placeholder="Search parts..."
              className="input-industrial w-full pl-12"
              data-testid="parts-search-input"
            />
          </div>
          <Button
            onClick={() => onSearch(localSearch)}
            className="btn-industrial bg-red-600 hover:bg-red-700"
            data-testid="parts-search-btn"
          >
            Search
          </Button>
        </div>

        <div className="flex flex-wrap gap-4">
          <div className="flex bg-zinc-800/50 p-1 rounded-sm">
            <button
              onClick={() => setTypeFilter("all")}
              className={`px-4 py-2 font-mono text-xs rounded-sm transition-colors ${typeFilter === "all" ? "bg-red-600 text-white" : "text-zinc-400 hover:text-white"}`}
              data-testid="filter-all"
            >
              All
            </button>
            <button
              onClick={() => setTypeFilter("OEM")}
              className={`px-4 py-2 font-mono text-xs rounded-sm transition-colors ${typeFilter === "OEM" ? "bg-red-600 text-white" : "text-zinc-400 hover:text-white"}`}
              data-testid="filter-oem"
            >
              OEM
            </button>
            <button
              onClick={() => setTypeFilter("Aftermarket")}
              className={`px-4 py-2 font-mono text-xs rounded-sm transition-colors ${typeFilter === "Aftermarket" ? "bg-red-600 text-white" : "text-zinc-400 hover:text-white"}`}
              data-testid="filter-aftermarket"
            >
              Aftermarket
            </button>
          </div>

          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="input-industrial h-10 px-4 bg-zinc-800/50"
            data-testid="category-filter"
          >
            <option value="all">All Categories</option>
            {categories.map(cat => (
              <option key={cat} value={cat.toLowerCase()}>{cat}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Results */}
      <div className="mb-4 flex items-center justify-between">
        <p className="text-sm text-zinc-500">
          Showing <span className="text-white font-mono">{filteredParts.length}</span> parts
        </p>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1,2,3,4,5,6].map(i => (
            <div key={i} className="bg-zinc-900 p-6 animate-pulse">
              <div className="h-8 bg-zinc-800 rounded mb-4 w-1/3" />
              <div className="h-6 bg-zinc-800 rounded mb-2" />
              <div className="h-4 bg-zinc-800 rounded w-2/3" />
            </div>
          ))}
        </div>
      ) : filteredParts.length === 0 ? (
        <div className="text-center py-16">
          <Package className="w-16 h-16 text-zinc-700 mx-auto mb-4" />
          <p className="text-zinc-500">No parts found. Try adjusting your filters.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredParts.map(part => (
            <PartCard
              key={part.id}
              part={part}
              onFavorite={onFavorite}
              isFavorite={favorites.includes(part.id)}
              onClick={() => onPartClick(part)}
            />
          ))}
        </div>
      )}
    </div>
  );
};

// Suppliers Page
const SuppliersPage = ({ suppliers, loading }) => {
  return (
    <div className="min-h-screen py-8 px-4 md:px-8 max-w-7xl mx-auto">
      <h1 className="font-heading text-3xl mb-2">US SUPPLIERS</h1>
      <p className="text-zinc-400 mb-8">Trusted automotive parts suppliers across the United States</p>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[1,2,3,4].map(i => (
            <div key={i} className="bg-zinc-900 p-6 animate-pulse">
              <div className="h-6 bg-zinc-800 rounded mb-4 w-1/3" />
              <div className="h-4 bg-zinc-800 rounded mb-2 w-1/2" />
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {suppliers.map((supplier, idx) => (
            <motion.div
              key={supplier.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="card-industrial bg-zinc-900 p-6"
              data-testid={`supplier-card-${supplier.id}`}
            >
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="font-heading text-xl">{supplier.name}</h3>
                  <p className="text-sm text-zinc-500 flex items-center gap-1 mt-1">
                    <MapPin className="w-3 h-3" /> {supplier.location}, {supplier.state}
                  </p>
                </div>
                <div className="flex items-center gap-1 bg-zinc-800 px-2 py-1">
                  <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                  <span className="font-mono text-sm">{supplier.rating}</span>
                </div>
              </div>

              <div className="flex flex-wrap gap-2 mb-4">
                {supplier.specialties.map((spec, i) => (
                  <Badge key={i} className="badge-industrial bg-zinc-800 text-zinc-300">
                    {spec}
                  </Badge>
                ))}
              </div>

              <div className="pt-4 border-t border-zinc-800 flex items-center justify-between">
                <p className="font-mono text-sm text-zinc-400">{supplier.contact}</p>
                <a
                  href={`https://${supplier.website}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-red-500 hover:text-red-400 flex items-center gap-1 text-sm"
                >
                  Visit <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
};

// Favorites Page
const FavoritesPage = ({ favorites, loading, onRemove, onPartClick }) => {
  return (
    <div className="min-h-screen py-8 px-4 md:px-8 max-w-7xl mx-auto">
      <h1 className="font-heading text-3xl mb-2">SAVED PARTS</h1>
      <p className="text-zinc-400 mb-8">Your saved parts for quick access</p>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1,2,3].map(i => (
            <div key={i} className="bg-zinc-900 p-6 animate-pulse">
              <div className="h-6 bg-zinc-800 rounded mb-4 w-1/3" />
              <div className="h-4 bg-zinc-800 rounded mb-2" />
            </div>
          ))}
        </div>
      ) : favorites.length === 0 ? (
        <div className="text-center py-16">
          <Heart className="w-16 h-16 text-zinc-700 mx-auto mb-4" />
          <p className="text-zinc-500">No saved parts yet. Start browsing and save parts you like!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {favorites.map(({ favorite_id, part }) => (
            <PartCard
              key={favorite_id}
              part={part}
              onFavorite={onRemove}
              isFavorite={true}
              onClick={() => onPartClick(part)}
            />
          ))}
        </div>
      )}
    </div>
  );
};

// Main App Component
function App() {
  const [currentPage, setCurrentPage] = useState("home");
  const [parts, setParts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [favoriteIds, setFavoriteIds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedPart, setSelectedPart] = useState(null);
  const [chatOpen, setChatOpen] = useState(false);

  // Fetch initial data
  useEffect(() => {
    fetchCategories();
    fetchParts();
    fetchSuppliers();
    fetchFavorites();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API}/categories`);
      setCategories(response.data);
    } catch (error) {
      console.error("Error fetching categories:", error);
    }
  };

  const fetchParts = async (search = "", category = "") => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (search) params.append("search", search);
      if (category) params.append("category", category);
      
      const response = await axios.get(`${API}/parts?${params.toString()}`);
      setParts(response.data);
    } catch (error) {
      console.error("Error fetching parts:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSuppliers = async () => {
    try {
      const response = await axios.get(`${API}/suppliers`);
      setSuppliers(response.data);
    } catch (error) {
      console.error("Error fetching suppliers:", error);
    }
  };

  const fetchFavorites = async () => {
    try {
      const response = await axios.get(`${API}/favorites`);
      setFavorites(response.data);
      setFavoriteIds(response.data.map(f => f.part.id));
    } catch (error) {
      console.error("Error fetching favorites:", error);
    }
  };

  const handleSearch = (query) => {
    setSearchQuery(query);
    fetchParts(query);
    setCurrentPage("parts");
  };

  const handleCategoryClick = (category) => {
    setSearchQuery("");
    fetchParts("", category);
    setCurrentPage("parts");
  };

  const handleFavorite = async (partId) => {
    if (favoriteIds.includes(partId)) {
      // Remove from favorites
      try {
        await axios.delete(`${API}/favorites/${partId}`);
        setFavoriteIds(prev => prev.filter(id => id !== partId));
        setFavorites(prev => prev.filter(f => f.part.id !== partId));
        toast.success("Removed from saved parts");
      } catch (error) {
        console.error("Error removing favorite:", error);
        toast.error("Failed to remove from saved");
      }
    } else {
      // Add to favorites
      try {
        await axios.post(`${API}/favorites`, { part_id: partId });
        setFavoriteIds(prev => [...prev, partId]);
        fetchFavorites();
        toast.success("Added to saved parts");
      } catch (error) {
        console.error("Error adding favorite:", error);
        toast.error("Failed to save part");
      }
    }
  };

  const handleNavigate = (page) => {
    setCurrentPage(page);
    if (page === "parts") {
      fetchParts(searchQuery);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 grid-pattern">
      <Toaster position="top-right" richColors />
      
      <Navbar 
        onNavigate={handleNavigate} 
        currentPage={currentPage} 
        favoritesCount={favoriteIds.length}
      />

      {/* Page Content */}
      <AnimatePresence mode="wait">
        {currentPage === "home" && (
          <motion.div key="home" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <HomePage 
              categories={categories}
              onSearch={handleSearch}
              onCategoryClick={handleCategoryClick}
            />
          </motion.div>
        )}
        {currentPage === "parts" && (
          <motion.div key="parts" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <PartsPage 
              parts={parts}
              loading={loading}
              favorites={favoriteIds}
              onFavorite={handleFavorite}
              onPartClick={setSelectedPart}
              searchQuery={searchQuery}
              onSearch={handleSearch}
            />
          </motion.div>
        )}
        {currentPage === "suppliers" && (
          <motion.div key="suppliers" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <SuppliersPage suppliers={suppliers} loading={loading && suppliers.length === 0} />
          </motion.div>
        )}
        {currentPage === "favorites" && (
          <motion.div key="favorites" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <FavoritesPage 
              favorites={favorites}
              loading={loading && favorites.length === 0}
              onRemove={handleFavorite}
              onPartClick={setSelectedPart}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Part Detail Modal */}
      <AnimatePresence>
        {selectedPart && (
          <PartDetail 
            part={selectedPart}
            onClose={() => setSelectedPart(null)}
            onFavorite={handleFavorite}
            isFavorite={favoriteIds.includes(selectedPart.id)}
          />
        )}
      </AnimatePresence>

      {/* AI Chat */}
      <AnimatePresence>
        <AIChat isOpen={chatOpen} onClose={() => setChatOpen(false)} />
      </AnimatePresence>

      {/* Chat FAB */}
      <motion.button
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setChatOpen(!chatOpen)}
        className="fixed bottom-20 right-4 md:bottom-6 md:right-52 w-14 h-14 bg-red-600 hover:bg-red-700 flex items-center justify-center shadow-lg z-[100] glow-red"
        data-testid="chat-fab"
      >
        {chatOpen ? (
          <X className="w-6 h-6 text-white" />
        ) : (
          <MessageSquare className="w-6 h-6 text-white" />
        )}
      </motion.button>
    </div>
  );
}

export default App;
