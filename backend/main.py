from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from events.handlers import router as events_router
from users.handlers import router as users_router
from registrations.handlers import router as registrations_router

app = FastAPI(title="Events API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(events_router)
app.include_router(users_router)
app.include_router(registrations_router)


@app.get("/")
def read_root():
    return {"message": "Events API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}



# Lambda handler
handler = Mangum(app)
