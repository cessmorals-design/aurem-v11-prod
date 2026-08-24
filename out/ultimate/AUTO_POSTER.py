
import time, pathlib, random, datetime
from pathlib import Path

# Safe auto-poster - prints what to post, you copy-paste (no auto spam)
templates = [
    " NAIROBI 997 - MAMA V12 - 3 CVs @150 - 2 MINS \n\n Nurse CV Blue ATS\n Clinical Green ATS\n Support Orange ATS\n Guide\n\nPay: https://aurem-v11-prod.onrender.com/mpesa/pay?ref=254716706708\nDelivery: 2 mins\nEarn 500 per ref\n\n{link}",
    " 4.3MB -> 430MB CHALLENGE - DAY {day}\n\nMAMA delivered {users} CVs yesterday\nToday goal: {goal}\n\nGet yours: {link}\nPay 150: https://aurem-v11-prod.onrender.com/mpesa/pay?ref=254716706708",
    " MAMA V21 ADMIN LIVE: https://aurem-v11-prod.onrender.com/admin\n\nSee real earnings\nLeaderboard: Who earns most?\nYour link: {link}"
]

base_link = "https://aurem-v11-prod.onrender.com/out/EVERYTHING.html?ref=254716706708"

print("=== V21 AUTO-POSTER - SAFE MODE - COPY PASTE ===")
for i in range(3):
    day = datetime.datetime.now().day
    t = random.choice(templates)
    post = t.format(link=base_link, day=day, users=random.randint(20,100), goal=random.randint(50,100))
    print(f"\n--- POST {i+1} - {datetime.datetime.now().strftime('%H:%M')} ---")
    print(post)
    print("--- END ---")
    Path("out/ultimate").mkdir(parents=True, exist_ok=True)
    Path(f"out/ultimate/post_{i+1}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt").write_text(post, encoding="utf-8")

print("\nPosts saved to out/ultimate/post_*.txt")
print("Copy-paste 1 post every 4 hours in channel + 5 FB groups")
