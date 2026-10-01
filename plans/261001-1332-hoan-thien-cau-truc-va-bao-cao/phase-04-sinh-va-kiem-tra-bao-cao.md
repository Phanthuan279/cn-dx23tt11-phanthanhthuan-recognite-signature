---
title: "Phase 4: Sinh và kiểm tra báo cáo"
status: done
---

# Phase 4: Sinh và kiểm tra báo cáo

## Overview

Sinh `.docx`/`.pdf` từ `build_thesis.py`, hội tụ số trang mục lục bằng
phương pháp hai lượt đã dùng ở dự án cũ (render → đo số trang thật bằng
`pdftotext -layout` → cập nhật mục lục → render lại → xác nhận khớp), và
xác minh bằng mắt từng trang quan trọng (bìa, mục lục, các chương, phụ
lục) — không chỉ tin vào việc script chạy không lỗi.

## Requirements

- [x] `.docx` sinh ra không lỗi, convert sang `.pdf` bằng LibreOffice không lỗi
- [x] Mục lục khớp chính xác số trang thật (phương pháp hai lượt)
- [x] Trang bìa đúng biểu mẫu (logo, canh giữa/canh trái đúng như đã sửa ở dự án cũ)
- [x] Mỗi chương, công thức, bảng, hình hiển thị đúng khi render ra ảnh kiểm tra bằng mắt

## Implementation Steps

1. Chạy `python thesis/docgen/build_thesis.py`, copy `thesis/docgen/thesis.docx` sang `thesis/doc/thesis.docx` (đúng quy ước đã dùng ở dự án cũ — script ghi vào `docgen/` trước, `doc/` là bản chính thức).
2. Convert sang PDF bằng `office.soffice.run_soffice` (skill docx đã dùng trước đó).
3. Đo số trang thật từng heading bằng `pdftotext -layout` + `\f`, cập nhật `TOC_ENTRIES`, chạy lại bước 1-2, xác nhận hội tụ (không còn lệch số trang nào).
4. Render các trang quan trọng ra ảnh (`pdftoppm -jpeg -r 100-150`) và xem bằng mắt: bìa chính, bìa lót, mục lục, trang đầu mỗi chương, phụ lục, tài liệu tham khảo — xác nhận không có lỗi canh lề/font/ngắt trang giống các lỗi đã gặp ở dự án cũ (ngắt dòng tiêu đề xấu, canh giữa/trái sai, tràn trang).
5. Chạy `pytest tests/` để xác nhận không có gì bị hỏng do thêm file mới vào dự án (không mong đợi test nào liên quan tới docx, nhưng xác nhận cho chắc).

## Todo

- [x] Sinh docx/pdf lần đầu
- [x] Hội tụ số trang mục lục (hai lượt)
- [x] Render và xem bằng mắt các trang quan trọng
- [x] Sửa mọi lỗi hiển thị phát hiện được trước khi coi là xong

## Success Criteria

Đã đo số trang thật của 40 heading/mục bằng `pdftotext -layout` (tách theo
form-feed `\f`, lấy dòng cuối mỗi trang làm số trang chân trang), cập nhật
`TOC_ENTRIES` khớp đúng từng mục, sinh lại docx/pdf lần hai và đo lại —
**0/40 mục lệch số trang** (script đo đối chiếu in "Total mismatches: 0").
Bản chính thức đã copy vào `thesis/doc/thesis.docx` và `thesis/pdf/thesis.pdf`
đúng quy ước của dự án cũ (docgen/ là bản làm việc, doc/+pdf/ là bản chính
thức). Đã xem bằng mắt (render ảnh `pdftoppm`) trang bìa (logo thật, khối
Giảng viên/Sinh viên căn trái đúng), trang mục lục (khớp số trang thật,
không tràn dòng), trang đầu các Chương 1-5, trang Phụ lục, trang Tài liệu
tham khảo — không phát hiện lỗi canh lề/font/ngắt trang nào. `pytest tests/`
vẫn pass (5/5) sau khi thêm các file docx/pdf mới.
