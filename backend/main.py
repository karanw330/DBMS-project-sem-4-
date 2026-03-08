from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

from backend.auth import router as auth_router
from backend.services.plans import router as plans_router
from backend.services.subscriptions import router as subs_router
from backend.services.payments import router as payments_router

app = FastAPI(title="Billing System Prototype")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dbms-project-sem-4.vercel.app",
        "https://dbms-project-sem-4-git-master-karanw330s-projects.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(plans_router, prefix="/api/plans", tags=["Plans"])
app.include_router(subs_router, prefix="/api/subscriptions", tags=["Subscriptions"])
app.include_router(payments_router, prefix="/api/payments", tags=["Payments"])

# Serve Frontend
# Ensure absolute path for robustness
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

