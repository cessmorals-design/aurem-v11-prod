param([string]$db, [string]$sql)
python -c "import sqlite3, sys; conn=sqlite3.connect(sys.argv[1]); cur=conn.execute(sys.argv[2]); rows=cur.fetchall(); [print(r[0] if len(r)==1 else r) for r in rows]" "$db" "$sql"
