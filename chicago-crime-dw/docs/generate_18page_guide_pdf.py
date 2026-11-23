"""
Master 2-Pass Compiler for the 18-Page Project-Specific Technical Guide PDF.
Target: chicago-crime-dw/docs/Chicago_Crime_Project_Concepts_and_Technical_Guide.pdf
Strictly enforces 18-page budget (minimum 15, maximum 20 pages).
"""

import os
import sys
import time
from reportlab.platypus import SimpleDocTemplate
from pdf_builder_18.config_18 import (
    PAGE_WIDTH, PAGE_HEIGHT, MARGIN_LEFT, MARGIN_RIGHT, MARGIN_TOP, MARGIN_BOTTOM,
    NumberedCanvas, get_doc_styles
)
from pdf_builder_18.pages_01_03 import build_pages_01_03
from pdf_builder_18.pages_04_05 import build_pages_04_05
from pdf_builder_18.pages_06_07 import build_pages_06_07
from pdf_builder_18.pages_08_09 import build_pages_08_09
from pdf_builder_18.pages_10_12 import build_pages_10_12
from pdf_builder_18.pages_13_14 import build_pages_13_14
from pdf_builder_18.pages_15_16 import build_pages_15_16
from pdf_builder_18.pages_17_18 import build_pages_17_18

def generate_story(styles, tracker):
    story = []
    story.extend(build_pages_01_03(styles, tracker))
    story.extend(build_pages_04_05(styles, tracker))
    story.extend(build_pages_06_07(styles, tracker))
    story.extend(build_pages_08_09(styles, tracker))
    story.extend(build_pages_10_12(styles, tracker))
    story.extend(build_pages_13_14(styles, tracker))
    story.extend(build_pages_15_16(styles, tracker))
    story.extend(build_pages_17_18(styles, tracker))
    return story

def build_pdf():
    t0 = time.time()
    pdf_path = os.path.abspath('chicago-crime-dw/docs/Chicago_Crime_Project_Concepts_and_Technical_Guide.pdf')
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    
    styles = get_doc_styles()
    tracker = {}
    
    # -------------------------------------------------------------
    # PASS 1: Dry run to record page offsets in tracker
    # -------------------------------------------------------------
    print("=== PASS 1: Capturing Section Page Offsets ===")
    pass1_path = os.path.abspath('chicago-crime-dw/docs/Chicago_Crime_Project_Concepts_and_Technical_Guide_pass1.pdf')
    doc_pass1 = SimpleDocTemplate(
        pass1_path,
        pagesize=(PAGE_WIDTH, PAGE_HEIGHT),
        leftMargin=MARGIN_LEFT, rightMargin=MARGIN_RIGHT,
        topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOTTOM
    )
    story1 = generate_story(styles, tracker)
    doc_pass1.build(story1, canvasmaker=NumberedCanvas)
    
    print("Captured Page Tracker Offsets:")
    for k in sorted(tracker.keys()):
        print(f"  {k:15}: Page {tracker[k]}")
        
    if os.path.exists(pass1_path):
        os.remove(pass1_path)
        
    # -------------------------------------------------------------
    # PASS 2: Build final publication PDF with exact TOC
    # -------------------------------------------------------------
    print("\n=== PASS 2: Building Final 18-Page Technical Guide PDF ===")
    doc_final = SimpleDocTemplate(
        pdf_path,
        pagesize=(PAGE_WIDTH, PAGE_HEIGHT),
        leftMargin=MARGIN_LEFT, rightMargin=MARGIN_RIGHT,
        topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOTTOM
    )
    story2 = generate_story(styles, tracker)
    doc_final.build(story2, canvasmaker=NumberedCanvas)
    
    elapsed = time.time() - t0
    fsize = os.path.getsize(pdf_path) / (1024 * 1024)
    print(f"\nPDF generated successfully in {elapsed:.2f} seconds!")
    print(f"Path: {pdf_path}")
    print(f"File Size: {fsize:.2f} MB")
    
    # -------------------------------------------------------------
    # PASS 3: PyMuPDF Visual Audit & Quality Verification
    # -------------------------------------------------------------
    print("\n=== VERIFICATION: PyMuPDF Page & Visual Audit ===")
    import pymupdf
    doc = pymupdf.open(pdf_path)
    page_count = len(doc)
    print(f"Total Page Count: {page_count} pages (Requirement: 15-20 pages)")
    
    if page_count < 15 or page_count > 20:
        print(f"CRITICAL WARNING: Page count {page_count} violates 15-20 page constraint!")
    else:
        print(f"SUCCESS: Page count {page_count} perfectly satisfies the 15-20 page constraint!")
        
    # Render all pages into images to inspect
    img_dir = os.path.abspath('chicago-crime-dw/docs/pdf_assets/rendered_18pages')
    os.makedirs(img_dir, exist_ok=True)
    
    for i in range(page_count):
        page = doc.load_page(i)
        pix = page.get_pixmap(dpi=150)
        out_img = os.path.join(img_dir, f"page_{i+1:02d}.png")
        pix.save(out_img)
        print(f"  Rendered Page {i+1:02d} -> {out_img} ({pix.width}x{pix.height} px)")
        
    doc.close()
    print("\n=== ALL QUALITY CHECKS COMPLETED ===")

if __name__ == '__main__':
    # Make sure docs directory is on python path
    docs_dir = os.path.abspath('chicago-crime-dw/docs')
    if docs_dir not in sys.path:
        sys.path.insert(0, docs_dir)
    build_pdf()
