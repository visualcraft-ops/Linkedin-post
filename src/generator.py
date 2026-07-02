"""LinkedIn Post Generator — Auto-generates and publishes viral-worthy content."""
import os
import json
import random
import hashlib
import time
import requests
from datetime import datetime, date
from pathlib import Path

try:
    from google import genai
except ImportError:
    genai = None

CONTENT_DIR = Path(__file__).parent.parent / "content"
GENERATED_DIR = CONTENT_DIR / "generated"
PUBLISHED_DIR = CONTENT_DIR / "published"
HISTORY_FILE = CONTENT_DIR / "history.json"

LINKEDIN_TOKEN = os.environ.get("LINKEDIN_TOKEN")
LINKEDIN_VERSION = "202606"
POST_SESSION = os.environ.get("POST_SESSION", "morning")

MORNING_CALENDAR = {
    0: {"topic": "Visual Merchandising", "style": "actionable_tips"},
    1: {"topic": "Vendor Management & Sourcing", "style": "thought_leadership"},
    2: {"topic": "Store Design & Retail Tech", "style": "case_study"},
    3: {"topic": "Retail Branding & Display Strategy", "style": "personal_story"},
    4: {"topic": "Vendor Negotiation & Cost Optimization", "style": "framework"},
    5: {"topic": "Sustainable VM & Retail Innovation", "style": "contrarian_take"},
    6: {"topic": "India Retail Trends & Future of Stores", "style": "future_prediction"},
}

EVENING_CALENDAR = {
    0: {"topic": "Quick VM Tip", "style": "micro_content"},
    1: {"topic": "Vendor Red Flags & Wins", "style": "debate_starter"},
    2: {"topic": "Retail Display Life", "style": "relatable_story"},
    3: {"topic": "AI in Visual Merchandising", "style": "poll"},
    4: {"topic": "Store Launch Stories", "style": "gratitude_post"},
    5: {"topic": "Weekend VM Inspiration", "style": "listicle"},
    6: {"topic": "Quick Commerce vs Physical Retail", "style": "poll"},
}

HOOKS = {
    "actionable_tips": [
        "Stop doing this with your store displays.\n\nI see it everywhere →",
        "3 VM changes that increased our footfall by 40%.\n\nNone of them cost money →",
        "Your mannequins are lying to customers.\n\nHere's what I mean →",
        "I set up 5 stores this year. Same display mistake in all of them at first →",
        "The window display formula that works every single time →",
        "Most VM teams waste 60% of their fixture budget.\n\nHere's the fix →",
        "One lighting change. 28% more dwell time.\n\nThe technique →",
        "94% of first impressions are visual.\n\nYet most stores ignore this →",
        "Tier-2 cities are booming. But their VM execution is stuck in 2018.\n\nHere's what needs to change →",
        "Reliance just crossed 20,000 stores.\n\nHere's what their VM gets right that others don't →",
    ],
    "thought_leadership": [
        "Vendor management in retail is broken.\n\nHere's what nobody wants to admit →",
        "We negotiate price. We should negotiate partnership.\n\nLet me explain →",
        "The real reason your vendor deliveries are always late?\n\nIt's not logistics →",
        "I've managed 50+ vendors across 5 store launches. The ones who deliver all have ONE thing in common →",
        "Unpopular opinion: Your cheapest vendor is your most expensive one.\n\nHere's why →",
        "90% of vendor conflicts happen because of THIS one missing step →",
        "India added 2,182 new retail stores in FY26.\n\nThe vendor ecosystem isn't keeping up. Here's why →",
        "Quick commerce is killing vendor timelines.\n\nRetail sourcing needs a complete rethink →",
        "The vendor who charges 15% more just saved my store launch.\n\nLet me explain →",
        "Near-shoring is changing everything in retail sourcing.\n\nAre you ready? →",
    ],
    "case_study": [
        "Day 1 of a new store launch.\n\nEverything that can go wrong, did →",
        "We had 48 hours to redesign an entire store for a tier-2 city. Here's what happened →",
        "A ₹200 change in our display increased sales by 25%.\n\nThe story →",
        "The store was losing footfall to quick commerce. One VM change fixed it →",
        "Our vendor missed the deadline by 3 days.\n\nHow I still launched on time →",
        "2 stores. Same brand. Different VM execution.\n\nThe results shocked us →",
        "We opened in a city where the brand had zero recall.\n\nVM was our only weapon →",
        "The planogram said one thing. The local customer wanted another.\n\nWhat I did →",
    ],
    "personal_story": [
        "8 years ago, I was arranging mannequins.\n\nToday I design retail experiences.\n\nHere's the messy middle →",
        "My worst vendor negotiation taught me my best lesson →",
        "Nobody in my family understood what 'Visual Merchandising' meant.\n\nNow they do →",
        "The display that got rejected 3 times became our highest-performing setup →",
        "From fixture planning to full store launches — my 8-year evolution →",
        "I walked into a Zara in 2016 and my entire career changed direction.\n\nHere's what I noticed →",
        "The moment I realized VM isn't decoration — it's revenue strategy →",
        "A customer once told me our display 'felt like home'.\n\nThat's when I understood experiential retail →",
    ],
    "framework": [
        "My 3-step framework for vendor evaluation:\n\n(Steal this) →",
        "The Q-C-D framework I use for every vendor onboarding:\n\nQuality. Cost. Delivery →",
        "How I plan a store launch VM in 30 days (step-by-step) →",
        "The 5-point vendor scorecard that eliminated 80% of our delays →",
        "Want flawless VM execution? Use this vendor briefing template →",
        "My planogram-to-execution checklist that never fails →",
        "The 'Walk-Stop-Buy' framework that transforms any store layout →",
        "How I evaluate a new vendor in under 1 hour (the 7-point audit) →",
    ],
    "contrarian_take": [
        "Hot take: The prettiest store display is often the worst performer.\n\nFight me on this →",
        "Controversial: VM is not about aesthetics.\n\nIt's about conversion →",
        "Everyone's chasing digital. Physical retail will outlast it all.\n\nHere's my case →",
        "Stop blaming vendors for delays.\n\nThe problem is YOUR brief →",
        "The 'lowest quote wins' approach is destroying retail quality.\n\nHere's a better way →",
        "Sustainability in VM is mostly greenwashing right now.\n\nLet's be honest →",
        "AI won't replace Visual Merchandisers.\n\nBut it will replace the ones who don't adapt →",
        "Quick commerce is NOT killing physical stores.\n\nIt's making them MORE important →",
        "Reliance, DMart, Trent — they're all expanding stores while everyone screams 'digital first'.\n\nThink about that →",
    ],
    "future_prediction": [
        "Retail VM in 2030 will look NOTHING like today.\n\n5 predictions →",
        "AI-powered planograms are already here.\n\nHere's what changes for VM teams →",
        "The future of vendor management is real-time, data-driven, and automated.\n\nHere's what that means →",
        "Physical stores aren't dying. They're becoming experience centers →",
        "Sustainable VM materials will be mandatory by 2028.\n\nAre your vendors ready? →",
        "India will add 10,000+ organized retail stores by 2028.\n\nThe VM talent gap is going to be massive →",
        "Agentic AI is coming for retail merchandising.\n\nMcKinsey and BCG agree. Here's what it means for VM →",
        "The store of 2030: AR wayfinding, adaptive displays, zero-waste fixtures.\n\nWho's building it? →",
    ],
    "micro_content": [
        "Quick VM tip that takes 2 minutes ⚡\n\n→",
        "One thing I do every Monday that transforms the store week →",
        "The smallest display change with the biggest ROI →",
        "60-second store walk trick I use every single day →",
        "Before you call your vendor — check this first →",
        "The 3-second rule in VM that most people forget →",
        "One question I ask every vendor that reveals everything →",
    ],
    "debate_starter": [
        "Agree or disagree?\n\n→",
        "I said this in a vendor meeting and the room went silent →",
        "This might be my most controversial vendor management opinion →",
        "Tell me I'm wrong about this VM approach →",
        "Every VM manager debates this. Where do you stand? →",
        "Is quick commerce making physical store VM MORE or LESS important? →",
        "Should retail brands invest in AI planograms or better vendor partnerships? →",
    ],
    "relatable_story": [
        "Retail VM life. Nobody tells you about these moments →",
        "When the fixture delivery arrives 30 mins before store opening 😅\n\nVM people, you know →",
        "That moment when the brand team changes the planogram AFTER you've set up the display →",
        "VM managers on launch day vs 3 days before launch.\n\nA thread →",
        "When the vendor says 'slight delay' and you know exactly what that means →",
        "When quick commerce delivers in 10 mins but your store fixture takes 10 weeks 😅 →",
        "The look on your face when the regional head walks in during a display change →",
    ],
    "gratitude_post": [
        "Shoutout to every vendor partner who delivers on impossible timelines →",
        "The unsung heroes of retail are the people who build what we design →",
        "Something I don't say enough to my vendor partners →",
        "Behind every successful store launch is a vendor who went above and beyond →",
        "To every carpenter, fabricator, and printer who brings VM to life — thank you →",
    ],
    "listicle": [
        "7 things I learned this week about retail displays →",
        "5 vendor management lessons from 8 years in retail →",
        "4 habits of the best VM professionals I've worked with →",
        "6 signs your vendor relationship is about to go wrong →",
        "5 sustainable VM materials every retailer should know about in 2026 →",
        "4 AI tools that are changing Visual Merchandising right now →",
    ],
    "poll": [],
}


POLL_TEMPLATES = [
    {"commentary": "Reliance just crossed 20,000 stores. India added 2,182 stores in FY26.\n\nBut what REALLY makes a new store succeed? 👇\n\n#RetailIndia #StoreLaunch #VisualMerchandising #RetailGrowth", "question": "Most critical for new store success in India?", "options": ["VM & display execution", "Vendor delivery speed", "Local market research", "Team training"]},
    {"commentary": "Quick commerce delivers in 10 mins. Physical stores take 10 weeks to set up.\n\nSo why are retailers STILL expanding stores? 🤔\n\n#QuickCommerce #PhysicalRetail #RetailStrategy #FutureOfRetail", "question": "Quick commerce vs physical stores — who wins long-term?", "options": ["Physical stores", "Quick commerce", "Hybrid model wins", "Depends on category"]},
    {"commentary": "AI planograms. AR wayfinding. Agentic merchandising.\n\nBCG and McKinsey are all-in on AI retail. But are VM teams ready? 🚀\n\n#AIinRetail #VisualMerchandising #RetailTech #FutureOfVM", "question": "Will AI replace traditional VM planning?", "options": ["Yes, within 3 years", "Partially — humans + AI", "No, creativity wins", "Too early to say"]},
    {"commentary": "India's biggest vendor management challenge in 2026 — honest answers only! 🙌\n\n#VendorManagement #RetailSourcing #SupplyChain #IndiaRetail", "question": "Biggest vendor challenge in India retail?", "options": ["On-time delivery", "Quality consistency", "Cost inflation", "Communication gaps"]},
    {"commentary": "Sustainability is no longer optional. But who pays for sustainable VM fixtures? 💡\n\n#SustainableRetail #GreenVM #RetailInnovation #ESG", "question": "Who should bear cost of sustainable VM?", "options": ["Brand/retailer", "Shared with vendor", "Customer (premium)", "Government subsidies"]},
    {"commentary": "VM people — the eternal debate! 🎨\n\nDoes storytelling or minimalism sell more in Indian retail?\n\n#VisualMerchandising #RetailDisplay #WindowDisplay #VMStrategy", "question": "What stops Indian customers at a window?", "options": ["Bold storytelling", "Minimalist design", "Festival/cultural themes", "Price-led messaging"]},
    {"commentary": "Tier-2 and tier-3 cities are driving India's retail boom.\n\nBut VM execution there needs a different playbook 🎯\n\n#Tier2Retail #IndiaRetail #VisualMerchandising #RetailExpansion", "question": "Biggest VM challenge in tier-2 cities?", "options": ["Finding local vendors", "Different aesthetics", "Budget constraints", "Logistics delays"]},
    {"commentary": "Vendor relationships make or break execution.\n\nAfter 50+ vendor partnerships, here's what I've learned matters most 🎯\n\n#VendorManagement #RetailPartners #SupplyChain #Procurement", "question": "What makes a great retail vendor?", "options": ["Reliable delivery", "Quality materials", "Proactive solutions", "Transparent pricing"]},
    {"commentary": "The future of store design is being shaped right now 🚀\n\nNeo-Chromatic Minimalism, Sculptural Storytelling, Crafted Materiality...\n\n#StoreDesign #RetailTrends #VMInnovation #RetailDesign", "question": "Which VM trend will dominate 2027?", "options": ["Experiential zones", "AI-adaptive displays", "Sustainable materials", "Hyper-local themes"]},
    {"commentary": "India's apparel retail is growing 10.5% in FY26.\n\nBut are VM professionals growing with it? Let's check 📊\n\n#RetailCareers #VisualMerchandising #VMCareer #IndiaRetail", "question": "Best career move for VM professionals?", "options": ["Learn AI/data tools", "Vendor management", "Multi-brand experience", "Retail tech skills"]},
    {"commentary": "Settling this once and for all 🔥\n\nExperience vs aesthetics in physical retail.\n\n#RetailExperience #VisualMerchandising #CustomerExperience #StoreDesign", "question": "What brings customers BACK to a store?", "options": ["Stunning displays", "Personalized experience", "Staff interactions", "Exclusive products"]},
    {"commentary": "The omnichannel reality:\n\nStores → Ecommerce → Quick commerce\n\nAll need coordinated VM. But who owns it? 🤷\n\n#Omnichannel #RetailStrategy #VisualMerchandising #RetailOps", "question": "Who should own omnichannel VM strategy?", "options": ["Central VM team", "Store managers", "Marketing team", "Dedicated digital+VM role"]},
]

HASHTAGS = {
    "Visual Merchandising": ["#VisualMerchandising", "#RetailDisplay", "#StoreDesign", "#VMTips", "#WindowDisplay", "#RetailExperience", "#VMStrategy", "#InStoreExperience"],
    "Vendor Management & Sourcing": ["#VendorManagement", "#RetailSourcing", "#SupplyChain", "#Procurement", "#VendorRelations", "#StrategicSourcing", "#RetailPartners", "#SupplyChainManagement"],
    "Store Design & Retail Tech": ["#StoreDesign", "#RetailTech", "#AIinRetail", "#SmartRetail", "#RetailInnovation", "#RetailExperience", "#OmnichannelRetail", "#DigitalRetail"],
    "Retail Branding & Display Strategy": ["#RetailBranding", "#DisplayStrategy", "#BrandExperience", "#InStoreMarketing", "#RetailMarketing", "#CustomerExperience", "#ExperientialRetail"],
    "Vendor Negotiation & Cost Optimization": ["#VendorNegotiation", "#CostOptimization", "#RetailSourcing", "#Procurement", "#RetailBusiness", "#SupplyChainIndia", "#RetailOperations"],
    "Sustainable VM & Retail Innovation": ["#SustainableRetail", "#GreenRetail", "#VMInnovation", "#EcoFriendlyDesign", "#RetailESG", "#CircularRetail", "#SustainableDesign", "#FutureOfRetail"],
    "India Retail Trends & Future of Stores": ["#IndiaRetail", "#RetailTrends", "#FutureOfRetail", "#RetailGrowth", "#RetailTransformation", "#Tier2Retail", "#RetailExpansion", "#RetailIndia"],
    "Quick VM Tip": ["#VMTips", "#VisualMerchandising", "#RetailHacks", "#StoreDisplay", "#QuickTip", "#RetailLife"],
    "Vendor Red Flags & Wins": ["#VendorManagement", "#RetailOps", "#SupplyChain", "#VendorStrategy", "#RetailInsight", "#RetailWins"],
    "Retail Display Life": ["#RetailLife", "#VMLife", "#StoreDisplay", "#RetailHumor", "#VisualMerchandising", "#RetailCommunity"],
    "AI in Visual Merchandising": ["#AIinRetail", "#VisualMerchandising", "#RetailTech", "#AgenticAI", "#SmartRetail", "#FutureOfVM", "#RetailInnovation"],
    "Store Launch Stories": ["#StoreLaunch", "#RetailExpansion", "#NewStore", "#RetailGrowth", "#VMExecution", "#IndiaRetail"],
    "Weekend VM Inspiration": ["#VMInspiration", "#RetailDesign", "#WeekendCreativity", "#DisplayIdeas", "#VisualMerchandising", "#StoreDesign"],
    "Quick Commerce vs Physical Retail": ["#QuickCommerce", "#PhysicalRetail", "#RetailDebate", "#FutureOfRetail", "#IndiaRetail", "#RetailStrategy", "#Omnichannel"],
}

CREATOR_TAGS = {
    "Visual Merchandising": ["Retail design enthusiasts", "VM community", "Store designers and merchandisers", "Display design professionals"],
    "Vendor Management & Sourcing": ["Vendor management professionals", "Retail procurement leaders", "Supply chain community", "Sourcing experts"],
    "Store Design & Retail Tech": ["Retail tech innovators", "Store design community", "Smart retail enthusiasts", "Retail innovation leaders"],
    "Retail Branding & Display Strategy": ["Brand experience designers", "Retail marketing leaders", "Display strategy community", "In-store experience professionals"],
    "Vendor Negotiation & Cost Optimization": ["Procurement professionals", "Retail sourcing leaders", "Cost optimization experts", "Retail operations community"],
    "Sustainable VM & Retail Innovation": ["Sustainable retail advocates", "Green design community", "Retail ESG professionals", "Eco-conscious retailers"],
    "India Retail Trends & Future of Stores": ["India retail community", "Retail growth leaders", "Future-of-retail thinkers", "Retail expansion professionals"],
}

BOOST_COMMENTS = [
    "Curious to hear from VM professionals with 5+ years experience — has vendor coordination changed for you?",
    "Also worth noting: this applies differently in metro vs tier-2 city retail. Would love to hear regional perspectives.",
    "For anyone starting in Visual Merchandising — bookmark this. I wish someone told me this on day 1.",
    "The responses here are gold 🙌 Keep them coming — learning from all of you.",
    "Follow-up thought: the best part about sharing here is realizing how many of us face the same vendor challenges daily.",
    "VM and retail friends — tag someone who needs to see this today 👇",
    "This sparked a great conversation in my DMs too. If you want to discuss VM strategies further, feel free to connect!",
    "Adding context: this is based on my experience in premium retail (Reliance, lifestyle brands). May differ for value retail.",
    "Quick clarification from the comments — yes, this works for both large format and standalone stores.",
    "Loving the different perspectives here! The VM and retail community on LinkedIn is genuinely one of the best 🙌",
]



# ============================================================
# CORE FUNCTIONS
# ============================================================

def load_history():
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text())
    return {"posts": [], "hashes": []}


def save_history(history):
    HISTORY_FILE.write_text(json.dumps(history, indent=2))


def get_today_config():
    day = date.today().weekday()
    if POST_SESSION == "evening":
        return EVENING_CALENDAR[day]
    return MORNING_CALENDAR[day]


def build_prompt(topic, style):
    hooks = HOOKS.get(style, HOOKS["actionable_tips"])
    hook = random.choice(hooks) if hooks else ""
    tags = " ".join(random.sample(HASHTAGS.get(topic, HASHTAGS["Visual Merchandising"]), min(4, len(HASHTAGS.get(topic, [])))))

    session_ctx = ""
    if POST_SESSION == "evening":
        session_ctx = "- EVENING post: lighter, conversational, under 150 words, slightly humorous"
    else:
        session_ctx = "- MORNING post: professional, value-driven, 150-250 words"

    return f"""Write a LinkedIn post AS Preethi Prasanna — 8+ years in Visual Merchandising, Vendor Management & Store Operations. Expert in store launches, VM execution, vendor coordination, fixture sourcing, and retail branding for premium brands in India (Reliance Retail, Landmark Group, Future Group).

Topic: {topic} | Style: {style}
Opening hook (adapt): "{hook}"
{session_ctx}

TRENDING CONTEXT (weave in naturally if relevant):
- India retail added 2,182 stores in FY26; Reliance crossed 20,000 stores
- Quick commerce (Blinkit, Zepto, JioMart) growing 29% but physical stores still expanding
- AI/Agentic AI transforming merchandising decisions (McKinsey, BCG reports)
- Sustainable VM materials & ESG compliance becoming mandatory
- Tier-2/3 cities driving 40% of new retail consumption
- AR wayfinding, Neo-Chromatic Minimalism, Sculptural Storytelling are 2026 VM trends
- Near-shoring & local vendor networks gaining importance
- Experiential retail: stores becoming experience centers, not just sales points

RULES:
- First 2 lines MUST create curiosity (shows before "see more")
- Line breaks every 1-2 sentences. Short punchy paragraphs.
- ONE specific number/example from Indian retail
- End with a question people WANT to answer
- 4 hashtags at end: {tags}
- 2-3 emojis max
- Write like a real person, NOT a corporate comms team
- Content should attract recruiters looking for VM/Vendor Management professionals
- Reference real trends, data points, or industry shifts to build credibility

NEVER: Start with "I", use "In today's fast-paced world", sound like ChatGPT, exceed 250 words, mention HR/recruitment/hiring topics.

Output ONLY the post text."""


def generate_with_gemini(prompt):
    """Generate content using the new google-genai SDK."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")
    if not genai:
        raise ImportError("google-genai package not installed")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    text = response.text.strip()
    if not text or len(text) < 50:
        raise ValueError(f"Gemini returned too-short response: '{text[:100]}'")
    return text


def generate_fallback(topic, style):
    """Fallback templates when API unavailable."""
    templates = [
        f"Stop scrolling.\n\nIf you're in retail VM, this will save you hours.\n\nAfter 5+ store launches, here's my cheat sheet for {topic.lower()}:\n\n→ Start with your customer's eye level\n→ Change displays every 14 days (not when you feel like it)\n→ Brief your vendors with visual references, not just text\n→ Measure footfall before/after every display change\n\nThe stores that win aren't doing anything revolutionary.\nThey're doing the basics consistently.\n\nWhich one do you struggle with most? 👇\n\n#VisualMerchandising #VendorManagement #StoreOperations #RetailTips",
        f"The biggest myth in retail?\n\n'Good VM sells itself.'\n\nNo. Good VM + reliable vendors + right execution = sales.\n\nI've seen stores with stunning designs but terrible vendor delivery.\nI've seen stores with basic VM but rock-solid vendor partnerships crushing targets.\n\nThe difference isn't the design.\nIt's the vendor relationship behind it.\n\n{topic} is a partnership game. Build accordingly.\n\nAgree? Disagree? Tell me 👇\n\n#RetailExcellence #VendorManagement #VisualMerchandising #VMExecution",
        f"Real talk about {topic.lower()}.\n\nNobody posts about the vendor failures. So let me go first.\n\nI once spent 2 weeks planning the perfect store display.\nThe fixture vendor delivered wrong specs 2 days before launch.\n\nThe fix? A backup vendor list and a 24-hour turnaround plan.\nWe launched on time. Customers never knew.\n\nResult: Lesson learned — always have Plan B vendors.\n\nWhat's a vendor challenge that taught you something? 👇\n\n#VendorManagement #VisualMerchandising #StoreLaunch #RetailTips",
        f"Here's a {topic.lower()} reminder that costs ₹0:\n\n1. Visit your vendor's workshop once a quarter (trust builds in person)\n2. Share visual briefs, not just specs (vendors aren't mind-readers)\n3. Pay on time — it's the best negotiation tool you'll ever have\n4. Document what works (future you will thank present you)\n\nSimple? Yes.\nDoes everyone do it? No.\n\nThat's the edge in vendor management.\n\nWhich one are you implementing this week? 👇\n\n#VendorManagement #RetailOperations #VMTips #RetailExcellence",
        f"Quiet confession from 8 years in retail VM:\n\nThe best store I ever launched wasn't the one with the biggest budget.\n\nIt was the one where:\n→ Vendors were briefed 45 days in advance\n→ Fixtures arrived 5 days before launch (not 5 hours)\n→ We did a mock setup before the real one\n→ Every display had a clear commercial objective\n\nRetail VM success isn't about aesthetics alone. It's about execution.\n\nYour displays are only as good as your vendor partnerships.\n\nBuild the vendor relationships first. The stunning stores follow.\n\nWhat made YOUR best store launch successful? 👇\n\n#VisualMerchandising #VendorManagement #StoreLaunch #RetailStrategy",
    ]
    return random.choice(templates)


def is_duplicate(content, history):
    return hashlib.md5(content.encode()).hexdigest() in history.get("hashes", [])



# ============================================================
# LINKEDIN TOKEN REFRESH
# ============================================================

def refresh_linkedin_token():
    """Refresh LinkedIn token and update GitHub secret. Returns new token or None."""
    refresh_token = os.environ.get("LINKEDIN_REFRESH_TOKEN")
    client_id = os.environ.get("LINKEDIN_CLIENT_ID")
    client_secret = os.environ.get("LINKEDIN_CLIENT_SECRET")
    gh_pat = os.environ.get("GH_PAT")
    if not all([refresh_token, client_id, client_secret]):
        print("⚠️ Missing refresh token env vars")
        return None
    try:
        r = requests.post("https://www.linkedin.com/oauth/v2/accessToken", data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        }, timeout=30)
        if not r.ok:
            print(f"❌ Token refresh failed: {r.status_code} {r.text}")
            return None
        new_token = r.json().get("access_token")
        if not new_token:
            return None
        print("✅ LinkedIn token refreshed successfully")
        # Update GitHub secret
        if gh_pat:
            try:
                from nacl import encoding, public
                repo = "visualcraft-ops/Linkedin-post"
                gh_headers = {"Authorization": f"Bearer {gh_pat}", "Accept": "application/vnd.github+json"}
                key_resp = requests.get(f"https://api.github.com/repos/{repo}/actions/secrets/public-key", headers=gh_headers, timeout=30)
                if key_resp.ok:
                    key_data = key_resp.json()
                    public_key = public.PublicKey(key_data["key"].encode("utf-8"), encoding.Base64Encoder())
                    sealed_box = public.SealedBox(public_key)
                    encrypted = sealed_box.encrypt(new_token.encode("utf-8"))
                    encrypted_value = encoding.Base64Encoder.encode(encrypted).decode("utf-8")
                    requests.put(f"https://api.github.com/repos/{repo}/actions/secrets/LINKEDIN_TOKEN",
                                 headers=gh_headers, json={"encrypted_value": encrypted_value, "key_id": key_data["key_id"]}, timeout=30)
                    print("✅ GitHub secret LINKEDIN_TOKEN updated")
            except Exception as e:
                print(f"⚠️ Failed to update GitHub secret: {e}")
        return new_token
    except Exception as e:
        print(f"❌ Token refresh error: {e}")
        return None


# ============================================================
# LINKEDIN API FUNCTIONS
# ============================================================

def get_person_id():
    r = requests.get("https://api.linkedin.com/v2/userinfo",
                     headers={"Authorization": f"Bearer {LINKEDIN_TOKEN}"}, timeout=30)
    if not r.ok:
        raise RuntimeError(f"Failed to get person ID: {r.status_code} {r.text}")
    return r.json()["sub"]


def publish_to_linkedin(content, poll_data=None):
    """Publish post or poll. Returns post URN on success."""
    if not LINKEDIN_TOKEN:
        print("⚠️ LINKEDIN_TOKEN not set — skipping publish")
        return None
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
        r = requests.post("https://api.linkedin.com/rest/posts", headers=headers, json=body, timeout=30)
        if r.status_code == 401:
            print("❌ Token expired! Attempting auto-refresh...")
            new_token = refresh_linkedin_token()
            if new_token:
                headers["Authorization"] = f"Bearer {new_token}"
                r = requests.post("https://api.linkedin.com/rest/posts", headers=headers, json=body, timeout=30)
                if r.ok:
                    post_urn = r.headers.get("x-restli-id", "")
                    print(f"✅ Published {'poll' if poll_data else 'post'} after refresh! URN: {post_urn}")
                    return post_urn
                print(f"❌ Post failed after refresh: {r.status_code} {r.text}")
            return None
        if not r.ok:
            print(f"❌ Post failed: {r.status_code} {r.text}")
            return None
        post_urn = r.headers.get("x-restli-id", "")
        print(f"✅ Published {'poll' if poll_data else 'post'}! URN: {post_urn}")
        return post_urn
    except Exception as e:
        print(f"❌ Publishing error: {e}")
        return None


def post_self_comment(post_urn):
    """Post a follow-up comment on own post to boost engagement."""
    if not LINKEDIN_TOKEN or not post_urn:
        return False
    try:
        time.sleep(30)  # Wait 30s to look natural
        person_id = get_person_id()
        headers = {
            "Authorization": f"Bearer {LINKEDIN_TOKEN}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": LINKEDIN_VERSION,
        }
        comment_text = random.choice(BOOST_COMMENTS)
        # Convert ugcPost URN to activity URN for comments API
        # x-restli-id returns "urn:li:ugcPost:123" but comments need activity URN
        # Use the ugcPost URN directly in the URL path
        url = f"https://api.linkedin.com/rest/socialActions/{post_urn}/comments"
        body = {
            "actor": f"urn:li:person:{person_id}",
            "object": post_urn,
            "message": {"text": comment_text},
        }
        r = requests.post(url, headers=headers, json=body, timeout=30)
        if r.status_code in (200, 201):
            print(f"💬 Self-comment posted: '{comment_text[:50]}...'")
            return True
        print(f"⚠️ Comment failed: {r.status_code} {r.text}")
        return False
    except Exception as e:
        print(f"⚠️ Comment error: {e}")
        return False


def add_engagement_tag(content, topic):
    """Add a subtle community callout to boost reach."""
    tags = CREATOR_TAGS.get(topic, CREATOR_TAGS.get("Visual Merchandising", []))
    if tags and random.random() < 0.6:
        tag = random.choice(tags)
        callouts = [
            f"\n\n🔔 {tag} — what's your take?",
            f"\n\nCalling all {tag.lower()} 👆",
            f"\n\n💬 {tag}, I'd love your perspective.",
        ]
        content += random.choice(callouts)
    return content


def save_post(content, topic, style):
    today = date.today().isoformat()
    session = f"_{POST_SESSION}" if POST_SESSION == "evening" else ""
    filename = f"{today}{session}_{topic.lower().replace(' & ', '-').replace(' ', '-')}.md"
    filepath = GENERATED_DIR / filename
    filepath.write_text(f"---\ndate: {today}\ntopic: {topic}\nstyle: {style}\nsession: {POST_SESSION}\n---\n\n{content}\n")
    return filepath


def build_poll_prompt(topic):
    return f"""Generate a LinkedIn POLL for Preethi Prasanna (8+ years Visual Merchandising, Vendor Management & Store Operations).
Topic: {topic}
- Commentary: 2-3 punchy lines that make people WANT to vote. Include 3-4 hashtags.
- Question: max 140 chars, clear and debatable
- 4 options: max 30 chars each, all valid answers
- Relevant to Indian retail/VM/vendor management professionals
- Should attract attention from recruiters and retail industry leaders
Output EXACTLY as JSON: {{"commentary": "text", "question": "q?", "options": ["A", "B", "C", "D"]}}"""


def generate_poll(topic):
    try:
        raw = generate_with_gemini(build_poll_prompt(topic))
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
        poll = json.loads(raw)
        if "question" in poll and "options" in poll and len(poll["options"]) >= 2:
            print("✅ Poll generated with Gemini")
            return poll
    except Exception as e:
        print(f"⚠️ Gemini poll failed ({e}), using template")
    return random.choice(POLL_TEMPLATES)


# ============================================================
# MAIN
# ============================================================

def main():
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    PUBLISHED_DIR.mkdir(parents=True, exist_ok=True)

    history = load_history()
    config = get_today_config()
    topic = config["topic"]
    style = config["style"]

    print(f"{'🌅' if POST_SESSION == 'morning' else '🌙'} {POST_SESSION.upper()} | Topic: {topic} | Style: {style}")

    is_poll = (style == "poll")

    if is_poll:
        print("📊 Generating LinkedIn POLL")
        poll_data = generate_poll(topic)
        content = poll_data.get("commentary", "Share your thoughts! 👇")
        filepath = save_post(content + f"\n\n[POLL: {poll_data['question']}]\n" + "\n".join(poll_data["options"]), topic, "poll")
        post_urn = publish_to_linkedin(content, poll_data)
    else:
        try:
            content = generate_with_gemini(build_prompt(topic, style))
            print("✅ Generated with Gemini")
        except Exception as e:
            print(f"⚠️ Gemini unavailable ({e}), using fallback")
            content = generate_fallback(topic, style)

        if is_duplicate(content, history):
            print("🔄 Duplicate detected, using fallback")
            content = generate_fallback(topic, style)

        content = add_engagement_tag(content, topic)
        filepath = save_post(content, topic, style)
        post_urn = publish_to_linkedin(content)
        poll_data = None

    # Self-comment boost (morning posts, 70% of time)
    if post_urn and POST_SESSION == "morning" and random.random() < 0.7:
        print("💬 Adding self-comment boost...")
        post_self_comment(post_urn)

    # Update history
    published = post_urn is not None
    history["posts"].append({
        "date": date.today().isoformat(),
        "session": POST_SESSION,
        "topic": topic,
        "style": style,
        "file": filepath.name,
        "hash": hashlib.md5(content.encode()).hexdigest(),
        "published": published,
        "post_urn": post_urn or "",
        "type": "poll" if is_poll else "text",
    })
    history["hashes"].append(hashlib.md5(content.encode()).hexdigest())
    save_history(history)

    print(f"\n{'='*50}\n📝 {'POLL' if is_poll else 'POST'}:\n{'='*50}")
    print(content)
    if is_poll and poll_data:
        print(f"\n📊 {poll_data['question']}")
        for i, opt in enumerate(poll_data['options'], 1):
            print(f"   {i}. {opt}")
    print("=" * 50)


if __name__ == "__main__":
    main()
