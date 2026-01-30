import re
import pdfplumber
from typing import List, Dict, Tuple, Optional

import pytesseract
import pypdfium2 as pdfium
import io

def extract_text_from_pdf(pdf_bytes):
    # 1. Try standard text extraction first
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        text_content = ""
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text_content += extracted + "\n"
    
    # 2. Check if we need OCR (e.g. empty text or known scanner watermarks)
    # Filter out common watermarks to see if there's real text
    clean_text = text_content.replace("CamScanner", "").replace("Scanned with", "").strip()
    
    if len(clean_text) < 50:
        print("Insufficient text layer detected. Switching to OCR...")
        text_content = ""  # Reset to avoid mixing garbage
        
        # Load with pypdfium2 for rendering
        pdf = pdfium.PdfDocument(pdf_bytes)
        
        for i in range(len(pdf)):
            page = pdf[i]
            # Render the page to a PIL image
            # Scale=2 provides better resolution for OCR
            bitmap = page.render(scale=3) 
            pil_image = bitmap.to_pil()
            
            # Run Tesseract with PSM 6 (Assume a single uniform block of text) helps with tables
            # Adding whitelist to force typical grade/credit chars: Letters, Digits, +, -, ., space, parens, ~
            custom_config = r'--psm 6 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-.~/() "'
            page_text = pytesseract.image_to_string(pil_image, config=custom_config)
            text_content += page_text + "\n"
            
        print("OCR Complete.")
            
    return text_content

def find_grading_scale(text: str) -> Dict[str, float]:
    """
    Attempts to find a grading scale in the text.
    Handles:
    1. Points: "A 4.0", "A- 3.7"
    2. Ranges: "A(100~80)", "B(79~70)" -> Maps to default 4.0 scale if detected.
    """
    scale = {}
    
    # Check for "GRADING SYSTEM" or similar headers if strict extraction is needed
    # But we scan generally.
    
    # Pattern 1: Explicit Points (A = 4.0)
    # Captures: Grade, Separator, Points
    point_pattern = re.compile(r"([A-F][+-]?)\s*(=|:|-)?\s*(\d\.\d{1,2})")
    
    # Pattern 2: Percentage Ranges (A(100~90))
    # Captures: Grade, Range Start, Range End
    # We map these to standard 4.3 or 4.0 scale points roughly? 
    # Or just return a standard scale if this system is detected.
    # The user's screenshot: "A(100~80)"
    # Update: Allow various separators (tilde, dash, en-dash, etc)
    range_pattern = re.compile(r"([A-F][+-]?)\s*\(\s*\d+\s*[~:,-]\s*\d+\s*\)")
    
    point_matches = point_pattern.findall(text)
    range_matches = range_pattern.findall(text)
    
    # Priority to explicit points
    for match in point_matches:
        grade = match[0]
        try:
            points = float(match[2])
            if grade not in scale:
                scale[grade] = points
        except ValueError:
            pass
            
    # If no point scale found, check for range scale
    if not scale and range_matches:
        # Detected a percentage based system like: A(100~90)
        # We can't extract "points" directly from "A(100~90)" without a mapping table.
        # But detection implies we should use a standard fallback for that system.
        # Let's define a standard mapping for this detected system.
        # Usually: A+=4.3/4.5, A=4.0, B+=3.5, B=3.0 etc.
        # IF the text mentions "A+" we assume 4.3 or 4.5 system?
        # Let's map to standard 4.0
        # Map to the requested 5.0 scale
        standard_5_0 = {
            "A+": 5.0, "A": 4.0, 
            "B+": 3.5, "B": 3.0, 
            "C+": 2.5, "C": 2.0, 
            "D+": 1.5, "D": 1.0, 
            "F": 0.0
        }
        return standard_5_0

    if not scale:
        return {} 
        
    return scale

def parse_courses(text: str, grading_scale: Dict[str, float]) -> Tuple[List[Dict], float]:
    """
    Parses courses and calculates GPA based on the provided (or default) grading scale.
    Returns: (List of Course Dicts, GPA)
    """
    courses = []
    
    # Regex to find course rows. 
    # This is TRICKY without specific structure. 
    # We'll look for lines containing: Code (Optional), Title (Optional), Credit (Number), Grade (Letter)
    
    # Heuristic: split by lines.
    lines = text.split('\n')
    
    total_points = 0.0
    total_credits = 0.0
    
    # Standard Grade Regex
    grade_pattern = re.compile(r"\b([A-F][+-]?)\b")
    # Credit Regex (usually 1.0 to 9.0, or 1 to 9)
    credit_pattern = re.compile(r"\b(\d{1,2}(\.\d+)?)\b")

    for line in lines:
        # Filter out lines that look like the Grading Scale table itself
        if "Grading Scale" in line or "Legend" in line or "GRADING SYSTEM" in line:
            # Also catch the weird "Grades prior to..." lines from the screenshot
            continue
        if "Grades prior to" in line or "Grades effective" in line:
            continue
            
        # Normalize line for OCR typos
        # At -> A+, Bt -> B+ (Common Tesseract typos)
        # 8B -> B (Common confusion)
        line_clean = line.replace("At", "A+").replace("Bt", "B+").replace("Ct", "C+").replace("Dt", "D+")
        line_clean = line_clean.replace("8B", "B").replace("8A", "A") 
        # remove pipes often found in tables
        line_clean = line_clean.replace("|", "")
        
        # Find potential grade
        # We search from the end of the line because Grade/Credit are often at the end
        
        # Find potential grade
        # We search from the end of the line because Grade/Credit are often at the end
        
        # Relaxed pattern for end-of-line grades (handling potential attached junk)
        # Matches Grade at the end, optionally followed by non-alphanumeric junk
        # regex: [A-F][+-]? followed by optional spaces/junk at end of string
        end_grade_pattern = re.compile(r"([A-F][+-]?)\s*[^0-9A-Za-z]*$")
        
        # We need to find ALL grades and credits in the line to handle 2-column layouts
        # e.g. "Course A   2.0 A      Course B   3.0 B"
        
        grades_found = grade_pattern.findall(line_clean)
        credits_found = credit_pattern.findall(line_clean)
        
        # Filter credits
        valid_credits = []
        for c_match in credits_found:
             try:
                 val = float(c_match[0])
                 if 0 < val < 20: # Sanity check for credit value
                     valid_credits.append(val)
             except ValueError:
                 continue

        # If we have matches
        if grades_found and valid_credits:
            # Heuristic: If we have equal number of grades and credits, pair them up
            # If not, we might fall back to the "last one" strategy or try to alignments
            
            # Case 1: Equal count (Ideal 2-column scenario)
            if len(grades_found) == len(valid_credits):
                for i in range(len(grades_found)):
                    g = grades_found[i]
                    c = valid_credits[i]
                    if g in grading_scale:
                        pts = grading_scale[g]
                        courses.append({
                            "raw_line": line.strip() + f" [part {i+1}]",
                            "grade": g,
                            "credit": c,
                            "points": pts
                        })
                        total_points += pts * c
                        total_credits += c
            
            # Case 2: Mismatch, likely just one course at the end or noise
            # Fallback to previous behavior: catch the last valid pair
            else:
                 # Try to take the last ones
                 g = grades_found[-1]
                 c = valid_credits[-1]
                 
                 if g in grading_scale:
                    pts = grading_scale[g]
                    courses.append({
                        "raw_line": line.strip(),
                        "grade": g,
                        "credit": c,
                        "points": pts
                    })
                    total_points += pts * c
                    total_credits += c
                
    gpa = 0.0
    if total_credits > 0:
        gpa = total_points / total_credits
        
    return courses, gpa

def convert_to_5_scale(gpa: float, source_max: float = 4.0) -> float:
    """
    Converts a GPA from a source scale (default 4.0) to a 5.0 scale.
    Formula: (GPA / SourceMax) * 5.0
    """
    if source_max <= 0: return 0.0
    return (gpa / source_max) * 5.0
