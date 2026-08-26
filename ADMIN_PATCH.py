# === V21 ADMIN PATCH FOR v11_max.py ===
@app.route('/out/admin/index.html')
def admin_page():
    return send_from_directory('out/admin', 'index.html')

@app.route('/admin')
def admin_alias():
    return send_from_directory('out/admin', 'index.html')

@app.route('/admin/data')
def admin_data():
    import sqlite3, pathlib
    from pathlib import Path
    conn = sqlite3.connect('logs/v11_autopost.db')
    try: totalUsers = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    except: totalUsers=0
    try: totalRev = conn.execute("SELECT COALESCE(SUM(paid),0) FROM users").fetchone()[0]
    except: totalRev=0
    try: totalClicks = conn.execute("SELECT COUNT(*) FROM ref_tracking").fetchone()[0]
    except: totalClicks=0
    try: totalConv = conn.execute("SELECT COALESCE(SUM(converted),0) FROM ref_tracking").fetchone()[0]
    except: totalConv=0
    try: sizeMB = round(sum([f.stat().st_size for f in Path("out").rglob("*") if f.is_file()])/1024/1024, 1)
    except: sizeMB=0
    leaderboard=[]
    try:
        team = conn.execute("SELECT name, ref_code, role FROM team_members").fetchall()
        for name, ref_code, role in team:
            clicks = conn.execute("SELECT COUNT(*) FROM ref_tracking WHERE ref_code=?", (ref_code,)).fetchone()[0]
            conv = conn.execute("SELECT COALESCE(SUM(converted),0) FROM ref_tracking WHERE ref_code=?", (ref_code,)).fetchone()[0]
            revenue = conn.execute("SELECT COALESCE(SUM(amount),0) FROM ref_tracking WHERE ref_code=?", (ref_code,)).fetchone()[0]
            leaderboard.append({"name":name,"ref":ref_code,"role":role,"clicks":clicks,"conv":int(conv),"revenue":int(revenue),"earn":int(conv*500)})
        leaderboard.sort(key=lambda x: x['earn'], reverse=True)
    except: pass
    tx=[]
    try:
        rows = conn.execute("SELECT phone, ref, amount, status, created FROM mpesa_tx ORDER BY id DESC LIMIT 20").fetchall()
        for r in rows:
            tx.append({"phone":r[0],"ref":r[1],"amount":r[2],"status":r[3],"created":r[4]})
    except: pass
    conn.close()
    return {"totalUsers":totalUsers,"totalRev":totalRev,"totalClicks":totalClicks,"totalConv":int(totalConv),"sizeMB":sizeMB,"leaderboard":leaderboard,"tx":tx}

@app.route('/out/ultimate/ROADMAP_430MB.txt')
def roadmap_txt():
    return send_from_directory('out/ultimate', 'ROADMAP_430MB.txt')
