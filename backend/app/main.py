from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.routers import states, skus, customers, auth, sales, shipments, analytics, chatbot

app = FastAPI(title="DRNKOO Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(states.router)
app.include_router(skus.router)
app.include_router(customers.router)
app.include_router(sales.router)
app.include_router(shipments.router)
app.include_router(analytics.router)
app.include_router(chatbot.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "DRNKOO Backend"}
