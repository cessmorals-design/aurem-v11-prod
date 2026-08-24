import sqlite3, pathlib
p = pathlib.Path("logs/v11_autopost.db")
conn = sqlite3.connect(str(p))
print("=== V12 DASHBOARD ===")
for tbl in ["users","cv_sales","jobs","posts"]:
    try:
        cnt = conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        print(f"{tbl}: {cnt}")
    except Exception as e:
        print(f"{tbl}: 0 (table missing - {e})")
print(f"ADS files: {len(list(pathlib.Path('out/ads').glob('*.*')))}")
print(f"CV PDFs: {len(list(pathlib.Path('out/cvs').glob('*.pdf')))}")
# show last users
try:
    rows = conn.execute("SELECT phone, paid, ref FROM users ORDER BY created DESC LIMIT 5").fetchall()
    print("\nLast users:")
    for r in rows: print(r)
except: print("\nNo users yet")
