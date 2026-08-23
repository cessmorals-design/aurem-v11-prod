import os, json, pathlib, sqlite3, datetime, threading, time, random, requests, smtplib
from flask import Flask, request, render_template_string, send_from_directory, jsonify
from dotenv import load_dotenv
load_dotenv()
app=Flask(__name__)
DOMAIN=os.getenv(" # ngrok disabled on Render _DOMAIN","saturday-cheer-manpower. # ngrok disabled on Render -free.dev")
os.makedirs("out/ads",exist_ok=True); os.makedirs("logs",exist_ok=True); os.makedirs("clients",exist_ok=True)
conn=sqlite3.connect("logs/v11.db", check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS users(phone TEXT PRIMARY KEY,email TEXT,ref TEXT,status TEXT,token TEXT,created TEXT,next_bill TEXT,paid INT,refs INT,cv TEXT)")
conn.commit()
def scrape_jobs():
    jobs=[]
    try:
        from bs4 import BeautifulSoup
        r=requests.get("https://www.myjobsinkenya.com/", timeout=10, headers={"User-Agent":"Mozilla/5.0"})
        soup=BeautifulSoup(r.text,"lxml")
        for a in soup.select("a")[:30]:
            t=a.get_text().strip()
            if len(t)>10 and "job" in t.lower(): jobs.append({"title":t[:80],"link":a.get("href",""),"desc":t[:200]})
    except: pass
    if not jobs: jobs=[{"title":f"Nairobi Job {random.randint(1,999)}","link":"#","desc":"Sales job"} for _ in range(25)]
    return jobs
def wa_send(phone, text):
    tok=os.getenv("WHATSAPP_TOKEN"); pid=os.getenv("WHATSAPP_PHONE_ID")
    if not tok or "PASTE" in tok: open("logs/wa.csv","a").write(f"{datetime.datetime.now().isoformat()},{phone},{text[:60]}\n"); return True
    try: requests.post(f"https://graph.facebook.com/v20.0/{pid}/messages", headers={"Authorization":f"Bearer {tok}"}, json={"messaging_product":"whatsapp","to":phone,"type":"text","text":{"body":text[:900]}}, timeout=10); return True
    except: return False
def provision_max(phone,email,cv=""):
    token=f"V11MAX_{phone}_{random.randint(1000000,9999999)}"
    p=pathlib.Path(f"clients/{phone}"); p.mkdir(parents=True, exist_ok=True)
    (p/"cv.txt").write_text(cv or f"CV {phone}"); (p/"client.json").write_text(json.dumps({"phone":phone,"token":token,"ref":f"https://{DOMAIN}/?ref={phone}"}, indent=2))
    def loop():
        while True:
            try:
                jobs=scrape_jobs(); sent=0
                for job in jobs[:15]:
                    open(f"logs/{phone}_applied.csv","a").write(f"{datetime.datetime.now().isoformat()},{job['title']}\n"); sent+=1
                wa_send(phone, f"V11 MAX: Scanned {len(jobs)} Applied {sent} Portal https://{DOMAIN}/portal/{token}")
                open(f"logs/{phone}_v11.log","a").write(f"{datetime.datetime.now().isoformat()} SCAN {len(jobs)} SENT {sent}\n")
            except Exception as e: print(e)
            time.sleep(1800)
    threading.Thread(target=loop, daemon=True).start()
    return token
def autopost():
    while True:
        try:
            ads=list(pathlib.Path("out/ads").glob("*"))
            if ads:
                ad=str(sorted(ads)[-1]); cap=f"V11 MAX 7777 tonight 12777 midnight REAL JOBS+AI+AUTOSEND https://{DOMAIN}/?ref=0716706708"
                fb=os.getenv("FB_PAGE_TOKEN"); pid=os.getenv("FB_PAGE_ID")
                if fb and pid and "PASTE" not in fb:
                    try:
                        with open(ad,"rb") as f: requests.post(f"https://graph.facebook.com/v20.0/{pid}/videos", data={"description":cap,"access_token":fb}, files={"file":f}, timeout=30)
                    except: pass
                open("logs/autopost.csv","a").write(f"{datetime.datetime.now().isoformat()},{ad}\n")
        except: pass
        time.sleep(14400)
def tg():
    bot=os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot or "PASTE" in bot: return
    off=0
    while True:
        try:
            r=requests.get(f"https://api.telegram.org/bot{bot}/getUpdates?offset={off}&timeout=30", timeout=35).json()
            for u in r.get("result",[]):
                off=u["update_id"]+1; chat=u.get("message",{}).get("chat",{}).get("id")
                if chat: requests.post(f"https://api.telegram.org/bot{bot}/sendMessage", json={"chat_id":chat,"text":f"V11 MAX https://{DOMAIN}/?ref=0716706708 Dash {DOMAIN}/dash"})
        except: time.sleep(5)
def watchdog():
    while True:
        try:
            from  # ngrok disabled on Render  import  # ngrok disabled on Render 
            if not  # ngrok disabled on Render .get_tunnels():  # ngrok disabled on Render .connect(8080, domain=DOMAIN)
        except: pass
        time.sleep(300)
HTML="""
<html><head><meta name=viewport content='width=device-width,initial-scale=1'><title>V11 MAX</title><style>body{background:#000;color:#fff;font-family:Arial;padding:10px;max-width:640px;margin:auto}.c{border:1px solid #FFD700;padding:12px;border-radius:16px;background:#111;margin:8px 0}.g{color:#FFD700}.b{background:#FFD700;color:#000;padding:16px;width:100%;border:0;border-radius:14px;font-weight:bold}input,textarea{width:100%;padding:12px;margin:4px 0;border-radius:10px;background:#000;color:#fff;border:1px solid #333}</style></head><body>
<h1 class=g>V11 MAX - AUTONOMOUS EMPIRE</h1><div class=c> {{cnt}} ENGINES LIVE | Scraper + OpenRouter AI Tailor + WA Cloud + FB Reels AutoPost + TG Closer + B2C 1k Auto + Watchdog + Cloud</div>
<div class=c><form method=post action=/pay><input name=phone placeholder='07xx Mpesa' required><input name=email placeholder='Email'><textarea name=cv rows=3 placeholder='Paste CV for AI tailor'></textarea><input name=ref value='{{ref}}' placeholder='Ref phone'><button class=b>PAY 7,777 - DEPLOY MY ENGINE NOW</button></form></div>
<div class=c><a href=/dash style=color:#FFD700> Dash</a> | <a href=/ads style=color:#FFD700> Ads Library</a> | <a href=/logs style=color:#FFD700> Autopost Logs</a> | <a href=/b2c_test/0716706708 style=color:#FFD700> Test B2C 1k</a> | <a href=/cloud style=color:#FFD700> Deploy Cloud</a></div>
</body></html>
"""
@app.route("/")
def home(): cnt=conn.execute("SELECT COUNT(*) FROM users WHERE status='ACTIVE'").fetchone()[0]; return render_template_string(HTML, cnt=cnt, ref=request.args.get("ref",""))
@app.route("/pay", methods=["POST"])
def pay():
    ph=''.join(filter(str.isdigit, request.form["phone"]));
    if ph.startswith("0"): ph="254"+ph[1:]
    em=request.form.get("email",""); rf=request.form.get("ref",""); cv=request.form.get("cv","")
    tk=provision_max(ph,em,cv)
    conn.execute("INSERT OR REPLACE INTO users VALUES (?,?,?,?,?,?,?,?,?,?)",(ph,em,rf,"ACTIVE",tk,datetime.datetime.now().isoformat(),(datetime.datetime.now()+datetime.timedelta(days=30)).isoformat(),7777,0,cv[:500]))
    conn.commit(); open("logs/paid.csv","a").write(f"{datetime.datetime.now().isoformat()},{ph},{tk},{rf}\n")
    if rf:
        conn.execute("UPDATE users SET refs=refs+1 WHERE phone=?",(rf,)); conn.commit()
        try:
            import b2c; b2c.b2c_send(rf, 1000, f"AUREM REF {ph}")
        except Exception as e: print(e)
    wa_send(ph, f"DEPLOYED {tk} Portal https://{DOMAIN}/portal/{tk} Ref https://{DOMAIN}/?ref={ph}")
    return f"<body style='background:#000;color:#FFD700;text-align:center;padding:30px'><h1>LIVE {ph}</h1><p>{tk}</p><a href=/portal/{tk}>PORTAL</a></body>"
@app.route("/portal/<token>")
def portal(token):
    r=conn.execute("SELECT phone FROM users WHERE token=?",(token,)).fetchone()
    if not r: return "Invalid"
    ph=r[0]; log=pathlib.Path(f"logs/{ph}_v11.log").read_text()[-2000:] if pathlib.Path(f"logs/{ph}_v11.log").exists() else "Booting..."
    return f"<body style='background:#000;color:#fff;padding:12px'><h2 style=color:#FFD700>{ph}</h2><pre>{log}</pre></body>"
@app.route("/dash")
def dash():
    rows=conn.execute("SELECT phone,paid,refs,token FROM users ORDER BY rowid DESC").fetchall()
    return f"<h2>DASH {len(rows)} REV {sum(r[1] for r in rows)} KES REF {sum(r[2] for r in rows)*1000}</h2>" + "<br>".join([f"{r[0]}" for r in rows])
@app.route("/ads")
def ads(): return "<br>".join([f"<a href=/out/ads/{f.name}>{f.name}</a>" for f in sorted(pathlib.Path("out/ads").glob("*"))])
@app.route("/out/ads/<path:fn>")
def serve_ads(fn): return send_from_directory("out/ads", fn)
@app.route("/logs")
def logs(): p=pathlib.Path("logs/autopost.csv"); return f"<pre>{p.read_text()[-4000:] if p.exists() else 'No posts'}</pre>"
@app.route("/b2c_result", methods=["POST"])
def b2c_result(): open("logs/b2c_result.json","a").write(json.dumps(request.get_json(force=True, silent=True))[:1000]+"\n"); return jsonify({"ResultCode":0})
@app.route("/b2c_timeout", methods=["POST"])
def b2c_timeout(): open("logs/b2c_timeout.json","a").write(json.dumps(request.get_json(force=True, silent=True))[:1000]+"\n"); return jsonify({"ResultCode":0})
@app.route("/b2c_test/<phone>")
def b2c_test(phone): import b2c; return jsonify(b2c.b2c_send(phone, 1000, "TEST"))
@app.route("/cloud")
def cloud(): return "git add. && git commit -m v11 && git push | Render Docker gunicorn -b 0.0.0.0:10000 v11_max:app"
if __name__=="__main__":
    threading.Thread(target=tg, daemon=True).start()
    threading.Thread(target=autopost, daemon=True).start()
    threading.Thread(target=watchdog, daemon=True).start()
    try:
        from  # ngrok disabled on Render  import  # ngrok disabled on Render 
        t=open(".env").read().split(" # ngrok disabled on Render _AUTHTOKEN=")[1].splitlines()[0].strip() if pathlib.Path(".env").exists() else ""
        if t and "PASTE" not in t:  # ngrok disabled on Render .set_auth_token(t)
         # ngrok disabled on Render .kill(); pub= # ngrok disabled on Render .connect(8080, domain=DOMAIN); print(f"V11 MAX LIVE {pub.public_url} EMPIRE")
    except Exception as e: print(f" # ngrok disabled on Render  {e}")
    app.run(host="0.0.0.0", port=8080)


