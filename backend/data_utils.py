import io
import json
import PyPDF2
import docx
import re
from typing import List, Dict

def extract_text_from_bytes(file_bytes: bytes, filename: str) -> str:
    if filename.endswith('.pdf'):
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            text = ""
            for page in reader.pages:
                text += (page.extract_text() or "") + "\n"
            return text
        except Exception:
            return ""
    elif filename.endswith('.docx') or filename.endswith('.doc'):
        try:
            doc = docx.Document(io.BytesIO(file_bytes))
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception:
            return ""
    else:
        try:
            return file_bytes.decode('utf-8', errors='ignore')
        except Exception:
            return ""

def analyze_eligibility(rfp_text: str, rfp_filename: str, company_data: Dict) -> Dict:
    """
    Precision-calibrated RAG eligibility analysis with strict mandatory validation.
    """
    rfp_lower = rfp_text.lower()
    
    # Extract company attributes safely
    company_name = company_data.get("name", "The Company")
    
    # Safe extraction of experience years
    raw_years = company_data.get("experience_years", company_data.get("Years of Experience in Temporary Staffing", 5))
    if isinstance(raw_years, str):
        y_match = re.search(r'(\d+)', raw_years)
        company_years = int(y_match.group(1)) if y_match else 5
    else:
        company_years = int(raw_years or 0)

    company_state = str(company_data.get("state", company_data.get("State of Incorporation", "Unknown"))).lower()
    company_cert = str(company_data.get("certification", company_data.get("Historically Underutilized Business/DBE Status", "Not certified"))).lower()
    company_context = str(company_data.get("raw_context", "")).lower()

    results = {
        "eligibility_score": 0,
        "summary": "",
        "matched_criteria": [],
        "missing_criteria": [],
        "risks": [],
        "checklist": [],
        "highlights": [],
        "filename": rfp_filename
    }

    # Tracking for Mandatory Disqualifiers
    mandatory_missing = False

    # 1. Experience Check (Weight: 25)
    experience_req_match = re.search(r'(\d+)\+?\s*years?', rfp_lower)
    required_years = int(experience_req_match.group(1)) if experience_req_match else 3
    
    if company_years >= required_years:
        results["matched_criteria"].append(f"Core Experience: {company_years} years (Req: {required_years}+)")
        results["eligibility_score"] += 25
    else:
        # Near matches within 1 year get 10 points but flagged as risk
        if (required_years - company_years) <= 1:
            results["matched_criteria"].append(f"Experience Baseline: {company_years} years")
            results["eligibility_score"] += 10
            results["risks"].append(f"Minor experience gap ({company_years} vs {required_years} years).")
        else:
            results["missing_criteria"].append(f"Insufficient Experience: {company_years} years (Req: {required_years}+)")
            mandatory_missing = True

    # 2. Certification Check (Weight: 15)
    cert_keywords = ["hub", "dbe", "mbe", "wbe", "veteran", "historically underutilized", "disadvantaged"]
    requires_cert = any(kw in rfp_lower for kw in cert_keywords)
    has_cert = not any(v in company_cert for v in ["not certified", "none", "n/a", "unknown"])
    
    if requires_cert:
        if has_cert:
            results["matched_criteria"].append(f"Priority Certification: {company_cert.upper()} status confirmed.")
            results["eligibility_score"] += 15
        else:
            results["risks"].append("Preferred socio-economic certification (HUB/DBE) missing.")
    else:
        # Small bonus for cert if not explicitly required
        if has_cert:
            results["matched_criteria"].append(f"Value Add: {company_cert.upper()} certification.")
            results["eligibility_score"] += 5

    # 3. Geographic Alignment (Weight: 10)
    state_keywords = ["texas", "tx", "california", "ca", "delaware", "de", "florida", "fl", "new york", "ny"]
    target_states = [s for s in state_keywords if s in rfp_lower]
    
    if any(s in company_state for s in target_states) or not target_states:
        results["matched_criteria"].append(f"Jurisdictional Alignment: {company_state.title()}.")
        results["eligibility_score"] += 10
    else:
        results["risks"].append(f"Geographic mismatch: Registered in {company_state.title()}.")

    # 4. Capability Match (Weight: 30) - Tightened Domain Logic
    domain_keywords = {
        "Staffing": ["staffing", "personnel", "workforce", "recruit"],
        "IT Services": ["it", "software", "development", "technology"],
        "Healthcare": ["health", "medical", "clinical", "nursing"],
        "Consulting": ["consulting", "strategy", "management"],
        "Engineering": ["engineering", "technical", "design"],
        "Security": ["security", "protection", "monitoring"],
        "Administrative": ["admin", "clerical", "office", "secretarial"]
    }
    
    found_highlights = []
    points_per_match = 10
    matches_found = 0
    
    for domain, kws in domain_keywords.items():
        if any(kw in rfp_lower for kw in kws):
            found_highlights.append(domain.upper())
            if any(kw in company_context for kw in kws):
                matches_found += 1
                if matches_found <= 3: # Cap at 3 domain matches for score
                    results["eligibility_score"] += points_per_match

    results["highlights"] = found_highlights
    if matches_found > 0:
        results["matched_criteria"].append(f"Core Capabilities: {matches_found} strong domain alignments detected.")
    else:
        results["risks"].append("Operational alignment is weak; core RFP service keywords missing from context.")

    # 5. Mandatory Compliance Checklist (Weight: 20) - STRICT ENFORCEMENT
    mandatory_items = [
        {"name": "W-9", "key": "has_w9", "pattern": r"w-?9|taxpayer"},
        {"name": "Insurance", "key": "has_insurance", "pattern": r"insurance|liability|workers"},
        {"name": "Bonding", "key": "bonding", "pattern": r"bonding|surety"},
        {"name": "Financials", "key": "has_financials", "pattern": r"financial|audit|revenue"},
        {"name": "References", "key": "references", "pattern": r"references|past performance"}
    ]
    
    for item in mandatory_items:
        if re.search(item["pattern"], rfp_lower):
            is_available = company_data.get(item["key"], False) or re.search(item["pattern"], company_context) is not None
            
            results["checklist"].append({
                "item": item["name"],
                "status": "Available" if is_available else "Required"
            })
            
            if is_available:
                results["eligibility_score"] += 4
            else:
                results["missing_criteria"].append(f"Missing Mandatory Element: {item['name']}")
                mandatory_missing = True # STRICT: Any missing required element caps the score

    # Final Score Normalization
    if mandatory_missing:
        results["eligibility_score"] = min(results["eligibility_score"], 45) 
    
    results["eligibility_score"] = min(results["eligibility_score"], 100)

    # Risk Highlight for Ineligible Docs
    if results["eligibility_score"] < 50:
        if not any("ALERT" in r for r in results["risks"]):
            results["risks"].append("ALERT: High probability of disqualification due to mandatory gaps detected.")
        if not results["missing_criteria"]:
            results["missing_criteria"].append("Strategic Value Mismatch")

    # Summary Generation
    if results["eligibility_score"] >= 90:
        status = "PREMIUM CHOICE"
        detail = "Exceptional synergy with zero compliance or experience gaps."
    elif results["eligibility_score"] >= 70:
        status = "VIABLE CONTENDER"
        detail = "Strong match with minor geographic or secondary gaps."
    elif results["eligibility_score"] >= 50:
        status = "BORDERLINE / CAUTION"
        detail = "Matches baseline requirements but carries moderate operational risk."
    else:
        status = "UNSUITABLE / DISQUALIFIED"
        detail = "Critical gaps in mandatory compliance or experience detected."

    results["summary"] = f"RAG Analysis Complete. Status: {status}. {detail} Final Result: {results['eligibility_score']}%."

    return results
