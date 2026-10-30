# V21 ULTIMATE FINAL PRODUCTION - GREEN 25/08 - NO CRASH - NO DB - STATIC HEALTH
from flask import Flask, jsonify, request, send_from_directory, redirect
import os
import hmac
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
        return {"users": {}, "clicks": [], "conversions": [], "conversion_signals": [], "tx": []}
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
        "status": "available",
        "payment_state": "disabled",
        "revenue_state": "unverified",
        "execution_authority": "none",
        "wa": False
    })

@app.route('/admin/data')
def admin_data():
    expected = os.environ.get("AUREM_ADMIN_TOKEN", "").strip()
    supplied = request.headers.get("Authorization", "")
    if not expected or not supplied.startswith("Bearer "):
        return jsonify({"ok": False, "error": "admin_auth_required"}), 401
    if not hmac.compare_digest(supplied[7:].strip(), expected):
        return jsonify({"ok": False, "error": "admin_auth_invalid"}), 401
    try:
        d = load_data()
        users = d.get("users", {})
        return jsonify({
            "totalUsers": len(users),
            "totalRev": None,
            "revenueStatus": "not_connected_to_verified_owner_ledger",
            "totalClicks": len(d.get("clicks", [])),
            "totalConv": len(d.get("conversions", [])),
            "unverifiedConversionSignals": len(d.get("conversion_signals", [])) + len(d.get("tx", [])),
            "leaderboard": [],
            "tx": []
        })
    except Exception as e:
        return jsonify({
            "totalUsers": None,
            "totalRev": None,
            "revenueStatus": "unavailable",
            "totalClicks": None,
            "totalConv": None,
            "unverifiedConversionSignals": None,
            "tx": [],
            "error": "admin_data_unavailable"
        })

@app.route('/track/click')
def track_click():
    try:
        d = load_data()
        ref = request.args.get("ref", "direct")[:64]
        if ref not in d["users"]:
            d["users"][ref] = {"clicks": 0}
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
        ref = request.args.get("ref", "direct")[:64]
        signals = d.setdefault("conversion_signals", [])
        signals.append({
            "ref": ref,
            "observed_at": datetime.utcnow().isoformat(),
            "status": "unverified",
        })
        save_data(d)
    except Exception:
        return jsonify({"ok": False, "error": "signal_record_failed"}), 500
    return jsonify({
        "ok": True,
        "status": "unverified_signal",
        "revenue_recorded": False,
    }), 202

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
    return jsonify({
        "ok": False,
        "error": "checkout_not_connected",
        "message": "Checkout is disabled until the canonical JARVIS Profit Engine provides an authenticated payment session.",
    }), 503

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
