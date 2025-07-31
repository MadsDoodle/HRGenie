
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from generate_offer_letter import generate_offer_letter
from fallback_jinja import generate_offer_letter_jinja
from load_employee_metadata import load_employee_metadata
from retriever import retrieve_relevant_chunks


# Initialize app
app = FastAPI(title="Offer Letter Generator API")

# Add CORS middleware to allow frontend to talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for the request body (v2-compatible)
class OfferRequest(BaseModel):
    employee_name: str
    use_jinja: bool = False  # Optional: fallback option for non-GPT generation

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "🎯 Offer Letter Generation API is up and running!"}

# Offer letter generation endpoint
@app.post("/generate-offer-letter")
def generate_offer(request: OfferRequest):
    try:
        if request.use_jinja:
            # Manual fallback using Jinja2
            emp = load_employee_metadata(request.employee_name)
            chunks = retrieve_relevant_chunks(
                f"Generate offer letter for {request.employee_name}", top_k=5
            )
            result = generate_offer_letter_jinja(emp, chunks)
            return {"status": "success", "source": "jinja", "offer_letter": result}
        else:
            # GPT-4o (fallback inside it automatically)
            result = generate_offer_letter(request.employee_name)
            return {"status": "success", "source": "gpt", "offer_letter": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Offer letter generation failed: {str(e)}")
    

##to run the code enter thos in the terminal
# uvicorn api_server:app --reload
# the put a "/docs" on the end of the URL like
# http://127.0.0.1:8000/docs

#also install ngrok to expose the FastAPI local url globally which can then be connected to frontend sites
#run "ngrok http 8000"

#python3 -m http.server 5500
#visit "http://localhost:5500"