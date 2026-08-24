from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import json, pathlib, os
app=FastAPI(title="AUREM V11 PROD - Morals Voke")
templates=Jinja2Templates(directory="app/templates")
jobs_file=pathlib.Path("out/jobs_today.json")
@app.get("/", response_class=HTMLResponse)
def home(request: Request, ref: str=""):
    jobs=json.loads(jobs_file.read_text(encoding="utf-8")) if jobs_file.exists() else []
    # track ref
    if ref: pathlib.Path("out/refs.log").write_text(f"{ref}\n", encoding="utf-8")
    return templates.TemplateResponse("index.html", {"request":request,"jobs":jobs,"ref":ref,"domain":os.getenv("DOMAIN")})
@app.get("/health")
def health(): return {"status":"ok","ads":len(list(pathlib.Path("out/ads").glob("*.webp"))),"jobs":len(json.loads(jobs_file.read_text())) if jobs_file.exists() else 0,"fb_profile":os.getenv("FB_PROFILE_ID")}
