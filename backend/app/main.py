from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.auth import router as auth_router
from app.routers.organizations import router as org_router
from app.routers.users import router as user_router
from app.routers.tickets import router as ticket_router
from app.routers.messages import router as message_router

app = FastAPI(
    title="Support Platform API",
    description="Multi-tenant Customer Support System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(org_router)
app.include_router(user_router)
app.include_router(ticket_router)
app.include_router(message_router)

@app.get("/")
def root():
    return {"message": "Support Platform API is running 🚀"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}