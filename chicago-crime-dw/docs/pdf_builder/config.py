"""
Configuration, Canvas, Styles, and Helper Flowables for the Technical Guide PDF.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    KeepTogether, PageBreak, Image, HRFlowable, Flowable
)
from reportlab.pdfgen import canvas

# Page geometry
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN_LEFT = 40
MARGIN_RIGHT = 40
MARGIN_TOP = 40
MARGIN_BOTTOM = 40
USABLE_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT  # 515.27 pt
USABLE_HEIGHT = PAGE_HEIGHT - MARGIN_TOP - MARGIN_BOTTOM

# Color Palette
PRIMARY = colors.HexColor('#0F2942')       # Deep Oxford Navy
SECONDARY = colors.HexColor('#2B5C8F')     # Academic Steel Blue
ACCENT = colors.HexColor('#C05621')        # Deep Rust / Amber
DARK_TEXT = colors.HexColor('#2D3748')     # Charcoal body text
LIGHT_BG = colors.HexColor('#F8FAFC')      # Card / Table background
ALT_ROW_BG = colors.HexColor('#EDF2F7')    # Alternating table row
BORDER_COLOR = colors.HexColor('#CBD5E0')  # Subtle dividing border
MUTED_TEXT = colors.HexColor('#718096')    # Captions & running headers
SUCCESS_COLOR = colors.HexColor('#276749') # Green highlight
CODE_BG = colors.HexColor('#F7FAFC')       # Code block background

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and render exact total page count,
    running headers, and running footers on all pages except the cover page.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        if self._pageNumber > 1:
            self.saveState()
            
            # Running Header (Top Rule & Text)
            self.setStrokeColor(BORDER_COLOR)
            self.setLineWidth(0.7)
            self.line(MARGIN_LEFT, PAGE_HEIGHT - 32, PAGE_WIDTH - MARGIN_RIGHT, PAGE_HEIGHT - 32)
            
            self.setFont('Helvetica-Bold', 7.5)
            self.setFillColor(PRIMARY)
            self.drawString(MARGIN_LEFT, PAGE_HEIGHT - 26, "CHICAGO CRIME ANALYTICS DATA WAREHOUSE")
            
            self.setFont('Helvetica', 7.5)
            self.setFillColor(MUTED_TEXT)
            self.drawRightString(PAGE_WIDTH - MARGIN_RIGHT, PAGE_HEIGHT - 26, "Technical Concepts & Implementation Guide")
            
            # Running Footer (Bottom Rule & Text)
            self.setStrokeColor(BORDER_COLOR)
            self.setLineWidth(0.7)
            self.line(MARGIN_LEFT, 32, PAGE_WIDTH - MARGIN_RIGHT, 32)
            
            self.setFont('Helvetica', 7.5)
            self.setFillColor(MUTED_TEXT)
            self.drawString(MARGIN_LEFT, 22, "Department of Computer Science & Engineering | Batch DW, OLAP & Predictive Mining")
            
            self.setFont('Helvetica-Bold', 7.5)
            self.setFillColor(PRIMARY)
            self.drawRightString(PAGE_WIDTH - MARGIN_RIGHT, 22, f"Page {self._pageNumber} of {page_count}")
            
            self.restoreState()

class PageTracker(Flowable):
    """
    Zero-dimension flowable that captures the canvas page number where it is placed.
    Used for generating accurate Table of Contents.
    """
    def __init__(self, key, tracker_dict):
        super().__init__()
        self.key = key
        self.tracker_dict = tracker_dict
        self.width = 0
        self.height = 0

    def draw(self):
        self.tracker_dict[self.key] = self.canv._pageNumber

def get_doc_styles():
    """Initializes and returns consistent paragraph styles."""
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle('DocTitle', fontName='Helvetica-Bold', fontSize=22, leading=26, textColor=PRIMARY, alignment=0))
    styles.add(ParagraphStyle('DocSubtitle', fontName='Helvetica', fontSize=11, leading=15, textColor=SECONDARY, alignment=0))
    
    styles.add(ParagraphStyle('SectionH1', fontName='Helvetica-Bold', fontSize=13, leading=17, textColor=PRIMARY, spaceBefore=14, spaceAfter=6, keepWithNext=True))
    styles.add(ParagraphStyle('SectionH2', fontName='Helvetica-Bold', fontSize=10.5, leading=14, textColor=SECONDARY, spaceBefore=10, spaceAfter=4, keepWithNext=True))
    styles.add(ParagraphStyle('SectionH3', fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=DARK_TEXT, spaceBefore=7, spaceAfter=3, keepWithNext=True))
    
    styles.add(ParagraphStyle('Body', fontName='Helvetica', fontSize=8.2, leading=11.5, textColor=DARK_TEXT, spaceBefore=2, spaceAfter=4))
    styles.add(ParagraphStyle('BodyBold', fontName='Helvetica-Bold', fontSize=8.2, leading=11.5, textColor=DARK_TEXT, spaceBefore=2, spaceAfter=4))
    styles.add(ParagraphStyle('BulletText', fontName='Helvetica', fontSize=8.2, leading=11.5, textColor=DARK_TEXT, spaceBefore=1, spaceAfter=2, leftIndent=12))
    
    styles.add(ParagraphStyle('CodeBlock', fontName='Courier', fontSize=7.0, leading=9.2, textColor=colors.HexColor('#1A202C')))
    styles.add(ParagraphStyle('TCell', fontName='Helvetica', fontSize=7.2, leading=9.5, textColor=DARK_TEXT))
    styles.add(ParagraphStyle('TCellBold', fontName='Helvetica-Bold', fontSize=7.2, leading=9.5, textColor=DARK_TEXT))
    styles.add(ParagraphStyle('THeader', fontName='Helvetica-Bold', fontSize=7.5, leading=10, textColor=colors.white))
    
    styles.add(ParagraphStyle('FigCaption', fontName='Helvetica-Oblique', fontSize=7.5, leading=10, textColor=MUTED_TEXT, alignment=1, spaceBefore=4, spaceAfter=8))
    styles.add(ParagraphStyle('CalloutHead', fontName='Helvetica-Bold', fontSize=8.5, leading=11.5, textColor=PRIMARY))
    styles.add(ParagraphStyle('CalloutBody', fontName='Helvetica', fontSize=8.0, leading=11.0, textColor=DARK_TEXT))
    
    styles.add(ParagraphStyle('ConceptTitle', fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=PRIMARY, spaceBefore=8, spaceAfter=4, keepWithNext=True))
    styles.add(ParagraphStyle('ConceptField', fontName='Helvetica-Bold', fontSize=8.2, leading=11.5, textColor=SECONDARY))
    styles.add(ParagraphStyle('ConceptText', fontName='Helvetica', fontSize=8.2, leading=11.5, textColor=DARK_TEXT))
    
    return styles

def make_callout(text, title=None, color=SECONDARY, styles=None):
    """Generates an academic callout box with a colored left accent border."""
    st = styles or get_doc_styles()
    content = []
    if title:
        content.append(Paragraph(f"<b>{title}</b>", st['CalloutHead']))
        content.append(Spacer(1, 3))
    content.append(Paragraph(text, st['CalloutBody']))
    
    tbl = Table([[content]], colWidths=[USABLE_WIDTH])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('LINEBEFORE', (0,0), (0,-1), 3.0, color),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 9),
        ('RIGHTPADDING', (0,0), (-1,-1), 9),
    ]))
    return tbl

def make_table(data_rows, col_widths, headers=True, styles=None):
    """Wraps row elements in Paragraphs and styles a clean data table."""
    st = styles or get_doc_styles()
    formatted = []
    for r_idx, row in enumerate(data_rows):
        formatted_row = []
        is_hdr = (r_idx == 0 and headers)
        for val in row:
            if isinstance(val, Flowable):
                formatted_row.append(val)
            else:
                p_style = st['THeader'] if is_hdr else st['TCell']
                formatted_row.append(Paragraph(str(val), p_style))
        formatted.append(formatted_row)
        
    t = Table(formatted, colWidths=col_widths)
    t_style = [
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]
    if headers:
        t_style.append(('BACKGROUND', (0,0), (-1,0), PRIMARY))
        # Alternating row colors
        for i in range(1, len(data_rows)):
            bg = ALT_ROW_BG if i % 2 == 1 else colors.white
            t_style.append(('BACKGROUND', (0, i), (-1, i), bg))
    else:
        for i in range(len(data_rows)):
            bg = ALT_ROW_BG if i % 2 == 1 else colors.white
            t_style.append(('BACKGROUND', (0, i), (-1, i), bg))
            
    t.setStyle(TableStyle(t_style))
    return t

def make_code_box(code_text, language='sql', styles=None):
    """Creates a formatted syntax box for code listings."""
    st = styles or get_doc_styles()
    # Replace whitespace/newlines into break lines
    lines = code_text.strip().split('\n')
    formatted = "<br/>".join([l.replace(" ", "&nbsp;").replace("<", "&lt;").replace(">", "&gt;") for l in lines])
    p = Paragraph(formatted, st['CodeBlock'])
    
    t = Table([[p]], colWidths=[USABLE_WIDTH])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CODE_BG),
        ('BOX', (0,0), (-1,-1), 0.6, colors.HexColor('#CBD5E0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('RIGHTPADDING', (0,0), (-1,-1), 7),
    ]))
    return t

def make_image_figure(img_path, caption, width=480, height=None, styles=None):
    """Renders a centered image with caption."""
    st = styles or get_doc_styles()
    flowables = []
    if os.path.exists(img_path):
        from PIL import Image as PILImage
        with PILImage.open(img_path) as im:
            orig_w, orig_h = im.size
        actual_h = height if height else (orig_h * (width / orig_w))
        img = Image(img_path, width=width, height=actual_h)
        flowables.append(img)
        flowables.append(Spacer(1, 2))
        flowables.append(Paragraph(caption, st['FigCaption']))
    else:
        flowables.append(Paragraph(f"[Image Not Found: {img_path}]", st['FigCaption']))
    return flowables

def make_concept_card(num, name, definition, why_needed, how_it_works, step_by_step,
                      math_formula=None, worked_example=None, project_usage=None,
                      exact_reference=None, pros_cons=None, styles=None):
    """
    Renders a concept block following the strict 10-point pedagogical structure.
    """
    st = styles or get_doc_styles()
    elements = []
    
    # Header line
    hdr_text = f"<b>Concept {num}: {name}</b>"
    elements.append(Paragraph(hdr_text, st['ConceptTitle']))
    
    # 10 Structure fields
    fields = [
        ("1. Simple Definition", definition),
        ("2. Why It Is Needed", why_needed),
        ("3. How It Works", how_it_works),
        ("4. Step-by-Step Execution", step_by_step),
    ]
    if math_formula:
        fields.append(("5. Mathematical Formulation", math_formula))
    if worked_example:
        fields.append(("6. Concrete Worked Example", worked_example))
    if project_usage:
        fields.append(("7. Project Implementation", project_usage))
    if exact_reference:
        fields.append(("8. Source File Reference", exact_reference))
    if pros_cons:
        fields.append(("9. Advantages & Limitations", pros_cons))
        
    for f_label, f_val in fields:
        elements.append(Paragraph(f"<b><font color='{SECONDARY.hexval()}'>{f_label}:</font></b> {f_val}", st['Body']))
        elements.append(Spacer(1, 1.5))
        
    elements.append(Spacer(1, 4))
    elements.append(HRFlowable(width="100%", thickness=0.4, color=BORDER_COLOR, spaceBefore=2, spaceAfter=4))
    return elements
