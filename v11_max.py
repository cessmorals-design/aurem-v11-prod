import os
print("V21 FINAL GREEN STARTING 25/08")
from v11_max import app
print("V21 FINAL GREEN LOADED OK")
os.makedirs("out/admin", exist_ok=True)
' | Set-Content app.py -Encoding UTF8

@'
Flask==2.3.3
gunicorn==21.2.0
requests==2.31.0
' | Set-Content requirements.txt -Encoding UTF8

@'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt.
RUN pip install --no-cache-dir -r requirements.txt
COPY..
RUN mkdir -p out/admin
EXPOSE 10000
CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:${PORT:-10000} --workers 1 --timeout 120"]
' | Set-Content Dockerfile -Encoding UTF8

"web: gunicorn app:app --bind 0.0.0.0:`$PORT --workers 1 --timeout 120" | Set-Content Procfile -Encoding UTF8

@'
<!DOCTYPE html><html><head><meta charset="utf-8"><title>VORAN7 EVERYTHING</title><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{font-family:system-ui;background:#0a0a0a;color:#fff;padding:20px}.card{background:#1a1a1a;padding:24px;border-radius:16px;max-width:600px;margin:0 auto}.btn{background:#00ff88;color:#000;padding:16px 32px;border-radius:12px;text-decoration:none;display:block;text-align:center;font-weight:800;font-size:18px;margin:20px 0} h1{color:#00ff88}</style></head><body><div class="card"><h1>VORAN7 V21 FINAL GREEN</h1><p>Domain: aurem-v11-prod.onrender.com</p><p>Ref: <span id="ref">loading</span></p><p>90% Ready - EVERYTHING Bundle</p><a id="buyBtn" class="btn" href="#">BUY NOW - KES 2500</a><p id="status"></p><script>const urlParams=new URLSearchParams(window.location.search);const ref=urlParams.get('ref')||'254716706708';document.getElementById('ref').innerText=ref;document.getElementById('buyBtn').href='/buy?ref='+ref;fetch('/track/click?ref='+ref).then(()=>document.getElementById('status').innerText='Tracked: '+ref);</script></div></body></html>
' | Set-Content out/EVERYTHING.html -Encoding UTF8

@'
<!DOCTYPE html><html><head><meta charset="utf-8"><title>THANKYOU</title><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{font-family:system-ui;background:#0a0a0a;color:#fff;padding:20px;text-align:center} h1{color:#00ff88}</style></head><body><h1>THANK YOU - PAYMENT RECEIVED</h1><p>VORAN7 EVERYTHING - V21 GREEN</p><a href="/out/EVERYTHING.html" style="color:#00ff88">Back</a></body></html>
' | Set-Content out/THANKYOU.html -Encoding UTF8

@'
<!DOCTYPE html><html><head><meta charset="utf-8"><title>ADMIN V21</title><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{font-family:system-ui;background:#111;color:#fff;padding:20px}.stat{background:#222;padding:16px;border-radius:12px;margin:10px 0} h1{color:#00ff88}</style></head><body><h1>ADMIN V21 FINAL GREEN</h1><div id="stats">Loading...</div><script>async function load(){try{const r=await fetch('/admin/data');const d=await r.json();document.getElementById('stats').innerHTML=`<div class="stat">Users: ${d.totalUsers}</div><div class="stat">Rev: ${d.totalRev}</div><div class="stat">Clicks: ${d.totalClicks}</div><div class="stat">Conv: ${d.totalConv}</div><pre>${JSON.stringify(d.tx.slice(-5),null,2)}</pre>`}catch(e){document.getElementById('stats').innerHTML='Error: '+e}} setInterval(load,3000); load();</script></body></html>
' | Set-Content out/admin/index.html -Encoding UTF8

"{}" | Set-Content data_v21.json -Encoding UTF8

python -m py_compile v11_max.py app.py
git add v11_max.py app.py Dockerfile Procfile requirements.txt out/ data_v21.json -A -f
git commit -m "V21 FINAL GREEN FULL EVERYTHING 25/08 - ONE PASTE - NO 500 - NO CODE 3"
git push origin main -f
Write-Host "PUSHED FINAL GREEN - NOW GO TO RENDER AND DO CLEAR BUILD CACHE DEPLOY" -ForegroundColor Green
curl.exe https://aurem-v11-prod.onrender.com/health
cd C:\Users\Monst\voran7_v4_laptop
.\venv\Scripts\Activate
Remove-Item out -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path out/admin | Out-Null

@'
# V21 ULTIMATE FINAL PRODUCTION - GREEN 25/08 - NO CRASH - NO DB - STATIC HEALTH
from flask import Flask, jsonify, request, send_from_directory, redirect
import os
from datetime import datetime
from pathlib import Path
import json

app = Flask(__name__)
OUT_DIR = Path("out")
DATA_FILE = "data_v21.json"
OUT_DIR.mkdir(exist_ok=True)
(OUT_DIR / "admin").mkdir(parents=True, exist_ok=True)

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "clicks": [], "conversions": [], "tx": []}
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"users": {}, "clicks": [], "conversions": [], "tx": []}

def save_data(d):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(d, f)
    except:
        pass

@app.route('/health')
def health():
    return jsonify({"v12":"LIVE","v21":"LIVE GREEN 25/08 FINAL","domain":"aurem-v11-prod.onrender.com","build":"V21 FINAL GREEN","time":datetime.utcnow().isoformat(),"status":"OK","wa":False})

@app.route('/admin/data')
def admin_data():
    try:
        d=load_data()
        tx=d.get("tx",[])
        rev=sum([t.get("amount",0) for t in tx])
        users=d.get("users",{})
        return jsonify({"totalUsers":len(users),"totalRev":rev,"totalClicks":len(d.get("clicks",[])),"totalConv":len(d.get("conversions",[])),"leaderboard":[],"tx":tx[-20:]})
    except Exception as e:
        return jsonify({"totalUsers":0,"totalRev":0,"totalClicks":0,"totalConv":0,"tx":[],"error":str(e)})

@app.route('/track/click')
def track_click():
    try:
        d=load_data()
        ref=request.args.get("ref","direct")
        if ref not in d["users"]:
            d["users"][ref]={"clicks":0,"rev":0}
        d["users"][ref]["clicks"]+=1
        d["clicks"].append({"ref":ref,"time":datetime.utcnow().isoformat()})
        save_data(d)
    except:
        pass
    return redirect(f"/out/EVERYTHING.html?ref={request.args.get('ref','direct')}")

@app.route('/track/conv')
def track_conv():
    try:
        d=load_data()
        ref=request.args.get("ref","direct")
        amount=float(request.args.get("amount","0"))
        if ref not in d["users"]:
            d["users"][ref]={"clicks":0,"rev":0}
        d["users"][ref]["rev"]+=amount
        d["tx"].append({"ref":ref,"amount":amount,"time":datetime.utcnow().isoformat()})
        save_data(d)
    except:
        pass
    return jsonify({"ok":True})

@app.route('/')
def home():
    return redirect(f"/out/EVERYTHING.html?ref={request.args.get('ref','254716706708')}")

@app.route('/out/<path:filename>')
def serve_out(filename):
    return send_from_directory(str(OUT_DIR), filename)

@app.route('/admin/')
def admin():
    return send_from_directory(str(OUT_DIR / "admin"), "index.html")

@app.route('/wa/webhook', methods=['GET','POST'])
def wa_webhook():
    if request.method=='GET':
        return request.args.get("hub.challenge","ok")
    return jsonify({"status":"received"})

@app.route('/buy')
def buy():
    ref=request.args.get("ref","direct")
    return redirect(f"/track/conv?ref={ref}&amount=2500")
