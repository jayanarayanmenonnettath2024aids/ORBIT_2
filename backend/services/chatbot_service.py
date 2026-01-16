"""
Chatbot Service - AI assistant for ORBIT platform
"""

import google.generativeai as genai
import os
import requests
from bs4 import BeautifulSoup
import re


class ChatbotService:
    def __init__(self):
        """Initialize chatbot service with Gemini AI and load balancing"""
        # Configure Gemini API with load balancing
        gemini_key = os.getenv('GEMINI_API_KEY')
        gemini_key_2 = os.getenv('GEMINI_API_KEY_2')
        
        # Setup key rotation for load balancing
        self.api_keys = [k for k in [gemini_key, gemini_key_2] if k]
        if not self.api_keys:
            print("⚠️  Warning: No GEMINI_API_KEY configured")
        else:
            print(f"✓ Load balancing enabled with {len(self.api_keys)} Gemini API keys for chatbot")
        
        self.current_key_index = 0
        self.conversation_history = {}
        
        # Initialize with first key
        if self.api_keys:
            genai.configure(api_key=self.api_keys[0])
            self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def _rotate_api_key(self):
        """Rotate to next API key for load balancing"""
        if len(self.api_keys) > 1:
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            genai.configure(api_key=self.api_keys[self.current_key_index])
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            print(f"🔄 Rotated to API key #{self.current_key_index + 1}")
    
    def _scrape_webpage(self, url):
        """Scrape webpage content for analysis"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            print(f"🌐 Scraping: {url}")
            response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            print(f"✅ HTTP {response.status_code} - Content length: {len(response.content)} bytes")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            print(f"📄 Extracted {len(text)} chars of text")
            
            # Limit to first 5000 characters to avoid token limits
            if len(text) < 200:
                print(f"⚠️  Content too short ({len(text)} chars) - website likely uses JavaScript rendering")
                return f"""Website uses JavaScript rendering and couldn't be fully scraped. 

**Please provide these details manually:**
- Competition title
- Deadline date
- Eligibility criteria (age, education, team size, etc.)
- Required skills or themes
- Any specific requirements

Or you can copy-paste the key details from the page!"""
            
            return text[:5000]
        except Exception as e:
            error_msg = f"Error scraping webpage: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
    
    def chat(self, user_id, message, context=None):
        """
        Handle chat message with context awareness
        
        Args:
            user_id: User identifier
            message: User's message
            context: Optional context (profile, opportunity)
        
        Returns:
            Dictionary with response and metadata
        """
        try:
            print(f"💬 Chatbot request from user {user_id}: {message[:100]}...")
            
            # Get or create conversation history
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            
            # Check if message contains a URL
            url_pattern = r'https?://[^\s]+'
            urls = re.findall(url_pattern, message)
            scraped_content = ""
            
            if urls:
                print(f"🔗 Detected URL in message, scraping: {urls[0]}")
                scraped_content = self._scrape_webpage(urls[0])
                print(f"📄 Scraped content length: {len(scraped_content)} chars")
                message += f"\n\n[Webpage Content Extracted]:\n{scraped_content}"
            
            # Build context-aware prompt
            system_prompt = self._build_system_prompt(context)
            full_prompt = f"{system_prompt}\n\nUser: {message}"
            
            # Add conversation history
            if self.conversation_history[user_id]:
                history_text = "\n".join([
                    f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
                    for msg in self.conversation_history[user_id][-5:]  # Last 5 messages
                ])
                full_prompt = f"Previous conversation:\n{history_text}\n\n{full_prompt}"
            
            # Generate response
            print(f"🤖 Calling Gemini AI...")
            
            # Try with retry and key rotation
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    response = self.model.generate_content(full_prompt)
                    response_text = response.text
                    print(f"✅ Got response: {response_text[:100]}...")
                    break
                except Exception as api_error:
                    if "429" in str(api_error) or "quota" in str(api_error).lower():
                        print(f"⚠️  Quota exceeded on attempt {attempt + 1}, rotating key...")
                        self._rotate_api_key()
                        if attempt == max_retries - 1:
                            return {
                                'response': "I'm currently experiencing high demand. Please try again in a minute. ⏰",
                                'error': 'quota_exceeded'
                            }
                    else:
                        raise
            else:
                # All retries exhausted
                return {
                    'response': "🚫 **API Quota Exhausted**\n\nBoth Gemini API keys have reached their limits.\n\n**Solutions:**\n1. Wait 1 minute and try again (if rate limit)\n2. Wait until tomorrow (if daily quota hit)\n3. Get new API keys from https://makersuite.google.com/app/apikey\n\n**Meanwhile, try:**\n- Just tell me the competition details (deadline, eligibility, requirements) and I'll help assess your eligibility!\n- Or use the 'Check Eligibility' button on opportunity cards",
                    'error': 'quota_exceeded'
                }
            
            # Update conversation history
            self.conversation_history[user_id].append({
                'role': 'user',
                'content': message
            })
            self.conversation_history[user_id].append({
                'role': 'assistant',
                'content': response_text
            })
            
            return {
                'response': response_text,
                'context_used': context is not None
            }
        except Exception as e:
            print(f"❌ Chatbot error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'response': "I'm having trouble processing that. Could you rephrase?",
                'error': str(e)
            }
    
    def _build_system_prompt(self, context):
        """Build context-aware system prompt"""
        base_prompt = """You are ORBIT's AI assistant, helping students find and succeed in opportunities.

Your capabilities:
- Explain eligibility requirements
- Suggest profile improvements
- Answer questions about opportunities
- Provide application tips
- Help interpret scores and recommendations
- Analyze competition posters/PDFs shared by users
- SCRAPE AND ANALYZE websites when users share links (fetch content, extract details, check eligibility)
- Extract information from competition announcements
- Compare user profile with opportunity requirements

You CANNOT:
- Auto-apply to opportunities
- Fill application forms
- Make final decisions for users

When users share a competition/opportunity link:
1. Fetch and analyze the webpage content
2. Extract: Title, Deadline, Eligibility criteria, Requirements, Prizes
3. Compare with user's profile (education, skills, experience)
4. Provide eligibility assessment (Eligible/Not Eligible/Partially Eligible)
5. List what matches and what's missing
6. Suggest improvements if needed

Be helpful, concise, and encourage user initiative."""
        
        if context:
            if 'profile' in context:
                profile = context['profile']
                education = profile.get('education', {})
                skills = profile.get('skills', {})
                skills_summary = []
                if isinstance(skills, dict):
                    for skill_list in skills.values():
                        if isinstance(skill_list, list):
                            skills_summary.extend(skill_list)
                skills_str = ', '.join(skills_summary[:5]) if skills_summary else 'N/A'
                
                base_prompt += f"\n\nUser Profile Summary:\n- Education: {education.get('degree', 'N/A')} in {education.get('major', 'N/A')}\n- Skills: {skills_str}"
            
            if 'opportunity' in context:
                opp = context['opportunity']
                base_prompt += f"\n\nCurrent Opportunity Context:\n- Title: {opp.get('title', 'N/A')}\n- Type: {opp.get('type', 'N/A')}"
        
        return base_prompt
    
    def clear_history(self, user_id):
        """Clear conversation history for user"""
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]
        return {'success': True}
