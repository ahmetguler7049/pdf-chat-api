from fastapi import FastAPI
from app.routers import pdf_router

app = FastAPI()

app.include_router(pdf_router.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the PDF Chat API!"}
