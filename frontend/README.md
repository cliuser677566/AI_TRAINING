# DRINKOO Frontend

This is the Phase 3-7 frontend for DRINKOO SKU management.

## Features

- Login page with non-production default credentials (`admin` / `password`)
- Protected dashboard shell
- State dropdown filter
- Sales by state and SKU performance tables
- Sales ingestion form (ETL input)
- Shipment creation form
- SKU form preview with beverage-size validation

## Run

1. Install dependencies:

```powershell
cd frontend
npm install
```

2. Create `.env`:

```powershell
Copy-Item .env.example .env
```

3. Start dev server:

```powershell
npm run dev
```

Default URL: `http://localhost:5173`

Status page URL: `http://localhost:5173/status`

## Build

```powershell
npm run build
```
