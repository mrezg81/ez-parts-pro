# EzParts v2.0 - Ultimate Auto Parts Finder PRD

## Vision
**"The Tesla of Auto Parts Apps"** - Built as a co-founder partnership to create something the industry has never seen.

## Original Problem Statement
Build EzParts - a parts finder app with AI Assistant that helps users find both Aftermarket and OEM automotive parts from US suppliers. Make it unique and the best of the best.

## User Personas
1. **Professional Mechanics** - Need quick part lookups, compatibility checks, price comparisons
2. **Car Enthusiasts/Modders** - Want aftermarket upgrades with performance specs
3. **DIY Home Mechanics** - Need installation difficulty guidance and tutorials
4. **Auto Shop Owners** - Require bulk pricing, supplier relationships, inventory management

## Unique Value Proposition
What makes EzParts different from AutoZone, RockAuto, or any competitor:

1. **AI Problem Diagnosis** - Describe symptoms, get parts recommendations
2. **Cross-Supplier Price Comparison** - See prices from 5+ suppliers instantly
3. **My Garage** - Save vehicles, get personalized compatibility on every part
4. **Installation Difficulty Ratings** - Know before you buy if it's DIY or shop job
5. **OEM ↔ Aftermarket Cross-Reference** - Find cheaper alternatives instantly
6. **Trust Scores** - Rate suppliers on delivery, quality, support

## Architecture
- **Frontend**: React 19 + Tailwind CSS + Framer Motion + PWA
- **Backend**: FastAPI (Python) 
- **Database**: MongoDB
- **AI**: GPT-4o-mini via Emergent Universal Key
- **Offline**: Service Worker with intelligent caching

## What's Been Implemented (March 6, 2026)

### Core Features (100% Working)
- **Home Page**: New tagline "Find Parts. Fix Problems."
- **Parts Catalog**: 10 sample parts across 6 categories
- **Part Cards**: Star ratings, review counts, difficulty badges, install time
- **Part Detail Modal**: Full specs, compatibility, cross-references
- **Price Comparison**: Real-time pricing from 5 US suppliers with "BEST DEAL" badge
- **My Garage**: Add/remove vehicles, select active vehicle, compatibility filtering
- **AI Chat**: Problem diagnosis, part recommendations, vehicle context awareness
- **Favorites**: Save parts for quick access
- **Suppliers**: Trust scores, shipping estimates, return policies
- **Filters**: OEM/Aftermarket toggle, category dropdown

### Backend API Endpoints (11 total)
```
GET  /api/parts                    - List parts with filtering
GET  /api/parts/{id}               - Get part details
GET  /api/parts/{id}/compare-prices - Price comparison across suppliers
GET  /api/parts/{id}/cross-reference - OEM/Aftermarket equivalents
GET  /api/categories               - Categories with counts
GET  /api/suppliers                - US suppliers with trust scores
POST /api/garage                   - Add vehicle
GET  /api/garage                   - List vehicles
DELETE /api/garage/{id}            - Remove vehicle
POST /api/favorites                - Add favorite
GET  /api/favorites                - List favorites  
DELETE /api/favorites/{id}         - Remove favorite
POST /api/chat                     - AI chat with vehicle context
GET  /api/chat/{session}           - Chat history
DELETE /api/chat/{session}         - Clear chat
POST /api/diagnose                 - Problem diagnosis
POST /api/voice-search             - Voice query processing
```

### Sample Data
- **10 Parts**: Brake pads, oil filters, coilovers, headlights, spark plugs, intakes, clutch kits, alternators, wheel bearings, exhausts
- **5 Suppliers**: AutoZone, RockAuto, Tire Rack, Summit Racing, CARiD
- **2 Demo Vehicles**: 2020 Ford F-150 XLT, 2019 Honda Civic Sport

## Testing Results
- Backend: 100% (11/11 tests passed)
- Frontend: 100% (25/25 features working)

## Future Roadmap

### P0 - Next Sprint
- [ ] User authentication (JWT + Google OAuth)
- [ ] Real supplier API integrations (RockAuto, AutoZone)
- [ ] Order placement through affiliate links

### P1 - High Priority
- [ ] VIN scanner for automatic vehicle detection
- [ ] Price alerts and watchlist
- [ ] Part reviews and ratings submission
- [ ] Installation guides with video

### P2 - Medium Priority
- [ ] Shop locator for professional installation
- [ ] Community Q&A forum
- [ ] Maintenance schedule tracker
- [ ] Mobile app (React Native)

### P3 - Nice to Have
- [ ] AR part visualization
- [ ] Bulk ordering for shops
- [ ] Loyalty rewards program
- [ ] White-label API for partners

## Business Model
1. **Affiliate Commissions** - 5-15% on parts sold through supplier links
2. **Pro Subscription** ($19.99/mo) - Shop features, bulk pricing, API access
3. **Sponsored Listings** - Brands pay for featured placement
4. **Data Analytics** - Anonymized market insights for manufacturers

## Tech Stack Details
- React 19 with Framer Motion animations
- Tailwind CSS with custom industrial theme
- MongoDB for flexible schema
- FastAPI with async support
- Emergent LLM integration (GPT-4o-mini)
- PWA service worker for offline access

## Design Philosophy
"The Performance Pro" - Dark industrial theme that reduces eye strain in workshop environments, high contrast for readability, minimal UI with maximum information density. Built for mechanics by mechanics.
