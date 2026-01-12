import os
import json
import re
import google.generativeai as genai
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
GEN_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEN_API_KEY)

# Configure Mistral
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
mistral_client = Mistral(api_key=MISTRAL_API_KEY)

PROMPT_TEMPLATE = """
Analyze the following RFP document against the provided Company Context. 
Identify the actual requirements specified in the RFP and evaluate the company's alignment.

Return the result STRICTLY as a JSON object with the following structure:
{{
  "eligibility_score": <integer from 0-100>,
  "summary": "<2-3 sentence overview of findings>",
  "matched_criteria": ["<specific strengths found in context relative to RFP>"],
  "missing_criteria": ["<critical gaps or missing items found in context>"],
  "risks": ["<hazards or disqualifiers>"],
  "checklist": [
    {{ 
      "item": "<Requirement Name, e.g., SOC 2 Report, 5 Years Experience, Hub Certification>", 
      "status": "Available", "Missing", or "Partial",
      "importance": "High" or "Optional"
    }}
  ],
  "highlights": ["<3-5 domain keywords specific to this RFP's industry>"]
}}

RFP DOCUMENT:
{rfp_text}

COMPANY CONTEXT:
{company_context}

UNIVERSAL SCORING PROTOCOL:
1. **Dynamic Extraction**: Identify the specific mandatory requirements from the RFP. Do not use a pre-set list.
2. **Strict Disqualification**: 
   - If any "High" importance item is "Missing", the `eligibility_score` MUST be capped at 45%.
   - If core services do not match the RFP's mission, the score MUST be capped at 40%.
3. **Value Discovery**: 
   - If the company matches all High importance items, the score should be 70+.
   - Scores above 90 are reserved for perfect matches with significant proof in the context.

IMPORTANT:
- Be an impartial, data-driven auditor.
- If the company context doesn't mention a requirement, it is "Missing".
- Return ONLY the JSON object.
"""

def clean_json_response(text):
    """Extract JSON from potential markdown wrappers."""
    match = re.search(r"(\{.*\})", text, re.DOTALL)
    if match:
        return match.group(1)
    return text

async def get_gemini_analysis(rfp_text, company_context):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        prompt = PROMPT_TEMPLATE.format(rfp_text=rfp_text[:30000], company_context=company_context[:10000])
        response = model.generate_content(prompt)
        json_str = clean_json_response(response.text)
        return json.loads(json_str)
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return None

async def get_mistral_analysis(rfp_text, company_context):
    try:
        # Mistral uses messages format
        prompt = PROMPT_TEMPLATE.format(rfp_text=rfp_text[:15000], company_context=company_context[:5000])
        response = mistral_client.chat.complete(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": prompt}]
        )
        json_str = clean_json_response(response.choices[0].message.content)
        return json.loads(json_str)
    except Exception as e:
        print(f"Mistral API Error: {e}")
        return None

async def analyze_rfp_with_dual_llm(rfp_text, company_context):
    """Primary: Gemini, Fallback: Mistral."""
    # Try Gemini first
    result = await get_gemini_analysis(rfp_text, company_context)
    if result:
        print("Analysis completed using PRIMARY model (Gemini).")
        return result
    
    # Fallback to Mistral
    print("Gemini failed. Switching to FALLBACK model (Mistral).")
    result = await get_mistral_analysis(rfp_text, company_context)
    if result:
        return result
    
    # Final fallback if both fail (unlikely)
    return {
        "eligibility_score": 0,
        "summary": "LLM analysis failed. Please check API keys and connectivity.",
        "matched_criteria": [],
        "missing_criteria": ["AI Engine Connectivity Error"],
        "risks": ["System could not verify compliance via LLM."],
        "checklist": [],
        "highlights": ["ERROR"]
    }
