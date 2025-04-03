import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.registerUser import router as registerUserRouter
from routers.referral_routes import router as referralRouter
from routers.clan_routes import router as clanRouter

app = FastAPI(title="Clan Saga API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://clansaga.vercel.app", "http://localhost:3000"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(registerUserRouter, prefix="/api/users", tags=["Users"])
app.include_router(referralRouter, prefix="/api/referrals", tags=["Referrals"])
app.include_router(clanRouter, prefix="/api/clans", tags=["Clans"])


@app.get('/')
async def root():
    return {'message': 'Welcome to Clan Saga API'}


@app.get('/api/health')
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)