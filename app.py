try:
    from v11_max import app as application
    app = application
    print("Loaded v11_max.py V21")
except Exception as e:
    print(f"v11_max import failed: {e} - falling back to minimal")
    from flask import Flask, jsonify
    app = Flask(__name__)
    @app.route('/health')
    def health():
        return jsonify({"v12":"FALLBACK","error":str(e),"fix":"check v11_max.py logs"})
    @app.route('/')
    def home():
        return f"FALLBACK ACTIVE - Error: {e} - check logs"
