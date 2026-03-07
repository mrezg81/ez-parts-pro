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

app = FastAPI(title="EzParts API - Heavy Machinery & Diesel", version="3.0")
api_router = APIRouter(prefix="/api")


# ============== MODELS ==============

class Part(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    part_number: str
    category: str
    type: str  # OEM or Aftermarket
    brand: str  # CAT, Komatsu, Case, Cummins, etc.
    price: float
    supplier: str
    supplier_location: str
    description: str
    specifications: dict = {}
    compatibility: List[str] = []  # Equipment models
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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Equipment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    year: int
    make: str  # CAT, Komatsu, Case, John Deere, etc.
    model: str
    serial_number: Optional[str] = None
    engine: Optional[str] = None  # Cummins, CAT, etc.
    nickname: Optional[str] = None
    hours: Optional[int] = None
    equipment_type: str  # Excavator, Loader, Dozer, Generator, etc.
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
    brands: List[str] = []  # CAT, Komatsu, etc.
    rating: float = 4.5
    trust_score: int = 85
    avg_shipping_days: float = 3.5
    return_policy: str = "30 days"
    contact: str = ""
    website: str = ""
    dealer_type: str = "Authorized"  # Authorized, Independent, Aftermarket


# ============== INITIALIZE HEAVY MACHINERY DATA ==============

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
            "supplier": "Caterpillar Dealer - Thompson Machinery",
            "supplier_location": "Nashville, TN",
            "description": "Genuine CAT main hydraulic pump for 320 series excavators. Factory-tested to OEM specifications. Critical for hydraulic system performance.",
            "specifications": {"flow_rate": "125 GPM", "pressure": "5000 PSI", "type": "Variable Displacement", "weight": "145 lbs"},
            "compatibility": ["CAT 320D", "CAT 320E", "CAT 320F", "CAT 323F"],
            "in_stock": True,
            "install_difficulty": 4,
            "install_time": "6-8 hours",
            "warranty": "12 Months / 2000 Hours",
            "oem_cross_ref": None,
            "aftermarket_alts": ["REMAN-259-0815", "HPUMP-320-AFT"],
            "avg_rating": 4.9,
            "review_count": 234,
            "weight_lbs": 145,
            "lead_time_days": 2
        },
        {
            "id": str(uuid.uuid4()),
            "name": "CAT Undercarriage Track Chain",
            "part_number": "6Y-6145",
            "category": "Undercarriage",
            "type": "OEM",
            "brand": "Caterpillar",
            "price": 8750.00,
            "supplier": "Caterpillar Dealer - Toromont CAT",
            "supplier_location": "Houston, TX",
            "description": "Genuine CAT sealed and lubricated track chain for D6 dozers. Extended service life with factory greasing. Includes master links.",
            "specifications": {"links": "44", "pitch": "8.5 inches", "type": "Sealed & Lubricated", "bushing": "Rotating"},
            "compatibility": ["CAT D6N", "CAT D6R", "CAT D6T", "CAT D6K2"],
            "in_stock": True,
            "install_difficulty": 5,
            "install_time": "8-12 hours",
            "warranty": "24 Months / 4000 Hours",
            "oem_cross_ref": None,
            "aftermarket_alts": ["ITR-D6-CHAIN", "BERCO-D6-TC"],
            "avg_rating": 4.8,
            "review_count": 567,
            "weight_lbs": 2850,
            "lead_time_days": 5
        },
        {
            "id": str(uuid.uuid4()),
            "name": "CAT Fuel Injector - C15 Engine",
            "part_number": "253-0616",
            "category": "Engine",
            "type": "OEM",
            "brand": "Caterpillar",
            "price": 1299.99,
            "supplier": "H.O. Penn Machinery",
            "supplier_location": "Bronx, NY",
            "description": "Genuine CAT HEUI fuel injector for C15 engines. Precision-engineered for optimal fuel atomization and emissions compliance.",
            "specifications": {"type": "HEUI", "pressure": "30000 PSI", "flow_rate": "Variable", "emissions": "EPA Tier 4"},
            "compatibility": ["CAT C15 ACERT", "CAT C15 MXS", "CAT 777F", "CAT 785D"],
            "in_stock": True,
            "install_difficulty": 4,
            "install_time": "3-4 hours per injector",
            "warranty": "12 Months",
            "oem_cross_ref": None,
            "aftermarket_alts": ["REMAN-253-0616", "DPH-C15-INJ"],
            "avg_rating": 4.7,
            "review_count": 892,
            "weight_lbs": 8.5,
            "lead_time_days": 1
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
            "description": "Genuine Komatsu final drive motor for PC200 series excavators. Complete assembly with planetary gears and travel motor.",
            "specifications": {"ratio": "52.7:1", "torque": "45000 Nm", "speed": "4.5 km/h", "oil_capacity": "6.5L"},
            "compatibility": ["Komatsu PC200-8", "Komatsu PC210-8", "Komatsu PC220-8"],
            "in_stock": True,
            "install_difficulty": 5,
            "install_time": "10-14 hours",
            "warranty": "18 Months / 3000 Hours",
            "oem_cross_ref": None,
            "aftermarket_alts": ["HYDX-PC200-FD", "TONG-21Y27"],
            "avg_rating": 4.8,
            "review_count": 345,
            "weight_lbs": 1650,
            "lead_time_days": 7
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Komatsu Hydraulic Cylinder Seal Kit",
            "part_number": "707-99-47790",
            "category": "Hydraulics",
            "type": "OEM",
            "brand": "Komatsu",
            "price": 289.99,
            "supplier": "Komatsu Parts Direct",
            "supplier_location": "Peoria, IL",
            "description": "Complete seal kit for boom cylinder on PC300 series. Includes all O-rings, wipers, and piston seals. NOK quality seals.",
            "specifications": {"cylinder_bore": "140mm", "rod_diameter": "100mm", "seal_material": "Polyurethane/NBR"},
            "compatibility": ["Komatsu PC300-7", "Komatsu PC300-8", "Komatsu PC350-8"],
            "in_stock": True,
            "install_difficulty": 3,
            "install_time": "4-6 hours",
            "warranty": "6 Months",
            "oem_cross_ref": None,
            "aftermarket_alts": ["NOK-PC300-BOOM", "TPSC-707-99"],
            "avg_rating": 4.6,
            "review_count": 1234,
            "weight_lbs": 2.5,
            "lead_time_days": 1
        },
        # CASE PARTS
        {
            "id": str(uuid.uuid4()),
            "name": "Case Loader Bucket Teeth Set",
            "part_number": "87713814",
            "category": "Ground Engaging",
            "type": "OEM",
            "brand": "Case",
            "price": 459.99,
            "supplier": "Titan Machinery",
            "supplier_location": "Fargo, ND",
            "description": "Set of 5 genuine Case bucket teeth for 621G wheel loader. Heavy-duty design for rock and hard material applications.",
            "specifications": {"quantity": "5 teeth", "type": "Tiger", "material": "Alloy Steel", "hardness": "500 BHN"},
            "compatibility": ["Case 621G", "Case 721G", "Case 821G", "Case 921G"],
            "in_stock": True,
            "install_difficulty": 2,
            "install_time": "1-2 hours",
            "warranty": "6 Months",
            "oem_cross_ref": None,
            "aftermarket_alts": ["ESCO-621-TEETH", "MTG-CASE-5PK"],
            "avg_rating": 4.5,
            "review_count": 678,
            "weight_lbs": 45,
            "lead_time_days": 2
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Case Hydraulic Filter Element",
            "part_number": "84255607",
            "category": "Filters",
            "type": "OEM",
            "brand": "Case",
            "price": 89.99,
            "supplier": "CNH Parts Store",
            "supplier_location": "Racine, WI",
            "description": "Genuine CNH hydraulic return filter for Case excavators. 10-micron filtration for system protection.",
            "specifications": {"micron_rating": "10", "type": "Return Line", "media": "Synthetic", "collapse_pressure": "300 PSI"},
            "compatibility": ["Case CX210D", "Case CX250D", "Case CX300D", "Case CX350D"],
            "in_stock": True,
            "install_difficulty": 1,
            "install_time": "30 minutes",
            "warranty": "90 Days",
            "oem_cross_ref": None,
            "aftermarket_alts": ["DONALDSON-P573481", "BALDWIN-BT9440"],
            "avg_rating": 4.7,
            "review_count": 2345,
            "weight_lbs": 3.2,
            "lead_time_days": 1
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
            "description": "Genuine Cummins Holset turbocharger for QSX15 engines. Variable geometry design for optimal boost across RPM range.",
            "specifications": {"type": "VGT", "max_boost": "45 PSI", "turbine": "80mm", "compressor": "88mm"},
            "compatibility": ["Cummins QSX15", "Komatsu SAA6D140E", "CAT 785C (Cummins)", "Hitachi EX1200-6"],
            "in_stock": True,
            "install_difficulty": 4,
            "install_time": "5-7 hours",
            "warranty": "24 Months",
            "oem_cross_ref": None,
            "aftermarket_alts": ["HOLSET-HE500VG", "BW-S480-QSX"],
            "avg_rating": 4.9,
            "review_count": 567,
            "weight_lbs": 85,
            "lead_time_days": 3
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Cummins Water Pump Assembly",
            "part_number": "4089908",
            "category": "Cooling",
            "type": "OEM",
            "brand": "Cummins",
            "price": 649.99,
            "supplier": "Diesel Parts Direct",
            "supplier_location": "Atlanta, GA",
            "description": "Genuine Cummins water pump for ISX engines. Includes gaskets and hardware. High-flow design for heavy-duty cooling.",
            "specifications": {"flow_rate": "200 GPM", "impeller": "Cast Iron", "bearing": "Double Row", "seal": "Ceramic"},
            "compatibility": ["Cummins ISX12", "Cummins ISX15", "Cummins X15"],
            "in_stock": True,
            "install_difficulty": 3,
            "install_time": "3-4 hours",
            "warranty": "12 Months",
            "oem_cross_ref": None,
            "aftermarket_alts": ["GATES-45066", "PAI-681813"],
            "avg_rating": 4.6,
            "review_count": 1456,
            "weight_lbs": 32,
            "lead_time_days": 1
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Cummins Injector Overhaul Kit",
            "part_number": "4352289",
            "category": "Engine",
            "type": "OEM",
            "brand": "Cummins",
            "price": 2199.99,
            "supplier": "Power Train Components",
            "supplier_location": "Indianapolis, IN",
            "description": "Complete 6-injector overhaul kit for ISX15 engines. Includes injectors, cups, tubes, and all gaskets. Fleetguard quality.",
            "specifications": {"quantity": "6 injectors", "type": "Common Rail", "pressure": "36000 PSI", "includes": "Cups, tubes, gaskets"},
            "compatibility": ["Cummins ISX15 2013-2020", "Cummins X15 2017+"],
            "in_stock": True,
            "install_difficulty": 5,
            "install_time": "12-16 hours",
            "warranty": "24 Months / Unlimited Miles",
            "oem_cross_ref": None,
            "aftermarket_alts": ["BOSCH-ISX-6PK", "DELPHI-ISX-KIT"],
            "avg_rating": 4.8,
            "review_count": 234,
            "weight_lbs": 28,
            "lead_time_days": 2
        },
        # AFTERMARKET OPTIONS
        {
            "id": str(uuid.uuid4()),
            "name": "Aftermarket Excavator Track Rollers",
            "part_number": "ITR-PC200-LR",
            "category": "Undercarriage",
            "type": "Aftermarket",
            "brand": "ITR America",
            "price": 185.00,
            "supplier": "Undercarriage USA",
            "supplier_location": "Miami, FL",
            "description": "Heavy-duty aftermarket lower track roller. Compatible with multiple brands. Lifetime-lubricated sealed design.",
            "specifications": {"type": "Single Flange", "bearing": "Tapered Roller", "seal": "Duo-Cone", "hardness": "58 HRC"},
            "compatibility": ["Komatsu PC200", "CAT 320", "Hitachi ZX200", "Kobelco SK200"],
            "in_stock": True,
            "install_difficulty": 2,
            "install_time": "1 hour per roller",
            "warranty": "18 Months",
            "oem_cross_ref": "20Y-30-00014",
            "aftermarket_alts": [],
            "avg_rating": 4.4,
            "review_count": 2341,
            "weight_lbs": 75,
            "lead_time_days": 1
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Heavy Duty Air Filter - Universal",
            "part_number": "DBA-5220",
            "category": "Filters",
            "type": "Aftermarket",
            "brand": "Donaldson",
            "price": 129.99,
            "supplier": "FleetFilter",
            "supplier_location": "Dallas, TX",
            "description": "Donaldson PowerCore air filter for heavy equipment. Fits CAT, Komatsu, and Case applications. Easy serviceability.",
            "specifications": {"type": "Primary", "media": "PowerCore", "efficiency": "99.99%", "restriction": "Low"},
            "compatibility": ["CAT 320D/E/F", "Komatsu PC200-8", "Case CX210D", "John Deere 210G"],
            "in_stock": True,
            "install_difficulty": 1,
            "install_time": "15 minutes",
            "warranty": "12 Months",
            "oem_cross_ref": "1106326",
            "aftermarket_alts": [],
            "avg_rating": 4.7,
            "review_count": 4521,
            "weight_lbs": 12,
            "lead_time_days": 1
        }
    ]
    
    for part in sample_parts:
        part['created_at'] = datetime.now(timezone.utc).isoformat()
        await db.parts.insert_one(part)
    
    # Heavy Equipment Suppliers
    sample_suppliers = [
        {"id": str(uuid.uuid4()), "name": "Thompson Machinery (CAT)", "location": "Nashville", "state": "TN", 
         "specialties": ["Excavators", "Dozers", "Loaders", "Mining Equipment"], "brands": ["Caterpillar"],
         "rating": 4.8, "trust_score": 95, "avg_shipping_days": 2.0, "return_policy": "30 days",
         "contact": "1-800-227-8228", "website": "thomcat.com", "dealer_type": "Authorized CAT Dealer"},
        {"id": str(uuid.uuid4()), "name": "SMS Equipment", "location": "Denver", "state": "CO", 
         "specialties": ["Excavators", "Mining", "Forestry"], "brands": ["Komatsu", "Hitachi"],
         "rating": 4.7, "trust_score": 92, "avg_shipping_days": 3.0, "return_policy": "30 days",
         "contact": "1-800-762-7866", "website": "smsequipment.com", "dealer_type": "Authorized Komatsu Dealer"},
        {"id": str(uuid.uuid4()), "name": "Titan Machinery", "location": "Fargo", "state": "ND", 
         "specialties": ["Construction", "Agriculture", "Parts"], "brands": ["Case", "Case IH", "CNH"],
         "rating": 4.6, "trust_score": 90, "avg_shipping_days": 2.5, "return_policy": "45 days",
         "contact": "1-888-511-7878", "website": "titanmachinery.com", "dealer_type": "Authorized Case Dealer"},
        {"id": str(uuid.uuid4()), "name": "Cummins Sales & Service", "location": "Columbus", "state": "IN", 
         "specialties": ["Diesel Engines", "Generators", "Turbochargers"], "brands": ["Cummins", "Fleetguard"],
         "rating": 4.9, "trust_score": 98, "avg_shipping_days": 1.5, "return_policy": "30 days",
         "contact": "1-800-286-6467", "website": "cummins.com", "dealer_type": "Factory Direct"},
        {"id": str(uuid.uuid4()), "name": "Undercarriage USA", "location": "Miami", "state": "FL", 
         "specialties": ["Tracks", "Rollers", "Idlers", "Sprockets"], "brands": ["ITR", "Berco", "Multi-Brand"],
         "rating": 4.5, "trust_score": 88, "avg_shipping_days": 3.5, "return_policy": "60 days",
         "contact": "1-888-778-2257", "website": "undercarriageusa.com", "dealer_type": "Aftermarket Specialist"},
        {"id": str(uuid.uuid4()), "name": "Diesel Parts Direct", "location": "Atlanta", "state": "GA", 
         "specialties": ["Engine Parts", "Fuel Systems", "Cooling"], "brands": ["Cummins", "CAT", "Detroit"],
         "rating": 4.6, "trust_score": 89, "avg_shipping_days": 2.0, "return_policy": "30 days",
         "contact": "1-855-347-7278", "website": "dieselpartsdirect.com", "dealer_type": "Multi-Brand Distributor"},
    ]
    
    for supplier in sample_suppliers:
        await db.suppliers.insert_one(supplier)
    
    # Sample equipment
    sample_equipment = [
        {"id": str(uuid.uuid4()), "year": 2019, "make": "Caterpillar", "model": "320F L", 
         "serial_number": "ZCW00234", "engine": "CAT C4.4 ACERT", "nickname": "Big Yellow", 
         "hours": 4500, "equipment_type": "Excavator", "created_at": datetime.now(timezone.utc).isoformat()},
        {"id": str(uuid.uuid4()), "year": 2021, "make": "Komatsu", "model": "PC210LC-11", 
         "serial_number": "K75123", "engine": "Komatsu SAA6D107E-3", "nickname": "Digger", 
         "hours": 2800, "equipment_type": "Excavator", "created_at": datetime.now(timezone.utc).isoformat()},
        {"id": str(uuid.uuid4()), "year": 2018, "make": "Case", "model": "621G", 
         "serial_number": "NCF123456", "engine": "FPT F4HFE613Y", "nickname": "Loader 1", 
         "hours": 6200, "equipment_type": "Wheel Loader", "created_at": datetime.now(timezone.utc).isoformat()},
    ]
    
    for equipment in sample_equipment:
        await db.garage.insert_one(equipment)


# ============== ROUTES ==============

@api_router.get("/")
async def root():
    return {"message": "EzParts API v3.0 - Heavy Machinery & Diesel Parts", 
            "brands": ["Caterpillar", "Komatsu", "Case", "Cummins"],
            "features": ["AI Assistant", "My Fleet", "Price Comparison"]}


# ---------- PARTS ----------

@api_router.get("/parts", response_model=List[Part])
async def get_parts(
    category: Optional[str] = None,
    type: Optional[str] = None,
    brand: Optional[str] = None,
    search: Optional[str] = None,
    in_stock: Optional[bool] = None,
    equipment_id: Optional[str] = None
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
    
    suppliers = await db.suppliers.find({}, {"_id": 0}).to_list(100)
    
    import random
    prices = []
    base_price = part['price']
    
    for supplier in suppliers:
        variation = random.uniform(0.88, 1.18)
        supplier_price = round(base_price * variation, 2)
        shipping = round(supplier['avg_shipping_days'] * 15, 2)  # Heavy parts = more shipping
        
        prices.append({
            "supplier": supplier['name'],
            "supplier_id": supplier['id'],
            "price": supplier_price,
            "in_stock": random.random() > 0.15,
            "shipping_days": supplier['avg_shipping_days'],
            "shipping_cost": shipping,
            "total_price": round(supplier_price + shipping, 2),
            "trust_score": supplier['trust_score'],
            "website": supplier['website'],
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
        {"id": "filters", "name": "Filters", "icon": "filter", "description": "Air, fuel, hydraulic & oil filters"},
        {"id": "ground-engaging", "name": "Ground Engaging", "icon": "shovel", "description": "Bucket teeth, edges & cutting tools"},
        {"id": "cooling", "name": "Cooling", "icon": "thermometer", "description": "Radiators, water pumps & thermostats"},
        {"id": "electrical", "name": "Electrical", "icon": "zap", "description": "Starters, alternators & sensors"},
    ]
    
    for cat in categories:
        count = await db.parts.count_documents({"category": {"$regex": cat["name"], "$options": "i"}})
        cat["count"] = count
    
    return categories


@api_router.get("/brands")
async def get_brands():
    """Get equipment brands"""
    return [
        {"id": "caterpillar", "name": "Caterpillar", "short": "CAT", "color": "#FFCD00"},
        {"id": "komatsu", "name": "Komatsu", "short": "KOM", "color": "#0066B3"},
        {"id": "case", "name": "Case", "short": "CASE", "color": "#C8102E"},
        {"id": "cummins", "name": "Cummins", "short": "CUM", "color": "#E31937"},
        {"id": "john-deere", "name": "John Deere", "short": "JD", "color": "#367C2B"},
        {"id": "hitachi", "name": "Hitachi", "short": "HIT", "color": "#E60012"},
        {"id": "volvo", "name": "Volvo CE", "short": "VOL", "color": "#003057"},
        {"id": "liebherr", "name": "Liebherr", "short": "LIE", "color": "#FFE600"},
    ]


# ---------- MY FLEET ----------

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


# Backwards compatibility
@api_router.get("/garage")
async def get_garage():
    return await get_fleet()

@api_router.post("/garage")
async def add_to_garage(equipment: EquipmentCreate):
    return await add_equipment(equipment)

@api_router.delete("/garage/{equipment_id}")
async def remove_from_garage(equipment_id: str):
    return await remove_equipment(equipment_id)


# ---------- SUPPLIERS ----------

@api_router.get("/suppliers", response_model=List[Supplier])
async def get_suppliers(brand: Optional[str] = None):
    query = {}
    if brand:
        query["brands"] = {"$regex": brand, "$options": "i"}
    
    suppliers = await db.suppliers.find(query, {"_id": 0}).to_list(100)
    suppliers.sort(key=lambda x: x.get('trust_score', 0), reverse=True)
    return suppliers


# ---------- FAVORITES ----------

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


# ---------- AI CHAT ----------

@api_router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest):
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="AI service not configured")
    
    history = await db.chat_messages.find(
        {"session_id": request.session_id},
        {"_id": 0}
    ).sort("timestamp", 1).to_list(20)
    
    parts_context = await db.parts.find({}, {"_id": 0, "name": 1, "part_number": 1, "category": 1, "type": 1, "brand": 1, "price": 1, "compatibility": 1}).to_list(50)
    
    parts_summary = "\n".join([
        f"- {p['name']} ({p['part_number']}): {p['brand']} {p['type']} for {p['category']}, ${p['price']}"
        for p in parts_context
    ])
    
    equipment_context = ""
    if request.equipment_context:
        equipment_context = f"\n\nUser's Active Equipment: {request.equipment_context.get('year', '')} {request.equipment_context.get('make', '')} {request.equipment_context.get('model', '')} ({request.equipment_context.get('equipment_type', '')}) with {request.equipment_context.get('engine', '')} engine, {request.equipment_context.get('hours', 'unknown')} hours."
    
    system_message = f"""You are EzParts Heavy Equipment Assistant, an expert in heavy machinery and diesel parts for construction, mining, and industrial equipment.

Your expertise covers:
- Caterpillar (CAT) excavators, dozers, loaders, haul trucks
- Komatsu excavators, wheel loaders, mining trucks
- Case construction and agricultural equipment
- Cummins diesel engines (ISX, QSX, B-series, L-series)
- John Deere, Hitachi, Volvo, Liebherr equipment
- Undercarriage components, hydraulics, drivetrain, engine parts

Available parts in database:
{parts_summary}
{equipment_context}

Guidelines:
- Be technical and direct - your users are heavy equipment mechanics and fleet managers
- Always specify OEM vs Aftermarket options and tradeoffs
- Mention part numbers when available
- Warn about common failure modes and symptoms
- Provide estimated repair hours for planning
- Consider equipment age and hours when recommending parts
- Safety is critical - never compromise on safety-related parts"""

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


# ============== APP SETUP ==============

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
    logger.info("EzParts Heavy Machinery API v3.0 started")


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
