import os, subprocess, tempfile, shutil
from flask import Flask, request, jsonify, send_from_directory

BIN = os.environ.get("BIN_DIR", "/app/bin")
STATIC = os.path.join(os.path.dirname(__file__), "..", "frontend")
STAGES = ["lexical", "syntax", "semantic", "icg"]
OUT_FILES = ["parsedTable.txt", "symbolTable.txt", "constantTable.txt", "threeAddressCode.txt"]
app = Flask(__name__, static_folder=STATIC, static_url_path="")

def run_stage(stage, code):
    d = tempfile.mkdtemp()
    try:
        with open(os.path.join(d, "input.c"), "w") as f:
            f.write(code)
        try:
            p = subprocess.run([os.path.join(BIN, stage), "input.c"], cwd=d,
                               capture_output=True, text=True, timeout=5)
            out, rc = p.stdout + p.stderr, p.returncode
        except subprocess.TimeoutExpired:
            out, rc = "Timed out after 5s", -1
        files = {}
        for n in OUT_FILES:
            fp = os.path.join(d, n)
            if os.path.exists(fp):
                files[n] = open(fp, errors="replace").read()
        # void main() in the compiler sources leaves a random exit code, so only a signal/timeout counts as a crash
        return {"ok": rc == 0, "crashed": rc < 0, "stdout": out, "files": files}
    finally:
        shutil.rmtree(d, ignore_errors=True)

@app.post("/api/compile")
def compile_code():
    code = (request.get_json(silent=True) or {}).get("code", "")
    if not code.strip() or len(code) > 20000:
        return jsonify(error="Provide 1-20000 characters of C code"), 400
    return jsonify({s: run_stage(s, code) for s in STAGES})

@app.get("/")
def index():
    return send_from_directory(STATIC, "index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
