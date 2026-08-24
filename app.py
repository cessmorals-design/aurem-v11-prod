import os
print("V21 STARTING...")
try:
    from v11_max import app
    print("V21 v11_max.py LOADED OK")
except Exception as e:
    print(f"V21 v11_max FAILED: {e}")
    import traceback; traceback.print_exc()
    from flask import Flask, jsonify
    app = Flask(__name__)
    @app.route('/health')
    def health():
        return jsonify({"v12":"LIVE","v21":"FALLBACK LIVE - v11_max error","error": str(e)})
    @app.route('/')
    def home():
        return f"FALLBACK - v11_max error: {e}"

# Ensure out folder
os.makedirs("out/admin", exist_ok=True)
