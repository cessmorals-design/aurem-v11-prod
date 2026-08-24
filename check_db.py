import sqlite3, pathlib
pathlib.Path("logs").mkdir(exist_ok=True)
conn = sqlite3.connect("logs/v11_autopost.db")
conn.execute("CREATE TABLE IF NOT EXISTS users(phone TEXT PRIMARY KEY, email TEXT, ref TEXT, ref_l2 TEXT, ref_l3 TEXT, status TEXT, token TEXT, created TEXT, next_bill TEXT, paid INT, refs INT, posts INT, county TEXT)")
conn.execute("CREATE TABLE IF NOT EXISTS posts(id INTEGER PRIMARY KEY AUTOINCREMENT, file TEXT, platform TEXT, caption TEXT, status TEXT, response TEXT, created TEXT)")
conn.execute("CREATE TABLE IF NOT EXISTS jobs(id INTEGER PRIMARY KEY AUTOINCREMENT, phone TEXT, county TEXT, title TEXT, portal TEXT, status TEXT, created TEXT)")
conn.execute("CREATE TABLE IF NOT EXISTS cv_sales(id INTEGER PRIMARY KEY AUTOINCREMENT, phone TEXT, amount INT, code TEXT, status TEXT, created TEXT)")
conn.commit()
print("DB recreated V12")
for tbl in ["users","cv_sales","jobs","posts"]:
    cnt = conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
    print(f"{tbl.upper()}: {cnt}")
import pathlib
print(f"ADS: {len(list(pathlib.Path('out/ads').glob('*.*')))}")
print(f"CVS: {len(list(pathlib.Path('out/cvs').glob('*.pdf')))}")
