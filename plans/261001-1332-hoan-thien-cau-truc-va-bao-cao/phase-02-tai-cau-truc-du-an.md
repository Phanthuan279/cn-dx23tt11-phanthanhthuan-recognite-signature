---
title: "Phase 2: Tái cấu trúc dự án"
status: todo
---

# Phase 2: Tái cấu trúc dự án

## Overview

Tạo các thư mục còn thiếu (theo bảng đối chiếu Phase 1) và cập nhật
README.md gốc để phản ánh đúng cấu trúc mới — làm nền cho Phase 3-6 viết
nội dung vào.

## Requirements

- [ ] Tạo `setup/` (README hướng dẫn cài đặt sẽ viết nội dung ở bước riêng, chỉ tạo khung ở đây nếu nội dung thuộc phase khác — thực ra nội dung setup/README.md làm luôn trong phase này vì không phụ thuộc báo cáo)
- [ ] Tạo `progress-report/` (khung thư mục, nội dung viết ở Phase 6)
- [ ] Tạo `thesis/{doc,pdf,html,abs/{formulas,screenshots},refs,docgen}/`
- [ ] Cập nhật `README.md` gốc: thêm mục trỏ tới `setup/`, `thesis/`, `progress-report/`, cập nhật sơ đồ cấu trúc thư mục

## Implementation Steps

1. Tạo cây thư mục: `mkdir -p setup progress-report thesis/{doc,pdf,html,abs/formulas,abs/screenshots,refs,docgen}`.
2. Viết `setup/README.md`: cài đặt (`pip install -r requirements.txt`), dữ liệu thử đã commit (`results/`), hướng dẫn tải MNIST + huấn luyện lại từ đầu (`python scripts/train.py`), chạy demo (`streamlit run app.py`) — mô phỏng đúng cấu trúc 4 mục mà `Recognite-signature/setup/README.md` dùng, nội dung thật khớp với dự án này.
3. Cập nhật `README.md`: thêm bảng liên kết tới `setup/README.md` và `thesis/pdf/thesis.pdf`; cập nhật sơ đồ cấu trúc cho khớp cây thư mục mới.
4. Không tạo nội dung `thesis/docgen/build_thesis.py`, `progress-report/progress-report.md` ở phase này — để Phase 3 và Phase 6 xử lý, tránh làm hai lần.

## Todo

- [ ] Tạo cây thư mục đầy đủ
- [ ] Viết `setup/README.md`
- [ ] Cập nhật `README.md` gốc (liên kết + sơ đồ cấu trúc)

## Success Criteria

`ls` cây thư mục của `digit-recognition` khớp 1-1 với các mục trong bảng
đối chiếu Phase 1 (trừ nội dung `thesis/doc`, `thesis/pdf`,
`thesis/docgen`, `progress-report/progress-report.md` — tạo ở phase sau).
`setup/README.md` mô tả đúng, chạy thử được các lệnh nêu trong đó.
