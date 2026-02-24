import json
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from openai import AsyncOpenAI
from app.config import get_settings
from app.agent.tools import WebScraperTool, LinkedInFinderTool, TechStackDetectorTool, EmailGeneratorTool, LeadScorerTool
 
settings = get_settings()
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

class AgentState(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    OBSERVING = "observing"
    COMPLETE = "complete"
    ERROR = "error"

@dataclass
class AgentContext:
    company_name: Optional[str] = None
    company_domain: Optional[str] = None
    icp_persona: str = ""
    scraped_data: Dict[str, Any] = field(default_factory=dict)
    decision_makers: List[Dict] = field(default_factory=list)
    tech_stack: List[Dict] = field(default_factory=list)
    pain_hypothesis: str = ""
    generated_email: Dict[str, Any] = field(default_factory=dict)
    lead_score: Dict[str, Any] = field(default_factory=dict)
    thoughts: List[str] = field(default_factory=list)
    current_step: int = 0
    max_steps: int = 10
    state: AgentState = AgentState.IDLE

class LeadIntelligenceAgent:
    def __init__(self):
        self.tools = {
            "web_scraper": WebScraperTool(),
            "linkedin_finder": LinkedInFinderTool(),
            "tech_detector": TechStackDetectorTool(),
            "email_generator": EmailGeneratorTool(),
            "lead_scorer": LeadScorerTool()
        }
    
    async def run(self, company_name: Optional[str], company_domain: Optional[str], icp_persona: str) -> Dict[str, Any]:
        if not company_name and not company_domain:
            return {"status": "error", "error": "company_name or company_domain is required"}
        ctx = AgentContext(
            company_name=company_name or company_domain,
            company_domain=company_domain or self._infer_domain(company_name),
            icp_persona=icp_persona,
            state=AgentState.THINKING
        )
        
        while ctx.current_step < ctx.max_steps and ctx.state != AgentState.COMPLETE:
            ctx.current_step += 1
            thought = await self._think(ctx)
            ctx.thoughts.append(thought)
            ctx.state = AgentState.EXECUTING
            action = await self._decide_action(ctx)
            
            if action["tool"] == "complete":
                ctx.state = AgentState.COMPLETE
                break
            if action["tool"] == "error":
                ctx.state = AgentState.ERROR
                break
            
            observation = await self._execute_tool(action, ctx)
            ctx.state = AgentState.OBSERVING
            await self._update_context(ctx, action["tool"], observation)
            await asyncio.sleep(0.5)
        
        return self._compile_result(ctx)
    
    def _infer_domain(self, company_name: Optional[str]) -> str:
        if not company_name: return ""
        cleaned = company_name.strip().lower()
        if "." in cleaned:
            return cleaned.replace("https://", "").replace("http://", "").replace("www.", "")
        return f"{cleaned.replace(' ', '').replace('.', '')}.com"
    
    async def _think(self, ctx: AgentContext) -> str:
        context = f"Step {ctx.current_step}: {ctx.company_name} ({ctx.company_domain}). Data: Scraped={bool(ctx.scraped_data)}, DM={len(ctx.decision_makers)}, Tech={len(ctx.tech_stack)}"
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": f"{context}\nWhat next?"}],
            max_tokens=150
        )
        return response.choices[0].message.content
    
    async def _decide_action(self, ctx: AgentContext) -> Dict[str, Any]:
        if not ctx.scraped_data:
            return {"tool": "web_scraper", "params": {"domain": ctx.company_domain}}
        if not ctx.decision_makers:
            return {"tool": "linkedin_finder", "params": {"company_name": ctx.company_name or ctx.company_domain, "icp_persona": ctx.icp_persona}}
        if not ctx.tech_stack:
            return {"tool": "tech_detector", "params": {"domain": ctx.company_domain}}
        if not ctx.pain_hypothesis:
            ctx.pain_hypothesis = await self._generate_pain(ctx)
            return {"tool": "observe", "params": {}}
        if not ctx.generated_email and ctx.decision_makers:
            return {"tool": "email_generator", "params": {"company_data": {"company_name": ctx.company_name, "description": ctx.scraped_data.get("raw_content", {}).get("description", "")}, "decision_maker": ctx.decision_makers[0], "tech_stack": ctx.tech_stack, "pain_hypothesis": ctx.pain_hypothesis}}
        if not ctx.lead_score:
            return {"tool": "lead_scorer", "params": {"company_data": {"company_name": ctx.company_name}, "tech_stack": ctx.tech_stack, "email_quality": ctx.generated_email, "icp_match": ctx.icp_persona}}
        return {"tool": "complete"}
    
    async def _execute_tool(self, action: Dict, ctx: AgentContext):
        if action["tool"] == "observe": return {"status": "ok"}
        tool = self.tools.get(action["tool"])
        if not tool: return {"error": "Unknown tool"}
        try:
            method = getattr(
                tool,
                "scrape" if action["tool"] == "web_scraper" else
                "find_decision_makers" if action["tool"] == "linkedin_finder" else
                "detect" if action["tool"] == "tech_detector" else
                "generate" if action["tool"] == "email_generator" else "score"
            )
            return await method(**action["params"])
        except Exception as e:
            return {"error": str(e)}
    
    async def _update_context(self, ctx: AgentContext, tool_name: str, observation: Any):
        if tool_name == "web_scraper": ctx.scraped_data = observation
        elif tool_name == "linkedin_finder": ctx.decision_makers = observation if isinstance(observation, list) else []
        elif tool_name == "tech_detector": ctx.tech_stack = observation if isinstance(observation, list) else []
        elif tool_name == "email_generator": ctx.generated_email = observation
        elif tool_name == "lead_scorer": ctx.lead_score = observation
    
    async def _generate_pain(self, ctx: AgentContext) -> str:
        tech = ", ".join([t["tech"] for t in ctx.tech_stack[:3]])
        prompt = f"Generate 2-sentence pain hypothesis for {ctx.company_name} (tech: {tech}, target: {ctx.icp_persona}). Focus on scaling challenges."
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    
    def _compile_result(self, ctx: AgentContext) -> Dict[str, Any]:
        return {
            "company_name": ctx.company_name, "company_domain": ctx.company_domain, "icp_persona": ctx.icp_persona,
            "reasoning_chain": ctx.thoughts, "steps_executed": ctx.current_step,
            "data": {
                "company_intelligence": ctx.scraped_data, "decision_makers": ctx.decision_makers,
                "tech_stack": ctx.tech_stack, "pain_hypothesis": ctx.pain_hypothesis,
                "generated_email": ctx.generated_email, "lead_score": ctx.lead_score
            },
            "status": "complete" if ctx.state == AgentState.COMPLETE else "incomplete"
        }
