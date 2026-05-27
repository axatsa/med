"""
PDF report generator using fpdf2 with UTF-8/Cyrillic support.
Requires DejaVuSans.ttf in assets/fonts/ (see setup.sh).
"""
import io
import json
import os
from datetime import datetime
from fpdf import FPDF, Align

from utils.translations import REPORT_TITLES, RISK_LABELS, RISK_ALERT

FONTS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts")
FONT_REGULAR = os.path.join(FONTS_DIR, "DejaVuSans.ttf")
FONT_BOLD = os.path.join(FONTS_DIR, "DejaVuSans-Bold.ttf")

# Colour palette
C_DARK = (35, 35, 80)
C_ACCENT = (120, 60, 160)
C_HIGH = (210, 50, 50)
C_MODERATE = (220, 140, 0)
C_LOW = (40, 160, 80)
C_LIGHT_BG = (245, 245, 255)
C_WHITE = (255, 255, 255)
C_GREY = (100, 100, 100)
C_BORDER = (200, 200, 220)


def _risk_color(level: str):
    return {"HIGH": C_HIGH, "MODERATE": C_MODERATE, "LOW": C_LOW}.get(level, C_GREY)


class MedPDF(FPDF):
    def __init__(self, lang="ru"):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.lang = lang
        self.titles = REPORT_TITLES[lang]
        self._fonts_loaded = False
        self._load_fonts()
        self.set_auto_page_break(auto=True, margin=15)
        self.set_margins(15, 15, 15)

    def _load_fonts(self):
        if os.path.exists(FONT_REGULAR):
            self.add_font("DejaVu", fname=FONT_REGULAR)
            self.add_font("DejaVu", style="B", fname=FONT_BOLD if os.path.exists(FONT_BOLD) else FONT_REGULAR)
            self._fonts_loaded = True

    def _font(self, bold=False, size=10):
        if self._fonts_loaded:
            self.set_font("DejaVu", style="B" if bold else "", size=size)
        else:
            self.set_font("Helvetica", style="B" if bold else "", size=size)

    def header(self):
        self._font(bold=True, size=9)
        self.set_fill_color(*C_DARK)
        self.set_text_color(*C_WHITE)
        self.rect(0, 0, 210, 22, "F")
        self.set_xy(15, 6)
        self.cell(0, 5, self.titles["main"], ln=1)
        self._font(bold=False, size=8)
        self.set_xy(15, 12)
        self.set_text_color(200, 180, 230)
        self.cell(0, 5, self.titles["sub"])
        self.set_text_color(0, 0, 0)
        self.ln(14)

    def footer(self):
        self.set_y(-12)
        self._font(size=7)
        self.set_text_color(*C_GREY)
        self.cell(0, 5, self.titles["disclaimer"], align="C")

    def section_title(self, text: str):
        self._font(bold=True, size=9)
        self.set_fill_color(*C_LIGHT_BG)
        self.set_text_color(*C_DARK)
        self.set_draw_color(*C_BORDER)
        self.rect(15, self.get_y(), 180, 7, "FD")
        self.set_x(17)
        self.cell(176, 7, text, ln=1)
        self.ln(1)

    def kv_row(self, label: str, value: str, fill=False):
        self._font(size=9)
        self.set_fill_color(248, 248, 255)
        self.set_text_color(60, 60, 60)
        h = 6
        self.set_x(15)
        self.cell(90, h, label, border="B", fill=fill)
        self._font(bold=True, size=9)
        self.set_text_color(*C_DARK)
        self.cell(90, h, str(value), border="B", fill=fill, ln=1)

    def risk_box(self, risk_percent: float, risk_level: str):
        color = _risk_color(risk_level)
        label = RISK_LABELS[risk_level][self.lang]
        y0 = self.get_y()

        # Outer box
        self.set_fill_color(250, 248, 255)
        self.set_draw_color(*C_BORDER)
        self.rect(15, y0, 180, 40, "FD")

        # Percentage
        self._font(bold=True, size=36)
        self.set_text_color(*color)
        self.set_xy(15, y0 + 4)
        self.cell(180, 18, f"{risk_percent:.0f}%", align="C", ln=1)

        # Label
        self._font(bold=True, size=14)
        self.set_text_color(*color)
        self.set_x(15)
        self.cell(180, 8, label, align="C", ln=1)

        # Sub-label
        self._font(size=8)
        self.set_text_color(*C_GREY)
        self.set_x(15)
        self.cell(180, 6, self.titles["probability"], align="C", ln=1)

        self.ln(2)

        # Scale bar
        scale_y = self.get_y()
        self.set_x(15)
        # LOW segment
        self.set_fill_color(40, 160, 80)
        self.rect(15, scale_y, 54, 4, "F")
        # MODERATE segment
        self.set_fill_color(220, 140, 0)
        self.rect(69, scale_y, 72, 4, "F")
        # HIGH segment
        self.set_fill_color(210, 50, 50)
        self.rect(141, scale_y, 54, 4, "F")

        self._font(size=7)
        self.set_text_color(*C_LOW)
        self.set_xy(15, scale_y + 5)
        self.cell(54, 4, self.titles["low"], align="C")
        self.set_text_color(*C_MODERATE)
        self.set_x(69)
        self.cell(72, 4, self.titles["moderate"], align="C")
        self.set_text_color(*C_HIGH)
        self.set_x(141)
        self.cell(54, 4, self.titles["high"], align="C")

        self.ln(12)

    def predictor_bar(self, label: str, contribution: int, direction: str, index: int):
        fill = index % 2 == 0
        self.set_fill_color(248, 248, 255) if fill else self.set_fill_color(255, 255, 255)
        y = self.get_y()
        self.rect(15, y, 180, 7, "F")

        # Arrow icon placeholder
        arrow = "▲" if direction == "up" else "▼"
        color = C_HIGH if direction == "up" else C_LOW
        self._font(size=9)
        self.set_text_color(*color)
        self.set_xy(15, y)
        self.cell(8, 7, arrow)

        self._font(size=9)
        self.set_text_color(*C_DARK)
        self.set_x(23)
        self.cell(120, 7, label)

        # Bar
        bar_x = 145
        bar_w = max(1, int(contribution * 0.30))
        self.set_fill_color(*color)
        self.rect(bar_x, y + 2, bar_w, 3, "F")

        self._font(bold=True, size=9)
        self.set_text_color(*C_DARK)
        self.set_xy(bar_x + 32, y)
        self.cell(20, 7, f"{contribution}%", ln=1)

    def recommendation_item(self, text: str, index: int):
        self._font(size=9)
        self.set_text_color(*C_DARK)
        self.set_x(15)
        self.cell(8, 6, "✓")
        self.set_x(23)
        self.multi_cell(172, 6, text)


def generate_pdf(patient, assessment, lang: str = "ru") -> bytes:
    """
    Generate a PDF report for the given patient and assessment.
    Returns raw PDF bytes.
    """
    titles = REPORT_TITLES[lang]
    pdf = MedPDF(lang=lang)
    pdf.add_page()

    today = datetime.now().strftime("%d.%m.%Y")

    # --- 1. Patient data ---
    pdf.section_title(titles["section_patient"])
    pdf.kv_row("Дата / Sana" if lang == "uz" else "Дата", today)
    pdf.kv_row("Имя пациентки / Bemor ismi" if lang == "uz" else "Имя пациентки", patient.full_name or "—", fill=True)
    pdf.kv_row("Возраст (лет)", str(patient.age or "—"))
    pdf.kv_row("Срок беременности (нед.)", str(patient.gestational_age or "—"), fill=True)
    pdf.kv_row("ИМТ (кг/м²)", str(patient.bmi or "—"))
    pdf.kv_row("АД (MAP, мм рт.ст.)", str(patient.map_pressure or "—"), fill=True)
    pdf.kv_row("Паритет", str(patient.parity or "—"))
    pdf.kv_row("История ПЭ в анамнезе", "Да" if patient.previous_pe else "Нет", fill=True)
    pdf.ln(3)

    # --- 2. Placental insufficiency ---
    pdf.section_title(titles["section_placental"])
    pdf.kv_row("Диагноз ПН", "Да" if patient.pn_diagnosis else "Нет")
    pdf.kv_row("Степень ПН", str(patient.pn_degree or "—"), fill=True)
    pdf.kv_row("Допплерометрия (PI маточных артерий)", str(patient.pi_uterine or "—"))
    pdf.kv_row("Задержка роста плода", "Да" if patient.fgr else "Нет", fill=True)
    pdf.ln(3)

    # --- 3. Immunological ---
    pdf.section_title(titles["section_immuno"])
    for label, val in [
        ("IL-6", patient.il6), ("IL-10", patient.il10),
        ("MCP-1", patient.mcp1), ("IP-10", patient.ip10), ("TNF-α", patient.tnf_alpha),
    ]:
        fill = label in ("IL-10", "IP-10")
        pdf.kv_row(label, str(val or "—"), fill=fill)
    pdf.ln(3)

    # --- 4. Angiogenic ---
    pdf.section_title(titles["section_angio"])
    for label, val in [
        ("VEGF-A", patient.vegfa), ("PlGF", patient.pigf),
        ("sFlt-1", patient.sflt1), ("sFlt-1/PlGF Ratio", patient.sflt1_pigf_ratio),
    ]:
        fill = label in ("sFlt-1", )
        pdf.kv_row(label, str(val or "—"), fill=fill)
    pdf.ln(3)

    # --- 5. Genetic ---
    pdf.section_title(titles["section_genetic"])
    pdf.kv_row("IL6 rs1800795", patient.il6_rs1800795 or "—")
    pdf.kv_row("IL10 rs1800896", patient.il10_rs1800896 or "—", fill=True)
    pdf.kv_row("VEGFA rs2010963", patient.vegfa_rs2010963 or "—")
    pdf.ln(3)

    # --- 6. Result ---
    pdf.section_title(titles["section_result"])
    pdf.risk_box(assessment.risk_percent, assessment.risk_level)

    # Alert text
    alert = RISK_ALERT[assessment.risk_level][lang]
    pdf._font(size=9)
    pdf.set_text_color(*C_DARK)
    pdf.set_fill_color(255, 245, 245)
    pdf.set_x(15)
    pdf.multi_cell(180, 6, alert, border=1, fill=True)
    pdf.ln(3)

    # --- 7. Predictors ---
    pdf.section_title(titles["section_predictors"])
    predictors = json.loads(assessment.top_predictors_json or "[]")
    for i, pred in enumerate(predictors):
        pdf.predictor_bar(pred.get("label", pred["name"]), pred["contribution"], pred["direction"], i)
    pdf.ln(3)

    # --- 8. Recommendations ---
    if pdf.get_y() > 230:
        pdf.add_page()
    pdf.section_title(titles["section_recs"])
    recs = json.loads(assessment.recommendations_json or "[]")
    for i, rec in enumerate(recs):
        pdf.recommendation_item(rec, i)
    pdf.ln(3)

    # --- 9. Model info ---
    pdf.section_title(titles["section_model"])
    from config import Config
    pdf.kv_row(titles["algorithm"], Config.MODEL_ALGORITHM)
    pdf.kv_row(titles["auc"], str(Config.MODEL_AUC), fill=True)
    pdf.kv_row(titles["updated"], Config.MODEL_LAST_UPDATED)

    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf.read()
