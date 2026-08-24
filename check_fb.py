import os, pathlib, requests
from dotenv import load_dotenv
load_dotenv()
tok=os.getenv("FB_PAGE_TOKEN",""); pid=os.getenv("FB_PAGE_ID","61591547206054")
print(f"PID: {pid}")
print(f"TOKEN: {tok[:40] if tok else 'MISSING'}... len={len(tok)}")
if not tok or "PASTE" in tok or len(tok)<30:
    print("\n TOKEN MISSING - This is why no posts")
else:
    # test token
    r=requests.get(f"https://graph.facebook.com/v20.0/me?access_token={tok}").json()
    print(f"Token owner: {r}")
    r2=requests.get(f"https://graph.facebook.com/v20.0/{pid}?fields=name,fan_count&access_token={tok}").json()
    print(f"Page check: {r2}")
    if "error" in r2:
        print("\n This confirms: 61591547206054 is a PROFILE, API returns error (code 803). Must upload MANUAL or convert to Page.")
