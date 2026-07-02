from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import invoices,auth,admin
from .db import Base,engine
from . import models
app = FastAPI()

Base.metadata.create_all(bind=engine)

origins=["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )

app.include_router(invoices.router)
app.include_router(auth.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {"message":"Hello"}