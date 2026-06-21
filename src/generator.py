"""LinkedIn Post Generator using Google Gemini AI + Auto-Publish."""
import os
import json
import random
import hashlib
import requests
from datetime import datetime, date
from pathlib import Path

try:
    import google.generativeai as genai
except ImportError:
    genai = None

CONTENT_DIR = Path(__file__).parent.parent / "content"
GENERATED_DIR = CONTENT_DIR / "generated"
PUBLISHED_DIR = CONTENT_DIR / "published"
HISTORY_FILE = CONTENT_DIR / "history.json"

LINKEDIN_TOKEN = os.environ.get("LINKEDIN_TOKEN")
LINKEDIN_VERSION = "202506"

CONTENT_CALENDAR = {
    0: {"topic": "Visual Merchandising", "style": "Tips & Best Practices"},
    1: {"topic": "HR & Recruitment", "style": "Thought Leadership"},
    2: {"topic": "Engagement", "style": "Poll / Question"},
    3: {"topic": "Store Operations", "style": "Case Study / Story"},
    4: {"topic": "Career & Leadership", "style": "Personal Insight"},
    5: {"topic": "Employee Engagement", "style": "Quick Tip"},
    6: {"topic": "Industry Trends", "style": "Weekly Roundup"},
}

HASHTAGS = {
    "Visual Merchandising": ["#VisualMerchandising", "#RetailDisplay", "#StoreDesign", "#VMTips", "#RetailExperience", "#WindowDisplay"],
    "HR & Recruitment": ["#HumanResources", "#Recruitment", "#TalentAcquisition", "#HRTech", "#Hiring", "#PeopleFirst"],
    "Engagement": ["#LinkedInPoll", "#CareerTalk", "#RetailCommunity", "#HRCommunity", "#LetsTalk"],
    "Store Operations": ["#RetailOperations", "#StoreManagement", "#RetailExcellence", "#CustomerExperience", "#RetailStrategy"],
    "Career & Leadership": ["#Leadership", "#CareerGrowth", "#ProfessionalDevelopment", "#CareerAdvice", "#GrowthMindset"],
    "Employee Engagement": ["#EmployeeEngagement", "#WorkplaceCulture", "#TeamBuilding", "#EmployeeExperience", "#PeopleMatter"],
    "Industry Trends": ["#FutureOfWork", "#RetailTrends", "#HRTrends", "#Innovation", "#DigitalTransformation"],
}

HOOKS = [
    "Here's something most people overlook →",
    "After 8+ years in retail, I've learned this →",
    "This changed how I think about {topic} →",
    "Unpopular opinion about {topic}:",
    "3 things I wish I knew earlier about {topic}:",
    "The biggest mistake I see in {topic}:",
    "Nobody talks about this in {topic}, but →",
    "A simple framework for {topic} that works:",
    "I've managed 5+ store launches. Here's my #1 lesson →",
    "If you're in {topic}, read this carefully →",
]


def load_history():
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text())
    return {"posts": [], "hashes": []}


def save_history(history):
    HISTORY_FILE.write_text(json.dumps(history, indent=2))


def get_today_config():
    day = date.today().weekday()
    return CONTENT_CALENDAR[day]


def build_prompt(topic, style):
    hook = random.choice(HOOKS).replace("{topic}", topic.lower())
    hashtags = " ".join(random.sample(HASHTAGS.get(topic, HASHTAGS["Career & Leadership"]), min(4, len(HASHTAGS.get(topic, [])))))

    return f"""You are a LinkedIn content creator for a professional named Preethi Prasanna who has 8+ years of experience in Visual Merchandising, Store Operations, and is transitioning into HR/People Management.

Generate ONE LinkedIn post with these requirements:
- Topic: {topic}
- Style: {style}
- Opening hook (use or adapt): "{hook}"
- Tone: Professional, authentic, human-like (NOT robotic or AI-sounding)
- Length: 150-250 words (optimal for LinkedIn engagement)
- Include a strong Call-to-Action at the end (ask a question to drive comments)
- Add 4-5 relevant hashtags at the end from these or similar: {hashtags}
- Use line breaks for readability (short paragraphs, 1-2 sentences each)
- Include emojis sparingly (2-3 max)
- Reference real retail/HR scenarios from Indian market
- Make it feel like a real person sharing their experience, NOT a generic AI post

DO NOT:
- Use phrases like "In today's fast-paced world" or "Let me share"
- Start with "I" as the very first word
- Use corporate jargon excessively
- Make it longer than 250 words

Output ONLY the LinkedIn post text. Nothing else."""


def generate_with_gemini(prompt):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")
    if not genai:
        raise ImportError("google-generativeai package not installed")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text.strip()


def generate_fallback(topic, style):
    """Fallback templates when API is unavailable."""
    templates = {
        "Visual Merchandising": [
            "Your store window has 3 seconds to stop a customer.\n\n3 seconds.\n\nThat's all the time you get before they walk past.\n\nAfter setting up 5+ stores this year, here's what I've learned about window displays that actually convert:\n\n→ Less is more. One hero product > 10 cluttered items\n→ Lighting creates mood. Warm light = luxury feel\n→ Change displays every 2 weeks minimum\n→ Eye-level placement drives 40% more attention\n\nThe best VM isn't about making things look pretty.\nIt's about making customers feel something.\n\nWhat's one display trick that works for your store? 👇\n\n#VisualMerchandising #RetailDisplay #StoreDesign #VMTips",
            "Most stores spend lakhs on inventory but ignore how it's presented.\n\nHere's the truth: A well-merchandised ₹500 product outsells a poorly displayed ₹5000 one.\n\nIn my 8 years of VM, the stores that win consistently do these 3 things:\n\n1️⃣ Zone their store by customer journey (not product category)\n2️⃣ Refresh displays weekly (not monthly)\n3️⃣ Train every store associate on basic VM principles\n\nVisual merchandising isn't a one-person job. It's a store culture.\n\nAgree or disagree? Let me know 👇\n\n#VisualMerchandising #RetailOperations #StoreManagement #CustomerExperience",
        ],
        "HR & Recruitment": [
            "The biggest hiring mistake in retail?\n\nHiring for skills, not attitude.\n\nI've onboarded dozens of store team members. The ones who lasted weren't always the most experienced.\n\nThey were the ones who:\n→ Showed curiosity about the brand\n→ Treated customers like people, not transactions\n→ Asked questions during induction (not just nodded)\n→ Took ownership from Day 1\n\nSkills can be trained in 2 weeks.\nAttitude takes years to change.\n\nHR teams: What's your #1 filter when hiring for retail? 👇\n\n#Recruitment #TalentAcquisition #HiringTips #RetailHR #PeopleFirst",
        ],
        "Engagement": [
            "Quick poll for my retail & HR network 👇\n\nWhat matters MORE for a new store launch?\n\n🅰️ Perfect visual displays\n🅱️ Well-trained store team\n🅲️ Strong brand marketing\n🅳️ Location & footfall\n\nI've seen stores with amazing VM but untrained staff fail.\nAnd stores with average displays but killer teams succeed.\n\nMy answer? 🅱️ — People always win.\n\nDrop your choice below! Let's debate 🔥\n\n#LinkedInPoll #RetailCommunity #StoreManagement #TeamBuilding",
        ],
        "Store Operations": [
            "Opening a new store in 30 days sounds exciting.\n\nUntil you're coordinating:\n→ Fixture installations\n→ Vendor deliveries\n→ Staff recruitment & training\n→ VM setup & brand compliance\n→ Marketing collateral\n→ Compliance & documentation\n\nAll. At. Once.\n\nAfter 5+ store launches, here's my #1 rule:\n\nStart with people, not products.\n\nHire and train your team FIRST. Everything else can be fixed on Day 2. A bad team on Day 1? That's a disaster.\n\nStore launch veterans — what's your survival tip? 👇\n\n#StoreOperations #RetailExcellence #NewStoreLaunch #RetailStrategy",
        ],
        "Career & Leadership": [
            "8 years ago, I started as a Visual Merchandiser.\n\nToday, I manage store operations, lead teams, handle onboarding, and drive training programs.\n\nNobody told me this would happen. But here's what I've realized:\n\nYour job title is just the starting point.\nThe skills you build along the way define your career.\n\nVM taught me:\n→ People management\n→ Stakeholder coordination\n→ Project execution\n→ Training & development\n\nEvery role has hidden skills. Are you noticing yours?\n\nWhat unexpected skill did YOUR job teach you? 👇\n\n#CareerGrowth #Leadership #ProfessionalDevelopment #GrowthMindset",
        ],
        "Employee Engagement": [
            "A simple 'good morning' to your store team costs nothing.\n\nBut it changes everything.\n\nI've seen teams transform when leaders just showed up — not to inspect, but to connect.\n\n3 things that boosted my team's morale instantly:\n\n☕ Morning check-ins (2 min, not 20)\n🎯 Recognizing small wins publicly\n📞 One personal conversation per week\n\nEmployee engagement doesn't need a ₹5L budget.\nIt needs presence and consistency.\n\nWhat's your go-to engagement hack? 👇\n\n#EmployeeEngagement #TeamBuilding #WorkplaceCulture #PeopleMatter",
        ],
        "Industry Trends": [
            "Retail in 2026 is unrecognizable from 2020.\n\n→ AI-powered planograms\n→ Digital-first VM strategies\n→ Experiential stores over transactional ones\n→ HR tech automating onboarding\n→ Employee experience = Customer experience\n\nThe retailers who'll win aren't just adapting.\nThey're building teams that can adapt continuously.\n\nThat's why HR in retail is more important than ever.\n\nWhat trend excites you most about retail's future? 👇\n\n#RetailTrends #FutureOfWork #HRTrends #Innovation #DigitalTransformation",
        ],
    }

    posts = templates.get(topic, templates["Career & Leadership"])
    return random.choice(posts)


def is_duplicate(content, history):
    content_hash = hashlib.md5(content.encode()).hexdigest()
    return content_hash in history.get("hashes", [])


def save_post(content, topic, style):
    today = date.today().isoformat()
    filename = f"{today}_{topic.lower().replace(' & ', '-').replace(' ', '-')}.md"
    filepath = GENERATED_DIR / filename

    metadata = f"""---
date: {today}
topic: {topic}
style: {style}
status: generated
---

{content}
"""
    filepath.write_text(metadata)
    return filepath


def get_person_id():
    """Get LinkedIn person ID from token."""
    r = requests.get("https://api.linkedin.com/v2/userinfo",
                     headers={"Authorization": f"Bearer {LINKEDIN_TOKEN}"},
                     timeout=30)
    if not r.ok:
        raise RuntimeError(f"Failed to get person ID: {r.status_code} {r.text}")
    return r.json()["sub"]


def publish_to_linkedin(content, poll_data=None):
    """Publish post to LinkedIn. Supports text posts and polls."""
    if not LINKEDIN_TOKEN:
        print("⚠️ LINKEDIN_TOKEN not set — skipping auto-publish")
        return False

    try:
        person_id = get_person_id()
        headers = {
            "Authorization": f"Bearer {LINKEDIN_TOKEN}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": LINKEDIN_VERSION,
        }
        body = {
            "author": f"urn:li:person:{person_id}",
            "commentary": content,
            "visibility": "PUBLIC",
            "distribution": {"feedDistribution": "MAIN_FEED", "targetEntities": [], "thirdPartyDistributionChannels": []},
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        }
        if poll_data:
            body["content"] = {
                "poll": {
                    "question": poll_data["question"][:140],
                    "options": [{"text": opt[:30]} for opt in poll_data["options"][:4]],
                    "settings": {"duration": "THREE_DAYS"},
                }
            }
        r = requests.post("https://api.linkedin.com/rest/posts",
                          headers=headers, json=body, timeout=30)
        if r.status_code == 401:
            print("❌ LinkedIn token expired! Regenerate using get_token.py")
            return False
        if not r.ok:
            print(f"❌ LinkedIn post failed: {r.status_code} {r.text}")
            return False
        print(f"✅ Successfully published {'poll' if poll_data else 'post'} to LinkedIn!")
        return True
    except Exception as e:
        print(f"❌ LinkedIn publishing error: {e}")
        return False


POLL_TEMPLATES = [
    {
        "commentary": "Every retailer debates this. Let's settle it 👇\n\nWhat drives MORE footfall to a store?\n\n#RetailStrategy #VisualMerchandising #StoreOperations #RetailPoll",
        "question": "What drives more footfall?",
        "options": ["Window displays", "Social media ads", "Word of mouth", "Location & visibility"],
    },
    {
        "commentary": "Honest answers only! 🙌\n\nAs an HR professional, what's YOUR biggest hiring challenge in retail?\n\n#HRCommunity #Recruitment #RetailHR #TalentAcquisition",
        "question": "Biggest hiring challenge in retail?",
        "options": ["High attrition rate", "Finding skilled staff", "Budget constraints", "Cultural fit"],
    },
    {
        "commentary": "This is the eternal retail debate 🔥\n\nWhat matters MORE for a new store launch?\n\n#StoreOperations #RetailExcellence #NewStoreLaunch #RetailPoll",
        "question": "Most critical for store launch success?",
        "options": ["Perfect VM displays", "Well-trained team", "Strong marketing", "Prime location"],
    },
    {
        "commentary": "Career growth in retail is unique. Where do YOU focus? 👇\n\n#CareerGrowth #RetailCareers #Leadership #ProfessionalDevelopment",
        "question": "Best skill for career growth in retail?",
        "options": ["People management", "Visual merchandising", "Data & analytics", "Customer experience"],
    },
    {
        "commentary": "Employee engagement doesn't need a massive budget 💡\n\nWhat keeps retail teams motivated the most?\n\n#EmployeeEngagement #TeamBuilding #WorkplaceCulture #RetailHR",
        "question": "What motivates retail teams most?",
        "options": ["Recognition & praise", "Growth opportunities", "Flexible schedules", "Team bonding events"],
    },
    {
        "commentary": "VM professionals — this one's for you! 🎨\n\nWhat's the #1 element that makes a window display stop traffic?\n\n#VisualMerchandising #RetailDisplay #WindowDisplay #VMTips",
        "question": "What makes a window display irresistible?",
        "options": ["Bold lighting", "Minimalist design", "Storytelling theme", "Color psychology"],
    },
    {
        "commentary": "The retail industry is evolving fast 🚀\n\nWhich trend will dominate retail in 2027?\n\n#RetailTrends #FutureOfWork #Innovation #RetailTech",
        "question": "Which trend will dominate retail next?",
        "options": ["AI-powered VM", "Experiential stores", "Sustainability focus", "Omnichannel fusion"],
    },
    {
        "commentary": "Onboarding can make or break a new hire's experience 🎯\n\nWhat's the most important part of the first week?\n\n#Onboarding #HRTips #EmployeeExperience #PeopleFirst",
        "question": "Most important in first-week onboarding?",
        "options": ["Buddy/mentor system", "Brand immersion", "Clear role clarity", "Team introductions"],
    },
]


def build_poll_prompt(topic):
    """Build Gemini prompt to generate a poll."""
    return f"""You are a LinkedIn content creator for Preethi Prasanna (8+ years in Visual Merchandising, Store Operations, transitioning to HR).

Generate a LinkedIn POLL about: {topic}

Requirements:
- Write a short commentary (2-3 lines, engaging, ends with a CTA to vote)
- Write a poll question (max 140 chars)
- Write exactly 4 poll options (max 30 chars each)
- Include 4 relevant hashtags in the commentary
- Tone: Professional, engaging, authentic

Output EXACTLY in this JSON format (no other text):
{{"commentary": "Your engaging intro text with hashtags", "question": "Your poll question?", "options": ["Option 1", "Option 2", "Option 3", "Option 4"]}}"""


def generate_poll(topic):
    """Generate poll content — try Gemini, fallback to templates."""
    try:
        prompt = build_poll_prompt(topic)
        raw = generate_with_gemini(prompt)
        # Parse JSON from response
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
        poll = json.loads(raw)
        if "question" in poll and "options" in poll and len(poll["options"]) >= 2:
            print("✅ Poll generated with Gemini AI")
            return poll
    except Exception as e:
        print(f"⚠️ Gemini poll generation failed ({e}), using template")

    return random.choice(POLL_TEMPLATES)


def main():
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    PUBLISHED_DIR.mkdir(parents=True, exist_ok=True)

    history = load_history()
    config = get_today_config()
    topic = config["topic"]
    style = config["style"]

    print(f"📅 Today's topic: {topic} | Style: {style}")

    # Check if today is a poll day (Wednesday = Engagement day, or randomly 2x/week)
    is_poll_day = (style == "Poll / Question") or (date.today().weekday() in [5] and random.random() < 0.5)

    if is_poll_day:
        print("📊 Generating a LinkedIn POLL today!")
        poll_data = generate_poll(topic)
        content = poll_data.get("commentary", "Share your thoughts! 👇")

        # Save post
        filepath = save_post(content + f"\n\n[POLL: {poll_data['question']}]\nOptions: {' | '.join(poll_data['options'])}", topic, "Poll")
        print(f"💾 Poll saved: {filepath.name}")

        # Publish poll
        published = publish_to_linkedin(content, poll_data)
    else:
        # Regular text post
        content = None
        try:
            prompt = build_prompt(topic, style)
            content = generate_with_gemini(prompt)
            print("✅ Generated with Gemini AI")
        except Exception as e:
            print(f"⚠️ Gemini unavailable ({e}), using templates")
            content = generate_fallback(topic, style)

        if is_duplicate(content, history):
            print("🔄 Duplicate detected, regenerating...")
            content = generate_fallback(topic, style)

        filepath = save_post(content, topic, style)
        print(f"💾 Post saved: {filepath.name}")
        published = publish_to_linkedin(content)

    # Update history
    content_hash = hashlib.md5(content.encode()).hexdigest()
    history["posts"].append({
        "date": date.today().isoformat(),
        "topic": topic,
        "style": style,
        "file": filepath.name,
        "hash": content_hash,
        "published": published,
        "type": "poll" if is_poll_day else "text",
    })
    history["hashes"].append(content_hash)
    save_history(history)

    print("\n" + "=" * 50)
    print(f"📝 TODAY'S LINKEDIN {'POLL' if is_poll_day else 'POST'}:")
    print("=" * 50)
    print(content)
    if is_poll_day:
        print(f"\n📊 Question: {poll_data['question']}")
        print(f"   Options: {' | '.join(poll_data['options'])}")
    print("=" * 50)

    return content


if __name__ == "__main__":
    main()
