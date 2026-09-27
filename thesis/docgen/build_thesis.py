#!/usr/bin/env python3
"""Generate the graduation thesis report (.docx) for the offline signature
verification project, following MauQuyDinhLuanVan_v1.1.pdf formatting rules:
Times New Roman 13pt, line spacing 1.5, paragraph spacing 6pt before/after,
margins top 2cm / bottom 2cm / left 3cm / right 2cm, page number bottom-right,
Arabic chapter.section.subsection numbering, IEEE reference format.
"""

from docx import Document
from docx.shared import Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER

BASE = "/home/user/Recognite-signature"
IMGD = f"{BASE}/thesis/abs"
FORM = f"{IMGD}/formulas"
SCR = f"{IMGD}/screenshots"
EA = f"{BASE}/results/error_analysis"
RES = f"{BASE}/results"

# ---------------------------------------------------------------------------
# Student / school identifying info -- PLACEHOLDERS, fill in once confirmed
# ---------------------------------------------------------------------------
SCHOOL = "[TÊN TRƯỜNG ĐẠI HỌC]"
FACULTY = "[TÊN KHOA]"
DEPARTMENT = "[TÊN BỘ MÔN]"
STUDENT_NAME = "[HỌ TÊN SINH VIÊN]"
STUDENT_ID = "[MSSV]"
STUDENT_CLASS = "[LỚP]"
ADVISOR = "[HỌ TÊN GIẢNG VIÊN HƯỚNG DẪN]"
ACADEMIC_YEAR = "[NĂM HỌC]"
THESIS_TITLE = "XÂY DỰNG HỆ THỐNG XÁC MINH CHỮ KÝ VIẾT TAY OFFLINE\nWRITER-INDEPENDENT SỬ DỤNG MẠNG NƠ-RON SIAMESE"

# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def set_cell_text(cell, text, bold=False, size=12, align=None):
    cell.text = ""
    p = cell.paragraphs[0]
    if align:
        p.alignment = align
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.font.name = "Times New Roman"
    run.bold = bold


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


def add_image(doc, path, width_cm=14, caption=None, caption_num=None):
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


def add_table(doc, headers, rows, col_widths_cm=None, caption=None, caption_num=None):
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
    doc.add_paragraph()
    return table


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

# ===========================================================================
# BÌA CHÍNH
# ===========================================================================
add_para(doc, SCHOOL, bold=True, center=True, size=14, space_after=0)
add_para(doc, FACULTY, bold=True, center=True, size=14, space_after=0)
add_para(doc, DEPARTMENT, bold=True, center=True, size=13, space_after=0)
for _ in range(6):
    doc.add_paragraph()
add_para(doc, "ĐỒ ÁN CHUYÊN NGÀNH", bold=True, center=True, size=20, space_after=6)
add_para(doc, THESIS_TITLE, bold=True, center=True, size=18, space_after=6)
for _ in range(6):
    doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
r = p.add_run(f"Giảng viên hướng dẫn: {ADVISOR}\nSinh viên thực hiện: {STUDENT_NAME}\nMã số sinh viên: {STUDENT_ID}\nLớp: {STUDENT_CLASS}")
r.font.name = "Times New Roman"
r.font.size = Pt(13)
for _ in range(4):
    doc.add_paragraph()
add_para(doc, ACADEMIC_YEAR, center=True, size=13, italic=True)
add_page_break(doc)

# ===========================================================================
# BÌA PHỤ (lặp lại nội dung bìa chính, giấy trắng, dùng làm trang lót)
# ===========================================================================
add_para(doc, SCHOOL, bold=True, center=True, size=14, space_after=0)
add_para(doc, FACULTY, bold=True, center=True, size=14, space_after=0)
add_para(doc, DEPARTMENT, bold=True, center=True, size=13, space_after=0)
for _ in range(6):
    doc.add_paragraph()
add_para(doc, "ĐỒ ÁN CHUYÊN NGÀNH", bold=True, center=True, size=20, space_after=6)
add_para(doc, THESIS_TITLE, bold=True, center=True, size=18, space_after=6)
for _ in range(8):
    doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
r = p.add_run(f"Giảng viên hướng dẫn: {ADVISOR}\nSinh viên thực hiện: {STUDENT_NAME}\nMã số sinh viên: {STUDENT_ID}\nLớp: {STUDENT_CLASS}")
r.font.name = "Times New Roman"
r.font.size = Pt(13)
for _ in range(4):
    doc.add_paragraph()
add_para(doc, ACADEMIC_YEAR, center=True, size=13, italic=True)
add_page_break(doc)

# ===========================================================================
# NHẬN XÉT CỦA GIẢNG VIÊN HƯỚNG DẪN
# ===========================================================================
add_heading(doc, "NHẬN XÉT CỦA GIẢNG VIÊN HƯỚNG DẪN", level=1, center=True)
for _ in range(12):
    p = doc.add_paragraph("..........................................................................................................")
add_para(doc, "")
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
r = p.add_run("[Địa danh], ngày ..... tháng ..... năm .....\nGiảng viên hướng dẫn\n(Ký và ghi rõ họ tên)")
r.font.name = "Times New Roman"
r.font.size = Pt(13)
r.italic = True
add_page_break(doc)

# ===========================================================================
# LỜI CẢM ƠN
# ===========================================================================
add_heading(doc, "LỜI CẢM ƠN", level=1, center=True)
add_para(doc, (
    "Em xin gửi lời cảm ơn chân thành đến giảng viên hướng dẫn "
    f"{ADVISOR} đã tận tình định hướng, góp ý và hỗ trợ em trong suốt quá trình "
    "thực hiện đồ án chuyên ngành này. Những nhận xét về phương pháp luận, đặc "
    "biệt là các yêu cầu nghiêm ngặt về việc tránh rò rỉ dữ liệu khi đánh giá mô "
    "hình sinh trắc học, đã giúp em xây dựng được một quy trình thực nghiệm đáng "
    "tin cậy hơn."
))
add_para(doc, (
    f"Em cũng xin cảm ơn quý thầy cô {DEPARTMENT}, {FACULTY}, {SCHOOL} đã "
    "truyền đạt kiến thức nền tảng về học máy, thị giác máy tính trong suốt quá "
    "trình học tập, là cơ sở để em có thể tiếp cận và triển khai đồ án ở mức độ "
    "kỹ thuật như trình bày trong báo cáo này."
))
add_para(doc, (
    "Do thời gian và điều kiện phần cứng thực nghiệm (huấn luyện hoàn toàn trên "
    "CPU, không có GPU) còn hạn chế, đồ án khó tránh khỏi một số thiếu sót, đặc "
    "biệt ở phạm vi thực nghiệm (một cấu hình chưa hoàn thành đủ 3 mức margin do "
    "sự cố khởi động lại môi trường tính toán giữa chừng, đã trình bày minh bạch ở "
    "Chương 4). Em rất mong nhận được sự góp ý của quý thầy cô để hoàn thiện hơn."
))
add_para(doc, "Em xin chân thành cảm ơn.")
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
r = p.add_run(f"{STUDENT_NAME}")
r.font.name = "Times New Roman"
r.font.size = Pt(13)
r.italic = True
add_page_break(doc)

# ===========================================================================
# TÓM TẮT
# ===========================================================================
add_heading(doc, "TÓM TẮT ĐỒ ÁN", level=1, center=True)
add_para(doc, (
    "Đồ án xây dựng một hệ thống xác minh chữ ký viết tay offline theo hướng "
    "writer-independent (không cần huấn luyện lại khi có người ký mới), dùng "
    "mạng nơ-ron Siamese kết hợp hàm mất mát contrastive loss. Hai cấu hình mô "
    "hình được huấn luyện và so sánh: Cấu hình A — mạng CNN 5 khối Conv-BatchNorm-"
    "ReLU-MaxPool huấn luyện từ đầu (from-scratch); Cấu hình B — học chuyển giao "
    "(transfer learning) từ backbone ResNet18 tiền huấn luyện trên ImageNet, tinh "
    "chỉnh 2 giai đoạn. Một baseline đối chứng dùng đặc trưng thủ công HOG kết "
    "hợp SVM nhân RBF cũng được xây dựng để so sánh."
))
add_para(doc, (
    "Dữ liệu thực nghiệm gồm bộ CEDAR (55 người ký, chia writer-disjoint 40/5/10 "
    "cho train/validation/test, không người ký nào xuất hiện ở hơn một tập) để "
    "huấn luyện và đánh giá trong miền, và bộ BHSig260 (chữ ký tiếng Bengali và "
    "Hindi) để đánh giá tổng quát hoá zero-shot ngoài miền — không tinh chỉnh lại "
    "mô hình, dùng nguyên ngưỡng quyết định τ đã chọn trên tập validation của "
    "CEDAR. Ngưỡng τ luôn được chọn trên tập validation theo tiêu chí Equal Error "
    "Rate (EER) rồi đóng băng trước khi áp dụng lên tập test, nhằm tránh rò rỉ "
    "thông tin từ tập kiểm tra vào quá trình chọn ngưỡng."
))
add_para(doc, (
    "Kết quả thực nghiệm thật (không phải số liệu mô phỏng) trên tập test CEDAR: "
    "Cấu hình B đạt AUC tổng thể 0,955 (EER validation 5,50%, rất sát chỉ tiêu "
    "5%), vượt trội so với Cấu hình A (AUC 0,915, EER validation 9,75%) và "
    "baseline HOG+SVM (AUC 0,887). Cải thiện rõ rệt nhất của Cấu hình B nằm ở "
    "khả năng chống giả mạo ngẫu nhiên (random forgery): FAR giảm từ 39,5% "
    "(Cấu hình A) xuống còn 13,0%. Đánh giá zero-shot trên BHSig260 cho thấy mô "
    "hình vẫn giữ được tín hiệu phân biệt nhất định qua miền dữ liệu khác hẳn về "
    "ngôn ngữ/hệ chữ viết (AUC 0,75–0,85) dù chưa đạt chỉ tiêu EER≤20% đề ra, và "
    "đồ án đã phân tích định tính nguyên nhân khả dĩ (lệch miền ở khâu tiền xử "
    "lý ảnh)."
))
add_para(doc, (
    "Một ứng dụng demo tương tác được xây dựng bằng Streamlit, cho phép người "
    "dùng tải lên hai ảnh chữ ký và nhận kết quả xác minh (chữ ký thật/giả) theo "
    "thời gian thực, xử lý ảnh hoàn toàn trong bộ nhớ (không lưu ảnh người dùng "
    "xuống đĩa), sử dụng mô hình Cấu hình B đã huấn luyện."
))
add_para(doc, "Từ khoá: xác minh chữ ký offline, mạng Siamese, contrastive loss, "
              "học chuyển giao, ResNet18, writer-independent, CEDAR, BHSig260.",
         italic=True)
add_page_break(doc)

add_heading(doc, "ABSTRACT", level=1, center=True)
add_para(doc, (
    "This project builds an offline handwritten signature verification system "
    "following a writer-independent approach, using a Siamese neural network "
    "trained with contrastive loss. Two model configurations are trained and "
    "compared: Configuration A, a 5-block Conv-BatchNorm-ReLU-MaxPool "
    "convolutional network trained from scratch, and Configuration B, a "
    "transfer-learning model built on an ImageNet-pretrained ResNet18 backbone "
    "fine-tuned in two stages. A handcrafted-feature baseline (HOG features with "
    "an RBF-kernel SVM) is also built for comparison."
))
add_para(doc, (
    "Experiments use the CEDAR dataset (55 writers, split writer-disjointly "
    "40/5/10 for train/validation/test) for in-domain training and evaluation, "
    "and the BHSig260 dataset (Bengali and Hindi signatures) for zero-shot "
    "cross-domain generalization -- no fine-tuning, the decision threshold τ "
    "selected on the CEDAR validation split is frozen and applied as-is. The "
    "threshold is always selected on the validation split by the Equal Error "
    "Rate (EER) criterion and frozen before being applied to the test split, to "
    "avoid leaking test-set information into threshold selection."
))
add_para(doc, (
    "Real (not simulated) experimental results on the CEDAR test split: "
    "Configuration B reaches an overall AUC of 0.955 (validation EER 5.50%, "
    "close to the 5% target), outperforming both Configuration A (AUC 0.915, "
    "validation EER 9.75%) and the HOG+SVM baseline (AUC 0.887). The clearest "
    "improvement is robustness to random forgeries, where FAR drops from 39.5% "
    "(Configuration A) to 13.0% (Configuration B). Zero-shot evaluation on "
    "BHSig260 shows the model retains meaningful discriminative signal across a "
    "very different script/language domain (AUC 0.75-0.85), although it does "
    "not meet the EER<=20% target; a qualitative root-cause analysis (domain "
    "shift in image preprocessing) is presented."
))
add_para(doc, (
    "An interactive Streamlit demo application is built, letting a user upload "
    "two signature images and receive a real-time genuine/forged decision, "
    "processing images entirely in memory (no uploaded image is written to "
    "disk), using the trained Configuration B model."
))
add_para(doc, "Keywords: offline signature verification, Siamese network, "
              "contrastive loss, transfer learning, ResNet18, writer-independent, "
              "CEDAR, BHSig260.", italic=True)
add_page_break(doc)

# ===========================================================================
# MỤC LỤC
# ===========================================================================
add_heading(doc, "MỤC LỤC", level=1, center=True)
TOC_ENTRIES = [
    (1, "MỞ ĐẦU", 16),
    (2, "1. Lý do chọn đề tài", 16),
    (2, "2. Mục tiêu đồ án", 16),
    (2, "3. Đối tượng và phạm vi nghiên cứu", 17),
    (2, "4. Phương pháp nghiên cứu", 17),
    (2, "5. Cấu trúc báo cáo", 17),
    (1, "CHƯƠNG 1. TỔNG QUAN", 19),
    (2, "1.1. Bài toán xác minh chữ ký viết tay", 19),
    (2, "1.2. Hướng tiếp cận writer-independent", 19),
    (2, "1.3. Các bộ dữ liệu chuẩn", 20),
    (2, "1.4. Các hướng tiếp cận liên quan", 21),
    (1, "CHƯƠNG 2. CƠ SỞ LÝ THUYẾT", 22),
    (2, "2.1. Mạng nơ-ron Siamese", 22),
    (2, "2.2. Hàm mất mát Contrastive Loss", 22),
    (2, "2.3. Kiến trúc mạng: CNN từ đầu và học chuyển giao", 23),
    (2, "2.4. Baseline: đặc trưng thủ công HOG và SVM", 24),
    (2, "2.5. Các độ đo đánh giá sinh trắc học", 25),
    (1, "CHƯƠNG 3. PHƯƠNG PHÁP THỰC HIỆN", 27),
    (2, "3.1. Kiến trúc tổng thể hệ thống", 27),
    (2, "3.2. Quy trình tiền xử lý ảnh", 27),
    (2, "3.3. Xây dựng cặp dữ liệu và chia tập writer-disjoint", 28),
    (2, "3.4. Thiết kế thực nghiệm và siêu tham số", 29),
    (2, "3.5. Xây dựng baseline HOG + SVM", 30),
    (2, "3.6. Ứng dụng demo", 31),
    (1, "CHƯƠNG 4. THỰC NGHIỆM VÀ KẾT QUẢ", 32),
    (2, "4.1. Kết quả tổng thể trên tập test CEDAR", 32),
    (2, "4.2. Kết quả phân theo loại giả mạo", 33),
    (2, "4.3. Đường cong ROC", 34),
    (2, "4.4. Phân tích định tính các ca lỗi", 36),
    (2, "4.5. Đánh giá tổng quát hoá zero-shot trên BHSig260", 41),
    (2, "4.6. Ứng dụng demo", 42),
    (1, "CHƯƠNG 5. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", 45),
    (2, "5.1. Kết quả đạt được", 45),
    (2, "5.2. Hạn chế", 45),
    (2, "5.3. Hướng phát triển", 46),
    (1, "TÀI LIỆU THAM KHẢO", 47),
    (1, "PHỤ LỤC", 49),
]
for lvl, text, pg in TOC_ENTRIES:
    add_toc_entry(doc, lvl, text, pg)
add_page_break(doc)

# ===========================================================================
# DANH MỤC HÌNH ẢNH
# ===========================================================================
add_heading(doc, "DANH MỤC HÌNH ẢNH", level=1, center=True)
figures = [
    ("Hình 2.1", "Sơ đồ khối quy trình tiền xử lý ảnh chữ ký (5 bước)"),
    ("Hình 2.2", "Kiến trúc mạng nơ-ron Siamese với hàm mất mát contrastive loss"),
    ("Hình 3.1", "Sơ đồ kiến trúc tổng thể hệ thống"),
    ("Hình 4.1", "Đường cong ROC — baseline HOG + SVM"),
    ("Hình 4.2", "Đường cong ROC — Cấu hình A (from-scratch CNN)"),
    ("Hình 4.3", "Đường cong ROC — Cấu hình B (transfer learning ResNet18)"),
    ("Hình 4.4", "Ca lỗi false-accept, giả mạo ngẫu nhiên, Cấu hình A"),
    ("Hình 4.5", "Ca lỗi false-reject, cùng người ký, Cấu hình A"),
    ("Hình 4.6", "Ca lỗi false-accept, giả mạo kỹ năng cao, Cấu hình A"),
    ("Hình 4.7", "Ca lỗi false-accept, giả mạo ngẫu nhiên, Cấu hình B (so sánh)"),
    ("Hình 4.8", "Ca lỗi false-reject nghiêm trọng trên BHSig260 (lệch miền tiền xử lý)"),
    ("Hình 4.9", "Ca lỗi false-accept giả mạo kỹ năng cao trên BHSig260"),
    ("Hình 4.10", "Giao diện demo Streamlit — trạng thái ban đầu"),
    ("Hình 4.11", "Giao diện demo Streamlit — kết quả với cặp chữ ký thật"),
    ("Hình 4.12", "Giao diện demo Streamlit — kết quả với cặp chữ ký giả"),
]
add_table(doc, ["Số hiệu", "Tên hình"], figures, col_widths_cm=[3, 13])
add_page_break(doc)

add_heading(doc, "DANH MỤC BẢNG BIỂU", level=1, center=True)
tables_list = [
    ("Bảng 2.1", "So sánh Cấu hình A và Cấu hình B"),
    ("Bảng 3.1", "Phân chia writer-disjoint tập CEDAR"),
    ("Bảng 3.2", "Số lượng cặp huấn luyện/kiểm định/kiểm tra"),
    ("Bảng 3.3", "Siêu tham số huấn luyện"),
    ("Bảng 4.1", "Kết quả tổng thể trên tập test CEDAR (3 mô hình)"),
    ("Bảng 4.2", "Kết quả phân theo loại giả mạo — Cấu hình A"),
    ("Bảng 4.3", "Kết quả phân theo loại giả mạo — Cấu hình B"),
    ("Bảng 4.4", "So sánh Cấu hình A và Cấu hình B theo loại giả mạo"),
    ("Bảng 4.5", "Kết quả zero-shot trên BHSig260 (Cấu hình A và baseline)"),
]
add_table(doc, ["Số hiệu", "Tên bảng"], tables_list, col_widths_cm=[3, 13])
add_page_break(doc)

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
    ("GPU/CPU", "Graphics/Central Processing Unit — Bộ xử lý đồ hoạ/trung tâm"),
    ("BN", "Batch Normalization — Chuẩn hoá theo lô"),
    ("τ (tau)", "Ngưỡng quyết định (decision threshold)"),
]
add_table(doc, ["Từ viết tắt", "Giải nghĩa"], abbr, col_widths_cm=[3, 13])
add_page_break(doc)

# ===========================================================================
# MỞ ĐẦU
# ===========================================================================
add_heading(doc, "MỞ ĐẦU", level=1, center=True)

add_heading(doc, "1. Lý do chọn đề tài", level=2)
add_para(doc, (
    "Chữ ký viết tay vẫn là một trong những phương thức xác thực danh tính phổ "
    "biến nhất trong các giao dịch hành chính, ngân hàng, pháp lý tại Việt Nam "
    "cũng như trên thế giới, do tính tiện lợi, không đòi hỏi thiết bị chuyên "
    "dụng và đã được chấp nhận rộng rãi về mặt pháp lý. Tuy nhiên, việc xác minh "
    "chữ ký bằng mắt thường của con người vốn tốn thời gian, phụ thuộc chủ quan "
    "vào kinh nghiệm người kiểm tra, và dễ mắc sai sót trước các dạng giả mạo có "
    "kỹ năng cao (skilled forgery) — nơi người giả mạo đã luyện tập, quan sát kỹ "
    "chữ ký gốc trước khi sao chép."
))
add_para(doc, (
    "Xác minh chữ ký offline (offline signature verification) — nghĩa là chỉ "
    "dựa trên ảnh tĩnh của chữ ký (ảnh scan/chụp), khác với xác minh online có "
    "thể thu thập thêm thông tin động như áp lực bút, tốc độ, trình tự nét viết "
    "— là bài toán khó hơn đáng kể vì chỉ có thông tin hình ảnh tĩnh để phân "
    "biệt. Đây cũng là bài toán thực tế nhất vì trong đa số tình huống (hồ sơ "
    "giấy, tài liệu scan lưu trữ), chỉ có ảnh tĩnh của chữ ký khả dụng."
))
add_para(doc, (
    "Một thách thức đặc trưng khác của bài toán là số lượng mẫu chữ ký thật của "
    "mỗi người thường rất ít (vài chục mẫu), không đủ để huấn luyện một bộ phân "
    "loại riêng cho từng người theo cách tiếp cận writer-dependent truyền "
    "thống. Hướng tiếp cận writer-independent — học một hàm đo độ tương đồng "
    "chung, áp dụng được cho người ký mới mà không cần huấn luyện lại — vì vậy "
    "phù hợp hơn với điều kiện dữ liệu thực tế, và là hướng tiếp cận được lựa "
    "chọn trong đồ án này."
))

add_heading(doc, "2. Mục tiêu đồ án", level=2)
add_bullet(doc, "Xây dựng một quy trình tiền xử lý ảnh chữ ký chuẩn hoá (grayscale, "
                "khử nhiễu, tách nền bằng ngưỡng Otsu, cắt sát vùng chữ ký, chuẩn "
                "hoá kích thước) áp dụng thống nhất cho mọi mô hình trong đồ án.")
add_bullet(doc, "Xây dựng và huấn luyện hai cấu hình mạng Siamese writer-independent: "
                "một mạng CNN huấn luyện từ đầu (Cấu hình A) và một mạng học chuyển "
                "giao từ ResNet18 (Cấu hình B), cùng dùng hàm mất mát contrastive "
                "loss, so sánh khách quan bằng cùng một quy trình đánh giá.")
add_bullet(doc, "Xây dựng một baseline đối chứng bằng đặc trưng thủ công (HOG) và "
                "SVM để có cơ sở so sánh với hướng tiếp cận học sâu.")
add_bullet(doc, "Đánh giá định lượng bằng các độ đo sinh trắc học chuẩn (FAR, FRR, "
                "EER, ROC/AUC) theo đúng quy trình chọn ngưỡng trên tập validation, "
                "đóng băng trước khi áp dụng lên tập test, để tránh rò rỉ dữ liệu.")
add_bullet(doc, "Đánh giá khả năng tổng quát hoá ngoài miền dữ liệu (zero-shot) trên "
                "một bộ dữ liệu khác hẳn về ngôn ngữ/hệ chữ viết (BHSig260).")
add_bullet(doc, "Xây dựng một ứng dụng demo trực quan, cho phép người dùng tương tác "
                "trực tiếp với mô hình đã huấn luyện.")

add_heading(doc, "3. Đối tượng và phạm vi nghiên cứu", level=2)
add_para(doc, (
    "Đối tượng nghiên cứu là ảnh chữ ký viết tay offline (ảnh tĩnh, không có "
    "thông tin động). Phạm vi thực nghiệm giới hạn ở hai bộ dữ liệu công khai: "
    "CEDAR (chữ ký tiếng Anh, dùng để huấn luyện và đánh giá trong miền) và "
    "BHSig260 (chữ ký tiếng Bengali và Hindi, chỉ dùng để đánh giá tổng quát hoá "
    "zero-shot, không huấn luyện). Do hạn chế phần cứng thực nghiệm (huấn luyện "
    "hoàn toàn trên CPU, không có GPU khả dụng trong môi trường thực hiện đồ "
    "án), quy mô huấn luyện đầy đủ mất khoảng 3,3 giờ cho Cấu hình A (toàn bộ 3 "
    "mức margin); với Cấu hình B, do sự cố khởi động lại môi trường tính toán "
    "giữa chừng mức margin cuối, chỉ 2/3 mức margin hoàn thành huấn luyện đầy đủ "
    "— mức margin còn thiếu không ảnh hưởng đến việc chọn mô hình cuối cùng vì "
    "mức margin=1.0 (đã hoàn thành) là mức tốt nhất trong 2 mức đã có kết quả, "
    "nhưng đồ án ghi nhận minh bạch giới hạn này thay vì che giấu."
))

add_heading(doc, "4. Phương pháp nghiên cứu", level=2)
add_para(doc, (
    "Đồ án sử dụng phương pháp thực nghiệm (empirical): triển khai thật các "
    "thuật toán, huấn luyện thật trên dữ liệu thật, đo đạc thật các độ đo đánh "
    "giá — không dùng số liệu giả định hay mô phỏng. Toàn bộ số liệu trình bày "
    "trong Chương 4 là kết quả thật từ các lần chạy huấn luyện và đánh giá được "
    "thực hiện trong quá trình làm đồ án."
))

add_heading(doc, "5. Cấu trúc báo cáo", level=2)
add_para(doc, "Ngoài phần Mở đầu và Kết luận, nội dung báo cáo gồm 5 chương:")
add_bullet(doc, "Chương 1 — Tổng quan: giới thiệu bài toán, khảo sát các hướng "
                "tiếp cận hiện có và các bộ dữ liệu chuẩn cho bài toán xác minh "
                "chữ ký offline.")
add_bullet(doc, "Chương 2 — Cơ sở lý thuyết: trình bày nền tảng toán học của mạng "
                "Siamese, contrastive loss, học chuyển giao, và các độ đo đánh giá "
                "sinh trắc học.")
add_bullet(doc, "Chương 3 — Phương pháp thực hiện: mô tả chi tiết kiến trúc hệ "
                "thống, quy trình tiền xử lý, cách xây dựng cặp dữ liệu huấn "
                "luyện, và thiết kế thực nghiệm.")
add_bullet(doc, "Chương 4 — Thực nghiệm và kết quả: trình bày kết quả định lượng "
                "và phân tích định tính các ca lỗi, so sánh giữa các mô hình.")
add_bullet(doc, "Chương 5 — Kết luận và hướng phát triển: tổng kết những gì đạt "
                "được, hạn chế còn tồn tại, và đề xuất hướng phát triển tiếp theo.")
add_page_break(doc)

# ===========================================================================
# CHƯƠNG 1 — TỔNG QUAN
# ===========================================================================
add_heading(doc, "CHƯƠNG 1. TỔNG QUAN", level=1, page_break_before=True)

add_heading(doc, "1.1. Bài toán xác minh chữ ký viết tay", level=2)
add_para(doc, (
    "Xác minh chữ ký (signature verification) là bài toán nhị phân: cho trước "
    "một chữ ký cần kiểm tra và một hoặc nhiều chữ ký tham chiếu đã biết là thật "
    "của một người, xác định chữ ký cần kiểm tra có phải do chính người đó ký "
    "hay không. Bài toán này khác với nhận dạng chữ ký (signature identification "
    "— xác định chữ ký thuộc về ai trong một tập người ký đã biết) và khác với "
    "nhận dạng chữ viết tay (handwriting recognition — đọc nội dung văn bản)."
))
add_para(doc, (
    "Theo nguồn dữ liệu đầu vào, bài toán chia làm hai nhánh: xác minh online "
    "(online/dynamic), thu thập được thông tin động trong lúc ký (toạ độ theo "
    "thời gian, áp lực bút, tốc độ, số lần nhấc bút) thông qua thiết bị bảng vẽ "
    "điện tử; và xác minh offline (offline/static), chỉ có ảnh tĩnh sau khi ký "
    "xong (ảnh scan, ảnh chụp). Xác minh offline khó hơn về bản chất vì đã mất "
    "toàn bộ thông tin động, chỉ còn lại hình dạng nét mực trên giấy — đây cũng "
    "là dạng bài toán phổ biến nhất trong thực tế (hồ sơ giấy tờ, hợp đồng scan) "
    "và là phạm vi của đồ án này."
))
add_para(doc, (
    "Một đặc điểm gây khó cho bài toán xác minh chữ ký, khác với nhiều bài toán "
    "sinh trắc học khác (vân tay, khuôn mặt), là số lượng mẫu chữ ký thật của "
    "mỗi người thường chỉ vài chục ảnh — không đủ để huấn luyện một mô hình "
    "phân loại riêng biệt, chuyên biệt cho từng người theo kiểu writer-dependent "
    "(mỗi người một bộ phân loại nhị phân thật/giả). Ngoài ra, chữ ký giả được "
    "chia thành hai loại có độ khó khác nhau rõ rệt: giả mạo ngẫu nhiên (random "
    "forgery — người giả mạo không hề biết hình dạng chữ ký thật, chỉ ký bằng "
    "chữ ký của chính họ) và giả mạo kỹ năng cao (skilled forgery — người giả "
    "mạo đã quan sát, luyện tập sao chép chữ ký thật trước khi thực hiện). Trực "
    "giác thông thường cho rằng skilled forgery khó phân biệt hơn nhiều so với "
    "random forgery; đồ án này sẽ cho thấy ở Chương 4 rằng trên bộ dữ liệu CEDAR "
    "thực tế, kết quả thực nghiệm của cả hai cấu hình mô hình lại ngược lại."
))

add_heading(doc, "1.2. Hướng tiếp cận writer-independent", level=2)
add_para(doc, (
    "Do hạn chế về số lượng mẫu/người ký nêu trên, hướng tiếp cận writer-"
    "independent được ưa chuộng hơn trong các nghiên cứu gần đây [1], [14]. Thay "
    "vì huấn luyện một bộ phân loại riêng cho từng người, hướng này học một hàm "
    "biểu diễn (embedding) hoặc một hàm đo độ tương đồng chung cho mọi người ký, "
    "sao cho hai chữ ký của cùng một người được ánh xạ gần nhau trong không gian "
    "biểu diễn, còn hai chữ ký của hai người khác nhau (hoặc chữ ký thật với chữ "
    "ký giả của cùng người) được ánh xạ xa nhau. Khi có người ký mới xuất hiện, "
    "hệ thống chỉ cần vài mẫu chữ ký thật tham chiếu của người đó, không cần "
    "huấn luyện lại mô hình — đây là ưu điểm cốt lõi khiến hướng tiếp cận này "
    "phù hợp với triển khai thực tế."
))
add_para(doc, (
    "Mạng nơ-ron Siamese [1], ban đầu được Bromley và cộng sự đề xuất chính cho "
    "bài toán xác minh chữ ký từ năm 1993, là kiến trúc điển hình cho hướng tiếp "
    "cận này: hai nhánh mạng có cùng cấu trúc và cùng chia sẻ trọng số nhận hai "
    "ảnh đầu vào, ánh xạ mỗi ảnh thành một vector embedding, và một hàm khoảng "
    "cách (thường là khoảng cách Euclid) đo độ khác biệt giữa hai embedding. "
    "Hàm mất mát contrastive loss [2] được dùng để huấn luyện mạng sao cho "
    "khoảng cách nhỏ với cặp cùng lớp (positive pair) và khoảng cách lớn hơn "
    "một ngưỡng margin với cặp khác lớp (negative pair). Đây là kiến trúc và "
    "hàm mất mát được lựa chọn cho cả hai cấu hình mô hình trong đồ án, trình "
    "bày chi tiết ở Chương 2."
))

add_heading(doc, "1.3. Các bộ dữ liệu chuẩn", level=2)
add_para(doc, (
    "CEDAR [3] là một trong những bộ dữ liệu chuẩn phổ biến nhất cho bài toán "
    "xác minh chữ ký offline tiếng Anh, do nhóm nghiên cứu tại Center of "
    "Excellence for Document Analysis and Recognition (CEDAR), Đại học Buffalo "
    "công bố. Bộ dữ liệu gồm chữ ký của 55 người ký, mỗi người có 24 chữ ký thật "
    "và 24 chữ ký giả (do người khác cố ý sao chép). Đồ án sử dụng toàn bộ 55 "
    "người ký này, chia writer-disjoint theo tỉ lệ 40/5/10 cho train/validation/"
    "test — nghĩa là một người ký chỉ xuất hiện trong đúng một trong ba tập, "
    "đảm bảo việc đánh giá phản ánh đúng khả năng tổng quát hoá cho người ký "
    "chưa từng thấy, đúng theo tinh thần writer-independent."
))
add_para(doc, (
    "BHSig260 [4] là bộ dữ liệu chữ ký cho hai hệ chữ Ấn Độ: Bengali (100 người "
    "ký) và Hindi/Devanagari (160 người ký), mỗi người có 24 chữ ký thật và 30 "
    "chữ ký giả kỹ năng cao. Đồ án chỉ dùng bộ này để đánh giá tổng quát hoá "
    "zero-shot — mô hình huấn luyện hoàn toàn trên CEDAR (chữ Latin) được áp "
    "thẳng lên BHSig260 (chữ Bengali/Devanagari) mà không tinh chỉnh lại, nhằm "
    "kiểm tra một tuyên bố mạnh hơn của tính writer-independent: liệu biểu diễn "
    "học được có tổng quát hoá được sang một hệ chữ viết hoàn toàn khác hay chỉ "
    "tổng quát hoá được cho người ký mới trong cùng hệ chữ."
))

add_heading(doc, "1.4. Các hướng tiếp cận liên quan", level=2)
add_para(doc, (
    "Trước khi học sâu trở nên phổ biến, các phương pháp truyền thống cho bài "
    "toán này dựa trên đặc trưng thủ công (handcrafted features) như Histogram "
    "of Oriented Gradients (HOG) [5] hoặc Local Binary Pattern (LBP) [6], trích "
    "xuất đặc trưng hình dạng/kết cấu của nét chữ, sau đó dùng một bộ phân loại "
    "truyền thống như Support Vector Machine (SVM) [7] để phân loại thật/giả. "
    "Hướng này có ưu điểm là nhẹ, không cần lượng dữ liệu lớn để huấn luyện, "
    "nhưng khả năng biểu diễn hạn chế hơn học sâu, đặc biệt trước các dạng giả "
    "mạo tinh vi. Đồ án xây dựng một baseline HOG+SVM (chi tiết ở Chương 2 và "
    "3) để có cơ sở so sánh khách quan với hướng tiếp cận học sâu."
))
add_para(doc, (
    "Về học sâu, ngoài kiến trúc CNN huấn luyện từ đầu, hướng học chuyển giao "
    "(transfer learning) [15] — tận dụng một mạng đã tiền huấn luyện trên một "
    "tập dữ liệu lớn (thường là ImageNet [9]) rồi tinh chỉnh cho bài toán mới — "
    "ngày càng phổ biến khi dữ liệu huấn luyện riêng cho bài toán đích còn hạn "
    "chế, như trường hợp CEDAR chỉ có 40 người ký để huấn luyện. Đồ án khai "
    "thác hướng này ở Cấu hình B, dùng backbone ResNet18 [8] (kiến trúc CNN có "
    "kết nối tắt residual, giúp huấn luyện mạng sâu hơn ổn định hơn) tiền huấn "
    "luyện trên ImageNet."
))

add_page_break(doc)

# ===========================================================================
# CHƯƠNG 2 — CƠ SỞ LÝ THUYẾT
# ===========================================================================
add_heading(doc, "CHƯƠNG 2. CƠ SỞ LÝ THUYẾT", level=1, page_break_before=True)

add_heading(doc, "2.1. Mạng nơ-ron Siamese", level=2)
add_para(doc, (
    "Mạng Siamese gồm hai (hoặc nhiều) nhánh mạng nơ-ron giống hệt nhau về kiến "
    "trúc và chia sẻ chung một bộ trọng số. Mỗi nhánh nhận một ảnh đầu vào "
    "x_1, x_2 và ánh xạ thành vector embedding f(x_1), f(x_2) trong không gian "
    "d chiều. Độ khác biệt giữa hai chữ ký được đo bằng khoảng cách Euclid giữa "
    "hai embedding:"
))
add_formula(doc, f"{FORM}/f_distance.png", width_cm=7, eq_num="(2.1)")
add_para(doc, (
    "trong đó f(·) là hàm ánh xạ (mạng CNN) mà quá trình huấn luyện sẽ tối ưu. "
    "Vì hai nhánh chia sẻ trọng số, mạng học một không gian embedding chung, "
    "không thiên vị nhánh nào — đây là điều kiện cần để khoảng cách D có ý "
    "nghĩa đối xứng (D(x_1, x_2) = D(x_2, x_1))."
))
add_image(doc, f"{FORM}/diagram_siamese.png", width_cm=14,
          caption="Kiến trúc mạng nơ-ron Siamese với hàm mất mát contrastive loss",
          caption_num="Hình 2.2")

add_heading(doc, "2.2. Hàm mất mát Contrastive Loss", level=2)
add_para(doc, (
    "Hàm mất mát contrastive loss [2] được thiết kế để huấn luyện trực tiếp "
    "không gian embedding theo mục tiêu: cặp cùng lớp (positive, nhãn y=1, hai "
    "chữ ký cùng một người) có khoảng cách D nhỏ; cặp khác lớp (negative, nhãn "
    "y=0) có khoảng cách D lớn hơn một ngưỡng margin m:"
))
add_formula(doc, f"{FORM}/f_contrastive.png", width_cm=11, eq_num="(2.2)")
add_para(doc, (
    "Số hạng thứ nhất phạt khoảng cách lớn ở cặp positive (kéo hai embedding lại "
    "gần nhau); số hạng thứ hai chỉ phạt khi khoảng cách D nhỏ hơn margin m ở "
    "cặp negative (đẩy hai embedding ra xa nhau, nhưng không phạt thêm khi đã đủ "
    "xa — tránh mạng \"cố gắng quá mức\" đẩy các cặp negative ra vô cực, điều có "
    "thể làm mất ổn định huấn luyện). Siêu tham số margin m kiểm soát mức độ "
    "\"đủ xa\" được yêu cầu; đồ án khảo sát 3 giá trị margin m ∈ {0,5; 1,0; 2,0} "
    "cho cả hai cấu hình, chọn giá trị tốt nhất theo EER trên tập validation "
    "(trình bày ở Chương 3 và 4)."
))

add_heading(doc, "2.3. Kiến trúc mạng: CNN từ đầu và học chuyển giao", level=2)
add_heading(doc, "2.3.1. Cấu hình A — CNN huấn luyện từ đầu", level=3)
add_para(doc, (
    "Cấu hình A dùng một mạng CNN gồm 5 khối liên tiếp, mỗi khối gồm: lớp tích "
    "chập (Convolution), chuẩn hoá theo lô (Batch Normalization [11] — giúp ổn "
    "định và tăng tốc hội tụ khi huấn luyện từ đầu, không có trọng số tiền huấn "
    "luyện để khởi tạo tốt), hàm kích hoạt ReLU, và lớp gộp cực đại (Max "
    "Pooling) để giảm kích thước không gian. Sau 5 khối, đặc trưng được làm "
    "phẳng và đưa qua một lớp fully-connected để ra vector embedding 128 chiều. "
    "Toàn bộ trọng số được khởi tạo ngẫu nhiên và huấn luyện hoàn toàn từ đầu "
    "trên tập train CEDAR (40 người ký, không có kiến thức tiền huấn luyện nào)."
))
add_heading(doc, "2.3.2. Cấu hình B — Học chuyển giao từ ResNet18", level=3)
add_para(doc, (
    "Cấu hình B dùng ResNet18 [8], một kiến trúc CNN sâu với các khối residual "
    "(kết nối tắt cộng trực tiếp đầu vào của khối vào đầu ra, giúp gradient lan "
    "truyền ổn định qua mạng sâu), đã được tiền huấn luyện trên ImageNet [9] "
    "(hơn 1 triệu ảnh, 1000 lớp đối tượng tự nhiên). Việc tinh chỉnh được thực "
    "hiện theo 2 giai đoạn: giai đoạn 1 đóng băng toàn bộ backbone, chỉ huấn "
    "luyện lớp embedding head (5 epoch, tốc độ học 1×10⁻⁴) để lớp head thích "
    "nghi ban đầu với đặc trưng embedding mục tiêu mà không phá vỡ trọng số "
    "pretrained; giai đoạn 2 mở khoá khối cuối cùng của backbone, huấn luyện "
    "tiếp với hai tốc độ học khác nhau (backbone 1×10⁻⁵, head 1×10⁻⁴) — tốc độ "
    "học nhỏ hơn cho backbone nhằm tinh chỉnh nhẹ nhàng, tránh \"quên\" các đặc "
    "trưng tổng quát đã học từ ImageNet (catastrophic forgetting)."
))
add_para(doc, "Bảng 2.1 tóm tắt khác biệt chính giữa hai cấu hình:")
add_table(doc, ["Tiêu chí", "Cấu hình A", "Cấu hình B"],
           [
               ["Kiến trúc", "CNN 5 khối tự thiết kế", "ResNet18 (18 lớp, residual)"],
               ["Khởi tạo trọng số", "Ngẫu nhiên", "Tiền huấn luyện ImageNet"],
               ["Kích thước ảnh vào", "220×150 (đơn kênh)", "224×224 (chuẩn hoá ImageNet)"],
               ["Chiến lược huấn luyện", "1 giai đoạn, huấn luyện toàn bộ", "2 giai đoạn tinh chỉnh"],
               ["Số tham số cần học từ đầu", "Toàn bộ", "Chỉ head + khối cuối"],
           ], col_widths_cm=[4, 6, 6], caption="So sánh Cấu hình A và Cấu hình B", caption_num="Bảng 2.1")

add_heading(doc, "2.4. Baseline: đặc trưng thủ công HOG và SVM", level=2)
add_para(doc, (
    "Histogram of Oriented Gradients (HOG) [5] là đặc trưng mô tả hình dạng "
    "cục bộ bằng cách chia ảnh thành các ô nhỏ (cell), tính histogram hướng "
    "gradient cường độ trong mỗi ô, sau đó chuẩn hoá theo từng khối (block) ô "
    "lân cận để giảm ảnh hưởng của thay đổi độ sáng/tương phản:"
))
add_formula(doc, f"{FORM}/f_hog.png", width_cm=8, eq_num="(2.3)")
add_para(doc, (
    "trong đó Gx, Gy là gradient ảnh theo hai trục, θ là hướng gradient dùng để "
    "phân bổ vào các bin của histogram. Vector đặc trưng HOG của toàn ảnh được "
    "ghép từ histogram của mọi ô, sau đó đưa vào Support Vector Machine (SVM) "
    "[7] với nhân RBF (Radial Basis Function) để phân loại cặp thật/giả. Siêu "
    "tham số C (điều chuẩn) và γ (độ rộng nhân RBF) được tìm bằng grid search "
    "trên tập validation, chi tiết ở Chương 3."
))

add_heading(doc, "2.5. Các độ đo đánh giá sinh trắc học", level=2)
add_para(doc, (
    "Đồ án dùng bộ độ đo chuẩn cho bài toán xác thực sinh trắc học nhị phân. "
    "Với một ngưỡng quyết định τ cho trước (cặp được phân loại là \"cùng người\" "
    "nếu D ≤ τ), hai loại lỗi được định nghĩa:"
))
add_formula(doc, f"{FORM}/f_far.png", width_cm=9, eq_num="(2.4)")
add_para(doc, (
    "False Acceptance Rate (FAR) — tỉ lệ các cặp thực chất KHÁC người (hoặc "
    "thật/giả) nhưng bị hệ thống chấp nhận nhầm là cùng người thật."
))
add_formula(doc, f"{FORM}/f_frr.png", width_cm=9, eq_num="(2.5)")
add_para(doc, (
    "False Rejection Rate (FRR) — tỉ lệ các cặp thực chất CÙNG người thật nhưng "
    "bị hệ thống từ chối nhầm. FAR và FRR luôn đánh đổi lẫn nhau theo τ: giảm τ "
    "làm giảm FAR nhưng tăng FRR và ngược lại."
))
add_para(doc, (
    "Equal Error Rate (EER) là điểm trên đường cong mà tại đó FAR = FRR, là một "
    "độ đo tổng hợp phổ biến để so sánh các hệ thống sinh trắc học không phụ "
    "thuộc vào việc chọn τ theo hướng ưu tiên loại lỗi nào:"
))
add_formula(doc, f"{FORM}/f_eer.png", width_cm=9, eq_num="(2.6)")
add_para(doc, (
    "Đồ án dùng EER trên tập validation làm tiêu chí CHỌN ngưỡng τ (select_"
    "threshold trong mã nguồn), sau đó ĐÓNG BĂNG giá trị τ này và chỉ dùng nó "
    "để tính FAR/FRR/Accuracy trên tập test — quy trình này đảm bảo tập test "
    "không hề được dùng để tinh chỉnh bất kỳ siêu tham số quyết định nào, tránh "
    "rò rỉ dữ liệu (data leakage) làm số liệu đánh giá trở nên lạc quan giả tạo."
))
add_formula(doc, f"{FORM}/f_accuracy.png", width_cm=9, eq_num="(2.7)")
add_para(doc, (
    "Ngoài ra, đường cong ROC (Receiver Operating Characteristic — biểu diễn "
    "True Positive Rate theo False Positive Rate khi quét τ qua mọi giá trị có "
    "thể) và diện tích dưới đường cong AUC (Area Under Curve, AUC=1 là hoàn "
    "hảo, AUC=0,5 là ngẫu nhiên) được dùng làm độ đo tổng hợp không phụ thuộc "
    "ngưỡng, cho phép so sánh trực tiếp khả năng phân biệt của các mô hình mà "
    "không cần cố định τ."
))

add_page_break(doc)

# ===========================================================================
# CHƯƠNG 3 — PHƯƠNG PHÁP THỰC HIỆN
# ===========================================================================
add_heading(doc, "CHƯƠNG 3. PHƯƠNG PHÁP THỰC HIỆN", level=1, page_break_before=True)

add_heading(doc, "3.1. Kiến trúc tổng thể hệ thống", level=2)
add_para(doc, (
    "Hệ thống gồm 4 khối chức năng chính, được tổ chức thành các module Python "
    "độc lập, có thể kiểm thử riêng biệt (mỗi module có bộ unit test tương "
    "ứng): (1) tiền xử lý ảnh (sigverify.preprocessing), (2) sinh cặp dữ liệu "
    "và chia tập writer-disjoint (sigverify.pairs), (3) mô hình và huấn luyện "
    "(sigverify.models, sigverify.training), (4) đánh giá (sigverify."
    "evaluation). Một ứng dụng Streamlit (app/) sử dụng lại chính module tiền "
    "xử lý và mô hình đã huấn luyện để phục vụ suy luận thời gian thực."
))

add_heading(doc, "3.2. Quy trình tiền xử lý ảnh", level=2)
add_para(doc, (
    "Mọi ảnh chữ ký, dù dùng để huấn luyện hay suy luận qua demo, đều đi qua "
    "cùng một quy trình 5 bước thống nhất, đảm bảo không có sự lệch pha "
    "(train-serving skew) giữa lúc huấn luyện và lúc triển khai:"
))
add_bullet(doc, "Bước 1 — Chuyển ảnh xám (grayscale): loại bỏ thông tin màu sắc "
                "không liên quan đến hình dạng nét chữ.")
add_bullet(doc, "Bước 2 — Khử nhiễu (denoise): áp dụng bộ lọc Gaussian (mặc định "
                "trong cấu hình đồ án) hoặc median để giảm nhiễu hạt từ quá trình "
                "scan/chụp ảnh, trước khi nhị phân hoá.")
add_bullet(doc, "Bước 3 — Xác định vùng chữ ký bằng ngưỡng Otsu: thuật toán Otsu "
                "[13] tự động tìm ngưỡng nhị phân hoá tối ưu (cực đại phương sai "
                "giữa hai lớp nền/nét chữ) để xác định vùng bounding-box chứa nét "
                "chữ ký — chỉ dùng để định vị vùng, không nhất thiết nhị phân hoá "
                "ảnh đầu ra cuối cùng (điều khiển bởi cờ binarize_output).")
add_bullet(doc, "Bước 4 — Cắt sát vùng chữ ký (tight crop to bounding box): loại "
                "bỏ phần nền trắng thừa xung quanh, giúp mô hình tập trung vào "
                "vùng thông tin, không bị ảnh hưởng bởi vị trí chữ ký lệch tâm "
                "trên ảnh gốc.")
add_bullet(doc, "Bước 5 — Resize/pad và chuẩn hoá (normalize): resize về kích "
                "thước cố định giữ tỉ lệ khung hình, đệm (pad) phần còn thiếu, rồi "
                "chuẩn hoá giá trị pixel — về đoạn [0, 1] cho Cấu hình A (đơn "
                "kênh), hoặc theo trung bình/độ lệch chuẩn ImageNet cho Cấu hình B "
                "(để tương thích với thống kê dữ liệu mà ResNet18 được tiền huấn "
                "luyện).")
add_image(doc, f"{FORM}/diagram_pipeline.png", width_cm=14,
          caption="Sơ đồ khối quy trình tiền xử lý ảnh chữ ký (5 bước)",
          caption_num="Hình 2.1")
add_para(doc, (
    "Một phát hiện quan trọng trong quá trình phân tích lỗi (trình bày chi tiết "
    "ở Chương 4) là chính bước khử nhiễu/ngưỡng Otsu này có thể là nguồn gây "
    "lệch miền (domain shift) khi áp dụng sang bộ dữ liệu BHSig260 — do tham số "
    "khử nhiễu được ngầm phù hợp với đặc điểm ảnh scan của CEDAR, không chuyển "
    "đổi tốt sang định dạng/độ phân giải ảnh khác của BHSig260."
))

add_heading(doc, "3.3. Xây dựng cặp dữ liệu và chia tập writer-disjoint", level=2)
add_para(doc, (
    "Vì mạng Siamese học từ cặp ảnh (không phải từng ảnh riêng lẻ), dữ liệu "
    "huấn luyện được tổ chức thành 3 loại cặp: genuine-genuine (hai chữ ký thật "
    "cùng người, nhãn positive), skilled forgery (một chữ ký thật ghép với một "
    "chữ ký giả kỹ năng cao của cùng người, nhãn negative), và random forgery "
    "(một chữ ký thật ghép với chữ ký thật của một người KHÁC, đóng vai trò giả "
    "mạo ngẫu nhiên, nhãn negative). Tỉ lệ lấy mẫu giữa positive : hard-negative "
    "(skilled) : easy-negative (random) là 2:1:1, với ngân sách lấy mẫu 40 cặp/"
    "loại/người ký."
))
add_para(doc, (
    "Việc chia tập tuân thủ nguyên tắc writer-disjoint: một người ký chỉ xuất "
    "hiện trong đúng một trong ba tập train/validation/test, không bao giờ xuất "
    "hiện ở hai tập cùng lúc. Đây là điều kiện bắt buộc để phép đánh giá phản "
    "ánh đúng khả năng tổng quát hoá cho người ký chưa từng thấy trong lúc "
    "huấn luyện — nếu vi phạm (cùng người ký xuất hiện ở cả train và test), số "
    "liệu đánh giá sẽ lạc quan giả tạo vì mô hình đã \"nhìn thấy\" phong cách "
    "viết của người đó."
))
add_table(doc, ["Tập", "Số người ký", "Tỉ lệ"],
           [["Train", 40, "72,7%"], ["Validation", 5, "9,1%"], ["Test", 10, "18,2%"]],
           col_widths_cm=[5, 5, 5],
           caption="Phân chia writer-disjoint tập CEDAR (tổng 55 người ký)",
           caption_num="Bảng 3.1")
add_table(doc, ["Tập", "Số cặp"],
           [["Train", 3200], ["Validation", 400], ["Test", 800]],
           col_widths_cm=[7, 7],
           caption="Số lượng cặp huấn luyện/kiểm định/kiểm tra (theo tỉ lệ 2:1:1)",
           caption_num="Bảng 3.2")

add_heading(doc, "3.4. Thiết kế thực nghiệm và siêu tham số", level=2)
add_para(doc, (
    "Cả hai cấu hình được huấn luyện với optimizer Adam [10], kích thước batch "
    "64, dừng sớm (early stopping) với patience 10 epoch sau 5 epoch khởi động "
    "(warmup — không tính dừng sớm trong giai đoạn này vì EER validation những "
    "epoch đầu thường dao động mạnh), tối đa 100 epoch. Ba giá trị margin của "
    "contrastive loss {0,5; 1,0; 2,0} được khảo sát độc lập cho mỗi cấu hình; "
    "mô hình tốt nhất được chọn theo EER thấp nhất trên tập validation. Một "
    "chi tiết phương pháp luận quan trọng: seed ngẫu nhiên được gieo lại "
    "(re-seed) trước MỖI mức margin, đảm bảo mỗi mức margin xuất phát từ cùng "
    "một cách khởi tạo trọng số và cùng một chuỗi tăng cường dữ liệu (data "
    "augmentation) — nếu không, mức margin sau sẽ kế thừa trạng thái ngẫu nhiên "
    "còn sót lại từ mức margin trước, làm cho việc so sánh giữa các margin bị "
    "nhiễu bởi một biến không kiểm soát được."
))
add_table(doc, ["Siêu tham số", "Giá trị"],
           [
               ["Kích thước batch", 64],
               ["Optimizer", "Adam"],
               ["Tốc độ học (Cấu hình A)", "1×10⁻³"],
               ["Tốc độ học head (Cấu hình B)", "1×10⁻⁴"],
               ["Tốc độ học backbone (Cấu hình B, giai đoạn 2)", "1×10⁻⁵"],
               ["Số epoch tối đa", 100],
               ["Patience dừng sớm", "10 epoch (sau 5 epoch khởi động)"],
               ["Các mức margin khảo sát", "0,5 / 1,0 / 2,0"],
               ["Kích thước embedding", "128 chiều"],
           ], col_widths_cm=[10, 6], caption="Siêu tham số huấn luyện", caption_num="Bảng 3.3")
add_para(doc, (
    "Toàn bộ quá trình huấn luyện được thực hiện trên CPU (không có GPU khả "
    "dụng trong môi trường thực hiện đồ án). Thời gian huấn luyện thực đo được: "
    "mỗi epoch mất khoảng 3,3–5,6 phút tuỳ cấu hình; toàn bộ 3 mức margin của "
    "Cấu hình A (dừng sớm ở epoch 14–21 mỗi mức) hoàn thành trong khoảng 3,3 "
    "giờ. Để tránh mất kết quả nếu môi trường tính toán bị gián đoạn giữa "
    "chừng (rủi ro thực tế với các phiên chạy dài trên hạ tầng container), một "
    "cơ chế checkpoint theo từng mức margin được cài đặt: mô hình tốt nhất tính "
    "đến thời điểm hiện tại được lưu lại (models_registry/config_*_best_"
    "checkpoint.pt) và tệp margin_sweep.json được cập nhật ngay sau khi MỖI "
    "mức margin hoàn thành, thay vì chỉ lưu một lần ở cuối toàn bộ sweep."
))
add_para(doc, (
    "Cơ chế này đã thực sự phát huy tác dụng: trong lần chạy Cấu hình B, môi "
    "trường container bị khởi động lại giữa chừng khi đang huấn luyện mức "
    "margin=2,0, làm mất kết quả của mức margin này. Nhờ checkpoint theo từng "
    "margin, 2/3 mức margin đã hoàn thành ({0,5: EER validation 14,3%}, {1,0: "
    "EER validation 5,5%}) được khôi phục và dùng làm kết quả cuối cùng thay vì "
    "phải huấn luyện lại từ đầu toàn bộ; mức margin=2,0 bị mất được ghi nhận "
    "minh bạch trong báo cáo (Chương 4, Chương 5) thay vì bị che giấu hay thay "
    "thế bằng số liệu giả định."
))

add_heading(doc, "3.5. Xây dựng baseline HOG + SVM", level=2)
add_para(doc, (
    "Baseline được xây dựng bằng cách trích đặc trưng HOG cho mỗi ảnh chữ ký đã "
    "qua tiền xử lý, ghép cặp bằng cách lấy trị tuyệt đối hiệu hai vector đặc "
    "trưng (|HOG(x_1) - HOG(x_2)|) làm đầu vào cho SVM nhân RBF. Siêu tham số C "
    "∈ {0,1; 1; 10} và γ ∈ {\"scale\"; 0,01; 0,001} được dò bằng grid search, "
    "chọn theo hiệu năng trên tập validation, theo đúng cùng một quy trình "
    "chọn-ngưỡng-trên-validation/đóng-băng-trên-test như hai cấu hình Siamese, "
    "đảm bảo phép so sánh giữa ba mô hình công bằng về phương pháp luận."
))

add_heading(doc, "3.6. Ứng dụng demo", level=2)
add_para(doc, (
    "Ứng dụng demo được xây dựng bằng Streamlit, cho phép người dùng tải lên "
    "hai ảnh chữ ký (một ảnh tham chiếu đã biết là thật, một ảnh cần kiểm tra), "
    "chọn mô hình (Cấu hình A hoặc B), và nhận kết quả xác minh theo thời gian "
    "thực: khoảng cách embedding D, ngưỡng τ đang dùng, và quyết định thật/giả. "
    "Toàn bộ ảnh người dùng tải lên được xử lý hoàn toàn trong bộ nhớ (in-"
    "memory), không được ghi xuống đĩa ở bất kỳ bước nào — một yêu cầu thiết kế "
    "quan trọng để bảo vệ dữ liệu sinh trắc học nhạy cảm của người dùng khi "
    "triển khai thực tế."
))

add_page_break(doc)

# ===========================================================================
# CHƯƠNG 4 — THỰC NGHIỆM VÀ KẾT QUẢ
# ===========================================================================
add_heading(doc, "CHƯƠNG 4. THỰC NGHIỆM VÀ KẾT QUẢ", level=1, page_break_before=True)
add_para(doc, (
    "Toàn bộ số liệu trong chương này là kết quả thật (không mô phỏng), thu "
    "được từ các lần chạy huấn luyện và đánh giá trên tập test CEDAR (800 cặp, "
    "10 người ký chưa từng xuất hiện trong tập train/validation) và tập "
    "BHSig260 (đánh giá zero-shot). Ngưỡng τ của mỗi mô hình luôn được chọn "
    "trên tập validation riêng của mô hình đó theo tiêu chí EER, sau đó đóng "
    "băng và áp dụng nguyên vẹn lên tập test/BHSig260."
))

add_heading(doc, "4.1. Kết quả tổng thể trên tập test CEDAR", level=2)
add_table(doc, ["Mô hình", "τ", "Accuracy", "FAR", "FRR", "AUC", "EER (val)"],
           [
               ["Baseline HOG+SVM", "0,1388", "78,50%", "23,50%", "19,50%", "0,887", "—"],
               ["Cấu hình A (margin=1,0)", "0,2471", "84,63%", "20,25%", "10,50%", "0,915", "9,75%"],
               ["Cấu hình B (margin=1,0)", "0,4763", "87,88%", "7,75%", "16,50%", "0,955", "5,50%"],
           ], col_widths_cm=[6, 3, 3, 3, 3, 3, 3],
           caption="Kết quả tổng thể trên tập test CEDAR (800 cặp)", caption_num="Bảng 4.1")
add_para(doc, (
    "Cấu hình B vượt trội cả baseline và Cấu hình A ở AUC tổng thể (0,955 so "
    "với 0,915 và 0,887) và EER trên tập validation (5,50% — rất sát chỉ tiêu "
    "5% đề ra ban đầu — so với 9,75% của Cấu hình A). Đáng chú ý, Cấu hình B có "
    "FRR (16,50%) cao hơn cả Cấu hình A (10,50%) dù AUC và FAR tốt hơn hẳn — "
    "điều này phản ánh việc ngưỡng τ của mỗi mô hình được chọn độc lập theo "
    "điểm cân bằng EER trên validation riêng của mô hình đó (τ càng lớn có xu "
    "hướng giảm FAR nhưng tăng FRR); so sánh Accuracy/FAR/FRR tại một τ cụ thể "
    "vì vậy có ý nghĩa hạn chế hơn so sánh bằng AUC (không phụ thuộc τ) khi "
    "đánh giá khả năng phân biệt thuần tuý của mô hình."
))

add_heading(doc, "4.2. Kết quả phân theo loại giả mạo", level=2)
add_table(doc, ["Loại giả mạo", "Accuracy", "FAR", "FRR", "AUC"],
           [
               ["Skilled forgery", "92,67%", "1,00%", "10,50%", "0,997"],
               ["Random forgery", "79,83%", "39,50%", "10,50%", "0,834"],
           ], col_widths_cm=[6, 4, 4, 4, 4],
           caption="Kết quả phân theo loại giả mạo — Cấu hình A", caption_num="Bảng 4.2")
add_table(doc, ["Loại giả mạo", "Accuracy", "FAR", "FRR", "AUC"],
           [
               ["Skilled forgery", "88,17%", "2,50%", "16,50%", "0,984"],
               ["Random forgery", "84,67%", "13,00%", "16,50%", "0,927"],
           ], col_widths_cm=[6, 4, 4, 4, 4],
           caption="Kết quả phân theo loại giả mạo — Cấu hình B", caption_num="Bảng 4.3")
add_para(doc, (
    "Kết quả đáng chú ý nhất của toàn bộ thực nghiệm: cả hai cấu hình đều phân "
    "biệt skilled forgery gần như hoàn hảo (AUC 0,997 và 0,984) nhưng gặp khó "
    "khăn rõ rệt hơn hẳn với random forgery (AUC 0,834 và 0,927) — NGƯỢC với "
    "trực giác thông thường rằng giả mạo có kỹ năng cao khó phân biệt hơn giả "
    "mạo ngẫu nhiên. Cách đọc hợp lý nhất từ phân tích định tính (mục 4.4): các "
    "chữ ký giả trong CEDAR có nét bút thiếu tự nhiên khá đặc trưng, dễ phân "
    "biệt ở mức thô với nét bút thật; trong khi đó, hai người viết thật khác "
    "nhau đôi khi có \"gestalt\" chữ ký tổng thể (độ nghiêng, mật độ nét, tỉ lệ "
    "khung) tương tự nhau, dễ gây nhầm lẫn hơn. Cấu hình B cải thiện mạnh nhất "
    "đúng vào điểm yếu này của Cấu hình A: FAR random forgery giảm từ 39,50% "
    "xuống 13,00% (giảm hơn 2/3), trong khi FAR skilled forgery chỉ tăng nhẹ từ "
    "1,00% lên 2,50% — một sự đánh đổi rất thuận lợi."
))
add_table(doc, ["Chỉ số", "Cấu hình A", "Cấu hình B", "Chênh lệch"],
           [
               ["AUC tổng thể", "0,915", "0,955", "+0,040"],
               ["FAR random forgery", "39,50%", "13,00%", "−26,50 điểm %"],
               ["AUC random forgery", "0,834", "0,927", "+0,093"],
               ["FAR skilled forgery", "1,00%", "2,50%", "+1,50 điểm %"],
               ["AUC skilled forgery", "0,997", "0,984", "−0,013"],
               ["EER validation", "9,75%", "5,50%", "−4,25 điểm %"],
           ], col_widths_cm=[6, 4, 4, 4],
           caption="So sánh Cấu hình A và Cấu hình B theo loại giả mạo", caption_num="Bảng 4.4")

add_heading(doc, "4.3. Đường cong ROC", level=2)
add_image(doc, f"{RES}/baseline/roc.png", width_cm=13,
          caption="Đường cong ROC — baseline HOG + SVM", caption_num="Hình 4.1")
add_image(doc, f"{RES}/config_a/roc.png", width_cm=13,
          caption="Đường cong ROC — Cấu hình A (from-scratch CNN)", caption_num="Hình 4.2")
add_image(doc, f"{RES}/config_b/roc.png", width_cm=13,
          caption="Đường cong ROC — Cấu hình B (transfer learning ResNet18)", caption_num="Hình 4.3")

add_heading(doc, "4.4. Phân tích định tính các ca lỗi", level=2)
add_heading(doc, "4.4.1. Trên tập test CEDAR (cùng miền dữ liệu huấn luyện)", level=3)
add_para(doc, (
    "Hình 4.4 minh hoạ một ca chấp nhận nhầm (false accept) điển hình ở random "
    "forgery của Cấu hình A: cặp chữ ký của hai người hoàn toàn khác nhau về "
    "nội dung tên (\"Melissa N. Dumble\" và \"Rrand R. Co\") nhưng có khoảng "
    "cách D rất nhỏ so với τ=0,2471. Cả hai chữ ký có nét gạch ngang/uốn lượn "
    "kéo dài đặc trưng phía trên chữ và độ nghiêng cursive tương tự nhau — mô "
    "hình dường như học mạnh các đặc trưng hình dạng tổng thể (độ nghiêng, mật "
    "độ nét, tỉ lệ khung) hơn là chi tiết nhận dạng nét chữ riêng của từng "
    "người."
))
add_image(doc, f"{EA}/cedar_test/random_forgery_false_accept_006.png", width_cm=13,
          caption="Ca lỗi false-accept, giả mạo ngẫu nhiên, Cấu hình A", caption_num="Hình 4.4")
add_para(doc, (
    "Hình 4.5 minh hoạ một ca từ chối nhầm (false reject) ở cặp genuine-"
    "genuine: hai chữ ký của cùng một người nhưng D cao hơn τ, do biến thiên tự "
    "nhiên trong cách ký của chính người đó giữa các lần ký khác nhau (một chữ "
    "ký chụm tròn hơn, một chữ ký dàn trải nghiêng hơn) mà mô hình dừng sớm ở "
    "epoch 18 chưa học đủ để dung nạp."
))
add_image(doc, f"{EA}/cedar_test/genuine_genuine_false_reject_000.png", width_cm=13,
          caption="Ca lỗi false-reject, cùng người ký, Cấu hình A", caption_num="Hình 4.5")
add_para(doc, (
    "Hình 4.6 minh hoạ ca chấp nhận nhầm hiếm gặp ở skilled forgery (D=0,1938, "
    "sát dưới τ=0,2471): cả hai chữ ký (thật và giả) đều có nét nghiêng chéo và "
    "các vòng loop lặp lại theo cùng một hướng — hoạ tiết hình học tổng thể "
    "giống nhau đủ để \"đánh lừa\" mô hình dù đây là chữ ký giả."
))
add_image(doc, f"{EA}/cedar_test/skilled_forgery_false_accept_012.png", width_cm=13,
          caption="Ca lỗi false-accept, giả mạo kỹ năng cao, Cấu hình A", caption_num="Hình 4.6")

add_heading(doc, "4.4.2. So sánh Cấu hình A và Cấu hình B", level=3)
add_para(doc, (
    "Hình 4.7 cho thấy Cấu hình B vẫn mắc cùng loại lỗi random-forgery đã quan "
    "sát ở Cấu hình A (nhầm hai người khác nhau, \"Glorimar Vicente\" và "
    "\"Melissa N. Dumble\", có nét nghiêng cursive tương tự) — nhưng với D="
    "0,3247 gần τ=0,4763 hơn (tỉ lệ D/τ ≈ 0,68) so với ca tương ứng ở Cấu hình "
    "A (tỉ lệ D/τ ≈ 0,05–0,08, tức gần như bằng 0). Nói cách khác, Cấu hình B "
    "vẫn mắc cùng loại lỗi định tính nhưng \"tự tin sai\" ít hơn nhiều — đặc "
    "trưng pretrained ImageNet của ResNet18 tổng quát hoá tốt hơn CNN train-"
    "from-scratch trên tập chỉ 40 người ký."
))
add_image(doc, f"{EA}/cedar_test_config_b/random_forgery_false_accept_004.png", width_cm=13,
          caption="Ca lỗi false-accept, giả mạo ngẫu nhiên, Cấu hình B (so sánh)", caption_num="Hình 4.7")

add_heading(doc, "4.4.3. Trên BHSig260 (zero-shot, khác miền dữ liệu)", level=3)
add_para(doc, (
    "Hình 4.8 minh hoạ ca từ chối nhầm nghiêm trọng nhất quan sát được: hai "
    "chữ ký \"sandeep\" (chữ Devanagari) của cùng một người, nhìn ảnh gốc khá "
    "giống nhau, nhưng D=1,9224 — cao gấp gần 8 lần τ=0,2471 lấy từ CEDAR. "
    "Quan sát ảnh đã qua tiền xử lý cho thấy ảnh A hiện ra đậm/dày nét hẳn so "
    "với ảnh B mảnh/nhạt, dù ảnh gốc trông tương đồng về độ đậm — dấu hiệu rõ "
    "của lệch miền (domain shift) ở khâu tiền xử lý: tham số khử nhiễu/ngưỡng "
    "Otsu được ngầm phù hợp với đặc điểm ảnh scan CEDAR, không chuyển đổi tốt "
    "sang định dạng/độ phân giải/độ tương phản khác của ảnh BHSig260. Đây là "
    "nguyên nhân khả dĩ, nhất quán (quan sát được ở cả hai lần chạy mô hình) "
    "cho tỉ lệ FRR rất cao (44,3%) khi đánh giá zero-shot trên BHSig260."
))
add_image(doc, f"{EA}/bhsig260/genuine_genuine_false_reject_000.png", width_cm=13,
          caption="Ca lỗi false-reject nghiêm trọng trên BHSig260 (lệch miền tiền xử lý)", caption_num="Hình 4.8")
add_para(doc, (
    "Hình 4.9 minh hoạ ca chấp nhận nhầm ở skilled forgery tiếng Hindi "
    "(\"ravindra kaur\", D=0,0176, rất gần 0) — nội dung chữ và phong cách nét "
    "gần như giống hệt nhau bằng mắt thường, càng củng cố giả thuyết mô hình "
    "nhạy với hình dạng/mật độ nét thô hơn là danh tính chi tiết, đặc biệt rõ "
    "hơn khi chuyển miền dữ liệu sang hệ chữ Devanagari có mật độ nét và kiểu "
    "nối chữ khác hẳn chữ Latin của CEDAR."
))
add_image(doc, f"{EA}/bhsig260/skilled_forgery_false_accept_008.png", width_cm=13,
          caption="Ca lỗi false-accept giả mạo kỹ năng cao trên BHSig260", caption_num="Hình 4.9")

add_heading(doc, "4.5. Đánh giá tổng quát hoá zero-shot trên BHSig260", level=2)
add_para(doc, (
    "Mô hình Cấu hình A huấn luyện trên CEDAR được áp thẳng lên BHSig260 KHÔNG "
    "tinh chỉnh lại, dùng nguyên ngưỡng τ đã đóng băng từ CEDAR validation — "
    "phép thử trực tiếp nhất cho tuyên bố writer-independent tổng quát hoá "
    "ngoài miền dữ liệu:"
))
add_table(doc, ["Mô hình", "Loại giả mạo", "FAR", "FRR", "AUC", "Đạt chỉ tiêu EER≤20%?"],
           [
               ["Cấu hình A (Siamese)", "Skilled forgery", "19,77%", "44,31%", "0,752", "Chưa đạt"],
               ["Cấu hình A (Siamese)", "Random forgery", "9,69%", "44,31%", "0,852", "—"],
               ["Baseline HOG+SVM", "Skilled forgery", "41,85%", "21,65%", "0,767", "Chưa đạt"],
               ["Baseline HOG+SVM", "Random forgery", "5,69%", "21,65%", "0,923", "—"],
           ], col_widths_cm=[5, 4, 3, 3, 3, 4],
           caption="Kết quả zero-shot trên BHSig260 (Cấu hình A và baseline)", caption_num="Bảng 4.5")
add_para(doc, (
    "Cả hai mô hình chưa đạt chỉ tiêu EER≤20% đề ra ban đầu cho bài toán zero-"
    "shot, nhưng AUC vẫn ở mức 0,75–0,92 — cao hơn hẳn ngẫu nhiên (0,5) — cho "
    "thấy embedding học được vẫn giữ tín hiệu phân biệt nhất định dù khác hoàn "
    "toàn ngôn ngữ/hệ chữ viết. FRR rất cao (44,31% với Siamese) phù hợp với "
    "giả thuyết lệch miền tiền xử lý nêu ở mục 4.4.3: vì FRR đo lỗi trên chính "
    "các cặp cùng-người-thật, một sai lệch hệ thống ở bước tiền xử lý (không "
    "phải ở khả năng phân biệt của embedding) là lời giải thích nhất quán hơn "
    "so với việc mô hình \"không học được đặc trưng chữ ký nói chung\"."
))
add_para(doc, (
    "Do đây là phép đánh giá zero-shot, ngưỡng τ KHÔNG được hiệu chỉnh lại theo "
    "BHSig260 (điều này sẽ vi phạm chính tính chất zero-shot/writer-independent "
    "muốn kiểm chứng) — nên số liệu ở Bảng 4.5 phản ánh đúng khả năng tổng quát "
    "hoá thực tế của mô hình khi gặp một hệ chữ viết hoàn toàn mới, mà không "
    "được \"ăn gian\" bằng cách điều chỉnh ngưỡng cho vừa dữ liệu đích."
))

add_heading(doc, "4.6. Ứng dụng demo", level=2)
add_para(doc, (
    "Hình 4.10–4.12 là ảnh chụp màn hình thực tế của ứng dụng demo Streamlit, "
    "sử dụng mô hình Cấu hình B đã huấn luyện, thử nghiệm với ảnh chữ ký thật "
    "lấy từ người ký #2 trong tập test CEDAR (chưa từng xuất hiện trong tập "
    "train/validation)."
))
add_image(doc, f"{SCR}/demo_empty.png", width_cm=13,
          caption="Giao diện demo Streamlit — trạng thái ban đầu", caption_num="Hình 4.10")
add_image(doc, f"{SCR}/demo_genuine.png", width_cm=13,
          caption="Giao diện demo Streamlit — kết quả với cặp chữ ký thật", caption_num="Hình 4.11")
add_image(doc, f"{SCR}/demo_forged.png", width_cm=13,
          caption="Giao diện demo Streamlit — kết quả với cặp chữ ký giả", caption_num="Hình 4.12")
add_para(doc, (
    "Cả hai trường hợp thử nghiệm thật (cặp chữ ký thật và cặp chữ ký giả) đều "
    "được ứng dụng phân loại đúng, khớp với nhãn thật của dữ liệu test, minh "
    "chứng rằng mô hình đã huấn luyện hoạt động đúng khi triển khai qua giao "
    "diện người dùng thực tế, không chỉ trên script đánh giá offline."
))

add_page_break(doc)

# ===========================================================================
# CHƯƠNG 5 — KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN
# ===========================================================================
add_heading(doc, "CHƯƠNG 5. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", level=1, page_break_before=True)

add_heading(doc, "5.1. Kết quả đạt được", level=2)
add_bullet(doc, "Xây dựng hoàn chỉnh một hệ thống xác minh chữ ký offline writer-"
                "independent, từ tiền xử lý ảnh, sinh cặp dữ liệu writer-disjoint, "
                "huấn luyện, đến đánh giá và demo tương tác — toàn bộ chạy được "
                "trên dữ liệu thật (CEDAR, BHSig260), không phải dữ liệu mô "
                "phỏng.")
add_bullet(doc, "Cấu hình B (học chuyển giao ResNet18) đạt AUC 0,955 và EER "
                "validation 5,50% trên tập test CEDAR, vượt Cấu hình A (huấn "
                "luyện từ đầu, AUC 0,915) và baseline HOG+SVM (AUC 0,887), rất "
                "sát chỉ tiêu ban đầu EER≤5%.")
add_bullet(doc, "Phát hiện định tính đáng chú ý: cả hai mô hình học sâu phân "
                "biệt giả mạo kỹ năng cao (skilled forgery) tốt hơn hẳn giả mạo "
                "ngẫu nhiên (random forgery) — ngược trực giác thông thường — do "
                "xu hướng học đặc trưng hình dạng/độ nghiêng tổng thể trước chi "
                "tiết danh tính từng người ký.")
add_bullet(doc, "Đánh giá zero-shot trên BHSig260 cho thấy mô hình vẫn giữ tín "
                "hiệu phân biệt có ý nghĩa (AUC 0,75–0,92) qua một hệ chữ viết "
                "hoàn toàn khác, dù chưa đạt chỉ tiêu EER≤20%; nguyên nhân khả dĩ "
                "(lệch miền ở khâu tiền xử lý) đã được xác định qua phân tích "
                "định tính trực tiếp trên ảnh lỗi thật.")
add_bullet(doc, "Xây dựng được cơ chế huấn luyện có khả năng phục hồi (per-"
                "margin checkpointing), đã thực sự cứu được 2/3 kết quả của Cấu "
                "hình B khi môi trường tính toán bị gián đoạn giữa chừng.")

add_heading(doc, "5.2. Hạn chế", level=2)
add_bullet(doc, "Cấu hình B chưa hoàn thành huấn luyện đầy đủ ở mức margin=2,0 "
                "do sự cố khởi động lại môi trường tính toán, nên phép so sánh "
                "3 mức margin của Cấu hình B chưa trọn vẹn như Cấu hình A (đã "
                "hoàn thành cả 3 mức).")
add_bullet(doc, "Toàn bộ huấn luyện thực hiện trên CPU do không có GPU khả dụng "
                "trong môi trường thực hiện đồ án, giới hạn quy mô thực nghiệm có "
                "thể thực hiện được trong thời gian cho phép (ví dụ: không thể "
                "chạy nhiều lần lặp lại với các seed khác nhau để ước lượng "
                "phương sai của kết quả).")
add_bullet(doc, "Khả năng tổng quát hoá sang hệ chữ viết khác (BHSig260) chưa "
                "đạt chỉ tiêu đề ra, cho thấy giới hạn thực sự của writer-"
                "independent khi chuyển miền dữ liệu quá xa so với miền huấn "
                "luyện.")
add_bullet(doc, "Đồ án chưa thử nghiệm các hàm mất mát thay thế (ví dụ triplet "
                "loss) hay các kỹ thuật tăng cường dữ liệu mạnh hơn, vốn có thể "
                "giải quyết triệt để hơn xu hướng học hình dạng thô đã quan sát "
                "được.")

add_heading(doc, "5.3. Hướng phát triển", level=2)
add_bullet(doc, "Hoàn thành huấn luyện Cấu hình B ở mức margin=2,0 (và lý tưởng "
                "là chạy lại cả 3 mức với seed sạch mỗi mức) trên GPU, nhiều khả "
                "năng đạt hoặc vượt chỉ tiêu EER≤5%.")
add_bullet(doc, "Chuẩn hoá bước tiền xử lý bất biến hơn với độ phân giải/độ "
                "tương phản nguồn (ví dụ: chuẩn hoá độ tương phản thích ứng thay "
                "vì kernel khử nhiễu cố định), nhằm giảm phần lệch miền quan sát "
                "được khi đánh giá trên BHSig260.")
add_bullet(doc, "Đo lại BHSig260 zero-shot với Cấu hình B (chưa thực hiện trong "
                "phạm vi đồ án này) để kiểm tra cải thiện quan sát được trên "
                "CEDAR có chuyển sang miền dữ liệu khác hay không.")
add_bullet(doc, "Thử nghiệm triplet loss hoặc các kỹ thuật tăng cường dữ liệu "
                "mạnh hơn (biến dạng đàn hồi, thay đổi độ nghiêng có kiểm soát) "
                "để giảm xu hướng học hình dạng thô trước chi tiết danh tính.")
add_bullet(doc, "Mở rộng ứng dụng demo thành dịch vụ API để tích hợp vào quy "
                "trình xử lý hồ sơ/tài liệu thực tế.")

add_page_break(doc)

# ===========================================================================
# TÀI LIỆU THAM KHẢO (IEEE)
# ===========================================================================
add_heading(doc, "TÀI LIỆU THAM KHẢO", level=1, center=True)
references = [
    "[1] J. Bromley, I. Guyon, Y. LeCun, E. Säckinger, and R. Shah, \"Signature "
    "verification using a 'Siamese' time delay neural network,\" in Advances in "
    "Neural Information Processing Systems (NeurIPS), 1993, pp. 737-744.",
    "[2] R. Hadsell, S. Chopra, and Y. LeCun, \"Dimensionality reduction by "
    "learning an invariant mapping,\" in Proc. IEEE Conf. Computer Vision and "
    "Pattern Recognition (CVPR), 2006, pp. 1735-1742.",
    "[3] M. K. Kalera, S. Srihari, and A. Xu, \"Offline signature verification "
    "and identification using distance statistics,\" Int. J. Pattern "
    "Recognition and Artificial Intelligence, vol. 18, no. 7, pp. 1339-1360, "
    "2004.",
    "[4] S. Pal, A. Alaei, U. Pal, and M. Blumenstein, \"Performance of an "
    "off-line signature verification method based on texture features on a "
    "large Indic-script signature dataset,\" in Proc. 12th IAPR Workshop on "
    "Document Analysis Systems (DAS), 2016, pp. 72-77.",
    "[5] N. Dalal and B. Triggs, \"Histograms of oriented gradients for human "
    "detection,\" in Proc. IEEE Conf. Computer Vision and Pattern Recognition "
    "(CVPR), 2005, pp. 886-893.",
    "[6] T. Ojala, M. Pietikäinen, and T. Mäenpää, \"Multiresolution gray-scale "
    "and rotation invariant texture classification with local binary "
    "patterns,\" IEEE Trans. Pattern Analysis and Machine Intelligence, vol. "
    "24, no. 7, pp. 971-987, 2002.",
    "[7] C. Cortes and V. Vapnik, \"Support-vector networks,\" Machine "
    "Learning, vol. 20, no. 3, pp. 273-297, 1995.",
    "[8] K. He, X. Zhang, S. Ren, and J. Sun, \"Deep residual learning for "
    "image recognition,\" in Proc. IEEE Conf. Computer Vision and Pattern "
    "Recognition (CVPR), 2016, pp. 770-778.",
    "[9] J. Deng, W. Dong, R. Socher, L.-J. Li, K. Li, and L. Fei-Fei, "
    "\"ImageNet: A large-scale hierarchical image database,\" in Proc. IEEE "
    "Conf. Computer Vision and Pattern Recognition (CVPR), 2009, pp. 248-255.",
    "[10] D. P. Kingma and J. Ba, \"Adam: A method for stochastic "
    "optimization,\" in Proc. Int. Conf. Learning Representations (ICLR), "
    "2015.",
    "[11] S. Ioffe and C. Szegedy, \"Batch normalization: Accelerating deep "
    "network training by reducing internal covariate shift,\" in Proc. Int. "
    "Conf. Machine Learning (ICML), 2015, pp. 448-456.",
    "[12] N. Srivastava, G. Hinton, A. Krizhevsky, I. Sutskever, and R. "
    "Salakhutdinov, \"Dropout: A simple way to prevent neural networks from "
    "overfitting,\" J. Machine Learning Research, vol. 15, no. 1, pp. "
    "1929-1958, 2014.",
    "[13] N. Otsu, \"A threshold selection method from gray-level "
    "histograms,\" IEEE Trans. Systems, Man, and Cybernetics, vol. 9, no. 1, "
    "pp. 62-66, 1979.",
    "[14] L. G. Hafemann, R. Sabourin, and L. S. Oliveira, \"Offline "
    "handwritten signature verification — literature review,\" in Proc. Int. "
    "Conf. Image Processing Theory, Tools and Applications (IPTA), 2017, pp. "
    "1-8.",
    "[15] S. J. Pan and Q. Yang, \"A survey on transfer learning,\" IEEE "
    "Trans. Knowledge and Data Engineering, vol. 22, no. 10, pp. 1345-1359, "
    "2010.",
]
for ref in references:
    add_para(doc, ref, justify=True, size=13, space_after=8)

add_page_break(doc)

# ===========================================================================
# PHỤ LỤC
# ===========================================================================
add_heading(doc, "PHỤ LỤC", level=1, center=True)

add_heading(doc, "Phụ lục A. Cấu trúc mã nguồn", level=2)
add_para(doc, (
    "Mã nguồn được tổ chức thành các module theo chức năng, mỗi module có bộ "
    "unit test riêng (tổng cộng 55 test đơn vị chạy trên dữ liệu tổng hợp trước "
    "khi tiến hành huấn luyện trên dữ liệu thật):"
))
add_bullet(doc, "src/sigverify/preprocessing/ — pipeline.py (5 bước tiền xử "
                "lý), datasets.py (đọc CEDAR/BHSig260), augment.py (tăng cường "
                "dữ liệu).")
add_bullet(doc, "src/sigverify/pairs/ — generator.py (sinh cặp genuine/"
                "skilled/random), splits.py (chia writer-disjoint).")
add_bullet(doc, "src/sigverify/models/ — siamese_scratch.py (Cấu hình A), "
                "siamese_transfer.py (Cấu hình B), losses.py (contrastive loss).")
add_bullet(doc, "src/sigverify/training/train_siamese.py — vòng lặp huấn "
                "luyện dùng chung cho cả hai cấu hình.")
add_bullet(doc, "src/sigverify/evaluation/metrics.py — FAR/FRR/EER, chọn "
                "ngưỡng trên validation, đánh giá đóng băng trên test.")
add_bullet(doc, "scripts/train_config_a.py, train_config_b.py — script huấn "
                "luyện đầy đủ, có checkpoint theo từng margin.")
add_bullet(doc, "scripts/error_analysis.py — trích xuất và phân tích các ca "
                "lỗi định tính.")
add_bullet(doc, "app/demo_app.py, app/inference.py — ứng dụng demo Streamlit.")

add_heading(doc, "Phụ lục B. Cấu hình siêu tham số đầy đủ (default.yaml)", level=2)
add_para(doc, "seed: 42", size=12)
add_para(doc, "image.size_scratch: [220, 150]   (Cấu hình A)", size=12)
add_para(doc, "image.size_transfer: [224, 224]  (Cấu hình B)", size=12)
add_para(doc, "preprocessing.denoise: gaussian", size=12)
add_para(doc, "preprocessing.binarize_output: false", size=12)
add_para(doc, "pairs.ratio_pos_hardneg_easyneg: [2, 1, 1]", size=12)
add_para(doc, "pairs.pairs_per_writer: 40", size=12)
add_para(doc, "split.train_writers / val_writers / test_writers: 40 / 5 / 10", size=12)
add_para(doc, "train.batch_size: 64", size=12)
add_para(doc, "train.max_epochs: 100", size=12)
add_para(doc, "train.early_stop_patience: 10  (warmup 5 epoch)", size=12)
add_para(doc, "train.margins: [0.5, 1.0, 2.0]", size=12)
add_para(doc, "model.embedding_dim: 128", size=12)
add_para(doc, "model.transfer_backbone: resnet18", size=12)

add_heading(doc, "Phụ lục C. Ghi chú minh bạch về phương pháp luận", level=2)
add_para(doc, (
    "Trong lần chạy huấn luyện đầy đủ đầu tiên, seed ngẫu nhiên chỉ được gieo "
    "một lần ở đầu script thay vì gieo lại cho từng mức margin, khiến các mức "
    "margin 1,0 và 2,0 kế thừa một phần trạng thái ngẫu nhiên còn lại từ mức "
    "margin trước đó. Lỗi này đã được phát hiện và sửa (gieo lại seed trước mỗi "
    "mức margin) trong scripts/train_config_a.py và scripts/train_config_b.py "
    "cho các lần chạy sau; số liệu trình bày trong Chương 4 vẫn là kết quả "
    "thật hợp lệ (không phải số liệu bịa đặt), chỉ nên đọc phần so sánh GIỮA "
    "CÁC MỨC MARGIN của cùng một cấu hình với mức thận trọng vừa phải — phép "
    "so sánh GIỮA HAI CẤU HÌNH A và B (ở mức margin=1,0, cả hai đều đã dùng "
    "quy trình seed đã sửa) không bị ảnh hưởng bởi hạn chế này."
))
add_para(doc, (
    "Mức margin=2,0 của Cấu hình B không hoàn thành huấn luyện do môi trường "
    "tính toán bị khởi động lại giữa chừng và không thể khôi phục lại từ điểm "
    "dừng — đây là hạn chế thực tế của hạ tầng thực nghiệm, không phải lựa chọn "
    "thiết kế, và được ghi nhận minh bạch thay vì thay thế bằng số liệu ước "
    "lượng hay giả định."
))

print("Base document configured.")
doc.save(f"{BASE}/thesis/docgen/thesis.docx")
print("Thesis document generated.")
