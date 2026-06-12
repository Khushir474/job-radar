"""Job Radar - Job Matching Engine"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from rapidfuzz import fuzz, process

from job_radar.models import Job, RoleCategory, ExperienceLevel, JobType
from job_radar.config import DEFAULT_KEYWORDS, DEFAULT_EXCLUDED_KEYWORDS


@dataclass
class MatchResult:
    """Result of job matching"""
    matched: bool
    matched_roles: list[RoleCategory]
    matched_keywords: list[str]
    matched_location: bool
    matched_experience: bool
    matched_job_type: bool
    excluded: bool
    excluded_keyword: Optional[str] = None
    score: float = 0.0


class JobMatcher:
    """Matches jobs against user criteria"""
    
    def __init__(
        self,
        roles: list[RoleCategory] = None,
        locations: list[str] = None,
        experience_levels: list[ExperienceLevel] = None,
        job_types: list[JobType] = None,
        excluded_keywords: list[str] = None,
        required_keywords: list[str] = None,
        keywords: dict[RoleCategory, list[str]] = None,
        fuzzy_threshold: int = 80,
    ):
        self.roles = roles or list(RoleCategory)
        self.locations = [loc.lower() for loc in (locations or [])]
        self.experience_levels = experience_levels or []
        self.job_types = job_types or []
        self.excluded_keywords = [kw.lower() for kw in (excluded_keywords or DEFAULT_EXCLUDED_KEYWORDS)]
        self.required_keywords = [kw.lower() for kw in (required_keywords or [])]
        self.keywords = keywords or DEFAULT_KEYWORDS
        self.fuzzy_threshold = fuzzy_threshold
        
        # Compile regex patterns for excluded words (whole word matching)
        self.excluded_patterns = [
            re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE)
            for kw in self.excluded_keywords
        ]
        self.required_patterns = [
            re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE)
            for kw in self.required_keywords
        ]
    
    def match(self, job: Job) -> MatchResult:
        """Match a job against all criteria"""
        # Check excluded keywords first (fast reject)
        excluded, excluded_kw = self._check_excluded(job)
        if excluded:
            return MatchResult(
                matched=False,
                matched_roles=[],
                matched_keywords=[],
                matched_location=False,
                matched_experience=False,
                matched_job_type=False,
                excluded=True,
                excluded_keyword=excluded_kw,
            )
        
        # Check required keywords (must have at least one if specified)
        if self.required_keywords and not self._check_required(job):
            return MatchResult(
                matched=False,
                matched_roles=[],
                matched_keywords=[],
                matched_location=False,
                matched_experience=False,
                matched_job_type=False,
                excluded=False,
            )
        
        # Match roles
        matched_roles, matched_keywords = self._match_roles(job)
        
        # Match location
        matched_location = self._match_location(job)
        
        # Match experience level
        matched_experience = self._match_experience(job)
        
        # Match job type
        matched_job_type = self._match_job_type(job)
        
        # Calculate overall score
        score = self._calculate_score(job, matched_roles, matched_location, matched_experience, matched_job_type)
        
        # Overall match: must match at least one role AND (location OR experience OR job_type)
        role_match = len(matched_roles) > 0
        other_match = matched_location or matched_experience or matched_job_type or not any([self.locations, self.experience_levels, self.job_types])
        
        matched = role_match and other_match
        
        return MatchResult(
            matched=matched,
            matched_roles=matched_roles,
            matched_keywords=matched_keywords,
            matched_location=matched_location,
            matched_experience=matched_experience,
            matched_job_type=matched_job_type,
            excluded=False,
            score=score,
        )
    
    def _check_excluded(self, job: Job) -> tuple[bool, Optional[str]]:
        """Check if job contains excluded keywords"""
        text = f"{job.title} {job.description or ''} {job.location}".lower()
        
        for pattern, keyword in zip(self.excluded_patterns, self.excluded_keywords):
            if pattern.search(text):
                return True, keyword
        
        return False, None
    
    def _check_required(self, job: Job) -> bool:
        """Check if job contains at least one required keyword"""
        if not self.required_keywords:
            return True
        
        text = f"{job.title} {job.description or ''} {job.location}".lower()
        
        for pattern in self.required_patterns:
            if pattern.search(text):
                return True
        
        return False
    
    def _match_roles(self, job: Job) -> tuple[list[RoleCategory], list[str]]:
        """Match job against role keywords"""
        text = f"{job.title} {job.description or ''}".lower()
        matched_roles = []
        matched_keywords = []
        
        for role in self.roles:
            role_keywords = self.keywords.get(role, [])
            for keyword in role_keywords:
                # Try exact match first
                if keyword.lower() in text:
                    if role not in matched_roles:
                        matched_roles.append(role)
                    if keyword not in matched_keywords:
                        matched_keywords.append(keyword)
                # Try fuzzy match for multi-word keywords
                elif len(keyword.split()) > 1:
                    score = fuzz.partial_ratio(keyword.lower(), text)
                    if score >= self.fuzzy_threshold:
                        if role not in matched_roles:
                            matched_roles.append(role)
                        if keyword not in matched_keywords:
                            matched_keywords.append(keyword)
        
        return matched_roles, matched_keywords
    
    def _match_location(self, job: Job) -> bool:
        """Match job location"""
        if not self.locations:
            return True
        
        job_location = job.location.lower()
        
        # Check for remote-friendly keywords
        remote_keywords = ["remote", "anywhere", "distributed", "worldwide", "global", "work from home", "wfh"]
        if any(kw in job_location for kw in remote_keywords):
            if any("remote" in loc or "anywhere" in loc for loc in self.locations):
                return True
        
        # Check for location matches
        for loc in self.locations:
            if loc in job_location:
                return True
            # Fuzzy match for cities
            if len(loc) > 3:
                score = fuzz.partial_ratio(loc, job_location)
                if score >= 85:
                    return True
        
        return False
    
    def _match_experience(self, job: Job) -> bool:
        """Match experience level"""
        if not self.experience_levels or not job.experience_level:
            return True
        
        return job.experience_level in self.experience_levels
    
    def _match_job_type(self, job: Job) -> bool:
        """Match job type"""
        if not self.job_types or not job.job_type:
            return True
        
        return job.job_type in self.job_types
    
    def _calculate_score(
        self,
        job: Job,
        matched_roles: list[RoleCategory],
        matched_location: bool,
        matched_experience: bool,
        matched_job_type: bool,
    ) -> float:
        """Calculate match score (0-100)"""
        score = 0.0
        
        # Role match (up to 40 points)
        score += min(len(matched_roles) * 10, 40)
        
        # Location match (up to 25 points)
        if matched_location:
            score += 25
        
        # Experience match (up to 20 points)
        if matched_experience:
            score += 20
        
        # Job type match (up to 15 points)
        if matched_job_type:
            score += 15
        
        return min(score, 100.0)


def create_matcher_from_config(config) -> JobMatcher:
    """Create JobMatcher from AppConfig"""
    return JobMatcher(
        roles=config.filters.roles,
        locations=config.filters.locations,
        experience_levels=config.filters.experience_levels,
        job_types=config.filters.job_types,
        excluded_keywords=config.filters.excluded_keywords,
        required_keywords=config.filters.required_keywords,
    )