import { useState, useEffect, useRef } from "react";
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
  Star,
  MapPin,
  ExternalLink,
  Trash2,
  Menu,
  Home,
  Users,
  Mic,
  MicOff,
  Wrench,
  Gauge,
  ArrowLeftRight,
  Clock,
  Shield,
  TrendingUp,
  Plus,
  ChevronRight,
  AlertTriangle,
  CheckCircle,
  Truck,
  DollarSign,
  Layers,
  Eye
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Toaster, toast } from "sonner";
import { EquipmentDiagram, ModelViewer3D, PartIdentificationWizard, ExplodedViewDiagram } from "@/components/PartsDiagram";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Category icons mapping for heavy equipment
const categoryIcons = {
  engine: Cog,
  hydraulics: Cog,
  undercarriage: Truck,
  drivetrain: Cog,
  filters: Package,
  "ground-engaging": Wrench,
  cooling: Gauge,
  electrical: Zap,
};

// Brand colors
const brandColors = {
  caterpillar: "#FFCD00",
  komatsu: "#0066B3", 
  case: "#C8102E",
  cummins: "#E31937",
};

// Difficulty labels for heavy equipment
const difficultyLabels = {
  1: { text: "Quick Service", color: "text-green-500" },
  2: { text: "Field Service", color: "text-green-400" },
  3: { text: "Shop Repair", color: "text-yellow-500" },
  4: { text: "Major Repair", color: "text-orange-500" },
  5: { text: "Overhaul", color: "text-red-500" },
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
const Navbar = ({ onNavigate, currentPage, favoritesCount, garageCount }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <nav className="navbar-glass sticky top-0 z-50" data-testid="navbar">
      <div className="max-w-7xl mx-auto px-4 md:px-8">
        <div className="flex items-center justify-between h-16">
          <button 
            onClick={() => onNavigate("home")}
            className="flex items-center gap-3 group"
            data-testid="logo-btn"
          >
            <img src="/logo.png" alt="EzParts" className="h-12 w-auto" />
          </button>

          <div className="hidden md:flex items-center gap-6">
            <button 
              onClick={() => onNavigate("home")}
              className={`text-sm font-medium transition-colors ${currentPage === "home" ? "text-yellow-500" : "text-zinc-400 hover:text-white"}`}
              data-testid="nav-home"
            >
              Home
            </button>
            <button 
              onClick={() => onNavigate("parts")}
              className={`text-sm font-medium transition-colors ${currentPage === "parts" ? "text-yellow-500" : "text-zinc-400 hover:text-white"}`}
              data-testid="nav-parts"
            >
              Parts
            </button>
            <button 
              onClick={() => onNavigate("diagrams")}
              className={`text-sm font-medium transition-colors flex items-center gap-1 ${currentPage === "diagrams" ? "text-yellow-500" : "text-zinc-400 hover:text-white"}`}
              data-testid="nav-diagrams"
            >
              <Layers className="w-4 h-4" />
              3D Diagrams
            </button>
            <button 
              onClick={() => onNavigate("garage")}
              className={`relative text-sm font-medium transition-colors flex items-center gap-1 ${currentPage === "garage" ? "text-yellow-500" : "text-zinc-400 hover:text-white"}`}
              data-testid="nav-garage"
            >
              <Truck className="w-4 h-4" />
              My Fleet
              {garageCount > 0 && (
                <span className="bg-yellow-500 text-black text-xs w-5 h-5 rounded-full flex items-center justify-center font-mono">
                  {garageCount}
                </span>
              )}
            </button>
            <button 
              onClick={() => onNavigate("suppliers")}
              className={`text-sm font-medium transition-colors ${currentPage === "suppliers" ? "text-yellow-500" : "text-zinc-400 hover:text-white"}`}
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
                <span className="absolute -top-2 -right-3 bg-yellow-500 text-black text-xs w-5 h-5 rounded-full flex items-center justify-center font-mono">
                  {favoritesCount}
                </span>
              )}
            </button>
          </div>

          <Sheet open={mobileMenuOpen} onOpenChange={setMobileMenuOpen}>
            <SheetTrigger asChild className="md:hidden">
              <Button variant="ghost" size="icon" data-testid="mobile-menu-btn">
                <Menu className="w-5 h-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="bg-zinc-900 border-zinc-800">
              <div className="flex flex-col gap-6 mt-8">
                <button onClick={() => { onNavigate("home"); setMobileMenuOpen(false); }} className="flex items-center gap-3 text-lg font-medium">
                  <Home className="w-5 h-5" /> Home
                </button>
                <button onClick={() => { onNavigate("parts"); setMobileMenuOpen(false); }} className="flex items-center gap-3 text-lg font-medium">
                  <Package className="w-5 h-5" /> Parts
                </button>
                <button onClick={() => { onNavigate("diagrams"); setMobileMenuOpen(false); }} className="flex items-center gap-3 text-lg font-medium text-yellow-500">
                  <Layers className="w-5 h-5" /> 3D Diagrams
                </button>
                <button onClick={() => { onNavigate("garage"); setMobileMenuOpen(false); }} className="flex items-center gap-3 text-lg font-medium">
                  <Truck className="w-5 h-5" /> My Fleet ({garageCount})
                </button>
                <button onClick={() => { onNavigate("suppliers"); setMobileMenuOpen(false); }} className="flex items-center gap-3 text-lg font-medium">
                  <Users className="w-5 h-5" /> Suppliers
                </button>
                <button onClick={() => { onNavigate("favorites"); setMobileMenuOpen(false); }} className="flex items-center gap-3 text-lg font-medium">
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

// Installation Difficulty Badge
const DifficultyBadge = ({ level }) => {
  const { text, color } = difficultyLabels[level] || difficultyLabels[3];
  return (
    <div className={`flex items-center gap-1 ${color}`}>
      <Wrench className="w-3 h-3" />
      <span className="text-xs font-mono">{text}</span>
    </div>
  );
};

// Star Rating Component
const StarRating = ({ rating, reviews }) => (
  <div className="flex items-center gap-1">
    <div className="flex">
      {[1,2,3,4,5].map(i => (
        <Star 
          key={i} 
          className={`w-3 h-3 ${i <= Math.round(rating) ? "fill-yellow-500 text-yellow-500" : "text-zinc-600"}`} 
        />
      ))}
    </div>
    <span className="text-xs text-zinc-400 font-mono">{rating.toFixed(1)}</span>
    {reviews && <span className="text-xs text-zinc-500">({reviews.toLocaleString()})</span>}
  </div>
);

// Part Card Component
const PartCard = ({ part, onFavorite, isFavorite, onClick, activeVehicle }) => {
  const IconComponent = categoryIcons[part.category?.toLowerCase()] || Package;
  const isCompatible = activeVehicle ? part.compatibility?.some(c => 
    c.toLowerCase().includes(activeVehicle.make?.toLowerCase()) && 
    c.toLowerCase().includes(activeVehicle.model?.toLowerCase())
  ) : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-industrial bg-zinc-900 p-6 cursor-pointer group relative"
      onClick={onClick}
      data-testid={`part-card-${part.id}`}
    >
      {/* Compatibility indicator */}
      {isCompatible !== null && (
        <div className={`absolute top-2 left-2 ${isCompatible ? "text-green-500" : "text-zinc-600"}`}>
          {isCompatible ? <CheckCircle className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}
        </div>
      )}
      
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
      <h3 className="font-heading text-lg mb-1 group-hover:text-red-500 transition-colors line-clamp-2">
        {part.name}
      </h3>
      <p className="font-mono text-sm text-zinc-500 mb-2">{part.part_number}</p>
      
      {/* Rating & Difficulty */}
      <div className="flex items-center justify-between mb-3">
        <StarRating rating={part.avg_rating || 4.5} reviews={part.review_count} />
        <DifficultyBadge level={part.install_difficulty || 2} />
      </div>
      
      <p className="text-sm text-zinc-400 mb-4 line-clamp-2">{part.description}</p>

      {/* Footer */}
      <div className="flex items-center justify-between pt-4 border-t border-zinc-800">
        <div>
          <p className="font-mono text-2xl font-bold text-white">${part.price?.toFixed(2)}</p>
          <p className="text-xs text-zinc-500">{part.brand}</p>
        </div>
        <div className="text-right">
          <p className="text-xs text-zinc-500">{part.supplier}</p>
          <div className="flex items-center gap-1 justify-end">
            <Clock className="w-3 h-3 text-zinc-500" />
            <p className="text-xs text-zinc-400">{part.install_time || "1-2 hrs"}</p>
          </div>
          <p className={`text-xs font-mono ${part.in_stock ? "text-green-500" : "text-red-500"}`}>
            {part.in_stock ? "IN STOCK" : "OUT OF STOCK"}
          </p>
        </div>
      </div>
    </motion.div>
  );
};

// Part Detail Modal with Price Comparison
const PartDetail = ({ part, onClose, onFavorite, isFavorite }) => {
  const [priceComparison, setPriceComparison] = useState(null);
  const [loadingPrices, setLoadingPrices] = useState(false);
  const IconComponent = categoryIcons[part?.category?.toLowerCase()] || Package;

  useEffect(() => {
    if (part?.id) {
      fetchPriceComparison();
    }
  }, [part?.id]);

  const fetchPriceComparison = async () => {
    setLoadingPrices(true);
    try {
      const response = await axios.get(`${API}/parts/${part.id}/compare-prices`);
      setPriceComparison(response.data);
    } catch (error) {
      console.error("Error fetching prices:", error);
    } finally {
      setLoadingPrices(false);
    }
  };

  if (!part) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4 overflow-y-auto"
      onClick={onClose}
      data-testid="part-detail-modal"
    >
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        className="bg-zinc-900 border border-zinc-800 max-w-4xl w-full max-h-[90vh] overflow-y-auto my-8"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-6 border-b border-zinc-800 flex items-center justify-between sticky top-0 bg-zinc-900 z-10">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-zinc-800 flex items-center justify-center">
              <IconComponent className="w-6 h-6 text-red-500" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <Badge className={`badge-industrial ${part.type === "OEM" ? "bg-blue-600/20 text-blue-400 border border-blue-600/30" : "bg-orange-600/20 text-orange-400 border border-orange-600/30"}`}>
                  {part.type}
                </Badge>
                <DifficultyBadge level={part.install_difficulty || 2} />
              </div>
              <p className="font-mono text-sm text-zinc-500 mt-1">{part.part_number}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-zinc-800 rounded" data-testid="close-detail-btn">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          <h2 className="font-heading text-2xl mb-2">{part.name}</h2>
          <StarRating rating={part.avg_rating || 4.5} reviews={part.review_count} />
          <p className="text-zinc-400 mt-4 mb-6">{part.description}</p>

          {/* Price & Stock */}
          <div className="bg-zinc-800/50 p-4 mb-6 flex items-center justify-between">
            <div>
              <p className="text-sm text-zinc-500">Starting at</p>
              <p className="font-mono text-3xl font-bold">${part.price?.toFixed(2)}</p>
            </div>
            <div className="text-right">
              <p className={`font-mono font-bold ${part.in_stock ? "text-green-500" : "text-red-500"}`}>
                {part.in_stock ? "IN STOCK" : "OUT OF STOCK"}
              </p>
              <div className="flex items-center gap-1 text-zinc-400 mt-1">
                <Clock className="w-4 h-4" />
                <span className="text-sm">{part.install_time || "1-2 hours"}</span>
              </div>
            </div>
          </div>

          {/* Price Comparison */}
          <div className="mb-6">
            <h3 className="font-heading text-sm text-zinc-500 mb-3 flex items-center gap-2">
              <DollarSign className="w-4 h-4" /> COMPARE PRICES
            </h3>
            {loadingPrices ? (
              <div className="flex items-center gap-2 text-zinc-500">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Loading prices...</span>
              </div>
            ) : priceComparison?.prices ? (
              <div className="space-y-2">
                {priceComparison.prices.slice(0, 5).map((price, idx) => (
                  <div 
                    key={idx} 
                    className={`flex items-center justify-between p-3 ${idx === 0 ? "bg-green-900/20 border border-green-600/30" : "bg-zinc-800/30"}`}
                  >
                    <div className="flex items-center gap-3">
                      {idx === 0 && <Badge className="bg-green-600 text-white text-xs">BEST DEAL</Badge>}
                      <div>
                        <p className="font-medium">{price.supplier}</p>
                        <div className="flex items-center gap-2 text-xs text-zinc-500">
                          <Truck className="w-3 h-3" />
                          <span>{price.shipping_days} day shipping</span>
                          <span className="text-zinc-600">|</span>
                          <span>Trust: {price.trust_score}%</span>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-mono font-bold">${price.price?.toFixed(2)}</p>
                      <p className="text-xs text-zinc-500">+${price.shipping_cost?.toFixed(2)} ship</p>
                      <p className="font-mono text-sm text-green-500">${price.total_price?.toFixed(2)} total</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-zinc-500">Price comparison not available</p>
            )}
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

          {/* Cross Reference */}
          {(part.oem_cross_ref || part.aftermarket_alts?.length > 0) && (
            <div className="mb-6">
              <h3 className="font-heading text-sm text-zinc-500 mb-3 flex items-center gap-2">
                <ArrowLeftRight className="w-4 h-4" /> CROSS REFERENCE
              </h3>
              <div className="bg-zinc-800/30 p-4">
                {part.oem_cross_ref && (
                  <div className="mb-2">
                    <span className="text-xs text-zinc-500">OEM Part Number: </span>
                    <span className="font-mono text-blue-400">{part.oem_cross_ref}</span>
                  </div>
                )}
                {part.aftermarket_alts?.length > 0 && (
                  <div>
                    <span className="text-xs text-zinc-500">Also fits: </span>
                    <span className="font-mono text-orange-400">{part.aftermarket_alts.join(", ")}</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Compatibility */}
          {part.compatibility?.length > 0 && (
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

          {/* Actions */}
          <div className="flex gap-4">
            <Button
              onClick={() => onFavorite(part.id)}
              variant={isFavorite ? "default" : "outline"}
              className={`btn-industrial flex-1 ${isFavorite ? "bg-red-600 hover:bg-red-700" : ""}`}
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

// My Fleet Component
const GaragePage = ({ vehicles, onAddVehicle, onRemoveVehicle, onSelectVehicle, activeVehicle, onNavigate }) => {
  const [showAddForm, setShowAddForm] = useState(false);
  const [newVehicle, setNewVehicle] = useState({ year: 2020, make: "", model: "", equipment_type: "", engine: "", nickname: "", hours: "", serial_number: "" });

  const handleSubmit = async (e) => {
    e.preventDefault();
    await onAddVehicle({
      ...newVehicle,
      year: parseInt(newVehicle.year),
      hours: newVehicle.hours ? parseInt(newVehicle.hours) : null
    });
    setNewVehicle({ year: 2020, make: "", model: "", equipment_type: "", engine: "", nickname: "", hours: "", serial_number: "" });
    setShowAddForm(false);
  };

  return (
    <div className="min-h-screen py-8 px-4 md:px-8 max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="font-heading text-3xl mb-2">MY FLEET</h1>
          <p className="text-zinc-400">Manage your heavy equipment for instant part compatibility</p>
        </div>
        <Button onClick={() => setShowAddForm(true)} className="btn-industrial bg-yellow-500 hover:bg-yellow-600 text-black" data-testid="add-vehicle-btn">
          <Plus className="w-4 h-4 mr-2" /> Add Equipment
        </Button>
      </div>

      {/* Add Equipment Form */}
      <AnimatePresence>
        {showAddForm && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-8 overflow-hidden"
          >
            <form onSubmit={handleSubmit} className="bg-zinc-900 border border-zinc-800 p-6">
              <h3 className="font-heading text-lg mb-4">ADD EQUIPMENT</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <Input type="number" placeholder="Year" value={newVehicle.year} onChange={(e) => setNewVehicle({...newVehicle, year: e.target.value})} className="input-industrial" required />
                <select value={newVehicle.make} onChange={(e) => setNewVehicle({...newVehicle, make: e.target.value})} className="input-industrial h-12 px-4 bg-zinc-900" required>
                  <option value="">Select Make</option>
                  <option value="Caterpillar">Caterpillar (CAT)</option>
                  <option value="Komatsu">Komatsu</option>
                  <option value="Case">Case</option>
                  <option value="John Deere">John Deere</option>
                  <option value="Hitachi">Hitachi</option>
                  <option value="Volvo">Volvo CE</option>
                  <option value="Liebherr">Liebherr</option>
                </select>
                <Input placeholder="Model (e.g., 320F)" value={newVehicle.model} onChange={(e) => setNewVehicle({...newVehicle, model: e.target.value})} className="input-industrial" required />
                <select value={newVehicle.equipment_type} onChange={(e) => setNewVehicle({...newVehicle, equipment_type: e.target.value})} className="input-industrial h-12 px-4 bg-zinc-900" required>
                  <option value="">Equipment Type</option>
                  <option value="Excavator">Excavator</option>
                  <option value="Wheel Loader">Wheel Loader</option>
                  <option value="Dozer">Dozer</option>
                  <option value="Motor Grader">Motor Grader</option>
                  <option value="Haul Truck">Haul Truck</option>
                  <option value="Backhoe">Backhoe</option>
                  <option value="Skid Steer">Skid Steer</option>
                  <option value="Generator">Generator</option>
                </select>
                <Input placeholder="Engine (e.g., Cummins QSX15)" value={newVehicle.engine} onChange={(e) => setNewVehicle({...newVehicle, engine: e.target.value})} className="input-industrial" />
                <Input placeholder="Serial Number" value={newVehicle.serial_number} onChange={(e) => setNewVehicle({...newVehicle, serial_number: e.target.value})} className="input-industrial" />
                <Input type="number" placeholder="Hours" value={newVehicle.hours} onChange={(e) => setNewVehicle({...newVehicle, hours: e.target.value})} className="input-industrial" />
                <Input placeholder="Nickname" value={newVehicle.nickname} onChange={(e) => setNewVehicle({...newVehicle, nickname: e.target.value})} className="input-industrial" />
              </div>
              <div className="flex gap-4">
                <Button type="submit" className="btn-industrial bg-yellow-500 hover:bg-yellow-600 text-black">Save Equipment</Button>
                <Button type="button" variant="outline" onClick={() => setShowAddForm(false)} className="btn-industrial">Cancel</Button>
              </div>
            </form>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Equipment Cards */}
      {vehicles.length === 0 ? (
        <div className="text-center py-16">
          <Truck className="w-16 h-16 text-zinc-700 mx-auto mb-4" />
          <p className="text-zinc-500 mb-4">No equipment in your fleet yet</p>
          <Button onClick={() => setShowAddForm(true)} className="btn-industrial bg-yellow-500 hover:bg-yellow-600 text-black">
            Add Your First Machine
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {vehicles.map((vehicle) => (
            <motion.div
              key={vehicle.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className={`card-industrial bg-zinc-900 p-6 ${activeVehicle?.id === vehicle.id ? "border-yellow-500" : ""}`}
              data-testid={`vehicle-card-${vehicle.id}`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="w-12 h-12 bg-zinc-800 flex items-center justify-center">
                  <Truck className="w-6 h-6 text-yellow-500" />
                </div>
                {activeVehicle?.id === vehicle.id && (
                  <Badge className="bg-yellow-500 text-black">ACTIVE</Badge>
                )}
              </div>
              
              {vehicle.nickname && (
                <p className="text-yellow-500 font-medium mb-1">"{vehicle.nickname}"</p>
              )}
              <h3 className="font-heading text-xl mb-1">
                {vehicle.year} {vehicle.make} {vehicle.model}
              </h3>
              <p className="text-zinc-500 text-sm mb-2">
                {vehicle.equipment_type || vehicle.trim} {vehicle.engine && `• ${vehicle.engine}`}
              </p>
              {vehicle.serial_number && (
                <p className="font-mono text-xs text-zinc-600 mb-2">S/N: {vehicle.serial_number}</p>
              )}
              
              {(vehicle.hours || vehicle.mileage) && (
                <p className="font-mono text-sm text-zinc-400 mb-4">
                  <Gauge className="w-4 h-4 inline mr-1" />
                  {vehicle.hours ? `${vehicle.hours.toLocaleString()} hours` : `${vehicle.mileage?.toLocaleString()} miles`}
                </p>
              )}

              <div className="flex gap-2 pt-4 border-t border-zinc-800">
                <Button 
                  onClick={() => onSelectVehicle(vehicle)}
                  variant={activeVehicle?.id === vehicle.id ? "default" : "outline"}
                  className={`btn-industrial flex-1 text-xs ${activeVehicle?.id === vehicle.id ? "bg-yellow-500 text-black hover:bg-yellow-600" : ""}`}
                >
                  {activeVehicle?.id === vehicle.id ? "Selected" : "Select"}
                </Button>
                <Button 
                  onClick={() => onNavigate("parts", vehicle)}
                  className="btn-industrial flex-1 text-xs bg-zinc-800 hover:bg-zinc-700"
                >
                  Find Parts
                </Button>
                <Button 
                  onClick={() => onRemoveVehicle(vehicle.id)}
                  variant="ghost"
                  size="icon"
                  className="text-zinc-500 hover:text-red-500"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
};

// AI Chat Component with Problem Diagnosis
const AIChat = ({ isOpen, onClose, activeVehicle }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(getSessionId);
  const [isListening, setIsListening] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      loadChatHistory();
    }
  }, [isOpen]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const loadChatHistory = async () => {
    try {
      const response = await axios.get(`${API}/chat/${sessionId}`);
      setMessages(response.data);
    } catch (error) {
      console.error("Error loading chat history:", error);
    }
  };

  const sendMessage = async (messageText = input) => {
    if (!messageText.trim() || loading) return;

    const userMessage = messageText.trim();
    setInput("");
    setMessages(prev => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);

    try {
      const response = await axios.post(`${API}/chat`, {
        session_id: sessionId,
        message: userMessage,
        vehicle_context: activeVehicle
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

  // Voice recognition (simplified)
  const toggleVoice = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      toast.error("Voice search not supported in this browser");
      return;
    }
    setIsListening(!isListening);
    toast.info(isListening ? "Voice stopped" : "Listening... speak now");
  };

  if (!isOpen) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 20, scale: 0.95 }}
      className="fixed bottom-36 right-4 md:bottom-24 md:right-52 w-[90vw] md:w-[420px] h-[520px] bg-zinc-900 border border-zinc-800 shadow-2xl flex flex-col z-[99]"
      data-testid="ai-chat-panel"
    >
      {/* Header */}
      <div className="p-4 border-b border-zinc-800 flex items-center justify-between bg-gradient-to-r from-yellow-900/20 to-transparent">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-br from-yellow-500 to-yellow-700 flex items-center justify-center rounded">
            <MessageSquare className="w-4 h-4 text-black" />
          </div>
          <div>
            <h3 className="font-heading text-sm text-yellow-500">EZPARTS AI</h3>
            <p className="text-xs text-zinc-500">
              {activeVehicle ? `${activeVehicle.year} ${activeVehicle.make} ${activeVehicle.model}` : "Heavy Equipment Expert"}
            </p>
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
          <div className="text-center py-6">
            <Wrench className="w-10 h-10 text-zinc-700 mx-auto mb-3" />
            <p className="text-zinc-500 text-sm mb-4">Describe a problem or ask about parts!</p>
            <div className="flex flex-wrap gap-2 justify-center">
              {[
                "CAT 320 hydraulic pump issue",
                "Komatsu undercarriage parts",
                "Cummins ISX injector problems",
                "Case loader bucket teeth"
              ].map((q) => (
                <button
                  key={q}
                  onClick={() => sendMessage(q)}
                  className="text-xs bg-zinc-800 px-3 py-1.5 rounded hover:bg-zinc-700 transition-colors"
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
            <div className={`inline-block max-w-[85%] p-3 text-sm ${msg.role === "user" ? "bg-red-600 text-white" : "bg-zinc-800 text-zinc-200"}`}>
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
        <div ref={messagesEndRef} />
      </ScrollArea>

      {/* Input */}
      <div className="p-4 border-t border-zinc-800">
        <div className="flex gap-2">
          <button
            onClick={toggleVoice}
            className={`p-3 rounded ${isListening ? "bg-red-600" : "bg-zinc-800 hover:bg-zinc-700"}`}
            data-testid="voice-btn"
          >
            {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
          </button>
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Describe your problem..."
            className="input-industrial flex-1"
            data-testid="chat-input"
          />
          <Button
            onClick={() => sendMessage()}
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
const HomePage = ({ categories, onSearch, onCategoryClick, activeVehicle }) => {
  const [searchQuery, setSearchQuery] = useState("");

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative py-16 md:py-28 px-4 md:px-8">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute inset-0 bg-cover bg-center opacity-20" style={{ backgroundImage: `url(https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=1920)` }} />
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-zinc-900/50 to-zinc-900" />
        </div>
        
        <div className="relative max-w-4xl mx-auto text-center">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
            {activeVehicle && (
              <div className="inline-flex items-center gap-2 bg-yellow-500/20 border border-yellow-500/30 px-4 py-2 rounded-sm mb-6">
                <Truck className="w-4 h-4 text-yellow-500" />
                <span className="text-sm">Shopping for: <span className="font-bold">{activeVehicle.year} {activeVehicle.make} {activeVehicle.model}</span></span>
              </div>
            )}
            {/* Logo */}
            <img src="/logo.png" alt="EzParts - The New Era" className="h-32 md:h-40 mx-auto mb-8" />
            <p className="text-lg md:text-xl text-zinc-400 mb-6 max-w-2xl mx-auto">
              CAT, Komatsu, Case, Cummins - Find OEM & aftermarket parts for excavators, dozers, loaders, and diesel engines.
            </p>
            {/* Brand logos */}
            <div className="flex items-center justify-center gap-6 mb-10">
              <span className="text-sm font-heading text-yellow-500">CATERPILLAR</span>
              <span className="text-sm font-heading text-blue-500">KOMATSU</span>
              <span className="text-sm font-heading text-red-500">CASE</span>
              <span className="text-sm font-heading text-red-600">CUMMINS</span>
            </div>
          </motion.div>

          {/* Search Bar */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <div className="flex flex-col md:flex-row gap-4 max-w-2xl mx-auto">
              <div className="relative flex-1">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500" />
                <Input
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && onSearch(searchQuery)}
                  placeholder="Search parts, part numbers, or describe a problem..."
                  className="input-industrial w-full pl-12"
                  data-testid="hero-search-input"
                />
              </div>
              <Button onClick={() => onSearch(searchQuery)} className="btn-industrial bg-red-600 hover:bg-red-700" data-testid="hero-search-btn">
                Search Parts
              </Button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Categories */}
      <section className="py-12 px-4 md:px-8 max-w-7xl mx-auto">
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
                <p className="text-xs text-zinc-500">{cat.description}</p>
                <p className="font-mono text-xs text-red-500 mt-2">{cat.count} parts</p>
              </motion.button>
            );
          })}
        </div>
      </section>

      {/* Features */}
      <section className="py-12 px-4 md:px-8 bg-zinc-900/50">
        <div className="max-w-7xl mx-auto grid md:grid-cols-4 gap-6">
          <div className="p-6">
            <div className="w-12 h-12 bg-red-600/20 flex items-center justify-center mb-4">
              <TrendingUp className="w-6 h-6 text-red-500" />
            </div>
            <h3 className="font-heading text-lg mb-2">PRICE COMPARISON</h3>
            <p className="text-zinc-400 text-sm">Compare prices across all suppliers instantly. Find the best deal every time.</p>
          </div>
          <div className="p-6">
            <div className="w-12 h-12 bg-red-600/20 flex items-center justify-center mb-4">
              <ArrowLeftRight className="w-6 h-6 text-red-500" />
            </div>
            <h3 className="font-heading text-lg mb-2">CROSS REFERENCE</h3>
            <p className="text-zinc-400 text-sm">Find OEM equivalents for aftermarket parts and vice versa.</p>
          </div>
          <div className="p-6">
            <div className="w-12 h-12 bg-red-600/20 flex items-center justify-center mb-4">
              <MessageSquare className="w-6 h-6 text-red-500" />
            </div>
            <h3 className="font-heading text-lg mb-2">AI DIAGNOSIS</h3>
            <p className="text-zinc-400 text-sm">Describe symptoms, get AI-powered diagnosis and part recommendations.</p>
          </div>
          <div className="p-6">
            <div className="w-12 h-12 bg-red-600/20 flex items-center justify-center mb-4">
              <Car className="w-6 h-6 text-red-500" />
            </div>
            <h3 className="font-heading text-lg mb-2">MY GARAGE</h3>
            <p className="text-zinc-400 text-sm">Save your vehicles for instant compatibility checking on every part.</p>
          </div>
        </div>
      </section>
    </div>
  );
};

// Parts Page
const PartsPage = ({ parts, loading, favorites, onFavorite, onPartClick, searchQuery, onSearch, activeVehicle }) => {
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
      {activeVehicle && (
        <div className="mb-6 bg-zinc-900 border border-zinc-800 p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Car className="w-5 h-5 text-red-500" />
            <span>Showing parts for: <span className="font-bold">{activeVehicle.year} {activeVehicle.make} {activeVehicle.model}</span></span>
          </div>
          <Badge className="bg-green-600/20 text-green-500 border-green-600/30">Compatibility Filter Active</Badge>
        </div>
      )}

      <div className="mb-8">
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500" />
            <Input value={localSearch} onChange={(e) => setLocalSearch(e.target.value)} onKeyDown={(e) => e.key === "Enter" && onSearch(localSearch)} placeholder="Search parts..." className="input-industrial w-full pl-12" data-testid="parts-search-input" />
          </div>
          <Button onClick={() => onSearch(localSearch)} className="btn-industrial bg-red-600 hover:bg-red-700" data-testid="parts-search-btn">Search</Button>
        </div>

        <div className="flex flex-wrap gap-4">
          <div className="flex bg-zinc-800/50 p-1 rounded-sm">
            {["all", "OEM", "Aftermarket"].map(type => (
              <button
                key={type}
                onClick={() => setTypeFilter(type)}
                className={`px-4 py-2 font-mono text-xs rounded-sm transition-colors ${typeFilter === type ? "bg-red-600 text-white" : "text-zinc-400 hover:text-white"}`}
                data-testid={`filter-${type.toLowerCase()}`}
              >
                {type === "all" ? "All" : type}
              </button>
            ))}
          </div>
          <select value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)} className="input-industrial h-10 px-4 bg-zinc-800/50" data-testid="category-filter">
            <option value="all">All Categories</option>
            {categories.map(cat => <option key={cat} value={cat.toLowerCase()}>{cat}</option>)}
          </select>
        </div>
      </div>

      <div className="mb-4">
        <p className="text-sm text-zinc-500">Showing <span className="text-white font-mono">{filteredParts.length}</span> parts</p>
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
              activeVehicle={activeVehicle}
            />
          ))}
        </div>
      )}
    </div>
  );
};

// Suppliers Page
const SuppliersPage = ({ suppliers, loading }) => (
  <div className="min-h-screen py-8 px-4 md:px-8 max-w-7xl mx-auto">
    <h1 className="font-heading text-3xl mb-2">US SUPPLIERS</h1>
    <p className="text-zinc-400 mb-8">Trusted suppliers ranked by trust score</p>

    {loading ? (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {[1,2,3,4].map(i => <div key={i} className="bg-zinc-900 p-6 animate-pulse"><div className="h-6 bg-zinc-800 rounded mb-4 w-1/3" /></div>)}
      </div>
    ) : (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {suppliers.map((supplier, idx) => (
          <motion.div key={supplier.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.1 }} className="card-industrial bg-zinc-900 p-6" data-testid={`supplier-card-${supplier.id}`}>
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="font-heading text-xl">{supplier.name}</h3>
                <p className="text-sm text-zinc-500 flex items-center gap-1 mt-1">
                  <MapPin className="w-3 h-3" /> {supplier.location}, {supplier.state}
                </p>
              </div>
              <div className="text-right">
                <div className="flex items-center gap-1 bg-zinc-800 px-2 py-1 mb-1">
                  <Shield className="w-4 h-4 text-green-500" />
                  <span className="font-mono text-sm">{supplier.trust_score}%</span>
                </div>
                <div className="flex items-center gap-1">
                  <Star className="w-3 h-3 text-yellow-500 fill-yellow-500" />
                  <span className="font-mono text-xs">{supplier.rating}</span>
                </div>
              </div>
            </div>

            <div className="flex flex-wrap gap-2 mb-4">
              {supplier.specialties?.map((spec, i) => <Badge key={i} className="badge-industrial bg-zinc-800 text-zinc-300">{spec}</Badge>)}
            </div>

            <div className="grid grid-cols-2 gap-4 text-sm mb-4">
              <div>
                <p className="text-zinc-500">Avg Shipping</p>
                <p className="font-mono">{supplier.avg_shipping_days} days</p>
              </div>
              <div>
                <p className="text-zinc-500">Return Policy</p>
                <p className="font-mono">{supplier.return_policy}</p>
              </div>
            </div>

            <div className="pt-4 border-t border-zinc-800 flex items-center justify-between">
              <p className="font-mono text-sm text-zinc-400">{supplier.contact}</p>
              <a href={`https://${supplier.website}`} target="_blank" rel="noopener noreferrer" className="text-red-500 hover:text-red-400 flex items-center gap-1 text-sm">
                Visit <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </motion.div>
        ))}
      </div>
    )}
  </div>
);

// Favorites Page
const FavoritesPage = ({ favorites, loading, onRemove, onPartClick, activeVehicle }) => (
  <div className="min-h-screen py-8 px-4 md:px-8 max-w-7xl mx-auto">
    <h1 className="font-heading text-3xl mb-2">SAVED PARTS</h1>
    <p className="text-zinc-400 mb-8">Your saved parts for quick access</p>

    {loading ? (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1,2,3].map(i => <div key={i} className="bg-zinc-900 p-6 animate-pulse"><div className="h-6 bg-zinc-800 rounded mb-4 w-1/3" /></div>)}
      </div>
    ) : favorites.length === 0 ? (
      <div className="text-center py-16">
        <Heart className="w-16 h-16 text-zinc-700 mx-auto mb-4" />
        <p className="text-zinc-500">No saved parts yet. Start browsing and save parts you like!</p>
      </div>
    ) : (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {favorites.map(({ favorite_id, part }) => (
          <PartCard key={favorite_id} part={part} onFavorite={onRemove} isFavorite={true} onClick={() => onPartClick(part)} activeVehicle={activeVehicle} />
        ))}
      </div>
    )}
  </div>
);

// 3D Diagrams Page
const DiagramsPage = ({ onSearch }) => {
  const [activeTab, setActiveTab] = useState("equipment");
  const [selectedEquipment, setSelectedEquipment] = useState("excavator");

  const handlePartSelect = (partName) => {
    onSearch(partName);
  };

  const handleWizardResult = (result) => {
    onSearch(result.location);
  };

  return (
    <div className="min-h-screen py-8 px-4 md:px-8 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="font-heading text-3xl mb-2 flex items-center gap-3">
          <Layers className="w-8 h-8 text-yellow-500" />
          3D PARTS DIAGRAMS
        </h1>
        <p className="text-zinc-400">Interactive diagrams to identify the exact part you need. No more ordering mistakes!</p>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 mb-8 overflow-x-auto pb-2">
        {[
          { id: "equipment", label: "Equipment Diagrams", icon: Truck },
          { id: "exploded", label: "Exploded Views", icon: Layers },
          { id: "wizard", label: "Part Finder Wizard", icon: Search },
          { id: "3d-viewer", label: "3D Part Viewer", icon: Eye },
        ].map((tab) => (
          <Button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            variant={activeTab === tab.id ? "default" : "outline"}
            className={`flex items-center gap-2 whitespace-nowrap ${activeTab === tab.id ? "bg-yellow-500 text-black hover:bg-yellow-600" : ""}`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </Button>
        ))}
      </div>

      {/* Equipment Diagram Tab */}
      {activeTab === "equipment" && (
        <div>
          {/* Equipment selector */}
          <div className="flex gap-2 mb-6">
            {[
              { id: "excavator", label: "Excavator" },
              { id: "engine", label: "Diesel Engine" },
              { id: "undercarriage", label: "Undercarriage" },
            ].map((eq) => (
              <Button
                key={eq.id}
                onClick={() => setSelectedEquipment(eq.id)}
                variant={selectedEquipment === eq.id ? "default" : "outline"}
                size="sm"
                className={selectedEquipment === eq.id ? "bg-zinc-700" : ""}
              >
                {eq.label}
              </Button>
            ))}
          </div>
          
          <EquipmentDiagram type={selectedEquipment} onPartSelect={handlePartSelect} />
          
          <div className="mt-6 bg-zinc-900 border border-zinc-800 p-4 rounded">
            <h3 className="font-heading text-sm text-yellow-500 mb-2">HOW TO USE</h3>
            <ul className="text-sm text-zinc-400 space-y-1">
              <li>• Click on the <span className="text-red-500">red hotspots</span> to identify parts</li>
              <li>• Hover over a hotspot to see available parts for that location</li>
              <li>• Click a part name to search for it in the catalog</li>
              <li>• Use zoom controls to inspect details</li>
            </ul>
          </div>
        </div>
      )}

      {/* Exploded View Tab */}
      {activeTab === "exploded" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ExplodedViewDiagram assembly="hydraulic-pump" />
          <div className="bg-zinc-900 border border-zinc-800 p-6 rounded">
            <h3 className="font-heading text-lg text-yellow-500 mb-4">ASSEMBLY BREAKDOWN</h3>
            <p className="text-zinc-400 text-sm mb-4">
              Exploded views help you understand how components fit together. 
              Each numbered part can be ordered separately or as a kit.
            </p>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-zinc-800 rounded">
                <span className="text-sm">Complete Seal Kit</span>
                <Badge className="bg-green-600">Available</Badge>
              </div>
              <div className="flex items-center justify-between p-3 bg-zinc-800 rounded">
                <span className="text-sm">Individual Components</span>
                <Badge className="bg-yellow-500 text-black">Order Separate</Badge>
              </div>
              <div className="flex items-center justify-between p-3 bg-zinc-800 rounded">
                <span className="text-sm">Remanufactured Assembly</span>
                <Badge className="bg-blue-500">Save 40%</Badge>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Part Finder Wizard Tab */}
      {activeTab === "wizard" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <PartIdentificationWizard onPartFound={handleWizardResult} />
          <div className="bg-zinc-900 border border-zinc-800 p-6 rounded">
            <h3 className="font-heading text-lg text-yellow-500 mb-4">WHY USE THE WIZARD?</h3>
            <div className="space-y-4">
              <div className="flex gap-3">
                <div className="w-8 h-8 bg-yellow-500/20 rounded flex items-center justify-center flex-shrink-0">
                  <CheckCircle className="w-4 h-4 text-yellow-500" />
                </div>
                <div>
                  <p className="font-medium">Avoid Wrong Orders</p>
                  <p className="text-sm text-zinc-500">Step-by-step guidance ensures you find the exact part</p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="w-8 h-8 bg-yellow-500/20 rounded flex items-center justify-center flex-shrink-0">
                  <Clock className="w-4 h-4 text-yellow-500" />
                </div>
                <div>
                  <p className="font-medium">Save Time</p>
                  <p className="text-sm text-zinc-500">No more scrolling through thousands of parts</p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="w-8 h-8 bg-yellow-500/20 rounded flex items-center justify-center flex-shrink-0">
                  <DollarSign className="w-4 h-4 text-yellow-500" />
                </div>
                <div>
                  <p className="font-medium">Reduce Returns</p>
                  <p className="text-sm text-zinc-500">Right part the first time = no shipping costs for returns</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 3D Viewer Tab */}
      {activeTab === "3d-viewer" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ModelViewer3D 
            partName="Hydraulic Pump Assembly" 
            partNumber="259-0815"
          />
          <div className="bg-zinc-900 border border-zinc-800 p-6 rounded">
            <h3 className="font-heading text-lg text-yellow-500 mb-4">3D INSPECTION</h3>
            <p className="text-zinc-400 text-sm mb-4">
              Rotate and zoom the 3D model to inspect every angle before ordering. 
              Match the part to what you see on your equipment.
            </p>
            <div className="space-y-2 text-sm">
              <p className="text-zinc-500">🖱️ <span className="text-zinc-300">Left-click + drag</span> to rotate</p>
              <p className="text-zinc-500">🖱️ <span className="text-zinc-300">Scroll wheel</span> to zoom in/out</p>
              <p className="text-zinc-500">🖱️ <span className="text-zinc-300">Right-click + drag</span> to pan</p>
            </div>
            <div className="mt-6 p-4 bg-yellow-500/10 border border-yellow-500/30 rounded">
              <p className="text-yellow-500 text-sm font-medium">💡 Pro Tip</p>
              <p className="text-zinc-400 text-xs mt-1">
                Take a photo of your damaged part and compare it side-by-side with the 3D model 
                to verify you're ordering the correct replacement.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Main App
function App() {
  const [currentPage, setCurrentPage] = useState("home");
  const [parts, setParts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [favoriteIds, setFavoriteIds] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  const [activeVehicle, setActiveVehicle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedPart, setSelectedPart] = useState(null);
  const [chatOpen, setChatOpen] = useState(false);

  useEffect(() => {
    fetchCategories();
    fetchParts();
    fetchSuppliers();
    fetchFavorites();
    fetchGarage();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API}/categories`);
      setCategories(response.data);
    } catch (error) {
      console.error("Error fetching categories:", error);
    }
  };

  const fetchParts = async (search = "", category = "", vehicleId = null) => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (search) params.append("search", search);
      if (category) params.append("category", category);
      if (vehicleId) params.append("vehicle_id", vehicleId);
      
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
      const response = await axios.get(`${API}/suppliers?sort_by=trust_score`);
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

  const fetchGarage = async () => {
    try {
      const response = await axios.get(`${API}/garage`);
      setVehicles(response.data);
    } catch (error) {
      console.error("Error fetching garage:", error);
    }
  };

  const handleAddVehicle = async (vehicle) => {
    try {
      await axios.post(`${API}/garage`, vehicle);
      fetchGarage();
      toast.success("Vehicle added to garage!");
    } catch (error) {
      console.error("Error adding vehicle:", error);
      toast.error("Failed to add vehicle");
    }
  };

  const handleRemoveVehicle = async (vehicleId) => {
    try {
      await axios.delete(`${API}/garage/${vehicleId}`);
      if (activeVehicle?.id === vehicleId) setActiveVehicle(null);
      fetchGarage();
      toast.success("Vehicle removed");
    } catch (error) {
      console.error("Error removing vehicle:", error);
    }
  };

  const handleSearch = (query) => {
    setSearchQuery(query);
    fetchParts(query, "", activeVehicle?.id);
    setCurrentPage("parts");
  };

  const handleCategoryClick = (category) => {
    setSearchQuery("");
    fetchParts("", category, activeVehicle?.id);
    setCurrentPage("parts");
  };

  const handleFavorite = async (partId) => {
    if (favoriteIds.includes(partId)) {
      try {
        await axios.delete(`${API}/favorites/${partId}`);
        setFavoriteIds(prev => prev.filter(id => id !== partId));
        setFavorites(prev => prev.filter(f => f.part.id !== partId));
        toast.success("Removed from saved parts");
      } catch (error) {
        console.error("Error removing favorite:", error);
      }
    } else {
      try {
        await axios.post(`${API}/favorites`, { part_id: partId });
        setFavoriteIds(prev => [...prev, partId]);
        fetchFavorites();
        toast.success("Added to saved parts");
      } catch (error) {
        console.error("Error adding favorite:", error);
      }
    }
  };

  const handleNavigate = (page, vehicle = null) => {
    setCurrentPage(page);
    if (page === "parts") {
      if (vehicle) {
        setActiveVehicle(vehicle);
        fetchParts("", "", vehicle.id);
      } else {
        fetchParts(searchQuery, "", activeVehicle?.id);
      }
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 grid-pattern">
      <Toaster position="top-right" richColors />
      
      <Navbar onNavigate={handleNavigate} currentPage={currentPage} favoritesCount={favoriteIds.length} garageCount={vehicles.length} />

      <AnimatePresence mode="wait">
        {currentPage === "home" && (
          <motion.div key="home" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <HomePage categories={categories} onSearch={handleSearch} onCategoryClick={handleCategoryClick} activeVehicle={activeVehicle} />
          </motion.div>
        )}
        {currentPage === "parts" && (
          <motion.div key="parts" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <PartsPage parts={parts} loading={loading} favorites={favoriteIds} onFavorite={handleFavorite} onPartClick={setSelectedPart} searchQuery={searchQuery} onSearch={handleSearch} activeVehicle={activeVehicle} />
          </motion.div>
        )}
        {currentPage === "diagrams" && (
          <motion.div key="diagrams" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <DiagramsPage onSearch={handleSearch} />
          </motion.div>
        )}
        {currentPage === "garage" && (
          <motion.div key="garage" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <GaragePage vehicles={vehicles} onAddVehicle={handleAddVehicle} onRemoveVehicle={handleRemoveVehicle} onSelectVehicle={setActiveVehicle} activeVehicle={activeVehicle} onNavigate={handleNavigate} />
          </motion.div>
        )}
        {currentPage === "suppliers" && (
          <motion.div key="suppliers" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <SuppliersPage suppliers={suppliers} loading={loading && suppliers.length === 0} />
          </motion.div>
        )}
        {currentPage === "favorites" && (
          <motion.div key="favorites" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <FavoritesPage favorites={favorites} loading={loading && favorites.length === 0} onRemove={handleFavorite} onPartClick={setSelectedPart} activeVehicle={activeVehicle} />
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {selectedPart && <PartDetail part={selectedPart} onClose={() => setSelectedPart(null)} onFavorite={handleFavorite} isFavorite={favoriteIds.includes(selectedPart.id)} />}
      </AnimatePresence>

      <AnimatePresence>
        <AIChat isOpen={chatOpen} onClose={() => setChatOpen(false)} activeVehicle={activeVehicle} />
      </AnimatePresence>

      <motion.button
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setChatOpen(!chatOpen)}
        className="fixed bottom-20 right-4 md:bottom-6 md:right-52 w-14 h-14 bg-gradient-to-br from-yellow-500 to-yellow-700 hover:from-yellow-400 hover:to-yellow-600 flex items-center justify-center shadow-lg z-[100]"
        style={{ boxShadow: "0 0 30px rgba(212, 175, 55, 0.4)" }}
        data-testid="chat-fab"
      >
        {chatOpen ? <X className="w-6 h-6 text-black" /> : <MessageSquare className="w-6 h-6 text-black" />}
      </motion.button>
    </div>
  );
}

export default App;
