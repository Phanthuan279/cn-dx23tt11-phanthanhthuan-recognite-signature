---
title: "Phát hiện sai đề tài: chuyển từ xác minh chữ ký sang nhận dạng chữ số viết tay"
date: 2026-10-01
summary: "Đồ án Siamese/chữ ký trước đó sai đề tài; đề tài thật là KNN/SVM trên MNIST — đã xây dựng lại đúng, có kết quả thật, chờ push GitHub."
---

# Phát hiện sai đề tài: chuyển từ xác minh chữ ký sang nhận dạng chữ số viết tay

## Bối cảnh

Dự án trước đó (`Recognite-signature`, repo GitHub `Phanthuan279/cn-dx23tt11-phanthanhthuan-recognite-signature`)
đã xây dựng một hệ thống xác minh chữ ký viết tay offline bằng mạng Siamese
(contrastive/triplet loss, CEDAR + BHSig260, Config A/B, ablations thật —
nhiều giờ huấn luyện CPU thật). Đề cương chi tiết nộp cho dự án đó có tiêu
đề "NHẬN DẠNG CHỮ SỐ VIẾT TAY" nhưng toàn bộ 19 trang nội dung thân bài lại
mô tả xác minh chữ ký — ban đầu được đánh giá là lỗi gõ còn sót lại từ
template, dựa trên tính nhất quán nội bộ của tài liệu.

Người dùng sau đó dán nguyên văn brief đề tài thật (Mục tiêu / Yêu cầu
triển khai / Công nghệ gợi ý) ghi rõ: "Huấn luyện và so sánh hiệu quả của
mô hình học máy KNN và SVM trên tập dữ liệu MNIST" — hoàn toàn khác với nội
dung đề cương đã nộp. Khi hỏi lại, người dùng xác nhận: đây đúng là đề tài
thật đã được phân (đã tự kiểm tra lại), và đề cương đã nộp (nội dung chữ
ký) **chỉ mới nộp, chưa được GVHD duyệt**.

## What happened

- Dừng ngay tiến trình huấn luyện T3 (Config B margin=2.0) đang chạy thật
  trên CPU, vì tiếp tục sẽ lãng phí tài nguyên cho đề tài sai.
- Xác nhận với người dùng qua AskUserQuestion: có nên bắt tay xây đề tài
  thật ngay không (có), và đặt ở đâu (repo/thư mục hoàn toàn mới, tách biệt
  khỏi dự án chữ ký).
- Tạo dự án mới tại `/home/user/digit-recognition`:
  - `src/digitrec/{data,models,evaluate}.py`: tải MNIST thật qua
    `sklearn.datasets.fetch_openml`, chia 54000/6000/10000 train/val/test,
    xây KNN (`KNeighborsClassifier`) và SVM (`SVC`, kernel RBF).
  - Đo thời gian thật trên subset trước khi chạy full (10k: SVM 14.9s;
    20k: 47.4s) để ước lượng full 54k sẽ khả thi (~235s thực tế, không
    cần chia nhỏ thành nhiều lần chạy nền như dự án chữ ký trước).
  - `scripts/train.py` chạy huấn luyện thật một lần, kết quả: KNN
    97.08% test accuracy (fit 0.07s), SVM RBF 98.35% test accuracy (fit
    235s) — khớp với benchmark MNIST đã biết, không có dấu hiệu rò rỉ
    dữ liệu hay lỗi tính toán.
  - `app.py`: demo Streamlit (vẽ/tải ảnh chữ số, so sánh dự đoán + độ
    tin cậy của cả hai mô hình). Phát hiện và sửa một lỗi nhỏ: SVC với
    `probability=True` làm chậm huấn luyện ~5 lần do Platt scaling nội
    bộ — đổi sang dùng `decision_function()` + softmax làm điểm tin cậy
    ước lượng cho SVM thay vì xác suất hiệu chỉnh.
  - Khởi chạy thật `streamlit run app.py` ở chế độ headless, xác nhận
    HTTP 200 và health check `ok`, dọn dẹp tiến trình dev server sau khi
    verify (tránh để tiến trình treo).
  - 4 unit test trên dữ liệu tổng hợp (không cần tải MNIST), README đầy
    đủ, `.gitignore` loại trừ mô hình nặng (`models/*`, tái tạo được) và
    cache MNIST.
  - `git init`, đổi nhánh mặc định sang `main`, commit toàn bộ.
- Thử tạo repository GitHub mới (`cn-dx23tt11-phanthanhthuan-digit-recognition`
  dưới tài khoản `Phanthuan279`) qua `mcp__github__create_repository`: bị
  GitHub từ chối (403 — tích hợp không có quyền tạo repo ở cấp tài khoản).
  Gọi tiếp `read_documentation` để tìm hướng giải quyết thì bị lớp an toàn
  "auto mode classifier" chặn thêm với lý do "Create Public Surface" —
  đúng theo thiết kế, tạo bề mặt công khai mới cần người dùng xác nhận
  trước, không phải lỗi cần sửa.
- Tạo plan chính thức tại `plans/261001-1258-nhan-dang-chu-so-knn-svm/`
  (3 phase: dữ liệu+huấn luyện, demo, tài liệu+công bố), validate pass,
  86% hoàn thành (26/30 mục), chỉ còn chặn ở bước đẩy mã nguồn lên GitHub.

## Decision

- Giữ nguyên toàn bộ dự án `Recognite-signature` (không xóa) — là công
  việc thật, có giá trị, chỉ là không khớp đề tài được phân; để người dùng
  tự quyết định việc trao đổi với GVHD xem có xin đổi/giữ đề tài hay không.
- Xây dựng đề tài đúng (KNN/SVM/MNIST) hoàn toàn trong một repository mới,
  không gộp chung với dự án cũ, theo đúng quy ước đặt tên repo đã dùng
  trước đó (`cn-<malop>-<hotenkhongdau>-<shortname>`).
- Không tự ý tạo repository GitHub công khai thay người dùng khi bị hệ
  thống an toàn chặn — báo lại và chờ người dùng tạo repo trống.

## Next steps

- Chờ người dùng tạo repo GitHub trống `cn-dx23tt11-phanthanhthuan-digit-recognition`
  dưới tài khoản `Phanthuan279`.
- Sau khi có repo: `add_repo`, `git remote add origin`, `git push -u origin main`.
- Tùy người dùng: cân nhắc có cần viết báo cáo đồ án dạng văn bản (theo
  biểu mẫu trình bày chính thức của trường, như đã làm cho dự án chữ ký)
  cho đề tài KNN/SVM này hay không — hiện chưa được yêu cầu, chưa làm.

> Historical work record — not durable authority. Prefer docs/specs/ADRs for current decisions.
