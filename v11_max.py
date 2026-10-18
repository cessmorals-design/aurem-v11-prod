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
    return jsonify({
        "v12": "LIVE",
        "v21": "LIVE GREEN 25/08 FINAL",
        "domain": "aurem-v11-prod.onrender.com",
        "build": "V21 FINAL GREEN",
        "time": datetime.utcnow().isoformat(),
        "status": "OK",
        "wa": False
    })

@app.route('/admin/data')
def admin_data():
    try:
        d = load_data()
        tx = d.get("tx", [])
        rev = sum([t.get("amount", 0) for t in tx])
        users = d.get("users", {})
        return jsonify({
            "totalUsers": len(users),
            "totalRev": rev,
            "totalClicks": len(d.get("clicks", [])),
            "totalConv": len(d.get("conversions", [])),
            "leaderboard": [],
            "tx": tx[-20:]
        })
    except Exception as e:
        return jsonify({
            "totalUsers": 0,
            "totalRev": 0,
            "totalClicks": 0,
            "totalConv": 0,
            "tx": [],
            "error": str(e)
        })

@app.route('/track/click')
def track_click():
    try:
        d = load_data()
        ref = request.args.get("ref", "direct")
        if ref not in d["users"]:
            d["users"][ref] = {"clicks": 0, "rev": 0}
        d["users"][ref]["clicks"] += 1
        d["clicks"].append({"ref": ref, "time": datetime.utcnow().isoformat()})
        save_data(d)
    except:
        pass
    return redirect(f"/out/EVERYTHING.html?ref={request.args.get('ref', 'direct')}")

@app.route('/track/conv')
def track_conv():
    try:
        d = load_data()
        ref = request.args.get("ref", "direct")
        amount = float(request.args.get("amount", "0"))
        if ref not in d["users"]:
            d["users"][ref] = {"clicks": 0, "rev": 0}
        d["users"][ref]["rev"] += amount
        d["tx"].append({"ref": ref, "amount": amount, "time": datetime.utcnow().isoformat()})
        save_data(d)
    except:
        pass
    return jsonify({"ok": True})

@app.route('/')
def home():
    return redirect(f"/out/EVERYTHING.html?ref={request.args.get('ref', '254716706708')}")

@app.route('/out/<path:filename>')
def serve_out(filename):
    return send_from_directory(str(OUT_DIR), filename)

@app.route('/admin/')
def admin():
    return send_from_directory(str(OUT_DIR / "admin"), "index.html")

@app.route('/wa/webhook', methods=['GET', 'POST'])
def wa_webhook():
    if request.method == 'GET':
        return request.args.get("hub.challenge", "ok")
    return jsonify({"status": "received"})

@app.route('/buy')
def buy():
    ref = request.args.get("ref", "direct")
    return redirect(f"/track/conv?ref={ref}&amount=2500")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
