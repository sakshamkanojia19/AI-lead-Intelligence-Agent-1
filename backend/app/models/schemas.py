from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class LeadInput(BaseModel):
    company_name: Optional[str] = None
    company_domain: Optional[str] = None
    icp_persona: str = Field(..., description="Target persona")

class DecisionMaker(BaseModel):
    name: str 
    title: str
    linkedin_url: Optional[str] = None
    email: Optional[str] = None
    relevance_score: float

class TechStackItem(BaseModel):
    technology: str
    category: str
    confidence: float

class LeadAnalysis(BaseModel):
    company_summary: str
    key_insights: List[str]
    pain_points: List[str]
    opportunities: List[str]

class GeneratedEmail(BaseModel):
    subject: str
    body: str
    personalization_elements: List[str]
    cta: str

class LeadScore(BaseModel):
    reply_probability: float
    quality_score: float
    reasoning: str
    factors: Dict[str, float]

class LeadResponse(BaseModel):
    id: str
    company_name: str
    company_domain: str
    icp_persona: str
    analysis: LeadAnalysis
    decision_makers: List[DecisionMaker]
    tech_stack: List[TechStackItem]
    pain_hypothesis: str
    generated_email: GeneratedEmail
    score: LeadScore
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class LeadList(BaseModel):
    leads: List[LeadResponse]
    total: int
