---
title: "Phase 1: Dữ liệu và huấn luyện mô hình"
status: done
---

# Phase 1: Dữ liệu và huấn luyện mô hình

## Overview

Tải dữ liệu MNIST thật, chia tập train/validation/test đúng cách, cài đặt
và huấn luyện hai mô hình KNN và SVM, đo và lưu lại số liệu so sánh thật
(không mô phỏng).

## Requirements

- [x] Tải MNIST thật (không phải dữ liệu giả lập) qua `sklearn.datasets.fetch_openml("mnist_784")`
- [x] Chia dữ liệu theo tỉ lệ chuẩn, có stratify theo nhãn, tập test tách biệt hoàn toàn khỏi lúc huấn luyện/chọn mô hình
- [x] Cài đặt KNN (`KNeighborsClassifier`) và SVM (`SVC`, kernel RBF)
- [x] Đo accuracy, classification report (precision/recall/F1 từng lớp), ma trận nhầm lẫn, thời gian huấn luyện cho cả hai mô hình
- [x] Lưu mô hình đã huấn luyện để dùng lại cho demo (Phase 2)

## Implementation Steps

1. `src/digitrec/data.py`: `load_mnist()` tải 70.000 ảnh 28×28 (784 chiều) qua `fetch_openml`, cache trên đĩa; `split_mnist()` chia 54.000 train / 6.000 val / 10.000 test, stratify theo chữ số.
2. `src/digitrec/models.py`: `build_knn()` (k=5, n_jobs=-1) và `build_svm()` (kernel RBF, C=5; không bật `probability=True` để tránh hiệu chỉnh Platt scaling làm chậm ~5 lần — dùng `decision_function` cho demo thay vì xác suất hiệu chỉnh).
3. `src/digitrec/evaluate.py`: `evaluate_model()` tính accuracy/classification_report/confusion_matrix; `plot_confusion_matrix()` vẽ và lưu ảnh.
4. `scripts/train.py`: chạy toàn bộ quy trình thật — tải dữ liệu, chia tập, huấn luyện từng mô hình, đánh giá trên val và test, lưu mô hình vào `models/`, lưu số liệu vào `results/`.
5. Đã thực thi thật `python scripts/train.py` một lần, đo thời gian và độ chính xác thật trên CPU.

## Todo

- [x] Viết `src/digitrec/data.py`, `models.py`, `evaluate.py`
- [x] Viết `scripts/train.py`
- [x] Chạy huấn luyện thật, xác nhận số liệu hợp lý (so với benchmark MNIST đã biết: KNN ~97%, SVM RBF ~98%)
- [x] Lưu `results/comparison_summary.json`, `results/{knn,svm}_metrics.json`, `results/confusion_matrix_{knn,svm}.png`

## Success Criteria

Kết quả thật đã đạt được (xem `results/comparison_summary.json`):

| Mô hình | Test accuracy | Val accuracy | Thời gian fit |
|---|---|---|---|
| KNN (k=5) | 97,08% | 97,35% | 0,07s |
| SVM (RBF, C=5) | 98,35% | 98,73% | 235s |

Cả hai số liệu đều khớp với kết quả benchmark KNN/SVM trên MNIST đã công bố
rộng rãi, không có dấu hiệu bất thường (rò rỉ dữ liệu, overfit nghiêm trọng,
hay lỗi tính toán).
