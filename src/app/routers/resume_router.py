from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
import tempfile
import os
from loguru import logger

from ..models import (
    ResumeAnalysisRequest, 
    ResumeAnalysisResponse, 
    DetailedAnalysisResponse,
    FileFormat
)
from ..services import AIService, FileService

router = APIRouter(prefix="/resume", tags=["resume"])

# Initialize services
ai_service = AIService()
file_service = FileService()

@router.post("/analyze", response_model=ResumeAnalysisResponse)
async def analyze_resume(request: ResumeAnalysisRequest):
    """
    Analyze and tailor a resume based on a job description
    """
    try:
        logger.info("Starting resume analysis")
        
        # Extract keywords from job description
        keywords_data = ai_service.extract_keywords_from_job_description(request.job_description)
        keywords = [kw['keyword'] for kw in keywords_data]
        
        # Analyze keyword matches in resume
        keyword_analysis = ai_service.analyze_resume_keywords(request.resume_text, keywords)
        
        # Tailor the resume
        tailored_resume = ai_service.tailor_resume(
            request.resume_text, 
            request.job_description, 
            request.target_role
        )
        
        # Generate improvement suggestions
        suggestions = ai_service.generate_improvement_suggestions(
            request.resume_text, 
            request.job_description, 
            keyword_analysis
        )
        
        # Calculate confidence score
        confidence_score = ai_service.calculate_confidence_score(keyword_analysis, keywords_data)
        
        # Prepare keyword matches for response
        keyword_matches = {
            kw: data['frequency'] 
            for kw, data in keyword_analysis.items() 
            if data['found']
        }
        
        # Get missing keywords
        missing_keywords = [
            kw for kw, data in keyword_analysis.items() 
            if not data['found']
        ]
        
        # Generate analysis summary
        analysis_summary = f"""
        Resume Analysis Complete
        
        Keywords Found: {len(keyword_matches)}/{len(keywords)}
        Missing Keywords: {len(missing_keywords)}
        Confidence Score: {confidence_score:.2%}
        
        The resume has been optimized to better match the job requirements.
        Consider incorporating the missing keywords to improve your chances.
        """
        
        return ResumeAnalysisResponse(
            original_resume=request.resume_text,
            tailored_resume=tailored_resume,
            keyword_matches=keyword_matches,
            missing_keywords=missing_keywords,
            suggestions=suggestions,
            confidence_score=confidence_score,
            analysis_summary=analysis_summary.strip()
        )
        
    except Exception as e:
        logger.error(f"Error in resume analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/analyze-file")
async def analyze_resume_file(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...),
    target_role: Optional[str] = Form(None),
    industry: Optional[str] = Form(None),
    experience_level: Optional[str] = Form(None)
):
    """
    Analyze resume from uploaded file
    """
    try:
        # Validate file
        if not resume_file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Detect file format
        file_format = file_service.detect_file_format(resume_file.filename)
        if not file_format:
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(resume_file.filename)[1]) as temp_file:
            content = await resume_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Validate file size
            if not file_service.validate_file_size(temp_file_path):
                raise HTTPException(status_code=400, detail="File too large (max 10MB)")
            
            # Extract text from file
            resume_text = file_service.extract_text_from_file(temp_file_path, file_format)
            if not resume_text:
                raise HTTPException(status_code=400, detail="Could not extract text from file")
            
            # Clean the text
            resume_text = file_service.clean_text(resume_text)
            
            # Create analysis request
            request = ResumeAnalysisRequest(
                resume_text=resume_text,
                job_description=job_description,
                target_role=target_role,
                industry=industry,
                experience_level=experience_level
            )
            
            # Perform analysis
            return await analyze_resume(request)
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing uploaded file: {e}")
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")

@router.post("/detailed-analysis", response_model=DetailedAnalysisResponse)
async def detailed_resume_analysis(request: ResumeAnalysisRequest):
    """
    Perform detailed analysis with section-by-section breakdown
    """
    try:
        logger.info("Starting detailed resume analysis")
        
        # Extract keywords
        keywords_data = ai_service.extract_keywords_from_job_description(request.job_description)
        keywords = [kw['keyword'] for kw in keywords_data]
        
        # Analyze resume sections
        sections_data = ai_service.analyze_resume_sections(request.resume_text)
        
        # Analyze keywords
        keyword_analysis = ai_service.analyze_resume_keywords(request.resume_text, keywords)
        
        # Create detailed keyword analysis
        detailed_keywords = []
        for kw_data in keywords_data:
            keyword = kw_data['keyword']
            analysis = keyword_analysis.get(keyword, {})
            
            detailed_keywords.append({
                "keyword": keyword,
                "importance": kw_data.get('importance', 0),
                "found_in_resume": analysis.get('found', False),
                "frequency": analysis.get('frequency', 0),
                "context": analysis.get('context', [])
            })
        
        # Create section analysis
        sections = []
        for section_data in sections_data:
            section_name = section_data.get('section_name', 'Unknown')
            original_content = section_data.get('content', '')
            
            # Tailor this section
            tailored_content = ai_service.tailor_resume(
                original_content,
                request.job_description,
                request.target_role
            )
            
            # Generate section-specific improvements
            improvements = ai_service.generate_improvement_suggestions(
                original_content,
                request.job_description,
                {kw: keyword_analysis.get(kw, {}) for kw in keywords}
            )
            
            sections.append({
                "section_name": section_name,
                "original_content": original_content,
                "tailored_content": tailored_content,
                "improvements": improvements[:3]  # Limit to 3 suggestions per section
            })
        
        # Calculate overall score
        overall_score = ai_service.calculate_confidence_score(keyword_analysis, keywords_data)
        
        # Generate recommendations
        recommendations = ai_service.generate_improvement_suggestions(
            request.resume_text,
            request.job_description,
            keyword_analysis
        )
        
        # Industry insights (placeholder for future enhancement)
        industry_insights = {
            "trending_skills": [kw['keyword'] for kw in keywords_data[:5]],
            "market_demand": "High" if overall_score > 0.7 else "Medium" if overall_score > 0.4 else "Low",
            "competition_level": "High" if overall_score > 0.8 else "Medium" if overall_score > 0.5 else "Low"
        }
        
        return DetailedAnalysisResponse(
            sections=sections,
            keyword_analysis=detailed_keywords,
            overall_score=overall_score,
            recommendations=recommendations,
            industry_insights=industry_insights
        )
        
    except Exception as e:
        logger.error(f"Error in detailed analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Detailed analysis failed: {str(e)}")

@router.get("/keywords")
async def extract_keywords(job_description: str):
    """
    Extract keywords from a job description
    """
    try:
        keywords = ai_service.extract_keywords_from_job_description(job_description)
        return {"keywords": keywords}
    except Exception as e:
        logger.error(f"Error extracting keywords: {e}")
        raise HTTPException(status_code=500, detail=f"Keyword extraction failed: {str(e)}")

