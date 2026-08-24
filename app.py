import os
print("V21 DOCKER STARTING...")
try:
    from v11_max import app
    print("V21 v11_max.py LOADED OK")
except Exception as e:
    print(f"V21 LOAD FAIL: {e}")
    import traceback; traceback.print_exc()
    from flask import Flask, jsonify
    app = Flask(__name__)
    @app.route('/health')
    def health():
        return jsonify({"v12":"LIVE","v21":"FALLBACK DOCKER LIVE","error": str(e)})
    @app.route('/')
    def home():
        return f"FALLBACK: {e}"
os.makedirs("out/admin", exist_ok=True)
