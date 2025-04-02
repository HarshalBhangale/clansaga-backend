import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.registerUser import router as registerUserRouter
from routers.redeemCode import router as redeemCodeRouter
from routers.getCode import router as getCodeRouter
from routers.checkReferralCode import router as checkReferralCodeRouter
from routers.clan_routes import router as clanRouter

app = FastAPI(title="Clan Saga API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(registerUserRouter, tags=["User"])
app.include_router(redeemCodeRouter, tags=["Referral"])
app.include_router(getCodeRouter, tags=["Referral"])
app.include_router(checkReferralCodeRouter, tags=["Referral"])
app.include_router(clanRouter, tags=["Clan"])


@app.get('/')
async def root():
    return {'message': 'Welcome to Clan Saga API'}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)