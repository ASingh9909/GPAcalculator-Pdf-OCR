# PDF GPA Calculator with OCR

This is a web application that extracts student transcript data from PDF files (including scanned image-based PDFs using OCR) and calculates the GPA on a 5.0 scale.

## Features

- **PDF Upload**: Supports standard text-based PDFs and scanned image PDFs.
- **OCR Integration**: Uses Tesseract OCR to read text from image-based transcripts.
- **Auto-Extraction**: automatically detects:
  - Grading Scales (e.g., standard 4.0, range-based percentages).
  - Course names, credits, and grades.
- **GPA Calculation**:
  - Automatically identifies grading scales.
  - Converts grades to a 5.0 scale (A+ = 5.0, A = 4.0, B = 3.0, etc.).
  - Calculates weighted GPA based on credits.
- **Interactive UI**: Drag-and-drop file upload and detailed result breakdown.

## Tech Stack

- **Frontend**: Next.js 14+ (App Router), TypeScript, Tailwind CSS v4, Lucide React
- **Backend**: FastAPI, Python 3.11+
- **PDF Processing**: `pdfplumber` (text), `pytesseract` & `pdf2image` (OCR), `pypdfium2`

## Prerequisites

1. **Python 3.10+**
2. **Node.js 18+**
3. **Tesseract OCR** (Required for scanned PDFs)
   - macOS: `brew install tesseract`
   - Windows/Linux: Install Tesseract binary and ensure it's in your PATH.

## Installation

### 1. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Frontend Setup

```bash
cd frontend
npm install
```

## Running the App

### Start Backend

```bash
# From backend directory
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

### Start Frontend

```bash
# From frontend directory
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Grading Scale Logic

The system currently defaults to a 5.0 scale logic:
- A+ (or ranges mapping to it) -> 5.0
- A -> 4.0
- B -> 3.0
- C -> 2.0
- D -> 1.0
- F -> 0.0

Half-steps (e.g., B+) are supported where applicable.
