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
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PartCreate(BaseModel):
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


class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    role: str  # user or assistant
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    response: str
    session_id: str


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
    contact: str = ""
    website: str = ""


# Initialize sample data
async def init_sample_data():
    # Check if parts already exist
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
            "description": "High-performance ceramic brake pads for Ford F-150. Low dust, quiet operation, and excellent stopping power.",
            "specifications": {"material": "Ceramic", "position": "Front", "warranty": "Lifetime"},
            "compatibility": ["Ford F-150 2015-2024", "Ford Expedition 2018-2024"],
            "in_stock": True,
            "image_url": "https://images.pexels.com/photos/4294075/pexels-photo-4294075.jpeg?auto=compress&cs=tinysrgb&w=400"
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
            "description": "Genuine Motorcraft oil filter for Ford vehicles. Factory-spec filtration for maximum engine protection.",
            "specifications": {"type": "Spin-on", "material": "Silicone Anti-Drainback", "micron_rating": "20"},
            "compatibility": ["Ford F-150 2011-2024", "Ford Mustang 2011-2024", "Ford Explorer 2011-2024"],
            "in_stock": True,
            "image_url": "https://images.unsplash.com/photo-1573864698664-4a1fd0c97b46?w=400"
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
            "description": "KW V3 Coilover kit with adjustable damping. Perfect balance of performance and daily drivability.",
            "specifications": {"adjustability": "Compression/Rebound", "lowering_range": "0.8-1.5 inches", "spring_rate": "Variable"},
            "compatibility": ["VW Golf GTI MK7 2015-2021", "VW Golf R MK7 2015-2021", "Audi A3 8V 2015-2020"],
            "in_stock": True,
            "image_url": "https://images.pexels.com/photos/35697332/pexels-photo-35697332.jpeg?auto=compress&cs=tinysrgb&w=400"
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
            "description": "Full LED projector headlight assembly with sequential turn signals. Plug and play installation.",
            "specifications": {"type": "LED Projector", "color_temp": "6000K", "beam_pattern": "DOT Approved"},
            "compatibility": ["Honda Civic 2016-2021 Sedan", "Honda Civic 2017-2021 Hatchback"],
            "in_stock": True,
            "image_url": None
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
            "description": "Set of 4 NGK Iridium IX spark plugs. OEM replacement for improved fuel efficiency and performance.",
            "specifications": {"type": "Iridium", "gap": "0.044 inches", "heat_range": "6"},
            "compatibility": ["Toyota Camry 2012-2024", "Honda Accord 2013-2024", "Nissan Altima 2013-2024"],
            "in_stock": True,
            "image_url": None
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
            "description": "K&N 77 Series cold air intake. Adds up to 18 HP with improved throttle response.",
            "specifications": {"filter_type": "Washable Cotton Gauze", "tube_material": "Polished Aluminum", "hp_gain": "12-18 HP"},
            "compatibility": ["Ford Mustang GT 2018-2024", "Ford Mustang Mach 1 2021-2024"],
            "in_stock": True,
            "image_url": None
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
            "description": "ACT Heavy Duty clutch kit with street disc. Handles up to 400 lb-ft of torque.",
            "specifications": {"disc_type": "Street", "pressure_plate": "Heavy Duty", "torque_capacity": "400 lb-ft"},
            "compatibility": ["Subaru WRX STI 2004-2021", "Subaru WRX 2006-2021"],
            "in_stock": False,
            "image_url": None
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
            "description": "Genuine Denso alternator for Honda Accord. Factory replacement with 2-year warranty.",
            "specifications": {"amperage": "130A", "voltage": "14V", "pulley_type": "Decoupler"},
            "compatibility": ["Honda Accord 2013-2017", "Honda CR-V 2012-2016"],
            "in_stock": True,
            "image_url": None
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
            "description": "Timken front wheel bearing hub assembly. Pre-assembled for easy installation.",
            "specifications": {"position": "Front", "abs_sensor": "Included", "bolt_pattern": "6x139.7mm"},
            "compatibility": ["Chevy Silverado 1500 2014-2018", "GMC Sierra 1500 2014-2018"],
            "in_stock": True,
            "image_url": None
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
            "description": "Borla ATAK cat-back exhaust system. Aggressive sound with maximum flow.",
            "specifications": {"material": "T-304 Stainless", "tip_style": "Quad Round", "sound_level": "Aggressive"},
            "compatibility": ["Chevy Camaro SS 2016-2024", "Chevy Camaro ZL1 2017-2024"],
            "in_stock": True,
            "image_url": None
        }
    ]
    
    for part in sample_parts:
        part['created_at'] = datetime.now(timezone.utc).isoformat()
        await db.parts.insert_one(part)
    
    # Sample suppliers
    sample_suppliers = [
        {"id": str(uuid.uuid4()), "name": "AutoZone", "location": "Memphis", "state": "TN", "specialties": ["Brakes", "Engine", "Electrical"], "rating": 4.5, "contact": "1-800-288-6966", "website": "autozone.com"},
        {"id": str(uuid.uuid4()), "name": "RockAuto", "location": "Madison", "state": "WI", "specialties": ["All Categories"], "rating": 4.7, "contact": "1-866-762-5288", "website": "rockauto.com"},
        {"id": str(uuid.uuid4()), "name": "Tire Rack", "location": "South Bend", "state": "IN", "specialties": ["Suspension", "Wheels", "Tires"], "rating": 4.8, "contact": "1-888-541-1777", "website": "tirerack.com"},
        {"id": str(uuid.uuid4()), "name": "Summit Racing", "location": "Tallmadge", "state": "OH", "specialties": ["Performance", "Engine", "Exhaust"], "rating": 4.6, "contact": "1-800-230-3030", "website": "summitracing.com"},
        {"id": str(uuid.uuid4()), "name": "CARiD", "location": "Cranbury", "state": "NJ", "specialties": ["Electrical", "Body", "Interior"], "rating": 4.4, "contact": "1-800-505-3274", "website": "carid.com"},
    ]
    
    for supplier in sample_suppliers:
        await db.suppliers.insert_one(supplier)


# Routes
@api_router.get("/")
async def root():
    return {"message": "EzParts API - Your Parts Finder"}


@api_router.get("/parts", response_model=List[Part])
async def get_parts(
    category: Optional[str] = None,
    type: Optional[str] = None,
    search: Optional[str] = None,
    in_stock: Optional[bool] = None
):
    query = {}
    
    if category:
        query["category"] = category
    if type:
        query["type"] = type
    if in_stock is not None:
        query["in_stock"] = in_stock
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"part_number": {"$regex": search, "$options": "i"}},
            {"brand": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
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


@api_router.get("/categories")
async def get_categories():
    categories = [
        {"id": "engine", "name": "Engine", "icon": "engine", "count": 0},
        {"id": "brakes", "name": "Brakes", "icon": "disc", "count": 0},
        {"id": "suspension", "name": "Suspension", "icon": "car", "count": 0},
        {"id": "electrical", "name": "Electrical", "icon": "zap", "count": 0},
        {"id": "transmission", "name": "Transmission", "icon": "cog", "count": 0},
        {"id": "exhaust", "name": "Exhaust", "icon": "wind", "count": 0},
    ]
    
    for cat in categories:
        count = await db.parts.count_documents({"category": {"$regex": cat["name"], "$options": "i"}})
        cat["count"] = count
    
    return categories


@api_router.get("/suppliers", response_model=List[Supplier])
async def get_suppliers():
    suppliers = await db.suppliers.find({}, {"_id": 0}).to_list(100)
    return suppliers


# Favorites
@api_router.post("/favorites", response_model=Favorite)
async def add_favorite(favorite: FavoriteCreate):
    # Check if part exists
    part = await db.parts.find_one({"id": favorite.part_id})
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    
    # Check if already favorited
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
    
    # Get full part details for each favorite
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


# AI Chat
@api_router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest):
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="AI service not configured")
    
    # Get existing chat history for context
    history = await db.chat_messages.find(
        {"session_id": request.session_id},
        {"_id": 0}
    ).sort("timestamp", 1).to_list(20)
    
    # Build context from parts database
    parts_context = await db.parts.find({}, {"_id": 0, "name": 1, "part_number": 1, "category": 1, "type": 1, "brand": 1, "price": 1, "compatibility": 1}).to_list(50)
    
    parts_summary = "\n".join([
        f"- {p['name']} ({p['part_number']}): {p['type']} {p['category']} by {p['brand']}, ${p['price']}"
        for p in parts_context
    ])
    
    system_message = f"""You are EzParts Assistant, an expert automotive parts advisor. You help mechanics, car enthusiasts, and DIY repair folks find the right parts for their vehicles.

Your expertise includes:
- OEM (Original Equipment Manufacturer) parts - factory-spec replacements
- Aftermarket parts - performance upgrades and alternatives
- US-based suppliers and their specialties
- Part compatibility and vehicle fitment
- Price comparisons and quality recommendations

Available parts in our database:
{parts_summary}

Guidelines:
- Be concise and technical - these users know their stuff
- Always mention if a part is OEM or Aftermarket
- Suggest alternatives when appropriate
- If you don't have exact info, recommend checking specific suppliers
- Use part numbers when available
- Mention compatibility concerns proactively"""

    # Initialize chat
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=request.session_id,
        system_message=system_message
    ).with_model("openai", "gpt-4o-mini")
    
    # Add history context
    history_text = ""
    if history:
        for msg in history[-10:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_text += f"{role}: {msg['content']}\n"
    
    # Create message with context
    full_message = f"{history_text}User: {request.message}" if history_text else request.message
    
    user_message = UserMessage(text=full_message)
    
    try:
        response = await chat.send_message(user_message)
        
        # Save messages to database
        user_msg = ChatMessage(
            session_id=request.session_id,
            role="user",
            content=request.message
        )
        assistant_msg = ChatMessage(
            session_id=request.session_id,
            role="assistant",
            content=response
        )
        
        user_doc = user_msg.model_dump()
        user_doc['timestamp'] = user_doc['timestamp'].isoformat()
        assistant_doc = assistant_msg.model_dump()
        assistant_doc['timestamp'] = assistant_doc['timestamp'].isoformat()
        
        await db.chat_messages.insert_one(user_doc)
        await db.chat_messages.insert_one(assistant_doc)
        
        return ChatResponse(response=response, session_id=request.session_id)
    
    except Exception as e:
        logging.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")


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


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.on_event("startup")
async def startup_event():
    await init_sample_data()
    logger.info("EzParts API started - Sample data initialized")


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
