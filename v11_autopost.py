import os, time, pathlib, requests, json
from dotenv import load_dotenv
load_dotenv()
DOMAIN=os.getenv("DOMAIN"); PROFILE=os.getenv("FB_PROFILE_ID"); TOK=os.getenv("FB_PAGE_TOKEN"); PID=os.getenv("FB_PAGE_ID")
print(f"Starting V11 Autoposter for Morals Voke {PROFILE} -> {DOMAIN}")
while True:
    ads=list(pathlib.Path("out/ads").glob("*.webp"))
    if not ads: time.sleep(60); continue
    for fp in ads:
        cap=f" {fp.stem.replace('_',' ').upper()} | Apply: https://{DOMAIN}/?ref=0716706708 | Join: https://whatsapp.com/channel/0029VbD5CSQ6LwHlCzEAt01s | Morals Voke {PROFILE}"
        print(f"Queue {fp.name}")
        if TOK and "PASTE" not in TOK and len(TOK)>30:
            try:
                with open(fp,'rb') as f:
                    r=requests.post(f"https://graph.facebook.com/v20.0/{PID}/photos", data={"caption":cap,"access_token":TOK}, files={"source":f}, timeout=60)
                print(f"FB {r.status_code}")
            except Exception as e: print(e)
        else:
            print(f"MANUAL NEEDED: Upload {fp} to FB Reel Morals Voke - Caption: {cap}")
        time.sleep(4*3600)
