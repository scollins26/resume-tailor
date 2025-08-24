from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class FileFormat(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"

class ResumeAnalysisRequest(BaseModel):
    resume_text: str = Field(..., description="The resume text content")
    job_description: str = Field(..., description="The job description text")
    target_role: Optional[str] = Field(None, description="Target job role/title")
    industry: Optional[str] = Field(None, description="Target industry")
    experience_level: Optional[str] = Field(None, description="Experience level (entry, mid, senior)")

class ResumeAnalysisResponse(BaseModel):
    original_resume: str
    tailored_resume: str
    keyword_matches: Dict[str, int] = Field(..., description="Keywords found and their frequency")
    missing_keywords: List[str] = Field(..., description="Important keywords missing from resume")
    suggestions: List[str] = Field(..., description="Specific suggestions for improvement")
    confidence_score: float = Field(..., description="Confidence score for the tailoring (0-1)")
    analysis_summary: str = Field(..., description="Summary of the analysis and recommendations")

class KeywordAnalysis(BaseModel):
    keyword: str
    importance: float = Field(..., description="Importance score (0-1)")
    found_in_resume: bool
    frequency: int = Field(0, description="Frequency in resume")
    context: List[str] = Field(..., description="Context where keyword appears")

class ResumeSection(BaseModel):
    section_name: str
    original_content: str
    tailored_content: str
    improvements: List[str]

class DetailedAnalysisResponse(BaseModel):
    sections: List[ResumeSection]
    keyword_analysis: List[KeywordAnalysis]
    overall_score: float
    recommendations: List[str]
    industry_insights: Dict[str, Any]

