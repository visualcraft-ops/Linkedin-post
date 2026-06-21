"""LinkedIn Post Generator using Google Gemini AI."""
import os
import json
import random
import hashlib
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


def main():
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    PUBLISHED_DIR.mkdir(parents=True, exist_ok=True)

    history = load_history()
    config = get_today_config()
    topic = config["topic"]
    style = config["style"]

    print(f"📅 Today's topic: {topic} | Style: {style}")

    # Try Gemini first, fallback to templates
    content = None
    try:
        prompt = build_prompt(topic, style)
        content = generate_with_gemini(prompt)
        print("✅ Generated with Gemini AI")
    except Exception as e:
        print(f"⚠️ Gemini unavailable ({e}), using templates")
        content = generate_fallback(topic, style)

    # Check duplicates
    if is_duplicate(content, history):
        print("🔄 Duplicate detected, regenerating...")
        content = generate_fallback(topic, style)

    # Save post
    filepath = save_post(content, topic, style)
    print(f"💾 Post saved: {filepath.name}")

    # Update history
    content_hash = hashlib.md5(content.encode()).hexdigest()
    history["posts"].append({
        "date": date.today().isoformat(),
        "topic": topic,
        "style": style,
        "file": filepath.name,
        "hash": content_hash,
    })
    history["hashes"].append(content_hash)
    save_history(history)

    # Print the post
    print("\n" + "=" * 50)
    print("📝 TODAY'S LINKEDIN POST:")
    print("=" * 50)
    print(content)
    print("=" * 50)

    return content


if __name__ == "__main__":
    main()
