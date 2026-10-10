from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import re
from pathlib import Path

app = Flask(__name__)

UPLOAD_FOLDER = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {"pdf", "txt", "epub", "md", "rtf"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_text_file(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def extract_text_from_pdf(file_path):
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        return "PDF extraction requires PyPDF2. Install dependencies first."

    text = ""
    try:
        reader = PdfReader(str(file_path))
        for page in reader.pages:
            extracted = page.extract_text() or ""
            text += extracted + "\n"
        return text
    except Exception as e:
        return f"PDF extraction error: {e}"


def normalize_text(raw_text):
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{2,}", "\n\n", text)
    return text.strip()


@app.route("/", methods=["GET"])
def index():
    return send_file(Path(__file__).resolve().parent.parent / "frontend" / "index.html")


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/process", methods=["POST"])
def process_document():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    uploaded_file = request.files["file"]
    if uploaded_file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(uploaded_file.filename):
        return jsonify({"error": "Unsupported file type"}), 400

    filename = secure_filename(uploaded_file.filename)
    save_path = UPLOAD_FOLDER / filename
    uploaded_file.save(save_path)

    ext = filename.rsplit(".", 1)[1].lower()

    if ext == "pdf":
        raw_text = extract_text_from_pdf(save_path)
    elif ext in {"txt", "md", "rtf"}:
        raw_text = extract_text_from_text_file(save_path)
    else:
        raw_text = extract_text_from_text_file(save_path)

    clean_text = normalize_text(raw_text)

    output_name = f"{Path(filename).stem}.clean.txt"
    output_path = UPLOAD_FOLDER / output_name
    output_path.write_text(clean_text, encoding="utf-8")

    return jsonify({
        "filename": filename,
        "output": output_name,
        "text_preview": clean_text[:1500],
        "word_count": len(clean_text.split()),
        "status": "success"
    })


@app.route("/downloads/<path:filename>", methods=["GET"])
def download_file(filename):
    file_path = UPLOAD_FOLDER / filename
    if not file_path.exists():
        return jsonify({"error": "File not found"}), 404
    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
