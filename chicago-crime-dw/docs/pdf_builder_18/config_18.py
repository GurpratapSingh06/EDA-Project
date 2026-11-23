"""
Configuration, Canvas, Styles, and Flowables for the 18-Page Technical Guide PDF.
Strictly calibrated for an 18-page budget with professional academic typography.
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

# Page geometry - calibrated for compact high density
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN_LEFT = 36
MARGIN_RIGHT = 36
MARGIN_TOP = 36
MARGIN_BOTTOM = 36
USABLE_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT  # 523.27 pt
USABLE_HEIGHT = PAGE_HEIGHT - MARGIN_TOP - MARGIN_BOTTOM # 769.89 pt

# Academic Color Palette
PRIMARY = colors.HexColor('#0F2942')       # Oxford Navy
SECONDARY = colors.HexColor('#2B5C8F')     # Steel Blue
ACCENT = colors.HexColor('#C05621')        # Deep Amber / Rust
DARK_TEXT = colors.HexColor('#2D3748')     # Charcoal body text
LIGHT_BG = colors.HexColor('#F8FAFC')      # Card / Table background
ALT_ROW_BG = colors.HexColor('#F1F5F9')    # Alternating table row
BORDER_COLOR = colors.HexColor('#CBD5E0')  # Subtle dividing border
MUTED_TEXT = colors.HexColor('#718096')    # Captions & running headers
SUCCESS_COLOR = colors.HexColor('#276749') # Forest Green
CODE_BG = colors.HexColor('#F8FAFC')       # Code block background

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically render exact total page count,
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
            
            # Running Header
            self.setStrokeColor(BORDER_COLOR)
            self.setLineWidth(0.6)
            self.line(MARGIN_LEFT, PAGE_HEIGHT - 28, PAGE_WIDTH - MARGIN_RIGHT, PAGE_HEIGHT - 28)
            
            self.setFont('Helvetica-Bold', 7.0)
            self.setFillColor(PRIMARY)
            self.drawString(MARGIN_LEFT, PAGE_HEIGHT - 22, "CHICAGO CRIME ANALYTICS DATA WAREHOUSE")
            
            self.setFont('Helvetica', 7.0)
            self.setFillColor(MUTED_TEXT)
            self.drawRightString(PAGE_WIDTH - MARGIN_RIGHT, PAGE_HEIGHT - 22, "Technical Reference & Viva Examination Guide")
            
            # Running Footer
            self.setStrokeColor(BORDER_COLOR)
            self.setLineWidth(0.6)
            self.line(MARGIN_LEFT, 26, PAGE_WIDTH - MARGIN_RIGHT, 26)
            
            self.setFont('Helvetica', 7.0)
            self.setFillColor(MUTED_TEXT)
            self.drawString(MARGIN_LEFT, 17, "Batch Data Warehousing, Dimensional Modeling, OLAP & Predictive Mining")
            
            self.setFont('Helvetica-Bold', 7.0)
            self.setFillColor(PRIMARY)
            self.drawRightString(PAGE_WIDTH - MARGIN_RIGHT, 17, f"Page {self._pageNumber} of {page_count}")
            
            self.restoreState()

class PageTracker(Flowable):
    """Captures page number for dynamic Table of Contents."""
    def __init__(self, key, tracker_dict):
        super().__init__()
        self.key = key
        self.tracker_dict = tracker_dict
        self.width = 0
        self.height = 0

    def draw(self):
        self.tracker_dict[self.key] = self.canv._pageNumber

def get_doc_styles():
    """Returns balanced paragraph styles optimized for publication elegance and readability."""
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle('DocTitle', fontName='Helvetica-Bold', fontSize=20, leading=24, textColor=PRIMARY))
    styles.add(ParagraphStyle('DocSubtitle', fontName='Helvetica', fontSize=10.5, leading=14.5, textColor=SECONDARY))
    
    styles.add(ParagraphStyle('SectionH1', fontName='Helvetica-Bold', fontSize=12.5, leading=15.5, textColor=PRIMARY, spaceBefore=6, spaceAfter=4, keepWithNext=True))
    styles.add(ParagraphStyle('SectionH2', fontName='Helvetica-Bold', fontSize=10.0, leading=12.8, textColor=SECONDARY, spaceBefore=5, spaceAfter=3, keepWithNext=True))
    styles.add(ParagraphStyle('SectionH3', fontName='Helvetica-Bold', fontSize=8.6, leading=11.0, textColor=DARK_TEXT, spaceBefore=3.5, spaceAfter=2, keepWithNext=True))
    
    styles.add(ParagraphStyle('Body', fontName='Helvetica', fontSize=8.0, leading=10.8, textColor=DARK_TEXT, spaceBefore=1.5, spaceAfter=2.5))
    styles.add(ParagraphStyle('BodyBold', fontName='Helvetica-Bold', fontSize=8.0, leading=10.8, textColor=DARK_TEXT, spaceBefore=1.5, spaceAfter=2.5))
    styles.add(ParagraphStyle('BulletText', fontName='Helvetica', fontSize=8.0, leading=10.8, textColor=DARK_TEXT, spaceBefore=1.5, spaceAfter=1.5, leftIndent=10))
    
    styles.add(ParagraphStyle('CodeBlock', fontName='Courier', fontSize=6.8, leading=8.8, textColor=colors.HexColor('#1A202C')))
    styles.add(ParagraphStyle('TCell', fontName='Helvetica', fontSize=7.4, leading=9.4, textColor=DARK_TEXT))
    styles.add(ParagraphStyle('TCellBold', fontName='Helvetica-Bold', fontSize=7.4, leading=9.4, textColor=DARK_TEXT))
    styles.add(ParagraphStyle('TCellHeader', fontName='Helvetica-Bold', fontSize=7.4, leading=9.4, textColor=colors.white))
    styles.add(ParagraphStyle('TCellCode', fontName='Courier', fontSize=6.6, leading=8.2, textColor=colors.HexColor('#1A202C')))
    
    styles.add(ParagraphStyle('MapCell', fontName='Helvetica', fontSize=6.5, leading=7.9, textColor=DARK_TEXT))
    styles.add(ParagraphStyle('MapCellHeader', fontName='Helvetica-Bold', fontSize=6.8, leading=8.2, textColor=colors.white))
    
    styles.add(ParagraphStyle('FigCaption', fontName='Helvetica-Oblique', fontSize=7.0, leading=8.8, textColor=MUTED_TEXT, alignment=1, spaceBefore=2, spaceAfter=3))
    styles.add(ParagraphStyle('CalloutTitle', fontName='Helvetica-Bold', fontSize=8.6, leading=11.0, textColor=PRIMARY))
    styles.add(ParagraphStyle('CalloutBody', fontName='Helvetica', fontSize=7.6, leading=10.0, textColor=DARK_TEXT))
    
    return styles

def make_table(data_matrix, col_widths, headers=True, styles=None, padding=3.6, cell_style=None, header_style=None):
    """Constructs a clean compact table with generous legibility padding."""
    table_data = []
    for r_idx, row in enumerate(data_matrix):
        formatted_row = []
        for c_idx, cell in enumerate(row):
            if isinstance(cell, str):
                if r_idx == 0 and headers:
                    h_style = header_style or (styles['TCellHeader'] if styles else ParagraphStyle('H', fontSize=7.4, leading=9.4, textColor=colors.white))
                    p = Paragraph(f"<b>{cell}</b>", h_style)
                else:
                    b_style = cell_style or (styles['TCell'] if styles else ParagraphStyle('B', fontSize=7.4, leading=9.4))
                    p = Paragraph(cell, b_style)
                formatted_row.append(p)
            else:
                formatted_row.append(cell)
        table_data.append(formatted_row)
        
    t = Table(table_data, colWidths=col_widths)
    t_style = [
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), padding),
        ('BOTTOMPADDING', (0, 0), (-1, -1), padding),
        ('LEFTPADDING', (0, 0), (-1, -1), 4.5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4.5),
        ('BOX', (0, 0), (-1, -1), 0.6, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, BORDER_COLOR),
    ]
    if headers:
        for r in range(1, len(data_matrix)):
            if r % 2 == 0:
                t_style.append(('BACKGROUND', (0, r), (-1, r), ALT_ROW_BG))
            else:
                t_style.append(('BACKGROUND', (0, r), (-1, r), LIGHT_BG))
    t.setStyle(TableStyle(t_style))
    return t

def make_callout(title, text, styles, accent_color=SECONDARY, padding_v=5.0):
    """Creates an elegant rounded callout box with balanced padding."""
    content = [
        Paragraph(f"<b>{title}</b>", styles['CalloutTitle']),
        Spacer(1, 2),
        Paragraph(text, styles['CalloutBody'])
    ]
    tbl = Table([[content]], colWidths=[USABLE_WIDTH])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 0.6, BORDER_COLOR),
        ('LINEBEFORE', (0, 0), (0, -1), 3.0, accent_color),
        ('TOPPADDING', (0, 0), (-1, -1), padding_v),
        ('BOTTOMPADDING', (0, 0), (-1, -1), padding_v),
        ('LEFTPADDING', (0, 0), (-1, -1), 8.0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8.0),
    ]))
    return tbl

def make_image_figure(img_path, caption, width=None, height=None, styles=None):
    """Generates an embedded image with caption."""
    elements = []
    if os.path.exists(img_path):
        from reportlab.platypus import Image as RLImage
        from PIL import Image as PILImage
        try:
            with PILImage.open(img_path) as pimg:
                orig_w, orig_h = pimg.size
            if width and not height:
                h = width * (orig_h / orig_w)
                w = width
            elif height and not width:
                w = height * (orig_w / orig_h)
                h = height
            elif width and height:
                w, h = width, height
            else:
                w, h = USABLE_WIDTH, USABLE_WIDTH * (orig_h / orig_w)
            
            img = RLImage(img_path, width=w, height=h)
            img.hAlign = 'CENTER'
            elements.append(img)
            if caption and styles:
                elements.append(Paragraph(caption, styles['FigCaption']))
        except Exception as e:
            elements.append(Paragraph(f"<i>[Image unavailable: {caption}]</i>", styles['Body']))
    else:
        if styles:
            elements.append(Paragraph(f"<i>[Missing asset: {os.path.basename(img_path)}]</i>", styles['Body']))
    return elements
