import os
import re
from typing import List, Dict, Tuple, Any
from openai import OpenAI
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your_openai_api_key_here":
            self.client = None
            logger.warning("OpenAI API key not configured. AI features will be disabled.")
        else:
            try:
                self.client = OpenAI(api_key=api_key)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.client = None
        self.model = "gpt-4-turbo-preview"
    
    def extract_keywords_from_job_description(self, job_description: str) -> List[Dict[str, Any]]:
        """Extract important keywords and skills from job description"""
        if not self.client:
            logger.warning("OpenAI client not available. Using fallback keyword extraction.")
            return self._fallback_keyword_extraction(job_description)
        
        prompt = f"""
        Analyze the following job description and extract the most important keywords, skills, and requirements.
        Focus on technical skills, soft skills, tools, technologies, and qualifications.
        
        Job Description:
        {job_description}
        
        Return a JSON array with objects containing:
        - keyword: the keyword/skill
        - importance: importance score (0-1)
        - category: "technical", "soft_skill", "tool", "qualification", or "experience"
        
        Format as JSON array only.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            # Parse the JSON response
            import json
            keywords_data = json.loads(response.choices[0].message.content)
            return keywords_data
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return self._fallback_keyword_extraction(job_description)
    
    def analyze_resume_keywords(self, resume_text: str, keywords: List[str]) -> Dict[str, Any]:
        """Analyze which keywords are present in the resume"""
        keyword_analysis = {}
        
        for keyword in keywords:
            # Case-insensitive search
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            matches = pattern.findall(resume_text)
            frequency = len(matches)
            
            # Get context around matches
            context = []
            for match in pattern.finditer(resume_text):
                start = max(0, match.start() - 50)
                end = min(len(resume_text), match.end() + 50)
                context.append(resume_text[start:end].strip())
            
            keyword_analysis[keyword] = {
                "found": frequency > 0,
                "frequency": frequency,
                "context": context[:3]  # Limit to first 3 contexts
            }
        
        return keyword_analysis
    
    def tailor_resume(self, resume_text: str, job_description: str, target_role: str = None) -> str:
        """Tailor the resume to better match the job description"""
        if not self.client:
            logger.warning("OpenAI client not available. Returning original resume.")
            return resume_text
        
        prompt = f"""
        You are an expert resume writer and career coach. Your task is to optimize a resume to better match a specific job description.
        
        Job Description:
        {job_description}
        
        Target Role: {target_role or "Not specified"}
        
        Original Resume:
        {resume_text}
        
        Please optimize the resume by:
        1. Incorporating relevant keywords from the job description naturally
        2. Highlighting relevant experience and skills
        3. Using action verbs and quantifiable achievements
        4. Ensuring ATS (Applicant Tracking System) compatibility
        5. Maintaining professional tone and formatting
        
        Return the optimized resume text. Keep the same general structure but enhance the content to better match the job requirements.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error tailoring resume: {e}")
            return resume_text
    
    def generate_improvement_suggestions(self, resume_text: str, job_description: str, keyword_analysis: Dict[str, Any]) -> List[str]:
        """Generate specific suggestions for resume improvement"""
        if not self.client:
            logger.warning("OpenAI client not available. Using fallback suggestions.")
            return self._fallback_suggestions(resume_text, job_description, keyword_analysis)
        
        missing_keywords = [kw for kw, data in keyword_analysis.items() if not data["found"]]
        
        prompt = f"""
        Based on the following information, provide specific, actionable suggestions to improve the resume:
        
        Job Description:
        {job_description}
        
        Resume:
        {resume_text}
        
        Missing Keywords: {', '.join(missing_keywords[:10])}
        
        Provide 5-7 specific suggestions that would help this resume better match the job requirements.
        Focus on practical improvements that can be implemented.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4
            )
            
            suggestions = response.choices[0].message.content.strip().split('\n')
            return [s.strip() for s in suggestions if s.strip()]
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return self._fallback_suggestions(resume_text, job_description, keyword_analysis)
    
    def calculate_confidence_score(self, keyword_analysis: Dict[str, Any], keywords: List[Dict[str, Any]]) -> float:
        """Calculate a confidence score for how well the resume matches the job"""
        if not keywords:
            return 0.0
        
        total_importance = sum(kw.get('importance', 0) for kw in keywords)
        if total_importance == 0:
            return 0.0
        
        matched_importance = 0
        for kw_data in keywords:
            keyword = kw_data.get('keyword', '')
            importance = kw_data.get('importance', 0)
            
            if keyword in keyword_analysis and keyword_analysis[keyword]['found']:
                matched_importance += importance
        
        return min(1.0, matched_importance / total_importance)
    
    def _fallback_keyword_extraction(self, job_description: str) -> List[Dict[str, Any]]:
        """Fallback keyword extraction when OpenAI is not available"""
        # Simple keyword extraction based on common patterns
        import re
        
        # Common technical skills
        technical_keywords = [
            'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'aws', 'docker',
            'kubernetes', 'machine learning', 'ai', 'data science', 'git', 'agile',
            'scrum', 'api', 'rest', 'graphql', 'html', 'css', 'typescript', 'angular',
            'vue.js', 'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch',
            'kafka', 'spark', 'hadoop', 'tensorflow', 'pytorch', 'scikit-learn'
        ]
        
        # Common soft skills
        soft_skills = [
            'leadership', 'communication', 'teamwork', 'problem solving', 'analytical',
            'creative', 'organized', 'detail-oriented', 'time management', 'collaboration',
            'mentoring', 'project management', 'customer service', 'sales', 'marketing'
        ]
        
        # Common tools
        tools = [
            'jira', 'confluence', 'slack', 'teams', 'zoom', 'figma', 'sketch',
            'photoshop', 'illustrator', 'excel', 'powerpoint', 'word', 'outlook'
        ]
        
        found_keywords = []
        job_lower = job_description.lower()
        
        # Check for technical skills
        for keyword in technical_keywords:
            if keyword in job_lower:
                found_keywords.append({
                    'keyword': keyword,
                    'importance': 0.8,
                    'category': 'technical'
                })
        
        # Check for soft skills
        for keyword in soft_skills:
            if keyword in job_lower:
                found_keywords.append({
                    'keyword': keyword,
                    'importance': 0.6,
                    'category': 'soft_skill'
                })
        
        # Check for tools
        for keyword in tools:
            if keyword in job_lower:
                found_keywords.append({
                    'keyword': keyword,
                    'importance': 0.7,
                    'category': 'tool'
                })
        
        return found_keywords
    
    def _fallback_suggestions(self, resume_text: str, job_description: str, keyword_analysis: Dict[str, Any]) -> List[str]:
        """Fallback suggestions when OpenAI is not available"""
        suggestions = []
        missing_keywords = [kw for kw, data in keyword_analysis.items() if not data["found"]]
        
        if missing_keywords:
            suggestions.append(f"Add the following keywords to your resume: {', '.join(missing_keywords[:5])}")
        
        suggestions.extend([
            "Use action verbs to start bullet points (e.g., 'Developed', 'Implemented', 'Led')",
            "Include specific metrics and quantifiable achievements",
            "Ensure your resume is ATS-friendly with clear section headers",
            "Highlight relevant experience that matches the job requirements",
            "Keep bullet points concise and impactful"
        ])
        
        return suggestions
    
    def _fallback_section_analysis(self, resume_text: str) -> List[Dict[str, str]]:
        """Fallback section analysis when OpenAI is not available"""
        sections = []
        
        # Simple section detection based on common headers
        lines = resume_text.split('\n')
        current_section = "Summary"
        current_content = []
        
        section_keywords = {
            'experience': ['experience', 'work history', 'employment', 'career'],
            'education': ['education', 'academic', 'degree', 'university', 'college'],
            'skills': ['skills', 'technical skills', 'competencies', 'expertise'],
            'summary': ['summary', 'objective', 'profile', 'about'],
            'projects': ['projects', 'portfolio', 'achievements'],
            'certifications': ['certifications', 'certificates', 'licenses']
        }
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if this line is a section header
            is_header = False
            for section_name, keywords in section_keywords.items():
                if any(keyword in line_lower for keyword in keywords):
                    # Save previous section
                    if current_content:
                        sections.append({
                            'section_name': current_section.title(),
                            'content': '\n'.join(current_content).strip()
                        })
                    
                    current_section = section_name.title()
                    current_content = []
                    is_header = True
                    break
            
            if not is_header and line.strip():
                current_content.append(line)
        
        # Add the last section
        if current_content:
            sections.append({
                'section_name': current_section.title(),
                'content': '\n'.join(current_content).strip()
            })
        
        return sections
    
    def analyze_resume_sections(self, resume_text: str) -> List[Dict[str, str]]:
        """Analyze and identify different sections of the resume"""
        if not self.client:
            logger.warning("OpenAI client not available. Using fallback section analysis.")
            return self._fallback_section_analysis(resume_text)
        
        prompt = f"""
        Analyze the following resume and identify its main sections. For each section, provide:
        1. Section name (e.g., "Experience", "Education", "Skills", "Summary")
        2. The content of that section
        
        Resume:
        {resume_text}
        
        Return as JSON array with objects containing "section_name" and "content".
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            import json
            sections = json.loads(response.choices[0].message.content)
            return sections
            
        except Exception as e:
            logger.error(f"Error analyzing resume sections: {e}")
            return self._fallback_section_analysis(resume_text)

