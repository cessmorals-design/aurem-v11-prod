import os, pathlib, sqlite3, datetime, threading, time, random, requests, logging
from flask import Flask, request, jsonify, render_template_string, send_from_directory
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
DOMAIN = os.getenv("NGROK_DOMAIN", "aurem-v11-prod.onrender.com")
BASE_URL = f"https://{DOMAIN}"
for d in ["out/ads","logs","clients","out/proof","out/cvs"]: pathlib.Path(d).mkdir(parents=True, exist_ok=True)
def get_db():
    conn = sqlite3.connect("logs/v11_autopost.db", check_same_thread=False)
    conn.execute("CREATE TABLE IF NOT EXISTS users(phone TEXT PRIMARY KEY, email TEXT, ref TEXT, ref_l2 TEXT, ref_l3 TEXT, status TEXT, token TEXT, created TEXT, next_bill TEXT, paid INT, refs INT, posts INT, county TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS posts(id INTEGER PRIMARY KEY AUTOINCREMENT, file TEXT, platform TEXT, caption TEXT, status TEXT, response TEXT, created TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS jobs(id INTEGER PRIMARY KEY AUTOINCREMENT, phone TEXT, county TEXT, title TEXT, portal TEXT, status TEXT, created TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS cv_sales(id INTEGER PRIMARY KEY AUTOINCREMENT, phone TEXT, amount INT, code TEXT, status TEXT, created TEXT)")
    conn.commit()
    return conn
db = get_db()
def v12_provision(phone, ref="0716706708", county="Nairobi"):
    token=f"V12_{phone}_{random.randint(100000,999999)}"
    p=pathlib.Path(f"clients/{phone}"); p.mkdir(exist_ok=True)
    (p/"engine.py").write_text(f"# V12 {token} ref:{ref}", encoding="utf-8")
    cur=db.execute("SELECT ref FROM users WHERE phone=?", (ref,)).fetchone()
    ref_l2=cur[0] if cur else "0716706708"
    cur2=db.execute("SELECT ref FROM users WHERE phone=?", (ref_l2,)).fetchone() if ref_l2 else None
    ref_l3=cur2[0] if cur2 else "0716706708"
    db.execute("INSERT OR REPLACE INTO users(phone, ref, ref_l2, ref_l3, status, token, created, paid, refs, posts, county) VALUES (?,?,?,?,?,?,?,?,?,?,?)", (phone, ref, ref_l2, ref_l3, "ACTIVE", token, datetime.datetime.now().isoformat(), 7777, 0, 0, county))
    db.commit()
    try: db.execute("UPDATE users SET refs=refs+1 WHERE phone=?", (ref,)); db.commit()
    except: pass
    return token, ref, ref_l2, ref_l3
@app.route("/")
def home():
    cnt=db.execute("SELECT COUNT(*) FROM users WHERE status='ACTIVE'").fetchone()[0]
    rev=db.execute("SELECT SUM(paid) FROM users").fetchone()[0] or 0
    ref=request.args.get("ref","0716706708")
    return render_template_string(f"<h1>AUREM V12 LIVE</h1><p>ACTIVE:{cnt} REV:{rev} Ref:{ref}</p><form action=/pay method=post><input name=phone placeholder=07... required><input name=ref value={ref} type=hidden><button>PAY 7777 V12</button></form><p><a href=/dash>/dash</a> | <a href=/health>/health</a></p>")
@app.route("/pay", methods=["POST"])
def pay():
    phone=request.form.get("phone","").strip().replace(" ","").replace("+","")
    if phone.startswith("0"): phone="254"+phone[1:]
    ref=request.form.get("ref","0716706708")
    token,r1,r2,r3=v12_provision(phone,ref)
    return jsonify({"status":"DEPLOYED","token":token})
@app.route("/health")
def health():
    return jsonify({"v12":"LIVE","has_token": bool(os.getenv("MPESA_SHORTCODE") or os.getenv("FB_PAGE_TOKEN") or os.getenv("WA_TOKEN")),"wa": bool(os.getenv("WA_TOKEN")),"cv_count": len(list(pathlib.Path("out/cvs").glob("*.pdf"))),"domain":DOMAIN,"timestamp": datetime.datetime.now().isoformat()})
@app.route("/dash")
def dash():
    users=db.execute("SELECT phone, paid FROM users ORDER BY created DESC LIMIT 50").fetchall()
    return "<h1>V12 DASH LIVE</h1>" + "<br>".join([f"{u[0]} {u[1]}" for u in users])
@app.route("/callback", methods=["POST"])
@app.route("/mpesa_cv_callback", methods=["POST"])
@app.route("/webhook", methods=["GET","POST"])
def webhook():
    if request.method=="GET" and request.path=="/webhook":
        if request.args.get("hub.verify_token")==os.getenv("WA_VERIFY","aurem_v12_verify"): return request.args.get("hub.challenge"),200
        return "fail",403
    return jsonify({"ResultCode":0,"ResultDesc":"V12 OK"})
@app.route("/out/ads/<path:fn>")
def serve_ad(fn): return send_from_directory("out/ads", fn)
@app.route("/out/cvs/<path:fn>")
def serve_cv(fn): return send_from_directory("out/cvs", fn)
if __name__=="__main__": app.run(host="0.0.0.0", port=int(os.getenv("PORT",10000)))
