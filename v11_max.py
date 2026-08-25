# V21 STABLE PROD - NO DB - NO init_db - 25/08 FINAL
from flask import Flask, jsonify, request, send_from_directory, redirect
import os, json
from datetime import datetime
from pathlib import Path

app = Flask(__name__)
DATA_FILE = "data_v21.json"
OUT_DIR = Path("out")
OUT_DIR.mkdir(exist_ok=True)
(OUT_DIR / "admin").mkdir(exist_ok=True)

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "clicks": [], "conversions": [], "tx": [], "cv_count": 4}
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"users": {}, "clicks": [], "conversions": [], "tx": [], "cv_count": 4}

def save_data(d):
    with open(DATA_FILE, 'w') as f:
        json.dump(d, f, indent=2)

@app.route('/health')
def health():
    return jsonify({"v12":"LIVE","v21":"LIVE FIXED 25/08 - NO CODE 3","domain":"aurem-v11-prod.onrender.com","build":"V21 FINAL GREEN","time":datetime.utcnow().isoformat()})

@app.route('/admin/data')
def admin_data():
    d=load_data()
    tx=d.get("tx",[])
    return jsonify({"totalUsers":len(d.get("users",{})),"totalRev":sum([t.get("amount",0) for t in tx]),"totalClicks":len(d.get("clicks",[])),"totalConv":len(d.get("conversions",[])),"tx":tx[-20:]})

@app.route('/track/click')
def track_click():
    d=load_data()
    ref=request.args.get("ref","direct")
    if ref not in d["users"]:
        d["users"][ref]={"clicks":0,"rev":0,"conv":0}
    d["users"][ref]["clicks"]+=1
    d["clicks"].append({"ref":ref,"time":datetime.utcnow().isoformat()})
    save_data(d)
    return redirect(f"/out/EVERYTHING.html?ref={ref}")

@app.route('/track/conv')
def track_conv():
    d=load_data()
    ref=request.args.get("ref","direct")
    amount=float(request.args.get("amount","0"))
    if ref not in d["users"]:
        d["users"][ref]={"clicks":0,"rev":0,"conv":0}
    d["users"][ref]["rev"]+=amount
    d["tx"].append({"ref":ref,"amount":amount,"time":datetime.utcnow().isoformat()})
    save_data(d)
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
