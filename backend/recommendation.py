from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, util
import json
import os
import re

router = APIRouter()
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

class QueryRequest(BaseModel):
    query: str

def load_data():
    try:
        file_path = os.path.join("data", "shl_assessments.json")
        print(f"Loading JSON from {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"JSON Load Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load data: {str(e)}")

def extract_max_duration(text):
    try:
        match = re.search(r'(\d{1,3})\s*(minutes|min)', text.lower())
        return int(match.group(1)) if match else None
    except Exception as e:
        print(f"Duration Extraction Error: {e}")
        return None

async def recommend_assessments(query: str):
    try:
        print("Received query:", query)
        data = load_data()

        max_duration = extract_max_duration(query)
        print(f"Max duration extracted: {max_duration}")
        if max_duration:
            data = [item for item in data if item.get("duration", 999) <= max_duration]
            print(f"Filtered data length after duration filter: {len(data)}")

        if not data:
            print("No assessments found matching duration filter.")
            raise HTTPException(status_code=404, detail="No matching assessments found.")

        query_embedding = model.encode(query, convert_to_tensor=True)
        print("Query embedding done.")

        descriptions = [item.get("description", "") for item in data]
        description_embeddings = model.encode(descriptions, convert_to_tensor=True)
        print("Embeddings for descriptions done.")

        scores = util.cos_sim(query_embedding, description_embeddings)[0]
        top_indices = scores.argsort(descending=True)[:10]
        print(f"Top indices: {top_indices}")

        results = [data[i] for i in top_indices]
        print("Returning results.")

        return results

    except Exception as e:
        print(f"Server Error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
