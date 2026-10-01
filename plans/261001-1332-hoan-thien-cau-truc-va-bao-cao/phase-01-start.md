---
title: "Phase 1: Rà soát cấu trúc hiện tại"
status: done
---

# Phase 1: Rà soát cấu trúc hiện tại

## Overview

Đối chiếu cấu trúc thư mục hiện tại của `digit-recognition` với dự án
`Recognite-signature` để xác định chính xác những gì còn thiếu trước khi
tái cấu trúc (Phase 2), tránh làm thiếu hoặc thừa.

## Kết quả rà soát (đã thực hiện)

So sánh `/home/user/digit-recognition` hiện tại với
`/home/user/Recognite-signature`:

| Mục | Recognite-signature | digit-recognition | Trạng thái |
|---|---|---|---|
| `README.md` | Có, đầy đủ | Có, đầy đủ nhưng thiếu mục trỏ tới `setup/`, `thesis/`, `progress-report/` | Cần cập nhật |
| `setup/README.md` | Có | Không có | **Thiếu** |
| `progress-report/progress-report.md` | Có, mốc thời gian thật từ `git log` | Không có | **Thiếu** |
| `thesis/doc/thesis.docx` | Có | Không có | **Thiếu** |
| `thesis/pdf/thesis.pdf` | Có | Không có | **Thiếu** |
| `thesis/docgen/build_thesis.py` | Có (2152 dòng, sinh báo cáo 67 trang) | Không có | **Thiếu** |
| `thesis/abs/` (hình, công thức, logo, ảnh chụp màn hình) | Có | Không có | **Thiếu** |
| `thesis/html/`, `thesis/refs/` | Có (trống, dự phòng) | Không có | **Thiếu** |
| Video demo | Không có trong repo (chỉ nhắc tới trong README là "nếu có") | Không có | Cần tạo mới |
| `src/<package>/` | `src/sigverify/` | `src/digitrec/` | Đã có, đúng quy ước |
| `scripts/` | Có | Có (`scripts/train.py`) | Đã có |
| `tests/` | Có | Có (5 test, pass) | Đã có |
| `results/` (số liệu thật, đã commit) | Có | Có (`comparison_summary.json`, ma trận nhầm lẫn) | Đã có |
| `plans/` | Có | Có (2 plan) | Đã có |

## Requirements

- [x] Liệt kê đầy đủ các mục còn thiếu so với dự án cũ
- [x] Xác nhận các mục đã có không cần làm lại

## Success Criteria

Bảng đối chiếu ở trên là căn cứ duy nhất cho phạm vi Phase 2-6 — không bổ
sung mục nào ngoài bảng này trừ khi phát sinh nhu cầu thật trong lúc làm.
