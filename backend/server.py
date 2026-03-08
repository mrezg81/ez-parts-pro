from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

app = FastAPI(title="EzParts API - Heavy Equipment, Cranes, Concrete, Mining & Agriculture", version="4.0")
api_router = APIRouter(prefix="/api")


# ============== MODELS ==============

class Part(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    part_number: str
    category: str
    type: str
    brand: str
    price: float
    supplier: str
    supplier_location: str
    description: str
    specifications: dict = {}
    compatibility: List[str] = []
    in_stock: bool = True
    image_url: Optional[str] = None
    install_difficulty: int = 3
    install_time: str = "2-4 hours"
    warranty: str = ""
    oem_cross_ref: Optional[str] = None
    aftermarket_alts: List[str] = []
    avg_rating: float = 4.5
    review_count: int = 0
    weight_lbs: Optional[float] = None
    lead_time_days: int = 1
    equipment_sector: str = "construction"  # construction, crane, concrete, mining, agriculture
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Equipment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    year: int
    make: str
    model: str
    serial_number: Optional[str] = None
    engine: Optional[str] = None
    nickname: Optional[str] = None
    hours: Optional[int] = None
    equipment_type: str
    equipment_sector: str = "construction"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EquipmentCreate(BaseModel):
    year: int
    make: str
    model: str
    serial_number: Optional[str] = None
    engine: Optional[str] = None
    nickname: Optional[str] = None
    hours: Optional[int] = None
    equipment_type: str
    equipment_sector: str = "construction"


class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    role: str
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChatRequest(BaseModel):
    session_id: str
    message: str
    equipment_context: Optional[dict] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    suggested_parts: List[str] = []


class FavoriteCreate(BaseModel):
    part_id: str


class Favorite(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    part_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Supplier(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    location: str
    state: str
    specialties: List[str] = []
    brands: List[str] = []
    rating: float = 4.5
    trust_score: int = 85
    avg_shipping_days: float = 3.5
    return_policy: str = "30 days"
    contact: str = ""
    website: str = ""
    dealer_type: str = "Authorized"
    sectors: List[str] = []  # construction, crane, concrete, mining, agriculture


# ============== INITIALIZE COMPREHENSIVE DATA ==============

async def init_sample_data():
    existing_parts = await db.parts.count_documents({})
    if existing_parts > 0:
        return
    
    sample_parts = [
        # CATERPILLAR PARTS
        {
            "id": str(uuid.uuid4()),
            "name": "CAT Hydraulic Pump - Main",
            "part_number": "259-0815",
            "category": "Hydraulics",
            "type": "OEM",
            "brand": "Caterpillar",
            "price": 4599.99,
            "supplier": "Thompson Machinery",
            "supplier_location": "Nashville, TN",
            "description": "Genuine CAT main hydraulic pump for 320 series excavators. Factory-tested to OEM specifications.",
            "specifications": {"flow_rate": "125 GPM", "pressure": "5000 PSI", "type": "Variable Displacement"},
            "compatibility": ["CAT 320D", "CAT 320E", "CAT 320F", "CAT 323F"],
            "in_stock": True,
            "install_difficulty": 4,
            "install_time": "6-8 hours",
            "warranty": "12 Months / 2000 Hours",
            "avg_rating": 4.9,
            "review_count": 234,
            "weight_lbs": 145,
            "lead_time_days": 2,
            "equipment_sector": "construction"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "CAT Undercarriage Track Chain",
            "part_number": "6Y-6145",
            "category": "Undercarriage",
            "type": "OEM",
            "brand": "Caterpillar",
            "price": 8750.00,
            "supplier": "Toromont CAT",
            "supplier_location": "Houston, TX",
            "description": "Genuine CAT sealed and lubricated track chain for D6 dozers.",
            "specifications": {"links": "44", "pitch": "8.5 inches", "type": "Sealed & Lubricated"},
            "compatibility": ["CAT D6N", "CAT D6R", "CAT D6T"],
            "in_stock": True,
            "install_difficulty": 5,
            "install_time": "8-12 hours",
            "warranty": "24 Months",
            "avg_rating": 4.8,
            "review_count": 567,
            "weight_lbs": 2850,
            "equipment_sector": "construction"
        },
        # KOMATSU PARTS
        {
            "id": str(uuid.uuid4()),
            "name": "Komatsu Final Drive Assembly",
            "part_number": "21Y-27-00102",
            "category": "Drivetrain",
            "type": "OEM",
            "brand": "Komatsu",
            "price": 12500.00,
            "supplier": "SMS Equipment",
            "supplier_location": "Denver, CO",
            "description": "Genuine Komatsu final drive motor for PC200 series excavators.",
            "specifications": {"ratio": "52.7:1", "torque": "45000 Nm", "speed": "4.5 km/h"},
            "compatibility": ["Komatsu PC200-8", "Komatsu PC210-8", "Komatsu PC220-8"],
            "in_stock": True,
            "install_difficulty": 5,
            "install_time": "10-14 hours",
            "warranty": "18 Months",
            "avg_rating": 4.8,
            "review_count": 345,
            "weight_lbs": 1650,
            "equipment_sector": "construction"
        },
        # CUMMINS DIESEL PARTS
        {
            "id": str(uuid.uuid4()),
            "name": "Cummins Turbocharger - QSX15",
            "part_number": "4089746",
            "category": "Engine",
            "type": "OEM",
            "brand": "Cummins",
            "price": 3899.99,
            "supplier": "Cummins Sales & Service",
            "supplier_location": "Columbus, IN",
            "description": "Genuine Cummins Holset turbocharger for QSX15 engines. Variable geometry design.",
            "specifications": {"type": "VGT", "max_boost": "45 PSI", "turbine": "80mm"},
            "compatibility": ["Cummins QSX15", "Komatsu SAA6D140E", "Hitachi EX1200-6"],
            "in_stock": True,
            "install_difficulty": 4,
            "install_time": "5-7 hours",
            "warranty": "24 Months",
            "avg_rating": 4.9,
            "review_count": 567,
            "weight_lbs": 85,
            "equipment_sector": "construction"
        },
        # NATIONAL CRANE PARTS
        {
            "id": str(uuid.uuid4()),
            "name": "National Crane Boom Hoist Winch",
            "part_number": "NC-80114857",
            "category": "Winch & Hoist",
            "type": "OEM",
            "brand": "National Crane",
            "price": 8950.00,
            "supplier": "Shawmut Equipment",
            "supplier_location": "Bloomfield, CT",
            "description": "OEM boom hoist winch assembly for National Crane NBT series. Includes motor and gearbox.",
            "specifications": {"capacity": "18,000 lbs", "line_speed": "250 fpm", "motor": "Hydraulic"},
            "compatibility": ["National NBT30H", "National NBT40", "National NBT45", "National NBT55"],
            "in_stock": True,
            "install_difficulty": 5,
            "install_time": "8-12 hours",
            "warranty": "12 Months",
            "avg_rating": 4.7,
            "review_count": 89,
            "weight_lbs": 450,
            "equipment_sector": "crane"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "National Crane Outrigger Cylinder",
            "part_number": "NC-80108965",
            "category": "Hydraulics",
            "type": "OEM",
            "brand": "National Crane",
            "price": 2450.00,
            "supplier": "Crane Network",
            "supplier_location": "Fort Wayne, IN",
            "description": "Hydraulic outrigger cylinder for National boom trucks. Chrome rod, premium seals.",
            "specifications": {"bore": "4 inches", "stroke": "72 inches", "pressure": "3500 PSI"},
            "compatibility": ["National 500E", "National 600E", "National 800D", "National 900A"],
            "in_stock": True,
            "install_difficulty": 3,
            "install_time": "3-5 hours",
            "warranty": "12 Months",
            "avg_rating": 4.6,
            "review_count": 156,
            "weight_lbs": 185,
            "equipment_sector": "crane"
        },
        # MANITEX CRANE PARTS
        {
            "id": str(uuid.uuid4()),
            "name": "Manitex Swing Bearing",
            "part_number": "MTX-7600219",
            "category": "Swing System",
            "type": "OEM",
            "brand": "Manitex",
            "price": 6750.00,
            "supplier": "Manitex Parts Direct",
            "supplier_location": "Georgetown, TX",
            "description": "OEM swing bearing for Manitex boom trucks. Precision-machined with internal gear.",
            "specifications": {"diameter": "48 inches", "gear": "Internal", "ball_type": "4-Point Contact"},
            "compatibility": ["Manitex 30100C", "Manitex 30112S", "Manitex 35124C", "Manitex 40124S"],
            "in_stock": True,
            "install_difficulty": 5,
            "install_time": "16-24 hours",
            "warranty": "24 Months",
            "avg_rating": 4.8,
            "review_count": 67,
            "weight_lbs": 1200,
            "equipment_sector": "crane"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Manitex Load Moment Indicator",
            "part_number": "MTX-LMI-2500",
            "category": "Safety Systems",
            "type": "OEM",
            "brand": "Manitex",
            "price": 4500.00,
            "supplier": "Crane Parts & Equipment",
            "supplier_location": "Dallas, TX",
            "description": "Complete LMI system for Manitex cranes. Includes sensors, display, and wiring harness.",
            "specifications": {"display": "7-inch Color", "sensors": "Pressure, Angle, Length", "compliance": "OSHA"},
            "compatibility": ["Manitex 26101C", "Manitex 30100C", "Manitex 35124C", "Manitex 50128S"],
            "in_stock": True,
            "install_difficulty": 4,
            "install_time": "6-8 hours",
            "warranty": "12 Months",
            "avg_rating": 4.5,
            "review_count": 43,
            "weight_lbs": 35,
            "equipment_sector": "crane"
        },
        # TEREX CRANE PARTS
        {
            "id": str(uuid.uuid4()),
            "name": "Terex Telescopic Boom Section",
            "part_number": "TX-20247831",
            "category": "Boom Components",
            "type": "OEM",
            "brand": "Terex",
            "price": 18500.00,
            "supplier": "Terex Parts",
            "supplier_location": "Westport, CT",
            "description": "Replacement boom section #3 for Terex RT cranes. High-strength steel construction.",
            "specifications": {"length": "35 feet", "material": "T-1 Steel", "capacity": "Chart Rated"},
            "compatibility": ["Terex RT230", "Terex RT345", "Terex RT555", "Terex RT780"],
            "in_stock": False,
            "install_difficulty": 5,
            "install_time": "24-40 hours",
            "warranty": "24 Months",
            "avg_rating": 4.9,
            "review_count": 28,
            "weight_lbs": 4500,
            "lead_time_days": 21,
            "equipment_sector": "crane"
        },
        # MANITOWOC CRANE PARTS
        {
            "id": str(uuid.uuid4()),
            "name": "Manitowoc Crawler Track Pad",
            "part_number": "MAN-81932456",
            "category": "Undercarriage",
            "type": "OEM",
            "brand": "Manitowoc",
            "price": 1250.00,
            "supplier": "Manitowoc Crane Care",
            "supplier_location": "Manitowoc, WI",
            "description": "OEM crawler track pad for Manitowoc lattice boom cranes. Set of 2 pads.",
            "specifications": {"width": "36 inches", "material": "Hardened Steel", "mounting": "Bolt-On"},
            "compatibility": ["Manitowoc 999", "Manitowoc 2250", "Manitowoc 4100W", "Manitowoc 16000"],
            "in_stock": True,
            "install_difficulty": 2,
            "install_time": "2-3 hours per pad",
            "warranty": "12 Months",
            "avg_rating": 4.7,
            "review_count": 234,
            "weight_lbs": 650,
            "equipment_sector": "crane"
        },
        # SIMON RO / RO STINGER PARTS
        {
            "id": str(uuid.uuid4()),
            "name": "Simon RO Hydraulic Pump",
            "part_number": "SRO-4789523",
            "category": "Hydraulics",
            "type": "OEM",
            "brand": "Simon RO",
            "price": 3200.00,
            "supplier": "Crane Parts USA",
            "supplier_location": "Oklahoma City, OK",
            "description": "Main hydraulic pump for Simon RO/RO Stinger service cranes. Gear type.",
            "specifications": {"flow": "45 GPM", "pressure": "3000 PSI", "type": "Gear Pump"},
            "compatibility": ["Simon RO TC2863", "RO Stinger TC3063", "Simon RO TC4063", "RO Stinger TC5067"],
            "in_stock": True,
            "install_difficulty": 3,
            "install_time": "4-6 hours",
            "warranty": "12 Months",
            "avg_rating": 4.4,
            "review_count": 78,
            "weight_lbs": 65,
            "equipment_sector": "crane"
        },
        # CONCRETE PUMP PARTS
        {
            "id": str(uuid.uuid4()),
            "name": "Schwing Concrete Pump Wear Plate",
            "part_number": "SCH-10063513",
            "category": "Pump Wear Parts",
            "type": "OEM",
            "brand": "Schwing",
            "price": 1850.00,
            "supplier": "Schwing America",
            "supplier_location": "St. Paul, MN",
            "description": "OEM spectacle wear plate for Schwing concrete pumps. Tungsten carbide surface.",
            "specifications": {"material": "Tungsten Carbide", "hardness": "62 HRC", "life": "80,000 cubic yards"},
            "compatibility": ["Schwing S36X", "Schwing S39SX", "Schwing S42SX", "Schwing S45SX"],
            "in_stock": True,
            "install_difficulty": 3,
            "install_time": "2-4 hours",
            "warranty": "6 Months",
            "avg_rating": 4.8,
            "review_count": 312,
            "weight_lbs": 125,
            "equipment_sector": "concrete"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Putzmeister Boom Pipe Assembly",
            "part_number": "PM-241889",
            "category": "Boom Components",
            "type": "OEM",
            "brand": "Putzmeister",
            "price": 2950.00,
            "supplier": "Putzmeister America",
            "supplier_location": "Sturtevant, WI",
            "description": "Hardened steel boom pipe section for Putzmeister concrete boom pumps. 5-inch ID.",
            "specifications": {"diameter": "5 inches", "length": "3 meters", "material": "Hardened Steel"},
            "compatibility": ["Putzmeister M36-4", "Putzmeister M42-5", "Putzmeister M47-5", "Putzmeister M52-5"],
            "in_stock": True,
            "install_difficulty": 4,
            "install_time": "4-6 hours",
            "warranty": "12 Months",
            "avg_rating": 4.7,
            "review_count": 189,
            "weight_lbs": 220,
            "equipment_sector": "concrete"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Concrete Pump S-Valve",
            "part_number": "CP-SVALVE-DN200",
            "category": "Pump Wear Parts",
            "type": "Aftermarket",
            "brand": "ConForms",
            "price": 2100.00,
            "supplier": "Concrete Pump Supply",
            "supplier_location": "Cleveland, OH",
            "description": "Universal S-valve for DN200 concrete pumps. Fits most major brands.",
            "specifications": {"size": "DN200 (8 inch)", "material": "Hardened Steel", "life": "60,000+ yards"},
            "compatibility": ["Schwing", "Putzmeister", "CIFA", "Sermac", "Alliance"],
            "in_stock": True,
            "install_difficulty": 3,
            "install_time": "3-4 hours",
            "warranty": "90 Days",
            "avg_rating": 4.5,
            "review_count": 567,
            "weight_lbs": 280,
            "equipment_sector": "concrete"
        },
        # MIXER TRUCK PARTS
        {
            "id": str(uuid.uuid4()),
            "name": "McNeilus Mixer Drum Roller",
            "part_number": "MCN-1142789",
            "category": "Drum Components",
            "type": "OEM",
            "brand": "McNeilus",
            "price": 850.00,
            "supplier": "McNeilus Parts",
            "supplier_location": "Dodge Center, MN",
            "description": "Front drum support roller for McNeilus mixer trucks. Heavy-duty sealed bearing.",
            "specifications": {"diameter": "12 inches", "bearing": "Sealed Double Row", "capacity": "25,000 lbs"},
            "compatibility": ["McNeilus Standard", "McNeilus Bridgemaster", "McNeilus Revolution"],
            "in_stock": True,
            "install_difficulty": 3,
            "install_time": "2-3 hours",
            "warranty": "12 Months",
            "avg_rating": 4.6,
            "review_count": 423,
            "weight_lbs": 85,
            "equipment_sector": "concrete"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Mixer Truck Hydraulic Motor",
            "part_number": "EATON-74318",
            "category": "Hydraulics",
            "type": "OEM",
            "brand": "Eaton",
            "price": 3200.00,
            "supplier": "Concrete Mixer Parts",
            "supplier_location": "Indianapolis, IN",
            "description": "Eaton hydraulic motor for concrete mixer drum rotation. Fits most mixer brands.",
            "specifications": {"displacement": "24 cu in/rev", "pressure": "4000 PSI", "speed": "250 RPM"},
            "compatibility": ["McNeilus", "Oshkosh", "Terex Advance", "Continental", "Beck"],
            "in_stock": True,
            "install_difficulty": 4,
            "install_time": "4-6 hours",
            "warranty": "12 Months",
            "avg_rating": 4.8,
            "review_count": 234,
            "weight_lbs": 110,
            "equipment_sector": "concrete"
        },
        # MINING EQUIPMENT PARTS
        {
            "id": str(uuid.uuid4()),
            "name": "CAT 793F Haul Truck Brake",
            "part_number": "CAT-3T5867",
            "category": "Brakes",
            "type": "OEM",
            "brand": "Caterpillar",
            "price": 12500.00,
            "supplier": "CAT Mining Parts",
            "supplier_location": "Tucson, AZ",
            "description": "Wet disc brake assembly for CAT 793 series haul trucks. Oil-cooled design.",
            "specifications": {"type": "Wet Disc", "cooling": "Oil Cooled", "discs": "Multiple"},
            "compatibility": ["CAT 793F", "CAT 793D", "CAT 793C"],
            "in_stock": True,
            "install_difficulty": 5,
            "install_time": "8-12 hours",
            "warranty": "12 Months",
            "avg_rating": 4.9,
            "review_count": 67,
            "weight_lbs": 1850,
            "equipment_sector": "mining"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Komatsu 930E Wheel Motor",
            "part_number": "KOM-830E-MOTOR",
            "category": "Drivetrain",
            "type": "OEM",
            "brand": "Komatsu",
            "price": 85000.00,
            "supplier": "Komatsu Mining",
            "supplier_location": "Peoria, IL",
            "description": "Electric wheel motor for Komatsu 930E ultra-class haul truck. AC drive system.",
            "specifications": {"power": "2500 HP", "type": "AC Induction", "cooling": "Air/Oil"},
            "compatibility": ["Komatsu 930E-4", "Komatsu 930E-4SE", "Komatsu 930E-5"],
            "in_stock": False,
            "install_difficulty": 5,
            "install_time": "40-60 hours",
            "warranty": "24 Months",
            "avg_rating": 4.9,
            "review_count": 23,
            "weight_lbs": 18500,
            "lead_time_days": 45,
            "equipment_sector": "mining"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Mining Truck Suspension Cylinder",
            "part_number": "HYD-MT-SUSP-01",
            "category": "Suspension",
            "type": "Aftermarket",
            "brand": "Peerless",
            "price": 8500.00,
            "supplier": "Mining Equipment Parts",
            "supplier_location": "Salt Lake City, UT",
            "description": "Heavy-duty nitrogen-oil suspension cylinder for mining haul trucks.",
            "specifications": {"capacity": "200 tons", "stroke": "18 inches", "type": "Nitrogen-Oil"},
            "compatibility": ["CAT 785", "CAT 789", "Komatsu HD785", "Hitachi EH3500"],
            "in_stock": True,
            "install_difficulty": 4,
            "install_time": "6-8 hours",
            "warranty": "12 Months",
            "avg_rating": 4.5,
            "review_count": 156,
            "weight_lbs": 2200,
            "equipment_sector": "mining"
        },
        # AGRICULTURE EQUIPMENT PARTS
        {
            "id": str(uuid.uuid4()),
            "name": "John Deere Combine Header Gearbox",
            "part_number": "JD-AH169838",
            "category": "Drivetrain",
            "type": "OEM",
            "brand": "John Deere",
            "price": 2850.00,
            "supplier": "John Deere Parts",
            "supplier_location": "Moline, IL",
            "description": "Header drive gearbox for John Deere S-Series combines. Right-angle design.",
            "specifications": {"ratio": "1.47:1", "input_speed": "540 RPM", "lubrication": "Oil Bath"},
            "compatibility": ["John Deere S660", "John Deere S670", "John Deere S680", "John Deere S690"],
            "in_stock": True,
            "install_difficulty": 4,
            "install_time": "4-6 hours",
            "warranty": "12 Months",
            "avg_rating": 4.8,
            "review_count": 189,
            "weight_lbs": 165,
            "equipment_sector": "agriculture"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Case IH Axial-Flow Rotor",
            "part_number": "CASE-87283596",
            "category": "Threshing",
            "type": "OEM",
            "brand": "Case IH",
            "price": 6500.00,
            "supplier": "Case IH Parts",
            "supplier_location": "Racine, WI",
            "description": "Replacement rotor for Case IH Axial-Flow combines. Heavy-duty construction.",
            "specifications": {"length": "106 inches", "diameter": "30 inches", "material": "Hardened Steel"},
            "compatibility": ["Case IH 7240", "Case IH 8240", "Case IH 9240"],
            "in_stock": True,
            "install_difficulty": 5,
            "install_time": "8-12 hours",
            "warranty": "12 Months",
            "avg_rating": 4.7,
            "review_count": 98,
            "weight_lbs": 850,
            "equipment_sector": "agriculture"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "AGCO Fendt Tractor Hydraulic Pump",
            "part_number": "FENDT-G926150010010",
            "category": "Hydraulics",
            "type": "OEM",
            "brand": "Fendt",
            "price": 4200.00,
            "supplier": "AGCO Parts",
            "supplier_location": "Duluth, GA",
            "description": "Variable displacement hydraulic pump for Fendt 900 series tractors.",
            "specifications": {"flow": "110 L/min", "pressure": "200 bar", "type": "Variable Displacement"},
            "compatibility": ["Fendt 930", "Fendt 933", "Fendt 936", "Fendt 939", "Fendt 942"],
            "in_stock": True,
            "install_difficulty": 4,
            "install_time": "5-7 hours",
            "warranty": "12 Months",
            "avg_rating": 4.9,
            "review_count": 67,
            "weight_lbs": 75,
            "equipment_sector": "agriculture"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Grain Cart Auger Flighting",
            "part_number": "AGR-AUG-16-10",
            "category": "Auger Components",
            "type": "Aftermarket",
            "brand": "Convey-All",
            "price": 1200.00,
            "supplier": "Ag Parts Direct",
            "supplier_location": "Omaha, NE",
            "description": "Replacement auger flighting for grain carts. 16-inch diameter, 10-foot section.",
            "specifications": {"diameter": "16 inches", "length": "10 feet", "pitch": "14 inches"},
            "compatibility": ["Brent", "J&M", "Unverferth", "Parker", "Killbros"],
            "in_stock": True,
            "install_difficulty": 3,
            "install_time": "3-4 hours",
            "warranty": "6 Months",
            "avg_rating": 4.4,
            "review_count": 234,
            "weight_lbs": 145,
            "equipment_sector": "agriculture"
        },
    ]
    
    for part in sample_parts:
        part['created_at'] = datetime.now(timezone.utc).isoformat()
        await db.parts.insert_one(part)
    
    # COMPREHENSIVE SUPPLIERS
    sample_suppliers = [
        # Construction
        {"id": str(uuid.uuid4()), "name": "Thompson Machinery (CAT)", "location": "Nashville", "state": "TN", 
         "specialties": ["Excavators", "Dozers", "Loaders"], "brands": ["Caterpillar"],
         "rating": 4.8, "trust_score": 95, "avg_shipping_days": 2.0, "return_policy": "30 days",
         "contact": "1-800-227-8228", "website": "thomcat.com", "dealer_type": "Authorized CAT Dealer",
         "sectors": ["construction", "mining"]},
        {"id": str(uuid.uuid4()), "name": "SMS Equipment", "location": "Denver", "state": "CO", 
         "specialties": ["Excavators", "Mining"], "brands": ["Komatsu", "Hitachi"],
         "rating": 4.7, "trust_score": 92, "avg_shipping_days": 3.0, "return_policy": "30 days",
         "contact": "1-800-762-7866", "website": "smsequipment.com", "dealer_type": "Authorized",
         "sectors": ["construction", "mining"]},
        # Cranes
        {"id": str(uuid.uuid4()), "name": "Shawmut Equipment", "location": "Bloomfield", "state": "CT", 
         "specialties": ["Boom Trucks", "Cranes", "Parts"], "brands": ["National Crane", "Manitex", "Terex"],
         "rating": 4.6, "trust_score": 91, "avg_shipping_days": 3.5, "return_policy": "30 days",
         "contact": "1-800-829-4161", "website": "shawmutequipment.com", "dealer_type": "Authorized",
         "sectors": ["crane"]},
        {"id": str(uuid.uuid4()), "name": "Manitowoc Crane Care", "location": "Manitowoc", "state": "WI", 
         "specialties": ["Crawler Cranes", "Tower Cranes"], "brands": ["Manitowoc", "Grove", "Potain"],
         "rating": 4.9, "trust_score": 97, "avg_shipping_days": 2.5, "return_policy": "45 days",
         "contact": "1-920-684-4410", "website": "manitowoccranes.com", "dealer_type": "Factory Direct",
         "sectors": ["crane"]},
        {"id": str(uuid.uuid4()), "name": "Crane Parts USA", "location": "Oklahoma City", "state": "OK", 
         "specialties": ["Service Cranes", "Boom Trucks"], "brands": ["Simon RO", "RO Stinger", "Elliott"],
         "rating": 4.5, "trust_score": 88, "avg_shipping_days": 4.0, "return_policy": "30 days",
         "contact": "1-800-432-7263", "website": "cranepartsusa.com", "dealer_type": "Aftermarket",
         "sectors": ["crane"]},
        # Concrete
        {"id": str(uuid.uuid4()), "name": "Schwing America", "location": "St. Paul", "state": "MN", 
         "specialties": ["Concrete Pumps", "Wear Parts"], "brands": ["Schwing"],
         "rating": 4.8, "trust_score": 94, "avg_shipping_days": 2.0, "return_policy": "30 days",
         "contact": "1-888-724-9464", "website": "schwing.com", "dealer_type": "Factory Direct",
         "sectors": ["concrete"]},
        {"id": str(uuid.uuid4()), "name": "Concrete Pump Supply", "location": "Cleveland", "state": "OH", 
         "specialties": ["Pump Parts", "Wear Parts", "Pipes"], "brands": ["Schwing", "Putzmeister", "CIFA"],
         "rating": 4.6, "trust_score": 89, "avg_shipping_days": 2.5, "return_policy": "60 days",
         "contact": "1-800-367-7867", "website": "concretepumpsupply.com", "dealer_type": "Aftermarket Specialist",
         "sectors": ["concrete"]},
        # Mining
        {"id": str(uuid.uuid4()), "name": "CAT Mining Parts", "location": "Tucson", "state": "AZ", 
         "specialties": ["Haul Trucks", "Shovels", "Drills"], "brands": ["Caterpillar"],
         "rating": 4.9, "trust_score": 96, "avg_shipping_days": 3.0, "return_policy": "30 days",
         "contact": "1-520-544-4000", "website": "cat.com/mining", "dealer_type": "Factory Direct",
         "sectors": ["mining"]},
        {"id": str(uuid.uuid4()), "name": "Mining Equipment Parts", "location": "Salt Lake City", "state": "UT", 
         "specialties": ["Haul Trucks", "Loaders", "Drills"], "brands": ["CAT", "Komatsu", "Hitachi", "Liebherr"],
         "rating": 4.5, "trust_score": 87, "avg_shipping_days": 4.0, "return_policy": "30 days",
         "contact": "1-801-355-1234", "website": "miningequipmentparts.com", "dealer_type": "Multi-Brand",
         "sectors": ["mining"]},
        # Agriculture
        {"id": str(uuid.uuid4()), "name": "John Deere Parts", "location": "Moline", "state": "IL", 
         "specialties": ["Combines", "Tractors", "Sprayers"], "brands": ["John Deere"],
         "rating": 4.8, "trust_score": 95, "avg_shipping_days": 2.0, "return_policy": "45 days",
         "contact": "1-800-522-7448", "website": "johndeere.com/parts", "dealer_type": "Factory Direct",
         "sectors": ["agriculture"]},
        {"id": str(uuid.uuid4()), "name": "Case IH Parts", "location": "Racine", "state": "WI", 
         "specialties": ["Combines", "Tractors", "Headers"], "brands": ["Case IH", "New Holland"],
         "rating": 4.7, "trust_score": 93, "avg_shipping_days": 2.5, "return_policy": "30 days",
         "contact": "1-877-422-7344", "website": "partstore.caseih.com", "dealer_type": "Factory Direct",
         "sectors": ["agriculture"]},
        {"id": str(uuid.uuid4()), "name": "Ag Parts Direct", "location": "Omaha", "state": "NE", 
         "specialties": ["Augers", "Grain Handling", "Tillage"], "brands": ["Multiple Brands"],
         "rating": 4.5, "trust_score": 88, "avg_shipping_days": 3.0, "return_policy": "30 days",
         "contact": "1-800-555-1234", "website": "agpartsdirect.com", "dealer_type": "Aftermarket",
         "sectors": ["agriculture"]},
        # Diesel
        {"id": str(uuid.uuid4()), "name": "Cummins Sales & Service", "location": "Columbus", "state": "IN", 
         "specialties": ["Diesel Engines", "Generators"], "brands": ["Cummins", "Fleetguard"],
         "rating": 4.9, "trust_score": 98, "avg_shipping_days": 1.5, "return_policy": "30 days",
         "contact": "1-800-286-6467", "website": "cummins.com", "dealer_type": "Factory Direct",
         "sectors": ["construction", "mining", "agriculture", "crane", "concrete"]},
    ]
    
    for supplier in sample_suppliers:
        await db.suppliers.insert_one(supplier)


# ============== ROUTES ==============

@api_router.get("/")
async def root():
    return {
        "message": "EzParts API v4.0 - Complete Heavy Equipment Parts Platform", 
        "sectors": ["Construction", "Cranes", "Concrete", "Mining", "Agriculture"],
        "brands": ["CAT", "Komatsu", "National Crane", "Manitex", "Terex", "Manitowoc", "Simon RO", "Schwing", "John Deere", "Case IH"],
        "features": ["AI Assistant", "My Fleet", "Price Comparison", "3D Diagrams"]
    }


@api_router.get("/parts", response_model=List[Part])
async def get_parts(
    category: Optional[str] = None,
    type: Optional[str] = None,
    brand: Optional[str] = None,
    search: Optional[str] = None,
    in_stock: Optional[bool] = None,
    equipment_id: Optional[str] = None,
    sector: Optional[str] = None
):
    query = {}
    
    if category:
        query["category"] = {"$regex": category, "$options": "i"}
    if type:
        query["type"] = type
    if brand:
        query["brand"] = {"$regex": brand, "$options": "i"}
    if in_stock is not None:
        query["in_stock"] = in_stock
    if sector:
        query["equipment_sector"] = {"$regex": sector, "$options": "i"}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"part_number": {"$regex": search, "$options": "i"}},
            {"brand": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"oem_cross_ref": {"$regex": search, "$options": "i"}}
        ]
    
    if equipment_id:
        equipment = await db.garage.find_one({"id": equipment_id}, {"_id": 0})
        if equipment:
            query["compatibility"] = {"$regex": f"{equipment['make']}.*{equipment['model']}", "$options": "i"}
    
    parts = await db.parts.find(query, {"_id": 0}).to_list(1000)
    
    for part in parts:
        if isinstance(part.get('created_at'), str):
            part['created_at'] = datetime.fromisoformat(part['created_at'].replace('Z', '+00:00'))
    
    return parts


@api_router.get("/parts/{part_id}", response_model=Part)
async def get_part(part_id: str):
    part = await db.parts.find_one({"id": part_id}, {"_id": 0})
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    
    if isinstance(part.get('created_at'), str):
        part['created_at'] = datetime.fromisoformat(part['created_at'].replace('Z', '+00:00'))
    
    return part


@api_router.get("/parts/{part_id}/compare-prices")
async def compare_prices(part_id: str):
    part = await db.parts.find_one({"id": part_id}, {"_id": 0})
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    
    sector = part.get('equipment_sector', 'construction')
    suppliers = await db.suppliers.find({"sectors": {"$in": [sector]}}, {"_id": 0}).to_list(100)
    
    if not suppliers:
        suppliers = await db.suppliers.find({}, {"_id": 0}).to_list(100)
    
    import random
    prices = []
    base_price = part['price']
    
    for supplier in suppliers[:6]:
        variation = random.uniform(0.88, 1.18)
        supplier_price = round(base_price * variation, 2)
        shipping = round(supplier.get('avg_shipping_days', 3) * 15, 2)
        
        prices.append({
            "supplier": supplier['name'],
            "supplier_id": supplier['id'],
            "price": supplier_price,
            "in_stock": random.random() > 0.15,
            "shipping_days": supplier.get('avg_shipping_days', 3),
            "shipping_cost": shipping,
            "total_price": round(supplier_price + shipping, 2),
            "trust_score": supplier.get('trust_score', 85),
            "website": supplier.get('website', ''),
            "dealer_type": supplier.get('dealer_type', 'Authorized')
        })
    
    prices.sort(key=lambda x: x['total_price'])
    
    return {
        "part": {"id": part['id'], "name": part['name'], "part_number": part['part_number'], "brand": part['brand']},
        "prices": prices,
        "best_deal": prices[0] if prices else None
    }


@api_router.get("/categories")
async def get_categories():
    categories = [
        {"id": "engine", "name": "Engine", "icon": "cog", "description": "Injectors, turbos, pumps & more"},
        {"id": "hydraulics", "name": "Hydraulics", "icon": "droplet", "description": "Pumps, cylinders, valves & seals"},
        {"id": "undercarriage", "name": "Undercarriage", "icon": "link", "description": "Tracks, rollers, idlers & sprockets"},
        {"id": "drivetrain", "name": "Drivetrain", "icon": "settings", "description": "Final drives, axles & transmissions"},
        {"id": "boom-components", "name": "Boom Components", "icon": "arrow-up", "description": "Boom sections, pins & bushings"},
        {"id": "winch-hoist", "name": "Winch & Hoist", "icon": "anchor", "description": "Winches, cables & drum assemblies"},
        {"id": "pump-wear", "name": "Pump Wear Parts", "icon": "tool", "description": "Wear plates, S-valves & pipes"},
        {"id": "swing-system", "name": "Swing System", "icon": "refresh", "description": "Swing bearings, motors & gears"},
        {"id": "safety", "name": "Safety Systems", "icon": "shield", "description": "LMI, cameras & warning systems"},
        {"id": "threshing", "name": "Threshing", "icon": "wheat", "description": "Rotors, concaves & sieves"},
    ]
    
    for cat in categories:
        count = await db.parts.count_documents({"category": {"$regex": cat["name"], "$options": "i"}})
        cat["count"] = count
    
    return categories


@api_router.get("/sectors")
async def get_sectors():
    """Get equipment sectors"""
    return [
        {"id": "construction", "name": "Construction", "icon": "hard-hat", "brands": ["Caterpillar", "Komatsu", "Case", "Volvo"]},
        {"id": "crane", "name": "Cranes & Lifting", "icon": "crane", "brands": ["National Crane", "Manitex", "Terex", "Manitowoc", "Simon RO", "RO Stinger"]},
        {"id": "concrete", "name": "Concrete", "icon": "truck", "brands": ["Schwing", "Putzmeister", "McNeilus", "CIFA"]},
        {"id": "mining", "name": "Mining", "icon": "mountain", "brands": ["Caterpillar", "Komatsu", "Hitachi", "Liebherr"]},
        {"id": "agriculture", "name": "Agriculture", "icon": "wheat", "brands": ["John Deere", "Case IH", "Fendt", "AGCO", "New Holland"]},
    ]


@api_router.get("/brands")
async def get_brands():
    """Get all equipment brands"""
    return [
        # Construction
        {"id": "caterpillar", "name": "Caterpillar", "short": "CAT", "color": "#FFCD00", "sector": "construction"},
        {"id": "komatsu", "name": "Komatsu", "short": "KOM", "color": "#0066B3", "sector": "construction"},
        {"id": "case", "name": "Case", "short": "CASE", "color": "#C8102E", "sector": "construction"},
        # Cranes
        {"id": "national-crane", "name": "National Crane", "short": "NAT", "color": "#003087", "sector": "crane"},
        {"id": "manitex", "name": "Manitex", "short": "MTX", "color": "#E31937", "sector": "crane"},
        {"id": "terex", "name": "Terex", "short": "TRX", "color": "#00843D", "sector": "crane"},
        {"id": "manitowoc", "name": "Manitowoc", "short": "MAN", "color": "#C8102E", "sector": "crane"},
        {"id": "simon-ro", "name": "Simon RO", "short": "SRO", "color": "#FF6600", "sector": "crane"},
        {"id": "ro-stinger", "name": "RO Stinger", "short": "ROS", "color": "#FF6600", "sector": "crane"},
        # Concrete
        {"id": "schwing", "name": "Schwing", "short": "SCH", "color": "#E31937", "sector": "concrete"},
        {"id": "putzmeister", "name": "Putzmeister", "short": "PM", "color": "#FFCD00", "sector": "concrete"},
        {"id": "mcneilus", "name": "McNeilus", "short": "MCN", "color": "#003087", "sector": "concrete"},
        # Mining
        {"id": "hitachi", "name": "Hitachi", "short": "HIT", "color": "#E60012", "sector": "mining"},
        {"id": "liebherr", "name": "Liebherr", "short": "LIE", "color": "#FFE600", "sector": "mining"},
        # Agriculture
        {"id": "john-deere", "name": "John Deere", "short": "JD", "color": "#367C2B", "sector": "agriculture"},
        {"id": "case-ih", "name": "Case IH", "short": "CIH", "color": "#C8102E", "sector": "agriculture"},
        {"id": "fendt", "name": "Fendt", "short": "FEN", "color": "#4A7729", "sector": "agriculture"},
        # Diesel
        {"id": "cummins", "name": "Cummins", "short": "CUM", "color": "#E31937", "sector": "diesel"},
    ]


@api_router.get("/fleet")
async def get_fleet():
    equipment = await db.garage.find({}, {"_id": 0}).to_list(100)
    return equipment


@api_router.post("/fleet")
async def add_equipment(equipment: EquipmentCreate):
    equipment_obj = Equipment(**equipment.model_dump())
    doc = equipment_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.garage.insert_one(doc)
    return equipment_obj


@api_router.get("/fleet/{equipment_id}")
async def get_equipment(equipment_id: str):
    equipment = await db.garage.find_one({"id": equipment_id}, {"_id": 0})
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment


@api_router.delete("/fleet/{equipment_id}")
async def remove_equipment(equipment_id: str):
    result = await db.garage.delete_one({"id": equipment_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return {"message": "Equipment removed from fleet"}


@api_router.get("/garage")
async def get_garage():
    return await get_fleet()

@api_router.post("/garage")
async def add_to_garage(equipment: EquipmentCreate):
    return await add_equipment(equipment)

@api_router.delete("/garage/{equipment_id}")
async def remove_from_garage(equipment_id: str):
    return await remove_equipment(equipment_id)


@api_router.get("/suppliers", response_model=List[Supplier])
async def get_suppliers(brand: Optional[str] = None, sector: Optional[str] = None):
    query = {}
    if brand:
        query["brands"] = {"$regex": brand, "$options": "i"}
    if sector:
        query["sectors"] = {"$in": [sector]}
    
    suppliers = await db.suppliers.find(query, {"_id": 0}).to_list(100)
    suppliers.sort(key=lambda x: x.get('trust_score', 0), reverse=True)
    return suppliers


@api_router.post("/favorites", response_model=Favorite)
async def add_favorite(favorite: FavoriteCreate):
    part = await db.parts.find_one({"id": favorite.part_id})
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    
    existing = await db.favorites.find_one({"part_id": favorite.part_id})
    if existing:
        raise HTTPException(status_code=400, detail="Part already in favorites")
    
    fav_obj = Favorite(part_id=favorite.part_id)
    doc = fav_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.favorites.insert_one(doc)
    return fav_obj


@api_router.get("/favorites")
async def get_favorites():
    favorites = await db.favorites.find({}, {"_id": 0}).to_list(100)
    
    result = []
    for fav in favorites:
        part = await db.parts.find_one({"id": fav["part_id"]}, {"_id": 0})
        if part:
            if isinstance(part.get('created_at'), str):
                part['created_at'] = datetime.fromisoformat(part['created_at'].replace('Z', '+00:00'))
            result.append({"favorite_id": fav["id"], "part": part})
    
    return result


@api_router.delete("/favorites/{part_id}")
async def remove_favorite(part_id: str):
    result = await db.favorites.delete_one({"part_id": part_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return {"message": "Removed from favorites"}


@api_router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest):
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="AI service not configured")
    
    history = await db.chat_messages.find(
        {"session_id": request.session_id},
        {"_id": 0}
    ).sort("timestamp", 1).to_list(20)
    
    parts_context = await db.parts.find({}, {"_id": 0, "name": 1, "part_number": 1, "category": 1, "type": 1, "brand": 1, "price": 1, "compatibility": 1, "equipment_sector": 1}).to_list(50)
    
    parts_summary = "\n".join([
        f"- {p['name']} ({p['part_number']}): {p['brand']} {p['type']} for {p.get('equipment_sector', 'general')}, ${p['price']}"
        for p in parts_context
    ])
    
    equipment_context = ""
    if request.equipment_context:
        equipment_context = f"\n\nUser's Active Equipment: {request.equipment_context.get('year', '')} {request.equipment_context.get('make', '')} {request.equipment_context.get('model', '')} ({request.equipment_context.get('equipment_type', '')}) with {request.equipment_context.get('engine', '')} engine, {request.equipment_context.get('hours', 'unknown')} hours."
    
    system_message = f"""You are EzParts Assistant, the most comprehensive heavy equipment parts expert covering ALL sectors:

CONSTRUCTION: CAT, Komatsu, Case, Volvo, Hitachi excavators, dozers, loaders
CRANES: National Crane, Manitex, Terex, Manitowoc, Simon RO, RO Stinger boom trucks and cranes
CONCRETE: Schwing, Putzmeister, McNeilus pump trucks and mixers
MINING: CAT, Komatsu, Hitachi haul trucks and shovels
AGRICULTURE: John Deere, Case IH, Fendt, AGCO combines, tractors, headers

Your expertise includes:
- OEM vs Aftermarket recommendations
- Part cross-references across brands
- Installation difficulty and time estimates
- Safety system compliance (LMI, OSHA requirements)
- Wear part life expectations

Available parts:
{parts_summary}
{equipment_context}

Guidelines:
- Be direct and technical
- Always specify installation difficulty (1-5)
- Mention safety considerations for crane/lifting equipment
- For concrete pumps, ask about yardage pumped for wear part recommendations
- For agriculture, consider crop/season timing for parts availability"""

    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=request.session_id,
        system_message=system_message
    ).with_model("openai", "gpt-4o-mini")
    
    history_text = ""
    if history:
        for msg in history[-10:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_text += f"{role}: {msg['content']}\n"
    
    full_message = f"{history_text}User: {request.message}" if history_text else request.message
    
    try:
        response = await chat.send_message(UserMessage(text=full_message))
        
        user_msg = ChatMessage(session_id=request.session_id, role="user", content=request.message)
        assistant_msg = ChatMessage(session_id=request.session_id, role="assistant", content=response)
        
        user_doc = user_msg.model_dump()
        user_doc['timestamp'] = user_doc['timestamp'].isoformat()
        assistant_doc = assistant_msg.model_dump()
        assistant_doc['timestamp'] = assistant_doc['timestamp'].isoformat()
        
        await db.chat_messages.insert_one(user_doc)
        await db.chat_messages.insert_one(assistant_doc)
        
        suggested_parts = []
        for part in parts_context:
            if part['part_number'].lower() in response.lower() or part['name'].lower() in response.lower():
                suggested_parts.append(part['part_number'])
        
        return ChatResponse(response=response, session_id=request.session_id, suggested_parts=suggested_parts[:3])
    
    except Exception as e:
        logging.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")


@api_router.get("/chat/{session_id}")
async def get_chat_history(session_id: str):
    messages = await db.chat_messages.find(
        {"session_id": session_id},
        {"_id": 0}
    ).sort("timestamp", 1).to_list(100)
    return messages


@api_router.delete("/chat/{session_id}")
async def clear_chat_history(session_id: str):
    await db.chat_messages.delete_many({"session_id": session_id})
    return {"message": "Chat history cleared"}


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@app.on_event("startup")
async def startup_event():
    await init_sample_data()
    logger.info("EzParts API v4.0 started - Construction, Cranes, Concrete, Mining & Agriculture")


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
