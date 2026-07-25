import os
import logging

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from app.core.arabic_pdf import prepare_cell_value, is_arabic_text
from app.core.paths import resource_path

logger = logging.getLogger(__name__)


FONT_DIR = resource_path("app/static/fonts")


def _register_arabic_fonts():
    """Register Arabic fonts for PDF rendering, prioritizing compatibility."""
    import os
    fonts_registered = False

    try:
        static_fonts_dir = resource_path("app/static/fonts")
        cairo_regular = os.path.join(static_fonts_dir, "Cairo-Regular.ttf")
        cairo_bold = os.path.join(static_fonts_dir, "Cairo-Bold.ttf")

        # 1. Use system Arial/DejaVu as they are extremely reliable for Arabic PDF glyphs
        font_paths = [
            "/usr/share/fonts/msttcore/arial.ttf",
            "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        ]

        bold_paths = [
            "/usr/share/fonts/msttcore/arialbd.ttf",
            "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf",
        ]

        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    # Register the reliable font as "Cairo" to satisfy style requirements
                    pdfmetrics.registerFont(TTFont("Cairo", font_path))
                    pdfmetrics.registerFont(TTFont("ArabicFont", font_path))
                    
                    # Register bold version
                    registered_bold = False
                    for b_path in bold_paths:
                        if os.path.exists(b_path):
                            pdfmetrics.registerFont(TTFont("Cairo-Bold", b_path))
                            registered_bold = True
                            break
                    
                    if not registered_bold:
                        pdfmetrics.registerFont(TTFont("Cairo-Bold", font_path))
                        
                    fonts_registered = True
                    logger.info(f"Registered high-compatibility font as Cairo: {font_path}")
                    break
                except Exception as e:
                    logger.error(f"Failed to register compatible font: {e}")

        # 2. Fallback to embedded Cairo only if system fonts failed (Cairo often has CMAP issues)
        if not fonts_registered and os.path.exists(cairo_regular):
            try:
                pdfmetrics.registerFont(TTFont("Cairo", cairo_regular))
                pdfmetrics.registerFont(TTFont("ArabicFont", cairo_regular))
                if os.path.exists(cairo_bold):
                    pdfmetrics.registerFont(TTFont("Cairo-Bold", cairo_bold))
                else:
                    pdfmetrics.registerFont(TTFont("Cairo-Bold", cairo_regular))
                fonts_registered = True
            except Exception as e:
                logger.error(f"Failed to register embedded Cairo: {e}")

    except Exception as e:
        logger.error(f"Font registration system error: {e}")


_register_arabic_fonts()


# Standard Report Aesthetics (Blue Theme)
BORDER_COLOR = colors.HexColor("#2F5597")  # Dark Blue
HEADER_BG_COLOR = colors.HexColor("#2F5597")  # Dark Blue
HEADER_TEXT_COLOR = colors.white
STRIPE_COLOR = colors.HexColor("#D9E1F2")  # Light Blue


def get_asset_path(filename: str) -> str:
    """Get absolute path to a static image asset."""
    return os.path.join(resource_path("app/static/images"), filename)


def draw_report_header(canvas, doc, title: str, meta_data: dict = None):
    """Draw the standardized branded header with dual logos and dynamic fields."""
    import os
    canvas.saveState()
    width, height = landscape(letter)

    # 1. Dual Logos
    new_civ_logo = get_asset_path("new_civilization.png")
    rayon_logo = get_asset_path("rayon_energy.png")

    if os.path.exists(new_civ_logo):
        canvas.drawImage(new_civ_logo, 40, height - 70, width=120, height=50, preserveAspectRatio=True, mask='auto')

    if os.path.exists(rayon_logo):
        canvas.drawImage(rayon_logo, width - 160, height - 70, width=120, height=50, preserveAspectRatio=True, mask='auto')

    # 2. Centered Title
    registered_fonts = pdfmetrics.getRegisteredFontNames()
    title_font = "Cairo-Bold" if "Cairo-Bold" in registered_fonts else "Helvetica-Bold"
    canvas.setFont(title_font, 18)
    
    pdf_title = prepare_cell_value(title) if is_arabic_text(title) else title
    canvas.drawCentredString(width / 2, height - 40, pdf_title)

    # 3. Metadata Section (Dynamic Fields)
    meta_font = "Cairo" if "Cairo" in registered_fonts else "Helvetica"
    canvas.setFont(meta_font, 9)
    
    # Date and Page
    from datetime import datetime
    date_str = datetime.now().strftime("%Y-%m-%d")
    canvas.drawString(40, height - 90, prepare_cell_value(f"التاريخ: {date_str}"))
    canvas.drawRightString(width - 40, height - 90, prepare_cell_value(f"الصفحة: {doc.page}"))

    # Dynamic fields row (RTL flow)
    if meta_data:
        y_pos = height - 105
        # Start from the right margin
        x_pos = width - 40
        for label, value in meta_data.items():
            if value:
                field_text = f"{label}: {value}"
                # Use drawRightString for RTL alignment
                canvas.drawRightString(x_pos, y_pos, prepare_cell_value(field_text))
                x_pos -= 180  # Horizontal spacing to the left

    # 4. Blue line separator
    canvas.setStrokeColor(BORDER_COLOR)
    canvas.setLineWidth(1.5)
    canvas.line(40, height - 115, width - 40, height - 115)

    canvas.restoreState()


def draw_report_footer(canvas, doc):
    """Draw the standardized footer with signature labels."""
    canvas.saveState()
    width, height = landscape(letter)
    
    registered_fonts = pdfmetrics.getRegisteredFontNames()
    footer_font = "Cairo-Bold" if "Cairo-Bold" in registered_fonts else "Helvetica-Bold"
    canvas.setFont(footer_font, 10)

    # Fixed Arabic labels
    canvas.drawRightString(width - 50, 60, prepare_cell_value("مدير المبيعات:"))
    canvas.drawRightString(width - 50, 40, prepare_cell_value("التوقيع:"))

    canvas.restoreState()
