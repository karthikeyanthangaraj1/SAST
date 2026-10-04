import os
import subprocess
from flask import Flask, render_template, request, send_file, flash, redirect

app = Flask(__name__)
app.secret_key = "sast-security-key"
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan_file():
    if 'file' not in request.files:
        return "No file uploaded", 400
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    target_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(target_path)

    json_report = os.path.join(OUTPUT_FOLDER, "trivy-report.json")
    md_report = os.path.join(OUTPUT_FOLDER, "SECURITY_REPORT.md")
    pdf_report = os.path.join(OUTPUT_FOLDER, "SECURITY_REPORT.pdf")

    # 1. Execute Trivy scan on uploaded file/folder
    subprocess.run([
        "trivy", "fs", "--security-checks", "vuln,config,secret",
        "--format", "json", "-o", json_report, target_path
    ], check=True)

    # 2. Trigger Local AI Analysis via OpenCode & Ollama
    os.environ["OPENAI_API_BASE"] = "http://localhost:11434/v1"
    os.environ["OPENAI_API_KEY"] = "ollama"
    
    prompt = f"Read {json_report}, analyze code logic flaws, and write a Marp-formatted slide/doc markdown file at {md_report}."
    subprocess.run(["opencode", "run", "--model", "qwen2.5-coder:7b", "--prompt", prompt], check=True)

    # 3. Convert Markdown to Executive PDF
    subprocess.run(["marp", "--pdf", md_report, "-o", pdf_report], check=True)

    return send_file(pdf_report, as_attachment=True, download_name=f"Security_Report_{file.filename}.pdf")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)