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

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Emergent LLM Key
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

# Create the main app
app = FastAPI(title="EzParts API", version="2.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# ============== MODELS ==============

class Part(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    part_number: str
    category: str
    type: str  # OEM or Aftermarket
    brand: str
    price: float
    supplier: str
    supplier_location: str
    description: str
    specifications: dict = {}
    compatibility: List[str] = []
    in_stock: bool = True
    image_url: Optional[str] = None
    # New fields for enhanced experience
    install_difficulty: int = 2  # 1-5 scale
    install_time: str = "1-2 hours"
    warranty: str = ""
    oem_cross_ref: Optional[str] = None  # OEM part number this replaces
    aftermarket_alts: List[str] = []  # Alternative aftermarket part numbers
    avg_rating: float = 4.5
    review_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Vehicle(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    year: int
    make: str
    model: str
    trim: Optional[str] = None
    engine: Optional[str] = None
    nickname: Optional[str] = None
    vin: Optional[str] = None
    mileage: Optional[int] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class VehicleCreate(BaseModel):
    year: int
    make: str
    model: str
    trim: Optional[str] = None
    engine: Optional[str] = None
    nickname: Optional[str] = None
    vin: Optional[str] = None
    mileage: Optional[int] = None


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
    vehicle_context: Optional[dict] = None  # Active vehicle for context


class ChatResponse(BaseModel):
    response: str
    session_id: str
    suggested_parts: List[str] = []  # Part IDs AI recommends


class DiagnoseRequest(BaseModel):
    symptoms: str
    vehicle_id: Optional[str] = None


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
    rating: float = 4.5
    trust_score: int = 85  # 0-100 based on delivery, quality, support
    avg_shipping_days: float = 3.5
    return_policy: str = "30 days"
    contact: str = ""
    website: str = ""


class PriceComparison(BaseModel):
    part_id: str
    part_name: str
    part_number: str
    prices: List[dict]  # [{supplier, price, in_stock, shipping_days, total_price}]


# ============== INITIALIZE SAMPLE DATA ==============

async def init_sample_data():
    existing_parts = await db.parts.count_documents({})
    if existing_parts > 0:
        return
    
    sample_parts = [
        {
            "id": str(uuid.uuid4()),
            "name": "Premium Ceramic Brake Pads",
            "part_number": "BP-2024-F150",
            "category": "Brakes",
            "type": "Aftermarket",
            "brand": "StopTech",
            "price": 89.99,
            "supplier": "AutoZone",
            "supplier_location": "Memphis, TN",
            "description": "High-performance ceramic brake pads for Ford F-150. Low dust, quiet operation, and excellent stopping power. Perfect upgrade from stock pads.",
            "specifications": {"material": "Ceramic", "position": "Front", "warranty": "Lifetime", "includes": "Hardware kit"},
            "compatibility": ["Ford F-150 2015-2024", "Ford Expedition 2018-2024", "Lincoln Navigator 2018-2024"],
            "in_stock": True,
            "image_url": "https://images.pexels.com/photos/4294075/pexels-photo-4294075.jpeg?auto=compress&cs=tinysrgb&w=400",
            "install_difficulty": 2,
            "install_time": "45 min - 1 hour",
            "warranty": "Lifetime",
            "oem_cross_ref": "FL3Z-2001-A",
            "aftermarket_alts": ["AK-BP-F150", "WAG-SX1414"],
            "avg_rating": 4.7,
            "review_count": 1243
        },
        {
            "id": str(uuid.uuid4()),
            "name": "OEM Engine Oil Filter",
            "part_number": "FL-500S-OEM",
            "category": "Engine",
            "type": "OEM",
            "brand": "Motorcraft",
            "price": 12.99,
            "supplier": "Ford Parts",
            "supplier_location": "Dearborn, MI",
            "description": "Genuine Motorcraft oil filter for Ford vehicles. Factory-spec filtration for maximum engine protection. Don't trust your engine to anything less.",
            "specifications": {"type": "Spin-on", "material": "Silicone Anti-Drainback", "micron_rating": "20", "flow_rate": "High"},
            "compatibility": ["Ford F-150 2011-2024", "Ford Mustang 2011-2024", "Ford Explorer 2011-2024", "Ford Edge 2011-2024"],
            "in_stock": True,
            "image_url": "https://images.unsplash.com/photo-1573864698664-4a1fd0c97b46?w=400",
            "install_difficulty": 1,
            "install_time": "15-30 min",
            "warranty": "1 Year",
            "oem_cross_ref": None,
            "aftermarket_alts": ["K&N-HP-2010", "FRAM-PH10575", "WIX-51372"],
            "avg_rating": 4.9,
            "review_count": 5672
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Performance Coilover Kit",
            "part_number": "COIL-MK7-GTI",
            "category": "Suspension",
            "type": "Aftermarket",
            "brand": "KW Suspensions",
            "price": 1899.00,
            "supplier": "Tire Rack",
            "supplier_location": "South Bend, IN",
            "description": "KW V3 Coilover kit with adjustable damping. Perfect balance of performance and daily drivability. German engineering at its finest.",
            "specifications": {"adjustability": "Compression/Rebound", "lowering_range": "0.8-1.5 inches", "spring_rate": "Variable", "material": "Stainless Steel"},
            "compatibility": ["VW Golf GTI MK7 2015-2021", "VW Golf R MK7 2015-2021", "Audi A3 8V 2015-2020", "Audi S3 8V 2015-2020"],
            "in_stock": True,
            "image_url": "https://images.pexels.com/photos/35697332/pexels-photo-35697332.jpeg?auto=compress&cs=tinysrgb&w=400",
            "install_difficulty": 4,
            "install_time": "4-6 hours",
            "warranty": "2 Years",
            "oem_cross_ref": "5Q0-413-031-EL",
            "aftermarket_alts": ["BC-BR-TYPE", "BILSTEIN-B16"],
            "avg_rating": 4.8,
            "review_count": 892
        },
        {
            "id": str(uuid.uuid4()),
            "name": "LED Headlight Assembly",
            "part_number": "HL-CIVIC-LED",
            "category": "Electrical",
            "type": "Aftermarket",
            "brand": "Spyder Auto",
            "price": 449.99,
            "supplier": "CARiD",
            "supplier_location": "Cranbury, NJ",
            "description": "Full LED projector headlight assembly with sequential turn signals. Plug and play installation. Transform your Civic's look instantly.",
            "specifications": {"type": "LED Projector", "color_temp": "6000K", "beam_pattern": "DOT Approved", "turn_signal": "Sequential"},
            "compatibility": ["Honda Civic 2016-2021 Sedan", "Honda Civic 2017-2021 Hatchback", "Honda Civic 2017-2021 Coupe"],
            "in_stock": True,
            "image_url": None,
            "install_difficulty": 3,
            "install_time": "2-3 hours",
            "warranty": "1 Year",
            "oem_cross_ref": "33100-TBA-A01",
            "aftermarket_alts": ["ANZO-121522", "DEPO-317-1170"],
            "avg_rating": 4.4,
            "review_count": 567
        },
        {
            "id": str(uuid.uuid4()),
            "name": "OEM Spark Plugs Set",
            "part_number": "SP-IRIDIUM-4",
            "category": "Engine",
            "type": "OEM",
            "brand": "NGK",
            "price": 45.99,
            "supplier": "RockAuto",
            "supplier_location": "Madison, WI",
            "description": "Set of 4 NGK Iridium IX spark plugs. OEM replacement for improved fuel efficiency and performance. Longest-lasting plug on the market.",
            "specifications": {"type": "Iridium", "gap": "0.044 inches", "heat_range": "6", "electrode": "Fine Wire"},
            "compatibility": ["Toyota Camry 2012-2024", "Honda Accord 2013-2024", "Nissan Altima 2013-2024", "Mazda 6 2014-2021"],
            "in_stock": True,
            "image_url": None,
            "install_difficulty": 2,
            "install_time": "30-45 min",
            "warranty": "Limited Lifetime",
            "oem_cross_ref": "90919-01275",
            "aftermarket_alts": ["BOSCH-9603", "DENSO-IK20TT"],
            "avg_rating": 4.9,
            "review_count": 8934
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Cold Air Intake System",
            "part_number": "CAI-MUSTANG-GT",
            "category": "Engine",
            "type": "Aftermarket",
            "brand": "K&N",
            "price": 329.99,
            "supplier": "Summit Racing",
            "supplier_location": "Tallmadge, OH",
            "description": "K&N 77 Series cold air intake. Adds up to 18 HP with improved throttle response. Million-mile limited warranty on filter.",
            "specifications": {"filter_type": "Washable Cotton Gauze", "tube_material": "Polished Aluminum", "hp_gain": "12-18 HP", "torque_gain": "15-20 lb-ft"},
            "compatibility": ["Ford Mustang GT 2018-2024", "Ford Mustang Mach 1 2021-2024", "Ford Mustang Bullitt 2019-2020"],
            "in_stock": True,
            "image_url": None,
            "install_difficulty": 2,
            "install_time": "1-2 hours",
            "warranty": "Million Mile Limited",
            "oem_cross_ref": "JR3Z-9601-A",
            "aftermarket_alts": ["AFE-54-12912", "AIRAID-450-356"],
            "avg_rating": 4.6,
            "review_count": 2341
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Performance Clutch Kit",
            "part_number": "CLU-STI-STAGE2",
            "category": "Transmission",
            "type": "Aftermarket",
            "brand": "ACT",
            "price": 789.00,
            "supplier": "Subimods",
            "supplier_location": "Orlando, FL",
            "description": "ACT Heavy Duty clutch kit with street disc. Handles up to 400 lb-ft of torque. Aggressive but daily drivable.",
            "specifications": {"disc_type": "Street", "pressure_plate": "Heavy Duty", "torque_capacity": "400 lb-ft", "pedal_feel": "Moderate Increase"},
            "compatibility": ["Subaru WRX STI 2004-2021", "Subaru WRX 2006-2021", "Subaru Forester XT 2004-2013"],
            "in_stock": False,
            "image_url": None,
            "install_difficulty": 5,
            "install_time": "6-8 hours",
            "warranty": "1 Year",
            "oem_cross_ref": "30100AA930",
            "aftermarket_alts": ["EXEDY-15803HD", "SPEC-SU333H"],
            "avg_rating": 4.7,
            "review_count": 1456
        },
        {
            "id": str(uuid.uuid4()),
            "name": "OEM Alternator",
            "part_number": "ALT-ACCORD-OEM",
            "category": "Electrical",
            "type": "OEM",
            "brand": "Denso",
            "price": 289.99,
            "supplier": "Honda Parts Now",
            "supplier_location": "Torrance, CA",
            "description": "Genuine Denso alternator for Honda Accord. Factory replacement with 2-year warranty. Tested to OEM specifications.",
            "specifications": {"amperage": "130A", "voltage": "14V", "pulley_type": "Decoupler", "regulator": "Internal"},
            "compatibility": ["Honda Accord 2013-2017", "Honda CR-V 2012-2016", "Honda Odyssey 2011-2017"],
            "in_stock": True,
            "image_url": None,
            "install_difficulty": 3,
            "install_time": "1.5-2.5 hours",
            "warranty": "2 Years",
            "oem_cross_ref": None,
            "aftermarket_alts": ["DB-13977", "TYC-2-11392"],
            "avg_rating": 4.8,
            "review_count": 723
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Wheel Bearing Hub Assembly",
            "part_number": "WHL-SILVERADO-FR",
            "category": "Suspension",
            "type": "Aftermarket",
            "brand": "Timken",
            "price": 189.99,
            "supplier": "O'Reilly Auto Parts",
            "supplier_location": "Springfield, MO",
            "description": "Timken front wheel bearing hub assembly. Pre-assembled for easy installation. OE quality at aftermarket price.",
            "specifications": {"position": "Front", "abs_sensor": "Included", "bolt_pattern": "6x139.7mm", "studs": "6"},
            "compatibility": ["Chevy Silverado 1500 2014-2018", "GMC Sierra 1500 2014-2018", "Chevy Tahoe 2015-2020", "GMC Yukon 2015-2020"],
            "in_stock": True,
            "image_url": None,
            "install_difficulty": 3,
            "install_time": "1.5-2 hours",
            "warranty": "3 Years / 36,000 Miles",
            "oem_cross_ref": "13592067",
            "aftermarket_alts": ["MOOG-515096", "SKF-BR930838"],
            "avg_rating": 4.6,
            "review_count": 3421
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Performance Exhaust System",
            "part_number": "EXH-CAMARO-CB",
            "category": "Exhaust",
            "type": "Aftermarket",
            "brand": "Borla",
            "price": 1499.00,
            "supplier": "American Muscle",
            "supplier_location": "Malvern, PA",
            "description": "Borla ATAK cat-back exhaust system. Aggressive sound with maximum flow. Made in the USA with aircraft-grade stainless.",
            "specifications": {"material": "T-304 Stainless", "tip_style": "Quad Round 4.5\"", "sound_level": "Aggressive", "hp_gain": "8-12 HP"},
            "compatibility": ["Chevy Camaro SS 2016-2024", "Chevy Camaro ZL1 2017-2024", "Chevy Camaro 1LE 2017-2024"],
            "in_stock": True,
            "image_url": None,
            "install_difficulty": 3,
            "install_time": "2-3 hours",
            "warranty": "Million Mile",
            "oem_cross_ref": "84173953",
            "aftermarket_alts": ["CORSA-14478", "MAGNAFLOW-15178"],
            "avg_rating": 4.9,
            "review_count": 1872
        }
    ]
    
    for part in sample_parts:
        part['created_at'] = datetime.now(timezone.utc).isoformat()
        await db.parts.insert_one(part)
    
    # Enhanced suppliers with trust scores
    sample_suppliers = [
        {"id": str(uuid.uuid4()), "name": "AutoZone", "location": "Memphis", "state": "TN", 
         "specialties": ["Brakes", "Engine", "Electrical", "DIY Friendly"], "rating": 4.5,
         "trust_score": 88, "avg_shipping_days": 2.5, "return_policy": "90 days",
         "contact": "1-800-288-6966", "website": "autozone.com"},
        {"id": str(uuid.uuid4()), "name": "RockAuto", "location": "Madison", "state": "WI", 
         "specialties": ["All Categories", "Best Prices", "Huge Selection"], "rating": 4.7,
         "trust_score": 92, "avg_shipping_days": 4.0, "return_policy": "30 days",
         "contact": "1-866-762-5288", "website": "rockauto.com"},
        {"id": str(uuid.uuid4()), "name": "Tire Rack", "location": "South Bend", "state": "IN", 
         "specialties": ["Suspension", "Wheels", "Tires", "Performance"], "rating": 4.8,
         "trust_score": 95, "avg_shipping_days": 2.0, "return_policy": "30 days",
         "contact": "1-888-541-1777", "website": "tirerack.com"},
        {"id": str(uuid.uuid4()), "name": "Summit Racing", "location": "Tallmadge", "state": "OH", 
         "specialties": ["Performance", "Engine", "Exhaust", "Racing"], "rating": 4.6,
         "trust_score": 90, "avg_shipping_days": 3.0, "return_policy": "30 days",
         "contact": "1-800-230-3030", "website": "summitracing.com"},
        {"id": str(uuid.uuid4()), "name": "CARiD", "location": "Cranbury", "state": "NJ", 
         "specialties": ["Electrical", "Body", "Interior", "Lighting"], "rating": 4.4,
         "trust_score": 82, "avg_shipping_days": 5.0, "return_policy": "60 days",
         "contact": "1-800-505-3274", "website": "carid.com"},
    ]
    
    for supplier in sample_suppliers:
        await db.suppliers.insert_one(supplier)
    
    # Sample vehicles for demonstration
    sample_vehicles = [
        {"id": str(uuid.uuid4()), "year": 2020, "make": "Ford", "model": "F-150", 
         "trim": "XLT", "engine": "3.5L V6 EcoBoost", "nickname": "Work Truck", 
         "mileage": 45000, "created_at": datetime.now(timezone.utc).isoformat()},
        {"id": str(uuid.uuid4()), "year": 2019, "make": "Honda", "model": "Civic", 
         "trim": "Sport", "engine": "2.0L I4", "nickname": "Daily Driver", 
         "mileage": 62000, "created_at": datetime.now(timezone.utc).isoformat()},
    ]
    
    for vehicle in sample_vehicles:
        await db.garage.insert_one(vehicle)


# ============== ROUTES ==============

@api_router.get("/")
async def root():
    return {"message": "EzParts API v2.0 - Your Ultimate Parts Finder", "features": ["AI Assistant", "My Garage", "Price Comparison", "Voice Search"]}


# ---------- PARTS ----------

@api_router.get("/parts", response_model=List[Part])
async def get_parts(
    category: Optional[str] = None,
    type: Optional[str] = None,
    search: Optional[str] = None,
    in_stock: Optional[bool] = None,
    vehicle_id: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None
):
    query = {}
    
    if category:
        query["category"] = {"$regex": category, "$options": "i"}
    if type:
        query["type"] = type
    if in_stock is not None:
        query["in_stock"] = in_stock
    if min_price is not None:
        query["price"] = {"$gte": min_price}
    if max_price is not None:
        query.setdefault("price", {})["$lte"] = max_price
    if min_rating is not None:
        query["avg_rating"] = {"$gte": min_rating}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"part_number": {"$regex": search, "$options": "i"}},
            {"brand": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"oem_cross_ref": {"$regex": search, "$options": "i"}}
        ]
    
    # Filter by vehicle compatibility if provided
    if vehicle_id:
        vehicle = await db.garage.find_one({"id": vehicle_id}, {"_id": 0})
        if vehicle:
            vehicle_str = f"{vehicle['make']} {vehicle['model']} {vehicle['year']}"
            query["compatibility"] = {"$regex": f"{vehicle['make']}.*{vehicle['model']}", "$options": "i"}
    
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


@api_router.get("/parts/{part_id}/cross-reference")
async def get_cross_reference(part_id: str):
    """Find OEM and aftermarket equivalents for a part"""
    part = await db.parts.find_one({"id": part_id}, {"_id": 0})
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    
    alternatives = []
    
    # Find by OEM cross reference
    if part.get('oem_cross_ref'):
        oem_parts = await db.parts.find(
            {"$or": [
                {"part_number": part['oem_cross_ref']},
                {"oem_cross_ref": part['oem_cross_ref']}
            ], "id": {"$ne": part_id}},
            {"_id": 0}
        ).to_list(10)
        alternatives.extend(oem_parts)
    
    # Find by aftermarket alternatives
    if part.get('aftermarket_alts'):
        for alt_pn in part['aftermarket_alts']:
            alt_parts = await db.parts.find(
                {"part_number": {"$regex": alt_pn.split('-')[0], "$options": "i"}, "id": {"$ne": part_id}},
                {"_id": 0}
            ).to_list(5)
            alternatives.extend(alt_parts)
    
    return {
        "original_part": part,
        "alternatives": alternatives,
        "oem_reference": part.get('oem_cross_ref'),
        "aftermarket_options": part.get('aftermarket_alts', [])
    }


@api_router.get("/parts/{part_id}/compare-prices")
async def compare_prices(part_id: str):
    """Compare prices across suppliers for a part"""
    part = await db.parts.find_one({"id": part_id}, {"_id": 0})
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    
    suppliers = await db.suppliers.find({}, {"_id": 0}).to_list(100)
    
    # Simulate price variations across suppliers
    import random
    prices = []
    base_price = part['price']
    
    for supplier in suppliers:
        variation = random.uniform(0.85, 1.15)
        supplier_price = round(base_price * variation, 2)
        shipping = round(supplier['avg_shipping_days'] * 2.5, 2)  # Rough shipping estimate
        
        prices.append({
            "supplier": supplier['name'],
            "supplier_id": supplier['id'],
            "price": supplier_price,
            "in_stock": random.random() > 0.2,  # 80% chance in stock
            "shipping_days": supplier['avg_shipping_days'],
            "shipping_cost": shipping,
            "total_price": round(supplier_price + shipping, 2),
            "trust_score": supplier['trust_score'],
            "website": supplier['website']
        })
    
    # Sort by total price
    prices.sort(key=lambda x: x['total_price'])
    
    return {
        "part": {"id": part['id'], "name": part['name'], "part_number": part['part_number']},
        "prices": prices,
        "best_deal": prices[0] if prices else None,
        "price_range": {
            "min": min(p['price'] for p in prices) if prices else 0,
            "max": max(p['price'] for p in prices) if prices else 0
        }
    }


@api_router.get("/categories")
async def get_categories():
    categories = [
        {"id": "engine", "name": "Engine", "icon": "cog", "description": "Filters, intake, spark plugs & more"},
        {"id": "brakes", "name": "Brakes", "icon": "disc", "description": "Pads, rotors, calipers & lines"},
        {"id": "suspension", "name": "Suspension", "icon": "car", "description": "Shocks, struts, springs & arms"},
        {"id": "electrical", "name": "Electrical", "icon": "zap", "description": "Batteries, alternators & lighting"},
        {"id": "transmission", "name": "Transmission", "icon": "cog", "description": "Clutch, fluid & components"},
        {"id": "exhaust", "name": "Exhaust", "icon": "wind", "description": "Headers, cats, mufflers & tips"},
    ]
    
    for cat in categories:
        count = await db.parts.count_documents({"category": {"$regex": cat["name"], "$options": "i"}})
        cat["count"] = count
    
    return categories


# ---------- MY GARAGE ----------

@api_router.get("/garage")
async def get_garage():
    """Get all vehicles in user's garage"""
    vehicles = await db.garage.find({}, {"_id": 0}).to_list(100)
    return vehicles


@api_router.post("/garage", response_model=Vehicle)
async def add_vehicle(vehicle: VehicleCreate):
    """Add a vehicle to the garage"""
    vehicle_obj = Vehicle(**vehicle.model_dump())
    doc = vehicle_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.garage.insert_one(doc)
    return vehicle_obj


@api_router.get("/garage/{vehicle_id}")
async def get_vehicle(vehicle_id: str):
    vehicle = await db.garage.find_one({"id": vehicle_id}, {"_id": 0})
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@api_router.delete("/garage/{vehicle_id}")
async def remove_vehicle(vehicle_id: str):
    result = await db.garage.delete_one({"id": vehicle_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return {"message": "Vehicle removed from garage"}


@api_router.get("/garage/{vehicle_id}/compatible-parts")
async def get_compatible_parts(vehicle_id: str, category: Optional[str] = None):
    """Get all parts compatible with a vehicle"""
    vehicle = await db.garage.find_one({"id": vehicle_id}, {"_id": 0})
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    query = {"compatibility": {"$regex": f"{vehicle['make']}.*{vehicle['model']}", "$options": "i"}}
    if category:
        query["category"] = {"$regex": category, "$options": "i"}
    
    parts = await db.parts.find(query, {"_id": 0}).to_list(100)
    return {
        "vehicle": vehicle,
        "compatible_parts": parts,
        "count": len(parts)
    }


# ---------- SUPPLIERS ----------

@api_router.get("/suppliers", response_model=List[Supplier])
async def get_suppliers(sort_by: Optional[str] = "trust_score"):
    suppliers = await db.suppliers.find({}, {"_id": 0}).to_list(100)
    
    if sort_by == "trust_score":
        suppliers.sort(key=lambda x: x.get('trust_score', 0), reverse=True)
    elif sort_by == "rating":
        suppliers.sort(key=lambda x: x.get('rating', 0), reverse=True)
    elif sort_by == "shipping":
        suppliers.sort(key=lambda x: x.get('avg_shipping_days', 99))
    
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


# ---------- AI CHAT & DIAGNOSIS ----------

@api_router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest):
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="AI service not configured")
    
    history = await db.chat_messages.find(
        {"session_id": request.session_id},
        {"_id": 0}
    ).sort("timestamp", 1).to_list(20)
    
    # Get parts for context
    parts_context = await db.parts.find({}, {"_id": 0, "name": 1, "part_number": 1, "category": 1, "type": 1, "brand": 1, "price": 1, "compatibility": 1, "install_difficulty": 1, "avg_rating": 1}).to_list(50)
    
    parts_summary = "\n".join([
        f"- {p['name']} ({p['part_number']}): {p['type']} {p['category']} by {p['brand']}, ${p['price']}, Rating: {p.get('avg_rating', 'N/A')}/5, Install Difficulty: {p.get('install_difficulty', 'N/A')}/5"
        for p in parts_context
    ])
    
    # Get vehicle context if provided
    vehicle_context = ""
    if request.vehicle_context:
        vehicle_context = f"\n\nUser's Active Vehicle: {request.vehicle_context.get('year', '')} {request.vehicle_context.get('make', '')} {request.vehicle_context.get('model', '')} {request.vehicle_context.get('trim', '')} with {request.vehicle_context.get('engine', '')} engine, {request.vehicle_context.get('mileage', 'unknown')} miles."
    
    system_message = f"""You are EzParts Assistant, the most knowledgeable automotive parts advisor in the industry. You help mechanics, car enthusiasts, and DIYers find the perfect parts.

Your expertise includes:
- OEM vs Aftermarket recommendations with honest pros/cons
- Part compatibility and fitment verification
- Installation difficulty assessment (1=easy DIY, 5=professional only)
- Price-to-value analysis
- Problem diagnosis from symptoms
- Cross-referencing OEM to aftermarket equivalents

Available parts in database:
{parts_summary}
{vehicle_context}

Guidelines:
- Be direct and technical - your users are gear heads
- Always mention installation difficulty level
- Recommend OEM for reliability, aftermarket for performance/value
- If a part is out of stock, suggest alternatives
- Use part numbers when available
- Warn about compatibility issues proactively
- For symptoms, suggest likely causes and parts needed
- If unsure, say so - never guess on safety parts"""

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
    
    user_message = UserMessage(text=full_message)
    
    try:
        response = await chat.send_message(user_message)
        
        # Save messages
        user_msg = ChatMessage(session_id=request.session_id, role="user", content=request.message)
        assistant_msg = ChatMessage(session_id=request.session_id, role="assistant", content=response)
        
        user_doc = user_msg.model_dump()
        user_doc['timestamp'] = user_doc['timestamp'].isoformat()
        assistant_doc = assistant_msg.model_dump()
        assistant_doc['timestamp'] = assistant_doc['timestamp'].isoformat()
        
        await db.chat_messages.insert_one(user_doc)
        await db.chat_messages.insert_one(assistant_doc)
        
        # Extract suggested parts from response (simple keyword matching)
        suggested_parts = []
        for part in parts_context:
            if part['part_number'].lower() in response.lower() or part['name'].lower() in response.lower():
                suggested_parts.append(part['part_number'])
        
        return ChatResponse(response=response, session_id=request.session_id, suggested_parts=suggested_parts[:3])
    
    except Exception as e:
        logging.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")


@api_router.post("/diagnose")
async def diagnose_problem(request: DiagnoseRequest):
    """AI-powered problem diagnosis from symptoms"""
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="AI service not configured")
    
    # Get vehicle info if provided
    vehicle_info = ""
    if request.vehicle_id:
        vehicle = await db.garage.find_one({"id": request.vehicle_id}, {"_id": 0})
        if vehicle:
            vehicle_info = f"Vehicle: {vehicle['year']} {vehicle['make']} {vehicle['model']} {vehicle.get('trim', '')} with {vehicle.get('mileage', 'unknown')} miles"
    
    # Get parts for recommendations
    parts = await db.parts.find({}, {"_id": 0}).to_list(50)
    
    system_message = """You are an expert automotive diagnostician. Analyze symptoms and provide:
1. Most likely cause (with confidence %)
2. Other possible causes to check
3. Recommended parts to fix the issue
4. Estimated repair difficulty (1-5)
5. Whether it's safe to drive

Be direct and technical. Format your response clearly."""
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"diagnose_{uuid.uuid4()}",
        system_message=system_message
    ).with_model("openai", "gpt-4o-mini")
    
    diagnosis_prompt = f"""
{vehicle_info}

Symptoms reported: {request.symptoms}

Available parts in our inventory:
{', '.join([f"{p['name']} ({p['category']})" for p in parts[:20]])}

Provide diagnosis and part recommendations."""
    
    try:
        response = await chat.send_message(UserMessage(text=diagnosis_prompt))
        
        return {
            "symptoms": request.symptoms,
            "vehicle": vehicle_info or "No vehicle specified",
            "diagnosis": response,
            "disclaimer": "This is an AI-assisted diagnosis. Always verify with a qualified mechanic for safety-critical repairs."
        }
    except Exception as e:
        logging.error(f"Diagnosis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/chat/{session_id}")
async def get_chat_history(session_id: str):
    messages = await db.chat_messages.find(
        {"session_id": session_id},
        {"_id": 0}
    ).sort("timestamp", 1).to_list(100)
    
    for msg in messages:
        if isinstance(msg.get('timestamp'), str):
            msg['timestamp'] = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
    
    return messages


@api_router.delete("/chat/{session_id}")
async def clear_chat_history(session_id: str):
    await db.chat_messages.delete_many({"session_id": session_id})
    return {"message": "Chat history cleared"}


# ---------- VOICE SEARCH ----------

@api_router.post("/voice-search")
async def voice_search(query: str):
    """Process voice search query and return parts"""
    # Clean up voice query (remove filler words)
    filler_words = ["um", "uh", "like", "you know", "so", "basically"]
    clean_query = query.lower()
    for word in filler_words:
        clean_query = clean_query.replace(word, "")
    clean_query = " ".join(clean_query.split())  # Remove extra spaces
    
    # Search parts
    parts = await db.parts.find({
        "$or": [
            {"name": {"$regex": clean_query, "$options": "i"}},
            {"part_number": {"$regex": clean_query, "$options": "i"}},
            {"category": {"$regex": clean_query, "$options": "i"}},
            {"brand": {"$regex": clean_query, "$options": "i"}},
            {"compatibility": {"$regex": clean_query, "$options": "i"}}
        ]
    }, {"_id": 0}).to_list(20)
    
    return {
        "original_query": query,
        "processed_query": clean_query,
        "results": parts,
        "count": len(parts)
    }


# ============== APP SETUP ==============

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.on_event("startup")
async def startup_event():
    await init_sample_data()
    logger.info("EzParts API v2.0 started - Enhanced features ready")


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
