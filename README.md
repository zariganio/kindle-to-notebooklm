# Kindle to Notebook LM

This project is a minimal prototype that lets a user upload a Kindle-derived document, extract text, and prepare a Notebook LM-friendly source file.

## Goals
- Web UI for uploading a PDF/TXT/EPUB-like source file
- Extract readable text from common document formats
- Prepare a clean text output for Notebook LM

## Notes
- This is a prototype and does not automate Kindle DRM bypass.
- For a real app, you would add: file storage, job queue, OCR, document metadata, and Notebook LM API integration once available.

## How to run

### 1. Create a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r backend/requirements.txt
```

### 3. Run the app
```bash
python backend/app.py
```

Then open:
- http://localhost:5000

## Files
- `backend/app.py` - Flask API + upload handling
- `frontend/index.html` - Simple web page UI
- `frontend/style.css` - Basic styling
