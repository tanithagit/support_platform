from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.auth import router as auth_router
from app.routers.organizations import router as org_router
from app.routers.users import router as user_router

app = FastAPI(
    title="Support Platform API",
    description="Multi-tenant Customer Support System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(org_router)
app.include_router(user_router)

@app.get("/")
def root():
    return {"message": "Support Platform API is running 🚀"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}