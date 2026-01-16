# ORBIT - 24 Hour Hackathon Implementation Plan

**Judge Feedback:** "Nothing unique, can be done with ChatGPT"  
**Goal:** Make ORBIT stand out with unique features that demonstrate system intelligence beyond AI prompts

---

## 🚨 CRITICAL CONSTRAINTS

- ❌ **NO AUTO-APPLY FUNCTIONALITY** - We only assist, never automate applications
- ❌ **NO PREFILL FEATURES** - No form auto-filling for applications
- ✅ **AI CHATBOT** - Must integrate AI chatbot within the system
- ✅ **FIX GOOGLE SEARCH** - Must improve accuracy and relevance

---

## 📋 PART 1: FIXES TO EXISTING CODE

### 1.1 Fix Google Search Accuracy (CRITICAL - 2 hours)
**File:** `backend/services/opportunity_service.py`

**Current Issues:**
- Query enhancement is too aggressive (lines 186-230)
- Filters are too strict, removing valid results
- No relevance scoring for results
- Poor domain-specific targeting

**Changes Needed:**

**Location: Lines 186-230** - Replace `_enhance_query` method
```python
def _enhance_query(self, query, filters):
    """
    SIMPLIFIED query enhancement - less aggressive
    """
    enhanced_parts = [query]
    
    # Add year filter if specified
    if filters and filters.get('deadline_year'):
        year = filters['deadline_year']
        enhanced_parts.append(f"{year}")
    
    # Simple domain targeting for common categories
    category_domains = {
        'hackathon': 'devpost.com OR devfolio.co OR unstop.com',
        'scholarship': 'scholars4dev.com OR opportunitydesk.org',
        'internship': 'internshala.com OR linkedin.com/jobs',
        'research': 'researchgate.net OR scholar.google.com'
    }
    
    query_lower = query.lower()
    for category, domains in category_domains.items():
        if category in query_lower:
            enhanced_parts.append(f"site:({domains})")
            break
    
    return ' '.join(enhanced_parts)
```

**Location: Lines 300-340** - Replace `_parse_search_results` method
```python
def _parse_search_results(self, items):
    """
    Parse search results WITH relevance scoring
    """
    opportunities = []
    
    for item in items:
        title = item.get('title', 'No title')
        link = item.get('link', '')
        snippet = item.get('snippet', 'No description')
        
        # Calculate relevance score (0-100)
        relevance_score = self._calculate_relevance_score(item)
        
        # Less strict filtering - accept if score > 30
        if relevance_score < 30:
            continue
        
        opportunity = {
            'title': title,
            'link': link,
            'description': snippet,
            'source': self._extract_domain(link),
            'relevance_score': relevance_score,
            'discovered_date': datetime.now().isoformat()
        }
        
        opportunities.append(opportunity)
    
    # Sort by relevance score
    opportunities.sort(key=lambda x: x['relevance_score'], reverse=True)
    return opportunities
```

**Location: After `_parse_search_results` method** - Add NEW method
```python
def _calculate_relevance_score(self, item):
    """
    Calculate relevance score (0-100) based on multiple factors
    """
    score = 50  # Base score
    
    title = item.get('title', '').lower()
    snippet = item.get('snippet', '').lower()
    link = item.get('link', '').lower()
    
    # High-value keywords boost score
    high_value_keywords = ['apply', 'deadline', 'eligibility', 'register', 'prize', 'stipend', '2026']
    for keyword in high_value_keywords:
        if keyword in title:
            score += 5
        if keyword in snippet:
            score += 3
    
    # Trusted domains get boost
    trusted_domains = ['devpost.com', 'devfolio.co', 'unstop.com', 'internshala.com', 
                      'scholars4dev.com', 'opportunitydesk.org', 'linkedin.com']
    for domain in trusted_domains:
        if domain in link:
            score += 15
            break
    
    # Penalty for irrelevant indicators
    spam_indicators = ['login', 'signin', 'profile', 'settings', 'terms', 'privacy']
    for indicator in spam_indicators:
        if indicator in link:
            score -= 20
    
    return max(0, min(100, score))

def _extract_domain(self, url):
    """Extract domain from URL"""
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc
    except:
        return 'Unknown'
```

---

### 1.2 Improve Resume Evaluation (1 hour)
**File:** `backend/services/profile_service.py`

**Location: Lines 150-180** - Update `_evaluate_resume` method prompt

**Change the Gemini prompt to include more detailed evaluation:**
```python
prompt = f"""
You are an expert career advisor evaluating a student resume. Provide:

1. Overall Score (0-100) based on:
   - Skills relevance and depth (30%)
   - Project quality and impact (25%)
   - Experience relevance (20%)
   - Education and achievements (15%)
   - Resume presentation (10%)

2. Detailed Strengths (3-5 specific points)
3. Critical Gaps (3-5 areas needing improvement)
4. Actionable Recommendations (3-5 specific next steps)
5. Competitive Analysis (how they compare to peers)

Resume Content:
{text[:3000]}

Return as JSON with fields: overall_score, strengths[], gaps[], recommendations[], competitive_position
"""
```

---

## 🎯 PART 2: NEW FEATURES TO IMPLEMENT

### Priority 1: MUST HAVE (Complete First 12 Hours)

### 2.1 Application Tracker Dashboard (4 hours)

**Backend Changes:**

**File:** `backend/services/firebase_service.py`
**Add NEW method after existing methods:**
```python
# Application Tracker methods
def create_application(self, user_id, application_data):
    """Create new application tracking entry"""
    try:
        application_ref = self.db.collection('applications').document()
        application_data.update({
            'user_id': user_id,
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP
        })
        application_ref.set(application_data)
        return {'id': application_ref.id, **application_data}
    except Exception as e:
        print(f"Error creating application: {str(e)}")
        raise

def get_user_applications(self, user_id):
    """Get all applications for a user"""
    try:
        applications = []
        docs = self.db.collection('applications')\
            .where('user_id', '==', user_id)\
            .order_by('created_at', direction=firestore.Query.DESCENDING)\
            .stream()
        
        for doc in docs:
            app_data = doc.to_dict()
            app_data['id'] = doc.id
            applications.append(app_data)
        
        return applications
    except Exception as e:
        print(f"Error fetching applications: {str(e)}")
        raise

def update_application_status(self, application_id, status, notes=None):
    """Update application status"""
    try:
        update_data = {
            'status': status,
            'updated_at': firestore.SERVER_TIMESTAMP
        }
        if notes:
            update_data['notes'] = notes
        
        self.db.collection('applications').document(application_id).update(update_data)
        return {'success': True}
    except Exception as e:
        print(f"Error updating application: {str(e)}")
        raise
```

**File:** `backend/app.py`
**Add NEW routes after existing routes (around line 200):**
```python
# Application Tracker Routes
@app.route('/api/applications', methods=['POST'])
def create_application():
    """Create new application tracking entry"""
    try:
        data = request.json
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        application_data = {
            'opportunity_title': data.get('opportunity_title'),
            'opportunity_link': data.get('opportunity_link'),
            'deadline': data.get('deadline'),
            'status': 'saved',  # saved, applied, under_review, accepted, rejected
            'priority': data.get('priority', 'medium'),  # low, medium, high
            'notes': data.get('notes', ''),
            'eligibility_score': data.get('eligibility_score')
        }
        
        result = firebase_service.create_application(user_id, application_data)
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/applications/<user_id>', methods=['GET'])
def get_applications(user_id):
    """Get all applications for a user"""
    try:
        applications = firebase_service.get_user_applications(user_id)
        return jsonify(applications), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/applications/<application_id>', methods=['PUT'])
def update_application(application_id):
    """Update application status"""
    try:
        data = request.json
        status = data.get('status')
        notes = data.get('notes')
        
        result = firebase_service.update_application_status(application_id, status, notes)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

**Frontend Component:**

**File:** `frontend/src/components/ApplicationTracker.jsx` (NEW FILE)
```jsx
import React, { useState, useEffect } from 'react';
import './ApplicationTracker.css';

function ApplicationTracker({ userId }) {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({
    total: 0,
    applied: 0,
    under_review: 0,
    accepted: 0
  });

  useEffect(() => {
    fetchApplications();
  }, [userId]);

  const fetchApplications = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/applications/${userId}`);
      const data = await response.json();
      setApplications(data);
      calculateStats(data);
    } catch (error) {
      console.error('Error fetching applications:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (apps) => {
    setStats({
      total: apps.length,
      applied: apps.filter(a => a.status === 'applied').length,
      under_review: apps.filter(a => a.status === 'under_review').length,
      accepted: apps.filter(a => a.status === 'accepted').length
    });
  };

  const updateStatus = async (appId, newStatus) => {
    try {
      await fetch(`${import.meta.env.VITE_API_URL}/api/applications/${appId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });
      fetchApplications();
    } catch (error) {
      console.error('Error updating application:', error);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      saved: '#gray',
      applied: '#3b82f6',
      under_review: '#f59e0b',
      accepted: '#10b981',
      rejected: '#ef4444'
    };
    return colors[status] || '#gray';
  };

  return (
    <div className="application-tracker">
      <h2>📊 Application Tracker</h2>
      
      {/* Stats Dashboard */}
      <div className="stats-grid">
        <div className="stat-card">
          <h3>{stats.total}</h3>
          <p>Total Tracked</p>
        </div>
        <div className="stat-card">
          <h3>{stats.applied}</h3>
          <p>Applied</p>
        </div>
        <div className="stat-card">
          <h3>{stats.under_review}</h3>
          <p>Under Review</p>
        </div>
        <div className="stat-card">
          <h3>{stats.accepted}</h3>
          <p>Accepted</p>
        </div>
      </div>

      {/* Applications List */}
      {loading ? (
        <p>Loading applications...</p>
      ) : (
        <div className="applications-list">
          {applications.map(app => (
            <div key={app.id} className="application-card">
              <div className="app-header">
                <h3>{app.opportunity_title}</h3>
                <span 
                  className="status-badge"
                  style={{ backgroundColor: getStatusColor(app.status) }}
                >
                  {app.status.replace('_', ' ').toUpperCase()}
                </span>
              </div>
              
              <p className="app-deadline">⏰ Deadline: {app.deadline}</p>
              
              {app.eligibility_score && (
                <p className="app-score">📈 Eligibility Score: {app.eligibility_score}%</p>
              )}
              
              <div className="app-actions">
                <select 
                  value={app.status} 
                  onChange={(e) => updateStatus(app.id, e.target.value)}
                >
                  <option value="saved">Saved</option>
                  <option value="applied">Applied</option>
                  <option value="under_review">Under Review</option>
                  <option value="accepted">Accepted</option>
                  <option value="rejected">Rejected</option>
                </select>
                
                <a href={app.opportunity_link} target="_blank" rel="noopener noreferrer">
                  View Opportunity →
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ApplicationTracker;
```

---

### 2.2 Live Eligibility Score System (3 hours)

**Backend Changes:**

**File:** `backend/services/profile_service.py`
**Add NEW method after existing methods:**
```python
def calculate_eligibility_score(self, profile_data, opportunity_data):
    """
    Calculate precise eligibility score (0-100) with detailed breakdown
    """
    score_breakdown = {
        'education_match': 0,      # 25 points
        'skills_match': 0,         # 25 points
        'experience_match': 0,     # 20 points
        'deadline_feasibility': 0, # 15 points
        'location_match': 0,       # 10 points
        'other_criteria': 0        # 5 points
    }
    
    # Education matching
    profile_education = profile_data.get('education', {}).get('degree', '').lower()
    opp_education = opportunity_data.get('education_requirement', '').lower()
    
    if 'any' in opp_education or not opp_education:
        score_breakdown['education_match'] = 25
    elif profile_education in opp_education:
        score_breakdown['education_match'] = 25
    elif 'bachelor' in profile_education and 'bachelor' in opp_education:
        score_breakdown['education_match'] = 20
    else:
        score_breakdown['education_match'] = 10
    
    # Skills matching
    profile_skills = set(skill.lower() for skill in profile_data.get('skills', []))
    required_skills = set(skill.lower() for skill in opportunity_data.get('required_skills', []))
    
    if required_skills:
        skills_match_percentage = len(profile_skills & required_skills) / len(required_skills)
        score_breakdown['skills_match'] = int(25 * skills_match_percentage)
    else:
        score_breakdown['skills_match'] = 20
    
    # Experience matching
    profile_experience = len(profile_data.get('experience', []))
    required_experience = opportunity_data.get('experience_years', 0)
    
    if profile_experience >= required_experience:
        score_breakdown['experience_match'] = 20
    elif profile_experience >= required_experience * 0.5:
        score_breakdown['experience_match'] = 15
    else:
        score_breakdown['experience_match'] = 5
    
    # Deadline feasibility
    deadline = opportunity_data.get('deadline')
    if deadline:
        try:
            from datetime import datetime, timedelta
            deadline_date = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
            days_until = (deadline_date - datetime.now()).days
            
            if days_until > 30:
                score_breakdown['deadline_feasibility'] = 15
            elif days_until > 14:
                score_breakdown['deadline_feasibility'] = 10
            elif days_until > 7:
                score_breakdown['deadline_feasibility'] = 5
            else:
                score_breakdown['deadline_feasibility'] = 0
        except:
            score_breakdown['deadline_feasibility'] = 10
    else:
        score_breakdown['deadline_feasibility'] = 10
    
    # Location matching
    profile_location = profile_data.get('location', '').lower()
    opp_location = opportunity_data.get('location', '').lower()
    
    if 'remote' in opp_location or 'online' in opp_location:
        score_breakdown['location_match'] = 10
    elif profile_location in opp_location:
        score_breakdown['location_match'] = 10
    else:
        score_breakdown['location_match'] = 5
    
    # Other criteria
    score_breakdown['other_criteria'] = 5
    
    total_score = sum(score_breakdown.values())
    
    return {
        'total_score': total_score,
        'breakdown': score_breakdown,
        'recommendation': self._get_recommendation(total_score),
        'missing_requirements': self._identify_gaps(profile_data, opportunity_data)
    }

def _get_recommendation(self, score):
    """Get recommendation based on score"""
    if score >= 80:
        return "Strong Match - Highly Recommended"
    elif score >= 60:
        return "Good Match - Recommended"
    elif score >= 40:
        return "Moderate Match - Consider After Improvements"
    else:
        return "Weak Match - Focus on Better-Fitting Opportunities"

def _identify_gaps(self, profile_data, opportunity_data):
    """Identify missing requirements"""
    gaps = []
    
    # Check skills gaps
    profile_skills = set(skill.lower() for skill in profile_data.get('skills', []))
    required_skills = set(skill.lower() for skill in opportunity_data.get('required_skills', []))
    missing_skills = required_skills - profile_skills
    
    if missing_skills:
        gaps.append({
            'category': 'Skills',
            'missing': list(missing_skills)
        })
    
    return gaps
```

**File:** `backend/app.py`
**Add NEW route:**
```python
@app.route('/api/eligibility/calculate', methods=['POST'])
def calculate_eligibility():
    """Calculate eligibility score for opportunity"""
    try:
        data = request.json
        user_id = data.get('user_id')
        opportunity_data = data.get('opportunity')
        
        # Get user profile
        profile = firebase_service.get_profile(user_id)
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        # Calculate score
        result = profile_service.calculate_eligibility_score(profile, opportunity_data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

**Frontend Component:**

**File:** `frontend/src/components/EligibilityScore.jsx` (NEW FILE)
```jsx
import React from 'react';
import './EligibilityScore.css';

function EligibilityScore({ score, breakdown, recommendation }) {
  const getScoreColor = (score) => {
    if (score >= 80) return '#10b981';
    if (score >= 60) return '#3b82f6';
    if (score >= 40) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div className="eligibility-score-widget">
      <div className="score-circle" style={{ borderColor: getScoreColor(score) }}>
        <h1>{score}</h1>
        <p>/ 100</p>
      </div>
      
      <div className="score-breakdown">
        <h3>Score Breakdown</h3>
        {Object.entries(breakdown).map(([key, value]) => (
          <div key={key} className="breakdown-item">
            <span>{key.replace('_', ' ').toUpperCase()}</span>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ 
                  width: `${(value / 25) * 100}%`,
                  backgroundColor: getScoreColor(value * 4)
                }}
              />
            </div>
            <span>{value} pts</span>
          </div>
        ))}
      </div>
      
      <div className="recommendation">
        <p>💡 {recommendation}</p>
      </div>
    </div>
  );
}

export default EligibilityScore;
```

---

### 2.3 AI Chatbot Integration (3 hours)

**Backend Changes:**

**File:** `backend/services/chatbot_service.py` (NEW FILE)
```python
import google.generativeai as genai
import os

class ChatbotService:
    def __init__(self):
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.conversation_history = {}
    
    def chat(self, user_id, message, context=None):
        """
        Handle chat message with context awareness
        """
        try:
            # Get or create conversation history
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            
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
            response = self.model.generate_content(full_prompt)
            response_text = response.text
            
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
            print(f"Chatbot error: {str(e)}")
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

You CANNOT:
- Auto-apply to opportunities
- Fill application forms
- Access external websites
- Make decisions for users

Be helpful, concise, and encourage user initiative."""
        
        if context:
            if 'profile' in context:
                base_prompt += f"\n\nUser Profile Summary:\n- Education: {context['profile'].get('education', 'N/A')}\n- Skills: {', '.join(context['profile'].get('skills', []))[:100]}"
            
            if 'opportunity' in context:
                base_prompt += f"\n\nCurrent Opportunity Context:\n- Title: {context['opportunity'].get('title', 'N/A')}\n- Type: {context['opportunity'].get('type', 'N/A')}"
        
        return base_prompt
    
    def clear_history(self, user_id):
        """Clear conversation history for user"""
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]
        return {'success': True}
```

**File:** `backend/app.py`
**Add NEW routes:**
```python
from services.chatbot_service import ChatbotService

# Initialize chatbot service
chatbot_service = ChatbotService()

# Chatbot Routes
@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chatbot messages"""
    try:
        data = request.json
        user_id = data.get('user_id')
        message = data.get('message')
        context = data.get('context')  # Optional: profile, current opportunity
        
        if not user_id or not message:
            return jsonify({'error': 'User ID and message required'}), 400
        
        result = chatbot_service.chat(user_id, message, context)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/clear/<user_id>', methods=['POST'])
def clear_chat_history(user_id):
    """Clear chat history for user"""
    try:
        result = chatbot_service.clear_history(user_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

**Frontend Component:**

**File:** `frontend/src/components/AIChatbot.jsx` (NEW FILE)
```jsx
import React, { useState, useRef, useEffect } from 'react';
import './AIChatbot.css';

function AIChatbot({ userId, context }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          message: input,
          context: context
        })
      });

      const data = await response.json();
      const aiMessage = { role: 'assistant', content: data.response };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error. Please try again.' 
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <>
      {/* Floating Chat Button */}
      <button 
        className="chat-toggle-btn"
        onClick={() => setIsOpen(!isOpen)}
      >
        💬
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="chat-window">
          <div className="chat-header">
            <h3>🤖 ORBIT Assistant</h3>
            <button onClick={() => setIsOpen(false)}>✕</button>
          </div>

          <div className="chat-messages">
            {messages.length === 0 && (
              <div className="chat-welcome">
                <p>👋 Hi! I'm your ORBIT assistant.</p>
                <p>Ask me about:</p>
                <ul>
                  <li>Eligibility requirements</li>
                  <li>Profile improvements</li>
                  <li>Application tips</li>
                  <li>Opportunity details</li>
                </ul>
              </div>
            )}

            {messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.role}`}>
                <div className="message-content">
                  {msg.content}
                </div>
              </div>
            ))}

            {loading && (
              <div className="message assistant">
                <div className="message-content typing">
                  <span></span><span></span><span></span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <div className="chat-input-area">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything..."
              rows="2"
            />
            <button onClick={sendMessage} disabled={loading || !input.trim()}>
              Send
            </button>
          </div>
        </div>
      )}
    </>
  );
}

export default AIChatbot;
```

---

### Priority 2: NICE TO HAVE (If Time Permits - Remaining 12 Hours)

### 2.4 Peer Success Stories (2 hours)
- Firebase collection for success stories
- Community feed showing recent acceptances
- Filter by opportunity type
- Inspiration and social proof

### 2.5 Resume Gap Analyzer (2 hours)
- Identify missing skills compared to top opportunities
- Suggest courses/certifications
- Timeline to fill gaps
- Competitive analysis

### 2.6 Smart Deadline Reminders (1 hour)
- Email/notification system for upcoming deadlines
- Customizable reminder timings
- Priority-based notifications

---

## 🛠️ IMPLEMENTATION STEPS

### Hour 0-4: Fix Critical Issues
1. **[1 person]** Fix Google Search relevance scoring in `opportunity_service.py`
2. **[1 person]** Improve resume evaluation prompts in `profile_service.py`
3. **[1 person]** Test and verify all API endpoints work correctly

### Hour 4-8: Application Tracker
1. **[Backend]** Add Firebase methods for application tracking
2. **[Backend]** Create API routes in `app.py`
3. **[Frontend]** Build `ApplicationTracker.jsx` component
4. **[Frontend]** Add stats dashboard with visual metrics

### Hour 8-12: Eligibility Score System
1. **[Backend]** Implement `calculate_eligibility_score` method
2. **[Backend]** Add API route for eligibility calculation
3. **[Frontend]** Build `EligibilityScore.jsx` with circular progress
4. **[Integration]** Connect to opportunity search results

### Hour 12-16: AI Chatbot
1. **[Backend]** Create `chatbot_service.py` with Gemini integration
2. **[Backend]** Add chat API routes
3. **[Frontend]** Build `AIChatbot.jsx` with floating button
4. **[Integration]** Add context passing from main components

### Hour 16-20: Polish & Integration
1. **[All]** Integrate all new features into main Dashboard
2. **[Frontend]** Add navigation between features
3. **[Testing]** Test complete user flow
4. **[UI/UX]** Improve styling and responsiveness

### Hour 20-24: Testing & Deployment
1. **[Testing]** End-to-end testing of all features
2. **[Bug Fixes]** Fix any critical issues
3. **[Deploy]** Push to production (Render + Vercel)
4. **[Demo]** Prepare 2-minute demo for judges

---

## 📊 SUCCESS METRICS

### What Makes Us Unique vs ChatGPT:

1. **Persistent Tracking** - ChatGPT can't track applications over time
2. **Quantified Scoring** - Our 0-100 eligibility score with breakdown
3. **Profile Integration** - Resume + opportunities + tracking in ONE system
4. **Contextual AI** - Chatbot knows YOUR profile and preferences
5. **Progress Dashboard** - Visual stats ChatGPT can't provide
6. **No Manual Copy-Paste** - Everything flows through our system

### Judge Demo Points:
- "We track 100% of your opportunities in ONE dashboard"
- "Our AI knows YOUR profile and gives personalized scores"
- "See EXACTLY why you're 73% eligible with breakdown"
- "Track application lifecycle: Saved → Applied → Accepted"
- "AI chatbot with context of YOUR profile and opportunities"

---

## 🚀 DEPLOYMENT CHECKLIST

Before final submission:
- [ ] All new Firebase collections indexed
- [ ] Environment variables set on Render
- [ ] Frontend .env.production configured
- [ ] All API endpoints tested in production
- [ ] Mobile responsive design verified
- [ ] Error handling for all new features
- [ ] Loading states for async operations
- [ ] Success/error messages for user actions

---

## 📝 TESTING CHECKLIST

- [ ] User can upload resume and create profile
- [ ] Search returns relevant opportunities with scores
- [ ] Application tracker saves and updates correctly
- [ ] Eligibility score calculates with breakdown
- [ ] Chatbot responds with context awareness
- [ ] All stats update in real-time
- [ ] Navigation between features works
- [ ] Mobile view is functional

---

## 💡 TIPS FOR TEAM SUCCESS

1. **Parallel Work:** Split into Backend + Frontend teams
2. **Communication:** Use this doc as single source of truth
3. **Git Strategy:** Feature branches, merge to main frequently
4. **Testing:** Test each feature immediately after implementation
5. **Priority:** Complete Priority 1 features before starting Priority 2
6. **Demo Prep:** Last 2 hours for testing and demo preparation

---

## 🎯 WINNING THE HACKATHON

**Key Differentiators:**
- Complete lifecycle tracking (not just search)
- Quantified decision-making (scores, not just suggestions)
- System intelligence (contextual AI, not prompt-based)
- Data persistence (dashboards, not conversations)
- Integrated experience (one platform, not multiple tools)

**Pitch Focus:**
"While ChatGPT helps you *ask* about opportunities, ORBIT helps you *manage* them. We're not a chatbot - we're an intelligent opportunity management system."

---

## 🔥 EMERGENCY CONTACTS

If stuck on any feature, prioritize this way:
1. Must work: Application Tracker + Eligibility Score
2. Should work: Google Search fixes + AI Chatbot
3. Nice to have: Success Stories + Gap Analyzer

**Time Running Out?**
- Cut Priority 2 features
- Focus on demo polish
- Ensure existing features are bug-free

---

**REMEMBER:** Judges want to see UNIQUENESS and COMPLETENESS, not perfection. A working system that does 3 things uniquely well beats a buggy system trying to do 10 things.

Good luck team! 🚀
