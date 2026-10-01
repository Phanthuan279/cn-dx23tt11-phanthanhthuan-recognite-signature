---
title: "Phase 3: Tài liệu, kiểm thử và công bố mã nguồn"
status: in-progress
---

# Phase 3: Tài liệu, kiểm thử và công bố mã nguồn

## Overview

Hoàn thiện tài liệu dự án (README), viết unit test không phụ thuộc mạng
(chạy trên dữ liệu tổng hợp), khởi tạo git, và công bố mã nguồn lên một
repository GitHub mới, tách biệt hoàn toàn khỏi dự án xác minh chữ ký cũ.

## Requirements

- [x] README mô tả đúng đề tài, kết quả thật, cấu trúc dự án, cách cài đặt/chạy lại
- [x] Unit test chạy được mà không cần tải MNIST (dùng dữ liệu tổng hợp 10 lớp tách biệt rõ)
- [x] `.gitignore` loại trừ mô hình đã huấn luyện (lớn, tái tạo được) và cache dữ liệu MNIST
- [x] Khởi tạo git repository local, commit toàn bộ mã nguồn + kết quả thật
- [ ] Repository GitHub mới được tạo và mã nguồn được đẩy lên

## Implementation Steps

1. `README.md`: mô tả đề tài, bảng kết quả thật (KNN 97,08%, SVM 98,35%), cấu trúc thư mục, hướng dẫn cài đặt/huấn luyện lại/chạy demo.
2. `tests/test_pipeline.py`: 4 test trên dữ liệu tổng hợp (10 cụm Gaussian tách biệt rõ đóng vai trò 10 chữ số) — kiểm tra KNN/SVM fit và predict đúng, `evaluate_model()` trả về đúng cấu trúc, `plot_confusion_matrix()` ghi file thật.
3. `.gitignore`: loại `models/*` (các file `.joblib` nặng, tái tạo bằng `scripts/train.py`) và `data/` (cache tải MNIST của sklearn).
4. `git init`, đổi nhánh mặc định sang `main`, `git add -A`, commit với mô tả rõ lý do đổi đề tài và số liệu thật đạt được.
5. **Chặn thực tế**: gọi `mcp__github__create_repository` để tạo repo mới bị GitHub từ chối (403 — tích hợp Claude Code không có quyền tạo repository ở cấp tài khoản), và lệnh gọi theo sau (`read_documentation`) bị lớp an toàn "auto mode classifier" chặn thêm với lý do "Create Public Surface" — tạo bề mặt công khai mới cần xác nhận rõ ràng của người dùng trước.
6. Đã báo người dùng: tạo trống repository `cn-dx23tt11-phanthanhthuan-digit-recognition` dưới tài khoản `Phanthuan279`, sau đó Claude sẽ `add_repo` + `git push`.

## Todo

- [x] Viết README.md
- [x] Viết tests/test_pipeline.py, chạy pass 4/4
- [x] Viết .gitignore
- [x] git init, đổi nhánh main, commit toàn bộ
- [ ] Người dùng tạo repo GitHub trống `cn-dx23tt11-phanthanhthuan-digit-recognition`
- [ ] Claude `add_repo` repo mới vào phiên làm việc
- [ ] `git remote add origin ...` + `git push -u origin main`

## Success Criteria

Repository GitHub công khai (hoặc riêng tư, tùy người dùng chọn) chứa toàn
bộ mã nguồn, kết quả thật, và README — có thể clone về và chạy lại
`pytest tests/` thành công ngay, chạy lại `python scripts/train.py` để tái
tạo đúng số liệu đã báo cáo.
