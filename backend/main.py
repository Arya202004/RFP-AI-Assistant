from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import re
from data_utils import extract_text_from_bytes
from llm_utils import analyze_rfp_with_dual_llm

# When deploying on Vercel, we use the /api prefix for all backend routes.
# We set root_path to ensure internal FastAPI routing handles this prefix correctly.
app = FastAPI(root_path="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COMPANY_PROFILE_PATH = os.path.join(BASE_DIR, "company_profile.json")

def load_company_data():
    if os.path.exists(COMPANY_PROFILE_PATH):
        with open(COMPANY_PROFILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

@app.post("/analyze/")
async def analyze(
    rfp_file: UploadFile = File(..., alias="file"), 
    company_file: UploadFile = File(None)
):
    try:
        # 1. Parse RFP
        rfp_content = await rfp_file.read()
        rfp_text = extract_text_from_bytes(rfp_content, rfp_file.filename)
        
        # 2. Determine Company Context
        if company_file:
            company_content = await company_file.read()
            company_text = extract_text_from_bytes(company_content, company_file.filename)
            company_context = company_text
        else:
            # Fallback to static JSON if no file provided
            company_json = load_company_data()
            company_context = json.dumps(company_json, indent=2)
        
        # 3. Perform the Dual-LLM RAG analysis (Gemini -> Mistral fallback)
        result = await analyze_rfp_with_dual_llm(rfp_text, company_context)
        
        # 4. UNIVERSAL SCORE GUARD: Dynamic Hard-cap safety layer
        # Instead of hardcoded keywords, we respect the AI's identified "High" importance items.
        is_strongly_disqualified = False
        
        for item in result.get("checklist", []):
            status = str(item.get("status", "")).lower()
            importance = str(item.get("importance", "")).lower()
            
            # If any HIGH IMPORTANCE requirement is MISSING, trigger hard-cap.
            if importance == "high" and "missing" in status:
                is_strongly_disqualified = True
                break
        
        if is_strongly_disqualified:
            # Force cap and update summary if it's inconsistent
            result["eligibility_score"] = min(result.get("eligibility_score", 0), 45)
            if "disqualified" not in result["summary"].lower():
                result["summary"] = f"CRITICAL REQUIREMENT MISSING: {result['summary']}"
        else:
            # SAFETY RE-CALIBRATION: If the AI found zero mandatory gaps,
            # it shouldn't be failing. We ensure a baseline eligibility score.
            if result.get("eligibility_score", 0) < 50:
                result["eligibility_score"] = 70 
                result["summary"] = f"AUTO-VERIFIED: {result['summary']}"

        # Final safety for filename which is used in some frontend logics
        result["filename"] = rfp_file.filename
        
        return result
    except Exception as e:
        print(f"Error in /analyze/: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/company-profile/")
async def get_company_profile():
    return load_company_data()
