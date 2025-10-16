# 🏠 Belgian Housing AI

AI-powered real estate market analysis for all 581 Belgian municipalities.

## Features
- ✅ Real demographic data from Statbel
- ✅ AI predictions for apartment demand
- ✅ REST API for integrations
- ✅ 50+ municipalities (expandable to 581)

## Quick Start

### On Replit:
1. Import this repository
2. Click "Run"
3. Done! API is live

### API Endpoints:
- `GET /api/health` - Health check
- `GET /api/municipalities` - All municipalities
- `GET /api/predictions/{nis_code}` - AI prediction
- `GET /api/search?q=<query>` - Search
- `GET /api/stats` - Statistics

## Tech Stack
- Python 3.11
- Flask (REST API)
- SQLite (Database)
- Pandas (Data processing)
- Statbel Open Data

## License
Uses Statbel Open Data (CC BY 4.0)
