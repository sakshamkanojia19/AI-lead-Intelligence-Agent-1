import httpx
import json
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from openai import AsyncOpenAI
from app.config import get_settings

settings = get_settings()
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
 
class WebScraperTool:
    async def scrape(self, domain: str) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as http_client:
                urls_to_try = [f"https://{domain}", f"https://www.{domain}"]
                content = {}
                used_url = None
                for url in urls_to_try:
                    try:
                        resp = await http_client.get(url, headers={"User-Agent": "Mozilla/5.0"})
                        if resp.status_code == 200:
                            used_url = url
                            soup = BeautifulSoup(resp.text, "html.parser")
                            meta = soup.find("meta", {"name": "description"})
                            if meta:
                                content["description"] = meta.get("content", "")
                            title = soup.find("title")
                            if title:
                                content["title"] = title.get_text()
                            texts = soup.stripped_strings
                            content["full_text"] = " ".join(list(texts)[:500])
                            break
                    except Exception:
                        continue
                return {"raw_content": content, "domain": domain, "source_url": used_url}
        except Exception as e:
            return {"error": str(e), "domain": domain}

class LinkedInFinderTool:
    async def find_decision_makers(self, company_name: str, icp_persona: str) -> List[Dict[str, Any]]:
        prompt = f"Given company '{company_name}' and target persona '{icp_persona}', generate 3 LinkedIn searches. Return JSON: {{'searches': [{{'title': '...', 'seniority': '...'}}]}}"
        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL, messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            strategy = json.loads(response.choices[0].message.content)
            results = []
            for i, s in enumerate(strategy.get("searches", [])):
                title = s.get("title", "Executive")
                keywords = f"{company_name} {title}".strip().replace(" ", "%20")
                results.append({
                    "name": f"Contact {i+1}",
                    "title": title,
                    "company": company_name,
                    "seniority": s.get("seniority", "senior"),
                    "linkedin_url": f"https://www.linkedin.com/search/results/people/?keywords={keywords}",
                    "relevance_score": 0.9 - (i * 0.15)
                })
            return results
        except Exception:
            return [{"name": "CTO", "title": "Chief Technology Officer", "company": company_name, "seniority": "c-suite", "relevance_score": 0.95}]

class TechStackDetectorTool:
    async def detect(self, domain: str) -> List[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient() as http_client:
                resp = await http_client.get(f"https://{domain}", headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
                html, headers = resp.text.lower(), dict(resp.headers)
                tech = []
                server = headers.get("server", "").lower()
                if "cloudflare" in server: tech.append({"tech": "Cloudflare", "category": "CDN", "confidence": 0.95})
                if "nginx" in server: tech.append({"tech": "Nginx", "category": "Web Server", "confidence": 0.9})
                if "react" in html or "data-reactroot" in html: tech.append({"tech": "React", "category": "Frontend", "confidence": 0.85})
                if "vue" in html: tech.append({"tech": "Vue.js", "category": "Frontend", "confidence": 0.8})
                if "gtag" in html: tech.append({"tech": "Google Analytics", "category": "Analytics", "confidence": 0.9})
                return tech
        except Exception:
            return [{"tech": "Unknown", "category": "N/A", "confidence": 0.0}]

class EmailGeneratorTool:
    async def generate(self, company_data: Dict, decision_maker: Dict, tech_stack: List, pain_hypothesis: str) -> Dict:
        tech_list = ", ".join([t["tech"] for t in tech_stack[:5]])
        prompt = f"Generate cold email to {decision_maker.get('name')} at {company_data.get('company_name')}. Tech: {tech_list}. Pain: {pain_hypothesis}. Return JSON with subject, body, personalization_elements, cta."
        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL, messages=[{"role": "user", "content": prompt}],
                temperature=0.7, response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception:
            return {"subject": f"Quick question about {company_data.get('company_name')}", 
                   "body": f"Hi {decision_maker.get('name', 'there')},\n\n{pain_hypothesis}\n\nWorth a chat?\n\nBest,",
                   "personalization_elements": ["Growth observation"], "cta": "15-min call?"}

class LeadScorerTool:
    async def score(self, company_data: Dict, tech_stack: List, email_quality: Dict, icp_match: str) -> Dict:
        prompt = f"Score lead for {company_data}. Return JSON with reply_probability (0-1), quality_score (0-100), reasoning, factors (dict of scores)."
        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL, messages=[{"role": "user", "content": prompt}],
                temperature=0.3, response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception:
            return {"reply_probability": 0.5, "quality_score": 50, "reasoning": "Default", "factors": {}}
