from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import requests

from generate_report import generate_report

app = FastAPI(title="Financial Insights API", version="1.0")

class Persona(BaseModel):
    name: str
    description: str
    interests: List[str]

class ReportRequest(BaseModel):
    persona: Persona
    companySize: str
    industry: str
    region: str
    role: str
    ticker: str
    language: str
    model: Optional[str] = "llama3"
    callback_url: Optional[str] = None

@app.post("/generate-report")
def generate_report_endpoint(request: ReportRequest, background_tasks: BackgroundTasks):
    if request.callback_url:
        background_tasks.add_task(process_and_callback, request)
        return {
            "status": "processing",
            "message": "Report will be sent to callback URL shortly.",
            "request_payload": request.dict()
        }
    else:
        try:
            result = generate_report(
                persona=request.persona.dict(),
                interests=request.persona.interests,
                company_size=request.companySize,
                industry=request.industry,
                region=request.region,
                role=request.role,
                ticker=request.ticker,
                language=request.language,
                model=request.model
            )
            return {
                "request_payload": request.dict(),
                "json_report": result["json_report"]
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

def process_and_callback(request: ReportRequest):
    try:
        result = generate_report(
            persona=request.persona.dict(),
            interests=request.persona.interests,
            company_size=request.companySize,
            industry=request.industry,
            region=request.region,
            role=request.role,
            ticker=request.ticker,
            language=request.language,
            model=request.model
        )
        callback_payload = {
            "request_payload": request.dict(),
            "json_report": result["json_report"]
        }

        response = requests.post(
            request.callback_url,
            json=callback_payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"[CALLBACK] Status {response.status_code}: {response.text}")

    except Exception as e:
        print(f"[ERROR] Callback failed: {e}")

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
