from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth
from database import connect_db, close_db

app = FastAPI(title="WMINTELLIOPS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

@app.on_event("startup")
async def startup():
    await connect_db()

@app.on_event("shutdown")
async def shutdown():
    await close_db()

@app.get("/")
async def root():
    return {"message": "WMINTELLIOPS API is running", "status": "operational"}
