"""Job Radar - Base Scraper Interface"""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin

import httpx
from selectolax.parser import HTMLParser
from tenacity import retry, stop_after_attempt, wait_exponential

from job_radar.models import Job, Company, ATSType

logger = logging.getLogger(__name__)


@dataclass
class ScrapedJob:
    """Raw scraped job data before normalization"""
    external_id: str
    title: str
    url: str
    location: str = ""
    department: str = ""
    experience_level: str = ""
    job_type: str = ""
    posted_date: Optional[datetime] = None
    description: str = ""
    raw_data: dict = None
    
    def __post_init__(self):
        if self.raw_data is None:
            self.raw_data = {}


class BaseScraper(ABC):
    """Base class for all job scrapers"""
    
    def __init__(
        self,
        company: Company,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: int = 5,
    ):
        self.company = company
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            },
            follow_redirects=True,
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _fetch(self, url: str, params: Optional[dict] = None, **kwargs) -> httpx.Response:
        """Fetch URL with retry logic"""
        assert self.client is not None
        response = await self.client.get(url, params=params, **kwargs)
        response.raise_for_status()
        return response

    async def _fetch_json(self, url: str, params: Optional[dict] = None, **kwargs) -> dict:
        """Fetch and parse JSON"""
        response = await self._fetch(url, params=params, **kwargs)
        return response.json()
    
    async def _fetch_html(self, url: str) -> HTMLParser:
        """Fetch and parse HTML"""
        response = await self._fetch(url)
        return HTMLParser(response.text)
    
    @abstractmethod
    async def scrape_jobs(self) -> list[ScrapedJob]:
        """Scrape jobs from company career page"""
        pass
    
    def normalize_job(self, scraped: ScrapedJob) -> Job:
        """Convert scraped job to normalized Job model"""
        return Job(
            id=f"{self.company.id}:{scraped.external_id}",
            company_id=self.company.id,
            external_id=scraped.external_id,
            title=scraped.title,
            url=scraped.url,
            location=scraped.location,
            department=scraped.department or None,
            experience_level=self._parse_experience_level(scraped.experience_level),
            job_type=self._parse_job_type(scraped.job_type),
            posted_date=scraped.posted_date,
            description=scraped.description or None,
            raw_data=scraped.raw_data,
        )
    
    def _parse_experience_level(self, level: str) -> Optional[str]:
        """Parse experience level string to enum"""
        if not level:
            return None
        level_lower = level.lower()
        if any(kw in level_lower for kw in ["intern", "entry", "new grad", "junior", "0-1", "0-2"]):
            return "entry"
        elif any(kw in level_lower for kw in ["senior", "sr.", "lead", "principal", "staff", "5+", "7+", "8+"]):
            return "senior"
        elif any(kw in level_lower for kw in ["director", "vp", "vice president", "head of"]):
            return "director"
        elif any(kw in level_lower for kw in ["mid", "intermediate", "2-4", "3-5"]):
            return "mid"
        return None
    
    def _parse_job_type(self, job_type: str) -> Optional[str]:
        """Parse job type string to enum"""
        if not job_type:
            return None
        type_lower = job_type.lower()
        if "full" in type_lower:
            return "full_time"
        elif "part" in type_lower:
            return "part_time"
        elif "contract" in type_lower or "contractor" in type_lower:
            return "contract"
        elif "intern" in type_lower:
            return "internship"
        elif "temporar" in type_lower:
            return "temporary"
        return None


class GreenhouseScraper(BaseScraper):
    """Scraper for Greenhouse.io ATS"""
    
    async def scrape_jobs(self) -> list[ScrapedJob]:
        board_token = self.company.ats_config.get("board_token")
        if not board_token:
            logger.warning(f"No board_token for {self.company.name}")
            return []
        
        # Greenhouse API endpoint
        api_url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
        params = {"content": "true"}  # Include description
        
        try:
            data = await self._fetch_json(api_url, params=params)
            jobs = []
            
            for job_data in data.get("jobs", []):
                # Filter for relevant departments/locations if needed
                jobs.append(ScrapedJob(
                    external_id=str(job_data.get("absolute_url", "").split("/")[-1]),
                    title=job_data.get("title", ""),
                    url=job_data.get("absolute_url", ""),
                    location=job_data.get("location", {}).get("name", ""),
                    department=job_data.get("departments", [{}])[0].get("name", "") if job_data.get("departments") else "",
                    posted_date=self._parse_date(job_data.get("updated_at")),
                    description=job_data.get("content", ""),
                    raw_data=job_data,
                ))
            
            return jobs
        except Exception as e:
            logger.error(f"Greenhouse scrape failed for {self.company.name}: {e}")
            return []
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            return None


class LeverScraper(BaseScraper):
    """Scraper for Lever.co ATS"""
    
    async def scrape_jobs(self) -> list[ScrapedJob]:
        board_token = self.company.ats_config.get("board_token")
        if not board_token:
            logger.warning(f"No board_token for {self.company.name}")
            return []
        
        api_url = f"https://api.lever.co/v0/postings/{board_token}"
        params = {"mode": "json"}
        
        try:
            data = await self._fetch_json(api_url, params=params)
            jobs = []
            
            for job_data in data:
                if job_data.get("state") != "published":
                    continue
                
                jobs.append(ScrapedJob(
                    external_id=job_data.get("id", ""),
                    title=job_data.get("text", ""),
                    url=job_data.get("hostedUrl", ""),
                    location=job_data.get("categories", {}).get("location", ""),
                    department=job_data.get("categories", {}).get("team", ""),
                    experience_level=job_data.get("categories", {}).get("commitment", ""),
                    posted_date=self._parse_date(job_data.get("createdAt")),
                    description=job_data.get("descriptionPlain", ""),
                    raw_data=job_data,
                ))
            
            return jobs
        except Exception as e:
            logger.error(f"Lever scrape failed for {self.company.name}: {e}")
            return []
    
    def _parse_date(self, timestamp: Optional[int]) -> Optional[datetime]:
        if not timestamp:
            return None
        try:
            return datetime.fromtimestamp(timestamp / 1000)
        except Exception:
            return None


class WorkdayScraper(BaseScraper):
    """Scraper for Workday ATS (basic implementation)"""
    
    async def scrape_jobs(self) -> list[ScrapedJob]:
        tenant = self.company.ats_config.get("tenant")
        career_site = self.company.ats_config.get("career_site", "external")
        
        if not tenant:
            logger.warning(f"No tenant for {self.company.name}")
            return []
        
        # Workday uses a more complex API, this is a simplified version
        # Real implementation would need to handle authentication, session, etc.
        base_url = f"https://{tenant}.wd1.myworkdayjobs.com"
        api_url = f"{base_url}/{career_site}"
        
        try:
            # This is a placeholder - actual Workday scraping requires
            # handling their GraphQL API with proper headers/session
            logger.warning(f"Workday scraping not fully implemented for {self.company.name}")
            return []
        except Exception as e:
            logger.error(f"Workday scrape failed for {self.company.name}: {e}")
            return []


class CustomScraper(BaseScraper):
    """Generic HTML scraper for custom career pages"""
    
    def __init__(self, company: Company, **kwargs):
        super().__init__(company, **kwargs)
        self.base_url = company.ats_config.get("base_url", str(company.career_url))
        self.job_list_selector = company.ats_config.get("job_list_selector", ".job, .position, .listing, [data-job-id]")
        self.title_selector = company.ats_config.get("title_selector", "h2, h3, .title, .job-title")
        self.url_selector = company.ats_config.get("url_selector", "a")
        self.location_selector = company.ats_config.get("location_selector", ".location, .job-location")
        self.pagination = company.ats_config.get("pagination", False)
    
    async def scrape_jobs(self) -> list[ScrapedJob]:
        jobs = []
        page = 1
        
        while True:
            url = self._build_page_url(page)
            logger.info(f"Scraping {self.company.name} page {page}: {url}")
            
            try:
                html = await self._fetch_html(url)
                job_elements = html.css(self.job_list_selector)
                
                if not job_elements:
                    break
                
                for elem in job_elements:
                    job = self._parse_job_element(elem)
                    if job:
                        jobs.append(job)
                
                if not self.pagination:
                    break
                
                page += 1
                await asyncio.sleep(1)  # Be respectful
                
            except Exception as e:
                logger.error(f"Custom scrape failed for {self.company.name} page {page}: {e}")
                break
        
        return jobs
    
    def _build_page_url(self, page: int) -> str:
        if page == 1:
            return self.base_url
        # Common pagination patterns
        if "?" in self.base_url:
            return f"{self.base_url}&page={page}"
        return f"{self.base_url}?page={page}"
    
    def _parse_job_element(self, elem) -> Optional[ScrapedJob]:
        try:
            title_elem = elem.css_first(self.title_selector)
            title = title_elem.text(strip=True) if title_elem else ""
            
            url_elem = elem.css_first(self.url_selector)
            url = urljoin(self.base_url, url_elem.attributes.get("href", "")) if url_elem else ""
            
            location_elem = elem.css_first(self.location_selector)
            location = location_elem.text(strip=True) if location_elem else ""
            
            # Extract external ID from URL or data attribute
            external_id = url.split("/")[-1] if url else ""
            if "data-job-id" in elem.attributes:
                external_id = elem.attributes["data-job-id"]
            
            if not title or not url:
                return None
            
            return ScrapedJob(
                external_id=external_id,
                title=title,
                url=url,
                location=location,
                raw_data={"html": elem.html},
            )
        except Exception as e:
            logger.debug(f"Failed to parse job element: {e}")
            return None


class AshbyScraper(BaseScraper):
    """Scraper for Ashby ATS"""
    
    async def scrape_jobs(self) -> list[ScrapedJob]:
        # Ashby uses a GraphQL API
        org_name = self.company.ats_config.get("organization_name")
        if not org_name:
            logger.warning(f"No organization_name for {self.company.name}")
            return []
        
        api_url = "https://jobs.ashbyhq.com/api/non-user-graphql"
        query = """
        query JobBoard($organizationHostedJobsPageName: String!) {
            jobBoard: organizationHostedJobsPage(name: $organizationHostedJobsPageName) {
                jobPostings(first: 100) {
                    edges {
                        node {
                            id
                            title
                            locationName
                            departmentName
                            employmentType
                            applyUrl
                            postedAt
                            description
                        }
                    }
                }
            }
        }
        """
        
        try:
            response = await self._fetch_json(api_url, json={"query": query, "variables": {"organizationHostedJobsPageName": org_name}})
            jobs = []
            
            for edge in response.get("data", {}).get("jobBoard", {}).get("jobPostings", {}).get("edges", []):
                job_data = edge.get("node", {})
                jobs.append(ScrapedJob(
                    external_id=job_data.get("id", ""),
                    title=job_data.get("title", ""),
                    url=job_data.get("applyUrl", ""),
                    location=job_data.get("locationName", ""),
                    department=job_data.get("departmentName", ""),
                    job_type=job_data.get("employmentType", ""),
                    posted_date=self._parse_date(job_data.get("postedAt")),
                    description=job_data.get("description", ""),
                    raw_data=job_data,
                ))
            
            return jobs
        except Exception as e:
            logger.error(f"Ashby scrape failed for {self.company.name}: {e}")
            return []
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            return None


# Scraper registry
SCRAPER_REGISTRY = {
    ATSType.GREENHOUSE: GreenhouseScraper,
    ATSType.LEVER: LeverScraper,
    ATSType.WORKDAY: WorkdayScraper,
    ATSType.ASHby: AshbyScraper,
    ATSType.CUSTOM: CustomScraper,
}


def get_scraper(ats_type: ATSType, company: Company, **kwargs) -> BaseScraper:
    """Get scraper instance for ATS type"""
    scraper_class = SCRAPER_REGISTRY.get(ats_type, CustomScraper)
    return scraper_class(company, **kwargs)