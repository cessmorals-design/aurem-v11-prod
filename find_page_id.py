import os, requests
from dotenv import load_dotenv
load_dotenv()
tok=os.getenv("FB_PAGE_TOKEN")
if not tok or len(tok)<20:
    tok=input("Paste your FB Token (EAAG...): ").strip()
    if tok:
        with open(".env","a",encoding="utf-8") as f: f.write(f"\nFB_PAGE_TOKEN={tok}\n")
url=f"https://graph.facebook.com/v20.0/me/accounts?access_token={tok}"
r=requests.get(url, timeout=15)
print(r.text[:3000])
try:
    data=r.json().get("data",[])
    for p in data:
        print(f"\n FOUND PAGE: {p['name']} -> ID: {p['id']}")
        print(f"Token: {p['access_token'][:40]}...")
        # save
        with open(".env","a",encoding="utf-8") as f:
            f.write(f"\nFB_PAGE_ID={p['id']}\nFB_PAGE_TOKEN={p['access_token']}\n")
    if data:
        print("\n Saved to .env - now run python post_now.py")
    else:
        print("\nNo pages found - token may be user token without pages_show_list. Generate Page Token in Graph Explorer.")
except Exception as e:
    print(e)
