import os
import re
import json
import requests
from typing import List, Dict, Tuple, Any
from loguru import logger

class OllamaService:
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.model = "llama2"
        self.client_available = self._check_ollama_connection()
        
        if self.client_available:
            logger.info("Ollama client initialized successfully")
        else:
            logger.warning("Ollama not available. AI features will be disabled.")
    
    def _check_ollama_connection(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama connection failed: {e}")
            return False
    
    def _call_ollama(self, prompt: str, system_prompt: str = None) -> str:
        """Make a call to Ollama API"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["response"]
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return ""
                
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            return ""
    
    def extract_keywords_from_job_description(self, job_description: str) -> List[Dict[str, Any]]:
        """Extract important keywords and skills from job description using Ollama"""
        if not self.client_available:
            logger.warning("Ollama client not available. Using fallback keyword extraction.")
            return self._fallback_keyword_extraction(job_description)
        
        system_prompt = """You are an expert at analyzing job descriptions and extracting key skills and requirements. 
        Return your response as a JSON array with objects containing: keyword, importance (0-1), and category (technical, soft_skill, tool, qualification, or experience).
        Only return valid JSON, no other text."""
        
        prompt = f"""
        Analyze this job description and extract the most important keywords, skills, and requirements:
        
        {job_description}
        
        Return as JSON array with objects: [{{"keyword": "skill", "importance": 0.8, "category": "technical"}}]
        """
        
        try:
            response = self._call_ollama(prompt, system_prompt)
            
            # Try to extract JSON from response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                keywords_data = json.loads(json_match.group())
                return keywords_data
            else:
                # Fallback: extract keywords manually
                return self._fallback_keyword_extraction(job_description)
                
        except Exception as e:
            logger.error(f"Error extracting keywords with Ollama: {e}")
            return self._fallback_keyword_extraction(job_description)
    
    def tailor_resume(self, resume_text: str, job_description: str, target_role: str = None) -> str:
        """Tailor the resume to better match the job description using Ollama"""
        if not self.client_available:
            logger.warning("Ollama client not available. Returning original resume.")
            return resume_text
        
        system_prompt = """You are an expert resume writer. Rewrite the resume to better match the job description while maintaining truthfulness and professional tone."""
        
        prompt = f"""
        Job Description:
        {job_description}
        
        Original Resume:
        {resume_text}
        
        Rewrite this resume to better match the job description. Focus on:
        1. Highlighting relevant skills and experiences
        2. Using keywords from the job description
        3. Emphasizing achievements that align with the role
        4. Maintaining professional tone and truthfulness
        
        Return only the rewritten resume text, no explanations.
        """
        
        try:
            tailored_resume = self._call_ollama(prompt, system_prompt)
            if tailored_resume and len(tailored_resume) > 100:
                return tailored_resume
            else:
                return resume_text
        except Exception as e:
            logger.error(f"Error tailoring resume with Ollama: {e}")
            return resume_text
    
    def generate_improvement_suggestions(self, resume_text: str, job_description: str, keyword_matches: Dict[str, Any]) -> List[str]:
        """Generate improvement suggestions using Ollama"""
        if not self.client_available:
            logger.warning("Ollama client not available. Using fallback suggestions.")
            return self._fallback_suggestions(resume_text, job_description, keyword_matches)
        
        system_prompt = """You are a career coach and resume expert. Provide specific, actionable suggestions for improving resumes."""
        
        prompt = f"""
        Resume:
        {resume_text}
        
        Job Description:
        {job_description}
        
        Keyword Analysis:
        {json.dumps(keyword_matches, indent=2)}
        
        Provide 5-7 specific, actionable suggestions to improve this resume for this job. 
        Focus on:
        1. Adding missing keywords
        2. Improving bullet points
        3. Quantifying achievements
        4. ATS optimization
        5. Professional presentation
        
        Return as a numbered list of suggestions.
        """
        
        try:
            suggestions_text = self._call_ollama(prompt, system_prompt)
            
            # Parse suggestions into a list
            suggestions = []
            lines = suggestions_text.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    # Remove numbering/bullets and clean up
                    clean_line = re.sub(r'^[\d\-•\.\s]+', '', line).strip()
                    if clean_line and len(clean_line) > 10:
                        suggestions.append(clean_line)
            
            if suggestions:
                return suggestions[:7]  # Limit to 7 suggestions
            else:
                return self._fallback_suggestions(resume_text, job_description, keyword_matches)
                
        except Exception as e:
            logger.error(f"Error generating suggestions with Ollama: {e}")
            return self._fallback_suggestions(resume_text, job_description, keyword_matches)
    
    def analyze_resume_sections(self, resume_text: str) -> Dict[str, Any]:
        """Analyze different sections of the resume using Ollama"""
        if not self.client_available:
            logger.warning("Ollama client not available. Using fallback section analysis.")
            return self._fallback_section_analysis(resume_text)
        
        system_prompt = """You are an expert resume analyzer. Analyze resume sections and provide insights in JSON format."""
        
        prompt = f"""
        Analyze this resume and provide insights about each section:
        
        {resume_text}
        
        Return as JSON with sections: experience, education, skills, summary, strengths, weaknesses, suggestions.
        """
        
        try:
            response = self._call_ollama(prompt, system_prompt)
            
            # Try to extract JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                return analysis
            else:
                return self._fallback_section_analysis(resume_text)
                
        except Exception as e:
            logger.error(f"Error analyzing sections with Ollama: {e}")
            return self._fallback_section_analysis(resume_text)
    
    def calculate_confidence_score(self, keyword_matches: Dict[str, Any], missing_keywords: List[str], total_keywords: int) -> float:
        """Calculate confidence score based on keyword matches"""
        if total_keywords == 0:
            return 0.0
        
        matched_count = len([k for k, v in keyword_matches.items() if v.get('found', False)])
        base_score = matched_count / total_keywords
        
        # Bonus for high-frequency matches
        frequency_bonus = 0
        for keyword, data in keyword_matches.items():
            if data.get('found', False):
                frequency = data.get('frequency', 0)
                if frequency > 1:
                    frequency_bonus += min(0.1, frequency * 0.02)
        
        final_score = min(1.0, base_score + frequency_bonus)
        return round(final_score, 3)
    
    # Fallback methods (same as original)
    def _fallback_keyword_extraction(self, job_description: str) -> List[Dict[str, Any]]:
        """Basic keyword extraction without AI"""
        # Common technical keywords
        technical_keywords = [
            'python', 'java', 'javascript', 'sql', 'html', 'css', 'react', 'node.js', 'aws', 'azure',
            'machine learning', 'ai', 'data science', 'analytics', 'database', 'api', 'git', 'docker',
            'kubernetes', 'agile', 'scrum', 'project management', 'leadership', 'communication'
        ]
        
        keywords = []
        job_lower = job_description.lower()
        
        for keyword in technical_keywords:
            if keyword in job_lower:
                keywords.append({
                    "keyword": keyword,
                    "importance": 0.8,
                    "category": "technical"
                })
        
        return keywords
    
    def _fallback_suggestions(self, resume_text: str, job_description: str, keyword_matches: Dict[str, Any]) -> List[str]:
        """Basic improvement suggestions without AI"""
        suggestions = []
        
        # Check for missing keywords
        missing_keywords = [k for k, v in keyword_matches.items() if not v.get('found', False)]
        if missing_keywords:
            suggestions.append(f"Add the following keywords to your resume: {', '.join(missing_keywords[:3])}")
        
        # Generic suggestions
        suggestions.extend([
            "Use action verbs to start bullet points (e.g., 'Developed', 'Implemented', 'Led')",
            "Include specific metrics and quantifiable achievements",
            "Ensure your resume is ATS-friendly with clear section headers",
            "Highlight relevant experience that matches the job requirements",
            "Keep bullet points concise and impactful"
        ])
        
        return suggestions[:6]
    
    def _fallback_section_analysis(self, resume_text: str) -> Dict[str, Any]:
        """Basic section analysis without AI"""
        return {
            "experience": "Experience section found",
            "education": "Education section found", 
            "skills": "Skills section found",
            "summary": "Resume appears complete",
            "strengths": ["Professional formatting", "Clear structure"],
            "weaknesses": ["Consider adding more quantifiable achievements"],
            "suggestions": ["Add specific metrics to bullet points"]
        }
