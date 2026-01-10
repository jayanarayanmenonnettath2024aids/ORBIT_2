"""
Profile Service - Handles resume parsing and profile management
"""

import PyPDF2
import io
import re
import google.generativeai as genai
import os
import json


class ProfileService:
    def __init__(self, firebase_service):
        """
        Initialize Profile Service
        
        Args:
            firebase_service: FirebaseService instance
        """
        self.firebase = firebase_service
        
        # Configure Gemini API with load balancing
        gemini_key = os.getenv('GEMINI_API_KEY')
        gemini_key_2 = os.getenv('GEMINI_API_KEY_2')
        
        # Setup key rotation for load balancing
        self.api_keys = [k for k in [gemini_key, gemini_key_2] if k]
        if not self.api_keys:
            print("⚠️  Warning: No GEMINI_API_KEY configured")
        elif len(self.api_keys) == 2:
            print(f"✓ Load balancing enabled with {len(self.api_keys)} Gemini API keys")
        
        self.current_key_index = 0
        self._configure_current_key()
    
    def _configure_current_key(self):
        """Configure Gemini with current API key"""
        if self.api_keys:
            genai.configure(api_key=self.api_keys[self.current_key_index])
            self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def _rotate_key(self):
        """Rotate to next API key for load balancing"""
        if len(self.api_keys) > 1:
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            self._configure_current_key()
    
    
    def parse_and_create_profile(self, resume_file):
        """
        Parse resume PDF and create structured profile
        
        Args:
            resume_file: FileStorage object from Flask
        
        Returns:
            Dictionary with profile_id, profile_data, resume_summary, and resume_grade
        """
        # Extract text from PDF
        resume_text = self._extract_text_from_pdf(resume_file)
        
        # Use Gemini to parse resume into structured format
        profile_data = self._parse_resume_with_gemini(resume_text)
        
        # Generate resume evaluation (summary and grade)
        evaluation = self._evaluate_resume(resume_text, profile_data)
        
        # Store in Firebase
        result = self.firebase.create_student_profile(profile_data, resume_text)
        
        # Add evaluation to result
        result['resume_summary'] = evaluation['summary']
        result['resume_grade'] = evaluation['grade']
        result['strengths'] = evaluation['strengths']
        result['improvements'] = evaluation['improvements']
        
        return result
    
    
    def create_profile_manual(self, profile_data):
        """
        Create profile from manual input (no resume parsing)
        
        Args:
            profile_data: Dictionary with structured profile
        
        Returns:
            Dictionary with profile_id and profile_data
        """
        # Validate profile structure
        self._validate_profile_structure(profile_data)
        
        # Store in Firebase
        result = self.firebase.create_student_profile(profile_data)
        
        return result
    
    
    def get_profile(self, profile_id):
        """
        Get profile by ID
        """
        return self.firebase.get_student_profile(profile_id)
    
    
    def update_profile(self, profile_id, profile_data):
        """
        Update existing profile
        """
        self._validate_profile_structure(profile_data)
        return self.firebase.update_student_profile(profile_id, profile_data)
    
    
    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================
    
    def _extract_text_from_pdf(self, pdf_file):
        """
        Extract text from PDF file
        
        Args:
            pdf_file: FileStorage object
        
        Returns:
            Extracted text as string
        """
        try:
            # Read PDF
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
            
            # Extract text from all pages
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text() + '\n'
            
            return text.strip()
            
        except Exception as e:
            raise Exception(f"Failed to parse PDF: {str(e)}")
    
    
    def _parse_resume_with_gemini(self, resume_text):
        """
        Use Gemini API to parse resume text into structured JSON
        
        Args:
            resume_text: Raw text extracted from resume
        
        Returns:
            Structured profile dictionary
        """
        prompt = f"""Extract information from this resume and return ONLY valid JSON.

RESUME:
{resume_text}

Return this exact JSON structure with NO extra text before or after:
{{
  "education": {{
    "degree": "B.Tech",
    "major": "Computer Science",
    "institution": "College Name",
    "year": "2nd year",
    "cgpa_or_percentage": "8.5"
  }},
  "skills": {{
    "programming_languages": ["Python", "Java"],
    "frameworks": ["React", "Django"],
    "tools": ["Git", "Docker"],
    "domains": ["Machine Learning", "Web Development"]
  }},
  "experience": [
    {{
      "type": "internship",
      "title": "Software Intern",
      "organization": "Company",
      "duration": "3 months",
      "description": "Built web apps"
    }}
  ],
  "achievements": ["Won hackathon", "1000+ problems solved"],
  "interests": ["AI", "Web Development"],
  "self_description": "Brief about section from resume"
}}

CRITICAL RULES:
1. Extract ALL information from the resume
2. Fill every field you can find
3. Use empty arrays [] if nothing found, NOT empty strings
4. Return ONLY the JSON object
5. No markdown, no explanation, JUST JSON
"""
        
        try:
            print(f"📄 Parsing resume with Gemini (length: {len(resume_text)} chars)")
            
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.1,  # Lower temperature for more accurate extraction
                    "max_output_tokens": 2048,
                }
            )
            
            # Rotate API key for load balancing
            self._rotate_key()
            
            # Extract JSON from response
            response_text = response.text.strip()
            print(f"✓ Gemini responded (length: {len(response_text)} chars)")
            print(f"Response preview: {response_text[:200]}...")
            
            # Remove markdown code block if present
            if response_text.startswith('```'):
                response_text = re.sub(r'^```(?:json)?\n', '', response_text)
                response_text = re.sub(r'\n```$', '', response_text)
            
            # Fix common JSON issues
            response_text = re.sub(r',\s*}', '}', response_text)  # Remove trailing commas before }
            response_text = re.sub(r',\s*]', ']', response_text)  # Remove trailing commas before ]
            
            # Parse JSON
            profile_data = json.loads(response_text)
            
            # Validate we got actual data
            has_content = False
            if profile_data.get('education', {}).get('degree'):
                has_content = True
            if profile_data.get('skills', {}).get('programming_languages'):
                has_content = True
            if profile_data.get('experience'):
                has_content = True
                
            if not has_content:
                print("⚠️  Parsed JSON but all fields are empty, using fallback")
                return self._create_fallback_profile(resume_text)
            
            print(f"✓ Successfully parsed resume with content")
            return profile_data
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"Response was: {response_text[:500] if 'response_text' in locals() else 'No response'}")
            return self._create_fallback_profile(resume_text)
        
        except Exception as e:
            print(f"❌ Failed to parse resume with Gemini: {str(e)}")
            return self._create_fallback_profile(resume_text)
    
    
    def _create_fallback_profile(self, resume_text):
        """
        Create profile with basic extraction when Gemini parsing fails
        """
        print("⚠️  Using fallback profile extraction")
        
        # Try to extract some basic info with regex
        skills_found = []
        frameworks_found = []
        tools_found = []
        
        # Common programming languages
        prog_langs = ['Python', 'Java', 'JavaScript', 'C++', 'C', 'TypeScript', 'Go', 'Rust', 'PHP', 'Ruby', 'Swift', 'Kotlin']
        for lang in prog_langs:
            if lang in resume_text:
                skills_found.append(lang)
        
        # Common frameworks
        frameworks = ['React', 'Angular', 'Vue', 'Django', 'Flask', 'FastAPI', 'Spring', 'Node.js', 'Express', 'Next.js', 'Streamlit']
        for fw in frameworks:
            if fw in resume_text:
                frameworks_found.append(fw)
        
        # Common tools
        tools = ['Git', 'Docker', 'Kubernetes', 'AWS', 'Azure', 'Linux', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis']
        for tool in tools:
            if tool in resume_text:
                tools_found.append(tool)
        
        # Extract education info
        degree = ""
        institution = ""
        if 'B.Tech' in resume_text or 'BTech' in resume_text:
            degree = "B.Tech"
        elif 'M.Tech' in resume_text or 'MTech' in resume_text:
            degree = "M.Tech"
        elif 'B.E' in resume_text or 'BE' in resume_text:
            degree = "B.E"
        
        # Try to find CGPA
        cgpa_match = re.search(r'CGPA[:\s]+([0-9.]+)', resume_text, re.IGNORECASE)
        cgpa = cgpa_match.group(1) if cgpa_match else ""
        
        return {
            "education": {
                "degree": degree,
                "major": "",
                "institution": institution,
                "year": "",
                "cgpa_or_percentage": cgpa
            },
            "skills": {
                "programming_languages": skills_found,
                "frameworks": frameworks_found,
                "tools": tools_found,
                "domains": []
            },
            "experience": [],
            "achievements": [],
            "interests": [],
            "self_description": resume_text[:500]  # First 500 chars as description
        }
    
    
    def _validate_profile_structure(self, profile_data):
        """
        Validate that profile has required structure
        
        Raises:
            Exception if structure is invalid
        """
        required_keys = ['education', 'skills', 'experience', 'interests']
        
        for key in required_keys:
            if key not in profile_data:
                raise Exception(f"Profile missing required field: {key}")
        
        # Validate education
        if not isinstance(profile_data['education'], dict):
            raise Exception("Education must be a dictionary")
        
        # Validate skills
        if not isinstance(profile_data['skills'], dict):
            raise Exception("Skills must be a dictionary")
        
        # Validate experience
        if not isinstance(profile_data['experience'], list):
            raise Exception("Experience must be an array")
        
        # Validate interests
        if not isinstance(profile_data['interests'], list):
            raise Exception("Interests must be an array")
        
        return True
    
    
    def _evaluate_resume(self, resume_text, profile_data):
        """
        Evaluate resume and provide customized, detailed summary, grade, and feedback
        
        Args:
            resume_text: Raw resume text
            profile_data: Parsed profile data
        
        Returns:
            Dictionary with summary, grade, strengths, improvements
        """
        # Extract key profile details for context
        edu = profile_data.get('education', {})
        skills = profile_data.get('skills', {})
        experience = profile_data.get('experience', [])
        achievements = profile_data.get('achievements', [])
        
        degree = edu.get('degree', 'Unknown')
        major = edu.get('major', 'Unknown')
        year = edu.get('year', 'Unknown')
        cgpa = edu.get('cgpa_or_percentage', 'Not mentioned')
        
        prog_langs = ', '.join(skills.get('programming_languages', [])) or 'None listed'
        frameworks = ', '.join(skills.get('frameworks', [])) or 'None listed'
        exp_count = len(experience)
        achievement_count = len(achievements)
        
        prompt = f"""You are an expert career counselor evaluating a SPECIFIC student's resume. Provide PERSONALIZED feedback based on their actual profile.

STUDENT PROFILE:
- Education: {year} {degree} in {major}
- CGPA: {cgpa}
- Programming Languages: {prog_langs}
- Frameworks/Tools: {frameworks}
- Projects/Experience: {exp_count} entries
- Achievements: {achievement_count} items

FULL RESUME TEXT:
{resume_text}

Provide a CUSTOMIZED evaluation in this EXACT JSON format:
{{
  "grade": "A+",
  "summary": "Write a SPECIFIC 2-3 sentence summary mentioning their actual degree, major, year, key skills, and experience level. Make it personal, not generic.",
  "strengths": ["Specific strength 1 with actual details", "Specific strength 2 with actual details", "Specific strength 3 with actual details"],
  "improvements": ["Specific actionable improvement 1", "Specific actionable improvement 2"]
}}

GRADING CRITERIA (Be strict and realistic):
- A+ (95-100): Exceptional - Multiple impressive projects, strong CGPA (>8.5), diverse tech stack, notable achievements, internship experience
- A (90-94): Excellent - Good projects with measurable impact, strong academics (>8.0), solid skills, some achievements
- A- (85-89): Very Good - 2-3 quality projects, good CGPA (>7.5), relevant skills, clear career direction
- B+ (80-84): Good - 1-2 decent projects, average+ CGPA (>7.0), some relevant skills, shows initiative
- B (75-79): Decent - Basic projects, average CGPA (>6.5), limited skills, needs more experience
- B- (70-74): Below Average - Minimal projects, weak CGPA (<6.5), few skills, needs significant work
- C+ (65-69): Weak - Almost no practical experience, poor academics, very limited skills
- C or below (60-64): Needs Major Improvement - No projects, weak foundation, must rebuild from basics

IMPORTANT:
1. Mention their ACTUAL degree, major, and year in the summary (e.g., "As a second-year B.Tech Computer Science student...")
2. Reference their SPECIFIC skills in strengths (e.g., "Strong Python and React.js expertise shown in projects")
3. Call out ACTUAL gaps (e.g., "Add CI/CD experience" not just "Add more experience")
4. Be honest about the grade - most student resumes are B/B+, not A+
5. If CGPA is below 7.0, mention academics need improvement
6. If no projects, that's a critical gap - state it clearly

Return ONLY the JSON, no extra text."""
        
        try:
            print("📊 Evaluating resume with Gemini...")
            
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 1024,
                }
            )
            
            self._rotate_key()
            
            response_text = response.text.strip()
            
            # Clean up response
            if response_text.startswith('```'):
                response_text = re.sub(r'^```(?:json)?\n', '', response_text)
                response_text = re.sub(r'\n```$', '', response_text)
            
            response_text = re.sub(r',\s*}', '}', response_text)
            response_text = re.sub(r',\s*]', ']', response_text)
            
            evaluation = json.loads(response_text)
            
            print(f"✓ Resume evaluated: Grade {evaluation.get('grade', 'N/A')}")
            
            return {
                'grade': evaluation.get('grade', 'B+'),
                'summary': evaluation.get('summary', 'Good candidate with potential for growth.'),
                'strengths': evaluation.get('strengths', []),
                'improvements': evaluation.get('improvements', [])
            }
            
        except Exception as e:
            print(f"⚠️  Resume evaluation failed: {e}")
            # Return default evaluation
            return {
                'grade': 'B+',
                'summary': 'Your profile shows promise. Continue building your skills and experience through projects and internships.',
                'strengths': ['Good foundation in technical skills', 'Demonstrates learning ability'],
                'improvements': ['Add more project experience', 'Highlight measurable achievements']
            }
    
    
    def get_profile_summary(self, profile_data):
        """
        Generate a brief text summary of profile (for prompts)
        
        Args:
            profile_data: Structured profile dictionary
        
        Returns:
            String summary
        """
        edu = profile_data.get('education', {})
        skills = profile_data.get('skills', {})
        experience = profile_data.get('experience', [])
        
        summary_parts = []
        
        # Education
        if edu.get('degree'):
            edu_str = f"{edu.get('year', '')} {edu.get('degree', '')} in {edu.get('major', '')}"
            if edu.get('institution'):
                edu_str += f" from {edu.get('institution')}"
            summary_parts.append(edu_str)
        
        # Skills
        all_skills = []
        if skills.get('programming_languages'):
            all_skills.extend(skills['programming_languages'])
        if skills.get('frameworks'):
            all_skills.extend(skills['frameworks'])
        if all_skills:
            summary_parts.append(f"Skills: {', '.join(all_skills[:5])}")
        
        # Experience
        if experience:
            exp_count = len(experience)
            summary_parts.append(f"{exp_count} experience entries")
        
        return '; '.join(summary_parts)
