from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import io
from typing import List, Dict, Any

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development convenience
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "GPA Calculator API"}

@app.post("/calculate-gpa")
async def calculate_gpa(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")
    
    content = await file.read()
    
    try:
        text_content = ""
        # We need to pass bytes to pdfplumber
        # Since extract_text_from_pdf does that, we can just pass content
        
        from parser import extract_text_from_pdf, find_grading_scale, parse_courses, convert_to_5_scale
        
        text_content = extract_text_from_pdf(content)
        print("------- EXTRACTED TEXT START -------")
        print(text_content)
        print("------- EXTRACTED TEXT END -------")
        
        extracted_scale = find_grading_scale(text_content)
        
        # Determine strictness. If we didn't find a scale, default to standard 4.0 to try and parse courses anyway.
        # But we flag it.
        # Default to the user-requested 5-point scale if no scale is found
        parsing_scale = extracted_scale if extracted_scale else {
            "A+": 5.0, "A": 4.0, 
            "B+": 3.5, "B": 3.0, 
            "C+": 2.5, "C": 2.0, 
            "D+": 1.5, "D": 1.0, 
            "F": 0.0
        }
        
        courses, raw_gpa = parse_courses(text_content, parsing_scale)
        
        # Determine source max (heuristic: max value in the extracted scale)
        source_max = max(parsing_scale.values()) if parsing_scale else 4.0
        
        final_gpa_5_scale = convert_to_5_scale(raw_gpa, source_max)
        
        return {
            "filename": file.filename,
            "extracted_scale": extracted_scale,
            "scale_source_max_detected": source_max,
            "courses_found": len(courses),
            "courses": courses,
            "raw_gpa": raw_gpa,
            "final_gpa_5_scale": final_gpa_5_scale,
            "preview_text": text_content[:500] 
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
