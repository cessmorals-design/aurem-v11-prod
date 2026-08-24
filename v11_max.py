import os, json, sqlite3, datetime, pathlib
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, redirect

app = Flask(__name__, static_folder='out', static_url_path='/out')

for p in ["out","out/ads","out/cvs","out/refs","out/qr","out/mpesa","out/delivery","out/whatsapp","out/admin","out/ultimate","logs"]:
    Path(p).mkdir(parents=True, exist_ok=True)

def init_db():
    conn = sqlite3.connect('logs/v11_autopost.db')
    conn.execute("CREATE TABLE IF NOT EXISTS users(phone TEXT PRIMARY KEY, email TEXT, ref TEXT, ref_l2 TEXT, ref_l3 TEXT, status TEXT, token TEXT, created TEXT, next_bill TEXT, paid INT, refs INT, posts INT, county TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS ref_tracking(id INTEGER PRIMARY KEY AUTOINCREMENT, ref_code TEXT, visitor_ip TEXT, clicked TEXT, converted INT, amount INT, source TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS mpesa_tx(id INTEGER PRIMARY KEY AUTOINCREMENT, phone TEXT, ref TEXT, amount INT, status TEXT, created TEXT, response TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS team_members(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, ref_code TEXT, role TEXT, total_refs INT, total_earned INT, created TEXT)")
    # Seed 7 members if empty
    cnt = conn.execute("SELECT COUNT(*) FROM team_members").fetchone()[0]
    if cnt==0:
        team = [
            ("MAMA","254716706708","ADMIN"),
            ("YOU","0716706708","OWNER"),
            ("Agent1","254700000001","AGENT"),
            ("Agent2","254700000002","AGENT"),
            ("Agent3","254700000003","AGENT"),
            ("Agent4","254700000004","AGENT"),
            ("Agent5","254700000005","AGENT"),
        ]
        for name, ref, role in team:
            conn.execute("INSERT INTO team_members(name, phone, ref_code, role, created) VALUES (?,?,?,?,?)",(name, ref, role, datetime.datetime.now().isoformat()))
    conn.commit(); conn.close()

init_db()

@app.before_request
def track_ref():
    ref = request.args.get('ref')
    if ref and len(ref)>=7:
        try:
            conn = sqlite3.connect('logs/v11_autopost.db')
            conn.execute("INSERT INTO ref_tracking(ref_code, visitor_ip, clicked, converted, amount, source) VALUES (?,?,?,?,?,?)",(ref, request.remote_addr, datetime.datetime.now().isoformat(),0,0,request.path))
            conn.commit(); conn.close()
        except: pass

@app.route('/health')
def health():
    try: cv_count = len(list(Path("out/cvs").glob("*.pdf")))
    except: cv_count=0
    try: sizeMB = round(sum([f.stat().st_size for f in Path("out").rglob("*") if f.is_file()])/1024/1024,1)
    except: sizeMB=0
    return jsonify({
        "domain":"aurem-v11-prod.onrender.com",
        "v12":"LIVE",
        "v21":"LIVE - ADMIN + EVERYTHING + REF + MPESA + WA",
        "cv_count":cv_count,
        "sizeMB":sizeMB,
        "has_token":bool(os.environ.get("WHATSAPP_TOKEN")),
        "wa":bool(os.environ.get("WHATSAPP_PHONE_ID")),
        "timestamp":datetime.datetime.now().isoformat(),
        "routes":["/","/health","/admin","/admin/data","/ref-stats","/mpesa/tx","/out/EVERYTHING.html","/everything","/out/mpesa/pay.html","/mpesa/pay","/out/delivery/success.html","/delivery/success","/out/refs/REF_DASHBOARD.html","/out/ultimate/ROADMAP_430MB.txt"]
    })

@app.route('/')
def home():
    ref = request.args.get('ref','0716706708')
    if Path("out/EVERYTHING.html").exists():
        return redirect(f"/out/EVERYTHING.html?ref={ref}")
    return f"<h1>V21 LIVE</h1><p><a href='/out/EVERYTHING.html?ref={ref}'>EVERYTHING</a> | <a href='/admin'>Admin</a></p>"

@app.route('/ref-stats')
def ref_stats():
    conn = sqlite3.connect('logs/v11_autopost.db')
    try: rows = conn.execute("SELECT ref_code, COUNT(*) as clicks, COALESCE(SUM(converted),0) as conv, COALESCE(SUM(amount),0) as rev FROM ref_tracking GROUP BY ref_code ORDER BY clicks DESC").fetchall()
    except: rows=[]
    try: team = conn.execute("SELECT name, ref_code FROM team_members").fetchall()
    except: team=[]
    conn.close()
    html="<h1>V21 Ref Stats</h1><style>body{font-family:sans-serif;padding:15px} table{border-collapse:collapse;width:100%} td,th{border:1px solid #ddd;padding:8px}</style><table><tr><th>Ref</th><th>Name</th><th>Clicks</th><th>Conv</th><th>Rev</th><th>Earn 500x</th></tr>"
    for ref, clicks, conv, rev in rows:
        name = next((t[0] for t in team if t[1]==ref), ref)
        html+=f"<tr><td>{ref}</td><td>{name}</td><td>{clicks}</td><td>{conv}</td><td>{rev}</td><td>{conv*500}</td></tr>"
    html+="</table><p><a href='/admin'>Admin</a> | <a href='/out/refs/REF_DASHBOARD.html'>Ref Dashboard</a></p>"
    return html

@app.route('/out/mpesa/pay.html')
def mpesa_pay_page(): return send_from_directory('out/mpesa','pay.html') if Path('out/mpesa/pay.html').exists() else "Pay page missing - run v17"
@app.route('/mpesa/pay')
def mpesa_pay_alias(): return send_from_directory('out/mpesa','pay.html') if Path('out/mpesa/pay.html').exists() else "Pay page missing"

@app.route('/mpesa/stk', methods=['POST'])
def mpesa_stk():
    data = request.get_json() or {}
    phone = data.get('phone','')
    ref = data.get('ref','0716706708')
    amount = int(data.get('amount',150))
    if not phone.startswith('2547') or len(phone)!=12:
        return jsonify({"error":"Phone must be 2547XXXXXXXX"}),400
    consumer_key = os.environ.get('MPESA_CONSUMER_KEY')
    if not consumer_key:
        conn = sqlite3.connect('logs/v11_autopost.db')
        conn.execute("INSERT INTO mpesa_tx(phone, ref, amount, status, created, response) VALUES (?,?,?,?,?,?)",(phone, ref, amount, "SIMULATED", datetime.datetime.now().isoformat(),"simulated"))
        conn.commit(); conn.close()
        return jsonify({"ResponseCode":"0","CustomerMessage":"SIMULATED - Pay manual to 0716706708"})
    # Real DARAJA here if keys set
    return jsonify({"ResponseCode":"0","CustomerMessage":"STK Sent"})

@app.route('/mpesa/callback', methods=['POST'])
def mpesa_callback():
    data = request.get_json() or {}
    ref = request.args.get('ref','0716706708')
    phone="254700000000"
    try:
        items = data.get('Body',{}).get('stkCallback',{}).get('CallbackMetadata',{}).get('Item',[])
        for it in items:
            if it.get('Name')=='PhoneNumber': phone=str(it.get('Value'))
    except: pass
    try:
        Path("out/mpesa").mkdir(parents=True, exist_ok=True)
        Path("out/mpesa/callback.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
        result_code = data.get('Body',{}).get('stkCallback',{}).get('ResultCode',1)
        if result_code==0:
            conn = sqlite3.connect('logs/v11_autopost.db')
            conn.execute("UPDATE ref_tracking SET converted=1, amount=150 WHERE ref_code=? ORDER BY id DESC LIMIT 1",(ref,))
            conn.execute("INSERT OR REPLACE INTO users(phone, ref, status, paid, created) VALUES (?,?,?,?,?)",(phone, ref, "ACTIVE",150, datetime.datetime.now().isoformat()))
            conn.execute("INSERT INTO mpesa_tx(phone, ref, amount, status, created, response) VALUES (?,?,?,?,?,?)",(phone, ref,150,"SUCCESS",datetime.datetime.now().isoformat(),json.dumps(data)))
            conn.commit(); conn.close()
    except: pass
    return {"ResultCode":0,"ResultDesc":"Accepted"}

@app.route('/mpesa/callback-wa', methods=['POST'])
def mpesa_callback_wa(): return mpesa_callback()

@app.route('/mpesa/tx')
def mpesa_tx():
    conn = sqlite3.connect('logs/v11_autopost.db')
    try: rows = conn.execute("SELECT phone, ref, amount, status, created FROM mpesa_tx ORDER BY id DESC LIMIT 50").fetchall()
    except: rows=[]
    conn.close()
    html="<h1>M-Pesa TX</h1><table border=1><tr><th>Phone</th><th>Ref</th><th>Amount</th><th>Status</th><th>Time</th></tr>"
    for r in rows: html+=f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td></tr>"
    html+="</table>"
    return html

@app.route('/out/delivery/success.html')
def delivery_success(): return send_from_directory('out/delivery','success.html')
@app.route('/delivery/success')
def delivery_success_alias(): return send_from_directory('out/delivery','success.html')
@app.route('/delivery')
def delivery_alias2(): return send_from_directory('out/delivery','success.html')
@app.route('/deliver/<phone>')
def manual_deliver(phone):
    ref = request.args.get('ref','0716706708')
    try:
        conn = sqlite3.connect('logs/v11_autopost.db')
        conn.execute("INSERT OR REPLACE INTO users(phone, ref, status, paid, created) VALUES (?,?,?,?,?)",(phone, ref, "ACTIVE",150, datetime.datetime.now().isoformat()))
        conn.commit(); conn.close()
    except: pass
    return f"<h1>Deliver to {phone}</h1><p><a href='/out/delivery/success.html?ref={ref}&phone={phone}'>Open Delivery</a></p>"

@app.route('/whatsapp/send/<phone>')
def whatsapp_send_manual(phone):
    ref = request.args.get('ref','0716706708')
    try:
        import sys; sys.path.append('.')
        from out.whatsapp.sender import send_full_pack
        result = send_full_pack(phone, ref)
        return jsonify({"status":"sent","phone":phone,"ref":ref,"result":result})
    except Exception as e:
        return jsonify({"status":"simulated","phone":phone,"ref":ref,"error":str(e)})

@app.route('/whatsapp/config')
def whatsapp_config():
    return jsonify({"token_set":bool(os.environ.get("WHATSAPP_TOKEN")),"phone_id_set":bool(os.environ.get("WHATSAPP_PHONE_ID")),"status":"LIVE" if os.environ.get("WHATSAPP_TOKEN") else "SIMULATED"})

@app.route('/out/admin/index.html')
def admin_page(): return send_from_directory('out/admin','index.html')
@app.route('/admin')
def admin_alias(): return send_from_directory('out/admin','index.html')
@app.route('/admin/data')
def admin_data():
    conn = sqlite3.connect('logs/v11_autopost.db')
    try: totalUsers = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    except: totalUsers=0
    try: totalRev = conn.execute("SELECT COALESCE(SUM(paid),0) FROM users").fetchone()[0]
    except: totalRev=0
    try: totalClicks = conn.execute("SELECT COUNT(*) FROM ref_tracking").fetchone()[0]
    except: totalClicks=0
    try: totalConv = conn.execute("SELECT COALESCE(SUM(converted),0) FROM ref_tracking").fetchone()[0]
    except: totalConv=0
    try: sizeMB = round(sum([f.stat().st_size for f in Path("out").rglob("*") if f.is_file()])/1024/1024,1)
    except: sizeMB=0
    leaderboard=[]
    try:
        team = conn.execute("SELECT name, ref_code, role FROM team_members").fetchall()
        for name, ref_code, role in team:
            clicks = conn.execute("SELECT COUNT(*) FROM ref_tracking WHERE ref_code=?", (ref_code,)).fetchone()[0]
            conv = conn.execute("SELECT COALESCE(SUM(converted),0) FROM ref_tracking WHERE ref_code=?", (ref_code,)).fetchone()[0]
            revenue = conn.execute("SELECT COALESCE(SUM(amount),0) FROM ref_tracking WHERE ref_code=?", (ref_code,)).fetchone()[0]
            leaderboard.append({"name":name,"ref":ref_code,"role":role,"clicks":clicks,"conv":int(conv),"revenue":int(revenue),"earn":int(conv*500),"payout":f"/deliver/254700000001?ref={ref_code}"})
        leaderboard.sort(key=lambda x: x['earn'], reverse=True)
    except: pass
    tx=[]
    try:
        rows = conn.execute("SELECT phone, ref, amount, status, created FROM mpesa_tx ORDER BY id DESC LIMIT 20").fetchall()
        for r in rows: tx.append({"phone":r[0],"ref":r[1],"amount":r[2],"status":r[3],"created":r[4]})
    except: pass
    conn.close()
    return jsonify({"totalUsers":totalUsers,"totalRev":totalRev,"totalClicks":totalClicks,"totalConv":int(totalConv),"sizeMB":sizeMB,"leaderboard":leaderboard,"tx":tx})

@app.route('/out/EVERYTHING.html')
def everything_page(): return send_from_directory('out','EVERYTHING.html')
@app.route('/everything')
def everything_alias():
    ref = request.args.get('ref','0716706708')
    return redirect(f"/out/EVERYTHING.html?ref={ref}")

@app.route('/out/refs/REF_DASHBOARD.html')
def ref_dash(): return send_from_directory('out/refs','REF_DASHBOARD.html')
@app.route('/out/ultimate/ROADMAP_430MB.txt')
def roadmap_txt(): return send_from_directory('out/ultimate','ROADMAP_430MB.txt')

if __name__ == '__main__':
    port = int(os.environ.get('PORT',10000))
    app.run(host='0.0.0.0', port=port, debug=False)
