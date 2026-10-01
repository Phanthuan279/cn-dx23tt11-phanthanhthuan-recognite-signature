---
title: "Hoàn thiện cấu trúc dự án và báo cáo đồ án chính thức"
description: "Đưa dự án nhận dạng chữ số viết tay lên cùng mức độ hoàn thiện tổ chức như dự án xác minh chữ ký cũ: cấu trúc thư mục đầy đủ, báo cáo đồ án chính thức (docx/pdf theo đúng biểu mẫu trình bày), video demo thật, và progress report."
status: pending
priority: P1
effort: "~1 ngày"
tags: [documentation, thesis, video, project-structure]
created: 2026-10-01
---

# Hoàn thiện cấu trúc dự án và báo cáo đồ án chính thức

## Bối cảnh

Dự án "Nhận dạng chữ số viết tay — KNN vs SVM trên MNIST" (plan trước:
`plans/261001-1258-nhan-dang-chu-so-knn-svm/`, đã 100% hoàn thành phần kỹ
thuật lõi: huấn luyện thật, demo Streamlit, test, đã đẩy lên GitHub) hiện
chỉ có cấu trúc tối giản (`src/`, `scripts/`, `app.py`, `tests/`,
`results/`, `README.md`). Dự án xác minh chữ ký cũ (`Recognite-signature`)
có mức độ hoàn thiện tổ chức cao hơn nhiều: thư mục `setup/` (hướng dẫn cài
đặt), `progress-report/` (nhật ký tiến độ với mốc thời gian thật),
`thesis/{doc,pdf,html,abs,refs,docgen}/` (báo cáo đồ án chính thức theo
đúng biểu mẫu trình bày của Trường Đại học Trà Vinh — bìa, mục lục, nhận
xét, chương, phụ lục, tài liệu tham khảo), và một video demo.

Người dùng yêu cầu: rà soát lại toàn bộ, kiểm tra cấu trúc đã đúng yêu cầu
chưa, tổ chức dự án này giống như dự án cũ, viết lại báo cáo đồ án đầy đủ
(pdf/docx), và có video demo.

## Mục tiêu

| # | Mục tiêu | Ưu tiên |
|---|------|----------|
| 1 | Cấu trúc thư mục đầy đủ, đúng quy ước như dự án cũ (`setup/`, `progress-report/`, `thesis/{doc,pdf,html,abs,refs,docgen}/`) | P1 |
| 2 | Báo cáo đồ án chính thức (.docx/.pdf) theo đúng biểu mẫu trình bày chính thức của trường, nội dung thật về KNN/SVM/MNIST | P1 |
| 3 | Video demo thật, quay lại luồng sử dụng ứng dụng Streamlit | P1 |
| 4 | Progress report với mốc thời gian thật (lấy từ `git log`) | P2 |

## Phạm vi

**Trong phạm vi**: tái sử dụng hạ tầng sinh báo cáo đã có (`build_thesis.py`
của dự án cũ — các hàm tiện ích `add_para`, `add_heading`, `add_image`,
`add_table`, cơ chế đánh số trang La Mã/Ả Rập, logo trường) nhưng viết lại
toàn bộ NỘI DUNG cho đúng đề tài này (không copy nội dung chữ ký sang); độ
dài báo cáo tỉ lệ thuận với độ phức tạp thật của đề tài (KNN/SVM cổ điển
trên MNIST đơn giản hơn nhiều so với mạng Siamese — báo cáo sẽ ngắn hơn một
cách tự nhiên, không độn trang cho đủ số lượng).

**Ngoài phạm vi**: không sửa đổi gì trong dự án `Recognite-signature` (chỉ
đọc để tham khảo cấu trúc/hạ tầng); không tạo lại các thí nghiệm kỹ thuật
đã xong (huấn luyện, demo) — chỉ bổ sung tài liệu/tổ chức xung quanh phần
kỹ thuật đã có.

## Phases

| # | Phase | Status |
|---|-------|--------|
| 1 | [Phase 1: Rà soát cấu trúc hiện tại](./phase-01-start.md) | Done |
| 2 | [Phase 2: Tái cấu trúc dự án](./phase-02-tai-cau-truc-du-an.md) | Done |
| 3 | [Phase 3: Viết nội dung báo cáo](./phase-03-viet-noi-dung-bao-cao.md) | Pending |
| 4 | [Phase 4: Sinh và kiểm tra báo cáo](./phase-04-sinh-va-kiem-tra-bao-cao.md) | Pending |
| 5 | [Phase 5: Video demo](./phase-05-video-demo.md) | Pending |
| 6 | [Phase 6: Progress report và rà soát cuối](./phase-06-progress-report-va-ra-soat-cuoi.md) | Pending |

## Success Criteria

- [ ] Cấu trúc thư mục khớp với quy ước dự án cũ (đối chiếu từng mục)
- [ ] `thesis/doc/thesis.docx` và `thesis/pdf/thesis.pdf` tồn tại, đúng biểu mẫu trình bày chính thức, nội dung thật 100% (số liệu từ `results/comparison_summary.json`, không mô phỏng)
- [ ] Video demo thật, cho thấy luồng sử dụng (vẽ/tải ảnh → xem dự đoán KNN và SVM)
- [ ] `progress-report/progress-report.md` với mốc thời gian thật từ `git log`
- [ ] `setup/README.md` hướng dẫn cài đặt/tái tạo đầy đủ
- [ ] README.md gốc cập nhật đúng cấu trúc mới
- [ ] Toàn bộ đã commit và đẩy lên nhánh `nhan-dang-chu-so-viet-tay`

## Dependencies

Phụ thuộc vào plan trước đã hoàn thành:
`plans/261001-1258-nhan-dang-chu-so-knn-svm/` (kết quả thật KNN/SVM, demo
app đã sửa lỗi canvas, đã đẩy GitHub). Không có plan nào phụ thuộc vào plan
này.

<!-- slug: hoan-thien-cau-truc-va-bao-cao -->
