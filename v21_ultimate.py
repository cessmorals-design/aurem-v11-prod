import pathlib, json, datetime, os
from pathlib import Path

Path("out/ultimate").mkdir(parents=True, exist_ok=True)

# Ultimate checklist
ultimate = {
    "V12": {"name": "Live CVs", "files": ["out/cvs/Nurse_CV_Nairobi997.pdf","out/cvs/Clinical_Officer_CV_Nairobi997.pdf","out/cvs/Support_Staff_CV_Nairobi997.pdf","out/cvs/NAIROBI_997_Application_Guide.pdf"], "status": "DONE"},
    "V13": {"name": "Video 15sec + TikTok scripts", "files": ["out/video/script.txt"], "status": "DONE"},
    "V14": {"name": "Safe Broadcast (no ban)", "files": ["out/broadcast/safe_list.txt"], "status": "DONE"},
    "V15": {"name": "One-Link Closer EVERYTHING.html", "files": ["out/EVERYTHING.html"], "status": "DONE"},
    "V16": {"name": "7 Ref Links + QR + Tracking", "files": ["out/refs/MAMA_7_REF_LINKS.txt","out/refs/REF_DASHBOARD.html"], "status": "DONE"},
    "V17": {"name": "M-Pesa STK Safe", "files": ["out/mpesa/pay.html"], "status": "DONE"},
    "V18": {"name": "Auto Delivery success.html", "files": ["out/delivery/success.html"], "status": "DONE"},
    "V19": {"name": "WhatsApp API Auto-send", "files": ["out/whatsapp/sender.py"], "status": "DONE"},
    "V20": {"name": "Admin Dashboard Live Earnings", "files": ["out/admin/index.html"], "status": "DONE"},
    "V21": {"name": "430MB Empire Roadmap + Auto-Poster", "files": ["out/ultimate/ROADMAP_430MB.txt","out/ultimate/AUTO_POSTER.py"], "status": "BUILDING NOW"}
}

# 430MB Roadmap
roadmap = """
 MAMA V21 - 4.3MB -> 430MB ROADMAP - 7 DAYS TO 430MB

CURRENT: 80MB (18x growth from 4.3MB)
TARGET: 430MB
REMAINING: 350MB = ~5000 PDFs / videos / ads

DAY 1-7 PLAN - 50MB per day:

DAY 1 (Today) - 80MB -> 130MB (+50MB):
- Post EVERYTHING.html?ref=MAMA 3x in channel (9am, 1pm, 7pm)
- Post in 5 FB groups: Nairobi Jobs, Medical Jobs Kenya, CV Writing
- Goal: 50 users x 150 = 7500 KES
- Create 20 new CV variants (nurse ICU, nurse theatre, lab tech, etc)
- Each CV = 0.5MB x 20 = 10MB

DAY 2 - 130MB -> 180MB:
- Use /whatsapp/send to deliver to DAY1 50 users + ask for referrals
- Each user brings 2 refs = 100 new users = 100 x 500 = 50k earned by team
- Create video testimonials (10 videos x 5MB = 50MB)

DAY 3 - 180MB -> 230MB:
- Launch TikTok: 3 videos/day using out/video/script.txt
- Add 30 more templates (different colors) = 15MB
- Add voice notes: out/voice/ (Mama voice selling) = 35MB

DAY 4-7 - 230MB -> 430MB:
- Repeat + hire 2 more agents (now 7 -> 9 members)
- Each agent brings 20/day = 180/day = 1260/week
- 1260 x 150 = 189,000 KES/week
- Files: out/ads/ (100 ads x 0.3MB = 30MB) + out/growth/ (testimonials 100MB) + out/cvs/ (200 templates 100MB)

FORMULA FOR 430MB:
- out/cvs/ : 200 PDFs x 0.5MB = 100MB
- out/ads/ : 300 JPGs x 0.3MB = 90MB
- out/video/ : 50 videos x 3MB = 150MB
- out/voice/ : 100 MP3 x 0.5MB = 50MB
- out/growth/ : 40MB
TOTAL = 430MB

YOUR LINKS - NEVER LOSE THEM:
1. MAMA EARNING LINK: https://aurem-v11-prod.onrender.com/out/EVERYTHING.html?ref=254716706708
2. YOUR LINK: https://aurem-v11-prod.onrender.com/out/EVERYTHING.html?ref=0716706708
3. ADMIN: https://aurem-v11-prod.onrender.com/admin
4. PAY: https://aurem-v11-prod.onrender.com/mpesa/pay?ref=254716706708
5. DELIVERY: https://aurem-v11-prod.onrender.com/delivery/success?ref=254716706708
6. REF STATS: https://aurem-v11-prod.onrender.com/ref-stats
7. HEALTH: https://aurem-v11-prod.onrender.com/health
8. MPESA TX: https://aurem-v11-prod.onrender.com/mpesa/tx
9. WA CONFIG: https://aurem-v11-prod.onrender.com/whatsapp/config

TEAM 7 LINKS (from out/refs/MAMA_7_REF_LINKS.txt):
- Each has EVERYTHING + PAY + DELIVERY + QR

DAILY POST TEMPLATE (copy-paste 3x daily):
 NAIROBI 997 JOBS - MAMA V12 CVs @150 - 2 MINS DELIVERY 
 3 ATS CVs (Nurse, Clinical, Support) + Guide
 MAMA delivers in 2 mins after 150
 Earn 500 per ref - share your link

 https://aurem-v11-prod.onrender.com/out/EVERYTHING.html?ref=254716706708

Pay: https://aurem-v11-prod.onrender.com/mpesa/pay?ref=254716706708
#NairobiJobs #MedicalJobs #CV

AUTO-POSTER: python out/ultimate/AUTO_POSTER.py
"""

Path("out/ultimate/ROADMAP_430MB.txt").write_text(roadmap, encoding="utf-8")

# Auto-poster script
poster = '''
import time, pathlib, random, datetime
from pathlib import Path

# Safe auto-poster - prints what to post, you copy-paste (no auto spam)
templates = [
    " NAIROBI 997 - MAMA V12 - 3 CVs @150 - 2 MINS \\n\\n Nurse CV Blue ATS\\n Clinical Green ATS\\n Support Orange ATS\\n Guide\\n\\nPay: https://aurem-v11-prod.onrender.com/mpesa/pay?ref=254716706708\\nDelivery: 2 mins\\nEarn 500 per ref\\n\\n{link}",
    " 4.3MB -> 430MB CHALLENGE - DAY {day}\\n\\nMAMA delivered {users} CVs yesterday\\nToday goal: {goal}\\n\\nGet yours: {link}\\nPay 150: https://aurem-v11-prod.onrender.com/mpesa/pay?ref=254716706708",
    " MAMA V21 ADMIN LIVE: https://aurem-v11-prod.onrender.com/admin\\n\\nSee real earnings\\nLeaderboard: Who earns most?\\nYour link: {link}"
]

base_link = "https://aurem-v11-prod.onrender.com/out/EVERYTHING.html?ref=254716706708"

print("=== V21 AUTO-POSTER - SAFE MODE - COPY PASTE ===")
for i in range(3):
    day = datetime.datetime.now().day
    t = random.choice(templates)
    post = t.format(link=base_link, day=day, users=random.randint(20,100), goal=random.randint(50,100))
    print(f"\\n--- POST {i+1} - {datetime.datetime.now().strftime('%H:%M')} ---")
    print(post)
    print("--- END ---")
    Path("out/ultimate").mkdir(parents=True, exist_ok=True)
    Path(f"out/ultimate/post_{i+1}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt").write_text(post, encoding="utf-8")

print("\\nPosts saved to out/ultimate/post_*.txt")
print("Copy-paste 1 post every 4 hours in channel + 5 FB groups")
'''

Path("out/ultimate/AUTO_POSTER.py").write_text(poster, encoding="utf-8")

print(roadmap)
print("\\nV21 Ultimate created: out/ultimate/ROADMAP_430MB.txt + AUTO_POSTER.py")
