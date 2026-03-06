# EzParts - Auto Parts Finder PRD

## Original Problem Statement
Build EzParts - a parts finder app with AI Assistant that helps users find both Aftermarket and OEM automotive parts from US suppliers. Features include: search parts by name/category, AI chatbot assistant powered by GPT-4o-mini, PWA with offline access, US supplier database.

## User Personas
1. **Auto Mechanics** - Professional mechanics looking for specific parts with compatibility info
2. **Car Enthusiasts** - DIYers upgrading their vehicles with aftermarket parts  
3. **Auto Shop Owners** - Need quick price comparisons from multiple suppliers
4. **Fleet Managers** - Looking for OEM parts for fleet maintenance

## Core Requirements (Static)
- Parts search by name, category, part number
- OEM vs Aftermarket filtering
- US supplier database with ratings
- AI-powered parts assistant
- Favorites/saved parts
- PWA with offline support
- Dark industrial theme for workshop use

## Architecture
- **Frontend**: React 19 + Tailwind CSS + Framer Motion
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **AI**: GPT-4o-mini via Emergent LLM Key
- **PWA**: Service Worker with cache-first strategy

## What's Been Implemented (March 6, 2026)

### MVP Features Completed
- Home page with hero search and category grid
- Parts listing with OEM/Aftermarket filters
- Part detail modals with full specifications
- Favorites add/remove functionality  
- AI Chat Assistant (GPT-4o-mini)
- US Suppliers page with ratings
- PWA service worker for offline access
- Dark industrial theme (red accent color)
- Mobile responsive design

### Backend Endpoints
- GET /api/parts - List all parts with filtering
- GET /api/parts/{id} - Get single part details
- GET /api/categories - Get category list with counts
- GET /api/suppliers - List US suppliers
- POST /api/favorites - Add to favorites
- GET /api/favorites - Get saved parts
- DELETE /api/favorites/{part_id} - Remove favorite
- POST /api/chat - AI chat endpoint
- GET /api/chat/{session_id} - Get chat history
- DELETE /api/chat/{session_id} - Clear chat

### Sample Data
- 10 auto parts across 6 categories
- 5 US suppliers with contact info
- Categories: Engine, Brakes, Suspension, Electrical, Transmission, Exhaust

## Prioritized Backlog

### P0 - Critical (Next Sprint)
- [ ] User authentication (JWT or Google OAuth)
- [ ] Real-time inventory sync with suppliers

### P1 - High Priority
- [ ] Vehicle garage - save user vehicles for compatibility
- [ ] Price alerts for saved parts
- [ ] Order integration with supplier websites

### P2 - Medium Priority
- [ ] Part reviews and ratings
- [ ] Installation guides/videos
- [ ] Comparison tool (side-by-side parts)
- [ ] Push notifications for price drops

### P3 - Nice to Have
- [ ] VIN decoder for automatic vehicle identification
- [ ] AR part visualization
- [ ] Community Q&A forum
- [ ] Mobile app (React Native)

## Next Tasks
1. Implement user authentication
2. Add more parts to database (API integration with RockAuto/AutoZone)
3. Vehicle compatibility checker
4. Implement price comparison view
5. Add part reviews system

## Tech Decisions Log
- Used simple button filters instead of Radix Tabs for reliability
- Chat FAB positioned to avoid Emergent badge overlap
- Service worker caches API responses for offline browsing
- Emergent LLM Key for AI without user API key setup
