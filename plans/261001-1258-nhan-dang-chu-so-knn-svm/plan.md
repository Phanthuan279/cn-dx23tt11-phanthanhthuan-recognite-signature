---
title: "Nhận dạng chữ số viết tay — So sánh KNN và SVM trên MNIST"
description: "Huấn luyện và so sánh KNN/SVM trên MNIST thật, kèm demo Streamlit minh họa, đúng đề tài đồ án thực tập chuyên ngành đã được phân."
status: completed
priority: P1
effort: "~1 ngày (đã hoàn thành phần lõi trong 1 phiên)"
tags: [machine-learning, mnist, knn, svm, streamlit]
created: 2026-10-01
---

# Nhận dạng chữ số viết tay — So sánh KNN và SVM trên MNIST

## Bối cảnh

Đồ án trước đó (xác minh chữ ký bằng mạng Siamese) hóa ra không khớp với đề
tài thật sự được phân. Đề tài đúng, theo xác nhận trực tiếp của sinh viên,
là **"Nhận dạng chữ số viết tay"**, với yêu cầu cụ thể như sau (trích từ
brief đề tài):

- **Mục tiêu**: Tìm hiểu về học máy; xây dựng mô hình học máy và ứng dụng
  minh họa hoạt động được, giải quyết đúng bài toán của đề tài và có dữ
  liệu minh họa để trình diễn.
- **Yêu cầu triển khai**: Huấn luyện và so sánh hiệu quả của mô hình học
  máy KNN và SVM trên tập dữ liệu MNIST.
- **Công nghệ gợi ý**: Python; Scikit-learn; TensorFlow/Keras; Streamlit
  (có thể thay bằng công nghệ tương đương nếu giải thích được lựa chọn và
  bảo đảm sản phẩm chạy ổn định).

Plan này ghi lại đúng phạm vi đề tài và đối chiếu với phần đã triển khai
thực tế tại `/home/user/digit-recognition`, để có một bản ghi rõ ràng, có
thể kiểm chứng, không lẫn với dự án chữ ký cũ.

## Mục tiêu

| # | Mục tiêu | Ưu tiên |
|---|------|----------|
| 1 | Huấn luyện KNN và SVM trên dữ liệu MNIST thật, đo và so sánh độ chính xác | P1 |
| 2 | Xây dựng ứng dụng demo Streamlit minh họa mô hình hoạt động thật | P1 |
| 3 | Tài liệu hóa đầy đủ (README, kết quả thật), có unit test, sẵn sàng công bố mã nguồn | P2 |

## Phạm vi

**Trong phạm vi**: tải dữ liệu MNIST thật qua `scikit-learn`; cài đặt và
huấn luyện KNN (`KNeighborsClassifier`) và SVM (`SVC`, kernel RBF); đánh
giá bằng accuracy, classification report, ma trận nhầm lẫn trên tập test
tách biệt; ứng dụng Streamlit cho phép vẽ/tải ảnh chữ số và xem dự đoán của
cả hai mô hình; unit test trên dữ liệu tổng hợp (không cần tải MNIST).

**Ngoài phạm vi**: mạng nơ-ron sâu (CNN/TensorFlow) — công nghệ gợi ý có
đề cập TensorFlow/Keras nhưng yêu cầu triển khai cụ thể chỉ nêu KNN và SVM;
có thể bổ sung một mô hình CNN như phần mở rộng tùy chọn nếu sinh viên
muốn, nhưng không phải yêu cầu bắt buộc của đề tài.

## Phases

| # | Phase | Status |
|---|-------|--------|
| 1 | [Phase 1: Dữ liệu và huấn luyện mô hình](./phase-01-start.md) | Done |
| 2 | [Phase 2: Demo Streamlit](./phase-02-demo-streamlit.md) | Done |
| 3 | [Phase 3: Tài liệu, kiểm thử và công bố mã nguồn](./phase-03-tai-lieu-kiem-thu-cong-bo.md) | In Progress |

## Kết quả thật đã đạt được

Huấn luyện thật trên MNIST thật (70.000 ảnh qua `sklearn.datasets.fetch_openml`),
chia chuẩn 54.000 train / 6.000 validation / 10.000 test:

| Mô hình | Test accuracy | Thời gian huấn luyện |
|---|---|---|
| KNN (k=5) | 97,08% | 0,07 giây |
| SVM (kernel RBF, C=5) | 98,35% | 235 giây |

Chi tiết: `results/comparison_summary.json`, `results/confusion_matrix_knn.png`,
`results/confusion_matrix_svm.png`.

## Success Criteria

- [x] Dữ liệu MNIST thật được tải và chia train/val/test đúng cách (không rò rỉ dữ liệu test)
- [x] KNN và SVM huấn luyện thật, có số liệu thật (accuracy, thời gian, ma trận nhầm lẫn)
- [x] Ứng dụng demo Streamlit chạy được, nhận ảnh/vẽ tay và trả kết quả dự đoán của cả hai mô hình
- [x] Unit test chạy được không cần tải MNIST (dữ liệu tổng hợp), toàn bộ pass
- [x] README mô tả đúng đề tài, cài đặt, cách chạy lại, và số liệu thật
- [ ] Mã nguồn đã được đẩy lên repository GitHub (`cn-dx23tt11-phanthanhthuan-digit-recognition`) — đang chờ sinh viên tạo repo trống (Claude không có quyền tự tạo repo mới)

## Dependencies

Không phụ thuộc dự án `Recognite-signature` (xác minh chữ ký) — đây là một
đề tài, một repository hoàn toàn riêng biệt.

<!-- slug: nhan-dang-chu-so-knn-svm -->
