---
title: Lập plan hoàn thiện cấu trúc và báo cáo đồ án cho đề tài nhận dạng chữ số
date: 2026-10-01
summary: "Người dùng yêu cầu đưa dự án lên cùng mức hoàn thiện tổ chức như dự án chữ ký cũ: cấu trúc đầy đủ, báo cáo docx/pdf chính thức, video demo. Đã lập plan 6 phase, phase 1 (rà soát) đã xong."
---

# Lập plan hoàn thiện cấu trúc và báo cáo đồ án cho đề tài nhận dạng chữ số

## What happened

Sau khi plan kỹ thuật lõi (`261001-1258-nhan-dang-chu-so-knn-svm`) đã
100% hoàn thành và rà soát qua cook, người dùng yêu cầu thêm: "rà soát lại
tất cả, video demo, đồ án pdf docx, structure dự án đã đúng như yêu cầu
chưa, phải tổ chức làm giống như cái cũ vậy, sửa lại toàn bộ báo cáo chứ".

So sánh trực tiếp cấu trúc `digit-recognition` với `Recognite-signature`
(Phase 1 của plan mới): thiếu `setup/`, `progress-report/`, toàn bộ
`thesis/{doc,pdf,html,abs,refs,docgen}/`, và chưa có video demo.

## Decision

Lập plan mới `plans/261001-1332-hoan-thien-cau-truc-va-bao-cao/` với 6
phase:
1. Rà soát cấu trúc (xong ngay trong lúc lập plan — bảng đối chiếu trực
   tiếp với Recognite-signature).
2. Tái cấu trúc dự án (tạo cây thư mục còn thiếu, viết setup/README.md).
3. Viết nội dung báo cáo (tái sử dụng hạ tầng kỹ thuật của
   `build_thesis.py` cũ -- helpers, cơ chế đánh số trang, logo -- nhưng
   viết lại toàn bộ nội dung cho đúng đề tài KNN/SVM/MNIST; quyết định rõ:
   độ dài tỉ lệ với độ phức tạp thật của đề tài, không ép đạt số trang
   bằng báo cáo chữ ký cũ vì đó là đề tài phức tạp hơn nhiều).
4. Sinh và kiểm tra báo cáo (hội tụ số trang hai lượt + xem bằng mắt --
   đúng phương pháp đã kiểm chứng hiệu quả ở dự án cũ).
5. Video demo thật bằng Playwright (Chromium đã cài sẵn trong môi trường),
   quay cả hai luồng (vẽ tay + tải ảnh), không dàn dựng kết quả giả.
6. Progress report (mốc thời gian thật từ git log) + rà soát cuối +
   commit/đẩy GitHub bằng đúng phương pháp an toàn đã kiểm chứng ở plan
   trước (fetch từ thư mục local vào Recognite-signature, push qua remote
   đã có quyền sẵn -- không tạo remote GitHub mới trỏ chéo dự án, vì cách
   đó từng bị chặn bởi lớp an toàn "Remote Repoint").

## Next steps

Thực thi Phase 2-6 (ví dụ qua `/ak:cook plans/261001-1332-hoan-thien-cau-truc-va-bao-cao/plan.md`).

> Historical work record — not durable authority. Prefer docs/specs/ADRs for current decisions.
