#!/usr/bin/env python3
"""Generate the graduation thesis report (.docx) for the offline signature
verification project, following:
  - MauQuyDinhLuanVan_v1.1.pdf: Times New Roman 13pt, line spacing 1.5,
    paragraph spacing 6pt before/after, margins top 2cm / bottom 2cm /
    left 3cm / right 2cm, page number bottom-right.
  - The approved đề cương chi tiết (Phan_Thanh_Thuan_170123591.docx): chapter
    breakdown, dataset scope, T1-T8 experiment plan, 21-reference IEEE list.
  - The official Trường Đại học Trà Vinh formatting appendix
    ("biểu mẫu trình bày"): cover/bìa lót layout, front-matter page order,
    nhận xét pages, BẢNG/SƠ ĐỒ/HÌNH numbered per-chapter, page numbers
    starting (Arabic) at Chương 1, front matter in lowercase Roman numerals.
"""

from docx import Document
from docx.shared import Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.enum.section import WD_ORIENT, WD_SECTION_START
from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER

BASE = "/home/user/Recognite-signature"
IMGD = f"{BASE}/thesis/abs"
FORM = f"{IMGD}/formulas"
SCR = f"{IMGD}/screenshots"
EA = f"{BASE}/results/error_analysis"
RES = f"{BASE}/results"

# ---------------------------------------------------------------------------
# Student / school identifying info
# ---------------------------------------------------------------------------
# From the official biểu mẫu (this school's real 3-level structure):
UNIVERSITY = "TRƯỜNG ĐẠI HỌC TRÀ VINH"
# From the approved đề cương chi tiết's own cover block:
SCHOOL = "TRƯỜNG KỸ THUẬT VÀ CÔNG NGHỆ"
FACULTY = "KHOA CÔNG NGHỆ THÔNG TIN"
STUDENT_NAME = "Phan Thành Thuận"
STUDENT_ID = "170123591"
STUDENT_CLASS = "DX23TT11"
STUDENT_COHORT = "2023"  # inferred from class code "DX23TT11" -- flagged in Phụ lục C
MAJOR = "Công nghệ thông tin"
ADVISOR = "ThS. Nguyễn Nhứt Lam"
LOCATION = "Trà Vinh"
SUBMIT_DATE = f"{LOCATION}, tháng 9 năm 2026"
# Official biểu mẫu's exact wording (used verbatim on the cover and on both
# formal nhận xét forms) -- previously this report used "ĐỒ ÁN CHUYÊN NGÀNH";
# corrected here to match the binding template, flagged in Phụ lục C.
PROJECT_TYPE = "ĐỒ ÁN THỰC TẬP CHUYÊN NGÀNH"
# NOTE: the source đề cương's own cover page reads "NHẬN DẠNG CHỮ SỐ VIẾT
# TAY" (handwritten DIGIT recognition), but every one of its 12 sections
# (đặt vấn đề, mục tiêu, cơ sở lý thuyết, phương pháp, thực nghiệm, demo,
# tài liệu tham khảo...) is about chữ ký (signature) verification -- "chữ
# số" vs "chữ ký" is almost certainly a leftover template typo. The title
# below is corrected to match the đề cương's actual content; flagged to the
# student for confirmation.
THESIS_TITLE = "XÂY DỰNG HỆ THỐNG XÁC MINH CHỮ KÝ VIẾT TAY OFFLINE\nSỬ DỤNG MẠNG NƠ-RON SIAMESE"

# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def set_cell_text(cell, text, bold=False, size=12, align=None, italic=False):
    cell.text = ""
    p = cell.paragraphs[0]
    if align:
        p.alignment = align
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.font.name = "Times New Roman"
    run.bold = bold
    run.italic = italic


def add_field(paragraph, instr, placeholder_text=""):
    run = paragraph.add_run()
    fld1 = OxmlElement("w:fldChar")
    fld1.set(qn("w:fldCharType"), "begin")
    instrText = OxmlElement("w:instrText")
    instrText.set(qn("xml:space"), "preserve")
    instrText.text = instr
    fld2 = OxmlElement("w:fldChar")
    fld2.set(qn("w:fldCharType"), "separate")
    t = OxmlElement("w:t")
    t.text = placeholder_text
    fld3 = OxmlElement("w:fldChar")
    fld3.set(qn("w:fldCharType"), "end")
    r = run._r
    r.append(fld1)
    r.append(instrText)
    r.append(fld2)
    r.append(t)
    r.append(fld3)


def add_page_break(doc):
    doc.add_page_break()


def set_page_number_format(section, fmt, start=None):
    sectPr = section._sectPr
    pgNumType = sectPr.find(qn("w:pgNumType"))
    if pgNumType is None:
        pgNumType = OxmlElement("w:pgNumType")
        sectPr.append(pgNumType)
    pgNumType.set(qn("w:fmt"), fmt)
    if start is not None:
        pgNumType.set(qn("w:start"), str(start))


def add_heading(doc, text, level=1, size=None, center=False, page_break_before=False):
    p = doc.add_paragraph()
    p.style = doc.styles[f"Heading {level}"] if level <= 3 else doc.styles["Normal"]
    if page_break_before:
        p.paragraph_format.page_break_before = True
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.bold = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(size or {1: 16, 2: 14, 3: 13}.get(level, 13))
    run.font.color.rgb = RGBColor(0, 0, 0)
    return p


def add_para(doc, text="", bold=False, italic=False, center=False, justify=True, size=13, space_after=None):
    p = doc.add_paragraph()
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif justify:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if space_after is not None:
        p.paragraph_format.space_after = Pt(space_after)
    run = p.add_run(text)
    run.bold = bold
    run.italic = italic
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    return p


def add_bullet(doc, text, size=13):
    p = doc.add_paragraph(style="List Bullet")
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    return p


def add_source_note(doc, source):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"({source})")
    run.italic = True
    run.font.size = Pt(11)
    run.font.name = "Times New Roman"


def add_image(doc, path, width_cm=14, caption=None, caption_num=None, source=None):
    doc.add_picture(path, width=Cm(width_cm))
    last_p = doc.paragraphs[-1]
    last_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if caption:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(f"{caption_num + ': ' if caption_num else ''}{caption}")
        run.italic = True
        run.font.size = Pt(12)
        run.font.name = "Times New Roman"
    if source:
        add_source_note(doc, source)


def add_table(doc, headers, rows, col_widths_cm=None, caption=None, caption_num=None, source=None):
    if caption:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(f"{caption_num + ': ' if caption_num else ''}{caption}")
        run.italic = True
        run.font.size = Pt(12)
        run.font.name = "Times New Roman"
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        set_cell_text(hdr_cells[i], h, bold=True, size=12, align=WD_ALIGN_PARAGRAPH.CENTER)
    for row in rows:
        cells = table.add_row().cells
        for i, val in enumerate(row):
            set_cell_text(cells[i], str(val), size=12, align=WD_ALIGN_PARAGRAPH.CENTER if i > 0 else WD_ALIGN_PARAGRAPH.LEFT)
    if col_widths_cm:
        for row in table.rows:
            for i, w in enumerate(col_widths_cm):
                row.cells[i].width = Cm(w)
    if source:
        add_source_note(doc, source)
    doc.add_paragraph()
    return table


def add_formula(doc, img_path, width_cm=8, eq_num=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(img_path, width=Cm(width_cm))
    if eq_num:
        p2 = doc.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r2 = p2.add_run(eq_num)
        r2.italic = True
        r2.font.size = Pt(12)
        r2.font.name = "Times New Roman"


def add_toc_entry(doc, level, text, page):
    p = doc.add_paragraph()
    p.paragraph_format.tab_stops.add_tab_stop(Cm(16), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    if level == 2:
        p.paragraph_format.left_indent = Cm(0.7)
    run = p.add_run(f"{text}\t{page}")
    run.font.name = "Times New Roman"
    run.font.size = Pt(13 if level == 1 else 12)
    run.bold = (level == 1)


def add_letterhead(doc, left_lines, right_lines):
    """Borderless 2-column admin letterhead (UBND .../CỘNG HOÀ... block)."""
    n = max(len(left_lines), len(right_lines))
    table = doc.add_table(rows=n, cols=2)
    for i in range(n):
        lc = table.rows[i].cells[0]
        rc = table.rows[i].cells[1]
        set_cell_text(lc, left_lines[i] if i < len(left_lines) else "", bold=True, size=13, align=WD_ALIGN_PARAGRAPH.LEFT)
        set_cell_text(rc, right_lines[i] if i < len(right_lines) else "", bold=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_paragraph()


def add_blank_lines(doc, n=12, width=100):
    for _ in range(n):
        doc.add_paragraph("." * width)


# ---------------------------------------------------------------------------
# BẢNG / SƠ ĐỒ / HÌNH counters: per-chapter numbering "BẢNG x.y", "SƠ ĐỒ
# x.y", "HÌNH x.y" (uppercase), reset at each CHƯƠNG heading -- per the
# official biểu mẫu's own numbering rule. Equations are NOT covered by that
# rule (the biểu mẫu only numbers Bảng/Sơ đồ/Hình this way); they keep plain
# sequential (1), (2), (3)... across the whole report.
# ---------------------------------------------------------------------------
class Counter:
    chapter = 0
    table = 0
    fig = 0
    diagram = 0
    eq = 0


def start_chapter(n):
    Counter.chapter = n
    Counter.table = 0
    Counter.fig = 0
    Counter.diagram = 0


def next_table():
    Counter.table += 1
    return f"BẢNG {Counter.chapter}.{Counter.table}"


def next_fig():
    Counter.fig += 1
    return f"HÌNH {Counter.chapter}.{Counter.fig}"


def next_diagram():
    Counter.diagram += 1
    return f"SƠ ĐỒ {Counter.chapter}.{Counter.diagram}"


def next_eq():
    Counter.eq += 1
    return f"({Counter.eq})"


# ---------------------------------------------------------------------------
# Document setup
# ---------------------------------------------------------------------------

doc = Document()

style = doc.styles["Normal"]
style.font.name = "Times New Roman"
style.font.size = Pt(13)
pf = style.paragraph_format
pf.line_spacing = 1.5
pf.space_before = Pt(6)
pf.space_after = Pt(6)

for lvl, sz in ((1, 16), (2, 14), (3, 13)):
    hstyle = doc.styles[f"Heading {lvl}"]
    hstyle.font.name = "Times New Roman"
    hstyle.font.size = Pt(sz)
    hstyle.font.color.rgb = RGBColor(0, 0, 0)
    hstyle.font.bold = True
    hstyle.paragraph_format.space_before = Pt(12)
    hstyle.paragraph_format.space_after = Pt(6)
    hstyle.paragraph_format.line_spacing = 1.5

section = doc.sections[0]
section.page_height = Cm(29.7)
section.page_width = Cm(21.0)
section.orientation = WD_ORIENT.PORTRAIT
section.top_margin = Cm(2)
section.bottom_margin = Cm(2)
section.left_margin = Cm(3.0)
section.right_margin = Cm(2)

footer = section.footer
fp = footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
add_field(fp, "PAGE", "1")
# Front matter (bìa through danh mục từ viết tắt) uses lowercase Roman page
# numbers; Arabic numbering restarts at 1 on Chương 1 (see the second
# section created further below) -- per the official biểu mẫu's rule
# "Bắt đầu đánh số trang từ chương 1".
set_page_number_format(section, "lowerRoman", start=1)


def cover_page(sub_label):
    add_para(doc, UNIVERSITY, bold=True, center=True, size=16, space_after=0)
    add_para(doc, SCHOOL, bold=True, center=True, size=16, space_after=0)
    add_para(doc, FACULTY, bold=True, center=True, size=14, space_after=0)
    for _ in range(5):
        doc.add_paragraph()
    add_para(doc, PROJECT_TYPE, bold=True, center=True, size=16, space_after=6)
    add_para(doc, THESIS_TITLE, bold=True, center=True, size=18, space_after=6)
    for _ in range(6):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Giảng viên hướng dẫn : ")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.bold = True
    r = p.add_run(ADVISOR.upper())
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.bold = True
    add_para(doc, "", space_after=0)
    add_para(doc, "Sinh viên thực hiện", bold=True, center=True, size=14, space_after=6)
    add_para(doc, STUDENT_NAME.upper(), bold=True, center=True, size=14, space_after=0)
    add_para(doc, f"Mã số sinh viên : {STUDENT_ID}", bold=True, center=True, size=14, space_after=0)
    add_para(doc, f"Lớp : {STUDENT_CLASS}", bold=True, center=True, size=14, space_after=0)
    add_para(doc, f"Khoá : {STUDENT_COHORT}", bold=True, center=True, size=14, space_after=0)
    for _ in range(4):
        doc.add_paragraph()
    add_para(doc, SUBMIT_DATE, bold=True, center=True, size=13)
    add_page_break(doc)


# ===========================================================================
# BÌA CHÍNH (in trên bìa cứng, chữ nhũ vàng) -- theo đúng biểu mẫu chính thức
# ===========================================================================
cover_page("bìa chính")

# ===========================================================================
# BÌA LÓT (in giấy thường, nội dung giống bìa chính)
# ===========================================================================
cover_page("bìa lót")

# ===========================================================================
# TÓM TẮT (bổ sung hợp lý, không có trong biểu mẫu nhưng không mâu thuẫn --
# đặt trước Mục lục)
# ===========================================================================
add_heading(doc, "TÓM TẮT ĐỒ ÁN", level=1, center=True)
add_para(doc, (
    "Đồ án xây dựng một hệ thống xác minh chữ ký viết tay offline theo "
    "hướng writer-independent, dùng mạng nơ-ron Siamese kết hợp hàm mất mát "
    "contrastive loss, đúng như đề cương chi tiết đã đề xuất. Hai cấu hình "
    "mô hình được huấn luyện và so sánh: Cấu hình A — mạng CNN 5 khối "
    "Conv-BatchNorm-ReLU-MaxPool huấn luyện từ đầu; Cấu hình B — học chuyển "
    "giao (transfer learning) từ backbone ResNet18 tiền huấn luyện trên "
    "ImageNet, tinh chỉnh 2 giai đoạn. Một baseline đối chứng dùng đặc "
    "trưng thủ công HOG kết hợp SVM nhân RBF cũng được xây dựng để so sánh."
))
add_para(doc, (
    "Dữ liệu thực nghiệm gồm bộ CEDAR (55 người ký, chia writer-disjoint "
    "40/5/10 cho train/validation/test) để huấn luyện và đánh giá trong "
    "miền, và bộ BHSig260 (chữ ký tiếng Bengali và Hindi) để đánh giá tổng "
    "quát hoá zero-shot ngoài miền — không tinh chỉnh lại, dùng nguyên "
    "ngưỡng quyết định τ đã chọn trên tập validation của CEDAR theo tiêu "
    "chí Equal Error Rate (EER), sau đó đóng băng trước khi áp dụng lên tập "
    "test, tránh rò rỉ dữ liệu."
))
add_para(doc, (
    "Kết quả thực nghiệm thật (không mô phỏng) trên tập test CEDAR: Cấu "
    "hình B đạt AUC tổng thể 0,955 (EER validation 5,50%), vượt Cấu hình A "
    "(AUC 0,915, EER validation 9,75%) và baseline HOG+SVM (AUC 0,887). Cải "
    "thiện rõ rệt nhất của Cấu hình B nằm ở khả năng chống giả mạo ngẫu "
    "nhiên: FAR giảm từ 39,5% xuống 13,0%. Đánh giá zero-shot trên BHSig260 "
    "cho thấy mô hình vẫn giữ tín hiệu phân biệt nhất định qua miền dữ liệu "
    "khác hẳn về ngôn ngữ/hệ chữ viết (AUC 0,75–0,85)."
))
add_para(doc, (
    "So với các thí nghiệm T1–T8 đề ra trong đề cương, đồ án đã hoàn thành "
    "đầy đủ T1 (baseline), T2 (Cấu hình A), T3 (Cấu hình B) và T7 (kiểm tra "
    "chéo BHSig260); T5 hoàn thành một phần (khảo sát margin, chưa khảo sát "
    "riêng tắt/bật tăng cường dữ liệu); T4, T6, T8 chưa thực hiện do giới "
    "hạn thời gian/phần cứng — được ghi nhận minh bạch làm hướng phát triển "
    "ở phần Kết luận. Một ứng dụng demo tương tác được xây dựng bằng "
    "Streamlit, xử lý ảnh hoàn toàn trong bộ nhớ, sử dụng mô hình Cấu hình "
    "B đã huấn luyện."
))
add_para(doc, "Từ khoá: xác minh chữ ký offline, mạng Siamese, contrastive loss, "
              "học chuyển giao, ResNet18, writer-independent, CEDAR, BHSig260.",
         italic=True)
add_page_break(doc)

add_heading(doc, "ABSTRACT", level=1, center=True)
add_para(doc, (
    "This project builds an offline handwritten signature verification "
    "system following a writer-independent approach, using a Siamese "
    "neural network trained with contrastive loss, as proposed in the "
    "approved project outline. Two model configurations are trained and "
    "compared: Configuration A, a 5-block Conv-BatchNorm-ReLU-MaxPool "
    "convolutional network trained from scratch, and Configuration B, a "
    "transfer-learning model built on an ImageNet-pretrained ResNet18 "
    "backbone fine-tuned in two stages. A handcrafted-feature baseline "
    "(HOG features with an RBF-kernel SVM) is also built for comparison."
))
add_para(doc, (
    "Experiments use the CEDAR dataset (55 writers, split writer-disjointly "
    "40/5/10 for train/validation/test) for in-domain training, and the "
    "BHSig260 dataset (Bengali and Hindi signatures) for zero-shot "
    "cross-domain generalization -- the threshold τ selected on the CEDAR "
    "validation split by the Equal Error Rate (EER) criterion is frozen "
    "and applied as-is, with no fine-tuning, to avoid leaking information "
    "into threshold selection."
))
add_para(doc, (
    "Real (not simulated) results on the CEDAR test split: Configuration B "
    "reaches an overall AUC of 0.955 (validation EER 5.50%), outperforming "
    "Configuration A (AUC 0.915, EER 9.75%) and the HOG+SVM baseline (AUC "
    "0.887); FAR on random forgeries drops from 39.5% to 13.0%. Zero-shot "
    "evaluation on BHSig260 shows the model retains meaningful "
    "discriminative signal across a different script/language domain (AUC "
    "0.75-0.85)."
))
add_para(doc, (
    "Of the eight experiments (T1-T8) planned in the outline, T1 "
    "(baseline), T2 (Configuration A), T3 (Configuration B) and T7 "
    "(cross-dataset check) are completed in full; T5 is partially completed "
    "(margin sweep done, augmentation on/off not separately tested); T4, "
    "T6 and T8 were not carried out given time/hardware constraints, and "
    "are reported honestly as future work. An interactive Streamlit demo "
    "application, processing images entirely in memory, is built using the "
    "trained Configuration B model."
))
add_para(doc, "Keywords: offline signature verification, Siamese network, "
              "contrastive loss, transfer learning, ResNet18, writer-independent, "
              "CEDAR, BHSig260.", italic=True)
add_page_break(doc)

# ===========================================================================
# MỤC LỤC (đánh số trang thật, đo từ bản render cuối cùng; front matter =
# số La Mã thường, nội dung chương = số Ả Rập bắt đầu từ 1 tại Chương 1)
# ===========================================================================
add_heading(doc, "MỤC LỤC", level=1, center=True)
TOC_ENTRIES = [
    (1, "LỜI MỞ ĐẦU", "ix"),
    (2, "1. Lý do chọn đề tài", "ix"),
    (2, "2. Mục tiêu nghiên cứu", "x"),
    (2, "3. Đối tượng và phạm vi nghiên cứu", "x"),
    (2, "4. Phương pháp nghiên cứu", "xii"),
    (2, "5. Cấu trúc báo cáo", "xii"),
    (1, "CHƯƠNG 1. TỔNG QUAN", "1"),
    (2, "1.1. Bài toán xác minh chữ ký", "1"),
    (2, "1.2. Hướng dùng đặc trưng thủ công", "1"),
    (2, "1.3. Hướng học sâu", "2"),
    (2, "1.4. Các bộ dữ liệu công khai thường dùng", "2"),
    (2, "1.5. Khoảng trống và hướng tiếp cận của đồ án", "3"),
    (1, "CHƯƠNG 2. CƠ SỞ LÝ THUYẾT", "5"),
    (2, "2.1. Tiền xử lý ảnh", "5"),
    (2, "2.2. Mạng nơ-ron tích chập (CNN)", "5"),
    (2, "2.3. Mạng Siamese", "5"),
    (2, "2.4. Hàm mất mát", "6"),
    (2, "2.5. Học chuyển giao (transfer learning)", "7"),
    (2, "2.6. Các độ đo đánh giá", "7"),
    (1, "CHƯƠNG 3. PHƯƠNG PHÁP THỰC HIỆN", "9"),
    (2, "3.1. Quy trình tổng thể", "9"),
    (2, "3.2. Chuẩn bị dữ liệu và sinh cặp mẫu", "9"),
    (2, "3.3. Phương pháp cơ sở (baseline)", "10"),
    (2, "3.4. Mô hình Siamese chính", "10"),
    (2, "3.5. Công cụ và môi trường", "11"),
    (1, "CHƯƠNG 4. THỰC NGHIỆM VÀ ĐÁNH GIÁ", "12"),
    (2, "4.1. Cách chia dữ liệu", "12"),
    (2, "4.2. Các thí nghiệm đã thực hiện", "12"),
    (2, "4.3. Kết quả tổng thể trên tập test CEDAR", "14"),
    (2, "4.4. Kết quả phân theo loại giả mạo", "15"),
    (2, "4.5. Đường cong ROC", "17"),
    (2, "4.6. Phân tích định tính các ca lỗi", "18"),
    (2, "4.7. Đánh giá tổng quát hoá zero-shot trên BHSig260 (T7)", "22"),
    (2, "4.8. Thảo luận", "25"),
    (1, "CHƯƠNG 5. CHƯƠNG TRÌNH DEMO", "27"),
    (2, "5.1. Chức năng", "27"),
    (2, "5.2. Luồng sử dụng", "27"),
    (2, "5.3. Kiến trúc và công cụ", "27"),
    (2, "5.4. Kết quả trình diễn", "28"),
    (1, "KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", "31"),
    (2, "1. Kết quả đạt được", "31"),
    (2, "2. Hạn chế", "31"),
    (2, "3. Hướng phát triển", "32"),
    (1, "PHỤ LỤC", "33"),
    (1, "TÀI LIỆU THAM KHẢO", "36"),
]
for lvl, text, pg in TOC_ENTRIES:
    add_toc_entry(doc, lvl, text, pg)
add_page_break(doc)

# ===========================================================================
# LỜI MỞ ĐẦU
# ===========================================================================
add_heading(doc, "LỜI MỞ ĐẦU", level=1, center=True)

add_heading(doc, "1. Lý do chọn đề tài", level=2)
add_para(doc, (
    "Chữ ký viết tay vẫn là cách xác nhận danh tính và ý chí phổ biến nhất "
    "trong ngân hàng, hợp đồng và thủ tục hành chính, nên nhu cầu kiểm tra "
    "chữ ký tự động rất thực tế."
))
add_para(doc, (
    "Hiện nay, nhiều nơi vẫn đối chiếu chữ ký bằng mắt thường: giao dịch "
    "viên so chữ ký trên chứng từ với chữ ký mẫu đã lưu. Cách làm này có "
    "các hạn chế sau:"
))
add_bullet(doc, "Tốn thời gian khi khối lượng chứng từ lớn.")
add_bullet(doc, "Phụ thuộc vào kinh nghiệm, sự tập trung và trạng thái của "
                "người kiểm tra, nên kết quả thiếu nhất quán.")
add_bullet(doc, "Khó phát hiện giả mạo tinh vi, đặc biệt khi người giả mạo "
                "đã quan sát và luyện tập chữ ký thật.")
add_bullet(doc, "Không để lại số liệu định lượng để đánh giá mức độ tin "
                "cậy của từng lần kiểm tra.")
add_para(doc, (
    "Về mặt kỹ thuật, xác minh chữ ký là bài toán khó vì bốn lý do. Thứ "
    "nhất, cùng một người ký hai lần không bao giờ cho hai chữ ký giống hệt "
    "nhau (biến thiên nội tại). Thứ hai, chữ ký giả chuyên nghiệp có thể "
    "rất giống chữ ký thật, nên khoảng cách giữa hai lớp nhỏ. Thứ ba, mỗi "
    "người thường chỉ có rất ít mẫu tham chiếu, chỉ từ một đến vài mẫu. Thứ "
    "tư, chất lượng ảnh chữ ký thay đổi nhiều tùy thiết bị (máy quét, "
    "camera điện thoại), loại giấy và loại bút."
))
add_para(doc, (
    "Các phương pháp học sâu, đặc biệt là mạng Siamese, phù hợp với đặc "
    "điểm này. Thay vì phân loại chữ ký thành từng người cụ thể, mạng học "
    "một hàm đo độ tương đồng giữa hai ảnh. Nhờ vậy hệ thống có thể kiểm "
    "tra người chưa từng xuất hiện trong lúc huấn luyện, chỉ cần vài mẫu "
    "chữ ký thật để so sánh, và không phải huấn luyện lại khi có thêm "
    "người dùng mới."
))
add_para(doc, (
    "Từ các lý do trên, đồ án chọn xây dựng hệ thống xác minh chữ ký viết "
    "tay offline sử dụng mạng Siamese, kèm một chương trình demo cho phép "
    "tải hai ảnh lên và nhận kết quả \"thật\" hoặc \"giả\". Đề tài có bộ "
    "dữ liệu công khai, phương pháp đã được nghiên cứu rõ và kết quả đo "
    "được bằng các chỉ số chuẩn, nên phù hợp với quy mô một đồ án thực tập "
    "chuyên ngành. Báo cáo này trình bày đầy đủ kết quả THẬT thu được sau "
    "khi thực hiện đề cương đã duyệt, bao gồm cả những phần đạt được và "
    "những phần chưa hoàn thành đúng kế hoạch."
))

add_heading(doc, "2. Mục tiêu nghiên cứu", level=2)
add_heading(doc, "2.1. Mục tiêu chung", level=3)
add_para(doc, (
    "Xây dựng hệ thống xác minh chữ ký viết tay offline theo hướng "
    "writer-independent, phân biệt được chữ ký thật và chữ ký giả từ ảnh "
    "chữ ký, có kiểm chứng bằng thực nghiệm trên bộ dữ liệu công khai và có "
    "chương trình demo để minh họa."
))
add_heading(doc, "2.2. Mục tiêu cụ thể", level=3)
add_bullet(doc, "Nắm vững bài toán xác minh chữ ký offline: các loại giả "
                "mạo, các hướng tiếp cận truyền thống và học sâu, các độ đo "
                "đánh giá chuẩn (Accuracy, FAR, FRR, EER).")
add_bullet(doc, "Xây dựng quy trình tiền xử lý ảnh chữ ký (chuyển xám, khử "
                "nhiễu, nhị phân hóa, cắt vùng chữ ký, căn giữa, chuẩn hóa "
                "kích thước) và quy trình sinh cặp mẫu huấn luyện từ bộ dữ "
                "liệu.")
add_bullet(doc, "Cài đặt phương pháp cơ sở (baseline) dùng đặc trưng thủ "
                "công HOG kết hợp SVM để làm mốc so sánh.")
add_bullet(doc, "Cài đặt và huấn luyện mạng Siamese trên hai cấu hình: CNN "
                "huấn luyện từ đầu và CNN dùng trọng số tiền huấn luyện "
                "(transfer learning), với hàm mất mát contrastive.")
add_bullet(doc, "Đánh giá mô hình trên tập kiểm thử gồm những người ký "
                "không xuất hiện trong lúc huấn luyện; so sánh với "
                "baseline; phân tích các trường hợp nhận sai; đối chiếu với "
                "các chỉ tiêu đề ra.")
add_bullet(doc, "Xây dựng chương trình demo: người dùng tải lên chữ ký mẫu "
                "và chữ ký cần kiểm tra, hệ thống trả về kết quả thật hoặc "
                "giả cùng điểm tương đồng.")
add_para(doc, (
    "Mức độ hoàn thành từng mục tiêu cụ thể so với đề cương được đối chiếu "
    "chi tiết ở mục 4.2 (Chương 4) và mục 1 phần Kết luận."
))

add_heading(doc, "3. Đối tượng và phạm vi nghiên cứu", level=2)
add_heading(doc, "3.1. Đối tượng nghiên cứu", level=3)
add_bullet(doc, "Ảnh chữ ký viết tay dạng offline: ảnh tĩnh thu được từ "
                "máy quét hoặc camera, không kèm dữ liệu chuyển động của "
                "bút.")
add_bullet(doc, "Các mô hình đo độ tương đồng giữa hai ảnh chữ ký, cụ thể "
                "là mạng Siamese và phương pháp cơ sở dùng đặc trưng thủ "
                "công.")
add_heading(doc, "3.2. Phạm vi và các lựa chọn của đồ án", level=3)
add_table(doc, ["Khía cạnh", "Lựa chọn của đồ án", "Lý do"],
           [
               ["Bài toán", "Xác minh (verification): chữ ký này thật hay "
                             "giả so với chữ ký mẫu", "Luồng demo đơn "
                             "giản, không cần cơ sở dữ liệu nhiều người"],
               ["Dạng dữ liệu", "Offline (ảnh tĩnh)", "Phổ biến, không cần "
                             "thiết bị chuyên dụng, dễ thu thập"],
               ["Cách huấn luyện", "Writer-independent: một mô hình chung "
                             "cho mọi người", "Thêm người mới không phải "
                             "huấn luyện lại"],
               ["Loại giả mạo", "Giả mạo ngẫu nhiên (random) và giả mạo "
                             "chuyên nghiệp (skilled)", "Đánh giá được cả "
                             "trường hợp dễ và khó"],
               ["Dữ liệu", "CEDAR làm bộ chính; BHSig260 để kiểm tra khả "
                             "năng tổng quát", "Bộ chính nhỏ, dễ huấn "
                             "luyện; bộ thứ hai lớn và khó hơn"],
               ["Đầu ra", "Nhãn thật hoặc giả, kèm điểm tương đồng", "Dễ "
                             "hiểu, dễ trình bày khi bảo vệ"],
           ], col_widths_cm=[3, 7, 6], caption="Phạm vi và các lựa chọn của đồ án",
           source="Nguồn: đề cương chi tiết đã duyệt")
add_heading(doc, "3.3. Những nội dung không thực hiện", level=3)
add_bullet(doc, "Chữ ký online (có tọa độ, áp lực, tốc độ bút).")
add_bullet(doc, "Định danh chủ nhân của chữ ký trong một tập nhiều người.")
add_bullet(doc, "Chống các kiểu tấn công như dùng ảnh in hoặc bản "
                "photocopy của chữ ký thật.")
add_bullet(doc, "Triển khai vào hệ thống thực tế hoặc thay thế giám định "
                "chữ ký có giá trị pháp lý. Kết quả của hệ thống chỉ mang "
                "tính tham khảo.")

add_heading(doc, "4. Phương pháp nghiên cứu", level=2)
add_para(doc, (
    "Đồ án sử dụng phương pháp thực nghiệm (empirical): triển khai thật "
    "các thuật toán, huấn luyện thật trên dữ liệu thật, đo đạc thật các độ "
    "đo đánh giá. Toàn bộ số liệu trình bày trong Chương 4 là kết quả thật "
    "từ các lần chạy huấn luyện và đánh giá được thực hiện trong quá trình "
    "làm đồ án — không dùng số liệu giả định hay mô phỏng."
))

add_heading(doc, "5. Cấu trúc báo cáo", level=2)
add_para(doc, "Ngoài phần Lời mở đầu và Kết luận, nội dung báo cáo gồm 5 "
              "chương, bám sát cấu trúc báo cáo dự kiến trong đề cương chi "
              "tiết:")
add_bullet(doc, "Chương 1 — Tổng quan: bài toán xác minh chữ ký, các hướng "
                "tiếp cận (đặc trưng thủ công và học sâu), các bộ dữ liệu "
                "công khai, khoảng trống nghiên cứu.")
add_bullet(doc, "Chương 2 — Cơ sở lý thuyết: tiền xử lý ảnh, CNN, mạng "
                "Siamese, hàm mất mát, học chuyển giao, các độ đo đánh giá.")
add_bullet(doc, "Chương 3 — Phương pháp thực hiện: quy trình tổng thể, "
                "sinh cặp mẫu, baseline, hai cấu hình Siamese, thiết lập "
                "huấn luyện, công cụ và môi trường.")
add_bullet(doc, "Chương 4 — Thực nghiệm và đánh giá: cách chia dữ liệu, "
                "các thí nghiệm T1–T8 đã thực hiện, kết quả, phân tích lỗi, "
                "thảo luận.")
add_bullet(doc, "Chương 5 — Chương trình demo: chức năng, luồng sử dụng, "
                "kiến trúc và công cụ, kết quả trình diễn thật.")
add_bullet(doc, "Kết luận và hướng phát triển: tổng kết những gì đạt được, "
                "hạn chế còn tồn tại, và đề xuất hướng phát triển tiếp "
                "theo.")

add_page_break(doc)

# ===========================================================================
# LỜI CẢM ƠN
# ===========================================================================
add_heading(doc, "LỜI CẢM ƠN", level=1, center=True)
add_para(doc, (
    f"Em xin gửi lời cảm ơn chân thành đến giảng viên hướng dẫn {ADVISOR} đã "
    "tận tình định hướng, góp ý và hỗ trợ em trong suốt quá trình thực hiện "
    "đồ án thực tập chuyên ngành này, từ lúc xây dựng đề cương chi tiết đến "
    "khi hoàn thiện báo cáo. Những nhận xét về phương pháp luận, đặc biệt "
    "là yêu cầu nghiêm ngặt về việc tránh rò rỉ dữ liệu khi đánh giá mô "
    "hình sinh trắc học và việc phải báo cáo trung thực cả những phần chưa "
    "hoàn thành đúng kế hoạch, đã giúp em xây dựng được một quy trình thực "
    "nghiệm đáng tin cậy hơn."
))
add_para(doc, (
    f"Em cũng xin cảm ơn quý thầy cô {FACULTY}, {SCHOOL}, {UNIVERSITY} đã "
    "truyền đạt kiến thức nền tảng về học máy, thị giác máy tính trong "
    "suốt quá trình học tập, là cơ sở để em có thể tiếp cận và triển khai "
    "đồ án ở mức độ kỹ thuật như trình bày trong báo cáo này."
))
add_para(doc, (
    "Do thời gian và điều kiện phần cứng thực nghiệm (huấn luyện hoàn toàn "
    "trên CPU, không có GPU) còn hạn chế, một số nội dung khảo sát trong đề "
    "cương (T4, T5 phần tăng cường dữ liệu, T6, T8 — mục 4.2 Chương 4) chưa "
    "kịp thực hiện đầy đủ; đồ án ghi nhận minh bạch những giới hạn này thay "
    "vì che giấu. Em rất mong nhận được sự góp ý của quý thầy cô để hoàn "
    "thiện hơn."
))
add_para(doc, "Em xin chân thành cảm ơn.")
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
r = p.add_run(STUDENT_NAME)
r.font.name = "Times New Roman"
r.font.size = Pt(13)
r.italic = True
add_page_break(doc)

# ===========================================================================
# NHẬN XÉT (của cơ quan thực tập, nếu có)
# ===========================================================================
add_heading(doc, "NHẬN XÉT", level=1, center=True)
add_para(doc, "(Của cơ quan thực tập, nếu có)", center=True, italic=True, size=13)
add_para(doc, (
    "Đồ án này được thực hiện hoàn toàn trong phạm vi học thuật tại "
    "trường (xây dựng và huấn luyện mô hình học máy trên dữ liệu công "
    "khai), không có giai đoạn thực tập tại một cơ quan/doanh nghiệp ngoài "
    "trường, nên không có nhận xét của cơ quan thực tập cho mục này."
), center=True, justify=False)
add_page_break(doc)

# ===========================================================================
# NHẬN XÉT (của giảng viên hướng dẫn trong đồ án của sinh viên)
# ===========================================================================
add_heading(doc, "NHẬN XÉT", level=1, center=True)
add_para(doc, "(Của giảng viên hướng dẫn trong đồ án của sinh viên)", center=True, italic=True, size=13)
add_blank_lines(doc, 12)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
r = p.add_run(f"{LOCATION}, ngày ..... tháng ..... năm .....\nGiảng viên hướng dẫn\n(Ký và ghi rõ họ tên)")
r.font.name = "Times New Roman"
r.font.size = Pt(13)
r.italic = True
add_page_break(doc)

# ===========================================================================
# BẢN NHẬN XÉT ĐỒ ÁN THỰC TẬP CHUYÊN NGÀNH (mẫu, của giảng viên hướng dẫn)
# ===========================================================================
add_letterhead(doc,
    ["UBND TỈNH TRÀ VINH", UNIVERSITY],
    ["CỘNG HOÀ XÃ HỘI CHỦ NGHĨA VIỆT NAM", "Độc lập – Tự do – Hạnh phúc"])
add_heading(doc, f"BẢN NHẬN XÉT {PROJECT_TYPE}", level=2, center=True)
add_para(doc, "(Của giảng viên hướng dẫn)", center=True, italic=True, size=13)
add_para(doc, f"Họ và tên sinh viên: {STUDENT_NAME}\t\tMSSV: {STUDENT_ID}", justify=False)
add_para(doc, f"Ngành: {MAJOR}\t\tKhoá: {STUDENT_COHORT}", justify=False)
add_para(doc, f"Tên đồ án: {THESIS_TITLE.replace(chr(10), ' ')}", justify=False)
add_para(doc, f"Họ và tên Giáo viên hướng dẫn: {ADVISOR}", justify=False)
add_para(doc, "Chức danh: ..........................\t\tHọc vị: Thạc sĩ", justify=False)
add_heading(doc, "NHẬN XÉT", level=3)
for item in [
    "1. Nội dung đồ án:",
    "2. Ưu điểm:",
    "3. Khuyết điểm:",
    "4. Điểm mới đồ án:",
    "5. Giá trị thực trên đồ án:",
]:
    add_para(doc, item, justify=False)
    add_blank_lines(doc, 2)
for item in ["7. Đề nghị sửa chữa bổ sung:", "8. Đánh giá:"]:
    add_para(doc, item, justify=False)
    add_blank_lines(doc, 2)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
r = p.add_run(f"{LOCATION}, ngày ..... tháng ..... năm 20.....\nGiảng viên hướng dẫn\n(Ký & ghi rõ họ tên)")
r.font.name = "Times New Roman"
r.font.size = Pt(13)
r.italic = True
add_page_break(doc)

# ===========================================================================
# NHẬN XÉT (của giảng viên chấm trong đồ án của sinh viên)
# ===========================================================================
add_heading(doc, "NHẬN XÉT", level=1, center=True)
add_para(doc, "(Của giảng viên chấm trong đồ án của sinh viên)", center=True, italic=True, size=13)
add_blank_lines(doc, 12)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
r = p.add_run("Giảng viên chấm\n(ký và ghi rõ họ tên)")
r.font.name = "Times New Roman"
r.font.size = Pt(13)
r.italic = True
add_page_break(doc)

# ===========================================================================
# BẢN NHẬN XÉT ĐỒ ÁN THỰC TẬP CHUYÊN NGÀNH (mẫu, của cán bộ chấm đồ án)
# ===========================================================================
add_letterhead(doc,
    ["UBND TỈNH TRÀ VINH", UNIVERSITY],
    ["CỘNG HOÀ XÃ HỘI CHỦ NGHĨA VIỆT NAM", "Độc lập - Tự do - Hạnh phúc"])
add_heading(doc, f"BẢN NHẬN XÉT {PROJECT_TYPE}", level=2, center=True)
add_para(doc, "(Của cán bộ chấm đồ án)", center=True, italic=True, size=13)
add_para(doc, "Họ và tên người nhận xét: ..........................................", justify=False)
add_para(doc, "Chức danh: ..........................\t\tHọc vị: ..........................", justify=False)
add_para(doc, "Chuyên ngành: ..........................................", justify=False)
add_para(doc, "Cơ quan công tác: ..........................................", justify=False)
add_para(doc, f"Tên sinh viên: {STUDENT_NAME}", justify=False)
add_para(doc, f"Tên đề tài đồ án: {THESIS_TITLE.replace(chr(10), ' ')}", justify=False)
add_heading(doc, "I. Ý KIẾN NHẬN XÉT", level=3)
for item in ["1. Nội dung:", "2. Điểm mới các kết quả của đồ án:", "3. Ứng dụng thực tế:"]:
    add_para(doc, item, justify=False)
    add_blank_lines(doc, 2)
add_heading(doc, "II. CÁC VẤN ĐỀ CẦN LÀM RÕ", level=3)
add_para(doc, "(Các câu hỏi của giáo viên phản biện)", italic=True, justify=False)
add_blank_lines(doc, 4)
add_heading(doc, "III. KẾT LUẬN", level=3)
add_para(doc, "(Ghi rõ đồng ý hay không đồng ý cho bảo vệ đồ án)", italic=True, justify=False)
add_blank_lines(doc, 4)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
r = p.add_run(f"..............., ngày ...... tháng ...... năm 20...\nNgười nhận xét\n(Ký & ghi rõ họ tên)")
r.font.name = "Times New Roman"
r.font.size = Pt(13)
r.italic = True
add_page_break(doc)

# ===========================================================================
# DANH MỤC CÁC BẢNG, SƠ ĐỒ, HÌNH
# ===========================================================================
add_heading(doc, "DANH MỤC CÁC BẢNG, SƠ ĐỒ, HÌNH", level=1, center=True)
add_para(doc, (
    "Chữ số thứ nhất chỉ số thứ tự chương, chữ số thứ hai chỉ thứ tự bảng "
    "biểu/sơ đồ/hình trong chương đó (ví dụ BẢNG 1.1 là bảng thứ nhất của "
    "Chương 1). Danh sách dưới đây liệt kê theo thứ tự xuất hiện trong báo "
    "cáo."
))
figlist = [
    ("BẢNG 1.1", "Các bộ dữ liệu chữ ký công khai thường dùng"),
    ("SƠ ĐỒ 2.1", "Minh hoạ kiến trúc mạng Siamese"),
    ("BẢNG 3.1", "Số người ký và số cặp mẫu theo từng tập (CEDAR)"),
    ("BẢNG 3.2", "Thiết lập huấn luyện: dự kiến so với thực tế đã dùng"),
    ("SƠ ĐỒ 3.1", "Quy trình tổng thể của hệ thống xác minh chữ ký"),
    ("BẢNG 4.1", "Cách chia dữ liệu trên bộ CEDAR"),
    ("BẢNG 4.2", "Danh sách thí nghiệm T1–T8: kết quả thực tế"),
    ("BẢNG 4.3", "Kết quả tổng thể trên tập test CEDAR"),
    ("BẢNG 4.4", "Kết quả phân theo loại giả mạo — Cấu hình A"),
    ("BẢNG 4.5", "Kết quả phân theo loại giả mạo — Cấu hình B"),
    ("BẢNG 4.6", "So sánh Cấu hình A và Cấu hình B theo loại giả mạo"),
    ("HÌNH 4.1", "Đường cong ROC — baseline HOG + SVM"),
    ("HÌNH 4.2", "Đường cong ROC — Cấu hình A"),
    ("HÌNH 4.3", "Đường cong ROC — Cấu hình B"),
    ("HÌNH 4.4", "Ca lỗi false-accept, giả mạo ngẫu nhiên, Cấu hình A"),
    ("HÌNH 4.5", "Ca lỗi false-reject, cùng người ký, Cấu hình A"),
    ("HÌNH 4.6", "Ca lỗi false-accept, giả mạo kỹ năng cao, Cấu hình A"),
    ("HÌNH 4.7", "Ca lỗi false-accept, giả mạo ngẫu nhiên, Cấu hình B"),
    ("HÌNH 4.8", "Ca lỗi false-reject nghiêm trọng trên BHSig260"),
    ("HÌNH 4.9", "Ca lỗi false-accept giả mạo kỹ năng cao trên BHSig260"),
    ("BẢNG 4.7", "Kết quả zero-shot trên BHSig260 (T7)"),
    ("BẢNG 4.8", "Rủi ro đã dự kiến so với thực tế xảy ra"),
    ("BẢNG 5.1", "Kiến trúc và công cụ của chương trình demo"),
    ("HÌNH 5.1", "Giao diện demo Streamlit — trạng thái ban đầu"),
    ("HÌNH 5.2", "Giao diện demo Streamlit — kết quả với cặp chữ ký thật"),
    ("HÌNH 5.3", "Giao diện demo Streamlit — kết quả với cặp chữ ký giả"),
]
add_table(doc, ["Số hiệu", "Tên bảng / sơ đồ / hình"], figlist, col_widths_cm=[3, 13])
add_page_break(doc)

# ===========================================================================
# DANH MỤC TỪ VIẾT TẮT
# ===========================================================================
add_heading(doc, "DANH MỤC TỪ VIẾT TẮT", level=1, center=True)
abbr = [
    ("CNN", "Convolutional Neural Network — Mạng nơ-ron tích chập"),
    ("SVM", "Support Vector Machine — Máy vector hỗ trợ"),
    ("HOG", "Histogram of Oriented Gradients — Lược đồ hướng gradient"),
    ("LBP", "Local Binary Pattern — Mẫu nhị phân cục bộ"),
    ("FAR", "False Acceptance Rate — Tỉ lệ chấp nhận nhầm"),
    ("FRR", "False Rejection Rate — Tỉ lệ từ chối nhầm"),
    ("EER", "Equal Error Rate — Điểm cân bằng lỗi (FAR = FRR)"),
    ("ROC", "Receiver Operating Characteristic — Đường cong đặc trưng vận hành"),
    ("AUC", "Area Under the Curve — Diện tích dưới đường cong ROC"),
    ("ResNet", "Residual Network — Mạng tích chập dư"),
    ("VGG", "Visual Geometry Group — Kiến trúc CNN của nhóm VGG, Oxford"),
    ("GPU/CPU", "Graphics/Central Processing Unit — Bộ xử lý đồ hoạ/trung tâm"),
    ("BN", "Batch Normalization — Chuẩn hoá theo lô"),
    ("τ (tau)", "Ngưỡng quyết định (decision threshold)"),
    ("T1–T8", "Ký hiệu các thí nghiệm theo đề cương chi tiết (mục 4.2, Chương 4)"),
]
add_table(doc, ["Từ viết tắt", "Giải nghĩa"], abbr, col_widths_cm=[3, 13])

# ===========================================================================
# [SECTION BREAK] Từ đây: số trang Ả Rập, bắt đầu lại từ 1 tại Chương 1,
# theo đúng quy định của biểu mẫu chính thức.
# ===========================================================================
new_section = doc.add_section(WD_SECTION_START.NEW_PAGE)
set_page_number_format(new_section, "decimal", start=1)


def chapter_byline(doc):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(f"GVHD: {ADVISOR}          SVTH: {STUDENT_NAME}")
    r.italic = True
    r.font.size = Pt(12)
    r.font.name = "Times New Roman"


# ===========================================================================
# CHƯƠNG 1 — TỔNG QUAN
# ===========================================================================
start_chapter(1)
add_heading(doc, "CHƯƠNG 1. TỔNG QUAN", level=1)
chapter_byline(doc)

add_heading(doc, "1.1. Bài toán xác minh chữ ký", level=2)
add_para(doc, (
    "Cho một chữ ký mẫu đã biết là thật và một chữ ký cần kiểm tra, hệ "
    "thống phải quyết định chữ ký cần kiểm tra có do cùng người ký thật "
    "hay không. Đây là bài toán phân loại nhị phân trên cặp ảnh [18]."
))
add_para(doc, "Có ba loại giả mạo thường được xét:")
add_bullet(doc, "Giả mạo ngẫu nhiên (random forgery): người giả không biết "
                "chữ ký thật, dùng chữ ký của người khác hoặc ký theo ý "
                "mình. Loại này dễ phát hiện nhất.")
add_bullet(doc, "Giả mạo đơn giản (simple forgery): người giả biết tên "
                "chủ chữ ký nhưng chưa thấy chữ ký thật.")
add_bullet(doc, "Giả mạo chuyên nghiệp (skilled forgery): người giả đã "
                "xem và luyện tập bắt chước chữ ký thật. Loại này khó phát "
                "hiện nhất.")
add_para(doc, (
    "Về cách huấn luyện, phương pháp writer-dependent xây một mô hình "
    "riêng cho từng người, còn writer-independent dùng một mô hình chung "
    "học cách so sánh hai chữ ký bất kỳ [10]. Đồ án theo hướng thứ hai."
))

add_heading(doc, "1.2. Hướng dùng đặc trưng thủ công", level=2)
add_para(doc, (
    "Các phương pháp này trích các đặc trưng do người thiết kế chọn, sau "
    "đó đưa vào bộ phân loại. Các nhóm đặc trưng thường gặp gồm:"
))
add_bullet(doc, "Đặc trưng hình học toàn cục: tỷ lệ khung hình, độ "
                "nghiêng, mật độ điểm ảnh, vị trí trọng tâm.")
add_bullet(doc, "Đặc trưng gradient và kết cấu: HOG (Histogram of "
                "Oriented Gradients) [3], LBP (Local Binary Patterns) [14].")
add_bullet(doc, "Đặc trưng miền tần số: biến đổi Fourier, wavelet.")
add_para(doc, (
    "Đặc trưng HOG chia ảnh thành các ô nhỏ (cell), tính histogram hướng "
    "gradient cường độ trong mỗi ô, sau đó chuẩn hoá theo từng khối (block) "
    "ô lân cận:"
))
add_formula(doc, f"{FORM}/f_hog.png", width_cm=8, eq_num=next_eq())
add_para(doc, (
    "trong đó Gx, Gy là gradient ảnh theo hai trục, θ là hướng gradient "
    "dùng để phân bổ vào các bin của histogram. Bộ phân loại thường là "
    "SVM, k-NN hoặc mô hình Markov ẩn; một số công trình dùng thống kê "
    "khoảng cách giữa các mẫu [11], trên bộ CEDAR. Ưu điểm là nhẹ, dễ giải "
    "thích và không cần nhiều dữ liệu. Nhược điểm là chất lượng phụ thuộc "
    "vào việc thiết kế đặc trưng, và thường giảm khi chuyển sang bộ dữ "
    "liệu có phong cách chữ ký khác."
))

add_heading(doc, "1.3. Hướng học sâu", level=2)
add_bullet(doc, "Bromley và cộng sự [1] đề xuất kiến trúc Siamese cho bài "
                "toán xác minh chữ ký (trên dữ liệu online). Đây là ý "
                "tưởng nền tảng: hai nhánh mạng dùng chung trọng số và so "
                "sánh hai vector đặc trưng.")
add_bullet(doc, "Hafemann, Sabourin và Oliveira [8] huấn luyện CNN để học "
                "đặc trưng writer-independent từ ảnh chữ ký của nhiều "
                "người, sau đó dùng đặc trưng này cho từng người cụ thể.")
add_bullet(doc, "Dey và cộng sự [4] đề xuất SigNet, một mạng Siamese tích "
                "chập dùng contrastive loss, đánh giá trên CEDAR, GPDS300, "
                "GPDS Synthetic và BHSig260.")
add_para(doc, (
    "Nhìn chung, các phương pháp học sâu cho kết quả tốt hơn hướng thủ "
    "công trên hầu hết các bộ dữ liệu chuẩn [7], [10], đổi lại cần nhiều dữ "
    "liệu hơn và chi phí tính toán lớn hơn."
))

add_heading(doc, "1.4. Các bộ dữ liệu công khai thường dùng", level=2)
add_table(doc, ["Bộ dữ liệu", "Số người ký", "Mẫu mỗi người", "Ghi chú"],
           [
               ["CEDAR [11]", 55, "24 thật, 24 giả", "Bộ nhỏ, phổ biến, "
                                    "phù hợp làm bộ chính — được đồ án chọn"],
               ["MCYT-75 [15]", 75, "15 thật, 15 giả", "Thu tại Tây Ban Nha; "
                                    "phiên bản offline gồm 2.250 ảnh"],
               ["GPDS-960 [21]", 960, "24 thật, 30 giả", "Bộ lớn, giả mạo "
                                    "chuyên nghiệp"],
               ["GPDS Synthetic [5]", "4.000 (tổng hợp)", "24 thật, 30 giả",
                                    "Chữ ký sinh tự động, dùng để huấn "
                                    "luyện quy mô lớn"],
               ["BHSig260 [17]", "260 (100 Bengali, 160 Hindi)", "24 thật, "
                                    "30 giả", "Chữ ký Bengali và Hindi — "
                                    "được đồ án chọn làm bộ thứ hai"],
           ], col_widths_cm=[4, 3, 3, 6], caption="Các bộ dữ liệu chữ ký công khai thường dùng",
           caption_num=next_table(), source="Nguồn: tổng hợp từ [5], [11], [15], [17], [21]")
add_para(doc, (
    "Đồ án chọn CEDAR làm bộ chính (huấn luyện + đánh giá trong miền) và "
    "BHSig260 làm bộ thứ hai (chỉ đánh giá tổng quát hoá zero-shot, không "
    "huấn luyện), đúng như phạm vi đã đề ra ở mục 3.2 (Lời mở đầu). Các bộ "
    "MCYT-75, GPDS-960 và GPDS Synthetic không được sử dụng trong phạm vi "
    "đồ án này, được nêu ở đây để có bức tranh tổng quan đầy đủ về các lựa "
    "chọn dữ liệu khả dĩ cho bài toán."
))

add_heading(doc, "1.5. Khoảng trống và hướng tiếp cận của đồ án", level=2)
add_bullet(doc, "Nhiều công trình chỉ báo cáo kết quả trên từng bộ dữ liệu "
                "riêng lẻ. Việc kiểm tra chéo giữa các bộ dữ liệu, tức là "
                "huấn luyện ở bộ này và kiểm thử ở bộ khác, ít được làm "
                "hơn nhưng phản ánh sát hơn khả năng tổng quát.")
add_bullet(doc, "Giả mạo chuyên nghiệp vẫn khó phát hiện hơn giả mạo ngẫu "
                "nhiên đáng kể, nên cần báo cáo tách riêng hai trường hợp.")
add_bullet(doc, "Các bộ dữ liệu công khai chủ yếu thu từ người ký ở nước "
                "ngoài. Đặc điểm chữ ký của người Việt có thể khác — đồ án "
                "chưa thu thập được tập mẫu tự thu thập (T8) trong phạm vi "
                "thời gian hiện tại, xem mục 4.2 và phần Kết luận.")
add_para(doc, (
    "Từ đó, đồ án tập trung vào ba việc: so sánh có kiểm soát giữa phương "
    "pháp cơ sở và mạng Siamese trên cùng quy trình tiền xử lý và cùng "
    "cách chia dữ liệu; đánh giá chéo giữa hai bộ dữ liệu CEDAR và "
    "BHSig260; và hoàn thiện một chương trình demo dùng được — cả ba nội "
    "dung này đã được thực hiện với dữ liệu và kết quả thật, trình bày ở "
    "Chương 4 và Chương 5."
))

add_page_break(doc)

# ===========================================================================
# CHƯƠNG 2 — CƠ SỞ LÝ THUYẾT
# ===========================================================================
start_chapter(2)
add_heading(doc, "CHƯƠNG 2. CƠ SỞ LÝ THUYẾT", level=1)
chapter_byline(doc)

add_heading(doc, "2.1. Tiền xử lý ảnh", level=2)
add_para(doc, (
    "Mục đích là loại bỏ khác biệt không liên quan đến người ký (nền, "
    "nhiễu, kích thước, vị trí) để mô hình tập trung vào hình dạng nét "
    "chữ. Các bước áp dụng trong đồ án:"
))
add_bullet(doc, "Chuyển ảnh xám và khử nhiễu bằng bộ lọc Gaussian (mặc "
                "định) hoặc median.")
add_bullet(doc, "Nhị phân hóa bằng ngưỡng Otsu [16] để tách nét chữ khỏi "
                "nền — thuật toán tự động tìm ngưỡng cực đại hoá phương "
                "sai giữa hai lớp nền/nét chữ.")
add_bullet(doc, "Cắt sát vùng chữ ký theo hộp bao quanh các điểm nét "
                "(bounding box).")
add_bullet(doc, "Căn giữa và đổi kích thước về cỡ cố định, giữ tỷ lệ khung "
                "hình bằng cách thêm viền trắng: 220×150 điểm ảnh cho "
                "Cấu hình A (huấn luyện từ đầu), 224×224 cho Cấu hình B "
                "(dùng mạng tiền huấn luyện).")
add_bullet(doc, "Chuẩn hóa giá trị điểm ảnh về khoảng [0, 1] (Cấu hình A) "
                "hoặc theo trung bình/độ lệch chuẩn ImageNet (Cấu hình B).")
add_para(doc, (
    "Bước nhị phân hoá chỉ dùng để xác định vùng chữ ký (bounding box); "
    "việc có dùng ảnh nhị phân làm đầu vào cuối cùng cho mô hình hay không "
    "(binarize_output) là một biến thử nghiệm riêng (T4, mục 4.2) — trong "
    "phạm vi thời gian thực hiện, đồ án chưa kịp chạy so sánh có/không nhị "
    "phân hoá đầu ra."
))

add_heading(doc, "2.2. Mạng nơ-ron tích chập (CNN)", level=2)
add_para(doc, (
    "CNN gồm các lớp tích chập, hàm kích hoạt ReLU, lớp gộp (pooling), "
    "chuẩn hóa theo lô (batch normalization) và các lớp kết nối đầy đủ. "
    "Các lớp đầu học đặc trưng cục bộ như nét ngang, nét cong; các lớp sau "
    "kết hợp thành cấu trúc lớn hơn như vòng, gạch nối và bố cục toàn chữ "
    "ký. Vì ảnh chữ ký ít chi tiết màu sắc nhưng giàu thông tin về hình "
    "dạng nét, CNN là lựa chọn tự nhiên để học biểu diễn."
))

add_heading(doc, "2.3. Mạng Siamese", level=2)
add_para(doc, (
    "Mạng Siamese gồm hai nhánh CNN giống hệt nhau và dùng chung trọng "
    "số. Mỗi ảnh đi qua một nhánh và được ánh xạ thành một vector đặc "
    "trưng (embedding). Khoảng cách giữa hai vector cho biết mức khác "
    "nhau của hai chữ ký:"
))
add_formula(doc, f"{FORM}/f_distance.png", width_cm=7, eq_num=next_eq())
add_para(doc, (
    "trong đó f_θ là mạng CNN với tham số θ. Hai chữ ký được coi là cùng "
    "người ký thật khi D nhỏ hơn một ngưỡng τ. Vì mạng học cách so sánh "
    "chứ không học nhận diện từng người, nó áp dụng được cho người mới mà "
    "không cần huấn luyện lại [13]."
))
add_image(doc, f"{FORM}/diagram_siamese.png", width_cm=13,
          caption="Minh hoạ kiến trúc mạng Siamese: hai nhánh CNN dùng chung trọng số",
          caption_num=next_diagram(), source="Nguồn: minh hoạ tự vẽ")

add_heading(doc, "2.4. Hàm mất mát", level=2)
add_para(doc, (
    "Contrastive loss [6] kéo hai chữ ký thật của cùng một người lại gần "
    "nhau và đẩy cặp thật–giả ra xa ít nhất một khoảng margin m:"
))
add_formula(doc, f"{FORM}/f_contrastive.png", width_cm=11, eq_num=next_eq())
add_para(doc, (
    "Với y = 1 cho cặp cùng người ký thật và y = 0 cho cặp khác nhau "
    "(thật với giả, hoặc hai người khác nhau). Ý tưởng gốc của việc học "
    "một hàm đo tương đồng bằng cách này đến từ công trình về xác thực "
    "khuôn mặt [2]."
))
add_para(doc, (
    "Triplet loss [19] dùng bộ ba gồm mẫu neo a, mẫu dương p (thật, cùng "
    "người) và mẫu âm n (giả hoặc của người khác):"
))
add_formula(doc, f"{FORM}/f_triplet.png", width_cm=11, eq_num=next_eq())
add_para(doc, (
    "Đồ án dùng contrastive loss làm chính cho toàn bộ thực nghiệm (T1–T5, "
    "T7). Triplet loss (T6, thí nghiệm bổ sung theo đề cương) chưa được "
    "cài đặt và chạy thực tế trong phạm vi thời gian thực hiện — công thức "
    "được trình bày ở đây để hoàn chỉnh phần cơ sở lý thuyết và làm cơ sở "
    "cho hướng phát triển tiếp theo (mục 3, phần Kết luận)."
))

add_heading(doc, "2.5. Học chuyển giao (transfer learning)", level=2)
add_para(doc, (
    "Học chuyển giao dùng mạng đã huấn luyện sẵn trên tập ảnh lớn như "
    "ImageNet (ví dụ VGG16 [20] hoặc ResNet18 [9]), bỏ lớp phân loại "
    "cuối, thay bằng lớp tạo embedding rồi tinh chỉnh (fine-tune) trên dữ "
    "liệu chữ ký. Ảnh chữ ký khác nhiều so với ảnh tự nhiên, nên cần thử "
    "tinh chỉnh nhiều tầng và so sánh với mạng huấn luyện từ đầu để xem "
    "học chuyển giao có thật sự giúp ích hay không. Đồ án chọn ResNet18 "
    "trong hai lựa chọn nêu trên (kết quả cụ thể ở Chương 4, mục 4.3–4.4)."
))

add_heading(doc, "2.6. Các độ đo đánh giá", level=2)
add_para(doc, (
    "Gọi lớp dương là chữ ký thật. TP là chữ ký thật được chấp nhận, FN là "
    "chữ ký thật bị từ chối, FP là chữ ký giả bị chấp nhận, TN là chữ ký "
    "giả bị từ chối. Với mỗi ngưỡng τ:"
))
add_formula(doc, f"{FORM}/f_far.png", width_cm=9, eq_num=next_eq())
add_formula(doc, f"{FORM}/f_frr.png", width_cm=9, eq_num=next_eq())
add_para(doc, (
    "FAR (False Acceptance Rate) là tỷ lệ chữ ký giả bị chấp nhận nhầm; "
    "FRR (False Rejection Rate) là tỷ lệ chữ ký thật bị từ chối nhầm. Tăng "
    "ngưỡng làm FAR tăng và FRR giảm, và ngược lại. EER (Equal Error Rate) "
    "là giá trị khi hai tỷ lệ này bằng nhau:"
))
add_formula(doc, f"{FORM}/f_eer.png", width_cm=9, eq_num=next_eq())
add_para(doc, (
    "Ngoài ra đồ án báo cáo Accuracy tại ngưỡng chọn trên tập validation, "
    "và diện tích dưới đường cong ROC (AUC):"
))
add_formula(doc, f"{FORM}/f_accuracy.png", width_cm=9, eq_num=next_eq())
add_para(doc, (
    "EER không phụ thuộc việc chọn ngưỡng nên thích hợp để so sánh các mô "
    "hình với nhau. Đồ án dùng EER trên tập validation làm tiêu chí CHỌN "
    "ngưỡng τ, sau đó ĐÓNG BĂNG giá trị này và chỉ dùng nó để tính FAR/"
    "FRR/Accuracy trên tập test, đảm bảo tập test không được dùng để tinh "
    "chỉnh bất kỳ siêu tham số quyết định nào."
))

add_page_break(doc)

# ===========================================================================
# CHƯƠNG 3 — PHƯƠNG PHÁP THỰC HIỆN
# ===========================================================================
start_chapter(3)
add_heading(doc, "CHƯƠNG 3. PHƯƠNG PHÁP THỰC HIỆN", level=1)
chapter_byline(doc)

add_heading(doc, "3.1. Quy trình tổng thể", level=2)
add_para(doc, (
    "Hệ thống nhận hai ảnh, đưa qua cùng một quy trình tiền xử lý và cùng "
    "một mạng CNN, rồi so khoảng cách giữa hai vector đặc trưng với một "
    "ngưỡng."
))
add_image(doc, f"{FORM}/diagram_pipeline.png", width_cm=14,
          caption="Quy trình tổng thể của hệ thống xác minh chữ ký",
          caption_num=next_diagram(), source="Nguồn: minh hoạ tự vẽ")

add_heading(doc, "3.2. Chuẩn bị dữ liệu và sinh cặp mẫu", level=2)
add_para(doc, (
    "Dữ liệu được chia theo người ký, không để một người xuất hiện ở "
    "nhiều tập, để mô phỏng đúng tình huống kiểm tra người chưa từng gặp. "
    "Từ ảnh của mỗi người, hệ thống sinh ba loại cặp:"
))
add_bullet(doc, "Cặp dương: hai chữ ký thật của cùng một người.")
add_bullet(doc, "Cặp âm khó: một chữ ký thật và một chữ ký giả chuyên "
                "nghiệp của cùng người đó.")
add_bullet(doc, "Cặp âm dễ: chữ ký thật của hai người khác nhau (giả mạo "
                "ngẫu nhiên).")
add_para(doc, (
    "Về nguyên tắc, với CEDAR mỗi người có 24 chữ ký thật nên có thể sinh "
    "tối đa 276 cặp dương (tổ hợp chập 2 của 24) và 576 cặp thật–giả (24 × "
    "24) cho mỗi người; đồ án lấy mẫu có kiểm soát trên tập tổ hợp này "
    "(ngân sách 40 cặp/loại/người ký, tỉ lệ dương : âm khó : âm dễ = 2:1:1) "
    "thay vì dùng toàn bộ tổ hợp, để cân bằng giữa ba loại cặp và giữ số "
    "lượng cặp huấn luyện ở mức khả thi cho huấn luyện trên CPU."
))
add_table(doc, ["Tập", "Số người ký", "Số cặp"],
           [["Train", 40, 3200], ["Validation", 5, 400], ["Test", 10, 800]],
           col_widths_cm=[5, 5, 5], caption="Số người ký và số cặp mẫu theo từng tập (CEDAR)",
           caption_num=next_table(), source="Nguồn: kết quả thực nghiệm của đồ án")

add_heading(doc, "3.3. Phương pháp cơ sở (baseline)", level=2)
add_bullet(doc, "Trích đặc trưng HOG từ ảnh đã chuẩn hóa kích thước.")
add_bullet(doc, "Với mỗi cặp ảnh, lấy vector chênh lệch tuyệt đối giữa hai "
                "vector đặc trưng.")
add_bullet(doc, "Huấn luyện SVM (nhân RBF) để phân loại cặp thành cùng "
                "người thật hoặc không; siêu tham số C ∈ {0,1; 1; 10} và "
                "γ ∈ {\"scale\"; 0,01; 0,001} dò bằng grid search trên tập "
                "validation.")
add_bullet(doc, "Dùng đúng cách chia người ký và đúng bộ cặp mẫu như mạng "
                "Siamese để so sánh công bằng.")

add_heading(doc, "3.4. Mô hình Siamese chính", level=2)
add_para(doc, "Đồ án cài đặt hai cấu hình đúng như đề cương đã đề xuất:")
add_bullet(doc, "Cấu hình A (huấn luyện từ đầu): 5 khối Conv, BatchNorm, "
                "ReLU và MaxPool, tiếp theo lớp kết nối đầy đủ, cho "
                "embedding 128 chiều.")
add_bullet(doc, "Cấu hình B (học chuyển giao): dùng ResNet18 đã tiền "
                "huấn luyện, thay lớp cuối bằng lớp embedding 128 chiều, "
                "huấn luyện 2 giai đoạn — giai đoạn 1 đóng băng backbone "
                "(chỉ huấn luyện head, 5 epoch), giai đoạn 2 mở khoá khối "
                "cuối cùng của backbone với tốc độ học nhỏ hơn.")
add_para(doc, "Các thiết lập huấn luyện thực tế đã sử dụng (so với dự kiến "
              "ban đầu trong đề cương):")
add_table(doc, ["Thành phần", "Dự kiến (đề cương)", "Thực tế đã dùng"],
           [
               ["Hàm mất mát", "Contrastive; margin 0,5/1,0/2,0", "Contrastive; "
                                "margin 0,5/1,0/2,0 — khớp đề cương"],
               ["Bộ tối ưu", "Adam [12]", "Adam [12] — khớp đề cương"],
               ["Tốc độ học", "≈1e-3 (từ đầu), 1e-4 (tinh chỉnh)", "1e-3 (Cấu "
                                "hình A); 1e-4 (head)/1e-5 (backbone) Cấu "
                                "hình B — khớp đề cương"],
               ["Kích thước lô", "32 đến 64", "64 — trong khoảng dự kiến"],
               ["Số epoch", "Tối đa 50–100, dừng sớm theo EER validation",
                                "Tối đa 100, patience 10 (sau 5 epoch khởi "
                                "động), dừng thật ở epoch 14–21 mỗi mức "
                                "margin — khớp đề cương"],
               ["Tăng cường dữ liệu", "Xoay ±5°, dịch chuyển, co giãn nhẹ, "
                                "nhiễu nhẹ, không lật ngang", "Đã cài đặt và "
                                "bật đúng như dự kiến (rotation ≤5°, "
                                "translate/scale jitter ±5%, Gaussian noise "
                                "σ=0,02, không lật ngang) — khớp đề cương"],
               ["Chọn ngưỡng τ", "Trên validation (EER hoặc Accuracy cao "
                                "nhất), cố định khi kiểm thử", "Trên "
                                "validation theo EER, đóng băng khi kiểm "
                                "thử — khớp đề cương"],
           ], col_widths_cm=[4, 6, 6], caption="Thiết lập huấn luyện: dự kiến so với thực tế đã dùng",
           caption_num=next_table(), source="Nguồn: đề cương chi tiết và kết quả thực nghiệm của đồ án")
add_para(doc, (
    "Toàn bộ huấn luyện thực tế chạy trên CPU (đề cương dự kiến dùng GPU "
    "miễn phí Google Colab/Kaggle — mục 6.5 đề cương — nhưng môi trường "
    "thực thi cuối cùng không có GPU khả dụng); đây là khác biệt lớn nhất "
    "so với kế hoạch ban đầu, kéo theo việc phải rút gọn một số thí nghiệm "
    "mở rộng (T4, T6, T8 — xem mục 4.2)."
))

add_heading(doc, "3.5. Công cụ và môi trường", level=2)
add_para(doc, (
    "Ngôn ngữ Python; thư viện PyTorch (mô hình), OpenCV và scikit-image "
    "(xử lý ảnh), scikit-learn (SVM, độ đo), NumPy và Matplotlib (tính "
    "toán, vẽ biểu đồ); Streamlit cho chương trình demo (đề cương đề xuất "
    "\"Streamlit hoặc Gradio\" — đồ án chọn Streamlit). Mã nguồn quản lý "
    "bằng Git."
))

add_page_break(doc)

# ===========================================================================
# CHƯƠNG 4 — THỰC NGHIỆM VÀ ĐÁNH GIÁ
# ===========================================================================
start_chapter(4)
add_heading(doc, "CHƯƠNG 4. THỰC NGHIỆM VÀ ĐÁNH GIÁ", level=1)
chapter_byline(doc)
add_para(doc, (
    "Toàn bộ số liệu trong chương này là kết quả thật (không mô phỏng), "
    "thu được từ các lần chạy huấn luyện và đánh giá trên tập test CEDAR "
    "và tập BHSig260. Ngưỡng τ của mỗi mô hình luôn được chọn trên tập "
    "validation riêng của mô hình đó theo tiêu chí EER, sau đó đóng băng "
    "và áp dụng nguyên vẹn lên tập test/BHSig260."
))

add_heading(doc, "4.1. Cách chia dữ liệu", level=2)
add_table(doc, ["Tập", "Số người ký (thực tế đã dùng)", "Vai trò"],
           [
               ["Huấn luyện", 40, "Huấn luyện mô hình"],
               ["Validation", 5, "Chọn siêu tham số, dừng sớm, chọn ngưỡng τ"],
               ["Kiểm thử", 10, "Đánh giá cuối cùng, dùng một lần cho mỗi "
                                 "cấu hình đã chốt"],
           ], col_widths_cm=[4, 6, 6], caption="Cách chia dữ liệu trên bộ CEDAR (55 người ký)",
           caption_num=next_table(), source="Nguồn: kết quả thực nghiệm của đồ án")
add_para(doc, (
    "Số người ký thực tế khớp hoàn toàn với đề xuất trong đề cương "
    "(40/5/10). Đề cương còn đề xuất lặp lại các thí nghiệm chính với ít "
    "nhất 3 cách chia người ký khác nhau và báo cáo trung bình kèm độ lệch "
    "chuẩn (mục 7.1 đề cương); do giới hạn thời gian huấn luyện trên CPU, "
    "đồ án chỉ chạy được một cách chia duy nhất — đây là một khác biệt so "
    "với đề cương, được ghi nhận ở mục 4.8 và phần Kết luận."
))

add_heading(doc, "4.2. Các thí nghiệm đã thực hiện", level=2)
add_para(doc, "Đối chiếu với danh sách thí nghiệm T1–T8 đề xuất trong đề cương:")
add_table(doc, ["Mã", "Mục đích", "Trạng thái thực tế"],
           [
               ["T1", "Mốc so sánh (HOG + SVM trên CEDAR)", "Hoàn thành đầy đủ"],
               ["T2", "Mô hình chính A (Siamese CNN từ đầu trên CEDAR)", "Hoàn thành đầy đủ (cả 3 mức margin)"],
               ["T3", "Mô hình chính B (Siamese ResNet18 trên CEDAR)", "Hoàn thành 2/3 mức margin — mất margin=2,0 do container tính toán khởi động lại giữa chừng, không phục hồi được"],
               ["T4", "Ảnh hưởng của tiền xử lý (nhị phân hoá, kích thước ảnh)", "Chưa thực hiện — thiếu thời gian trên CPU"],
               ["T5", "Ảnh hưởng của huấn luyện (tăng cường dữ liệu, margin)", "Một phần: đã khảo sát 3 mức margin cho cả 2 cấu hình; chưa chạy so sánh riêng có/không tăng cường dữ liệu"],
               ["T6", "So sánh hàm mất mát (contrastive và triplet)", "Chưa thực hiện — thí nghiệm bổ sung tùy chọn theo đề cương"],
               ["T7", "Khả năng tổng quát (huấn luyện CEDAR, kiểm thử BHSig260 zero-shot)", "Hoàn thành đầy đủ (Cấu hình A và baseline)"],
               ["T8", "Mẫu tự thu thập (tùy chọn)", "Chưa thực hiện — thí nghiệm tùy chọn theo đề cương"],
           ], col_widths_cm=[2, 7, 7], caption="Danh sách thí nghiệm T1–T8: kết quả thực tế",
           caption_num=next_table(), source="Nguồn: đối chiếu đề cương chi tiết và kết quả thực nghiệm của đồ án")
add_para(doc, (
    "Theo đề cương, T1–T5 và T7 là bắt buộc, T6 và T8 chỉ làm khi còn thời "
    "gian. Đồ án hoàn thành đầy đủ T1, T2, T7 và một phần lớn T3 (2/3 "
    "margin, không phải lỗi thiết kế mà do sự cố hạ tầng tính toán ngoài "
    "kiểm soát — xem mục 4.8), hoàn thành một phần T5 (margin, chưa "
    "augmentation on/off); T4 — một thí nghiệm BẮT BUỘC theo đề cương — "
    "chưa kịp thực hiện, là hạn chế lớn nhất so với kế hoạch ban đầu và "
    "được ghi nhận trung thực ở đây thay vì bỏ qua."
))

add_heading(doc, "4.3. Kết quả tổng thể trên tập test CEDAR", level=2)
add_table(doc, ["Mô hình", "τ", "Accuracy", "FAR", "FRR", "AUC", "EER (val, toàn bộ loại cặp)"],
           [
               ["Baseline HOG+SVM (T1)", "0,1388", "78,50%", "23,50%", "19,50%", "0,887", "—"],
               ["Cấu hình A (T2, margin=1,0)", "0,2471", "84,63%", "20,25%", "10,50%", "0,915", "9,75%"],
               ["Cấu hình B (T3, margin=1,0)", "0,4763", "87,88%", "7,75%", "16,50%", "0,955", "5,50%"],
           ], col_widths_cm=[6, 3, 3, 3, 3, 3, 4],
           caption="Kết quả tổng thể trên tập test CEDAR (800 cặp)",
           caption_num=next_table(), source="Nguồn: kết quả thực nghiệm của đồ án")
add_para(doc, (
    "Lưu ý về chỉ tiêu đề xuất (Bảng 9 đề cương, \"EER trên tập kiểm thử "
    "CEDAR — giả mạo chuyên nghiệp — không quá 5%\"): giá trị EER 5,50% "
    "(Cấu hình B) ở bảng trên được tính trên TOÀN BỘ tập validation (gồm "
    "cả cặp genuine-genuine, skilled và random forgery trộn lẫn), KHÔNG "
    "phải EER tính riêng chỉ trên cặp giả mạo chuyên nghiệp như chỉ tiêu "
    "đề cương yêu cầu chặt chẽ. Một EER riêng cho skilled-forgery-only "
    "chưa được tính tách biệt trong lần chạy này. Kết quả gần nhất có thể "
    "dùng để suy luận là AUC skilled forgery của Cấu hình B đạt 0,984 (FAR "
    "2,50% — BẢNG 4.6), cho thấy khả năng cao là EER riêng cho skilled "
    "forgery sẽ thấp hơn 5,50% nói trên, nhưng đây KHÔNG được xem là số đo "
    "chính thức đạt chỉ tiêu; việc tính EER tách riêng theo đúng định "
    "nghĩa chỉ tiêu là một việc còn thiếu, nêu ở mục 4.8 và phần Kết luận."
))

add_heading(doc, "4.4. Kết quả phân theo loại giả mạo", level=2)
add_table(doc, ["Loại giả mạo", "Accuracy", "FAR", "FRR", "AUC"],
           [
               ["Skilled forgery", "92,67%", "1,00%", "10,50%", "0,997"],
               ["Random forgery", "79,83%", "39,50%", "10,50%", "0,834"],
           ], col_widths_cm=[6, 4, 4, 4, 4],
           caption="Kết quả phân theo loại giả mạo — Cấu hình A (T2)",
           caption_num=next_table(), source="Nguồn: kết quả thực nghiệm của đồ án")
add_table(doc, ["Loại giả mạo", "Accuracy", "FAR", "FRR", "AUC"],
           [
               ["Skilled forgery", "88,17%", "2,50%", "16,50%", "0,984"],
               ["Random forgery", "84,67%", "13,00%", "16,50%", "0,927"],
           ], col_widths_cm=[6, 4, 4, 4, 4],
           caption="Kết quả phân theo loại giả mạo — Cấu hình B (T3)",
           caption_num=next_table(), source="Nguồn: kết quả thực nghiệm của đồ án")
add_para(doc, (
    "Kết quả đáng chú ý nhất của toàn bộ thực nghiệm: cả hai cấu hình đều "
    "phân biệt skilled forgery gần như hoàn hảo (AUC 0,997 và 0,984) nhưng "
    "gặp khó khăn rõ rệt hơn hẳn với random forgery (AUC 0,834 và 0,927) — "
    "NGƯỢC với trực giác thông thường rằng giả mạo có kỹ năng cao khó phân "
    "biệt hơn giả mạo ngẫu nhiên. Cách đọc hợp lý nhất từ phân tích định "
    "tính (mục 4.6): các chữ ký giả trong CEDAR có nét bút thiếu tự nhiên "
    "khá đặc trưng, dễ phân biệt ở mức thô với nét bút thật; trong khi đó, "
    "hai người viết thật khác nhau đôi khi có \"gestalt\" chữ ký tổng thể "
    "(độ nghiêng, mật độ nét, tỉ lệ khung) tương tự nhau, dễ gây nhầm lẫn "
    "hơn. Cấu hình B cải thiện mạnh nhất đúng vào điểm yếu này của Cấu "
    "hình A: FAR random forgery giảm từ 39,50% xuống 13,00% (giảm hơn "
    "2/3), trong khi FAR skilled forgery chỉ tăng nhẹ từ 1,00% lên 2,50% "
    "— một sự đánh đổi rất thuận lợi."
))
add_table(doc, ["Chỉ số", "Cấu hình A", "Cấu hình B", "Chênh lệch"],
           [
               ["AUC tổng thể", "0,915", "0,955", "+0,040"],
               ["FAR random forgery", "39,50%", "13,00%", "−26,50 điểm %"],
               ["AUC random forgery", "0,834", "0,927", "+0,093"],
               ["FAR skilled forgery", "1,00%", "2,50%", "+1,50 điểm %"],
               ["AUC skilled forgery", "0,997", "0,984", "−0,013"],
               ["EER validation (toàn bộ loại cặp)", "9,75%", "5,50%", "−4,25 điểm %"],
           ], col_widths_cm=[6, 4, 4, 4],
           caption="So sánh Cấu hình A và Cấu hình B theo loại giả mạo",
           caption_num=next_table(), source="Nguồn: kết quả thực nghiệm của đồ án")

add_heading(doc, "4.5. Đường cong ROC", level=2)
add_image(doc, f"{RES}/baseline/roc.png", width_cm=13,
          caption="Đường cong ROC — baseline HOG + SVM (T1)",
          caption_num=next_fig(), source="Nguồn: kết quả thực nghiệm của đồ án")
add_image(doc, f"{RES}/config_a/roc.png", width_cm=13,
          caption="Đường cong ROC — Cấu hình A (T2)",
          caption_num=next_fig(), source="Nguồn: kết quả thực nghiệm của đồ án")
add_image(doc, f"{RES}/config_b/roc.png", width_cm=13,
          caption="Đường cong ROC — Cấu hình B (T3)",
          caption_num=next_fig(), source="Nguồn: kết quả thực nghiệm của đồ án")

add_heading(doc, "4.6. Phân tích định tính các ca lỗi", level=2)
add_para(doc, (
    "Hình dưới đây minh hoạ một ca chấp nhận nhầm (false accept) điển "
    "hình ở random forgery của Cấu hình A: cặp chữ ký của hai người hoàn "
    "toàn khác nhau về nội dung tên (\"Melissa N. Dumble\" và \"Rrand R. "
    "Co\") nhưng có khoảng cách D rất nhỏ so với τ=0,2471. Cả hai chữ ký "
    "có nét gạch ngang/uốn lượn kéo dài đặc trưng phía trên chữ và độ "
    "nghiêng cursive tương tự nhau — mô hình dường như học mạnh các đặc "
    "trưng hình dạng tổng thể hơn là chi tiết nhận dạng nét chữ riêng của "
    "từng người."
))
add_image(doc, f"{EA}/cedar_test/random_forgery_false_accept_006.png", width_cm=13,
          caption="Ca lỗi false-accept, giả mạo ngẫu nhiên, Cấu hình A",
          caption_num=next_fig(), source="Nguồn: trích xuất từ predictions_test.csv của đồ án")
add_para(doc, (
    "Hình dưới minh hoạ một ca từ chối nhầm (false reject) ở cặp "
    "genuine-genuine: hai chữ ký của cùng một người nhưng D cao hơn τ, do "
    "biến thiên tự nhiên trong cách ký của chính người đó giữa các lần ký "
    "khác nhau mà mô hình dừng sớm ở epoch 18 chưa học đủ để dung nạp."
))
add_image(doc, f"{EA}/cedar_test/genuine_genuine_false_reject_000.png", width_cm=13,
          caption="Ca lỗi false-reject, cùng người ký, Cấu hình A",
          caption_num=next_fig(), source="Nguồn: trích xuất từ predictions_test.csv của đồ án")
add_para(doc, (
    "Hình dưới minh hoạ ca chấp nhận nhầm hiếm gặp ở skilled forgery "
    "(D=0,1938, sát dưới τ=0,2471): cả hai chữ ký (thật và giả) đều có "
    "nét nghiêng chéo và các vòng loop lặp lại theo cùng một hướng — hoạ "
    "tiết hình học tổng thể giống nhau đủ để \"đánh lừa\" mô hình dù đây "
    "là chữ ký giả."
))
add_image(doc, f"{EA}/cedar_test/skilled_forgery_false_accept_012.png", width_cm=13,
          caption="Ca lỗi false-accept, giả mạo kỹ năng cao, Cấu hình A",
          caption_num=next_fig(), source="Nguồn: trích xuất từ predictions_test.csv của đồ án")
add_para(doc, (
    "So sánh Cấu hình A và Cấu hình B trên cùng loại lỗi: hình dưới cho "
    "thấy Cấu hình B vẫn mắc cùng loại lỗi random-forgery đã quan sát ở "
    "Cấu hình A (nhầm hai người khác nhau, \"Glorimar Vicente\" và "
    "\"Melissa N. Dumble\") — nhưng với D=0,3247 gần τ=0,4763 hơn (tỉ lệ "
    "D/τ ≈ 0,68) so với ca tương ứng ở Cấu hình A (tỉ lệ D/τ ≈ 0,05–0,08). "
    "Nói cách khác, Cấu hình B vẫn mắc cùng loại lỗi định tính nhưng \"tự "
    "tin sai\" ít hơn nhiều — đặc trưng pretrained ImageNet của ResNet18 "
    "tổng quát hoá tốt hơn CNN train-from-scratch trên tập chỉ 40 người "
    "ký."
))
add_image(doc, f"{EA}/cedar_test_config_b/random_forgery_false_accept_004.png", width_cm=13,
          caption="Ca lỗi false-accept, giả mạo ngẫu nhiên, Cấu hình B (so sánh)",
          caption_num=next_fig(), source="Nguồn: trích xuất từ predictions_test.csv của đồ án")

add_heading(doc, "4.7. Đánh giá tổng quát hoá zero-shot trên BHSig260 (T7)", level=2)
add_para(doc, (
    "Mô hình Cấu hình A huấn luyện trên CEDAR được áp thẳng lên BHSig260 "
    "KHÔNG tinh chỉnh lại, dùng nguyên ngưỡng τ đã đóng băng từ CEDAR "
    "validation — phép thử trực tiếp nhất cho tuyên bố writer-independent "
    "tổng quát hoá ngoài miền dữ liệu, đúng tinh thần thí nghiệm T7:"
))
add_table(doc, ["Mô hình", "Loại giả mạo", "FAR", "FRR", "AUC", "Đạt chỉ tiêu EER≤20%?"],
           [
               ["Cấu hình A (Siamese)", "Skilled forgery", "19,77%", "44,31%", "0,752", "Chưa đạt"],
               ["Cấu hình A (Siamese)", "Random forgery", "9,69%", "44,31%", "0,852", "—"],
               ["Baseline HOG+SVM", "Skilled forgery", "41,85%", "21,65%", "0,767", "Chưa đạt"],
               ["Baseline HOG+SVM", "Random forgery", "5,69%", "21,65%", "0,923", "—"],
           ], col_widths_cm=[5, 4, 3, 3, 3, 4],
           caption="Kết quả zero-shot trên BHSig260 (T7): Cấu hình A và baseline",
           caption_num=next_table(), source="Nguồn: kết quả thực nghiệm của đồ án")
add_para(doc, (
    "Cả hai mô hình chưa đạt chỉ tiêu EER≤20% đề ra ban đầu, nhưng AUC vẫn "
    "ở mức 0,75–0,92 — cao hơn hẳn ngẫu nhiên — cho thấy embedding học "
    "được vẫn giữ tín hiệu phân biệt nhất định dù khác hoàn toàn ngôn "
    "ngữ/hệ chữ viết. Cấu hình B chưa được đo zero-shot trên BHSig260 "
    "trong phạm vi đồ án này (chỉ Cấu hình A và baseline được chạy T7) — "
    "nêu ở mục 4.8 như một việc còn thiếu."
))
add_para(doc, (
    "Hình dưới minh hoạ ca từ chối nhầm nghiêm trọng nhất quan sát được: "
    "hai chữ ký \"sandeep\" (chữ Devanagari) của cùng một người, nhìn ảnh "
    "gốc khá giống nhau, nhưng D=1,9224 — cao gấp gần 8 lần τ=0,2471 lấy "
    "từ CEDAR. Ảnh đã qua tiền xử lý cho thấy ảnh A hiện ra đậm/dày nét "
    "hẳn so với ảnh B mảnh/nhạt — dấu hiệu lệch miền (domain shift) ở khâu "
    "tiền xử lý: tham số khử nhiễu/ngưỡng Otsu được ngầm phù hợp với đặc "
    "điểm ảnh scan CEDAR, không chuyển đổi tốt sang định dạng/độ tương "
    "phản khác của ảnh BHSig260."
))
add_image(doc, f"{EA}/bhsig260/genuine_genuine_false_reject_000.png", width_cm=13,
          caption="Ca lỗi false-reject nghiêm trọng trên BHSig260 (lệch miền tiền xử lý)",
          caption_num=next_fig(), source="Nguồn: trích xuất từ predictions_bhsig260.csv của đồ án")
add_image(doc, f"{EA}/bhsig260/skilled_forgery_false_accept_008.png", width_cm=13,
          caption="Ca lỗi false-accept giả mạo kỹ năng cao trên BHSig260",
          caption_num=next_fig(), source="Nguồn: trích xuất từ predictions_bhsig260.csv của đồ án")

add_heading(doc, "4.8. Thảo luận", level=2)
add_para(doc, "So với các rủi ro đã nêu trước trong đề cương (mục 7.4):")
add_table(doc, ["Rủi ro đã dự kiến", "Có xảy ra không", "Xử lý thực tế"],
           [
               ["Ít người ký nên mô hình dễ học vẹt", "Có, một phần — quan "
                    "sát được ở lỗi random-forgery (mục 4.4, 4.6)", "Đã dùng "
                    "tăng cường dữ liệu, dừng sớm, học chuyển giao (Cấu hình "
                    "B cải thiện rõ rệt); kiểm tra thêm trên BHSig260 (T7)"],
               ["Không tải được bộ dữ liệu thứ hai đúng hạn", "Không xảy ra",
                    "BHSig260 tải và dùng được đúng kế hoạch"],
               ["Thời gian huấn luyện lâu, giới hạn GPU miễn phí", "Có, "
                    "nghiêm trọng hơn dự kiến — không có GPU khả dụng, phải "
                    "chạy hoàn toàn trên CPU", "Dùng checkpoint theo từng "
                    "mức margin (không có trong kế hoạch gốc, bổ sung sau "
                    "khi thấy cần); vẫn không đủ thời gian cho T4, T6, T8"],
               ["Kết quả khó tái lập", "Một sự cố liên quan xảy ra: seed chỉ "
                    "gieo một lần đầu script thay vì gieo lại mỗi mức margin "
                    "ở lần chạy đầu tiên", "Phát hiện và sửa lỗi (gieo lại "
                    "seed mỗi margin) cho các lần chạy sau; ghi nhận minh "
                    "bạch trong Phụ lục"],
           ], col_widths_cm=[5, 4, 7], caption="Rủi ro đã dự kiến so với thực tế xảy ra",
           caption_num=next_table(), source="Nguồn: đối chiếu đề cương chi tiết và thực tế thực hiện đồ án")
add_para(doc, (
    "Một rủi ro KHÔNG có trong danh sách dự kiến ban đầu cũng đã xảy ra "
    "thực tế: môi trường tính toán (container) bị khởi động lại giữa "
    "chừng khi đang huấn luyện mức margin=2,0 của Cấu hình B, làm mất kết "
    "quả của mức margin này (không phục hồi được). Nhờ cơ chế checkpoint "
    "theo từng margin, 2/3 mức margin đã hoàn thành vẫn được giữ lại và "
    "dùng làm kết quả cuối cùng thay vì phải huấn luyện lại từ đầu."
))
add_para(doc, (
    "Tổng kết mức đạt chỉ tiêu định lượng đề xuất (Bảng 9 đề cương): chỉ "
    "tiêu EER≤5% trên CEDAR skilled-forgery CHƯA được đo đúng định nghĩa "
    "(chỉ có EER trộn lẫn mọi loại cặp = 5,50% cho Cấu hình B — xem lưu ý "
    "ở mục 4.3); chỉ tiêu EER≤20% trên BHSig260 skilled-forgery CHƯA đạt "
    "(19,77% FAR / 44,31% FRR cho Cấu hình A, một phép đo gần nhưng không "
    "tương đương EER); chỉ tiêu \"EER Siamese thấp hơn baseline\" đã ĐẠT "
    "một cách nhất quán trên cả AUC tổng thể và AUC theo từng loại giả "
    "mạo, ở cả hai bộ dữ liệu; chỉ tiêu \"kiểm tra chéo giữa các bộ dữ "
    "liệu có phân tích nguyên nhân chênh lệch\" đã ĐẠT (mục 4.7, phân tích "
    "lệch miền tiền xử lý)."
))

add_page_break(doc)

# ===========================================================================
# CHƯƠNG 5 — CHƯƠNG TRÌNH DEMO
# ===========================================================================
start_chapter(5)
add_heading(doc, "CHƯƠNG 5. CHƯƠNG TRÌNH DEMO", level=1)
chapter_byline(doc)
add_para(doc, (
    "Chương trình demo là một ứng dụng web nhỏ, chạy trên máy cá nhân, "
    "cho phép kiểm tra một cặp chữ ký và quan sát ảnh hưởng của ngưỡng "
    "quyết định, đúng như thiết kế đề ra trong đề cương (mục 8)."
))

add_heading(doc, "5.1. Chức năng", level=2)
add_bullet(doc, "Tải lên ảnh chữ ký mẫu (thật) và một ảnh chữ ký cần kiểm "
                "tra.")
add_bullet(doc, "Hiển thị ảnh gốc và ảnh sau tiền xử lý để người dùng "
                "thấy hệ thống đang \"nhìn\" gì.")
add_bullet(doc, "Trả về kết quả thật hoặc giả, kèm khoảng cách D giữa hai "
                "embedding.")
add_bullet(doc, "Thanh trượt ngưỡng τ: khi người dùng kéo, kết quả thay "
                "đổi theo, minh họa sự đánh đổi giữa FAR và FRR.")

add_heading(doc, "5.2. Luồng sử dụng", level=2)
add_bullet(doc, "Người dùng mở ứng dụng và tải lên chữ ký mẫu.")
add_bullet(doc, "Người dùng tải lên chữ ký cần kiểm tra.")
add_bullet(doc, "Ứng dụng tiền xử lý hai ảnh, đưa qua mô hình đã huấn "
                "luyện (Cấu hình B) và tính khoảng cách D.")
add_bullet(doc, "Ứng dụng so D với ngưỡng τ, hiển thị kết quả và điểm "
                "tương đồng.")

add_heading(doc, "5.3. Kiến trúc và công cụ", level=2)
add_table(doc, ["Thành phần", "Nhiệm vụ", "Công cụ"],
           [
               ["Giao diện", "Nhận ảnh, hiển thị kết quả, thanh trượt "
                              "ngưỡng", "Streamlit"],
               ["Mô-đun tiền xử lý", "Dùng chung mã với lúc huấn luyện để "
                              "tránh lệch (train-serving skew)", "OpenCV, "
                              "NumPy"],
               ["Mô-đun mô hình", "Tải checkpoint tốt nhất, tính embedding "
                              "và khoảng cách", "PyTorch"],
           ], col_widths_cm=[4, 7, 5], caption="Kiến trúc và công cụ của chương trình demo",
           caption_num=next_table(), source="Nguồn: tự tổng hợp từ mã nguồn app/ của đồ án")
add_para(doc, (
    "Ảnh người dùng tải lên chỉ được xử lý trong bộ nhớ và không lưu lại "
    "xuống đĩa ở bất kỳ bước nào, vì chữ ký là dữ liệu cá nhân — đúng yêu "
    "cầu thiết kế nêu trong đề cương (mục 8.3)."
))

add_heading(doc, "5.4. Kết quả trình diễn", level=2)
add_para(doc, (
    "Hình dưới là ảnh chụp màn hình thực tế của ứng dụng, sử dụng mô hình "
    "Cấu hình B đã huấn luyện, thử nghiệm với ảnh chữ ký thật lấy từ người "
    "ký #2 trong tập test CEDAR (chưa từng xuất hiện trong tập train/"
    "validation)."
))
add_image(doc, f"{SCR}/demo_empty.png", width_cm=13,
          caption="Giao diện demo Streamlit — trạng thái ban đầu",
          caption_num=next_fig(), source="Nguồn: ảnh chụp màn hình ứng dụng demo của đồ án")
add_image(doc, f"{SCR}/demo_genuine.png", width_cm=13,
          caption="Giao diện demo Streamlit — kết quả với cặp chữ ký thật",
          caption_num=next_fig(), source="Nguồn: ảnh chụp màn hình ứng dụng demo của đồ án")
add_image(doc, f"{SCR}/demo_forged.png", width_cm=13,
          caption="Giao diện demo Streamlit — kết quả với cặp chữ ký giả",
          caption_num=next_fig(), source="Nguồn: ảnh chụp màn hình ứng dụng demo của đồ án")
add_para(doc, (
    "Cả hai trường hợp thử nghiệm thật (cặp chữ ký thật và cặp chữ ký "
    "giả) đều được ứng dụng phân loại đúng, khớp với nhãn thật của dữ "
    "liệu test, minh chứng rằng mô hình đã huấn luyện hoạt động đúng khi "
    "triển khai qua giao diện người dùng thực tế, không chỉ trên script "
    "đánh giá offline. Việc chuẩn bị các cặp mẫu cố định lấy từ tập kiểm "
    "thử để trình diễn khi bảo vệ (mục 8.4 đề cương) có thể thực hiện "
    "trực tiếp bằng các ảnh test đã có sẵn trong `data/splits/test_pairs."
    "csv`."
))

add_page_break(doc)

# ===========================================================================
# KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN (không đánh số chương, giống Lời mở đầu)
# ===========================================================================
add_heading(doc, "KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", level=1, center=True)

add_heading(doc, "1. Kết quả đạt được", level=2)
add_bullet(doc, "Xây dựng hoàn chỉnh một hệ thống xác minh chữ ký offline "
                "writer-independent, từ tiền xử lý ảnh, sinh cặp dữ liệu "
                "writer-disjoint, huấn luyện, đến đánh giá và demo tương "
                "tác — toàn bộ chạy trên dữ liệu thật (CEDAR, BHSig260).")
add_bullet(doc, "Hoàn thành đầy đủ T1 (baseline), T2 (Cấu hình A), phần "
                "lớn T3 (Cấu hình B, 2/3 margin) và T7 (kiểm tra chéo "
                "BHSig260) trong 8 thí nghiệm đề ra ở đề cương.")
add_bullet(doc, "Cấu hình B (học chuyển giao ResNet18) đạt AUC 0,955 trên "
                "tập test CEDAR, vượt Cấu hình A (AUC 0,915) và baseline "
                "HOG+SVM (AUC 0,887), cải thiện rõ rệt nhất ở khả năng "
                "chống giả mạo ngẫu nhiên (FAR giảm từ 39,5% xuống 13,0%).")
add_bullet(doc, "Phát hiện định tính đáng chú ý: cả hai mô hình học sâu "
                "phân biệt giả mạo kỹ năng cao tốt hơn hẳn giả mạo ngẫu "
                "nhiên — ngược trực giác thông thường — do xu hướng học "
                "đặc trưng hình dạng/độ nghiêng tổng thể trước chi tiết "
                "danh tính từng người ký.")
add_bullet(doc, "Đánh giá zero-shot trên BHSig260 (T7) cho thấy mô hình "
                "vẫn giữ tín hiệu phân biệt có ý nghĩa (AUC 0,75–0,92) qua "
                "một hệ chữ viết hoàn toàn khác; nguyên nhân khả dĩ (lệch "
                "miền ở khâu tiền xử lý) đã được xác định qua phân tích "
                "định tính trực tiếp trên ảnh lỗi thật.")

add_heading(doc, "2. Hạn chế", level=2)
add_bullet(doc, "T4 (ảnh hưởng tiền xử lý) — thí nghiệm BẮT BUỘC theo đề "
                "cương — chưa thực hiện do giới hạn thời gian trên CPU.")
add_bullet(doc, "T5 chỉ hoàn thành một phần: đã khảo sát margin, chưa "
                "khảo sát riêng tác động của tăng cường dữ liệu.")
add_bullet(doc, "T6 (triplet loss) và T8 (mẫu tự thu thập) — hai thí "
                "nghiệm tùy chọn theo đề cương — chưa thực hiện.")
add_bullet(doc, "Cấu hình B chưa hoàn thành huấn luyện đầy đủ ở mức "
                "margin=2,0 do sự cố khởi động lại môi trường tính toán "
                "giữa chừng.")
add_bullet(doc, "Chưa lặp lại thí nghiệm với ít nhất 3 cách chia người ký "
                "khác nhau như đề cương đề xuất (mục 7.1), nên chưa có ước "
                "lượng độ lệch chuẩn của kết quả.")
add_bullet(doc, "EER dùng để đối chiếu với chỉ tiêu định lượng (Bảng 9 đề "
                "cương) hiện được tính trên toàn bộ loại cặp trộn lẫn, "
                "chưa tính riêng cho skilled-forgery-only như định nghĩa "
                "chỉ tiêu yêu cầu chặt chẽ; Cấu hình B chưa được đo "
                "zero-shot trên BHSig260 (chỉ Cấu hình A và baseline).")
add_bullet(doc, "Toàn bộ huấn luyện thực hiện trên CPU, giới hạn quy mô "
                "thực nghiệm có thể thực hiện được trong thời gian cho "
                "phép.")

add_heading(doc, "3. Hướng phát triển", level=2)
add_bullet(doc, "Hoàn thành T4 (ảnh hưởng tiền xử lý: nhị phân hoá đầu "
                "ra, kích thước ảnh) và phần còn lại của T5 (tăng cường dữ "
                "liệu bật/tắt) trên GPU.")
add_bullet(doc, "Hoàn thành huấn luyện Cấu hình B ở mức margin=2,0 (lý "
                "tưởng là chạy lại cả 3 mức với seed sạch mỗi mức).")
add_bullet(doc, "Tính riêng EER cho tập con skilled-forgery-only để đối "
                "chiếu đúng định nghĩa với chỉ tiêu đề xuất ban đầu (Bảng "
                "9 đề cương), và đo zero-shot BHSig260 cho Cấu hình B.")
add_bullet(doc, "Thử nghiệm T6 (triplet loss, công thức đã trình bày ở "
                "mục 2.4) và T8 (thu thập một tập mẫu chữ ký người Việt "
                "nhỏ, có sự đồng ý của người ký).")
add_bullet(doc, "Lặp lại các thí nghiệm chính với ít nhất 3 cách chia "
                "người ký khác nhau để báo cáo trung bình kèm độ lệch "
                "chuẩn, như đề cương đã đề xuất.")
add_bullet(doc, "Chuẩn hoá bước tiền xử lý bất biến hơn với độ phân giải/"
                "độ tương phản nguồn, nhằm giảm phần lệch miền quan sát "
                "được khi đánh giá trên BHSig260.")
add_bullet(doc, "Các hướng mở rộng dài hạn khác theo đề cương: mở rộng "
                "sang chữ ký online, thử các kiến trúc mới hơn (ví dụ mô "
                "hình dựa trên attention), bổ sung tập chữ ký người Việt, "
                "và tăng khả năng chống lại ảnh in hoặc photocopy.")

add_page_break(doc)

# ===========================================================================
# PHỤ LỤC (theo biểu mẫu, đặt trước Tài liệu tham khảo)
# ===========================================================================
add_heading(doc, "PHỤ LỤC", level=1, center=True)

add_heading(doc, "Phụ lục A. Cấu trúc mã nguồn", level=2)
add_bullet(doc, "src/sigverify/preprocessing/ — pipeline.py (tiền xử lý), "
                "datasets.py (đọc CEDAR/BHSig260), augment.py (tăng cường "
                "dữ liệu: rotation ≤5°, translate/scale jitter, Gaussian "
                "noise, không lật ngang — khớp Bảng thiết lập huấn luyện "
                "trong đề cương).")
add_bullet(doc, "src/sigverify/pairs/ — generator.py (sinh cặp genuine/"
                "skilled/random), splits.py (chia writer-disjoint).")
add_bullet(doc, "src/sigverify/models/ — siamese_scratch.py (Cấu hình A), "
                "siamese_transfer.py (Cấu hình B), losses.py (contrastive "
                "loss).")
add_bullet(doc, "src/sigverify/training/train_siamese.py — vòng lặp huấn "
                "luyện dùng chung cho cả hai cấu hình.")
add_bullet(doc, "src/sigverify/evaluation/metrics.py — FAR/FRR/EER, chọn "
                "ngưỡng trên validation, đánh giá đóng băng trên test.")
add_bullet(doc, "scripts/train_config_a.py, train_config_b.py — script "
                "huấn luyện đầy đủ, có checkpoint theo từng margin.")
add_bullet(doc, "scripts/run_ablations.py, configs/ablation_variants/ — "
                "mã nguồn cho T4/T5 đã viết sẵn nhưng CHƯA chạy với dữ "
                "liệu thật (xem mục 4.2, Chương 4).")
add_bullet(doc, "scripts/error_analysis.py — trích xuất và phân tích các "
                "ca lỗi định tính.")
add_bullet(doc, "app/demo_app.py, app/inference.py — ứng dụng demo "
                "Streamlit (Chương 5).")

add_heading(doc, "Phụ lục B. Cấu hình siêu tham số đầy đủ (default.yaml)", level=2)
for line in [
    "seed: 42",
    "image.size_scratch: [220, 150]   (Cấu hình A)",
    "image.size_transfer: [224, 224]  (Cấu hình B)",
    "preprocessing.denoise: gaussian",
    "preprocessing.binarize_output: false",
    "pairs.ratio_pos_hardneg_easyneg: [2, 1, 1]",
    "pairs.pairs_per_writer: 40",
    "split.train_writers / val_writers / test_writers: 40 / 5 / 10",
    "train.batch_size: 64",
    "train.max_epochs: 100",
    "train.early_stop_patience: 10  (warmup 5 epoch)",
    "train.margins: [0.5, 1.0, 2.0]",
    "model.embedding_dim: 128",
    "model.transfer_backbone: resnet18",
]:
    add_para(doc, line, size=12)

add_heading(doc, "Phụ lục C. Ghi chú minh bạch về phương pháp luận", level=2)
add_para(doc, (
    "Trong lần chạy huấn luyện đầy đủ đầu tiên, seed ngẫu nhiên chỉ được "
    "gieo một lần ở đầu script thay vì gieo lại cho từng mức margin, "
    "khiến các mức margin 1,0 và 2,0 kế thừa một phần trạng thái ngẫu "
    "nhiên còn lại từ mức margin trước đó. Lỗi này đã được phát hiện và "
    "sửa (gieo lại seed trước mỗi mức margin) trong scripts/"
    "train_config_a.py và scripts/train_config_b.py cho các lần chạy sau; "
    "số liệu trình bày trong Chương 4 vẫn là kết quả thật hợp lệ, chỉ nên "
    "đọc phần so sánh GIỮA CÁC MỨC MARGIN của cùng một cấu hình với mức "
    "thận trọng vừa phải — phép so sánh GIỮA HAI CẤU HÌNH A và B (ở mức "
    "margin=1,0, cả hai đều đã dùng quy trình seed đã sửa) không bị ảnh "
    "hưởng bởi hạn chế này."
))
add_para(doc, (
    "Mức margin=2,0 của Cấu hình B không hoàn thành huấn luyện do môi "
    "trường tính toán bị khởi động lại giữa chừng và không thể khôi phục "
    "lại từ điểm dừng — đây là hạn chế thực tế của hạ tầng thực nghiệm, "
    "không phải lựa chọn thiết kế, và được ghi nhận minh bạch thay vì "
    "thay thế bằng số liệu ước lượng hay giả định."
))
add_para(doc, (
    "Tiêu đề trên trang bìa của đề cương chi tiết gốc ghi \"NHẬN DẠNG CHỮ "
    "SỐ VIẾT TAY\" — không khớp với toàn bộ 12 mục nội dung của đề cương "
    "(đều nói về xác minh chữ ký viết tay). Đây được xem là lỗi đánh máy "
    "còn sót lại từ mẫu đề cương cũ (nhầm \"chữ số\" thành \"chữ ký\"); "
    "tiêu đề trên trang bìa báo cáo này đã được sửa lại cho khớp với nội "
    "dung thực tế."
))
add_para(doc, (
    f"Tên loại đồ án trên trang bìa đã đổi từ \"ĐỒ ÁN CHUYÊN NGÀNH\" (dùng "
    f"ở bản báo cáo trước) sang đúng cụm từ \"{PROJECT_TYPE}\" theo biểu "
    "mẫu chính thức của trường; tương tự, tên trường trên bìa được bổ "
    f"sung thêm dòng \"{UNIVERSITY}\" ở trên cùng (theo biểu mẫu), giữ "
    f"nguyên hai dòng \"{SCHOOL}\" / \"{FACULTY}\" đã ghi trong đề cương "
    f"chi tiết đã duyệt bên dưới, và địa danh/ngày tháng đổi từ \"Vĩnh "
    f"Long\" (dùng ở bản trước) sang \"{LOCATION}\" theo đúng biểu mẫu."
))
add_para(doc, (
    f"\"Khoá: {STUDENT_COHORT}\" và \"Ngành: {MAJOR}\" trên bìa và trên "
    "hai bản nhận xét mẫu được suy luận từ mã lớp "
    f"\"{STUDENT_CLASS}\" và tên khoa \"{FACULTY}\", và đã được sinh viên "
    "xác nhận là chính xác."
))
add_para(doc, (
    "Biểu mẫu trình bày chính thức của trường quy định danh mục tài liệu "
    "tham khảo theo kiểu tác giả-năm (xếp theo abc họ/tên tác giả, tách "
    "\"Tiếng Việt\"/\"Tiếng Anh\"), khác với định dạng IEEE đánh số [1]-"
    "[21] mà đề cương chi tiết đã duyệt của đồ án này yêu cầu rõ ràng (mục "
    "12 đề cương: \"đánh số [1] đến [21]... theo định dạng IEEE\"). Đây là "
    "hai nguồn tài liệu mâu thuẫn nhau về quy tắc này. Báo cáo GIỮ NGUYÊN "
    "định dạng IEEE theo đúng đề cương đã duyệt riêng cho đồ án này (phù "
    "hợp hơn với lĩnh vực công nghệ thông tin, và ví dụ tham khảo trong "
    "biểu mẫu chung của trường — về \"lúa lai\", kinh tế — cho thấy biểu "
    "mẫu đó vốn dùng chung cho nhiều ngành khác nhau, không chuyên biệt "
    "cho ngành công nghệ thông tin). Sinh viên đã xác nhận giữ định dạng "
    "IEEE theo đề cương chi tiết đã duyệt."
))
add_para(doc, (
    "Trang bìa cứng và bìa lót trong bản in cuối cùng thường không đánh "
    "số trang; bản .docx này đánh số La Mã liên tục bắt đầu từ trang bìa "
    "để đơn giản hoá việc dựng tài liệu tự động — khi in chính thức, sinh "
    "viên nên ẩn số trang thủ công trên hai trang bìa nếu muốn khớp tuyệt "
    "đối với quy ước thường thấy."
))

add_page_break(doc)

# ===========================================================================
# TÀI LIỆU THAM KHẢO (21 mục, đúng theo đề cương đã duyệt, định dạng IEEE --
# đặt SAU Phụ lục, đúng vị trí cuối cùng theo biểu mẫu chính thức)
# ===========================================================================
add_heading(doc, "TÀI LIỆU THAM KHẢO", level=1, center=True)
references = [
    "[1] J. Bromley, I. Guyon, Y. LeCun, E. Säckinger, and R. Shah, "
    "\"Signature verification using a 'Siamese' time delay neural "
    "network,\" in Advances in Neural Information Processing Systems, "
    "1994, pp. 737-744.",
    "[2] S. Chopra, R. Hadsell, and Y. LeCun, \"Learning a similarity "
    "metric discriminatively, with application to face verification,\" "
    "in Proc. CVPR, 2005, pp. 539-546.",
    "[3] N. Dalal and B. Triggs, \"Histograms of oriented gradients for "
    "human detection,\" in Proc. CVPR, 2005.",
    "[4] S. Dey, A. Dutta, J. I. Toledo, S. K. Ghosh, J. Lladós, and U. "
    "Pal, \"SigNet: Convolutional Siamese network for writer independent "
    "offline signature verification,\" arXiv:1707.02131, 2017.",
    "[5] M. A. Ferrer, M. Diaz-Cabrera, and A. Morales, \"Static "
    "signature synthesis: a neuromotor inspired approach for "
    "biometrics,\" IEEE Trans. Pattern Anal. Mach. Intell., vol. 37, no. "
    "3, 2015.",
    "[6] R. Hadsell, S. Chopra, and Y. LeCun, \"Dimensionality reduction "
    "by learning an invariant mapping,\" in Proc. CVPR, 2006.",
    "[7] L. G. Hafemann, R. Sabourin, and L. S. Oliveira, \"Offline "
    "handwritten signature verification: literature review,\" in Proc. "
    "IPTA, 2017. [arXiv:1507.07909]",
    "[8] L. G. Hafemann, R. Sabourin, and L. S. Oliveira, \"Learning "
    "features for offline handwritten signature verification using deep "
    "convolutional neural networks,\" Pattern Recognition, vol. 70, pp. "
    "163-176, 2017.",
    "[9] K. He, X. Zhang, S. Ren, and J. Sun, \"Deep residual learning "
    "for image recognition,\" in Proc. CVPR, 2016.",
    "[10] D. Impedovo and G. Pirlo, \"Automatic signature verification: "
    "the state of the art,\" IEEE Trans. Syst., Man, Cybern., Part C, "
    "vol. 38, no. 5, pp. 609-635, 2008.",
    "[11] M. K. Kalera, S. Srihari, and A. Xu, \"Offline signature "
    "verification and identification using distance statistics,\" Int. "
    "J. Pattern Recognit. Artif. Intell., vol. 18, no. 7, 2004. (Bộ dữ "
    "liệu CEDAR)",
    "[12] D. P. Kingma and J. Ba, \"Adam: A method for stochastic "
    "optimization,\" in Proc. ICLR, 2015.",
    "[13] G. Koch, R. Zemel, and R. Salakhutdinov, \"Siamese neural "
    "networks for one-shot image recognition,\" in ICML Deep Learning "
    "Workshop, 2015.",
    "[14] T. Ojala, M. Pietikäinen, and T. Mäenpää, \"Multiresolution "
    "gray-scale and rotation invariant texture classification with "
    "local binary patterns,\" IEEE Trans. Pattern Anal. Mach. Intell., "
    "vol. 24, no. 7, 2002.",
    "[15] J. Ortega-Garcia et al., \"MCYT baseline corpus: a bimodal "
    "biometric database,\" IEE Proc. -- Vis., Image, Signal Process., "
    "vol. 150, no. 6, 2003. (Bộ dữ liệu MCYT)",
    "[16] N. Otsu, \"A threshold selection method from gray-level "
    "histograms,\" IEEE Trans. Syst., Man, Cybern., vol. 9, no. 1, 1979.",
    "[17] S. Pal, A. Alaei, U. Pal, and M. Blumenstein, \"Performance of "
    "an off-line signature verification method based on texture "
    "features on a large Indic-script signature dataset,\" in Proc. "
    "DAS, 2016. (Bộ dữ liệu BHSig260)",
    "[18] R. Plamondon and S. N. Srihari, \"Online and off-line "
    "handwriting recognition: a comprehensive survey,\" IEEE Trans. "
    "Pattern Anal. Mach. Intell., vol. 22, no. 1, pp. 63-84, 2000.",
    "[19] F. Schroff, D. Kalenichenko, and J. Philbin, \"FaceNet: A "
    "unified embedding for face recognition and clustering,\" in Proc. "
    "CVPR, 2015, pp. 815-823.",
    "[20] K. Simonyan and A. Zisserman, \"Very deep convolutional "
    "networks for large-scale image recognition,\" in Proc. ICLR, 2015.",
    "[21] J. F. Vargas, M. A. Ferrer, C. M. Travieso, and J. B. Alonso, "
    "\"Off-line handwritten signature GPDS-960 corpus,\" in Proc. ICDAR, "
    "2007, pp. 764-768.",
]
for ref in references:
    add_para(doc, ref, justify=True, size=13, space_after=8)

print("Base document configured.")
doc.save(f"{BASE}/thesis/docgen/thesis.docx")
print(f"Total: {Counter.eq} công thức đánh số (xuyên suốt); Bảng/Sơ đồ/Hình đánh số theo từng chương.")
print("Thesis document generated.")
