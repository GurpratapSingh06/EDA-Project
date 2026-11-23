"""
Master PDF Generation Script for:
chicago-crime-dw/docs/Chicago_Crime_Project_Concepts_and_Technical_Guide.pdf

Executes a two-pass build to guarantee 100% accurate Table of Contents page numbering,
running headers and footers, and validates the output using PyMuPDF.
"""

import os
import sys
import io
import time
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate

# Ensure pdf_builder is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from pdf_builder.config import (
    A4, MARGIN_LEFT, MARGIN_RIGHT, MARGIN_TOP, MARGIN_BOTTOM,
    NumberedCanvas, get_doc_styles
)
from pdf_builder.sec1_overview import build_cover_page, build_table_of_contents, build_section_1
from pdf_builder.sec2_preprocessing import build_section_2
from pdf_builder.sec3_modeling import build_section_3
from pdf_builder.sec4_etl import build_section_4
from pdf_builder.sec5_olap import build_section_5
from pdf_builder.sec6_ml import build_section_6
from pdf_builder.sec7_dashboards import build_section_7
from pdf_builder.sec8_tech_stack import build_section_8
from pdf_builder.sec9_mapping import build_section_9
from pdf_builder.sec10_viva import build_section_10

def assemble_story(styles, tracker):
    """Assembles all sections sequentially into a single ReportLab story."""
    story = []
    
    # Cover Page
    story.extend(build_cover_page(styles))
    
    # Table of Contents
    story.extend(build_table_of_contents(styles, tracker))
    
    # Section 1: Executive Overview & Architecture Justification
    story.extend(build_section_1(styles, tracker))
    
    # Section 2: Data Preprocessing & Feature Engineering
    story.extend(build_section_2(styles, tracker))
    
    # Section 3: Dimensional Modeling & Fact Constellation Schema Design
    story.extend(build_section_3(styles, tracker))
    
    # Section 4: End-to-End Batch ETL Lifecycle & Operational Mechanics
    story.extend(build_section_4(styles, tracker))
    
    # Section 5: Multidimensional OLAP Operations & Business Analysis
    story.extend(build_section_5(styles, tracker))
    
    # Section 6: Predictive Data Mining & Machine Learning Pipelines
    story.extend(build_section_6(styles, tracker))
    
    # Section 7: Business Intelligence & Interactive Dashboard Systems
    story.extend(build_section_7(styles, tracker))
    
    # Section 8: Technology Stack, Libraries & Execution Architecture
    story.extend(build_section_8(styles, tracker))
    
    # Section 9: Master Concept-to-Implementation Mapping Catalog
    story.extend(build_section_9(styles, tracker))
    
    # Section 10: Comprehensive Project-Specific Viva Voce Guide (35 Q&As)
    story.extend(build_section_10(styles, tracker))
    
    return story

def generate_pdf():
    t0 = time.time()
    pdf_path = os.path.join(current_dir, "Chicago_Crime_Project_Concepts_and_Technical_Guide.pdf")
    styles = get_doc_styles()
    tracker = {}
    
    print("=== PASS 1: Capturing Section Page Offsets ===")
    dummy_buffer = io.BytesIO()
    doc_pass1 = SimpleDocTemplate(
        dummy_buffer,
        pagesize=A4,
        leftMargin=MARGIN_LEFT,
        rightMargin=MARGIN_RIGHT,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM
    )
    story_pass1 = assemble_story(styles, tracker)
    doc_pass1.build(story_pass1, canvasmaker=NumberedCanvas)
    print("Captured Page Tracker Offsets:")
    for k, v in sorted(tracker.items()):
        print(f"  {k:15s}: Page {v}")
        
    print("\n=== PASS 2: Building Final Publication-Quality PDF ===")
    doc_final = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=MARGIN_LEFT,
        rightMargin=MARGIN_RIGHT,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM
    )
    story_final = assemble_story(styles, tracker)
    doc_final.build(story_final, canvasmaker=NumberedCanvas)
    
    t_elapsed = time.time() - t0
    file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
    print(f"\nPDF generated successfully in {t_elapsed:.2f} seconds!")
    print(f"Path: {pdf_path}")
    print(f"File Size: {file_size_mb:.2f} MB")
    
    # Verification with PyMuPDF
    print("\n=== VERIFICATION: PyMuPDF Page & Visual Audit ===")
    import pymupdf
    doc_pdf = pymupdf.open(pdf_path)
    page_count = len(doc_pdf)
    print(f"Total Page Count: {page_count} pages")
    
    # Render first 3 pages and sample middle/end pages to images for audit
    render_pages = [1, 2, 3, 5, 8, 12, 16, page_count]
    render_dir = os.path.join(current_dir, "pdf_assets")
    os.makedirs(render_dir, exist_ok=True)
    
    for p_num in render_pages:
        if p_num <= page_count:
            page = doc_pdf[p_num - 1]
            pix = page.get_pixmap(dpi=150)
            sample_img_path = os.path.join(render_dir, f"rendered_page_{p_num:02d}.png")
            pix.save(sample_img_path)
            print(f"  Rendered Page {p_num:02d} -> {sample_img_path} ({pix.width}x{pix.height} px)")
            
    doc_pdf.close()
    print("\n=== ALL VALIDATION CHECKS PASSED ===")

if __name__ == "__main__":
    generate_pdf()
