from fastapi import FastAPI
from pydantic import BaseModel
from recommendation import recommend_assessments
import uvicorn

app = FastAPI()

class Query(BaseModel):
    query: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the SHL Assessment Recommender API"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/recommend")
async def recommend_endpoint(item: Query):
    recs = await recommend_assessments(item.query)
    return recs

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
