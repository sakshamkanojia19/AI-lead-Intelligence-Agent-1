from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
from bson import ObjectId

from app.config import get_settings
from app.models.database import init_db, close_db, get_leads_collection, serialize_lead
from app.models.schemas import LeadInput, LeadResponse, LeadList, LeadAnalysis, DecisionMaker, TechStackItem, GeneratedEmail, LeadScore
from app.agent.core import LeadIntelligenceAgent

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()

app = FastAPI(title="AI Lead Intelligence Agent", version="1.0.0", lifespan=lifespan)

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/leads/research", response_model=LeadResponse)
async def research_lead(input_data: LeadInput):
    try:
        agent = LeadIntelligenceAgent()
        result = await agent.run(input_data.company_name, input_data.company_domain, input_data.icp_persona)
        if result.get("status") != "complete":
            raise HTTPException(status_code=500, detail=result.get("error", "Agent failed"))
        
        data = result["data"]
        lead_doc = {
            "company_name": result["company_name"] or result["company_domain"],
            "company_domain": result["company_domain"] or "",
            "icp_persona": result["icp_persona"],
            "company_intelligence": data.get("company_intelligence", {}),
            "decision_makers": data.get("decision_makers", []),
            "tech_stack": data.get("tech_stack", []),
            "pain_hypothesis": data.get("pain_hypothesis", ""),
            "generated_email": data.get("generated_email", {}),
            "lead_score": data.get("lead_score", {}),
            "reasoning_chain": result.get("reasoning_chain", []),
            "steps_executed": result.get("steps_executed", 0),
            "status": "new",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        collection = get_leads_collection()
        insert_result = await collection.insert_one(lead_doc)
        lead_doc["_id"] = insert_result.inserted_id
        return format_lead_response(lead_doc)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/leads", response_model=LeadList)
async def list_leads(skip: int = 0, limit: int = 50):
    collection = get_leads_collection()
    total = await collection.count_documents({})
    cursor = collection.find({}).sort("created_at", -1).skip(skip).limit(limit)
    leads = [format_lead_response(doc) async for doc in cursor]
    return LeadList(leads=leads, total=total)

@app.get("/api/leads/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: str):
    collection = get_leads_collection()
    try:
        oid = ObjectId(lead_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid lead id")
    doc = await collection.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return format_lead_response(doc)

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

def format_lead_response(lead: dict) -> LeadResponse:
    doc = serialize_lead(lead)
    company_intel = doc.get("company_intelligence", {}) or {}
    raw_content = company_intel.get("raw_content", {}) or {}
    decision_makers = doc.get("decision_makers", []) or []
    tech_stack = doc.get("tech_stack", []) or []
    lead_score = doc.get("lead_score", {}) or {}
    generated_email = doc.get("generated_email", {}) or {}
    personalization_elements = generated_email.get("personalization_elements", [])
    if isinstance(personalization_elements, dict):
        personalization_elements = [f"{k}: {v}" for k, v in personalization_elements.items()]
    elif isinstance(personalization_elements, str):
        personalization_elements = [personalization_elements]
    elif not isinstance(personalization_elements, list):
        personalization_elements = []
    else:
        personalization_elements = [str(v) for v in personalization_elements]

    company_summary = raw_content.get("description") or raw_content.get("title") or ""
    key_insights = []
    if raw_content.get("title"):
        key_insights.append(f"Site title: {raw_content.get('title')}")
    if company_intel.get("source_url"):
        key_insights.append(f"Source: {company_intel.get('source_url')}")

    return LeadResponse(
        id=doc.get("id", ""),
        company_name=doc.get("company_name", ""),
        company_domain=doc.get("company_domain", ""),
        icp_persona=doc.get("icp_persona", ""),
        analysis=LeadAnalysis(
            company_summary=company_summary,
            key_insights=key_insights,
            pain_points=[doc.get("pain_hypothesis")] if doc.get("pain_hypothesis") else [],
            opportunities=[]
        ),
        decision_makers=[
            DecisionMaker(
                name=d.get("name", "Unknown"),
                title=d.get("title", "Executive"),
                linkedin_url=d.get("linkedin_url"),
                email=d.get("email"),
                relevance_score=float(d.get("relevance_score", 0.5))
            )
            for d in decision_makers
        ],
        tech_stack=[
            TechStackItem(
                technology=t.get("technology") or t.get("tech") or "Unknown",
                category=t.get("category") or "Other",
                confidence=float(t.get("confidence", 0.5))
            )
            for t in tech_stack
        ],
        pain_hypothesis=doc.get("pain_hypothesis", ""),
        generated_email=GeneratedEmail(
            subject=generated_email.get("subject", ""),
            body=generated_email.get("body", ""),
            personalization_elements=personalization_elements,
            cta=generated_email.get("cta", "")
        ),
        score=LeadScore(
            reply_probability=float(lead_score.get("reply_probability", 0.0)),
            quality_score=float(lead_score.get("quality_score", 0.0)),
            reasoning=lead_score.get("reasoning", ""),
            factors={k: float(v) for k, v in (lead_score.get("factors") or {}).items()}
        ),
        status=doc.get("status", "new"),
        created_at=doc.get("created_at", datetime.utcnow())
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
