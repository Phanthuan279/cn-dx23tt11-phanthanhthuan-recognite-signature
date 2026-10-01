---
title: "Phase 4: Sinh và kiểm tra báo cáo"
status: todo
---

# Phase 4: Sinh và kiểm tra báo cáo

## Overview

Sinh `.docx`/`.pdf` từ `build_thesis.py`, hội tụ số trang mục lục bằng
phương pháp hai lượt đã dùng ở dự án cũ (render → đo số trang thật bằng
`pdftotext -layout` → cập nhật mục lục → render lại → xác nhận khớp), và
xác minh bằng mắt từng trang quan trọng (bìa, mục lục, các chương, phụ
lục) — không chỉ tin vào việc script chạy không lỗi.

## Requirements

- [ ] `.docx` sinh ra không lỗi, convert sang `.pdf` bằng LibreOffice không lỗi
- [ ] Mục lục khớp chính xác số trang thật (phương pháp hai lượt)
- [ ] Trang bìa đúng biểu mẫu (logo, canh giữa/canh trái đúng như đã sửa ở dự án cũ)
- [ ] Mỗi chương, công thức, bảng, hình hiển thị đúng khi render ra ảnh kiểm tra bằng mắt

## Implementation Steps

1. Chạy `python thesis/docgen/build_thesis.py`, copy `thesis/docgen/thesis.docx` sang `thesis/doc/thesis.docx` (đúng quy ước đã dùng ở dự án cũ — script ghi vào `docgen/` trước, `doc/` là bản chính thức).
2. Convert sang PDF bằng `office.soffice.run_soffice` (skill docx đã dùng trước đó).
3. Đo số trang thật từng heading bằng `pdftotext -layout` + `\f`, cập nhật `TOC_ENTRIES`, chạy lại bước 1-2, xác nhận hội tụ (không còn lệch số trang nào).
4. Render các trang quan trọng ra ảnh (`pdftoppm -jpeg -r 100-150`) và xem bằng mắt: bìa chính, bìa lót, mục lục, trang đầu mỗi chương, phụ lục, tài liệu tham khảo — xác nhận không có lỗi canh lề/font/ngắt trang giống các lỗi đã gặp ở dự án cũ (ngắt dòng tiêu đề xấu, canh giữa/trái sai, tràn trang).
5. Chạy `pytest tests/` để xác nhận không có gì bị hỏng do thêm file mới vào dự án (không mong đợi test nào liên quan tới docx, nhưng xác nhận cho chắc).

## Todo

- [ ] Sinh docx/pdf lần đầu
- [ ] Hội tụ số trang mục lục (hai lượt)
- [ ] Render và xem bằng mắt các trang quan trọng
- [ ] Sửa mọi lỗi hiển thị phát hiện được trước khi coi là xong

## Success Criteria

Mục lục khớp số trang thật tuyệt đối. Xem bằng mắt xác nhận bìa, mục lục,
từng chương, phụ lục không có lỗi hiển thị. `pytest tests/` vẫn pass.
