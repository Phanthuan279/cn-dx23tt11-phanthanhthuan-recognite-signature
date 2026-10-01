---
title: "Phase 2: Tái cấu trúc dự án"
status: done
---

# Phase 2: Tái cấu trúc dự án

## Overview

Tạo các thư mục còn thiếu (theo bảng đối chiếu Phase 1) và cập nhật
README.md gốc để phản ánh đúng cấu trúc mới — làm nền cho Phase 3-6 viết
nội dung vào.

## Requirements

- [x] Tạo `setup/` với `setup/README.md` đầy đủ nội dung
- [x] Tạo `progress-report/` (khung thư mục, nội dung viết ở Phase 6)
- [x] Tạo `thesis/{doc,pdf,html,abs/{formulas,screenshots},refs,docgen}/`
- [x] Cập nhật `README.md` gốc: thêm mục trỏ tới `setup/`, `thesis/`, cập nhật sơ đồ cấu trúc thư mục

## Implementation Steps

1. Tạo cây thư mục: `mkdir -p setup progress-report thesis/{doc,pdf,html,abs/formulas,abs/screenshots,refs,docgen}`.
2. Viết `setup/README.md`: cài đặt (`pip install -r requirements.txt`), dữ liệu thử đã commit (`results/`), hướng dẫn tải MNIST + huấn luyện lại từ đầu (`python scripts/train.py`), chạy demo (`streamlit run app.py`) — mô phỏng đúng cấu trúc 4 mục mà `Recognite-signature/setup/README.md` dùng, nội dung thật khớp với dự án này.
3. Cập nhật `README.md`: thêm bảng liên kết tới `setup/README.md` và `thesis/pdf/thesis.pdf`; cập nhật sơ đồ cấu trúc cho khớp cây thư mục mới.
4. Không tạo nội dung `thesis/docgen/build_thesis.py`, `progress-report/progress-report.md` ở phase này — để Phase 3 và Phase 6 xử lý, tránh làm hai lần.

## Todo

- [x] Tạo cây thư mục đầy đủ
- [x] Viết `setup/README.md`
- [x] Cập nhật `README.md` gốc (liên kết + sơ đồ cấu trúc)

## Success Criteria

Đã rà soát: `find . -maxdepth 3 -type d` khớp 1-1 với bảng đối chiếu Phase
1 (trừ nội dung `thesis/doc`, `thesis/pdf`, `thesis/docgen`,
`progress-report/progress-report.md` — tạo ở phase sau, đúng kế hoạch).
`setup/README.md` tồn tại, nội dung khớp số liệu thật (235 giây SVM, 0,07
giây KNN — đối chiếu với `results/comparison_summary.json`). README.md gốc
có liên kết tới `setup/README.md` và `thesis/doc/thesis.docx` /
`thesis/pdf/thesis.pdf` (hai liên kết sau chưa trỏ tới file có thật — sẽ
có sau Phase 4, đây là tham chiếu trước có chủ đích, không phải lỗi).
`pytest tests/` vẫn pass (5/5) sau khi đổi cấu trúc.
