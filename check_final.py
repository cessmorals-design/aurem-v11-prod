from pathlib import Path
out_files = len(list(Path('out').rglob('*.*')))
out_size = round(sum([f.stat().st_size for f in Path('out').rglob('*') if f.is_file()])/1024/1024,1)
print(f"OUT files: {out_files}")
print(f"OUT SIZE: {out_size} MB | {round(out_size/430*100,1)}% to 430MB")
print(f"ULTIMATE: {Path('out/ultimate/ROADMAP_430MB.txt').exists()}")
print(f"ADMIN: {Path('out/admin/index.html').exists()}")
print(f"EVERYTHING: {Path('out/EVERYTHING.html').exists()}")
print(f"DB: {Path('logs/v11_autopost.db').exists()}")
