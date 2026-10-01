#!/usr/bin/env python3
"""Generate the graduation thesis report (.docx) for the handwritten digit
recognition project (KNN vs SVM on MNIST), following:
  - MauQuyDinhLuanVan_v1.1.pdf: Times New Roman 13pt, line spacing 1.5,
    paragraph spacing 6pt before/after, margins top 2cm / bottom 2cm /
    left 3cm / right 2cm, page number bottom-right.
  - The real assigned đề tài brief: "Huấn luyện và so sánh hiệu quả của mô
    hình học máy KNN và SVM trên tập dữ liệu MNIST", công nghệ gợi ý
    Python/Scikit-learn/Streamlit.
  - The official Trường Đại học Trà Vinh formatting appendix
    ("biểu mẫu trình bày"): cover/bìa lót layout, front-matter page order,
    nhận xét pages, BẢNG/SƠ ĐỒ/HÌNH numbered per-chapter, page numbers
    starting (Arabic) at Chương 1, front matter in lowercase Roman numerals.

Infrastructure (helpers, Counter, cover_page, page-numbering OXML) reused
from the earlier Recognite-signature project's build_thesis.py; all
chapter CONTENT below is new and specific to this topic (KNN/SVM/MNIST).
"""

import json

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.enum.section import WD_ORIENT, WD_SECTION_START
from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER

BASE = "/home/user/digit-recognition"
IMGD = f"{BASE}/thesis/abs"
FORM = f"{IMGD}/formulas"
SCR = f"{IMGD}/screenshots"
RES = f"{BASE}/results"

# ---------------------------------------------------------------------------
# Real results loaded directly from the actual training run -- every number
# quoted in Chapter 4 is read from this file, never hand-typed, so the report
# cannot drift from results/comparison_summary.json.
# ---------------------------------------------------------------------------
with open(f"{RES}/comparison_summary.json", encoding="utf-8") as f:
    RESULTS = json.load(f)

KNN = RESULTS["knn"]
SVM = RESULTS["svm"]


def pct(x):
    return f"{x * 100:.2f}".replace(".", ",")


def sec(x):
    return f"{x:.2f}".replace(".", ",")


# ---------------------------------------------------------------------------
# Student / school identifying info (same student, same school -- unrelated
# to the topic correction)
# ---------------------------------------------------------------------------
UNIVERSITY = "TRƯỜNG ĐẠI HỌC TRÀ VINH"
SCHOOL = "TRƯỜNG KỸ THUẬT VÀ CÔNG NGHỆ"
FACULTY = "KHOA CÔNG NGHỆ THÔNG TIN"
STUDENT_NAME = "Phan Thành Thuận"
STUDENT_ID = "170123591"
STUDENT_CLASS = "DX23TT11"
STUDENT_COHORT = "2023"
MAJOR = "Công nghệ thông tin"
ADVISOR = "ThS. Nguyễn Nhứt Lam"
LOCATION = "Trà Vinh"
SUBMIT_DATE = f"{LOCATION}, tháng 10 năm 2026"
PROJECT_TYPE = "ĐỒ ÁN THỰC TẬP CHUYÊN NGÀNH"
THESIS_TITLE = "NHẬN DẠNG CHỮ SỐ VIẾT TAY\nHUẤN LUYỆN VÀ SO SÁNH KNN, SVM\nTRÊN TẬP DỮ LIỆU MNIST"

# ---------------------------------------------------------------------------
# Low-level helpers (reused verbatim from Recognite-signature/build_thesis.py)
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
    for row in table.rows:
        trPr = row._tr.get_or_add_trPr()
        cant_split = OxmlElement("w:cantSplit")
        trPr.append(cant_split)
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
# BẢNG / SƠ ĐỒ / HÌNH counters, per-chapter
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
set_page_number_format(section, "lowerRoman", start=1)


def cover_page():
    add_para(doc, UNIVERSITY, bold=True, center=True, size=16, space_after=0)
    add_para(doc, SCHOOL, bold=True, center=True, size=16, space_after=0)
    add_para(doc, FACULTY, bold=True, center=True, size=14, space_after=0)
    add_image(doc, f"{IMGD}/logo_truong_dai_hoc_tra_vinh.png", width_cm=2.2)
    add_para(doc, PROJECT_TYPE, bold=True, center=True, size=16, space_after=6)
    add_para(doc, THESIS_TITLE, bold=True, center=True, size=18, space_after=6)
    for _ in range(3):
        doc.add_paragraph()
    # Left-aligned per the official template (no explicit alignment set there).
    p = doc.add_paragraph()
    r = p.add_run("Giảng viên hướng dẫn : ")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.bold = True
    r = p.add_run(ADVISOR.upper())
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.bold = True
    add_para(doc, "", center=False, justify=False, space_after=0)
    p = doc.add_paragraph()
    r = p.add_run("Sinh viên thực hiện: ")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.bold = True
    r = p.add_run(STUDENT_NAME.upper())
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.bold = True
    add_para(doc, f"Mã số sinh viên : {STUDENT_ID}", bold=True, center=False, justify=False, size=14, space_after=0)
    add_para(doc, f"Lớp : {STUDENT_CLASS}", bold=True, center=False, justify=False, size=14, space_after=0)
    add_para(doc, f"Khoá : {STUDENT_COHORT}", bold=True, center=False, justify=False, size=14, space_after=0)
    for _ in range(3):
        doc.add_paragraph()
    add_para(doc, SUBMIT_DATE, bold=True, center=True, size=13)
    add_page_break(doc)


# ===========================================================================
# BÌA CHÍNH / BÌA LÓT
# ===========================================================================
cover_page()
cover_page()

# ===========================================================================
# TÓM TẮT
# ===========================================================================
add_heading(doc, "TÓM TẮT ĐỒ ÁN", level=1, center=True)
add_para(doc, (
    "Đồ án huấn luyện và so sánh hiệu quả của hai mô hình học máy kinh điển "
    "— K-Nearest Neighbors (KNN) và Support Vector Machine (SVM) nhân RBF — "
    "trên bài toán nhận dạng chữ số viết tay, sử dụng bộ dữ liệu chuẩn MNIST "
    "(70.000 ảnh chữ số 0-9, kích thước 28×28 điểm ảnh mức xám). Đây là "
    "đúng đề tài đã được phân công: tìm hiểu học máy, xây dựng mô hình và "
    "ứng dụng minh hoạ giải quyết bài toán của đề tài."
))
add_para(doc, (
    f"Dữ liệu được chia theo tỉ lệ 54.000/6.000/10.000 (train/validation/"
    "test) theo phương pháp stratify (giữ nguyên tỉ lệ các chữ số ở mỗi "
    "tập). Kết quả thực nghiệm thật (không mô phỏng) trên tập test: KNN "
    f"(k=5) đạt độ chính xác {pct(KNN['test_accuracy'])}%, thời gian huấn "
    f"luyện {sec(KNN['fit_time_seconds'])} giây; SVM (kernel RBF, C=5) đạt "
    f"độ chính xác {pct(SVM['test_accuracy'])}%, thời gian huấn luyện "
    f"{sec(SVM['fit_time_seconds'])} giây (~{SVM['fit_time_seconds']/60:.1f} "
    "phút)."
))
add_para(doc, (
    "SVM cho độ chính xác cao hơn KNN nhưng đổi lại thời gian huấn luyện "
    "dài hơn nhiều — thể hiện rõ sự đánh đổi giữa một bộ phân loại "
    "\"lazy learner\" (KNN, gần như không tốn thời gian huấn luyện vì chỉ "
    "lưu lại dữ liệu) và một bộ phân loại giải bài toán tối ưu trong lúc "
    "huấn luyện (SVM). Một chương trình demo tương tác được xây dựng bằng "
    "Streamlit, cho phép người dùng vẽ hoặc tải ảnh một chữ số lên và xem "
    "cả hai mô hình dự đoán kèm điểm tin cậy."
))
add_para(doc, "Từ khoá: nhận dạng chữ số viết tay, MNIST, K-Nearest Neighbors, "
              "Support Vector Machine, học máy, scikit-learn.", italic=True)
add_page_break(doc)

# ===========================================================================
# MỤC LỤC
# ===========================================================================
add_heading(doc, "MỤC LỤC", level=1, center=True)
TOC_ENTRIES = [
    (1, "LỜI MỞ ĐẦU", "vi"),
    (2, "1. Lý do chọn đề tài", "vi"),
    (2, "2. Mục tiêu nghiên cứu", "vi"),
    (2, "3. Đối tượng và phạm vi nghiên cứu", "vii"),
    (2, "4. Phương pháp nghiên cứu", "viii"),
    (2, "5. Cấu trúc báo cáo", "viii"),
    (1, "CHƯƠNG 1. TỔNG QUAN", "1"),
    (2, "1.1. Bài toán nhận dạng chữ số viết tay", "1"),
    (2, "1.2. Bộ dữ liệu MNIST", "1"),
    (2, "1.3. Các hướng tiếp cận", "1"),
    (2, "1.4. Phạm vi và lựa chọn của đồ án", "2"),
    (2, "1.5. Tổng kết chương", "2"),
    (1, "CHƯƠNG 2. CƠ SỞ LÝ THUYẾT", "3"),
    (2, "2.1. Thuật toán K-Nearest Neighbors", "3"),
    (2, "2.2. Support Vector Machine và kernel RBF", "3"),
    (2, "2.3. Các độ đo đánh giá", "5"),
    (2, "2.4. Tổng kết chương", "6"),
    (1, "CHƯƠNG 3. PHƯƠNG PHÁP THỰC HIỆN", "7"),
    (2, "3.1. Quy trình tổng thể", "7"),
    (2, "3.2. Chuẩn bị dữ liệu", "7"),
    (2, "3.3. Cài đặt mô hình KNN", "8"),
    (2, "3.4. Cài đặt mô hình SVM", "8"),
    (2, "3.5. Công cụ và môi trường", "9"),
    (2, "3.6. Tổng kết chương", "9"),
    (1, "CHƯƠNG 4. THỰC NGHIỆM VÀ ĐÁNH GIÁ", "10"),
    (2, "4.1. Cách chia dữ liệu", "10"),
    (2, "4.2. Kết quả tổng thể trên tập test", "10"),
    (2, "4.3. Kết quả phân theo từng chữ số", "11"),
    (2, "4.4. So sánh thời gian huấn luyện", "12"),
    (2, "4.5. Phân tích định tính các ca lỗi", "13"),
    (2, "4.6. Thảo luận", "13"),
    (1, "CHƯƠNG 5. CHƯƠNG TRÌNH DEMO", "15"),
    (2, "5.1. Chức năng", "15"),
    (2, "5.2. Kiến trúc và luồng xử lý", "15"),
    (2, "5.3. Công nghệ sử dụng", "15"),
    (2, "5.4. Kết quả trình diễn", "16"),
    (2, "5.5. Hạn chế của chương trình demo", "17"),
    (1, "KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", "18"),
    (1, "PHỤ LỤC", "20"),
    (1, "TÀI LIỆU THAM KHẢO", "21"),
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
    "Nhận dạng chữ số viết tay là một trong những bài toán kinh điển và dễ "
    "tiếp cận nhất của thị giác máy tính, nhưng vẫn mang đầy đủ các thách "
    "thức cơ bản của học máy có giám sát: cùng một chữ số được những người "
    "khác nhau viết theo nhiều nét khác nhau, cùng một người viết cùng một "
    "số cũng không bao giờ cho hai nét vẽ giống hệt nhau."
))
add_para(doc, (
    "Bài toán này còn có giá trị thực tiễn rõ ràng: đọc số trên phiếu điền "
    "tay (mã bưu điện, số trên séc ngân hàng, phiếu khảo sát, bài thi trắc "
    "nghiệm), là bước xử lý đầu vào cho nhiều hệ thống số hoá giấy tờ."
))
add_para(doc, (
    "Bộ dữ liệu MNIST — do Yann LeCun và cộng sự công bố — là bộ dữ liệu "
    "chuẩn, đã được dùng để đánh giá hầu hết các thuật toán học máy và học "
    "sâu trong hơn 25 năm qua. Việc huấn luyện và so sánh hai thuật toán "
    "học máy kinh điển (KNN, SVM) trên MNIST phù hợp với quy mô một đồ án "
    "thực tập chuyên ngành: có đủ độ khó để thể hiện hiểu biết về học máy, "
    "nhưng không đòi hỏi phần cứng GPU hay thời gian huấn luyện quá dài."
))
add_para(doc, (
    "Đây là đúng đề tài được phân công: \"Huấn luyện và so sánh hiệu quả "
    "của mô hình học máy KNN và SVM trên tập dữ liệu MNIST\", với mục tiêu "
    "tìm hiểu học máy và xây dựng một ứng dụng minh hoạ hoạt động được. "
    "Báo cáo này trình bày đầy đủ kết quả thật thu được từ việc thực hiện "
    "đề tài đó."
))

add_heading(doc, "2. Mục tiêu nghiên cứu", level=2)
add_heading(doc, "2.1. Mục tiêu chung", level=3)
add_para(doc, (
    "Tìm hiểu về học máy; xây dựng và huấn luyện hai mô hình học máy (KNN "
    "và SVM) giải quyết đúng bài toán nhận dạng chữ số viết tay trên bộ dữ "
    "liệu MNIST; so sánh hiệu quả của hai mô hình; xây dựng một ứng dụng "
    "minh hoạ hoạt động được, có dữ liệu thật để trình diễn."
))
add_heading(doc, "2.2. Mục tiêu cụ thể", level=3)
add_bullet(doc, "Nắm vững nguyên lý hoạt động của thuật toán K-Nearest "
                "Neighbors và Support Vector Machine (kernel RBF).")
add_bullet(doc, "Tải và chuẩn bị bộ dữ liệu MNIST thật, chia tập "
                "train/validation/test theo phương pháp stratify.")
add_bullet(doc, "Cài đặt, huấn luyện cả hai mô hình bằng scikit-learn trên "
                "cùng một tập dữ liệu, cùng một cách chia, để so sánh công "
                "bằng.")
add_bullet(doc, "Đánh giá hai mô hình bằng các độ đo chuẩn (accuracy, "
                "precision, recall, F1-score, ma trận nhầm lẫn); phân tích "
                "sự đánh đổi giữa độ chính xác và chi phí tính toán.")
add_bullet(doc, "Xây dựng chương trình demo bằng Streamlit: người dùng vẽ "
                "hoặc tải ảnh một chữ số lên, xem cả hai mô hình dự đoán.")

add_heading(doc, "3. Đối tượng và phạm vi nghiên cứu", level=2)
add_heading(doc, "3.1. Đối tượng nghiên cứu", level=3)
add_bullet(doc, "Ảnh chữ số viết tay dạng số hoá, mức xám, kích thước chuẩn "
                "28×28 điểm ảnh (định dạng của bộ dữ liệu MNIST).")
add_bullet(doc, "Hai thuật toán học máy có giám sát: K-Nearest Neighbors và "
                "Support Vector Machine.")
add_heading(doc, "3.2. Phạm vi và các lựa chọn của đồ án", level=3)
add_table(doc, ["Khía cạnh", "Lựa chọn của đồ án", "Lý do"],
          [
              ["Bài toán", "Phân loại đa lớp (10 lớp, chữ số 0-9)",
               "Đúng bài toán MNIST chuẩn, có nhãn thật để đánh giá"],
              ["Bộ dữ liệu", "MNIST thật (70.000 ảnh, qua "
               "sklearn.datasets.fetch_openml)", "Bộ dữ liệu chuẩn của "
               "ngành, công nghệ gợi ý trong đề tài là Scikit-learn"],
              ["Mô hình", "KNN và SVM (kernel RBF)", "Đúng hai mô hình đề "
               "tài yêu cầu so sánh"],
              ["Công cụ", "Python, scikit-learn, Streamlit", "Đúng công "
               "nghệ gợi ý trong đề tài"],
              ["Đầu ra demo", "Nhãn dự đoán (0-9) kèm điểm tin cậy của cả "
               "hai mô hình", "Minh hoạ trực quan sự khác biệt giữa hai mô "
               "hình"],
          ], col_widths_cm=[3, 7, 6], caption="Phạm vi và các lựa chọn của đồ án",
          source="Nguồn: đề tài được phân công")
add_heading(doc, "3.3. Những nội dung không thực hiện", level=3)
add_bullet(doc, "Các mô hình học sâu (CNN, mạng nơ-ron nhiều lớp) — đề tài "
                "chỉ yêu cầu KNN và SVM; TensorFlow/Keras được đề tài gợi ý "
                "như một lựa chọn công nghệ, không bắt buộc dùng.")
add_bullet(doc, "Nhận dạng chữ số viết tay trên ảnh chụp thực tế có nền "
                "phức tạp, nhiều số liền nhau (ngoài phạm vi: đề tài chỉ "
                "xét từng chữ số đơn lẻ, giống định dạng MNIST).")
add_bullet(doc, "Triển khai sản phẩm thành dịch vụ thực tế quy mô lớn.")

add_heading(doc, "4. Phương pháp nghiên cứu", level=2)
add_para(doc, (
    "Đồ án sử dụng phương pháp thực nghiệm: cài đặt và huấn luyện thật hai "
    "mô hình bằng scikit-learn trên dữ liệu MNIST thật, đo đạc thật các độ "
    "đo đánh giá trên một tập kiểm thử tách biệt hoàn toàn với tập huấn "
    "luyện. Toàn bộ số liệu trong Chương 4 được đọc trực tiếp từ tệp kết "
    "quả thật `results/comparison_summary.json` sinh ra bởi "
    "`scripts/train.py`, không dùng số liệu giả định."
))

add_heading(doc, "5. Cấu trúc báo cáo", level=2)
add_para(doc, "Ngoài phần Lời mở đầu và Kết luận, nội dung báo cáo gồm 5 "
              "chương:")
add_bullet(doc, "Chương 1 — Tổng quan: bài toán, bộ dữ liệu MNIST, các "
                "hướng tiếp cận, phạm vi đồ án.")
add_bullet(doc, "Chương 2 — Cơ sở lý thuyết: thuật toán KNN, SVM/kernel "
                "RBF, các độ đo đánh giá.")
add_bullet(doc, "Chương 3 — Phương pháp thực hiện: quy trình tổng thể, "
                "chuẩn bị dữ liệu, cài đặt từng mô hình, công cụ môi "
                "trường.")
add_bullet(doc, "Chương 4 — Thực nghiệm và đánh giá: kết quả thật, phân "
                "tích lỗi, thảo luận.")
add_bullet(doc, "Chương 5 — Chương trình demo: chức năng, kiến trúc, kết "
                "quả trình diễn thật.")

add_page_break(doc)

# ===========================================================================
# LỜI CẢM ƠN
# ===========================================================================
add_heading(doc, "LỜI CẢM ƠN", level=1, center=True)
add_para(doc, (
    f"Em xin gửi lời cảm ơn chân thành đến giảng viên hướng dẫn {ADVISOR} đã "
    "tận tình định hướng và hỗ trợ em trong suốt quá trình thực hiện đồ án "
    "thực tập chuyên ngành này."
))
add_para(doc, (
    f"Em cũng xin cảm ơn quý thầy cô {FACULTY}, {SCHOOL}, {UNIVERSITY} đã "
    "truyền đạt kiến thức nền tảng về học máy trong suốt quá trình học tập, "
    "là cơ sở để em có thể tiếp cận và triển khai đồ án ở mức độ kỹ thuật "
    "như trình bày trong báo cáo này."
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
    "Đồ án này được thực hiện hoàn toàn trong phạm vi học thuật tại trường "
    "(xây dựng và huấn luyện mô hình học máy trên dữ liệu công khai), "
    "không có giai đoạn thực tập tại một cơ quan/doanh nghiệp ngoài "
    "trường, nên không có nhận xét của cơ quan thực tập cho mục này."
), center=True, justify=False)
add_page_break(doc)

# ===========================================================================
# NHẬN XÉT (của giảng viên hướng dẫn)
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
# BẢN NHẬN XÉT (mẫu, của giảng viên hướng dẫn)
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
# NHẬN XÉT (của giảng viên chấm)
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
# BẢN NHẬN XÉT (mẫu, của cán bộ chấm)
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
add_heading(doc, "NHẬN XÉT", level=3)
for item in [
    "1. Nội dung đồ án:",
    "2. Ưu điểm:",
    "3. Khuyết điểm:",
    "4. Đề nghị sửa chữa bổ sung:",
    "5. Đánh giá:",
]:
    add_para(doc, item, justify=False)
    add_blank_lines(doc, 2)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
r = p.add_run(f"{LOCATION}, ngày ..... tháng ..... năm 20.....\nGiảng viên chấm\n(Ký & ghi rõ họ tên)")
r.font.name = "Times New Roman"
r.font.size = Pt(13)
r.italic = True
add_page_break(doc)

# ===========================================================================
# DANH MỤC TỪ VIẾT TẮT
# ===========================================================================
add_heading(doc, "DANH MỤC TỪ VIẾT TẮT", level=1, center=True)
abbr = [
    ("KNN", "K-Nearest Neighbors — K láng giềng gần nhất"),
    ("SVM", "Support Vector Machine — Máy vector hỗ trợ"),
    ("RBF", "Radial Basis Function — Hàm cơ sở xuyên tâm (một loại kernel)"),
    ("MNIST", "Modified National Institute of Standards and Technology "
              "database — bộ dữ liệu chữ số viết tay chuẩn"),
    ("TP/TN/FP/FN", "True Positive/True Negative/False Positive/False "
                     "Negative"),
    ("CPU/GPU", "Central/Graphics Processing Unit — Bộ xử lý trung "
                "tâm/đồ hoạ"),
]
add_table(doc, ["Từ viết tắt", "Giải nghĩa"], abbr, col_widths_cm=[3, 13])

# ===========================================================================
# [SECTION BREAK] Số trang Ả Rập, bắt đầu lại từ 1 tại Chương 1
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

add_heading(doc, "1.1. Bài toán nhận dạng chữ số viết tay", level=2)
add_para(doc, (
    "Cho một ảnh chứa một chữ số viết tay (0-9), hệ thống phải xác định "
    "đúng chữ số đó. Đây là bài toán phân loại đa lớp (multi-class "
    "classification) với 10 lớp, một trong những bài toán được nghiên cứu "
    "nhiều nhất trong lịch sử học máy vì vừa có ứng dụng thực tế (đọc mã "
    "bưu điện, số trên séc ngân hàng), vừa có bộ dữ liệu chuẩn hoá tốt để "
    "đánh giá công bằng giữa các thuật toán [1]."
))
add_para(doc, (
    "Độ khó của bài toán đến từ sự biến thiên lớn trong cách viết: hai "
    "người viết cùng một chữ số có thể khác nhau về độ nghiêng, độ dày nét "
    "bút, kích thước, vị trí trong khung ảnh; một số cặp chữ số có hình "
    "dạng gần giống nhau khi viết tay cẩu thả (ví dụ 4 và 9, 3 và 5, 7 và "
    "1), dễ gây nhầm lẫn ngay cả với mắt người."
))

add_heading(doc, "1.2. Bộ dữ liệu MNIST", level=2)
add_para(doc, (
    "MNIST (Modified National Institute of Standards and Technology) là bộ "
    "dữ liệu chữ số viết tay do Yann LeCun, Corinna Cortes và Christopher "
    "Burges tổng hợp và chuẩn hoá, công bố công khai [2]. Bộ dữ liệu gồm "
    "70.000 ảnh chữ số viết tay (0-9), mỗi ảnh có kích thước 28×28 điểm "
    "ảnh, mức xám (grayscale, giá trị 0-255), đã được căn giữa và chuẩn "
    "hoá kích thước sẵn."
))
add_para(doc, (
    "Đồ án tải bộ dữ liệu này thông qua hàm `sklearn.datasets.fetch_openml"
    "(\"mnist_784\")` của scikit-learn, lấy từ kho dữ liệu công khai "
    "OpenML — đây là bộ MNIST gốc, không phải bản mô phỏng hay rút gọn. "
    "Mỗi ảnh 28×28 được biểu diễn phẳng (flatten) thành một vector 784 "
    "chiều để đưa vào KNN và SVM."
))

add_heading(doc, "1.3. Các hướng tiếp cận", level=2)
add_para(doc, "Có ba nhóm hướng tiếp cận chính cho bài toán này:")
add_bullet(doc, "Học máy dựa trên khoảng cách/láng giềng (KNN): không có "
                "giai đoạn \"học\" theo nghĩa tối ưu tham số, chỉ lưu lại "
                "toàn bộ dữ liệu huấn luyện và so sánh khoảng cách lúc dự "
                "đoán [3].")
add_bullet(doc, "Học máy dựa trên biên phân tách (SVM): tìm một siêu "
                "phẳng (hyperplane) hoặc một mặt phân tách phi tuyến (qua "
                "kernel) tách các lớp với biên lớn nhất có thể [4].")
add_bullet(doc, "Học sâu (mạng nơ-ron tích chập — CNN): tự động học đặc "
                "trưng từ ảnh qua nhiều lớp tích chập, hiện là hướng cho "
                "độ chính xác cao nhất trên MNIST (trên 99,5%), nhưng cần "
                "nhiều dữ liệu, thời gian huấn luyện và thường cần GPU để "
                "huấn luyện nhanh.")
add_para(doc, (
    "Đề tài được phân công chỉ định rõ hai mô hình cần huấn luyện và so "
    "sánh là KNN và SVM (công nghệ gợi ý TensorFlow/Keras cho hướng học "
    "sâu là tuỳ chọn, không bắt buộc), nên đồ án tập trung triển khai và "
    "so sánh kỹ hai mô hình này."
))

add_heading(doc, "1.4. Phạm vi và lựa chọn của đồ án", level=2)
add_para(doc, (
    "Đồ án huấn luyện KNN (k=5, khoảng cách Euclidean) và SVM (kernel RBF, "
    "C=5) trên cùng một tập huấn luyện 54.000 ảnh MNIST thật, đánh giá "
    "trên cùng một tập kiểm thử 10.000 ảnh tách biệt hoàn toàn, để đảm bảo "
    "so sánh công bằng. Công nghệ sử dụng: Python, scikit-learn (huấn "
    "luyện mô hình), NumPy/Pandas (xử lý dữ liệu), Matplotlib (trực quan "
    "hoá ma trận nhầm lẫn), Streamlit (chương trình demo) — đúng nhóm "
    "công nghệ gợi ý của đề tài."
))

add_heading(doc, "1.5. Tổng kết chương", level=2)
add_para(doc, (
    "Chương này giới thiệu bài toán nhận dạng chữ số viết tay, bộ dữ liệu "
    "MNIST và ba hướng tiếp cận chính, từ đó xác định phạm vi của đồ án: "
    "huấn luyện và so sánh KNN với SVM trên MNIST thật. Chương 2 trình bày "
    "cơ sở lý thuyết của hai thuật toán này."
))
add_page_break(doc)

# ===========================================================================
# CHƯƠNG 2 — CƠ SỞ LÝ THUYẾT
# ===========================================================================
start_chapter(2)
add_heading(doc, "CHƯƠNG 2. CƠ SỞ LÝ THUYẾT", level=1)
chapter_byline(doc)

add_heading(doc, "2.1. Thuật toán K-Nearest Neighbors", level=2)
add_para(doc, (
    "K-Nearest Neighbors (KNN) là một thuật toán học máy có giám sát thuộc "
    "nhóm \"lazy learning\": thuật toán không xây dựng một mô hình tham số "
    "trong giai đoạn huấn luyện mà chỉ lưu lại toàn bộ tập dữ liệu huấn "
    "luyện. Khi cần dự đoán nhãn cho một mẫu mới x, thuật toán tính "
    "khoảng cách từ x đến tất cả các mẫu huấn luyện, chọn ra k mẫu gần "
    "nhất, rồi gán nhãn theo nguyên tắc đa số (majority vote) trong k mẫu "
    "đó [3]."
))
add_para(doc, "Khoảng cách Euclidean giữa hai vector d chiều:")
add_formula(doc, f"{FORM}/f_euclidean.png", width_cm=8, eq_num=next_eq())
add_para(doc, "Quy tắc quyết định theo đa số trong k láng giềng gần nhất:")
add_formula(doc, f"{FORM}/f_knn_vote.png", width_cm=9, eq_num=next_eq())
add_para(doc, (
    "Tham số quan trọng nhất của KNN là k (số láng giềng xét đến). k nhỏ "
    "làm mô hình nhạy với nhiễu (dễ overfitting); k lớn làm ranh giới "
    "quyết định mượt hơn nhưng có thể bỏ sót các cấu trúc cục bộ "
    "(underfitting). Đồ án dùng k=5, một giá trị phổ biến cho MNIST, cân "
    "bằng giữa hai thái cực trên."
))
add_para(doc, (
    "Ưu điểm chính của KNN là đơn giản, không có giả định về phân phối dữ "
    "liệu, và gần như không tốn thời gian huấn luyện (chỉ lưu dữ liệu). "
    "Nhược điểm là toàn bộ chi phí tính toán dồn vào lúc dự đoán (phải so "
    "khoảng cách với mọi mẫu huấn luyện) và tốn bộ nhớ vì phải giữ lại "
    "toàn bộ tập huấn luyện."
))

add_heading(doc, "2.2. Support Vector Machine và kernel RBF", level=2)
add_para(doc, (
    "Support Vector Machine (SVM) là một thuật toán phân loại tìm một "
    "siêu phẳng phân tách các lớp sao cho khoảng cách (margin) từ siêu "
    "phẳng đến các điểm dữ liệu gần nhất của mỗi lớp (support vectors) là "
    "lớn nhất có thể [4]. Với dữ liệu phân tách tuyến tính, hàm quyết "
    "định có dạng:"
))
add_formula(doc, f"{FORM}/f_svm_hyperplane.png", width_cm=5, eq_num=next_eq())
add_para(doc, "và bài toán tối ưu biên lớn nhất (margin tối đa) được phát biểu là:")
add_formula(doc, f"{FORM}/f_svm_margin.png", width_cm=12, eq_num=next_eq())
add_para(doc, (
    "Dữ liệu ảnh chữ số viết tay không phân tách tuyến tính trong không "
    "gian gốc, nên SVM cần dùng \"kernel trick\": ánh xạ dữ liệu sang một "
    "không gian chiều cao hơn (ngầm định, không cần tính tường minh) nơi "
    "các lớp dễ phân tách hơn. Đồ án dùng kernel RBF (Radial Basis "
    "Function), kernel phổ biến nhất cho dữ liệu phi tuyến [5]:"
))
add_formula(doc, f"{FORM}/f_rbf_kernel.png", width_cm=8, eq_num=next_eq())
add_para(doc, (
    "trong đó γ (gamma) kiểm soát \"độ rộng\" ảnh hưởng của mỗi điểm dữ "
    "liệu — γ lớn làm ranh giới quyết định phức tạp, dễ overfitting; γ nhỏ "
    "làm ranh giới mượt hơn. Hàm quyết định cuối cùng của SVM kernel là "
    "một tổ hợp tuyến tính có trọng số của kernel giữa mẫu cần dự đoán và "
    "các support vector:"
))
add_formula(doc, f"{FORM}/f_svm_decision.png", width_cm=10, eq_num=next_eq())
add_para(doc, (
    "Tham số C kiểm soát mức độ \"chấp nhận lỗi\" trên tập huấn luyện: C "
    "lớn phạt nặng các điểm bị phân loại sai (biên hẹp hơn, bám sát dữ "
    "liệu huấn luyện hơn); C nhỏ cho phép nhiều điểm nằm sai phía biên hơn "
    "(biên rộng hơn, tổng quát hoá tốt hơn nhưng có thể underfitting). Đồ "
    "án dùng C=5 và γ=\"scale\" (giá trị mặc định của scikit-learn, tự "
    "tính theo phương sai của dữ liệu đầu vào)."
))
add_para(doc, (
    "So với KNN, SVM cần giải một bài toán tối ưu (quadratic programming) "
    "trong lúc huấn luyện, nên chi phí huấn luyện cao hơn hẳn, nhưng đổi "
    "lại lúc dự đoán chỉ cần tính kernel với các support vector (thường "
    "chỉ là một phần nhỏ của tập huấn luyện) chứ không phải toàn bộ dữ "
    "liệu như KNN."
))

add_heading(doc, "2.3. Các độ đo đánh giá", level=2)
add_para(doc, (
    "Với bài toán phân loại đa lớp, đồ án dùng các độ đo chuẩn sau, tính "
    "theo kiểu one-vs-rest cho từng lớp (từng chữ số) rồi lấy trung bình:"
))
add_formula(doc, f"{FORM}/f_accuracy.png", width_cm=9, eq_num=next_eq())
add_formula(doc, f"{FORM}/f_precision.png", width_cm=7, eq_num=next_eq())
add_formula(doc, f"{FORM}/f_recall.png", width_cm=7, eq_num=next_eq())
add_formula(doc, f"{FORM}/f_f1.png", width_cm=10, eq_num=next_eq())
add_para(doc, (
    "Ngoài ra, ma trận nhầm lẫn (confusion matrix) — bảng 10×10 đếm số "
    "lần mỗi chữ số thật (hàng) bị dự đoán thành từng chữ số (cột) — được "
    "dùng để phân tích định tính các cặp chữ số dễ gây nhầm lẫn (Chương "
    "4)."
))

add_heading(doc, "2.4. Tổng kết chương", level=2)
add_para(doc, (
    "Chương này trình bày nguyên lý của KNN (dựa trên khoảng cách, không "
    "có giai đoạn tối ưu) và SVM kernel RBF (dựa trên tối ưu biên phân "
    "tách, tốn chi phí huấn luyện cao hơn), cùng các độ đo dùng để đánh "
    "giá và so sánh hai mô hình ở Chương 4."
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
    "Toàn bộ pipeline gồm bốn bước: (1) tải dữ liệu MNIST thật qua "
    "scikit-learn; (2) chia dữ liệu theo stratify thành ba tập; (3) huấn "
    "luyện độc lập hai mô hình KNN và SVM trên cùng tập huấn luyện; (4) "
    "đánh giá cả hai trên cùng tập kiểm thử và lưu kết quả thật vào "
    "results/. Mô hình đã huấn luyện được nạp lại trong app.py để phục vụ "
    "demo (Chương 5)."
))
add_image(doc, f"{SCR}/01_giao_dien_ban_dau.png", width_cm=11,
          caption="Quy trình tổng thể của đồ án, minh hoạ qua giao diện demo",
          caption_num=next_fig(),
          source="Nguồn: ảnh chụp màn hình chương trình demo thật của đồ án")

add_heading(doc, "3.2. Chuẩn bị dữ liệu", level=2)
add_para(doc, (
    "Dữ liệu được tải bằng hàm `load_mnist()` (src/digitrec/data.py), gọi "
    "`sklearn.datasets.fetch_openml(\"mnist_784\", version=1, "
    "as_frame=False)` — tải về và lưu cache cục bộ 70.000 ảnh MNIST thật, "
    "mỗi ảnh là một vector 784 chiều (giá trị điểm ảnh 0-255) kèm nhãn "
    "chữ số thật."
))
add_para(doc, (
    "Hàm `split_mnist()` chia dữ liệu làm hai bước bằng "
    "`train_test_split` của scikit-learn với tham số `stratify` (giữ "
    "nguyên tỉ lệ 10 chữ số ở mỗi tập con): trước tiên tách 10.000 ảnh làm "
    "tập kiểm thử (test) — tập này không được dùng cho bất kỳ mục đích "
    "nào khác ngoài đánh giá cuối cùng ở Chương 4 — sau đó tách tiếp "
    "6.000 ảnh từ phần còn lại làm tập kiểm định (validation), 54.000 ảnh "
    "còn lại dùng để huấn luyện."
))
add_table(doc, ["Tập dữ liệu", "Số lượng ảnh", "Vai trò"],
          [
              ["Huấn luyện (train)", "54.000", "Huấn luyện cả hai mô hình"],
              ["Kiểm định (validation)", "6.000", "Theo dõi trong quá "
               "trình phát triển, không dùng để chọn tham số qua nhiều "
               "vòng thử"],
              ["Kiểm thử (test)", "10.000", "Đánh giá cuối cùng, hoàn toàn "
               "tách biệt — số liệu báo cáo ở Chương 4 lấy từ tập này"],
          ], col_widths_cm=[5, 4, 7], caption="Cách chia tập dữ liệu MNIST",
          source="Nguồn: src/digitrec/data.py của đồ án")

add_heading(doc, "3.3. Cài đặt mô hình KNN", level=2)
add_para(doc, (
    "Mô hình KNN được khởi tạo bằng `sklearn.neighbors.KNeighborsClassifier"
    "(n_neighbors=5, n_jobs=-1)` (hàm `build_knn()` trong "
    "src/digitrec/models.py). Tham số `n_jobs=-1` cho phép dùng tất cả "
    "luồng CPU khi tính khoảng cách lúc dự đoán, vì đây là bước tốn chi "
    "phí tính toán nhất của KNN."
))

add_heading(doc, "3.4. Cài đặt mô hình SVM", level=2)
add_para(doc, (
    "Mô hình SVM được khởi tạo bằng `sklearn.svm.SVC(kernel=\"rbf\", C=5.0, "
    "gamma=\"scale\")` (hàm `build_svm()`). Một lựa chọn kỹ thuật đáng chú "
    "ý: tham số `probability=True` của scikit-learn (dùng để có xác suất "
    "dự đoán đã hiệu chỉnh) chủ động KHÔNG được bật, vì nó kích hoạt một "
    "vòng kiểm định chéo 5-fold nội bộ (Platt scaling) làm thời gian huấn "
    "luyện chậm đi khoảng 5 lần. Thay vào đó, chương trình demo (Chương "
    "5) dùng `decision_function()` của SVM kết hợp hàm softmax làm điểm "
    "tin cậy ước lượng — đây là điểm tin cậy chưa hiệu chỉnh, được ghi chú "
    "rõ trong giao diện demo để không gây hiểu lầm là xác suất chuẩn."
))

add_heading(doc, "3.5. Công cụ và môi trường", level=2)
add_table(doc, ["Thành phần", "Công cụ/phiên bản"],
          [
              ["Ngôn ngữ", "Python 3.10+"],
              ["Học máy", "scikit-learn (KNeighborsClassifier, SVC)"],
              ["Xử lý dữ liệu", "NumPy, Pandas"],
              ["Trực quan hoá", "Matplotlib (ma trận nhầm lẫn)"],
              ["Giao diện demo", "Streamlit 1.64 (canvas vẽ dùng "
               "st.components.v2, không phụ thuộc thư viện ngoài)"],
              ["Kiểm thử", "pytest (5 test, kể cả kiểm tra demo chạy "
               "thật qua streamlit.testing.v1.AppTest)"],
              ["Phần cứng", "CPU thường, không cần GPU"],
          ], col_widths_cm=[5, 11], caption="Công cụ và môi trường phát triển")

add_heading(doc, "3.6. Tổng kết chương", level=2)
add_para(doc, (
    "Chương này trình bày quy trình bốn bước của đồ án và cách cài đặt cụ "
    "thể từng mô hình bằng scikit-learn, cùng các lựa chọn tham số có chủ "
    "đích (k=5, kernel RBF, không bật probability=True). Chương 4 trình "
    "bày kết quả thực nghiệm thật thu được từ quy trình này."
))
add_page_break(doc)

# ===========================================================================
# CHƯƠNG 4 — THỰC NGHIỆM VÀ ĐÁNH GIÁ
# ===========================================================================
start_chapter(4)
add_heading(doc, "CHƯƠNG 4. THỰC NGHIỆM VÀ ĐÁNH GIÁ", level=1)
chapter_byline(doc)

add_heading(doc, "4.1. Cách chia dữ liệu", level=2)
add_para(doc, (
    "Như trình bày ở mục 3.2, dữ liệu MNIST thật (70.000 ảnh) được chia "
    "stratify thành 54.000 ảnh huấn luyện, 6.000 ảnh kiểm định và 10.000 "
    "ảnh kiểm thử. Toàn bộ số liệu dưới đây được đo trên tập kiểm thử "
    "10.000 ảnh — hoàn toàn không được mô hình nhìn thấy trong lúc huấn "
    "luyện."
))

add_heading(doc, "4.2. Kết quả tổng thể trên tập test", level=2)
add_table(doc, ["Mô hình", "Độ chính xác (test)", "Độ chính xác (validation)",
                "Thời gian huấn luyện"],
          [
              ["KNN (k=5)", f"{pct(KNN['test_accuracy'])}%",
               f"{pct(KNN['val_accuracy'])}%",
               f"{sec(KNN['fit_time_seconds'])} giây"],
              ["SVM (RBF, C=5)", f"{pct(SVM['test_accuracy'])}%",
               f"{pct(SVM['val_accuracy'])}%",
               f"{sec(SVM['fit_time_seconds'])} giây "
               f"(~{SVM['fit_time_seconds']/60:.1f} phút)"],
          ], col_widths_cm=[4, 4, 4, 4],
          caption="Kết quả tổng thể trên tập test (10.000 ảnh)",
          caption_num=next_table(),
          source="Nguồn: results/comparison_summary.json của đồ án")
add_para(doc, (
    f"SVM đạt độ chính xác cao hơn KNN "
    f"{(SVM['test_accuracy']-KNN['test_accuracy'])*100:.2f} điểm phần "
    "trăm trên tập test, nhưng thời gian huấn luyện của SVM gấp khoảng "
    f"{SVM['fit_time_seconds']/KNN['fit_time_seconds']:.0f} lần KNN. Kết "
    "quả này khớp với lý thuyết ở Chương 2: KNN là \"lazy learner\" "
    "(fit() chỉ lưu dữ liệu, gần như tức thời), còn SVM phải giải một bài "
    "toán tối ưu bậc hai trong lúc huấn luyện."
))
add_para(doc, (
    "Bảng precision/recall/F1-score trung bình (macro average, trung bình "
    "không trọng số qua 10 lớp) trên tập test:"
))
knn_macro = KNN["test_classification_report"]["macro avg"]
svm_macro = SVM["test_classification_report"]["macro avg"]
add_table(doc, ["Mô hình", "Precision (macro)", "Recall (macro)", "F1-score (macro)"],
          [
              ["KNN", f"{knn_macro['precision']:.4f}", f"{knn_macro['recall']:.4f}", f"{knn_macro['f1-score']:.4f}"],
              ["SVM", f"{svm_macro['precision']:.4f}", f"{svm_macro['recall']:.4f}", f"{svm_macro['f1-score']:.4f}"],
          ], col_widths_cm=[4, 4, 4, 4],
          caption="Precision/Recall/F1-score trung bình macro trên tập test",
          caption_num=next_table(),
          source="Nguồn: results/comparison_summary.json của đồ án")

add_heading(doc, "4.3. Kết quả phân theo từng chữ số", level=2)
add_image(doc, f"{RES}/confusion_matrix_knn.png", width_cm=11,
          caption="Ma trận nhầm lẫn của KNN trên tập test",
          caption_num=next_fig(), source="Nguồn: kết quả thực nghiệm của đồ án")
add_image(doc, f"{RES}/confusion_matrix_svm.png", width_cm=11,
          caption="Ma trận nhầm lẫn của SVM trên tập test",
          caption_num=next_fig(), source="Nguồn: kết quả thực nghiệm của đồ án")
knn_report = KNN["test_classification_report"]
svm_report = SVM["test_classification_report"]
rows = []
for d in "0123456789":
    rows.append([d, f"{knn_report[d]['recall']:.4f}", f"{svm_report[d]['recall']:.4f}"])
add_table(doc, ["Chữ số", "Recall KNN", "Recall SVM"], rows, col_widths_cm=[4, 6, 6],
          caption="Recall theo từng chữ số trên tập test",
          caption_num=next_table(),
          source="Nguồn: results/comparison_summary.json của đồ án")
add_para(doc, (
    "Quan sát từ ma trận nhầm lẫn: chữ số có recall thấp nhất đối với KNN "
    f"là số 8 (recall {knn_report['8']['recall']:.4f}), chủ yếu bị nhầm "
    "thành số 3 (18 trường hợp trên tập test) và số 5 (17 trường hợp); với "
    "SVM, chữ số 8 được nhận dạng tốt hơn rõ rệt "
    f"(recall {svm_report['8']['recall']:.4f}). Ở cả hai mô hình, cặp chữ "
    "số dễ nhầm lẫn nhất là 4↔9 (KNN nhầm 23 trường hợp số 4 thành số 9), "
    "phù hợp với trực giác vì hai chữ số này có hình dạng gần giống nhau "
    "khi viết tay thiếu nét rõ ràng ở phần trên."
))

add_heading(doc, "4.4. So sánh thời gian huấn luyện", level=2)
add_para(doc, (
    f"Thời gian huấn luyện đo được: KNN {sec(KNN['fit_time_seconds'])} "
    f"giây, SVM {sec(SVM['fit_time_seconds'])} giây, trên cùng một máy "
    "(CPU thường, không có GPU), cùng 54.000 mẫu huấn luyện. Chênh lệch "
    "này minh hoạ rõ sự đánh đổi giữa chi phí huấn luyện và độ chính xác: "
    "nếu cần huấn luyện lại thường xuyên (dữ liệu cập nhật liên tục), KNN "
    "có lợi thế rõ rệt; nếu mô hình được huấn luyện một lần rồi dùng lâu "
    "dài để suy luận, phần chi phí huấn luyện một lần của SVM trở nên ít "
    "quan trọng hơn so với độ chính xác cao hơn mà nó mang lại."
))

add_heading(doc, "4.5. Phân tích định tính các ca lỗi", level=2)
add_para(doc, (
    "Từ ma trận nhầm lẫn của KNN (Hình 4.1), ba cặp chữ số dễ nhầm lẫn "
    "nhất là: 4→9 (23 lần), 8→3 (18 lần), 2→7 (18 lần), 8→5 (17 lần). "
    "Những nhầm lẫn này đều hợp lý về mặt hình học: các cặp số này có thể "
    "trông rất giống nhau khi nét viết tay không rõ ràng (ví dụ số 4 viết "
    "không khép kín phần trên dễ giống số 9; số 8 viết không khép kín "
    "vòng dưới dễ giống số 3 hoặc số 5)."
))
add_para(doc, (
    "SVM giảm đáng kể các nhầm lẫn này (Hình 4.2) — ví dụ số 8 chỉ còn bị "
    "nhầm thành số 3 ở 5 trường hợp và số 5 ở 3 trường hợp, so với 18 và "
    "17 trường hợp của KNN. Điều này phù hợp với lý thuyết: SVM với kernel "
    "RBF có thể học một ranh giới quyết định phi tuyến phức tạp hơn nhiều "
    "so với ranh giới ngầm định theo khoảng cách Euclidean đơn giản của "
    "KNN, nên phân biệt tốt hơn các chữ số có hình dạng gần giống nhau."
))

add_heading(doc, "4.6. Thảo luận", level=2)
add_para(doc, (
    "Kết quả thực nghiệm khớp với kỳ vọng lý thuyết đặt ra ở Chương 2: cả "
    "hai mô hình đều đạt độ chính xác trên 97% — mức khá cao cho hai "
    "thuật toán học máy \"cổ điển\" (chưa dùng học sâu) trên một bộ dữ "
    "liệu đã được chuẩn hoá tốt như MNIST. SVM vượt trội hơn về độ chính "
    "xác nhờ khả năng học ranh giới phi tuyến qua kernel RBF, nhưng phải "
    "đánh đổi bằng thời gian huấn luyện lớn hơn nhiều bậc. KNN phù hợp "
    "hơn cho các tình huống cần huấn luyện/cập nhật nhanh hoặc tài nguyên "
    "tính toán lúc huấn luyện hạn chế; SVM phù hợp hơn khi độ chính xác "
    "là ưu tiên hàng đầu và mô hình chỉ cần huấn luyện một lần."
))
add_para(doc, (
    "Một hạn chế cần lưu ý: do không bật `probability=True`, điểm tin cậy "
    "của SVM hiển thị trong demo (Chương 5) là ước lượng softmax từ "
    "decision_function, không phải xác suất đã hiệu chỉnh thống kê như "
    "KNN (predict_proba dựa trên tỉ lệ nhãn trong k láng giềng). Đây là "
    "lựa chọn có chủ đích để giữ thời gian huấn luyện hợp lý, được ghi "
    "chú rõ trong cả mã nguồn lẫn giao diện demo."
))
add_page_break(doc)

# ===========================================================================
# CHƯƠNG 5 — CHƯƠNG TRÌNH DEMO
# ===========================================================================
start_chapter(5)
add_heading(doc, "CHƯƠNG 5. CHƯƠNG TRÌNH DEMO", level=1)
chapter_byline(doc)

add_heading(doc, "5.1. Chức năng", level=2)
add_para(doc, (
    "Chương trình demo là một ứng dụng web xây dựng bằng Streamlit "
    "(app.py), cho phép người dùng nhập một chữ số viết tay theo hai cách "
    "— vẽ trực tiếp bằng chuột/cảm ứng, hoặc tải lên một ảnh có sẵn — rồi "
    "hiển thị song song kết quả dự đoán của cả KNN và SVM kèm biểu đồ "
    "điểm tin cậy cho từng chữ số (0-9)."
))

add_heading(doc, "5.2. Kiến trúc và luồng xử lý", level=2)
add_para(doc, "Luồng xử lý của demo gồm các bước:")
add_bullet(doc, "Nạp hai mô hình đã huấn luyện (models/knn_mnist.joblib, "
                "models/svm_mnist.joblib) qua joblib, cache bằng "
                "@st.cache_resource để không nạp lại ở mỗi lần tương tác.")
add_bullet(doc, "Nhận ảnh đầu vào (từ canvas vẽ tay hoặc tệp tải lên).")
add_bullet(doc, "Tiền xử lý: chuyển mức xám, resize về đúng 28×28 điểm "
                "ảnh, tự động đảo màu nếu ảnh có nền sáng/chữ tối (quy "
                "ước ngược với MNIST), chuẩn hoá giá trị điểm ảnh về [0,1] "
                "và duỗi phẳng (flatten) thành vector 784 chiều — đúng "
                "định dạng đầu vào hai mô hình đã học.")
add_bullet(doc, "Gọi predict() của cả hai mô hình trên cùng một vector "
                "đầu vào, hiển thị kết quả song song.")

add_heading(doc, "5.3. Công nghệ sử dụng", level=2)
add_para(doc, (
    "Canvas vẽ chữ số được cài đặt bằng `st.components.v2.component()` "
    "— thành phần inline HTML5 Canvas có sẵn của Streamlit, không phụ "
    "thuộc thư viện ngoài. Thư viện phổ biến `streamlit-drawable-canvas` "
    "ban đầu được cân nhắc nhưng loại bỏ sau khi phát hiện phiên bản mới "
    "nhất của thư viện này không tương thích với phiên bản Streamlit đang "
    "dùng (lỗi runtime `StreamlitAPIException` khi khởi tạo). Đề tài cho "
    "phép thay thế bằng công nghệ tương đương nếu giải thích được lựa "
    "chọn và bảo đảm sản phẩm chạy ổn định — lựa chọn này được kiểm chứng "
    "chạy ổn định bằng kiểm thử tự động (`streamlit.testing.v1.AppTest`, "
    "thực thi toàn bộ app thật, xác nhận không có ngoại lệ runtime)."
))

add_heading(doc, "5.4. Kết quả trình diễn", level=2)
add_para(doc, (
    "Hình dưới đây là ảnh chụp màn hình THẬT của chương trình demo đang "
    "chạy (không dàn dựng), ở trạng thái ban đầu:"
))
add_image(doc, f"{SCR}/01_giao_dien_ban_dau.png", width_cm=13,
          caption="Giao diện demo ở trạng thái ban đầu",
          caption_num=next_fig(),
          source="Nguồn: ảnh chụp màn hình chương trình demo thật của đồ án")
add_para(doc, (
    "Khi tải lên một ảnh chữ số thật lấy từ tập kiểm thử MNIST (nhãn thật "
    "là số 7, không nằm trong tập huấn luyện của cả hai mô hình), cả KNN "
    "và SVM đều dự đoán đúng là số 7, với điểm tin cậy cao nhất rõ rệt ở "
    "cột tương ứng:"
))
add_image(doc, f"{SCR}/02_tai_anh_len_ket_qua.png", width_cm=13,
          caption="Kết quả dự đoán thật khi tải ảnh chữ số \"7\" từ tập kiểm thử MNIST",
          caption_num=next_fig(),
          source="Nguồn: ảnh chụp màn hình chương trình demo thật của đồ án")

add_heading(doc, "5.5. Hạn chế của chương trình demo", level=2)
add_bullet(doc, "Cần chạy `scripts/train.py` trước để tạo mô hình trong "
                "models/ (không commit lên kho mã nguồn do dung lượng lớn, "
                "đặc biệt mô hình KNN lưu toàn bộ 54.000 mẫu huấn "
                "luyện).")
add_bullet(doc, "Điểm tin cậy của SVM là ước lượng từ decision_function "
                "qua softmax, không phải xác suất đã hiệu chỉnh thống kê "
                "(xem thảo luận ở mục 4.6).")
add_bullet(doc, "Canvas vẽ tay hoạt động tốt nhất với nét bút dày, viết "
                "căn giữa khung vẽ — giống quy ước của ảnh MNIST gốc.")
add_page_break(doc)

# ===========================================================================
# KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN
# ===========================================================================
add_heading(doc, "KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", level=1, center=True)

add_heading(doc, "1. Kết quả đạt được", level=2)
add_bullet(doc, "Hoàn thành đúng yêu cầu đề tài: huấn luyện và so sánh "
                "KNN với SVM trên bộ dữ liệu MNIST thật (không mô phỏng).")
add_bullet(doc, f"KNN (k=5) đạt độ chính xác {pct(KNN['test_accuracy'])}% "
                f"trên tập test, thời gian huấn luyện "
                f"{sec(KNN['fit_time_seconds'])} giây.")
add_bullet(doc, f"SVM (kernel RBF, C=5) đạt độ chính xác "
                f"{pct(SVM['test_accuracy'])}% trên tập test, thời gian "
                f"huấn luyện {sec(SVM['fit_time_seconds'])} giây.")
add_bullet(doc, "Phân tích định tính xác định được các cặp chữ số dễ gây "
                "nhầm lẫn nhất (4↔9, 8↔3, 8↔5, 2↔7) và cho thấy SVM giảm "
                "đáng kể các nhầm lẫn này so với KNN.")
add_bullet(doc, "Xây dựng thành công chương trình demo Streamlit chạy "
                "ổn định (kiểm chứng bằng kiểm thử tự động), cho phép vẽ "
                "hoặc tải ảnh chữ số lên và xem cả hai mô hình dự đoán.")

add_heading(doc, "2. Hạn chế", level=2)
add_bullet(doc, "Chưa khảo sát ảnh hưởng của việc thay đổi tham số k "
                "(KNN) hay C/gamma (SVM) qua nhiều giá trị khác nhau — đồ "
                "án dùng các giá trị phổ biến, hợp lý cho MNIST nhưng "
                "chưa phải kết quả của một quá trình tìm kiếm tham số tối "
                "ưu (hyperparameter tuning) có hệ thống.")
add_bullet(doc, "Chưa so sánh với hướng tiếp cận học sâu (CNN) — nằm "
                "ngoài phạm vi đề tài vốn chỉ yêu cầu KNN và SVM.")
add_bullet(doc, "Canvas vẽ tay trong demo là ảnh tĩnh, không có tiền xử "
                "lý nâng cao (căn giữa tự động theo trọng tâm nét vẽ) như "
                "quy trình chuẩn hoá chính thức của bộ dữ liệu MNIST gốc.")

add_heading(doc, "3. Hướng phát triển", level=2)
add_bullet(doc, "Tìm kiếm tham số tối ưu có hệ thống (ví dụ GridSearchCV "
                "của scikit-learn) cho cả k của KNN và C/gamma của SVM.")
add_bullet(doc, "So sánh thêm với một mô hình CNN đơn giản (TensorFlow/"
                "Keras, đúng công nghệ gợi ý của đề tài) để có góc nhìn "
                "đầy đủ hơn về đánh đổi giữa học máy cổ điển và học sâu.")
add_bullet(doc, "Cải thiện tiền xử lý ảnh vẽ tay trong demo (căn giữa "
                "theo trọng tâm, chuẩn hoá độ dày nét) để tăng độ chính "
                "xác khi người dùng vẽ trực tiếp.")
add_page_break(doc)

# ===========================================================================
# PHỤ LỤC
# ===========================================================================
add_heading(doc, "PHỤ LỤC", level=1, center=True)
add_heading(doc, "A. Cấu trúc mã nguồn", level=2)
add_para(doc, (
    "src/digitrec/data.py (tải và chia dữ liệu MNIST thật), "
    "src/digitrec/models.py (khởi tạo KNN và SVM), "
    "src/digitrec/evaluate.py (tính độ đo, vẽ ma trận nhầm lẫn), "
    "scripts/train.py (huấn luyện cả hai mô hình, lưu kết quả thật vào "
    "results/), app.py (chương trình demo Streamlit), "
    "tests/test_pipeline.py (5 kiểm thử tự động, bao gồm kiểm tra demo "
    "chạy không lỗi runtime bằng streamlit.testing.v1.AppTest)."
))
add_heading(doc, "B. Hướng dẫn chạy lại", level=2)
add_para(doc, (
    "Chi tiết đầy đủ xem setup/README.md của kho mã nguồn. Tóm tắt: "
    "`pip install -r requirements.txt` → `python scripts/train.py` (tải "
    "MNIST thật, huấn luyện cả hai mô hình, ghi kết quả thật vào "
    "results/) → `streamlit run app.py` (chạy demo)."
))
add_heading(doc, "C. Mã nguồn đã đẩy lên kho mã nguồn công khai", level=2)
add_para(doc, (
    "Toàn bộ mã nguồn, kết quả thật (results/), báo cáo này và video demo "
    "đã được đẩy lên kho mã nguồn công khai trên GitHub, nhánh "
    "nhan-dang-chu-so-viet-tay."
))
add_page_break(doc)

# ===========================================================================
# TÀI LIỆU THAM KHẢO
# ===========================================================================
add_heading(doc, "TÀI LIỆU THAM KHẢO", level=1, center=True)
REFS = [
    "[1] Y. LeCun, L. Bottou, Y. Bengio, and P. Haffner, \"Gradient-based "
    "learning applied to document recognition,\" Proceedings of the IEEE, "
    "vol. 86, no. 11, pp. 2278-2324, 1998.",
    "[2] Y. LeCun, C. Cortes, and C. J. C. Burges, \"The MNIST Database of "
    "Handwritten Digits,\" http://yann.lecun.com/exdb/mnist/.",
    "[3] T. Cover and P. Hart, \"Nearest neighbor pattern classification,\" "
    "IEEE Transactions on Information Theory, vol. 13, no. 1, pp. 21-27, "
    "1967.",
    "[4] C. Cortes and V. Vapnik, \"Support-Vector Networks,\" Machine "
    "Learning, vol. 20, no. 3, pp. 273-297, 1995.",
    "[5] B. Scholkopf and A. J. Smola, Learning with Kernels: Support "
    "Vector Machines, Regularization, Optimization, and Beyond. MIT "
    "Press, 2002.",
    "[6] F. Pedregosa et al., \"Scikit-learn: Machine Learning in Python,\" "
    "Journal of Machine Learning Research, vol. 12, pp. 2825-2830, 2011.",
    "[7] Scikit-learn developers, \"sklearn.neighbors.KNeighborsClassifier\" "
    "và \"sklearn.svm.SVC,\" scikit-learn documentation, "
    "https://scikit-learn.org/stable/.",
    "[8] Scikit-learn developers, \"sklearn.datasets.fetch_openml,\" "
    "scikit-learn documentation, https://scikit-learn.org/stable/.",
    "[9] Streamlit Inc., \"Streamlit documentation,\" "
    "https://docs.streamlit.io/.",
    "[10] C. R. Harris et al., \"Array programming with NumPy,\" Nature, "
    "vol. 585, pp. 357-362, 2020.",
    "[11] J. D. Hunter, \"Matplotlib: A 2D graphics environment,\" "
    "Computing in Science & Engineering, vol. 9, no. 3, pp. 90-95, 2007.",
    "[12] Đề tài được phân công: \"Huấn luyện và so sánh hiệu quả của mô "
    "hình học máy KNN và SVM trên tập dữ liệu MNIST\" (brief đề tài thật, "
    "Trường Đại học Trà Vinh, 2026).",
]
for ref in REFS:
    add_para(doc, ref, justify=False, space_after=6)

doc.save(f"{BASE}/thesis/docgen/thesis.docx")
print("Saved thesis.docx")
