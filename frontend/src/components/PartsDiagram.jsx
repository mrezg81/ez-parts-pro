import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  RotateCcw, 
  ZoomIn, 
  ZoomOut, 
  Maximize2, 
  Info, 
  ChevronLeft, 
  ChevronRight,
  Crosshair,
  Eye,
  Layers
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

// Import model-viewer as a side effect
import '@google/model-viewer';

// Equipment diagram data - mapping parts to their locations on equipment
const equipmentDiagrams = {
  excavator: {
    name: "Excavator Assembly",
    image: "https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=800",
    hotspots: [
      { id: "boom-cylinder", x: 35, y: 25, label: "Boom Cylinder", parts: ["Hydraulic Cylinder Seal Kit", "Boom Pin"] },
      { id: "hydraulic-pump", x: 55, y: 60, label: "Main Hydraulic Pump", parts: ["CAT Hydraulic Pump - Main"] },
      { id: "final-drive", x: 80, y: 75, label: "Final Drive", parts: ["Komatsu Final Drive Assembly"] },
      { id: "track-chain", x: 75, y: 85, label: "Track Chain", parts: ["CAT Undercarriage Track Chain"] },
      { id: "engine", x: 50, y: 50, label: "Engine Bay", parts: ["CAT Fuel Injector - C15 Engine", "Cummins Turbocharger"] },
      { id: "bucket-teeth", x: 15, y: 35, label: "Bucket Teeth", parts: ["Case Loader Bucket Teeth Set"] },
    ]
  },
  engine: {
    name: "Diesel Engine Assembly",
    image: "https://images.unsplash.com/photo-1486262715619-67b85e0b08d3?w=800",
    hotspots: [
      { id: "turbo", x: 30, y: 20, label: "Turbocharger", parts: ["Cummins Turbocharger - QSX15"] },
      { id: "injectors", x: 45, y: 35, label: "Fuel Injectors", parts: ["CAT Fuel Injector - C15 Engine", "Cummins Injector Overhaul Kit"] },
      { id: "water-pump", x: 60, y: 55, label: "Water Pump", parts: ["Cummins Water Pump Assembly"] },
      { id: "air-filter", x: 25, y: 45, label: "Air Intake", parts: ["Heavy Duty Air Filter - Universal"] },
      { id: "oil-filter", x: 70, y: 65, label: "Oil Filter", parts: ["Case Hydraulic Filter Element"] },
    ]
  },
  undercarriage: {
    name: "Undercarriage Assembly",
    image: "https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800",
    hotspots: [
      { id: "track-chain", x: 50, y: 70, label: "Track Chain", parts: ["CAT Undercarriage Track Chain"] },
      { id: "track-roller", x: 30, y: 80, label: "Track Rollers", parts: ["Aftermarket Excavator Track Rollers"] },
      { id: "idler", x: 15, y: 75, label: "Front Idler", parts: ["Front Idler Assembly"] },
      { id: "sprocket", x: 85, y: 75, label: "Drive Sprocket", parts: ["Drive Sprocket"] },
      { id: "final-drive", x: 80, y: 60, label: "Final Drive Motor", parts: ["Komatsu Final Drive Assembly"] },
    ]
  }
};

// Sample 3D model URLs (using free GLB models for demo)
const sampleModels = {
  "hydraulic-pump": "https://modelviewer.dev/shared-assets/models/Astronaut.glb",
  "engine-block": "https://modelviewer.dev/shared-assets/models/RobotExpressive.glb",
  "turbocharger": "https://modelviewer.dev/shared-assets/models/Horse.glb",
};

// Interactive Hotspot Component
const Hotspot = ({ hotspot, isActive, onClick, onPartClick }) => {
  const [showTooltip, setShowTooltip] = useState(false);

  return (
    <div
      className="absolute cursor-pointer group"
      style={{ left: `${hotspot.x}%`, top: `${hotspot.y}%`, transform: 'translate(-50%, -50%)' }}
      onClick={() => onClick(hotspot)}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      {/* Pulse ring */}
      <div className={`absolute w-8 h-8 rounded-full ${isActive ? 'bg-yellow-500/30' : 'bg-red-500/30'} animate-ping`} />
      
      {/* Main dot */}
      <div className={`relative w-6 h-6 rounded-full ${isActive ? 'bg-yellow-500' : 'bg-red-600'} border-2 border-white flex items-center justify-center z-10 transition-all group-hover:scale-125`}>
        <Crosshair className="w-3 h-3 text-white" />
      </div>

      {/* Tooltip */}
      <AnimatePresence>
        {(showTooltip || isActive) && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="absolute left-8 top-0 bg-zinc-900 border border-zinc-700 p-3 rounded shadow-xl z-20 min-w-[200px]"
          >
            <p className="font-heading text-sm text-yellow-500 mb-2">{hotspot.label}</p>
            <div className="space-y-1">
              {hotspot.parts.map((part, idx) => (
                <button
                  key={idx}
                  onClick={(e) => { e.stopPropagation(); onPartClick(part); }}
                  className="block text-xs text-zinc-400 hover:text-white transition-colors"
                >
                  → {part}
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// Interactive Equipment Diagram
export const EquipmentDiagram = ({ type = "excavator", onPartSelect }) => {
  const [activeHotspot, setActiveHotspot] = useState(null);
  const [zoom, setZoom] = useState(1);
  const diagram = equipmentDiagrams[type] || equipmentDiagrams.excavator;

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-zinc-800 flex items-center justify-between">
        <div>
          <h3 className="font-heading text-lg text-yellow-500">{diagram.name}</h3>
          <p className="text-xs text-zinc-500">Click hotspots to identify parts</p>
        </div>
        <div className="flex gap-2">
          <Button size="sm" variant="outline" onClick={() => setZoom(z => Math.max(0.5, z - 0.25))}>
            <ZoomOut className="w-4 h-4" />
          </Button>
          <Button size="sm" variant="outline" onClick={() => setZoom(z => Math.min(2, z + 0.25))}>
            <ZoomIn className="w-4 h-4" />
          </Button>
          <Button size="sm" variant="outline" onClick={() => setZoom(1)}>
            <RotateCcw className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Diagram */}
      <div className="relative overflow-hidden" style={{ height: '400px' }}>
        <div 
          className="absolute inset-0 transition-transform duration-300"
          style={{ transform: `scale(${zoom})`, transformOrigin: 'center' }}
        >
          <img 
            src={diagram.image} 
            alt={diagram.name}
            className="w-full h-full object-cover opacity-80"
          />
          
          {/* Hotspots */}
          {diagram.hotspots.map((hotspot) => (
            <Hotspot
              key={hotspot.id}
              hotspot={hotspot}
              isActive={activeHotspot?.id === hotspot.id}
              onClick={setActiveHotspot}
              onPartClick={onPartSelect}
            />
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="p-4 border-t border-zinc-800 bg-zinc-950">
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-600" />
            <span className="text-zinc-400">Part Location</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-yellow-500" />
            <span className="text-zinc-400">Selected</span>
          </div>
          <span className="text-zinc-600">|</span>
          <span className="text-zinc-500">{diagram.hotspots.length} identified parts</span>
        </div>
      </div>
    </div>
  );
};

// 3D Model Viewer Component
export const ModelViewer3D = ({ modelUrl, partName, partNumber }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [viewMode, setViewMode] = useState('3d'); // '3d' or 'exploded'

  // Use a placeholder model if none provided
  const modelSrc = modelUrl || "https://modelviewer.dev/shared-assets/models/Astronaut.glb";

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-zinc-800 flex items-center justify-between">
        <div>
          <h3 className="font-heading text-sm text-yellow-500">3D PART VIEW</h3>
          <p className="text-xs text-zinc-500">{partName || "Part Model"}</p>
        </div>
        <div className="flex gap-2">
          <Button 
            size="sm" 
            variant={viewMode === '3d' ? 'default' : 'outline'}
            onClick={() => setViewMode('3d')}
            className={viewMode === '3d' ? 'bg-yellow-500 text-black' : ''}
          >
            <Eye className="w-4 h-4 mr-1" /> 3D
          </Button>
          <Button 
            size="sm" 
            variant={viewMode === 'exploded' ? 'default' : 'outline'}
            onClick={() => setViewMode('exploded')}
            className={viewMode === 'exploded' ? 'bg-yellow-500 text-black' : ''}
          >
            <Layers className="w-4 h-4 mr-1" /> Exploded
          </Button>
        </div>
      </div>

      {/* 3D Viewer */}
      <div className="relative" style={{ height: '350px' }}>
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-zinc-900 z-10">
            <div className="text-center">
              <div className="w-8 h-8 border-2 border-yellow-500 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
              <p className="text-xs text-zinc-500">Loading 3D Model...</p>
            </div>
          </div>
        )}
        
        <model-viewer
          src={modelSrc}
          alt={partName || "3D Part Model"}
          camera-controls
          auto-rotate
          shadow-intensity="1"
          exposure="0.8"
          environment-image="neutral"
          style={{ width: '100%', height: '100%', backgroundColor: '#18181b' }}
          onLoad={() => setIsLoading(false)}
        >
          {/* Hotspot annotations */}
          <button 
            className="hotspot" 
            slot="hotspot-1" 
            data-position="0 0.15 0.1" 
            data-normal="0 0 1"
          >
            <div className="bg-yellow-500 text-black text-xs px-2 py-1 rounded">
              {partNumber || "Part #"}
            </div>
          </button>
        </model-viewer>
      </div>

      {/* Controls info */}
      <div className="p-3 border-t border-zinc-800 bg-zinc-950">
        <div className="flex items-center justify-between text-xs text-zinc-500">
          <span>🖱️ Drag to rotate • Scroll to zoom • Right-click to pan</span>
          <Badge className="bg-zinc-800 text-zinc-400">Interactive 3D</Badge>
        </div>
      </div>
    </div>
  );
};

// Part Identification Wizard
export const PartIdentificationWizard = ({ equipment, onPartFound }) => {
  const [step, setStep] = useState(0);
  const [selectedSystem, setSelectedSystem] = useState(null);
  const [selectedLocation, setSelectedLocation] = useState(null);

  const systems = [
    { id: 'engine', name: 'Engine & Powertrain', icon: '⚙️' },
    { id: 'hydraulics', name: 'Hydraulics', icon: '💧' },
    { id: 'undercarriage', name: 'Undercarriage', icon: '🔗' },
    { id: 'electrical', name: 'Electrical', icon: '⚡' },
    { id: 'cooling', name: 'Cooling System', icon: '❄️' },
    { id: 'filters', name: 'Filters & Maintenance', icon: '🔧' },
  ];

  const locations = {
    engine: ['Turbocharger', 'Fuel Injectors', 'Water Pump', 'Oil Pump', 'Starter Motor'],
    hydraulics: ['Main Pump', 'Boom Cylinder', 'Arm Cylinder', 'Bucket Cylinder', 'Control Valve'],
    undercarriage: ['Track Chain', 'Track Rollers', 'Idler', 'Sprocket', 'Final Drive'],
    electrical: ['Alternator', 'Starter', 'Sensors', 'Wiring Harness', 'ECM'],
    cooling: ['Radiator', 'Water Pump', 'Thermostat', 'Fan Clutch', 'Hoses'],
    filters: ['Oil Filter', 'Fuel Filter', 'Air Filter', 'Hydraulic Filter', 'Cab Air Filter'],
  };

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded overflow-hidden">
      <div className="p-4 border-b border-zinc-800">
        <h3 className="font-heading text-lg text-yellow-500">PART IDENTIFICATION WIZARD</h3>
        <p className="text-xs text-zinc-500">Answer questions to find the exact part you need</p>
      </div>

      {/* Progress */}
      <div className="px-4 py-2 bg-zinc-950 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          {[0, 1, 2].map((s) => (
            <div key={s} className="flex items-center">
              <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${step >= s ? 'bg-yellow-500 text-black' : 'bg-zinc-700 text-zinc-400'}`}>
                {s + 1}
              </div>
              {s < 2 && <div className={`w-8 h-0.5 ${step > s ? 'bg-yellow-500' : 'bg-zinc-700'}`} />}
            </div>
          ))}
          <span className="text-xs text-zinc-500 ml-2">
            {step === 0 && "Select System"}
            {step === 1 && "Select Location"}
            {step === 2 && "View Parts"}
          </span>
        </div>
      </div>

      <div className="p-4">
        {/* Step 1: Select System */}
        {step === 0 && (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {systems.map((system) => (
              <button
                key={system.id}
                onClick={() => { setSelectedSystem(system); setStep(1); }}
                className="p-4 bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 hover:border-yellow-500/50 rounded text-left transition-all"
              >
                <span className="text-2xl mb-2 block">{system.icon}</span>
                <span className="font-heading text-sm">{system.name}</span>
              </button>
            ))}
          </div>
        )}

        {/* Step 2: Select Location */}
        {step === 1 && selectedSystem && (
          <div>
            <button onClick={() => setStep(0)} className="text-xs text-yellow-500 mb-4 flex items-center gap-1">
              <ChevronLeft className="w-3 h-3" /> Back to systems
            </button>
            <p className="text-sm text-zinc-400 mb-3">Where on the {selectedSystem.name.toLowerCase()} is the part located?</p>
            <div className="grid grid-cols-2 gap-2">
              {locations[selectedSystem.id]?.map((loc) => (
                <button
                  key={loc}
                  onClick={() => { setSelectedLocation(loc); setStep(2); }}
                  className="p-3 bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 hover:border-yellow-500/50 rounded text-left text-sm transition-all"
                >
                  {loc}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Step 3: Show Parts */}
        {step === 2 && selectedLocation && (
          <div>
            <button onClick={() => setStep(1)} className="text-xs text-yellow-500 mb-4 flex items-center gap-1">
              <ChevronLeft className="w-3 h-3" /> Back to locations
            </button>
            <div className="bg-green-900/20 border border-green-600/30 p-4 rounded mb-4">
              <p className="text-green-500 font-heading text-sm mb-1">✓ PART IDENTIFIED</p>
              <p className="text-sm text-zinc-300">
                Based on your selection: <span className="text-yellow-500 font-bold">{selectedSystem.name} → {selectedLocation}</span>
              </p>
            </div>
            <Button 
              onClick={() => onPartFound?.({ system: selectedSystem.id, location: selectedLocation })}
              className="w-full bg-yellow-500 hover:bg-yellow-600 text-black"
            >
              Search Parts for {selectedLocation}
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

// Exploded View Diagram (SVG-based)
export const ExplodedViewDiagram = ({ assembly = "hydraulic-pump" }) => {
  const [hoveredPart, setHoveredPart] = useState(null);
  const [selectedPart, setSelectedPart] = useState(null);

  // Simplified exploded view parts
  const parts = [
    { id: 1, name: "Housing", x: 150, y: 50, color: "#3b82f6" },
    { id: 2, name: "Piston Assembly", x: 150, y: 120, color: "#ef4444" },
    { id: 3, name: "Seal Kit", x: 150, y: 190, color: "#22c55e" },
    { id: 4, name: "Bearing", x: 80, y: 155, color: "#f59e0b" },
    { id: 5, name: "Shaft", x: 220, y: 155, color: "#8b5cf6" },
    { id: 6, name: "End Cap", x: 150, y: 260, color: "#ec4899" },
  ];

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded overflow-hidden">
      <div className="p-4 border-b border-zinc-800">
        <h3 className="font-heading text-lg text-yellow-500">EXPLODED VIEW</h3>
        <p className="text-xs text-zinc-500">Hover over parts to identify components</p>
      </div>

      <div className="relative p-4" style={{ height: '350px' }}>
        <svg viewBox="0 0 300 300" className="w-full h-full">
          {/* Connection lines */}
          <g stroke="#374151" strokeWidth="1" strokeDasharray="4">
            <line x1="150" y1="70" x2="150" y2="100" />
            <line x1="150" y1="140" x2="150" y2="170" />
            <line x1="150" y1="210" x2="150" y2="240" />
            <line x1="100" y1="155" x2="130" y2="155" />
            <line x1="200" y1="155" x2="170" y2="155" />
          </g>

          {/* Parts */}
          {parts.map((part) => (
            <g 
              key={part.id}
              onMouseEnter={() => setHoveredPart(part)}
              onMouseLeave={() => setHoveredPart(null)}
              onClick={() => setSelectedPart(part)}
              className="cursor-pointer"
            >
              <motion.rect
                x={part.x - 30}
                y={part.y - 15}
                width="60"
                height="30"
                rx="4"
                fill={part.color}
                opacity={hoveredPart?.id === part.id || selectedPart?.id === part.id ? 1 : 0.7}
                animate={{ 
                  scale: hoveredPart?.id === part.id ? 1.1 : 1,
                  y: hoveredPart?.id === part.id ? part.y - 20 : part.y - 15
                }}
                style={{ transformOrigin: 'center' }}
              />
              <text
                x={part.x}
                y={part.y + 4}
                textAnchor="middle"
                className="text-xs fill-white font-bold pointer-events-none"
              >
                {part.id}
              </text>
            </g>
          ))}
        </svg>

        {/* Part info panel */}
        <AnimatePresence>
          {(hoveredPart || selectedPart) && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="absolute right-4 top-4 bg-zinc-800 border border-zinc-700 p-3 rounded shadow-xl"
            >
              <div 
                className="w-4 h-4 rounded mb-2" 
                style={{ backgroundColor: (hoveredPart || selectedPart).color }}
              />
              <p className="font-heading text-sm">{(hoveredPart || selectedPart).name}</p>
              <p className="text-xs text-zinc-500">Part #{(hoveredPart || selectedPart).id}</p>
              <Button size="sm" className="mt-2 w-full bg-yellow-500 text-black text-xs">
                Find This Part
              </Button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Parts legend */}
      <div className="p-4 border-t border-zinc-800 bg-zinc-950">
        <div className="flex flex-wrap gap-2">
          {parts.map((part) => (
            <div 
              key={part.id}
              className="flex items-center gap-1 text-xs cursor-pointer hover:opacity-80"
              onMouseEnter={() => setHoveredPart(part)}
              onMouseLeave={() => setHoveredPart(null)}
            >
              <div className="w-3 h-3 rounded" style={{ backgroundColor: part.color }} />
              <span className="text-zinc-400">{part.id}. {part.name}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default { EquipmentDiagram, ModelViewer3D, PartIdentificationWizard, ExplodedViewDiagram };
