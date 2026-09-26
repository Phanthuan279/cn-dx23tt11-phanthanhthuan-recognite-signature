---
phase: 4
title: "Phase 4: Baseline HOG/LBP + SVM"
status: pending
priority: P1
effort: "1.5d"
dependencies: [3]
---

# Phase 4: Baseline HOG/LBP + SVM

## Context Links

- Phase trước: [Phase 3: Sinh cặp huấn luyện, chia tập theo người ký & khung đo FAR/FRR/EER/ROC](./phase-03-pairs-split-metrics-framework.md)
- Plan overview: [plan.md](./plan.md)

## Overview

- **Priority:** P1 — bắt buộc phải có trước Config A/B để làm mốc so sánh (yêu cầu người dùng: "Siamese phải thấp hơn baseline").
- **Status:** Pending
- Cài đặt baseline đặc trưng thủ công (HOG hoặc LBP) + SVM nhân RBF trên vector chênh lệch tuyệt đối giữa 2 đặc trưng ảnh, dùng đúng khung chia tập/đo lường từ Phase 3, chạy và ghi lại kết quả làm mốc.

## Key Insights

- Baseline phải dùng **cùng** `data/splits/{train,val,test}_pairs.csv` và **cùng** `src/sigverify/evaluation/metrics.py` với Siamese ở Phase 5/6 — nếu không, so sánh "Siamese thấp hơn baseline" không có ý nghĩa khoa học.
- SVM (`decision_function`) cho điểm số càng cao = càng giống lớp dương (genuine) theo quy ước sklearn mặc định — nhưng khung đo ở Phase 3 quy ước `scores` là **khoảng cách** (thấp = genuine). Baseline phải tự chuyển đổi: `score_as_distance = -svm.decision_function(X)` trước khi gọi `compute_far_frr`/`select_threshold`, để tái sử dụng đúng khung mà không sửa `metrics.py`.
- HOG trên ảnh 220×150 có thể sinh vector đặc trưng vài nghìn chiều; nếu quá lớn làm chậm `GridSearchCV`, thêm bước PCA tuỳ chọn (cấu hình được, mặc định tắt, chỉ bật nếu thời gian huấn luyện SVM vượt ngưỡng chấp nhận được).
- Grid search tham số SVM (`C`, `gamma`) chỉ được cross-validate **trong nội bộ tập train** (vd. k-fold theo cặp, hoặc theo writer con nếu muốn nghiêm ngặt hơn) — **không** được dùng tập val cho việc chọn siêu tham số SVM nếu val còn dùng để chọn ngưỡng τ theo đúng quy tắc Phase 3; val chỉ dùng cho `select_threshold`.

## Requirements

- [x] `src/sigverify/features/handcrafted.py`: hàm `extract_hog(img) -> np.ndarray` và `extract_lbp(img) -> np.ndarray`, cả hai nhận ảnh đã tiền xử lý (grayscale, chuẩn hoá `mode="unit"`, kích thước `image.size_scratch`).
- [x] `src/sigverify/training/train_baseline.py`: pipeline đầy đủ — đọc cặp từ Phase 3 → trích đặc trưng 2 ảnh → vector `|f(x1) - f(x2)|` → `GridSearchCV(SVC(kernel="rbf"), ...)` trên train → `select_threshold` trên val → `evaluate_at_threshold` trên test, tách theo `forgery_type`.
- [x] `scripts/run_baseline.py`: CLI chạy toàn bộ pipeline, lưu mô hình SVM đã fit (`models_registry/baseline_svm.joblib`) và bảng kết quả (`results/baseline/metrics.json`, kèm ROC plot `results/baseline/roc.png`).
- [x] `tests/test_baseline_features.py`: assert `extract_hog`/`extract_lbp` trả về vector 1 chiều, độ dài cố định, không đổi giữa 2 lần gọi cùng ảnh (tái lập được).

## Architecture

```
pair (img_a, img_b, label, forgery_type)
  → preprocess_image(img_a), preprocess_image(img_b)   [Phase 2, size_scratch]
  → f_a = extract_hog(img_a); f_b = extract_hog(img_b)  [hoặc extract_lbp, chọn qua config]
  → x = |f_a - f_b|
  → SVC(kernel="rbf").decision_function(x) → score_svm
  → score_distance = -score_svm                          [đổi chiều cho khớp quy ước metrics.py]

Huấn luyện: GridSearchCV trên (x_train, label_train) — cross-val nội bộ trong train, KHÔNG đụng val/test.
Ngưỡng: select_threshold(score_distance_val, label_val, method="eer") → tau_baseline
Đánh giá: evaluate_at_threshold(score_distance_test, label_test, tau_baseline), tách theo forgery_type.
```

## Related Code Files

- Create: `src/sigverify/features/handcrafted.py`
- Create: `src/sigverify/training/train_baseline.py`
- Create: `scripts/run_baseline.py`
- Create: `tests/test_baseline_features.py`
- Modify: `configs/default.yaml` — thêm `baseline.feature_type: "hog"` (giá trị `"hog"` hoặc `"lbp"`), `baseline.svm_param_grid: {C: [0.1,1,10], gamma: ["scale", 0.01, 0.001]}`, `baseline.pca_components: null`

## Implementation Steps

1. Viết `extract_hog` dùng `skimage.feature.hog` (orientations, pixels_per_cell, cells_per_block cấu hình được, giá trị mặc định hợp lý cho ảnh 220×150, vd. `pixels_per_cell=(16,16)`).
2. Viết `extract_lbp` dùng `skimage.feature.local_binary_pattern` + histogram hoá (số bins cấu hình được) để ra vector cố định chiều.
3. Viết `test_baseline_features.py` trước khi chạy pipeline đầy đủ, xác nhận tính ổn định của 2 hàm trích đặc trưng.
4. Viết `train_baseline.py::build_feature_matrix(pairs_df, feature_type) -> (X, y, forgery_type_array)`.
5. Viết `train_baseline.py::fit_svm(X_train, y_train, param_grid) -> best_estimator` dùng `GridSearchCV` với `cv` nội bộ trên train (vd. `StratifiedKFold(5)`).
6. Viết `train_baseline.py::run() -> dict` nối toàn bộ luồng ở Architecture, trả kết quả theo `forgery_type`.
7. Viết `run_baseline.py`: gọi `run()`, lưu `models_registry/baseline_svm.joblib` (`joblib.dump`), lưu `results/baseline/metrics.json` (FAR/FRR/EER/Accuracy tách theo `skilled_forgery`/`random_forgery`, cộng tổng), vẽ và lưu `results/baseline/roc.png` bằng matplotlib (2 đường ROC: skilled và random).
8. Chạy `pytest tests/test_baseline_features.py`.
9. Nếu có CEDAR thật trong môi trường thực thi: chạy `run_baseline.py` thật, ghi lại số liệu vào `results/baseline/metrics.json` — đây là **mốc so sánh bắt buộc** cho Phase 5/6.

## Todo List

- [x] `extract_hog`, `extract_lbp` ổn định, có test
- [x] `train_baseline.py` tái sử dụng đúng split + metrics từ Phase 3
- [x] Đổi chiều điểm số SVM → khoảng cách trước khi gọi `metrics.py`
- [x] `run_baseline.py` sinh `metrics.json` + `roc.png`
- [x] Kết quả baseline tách riêng skilled/random forgery

## Success Criteria

- `pytest tests/test_baseline_features.py` pass.
- `results/baseline/metrics.json` tồn tại với đầy đủ FAR/FRR/EER/Accuracy cho cả 2 loại forgery, dùng làm số tham chiếu bắt buộc khi đánh giá Phase 5/6.
- Không có đoạn code nào trong `train_baseline.py` truyền `val` vào `GridSearchCV` hoặc dùng `test` để chọn `C`/`gamma`.

## Risk Assessment

- **Rủi ro:** `GridSearchCV` chậm nếu vector HOG quá lớn × nhiều cặp. **Giảm thiểu:** bắt đầu với lưới tham số nhỏ (3×3), giới hạn số cặp train dùng cho grid search (subsample), chỉ mở rộng nếu tài nguyên cho phép; PCA tuỳ chọn nêu ở Key Insights.
- **Rủi ro:** nhầm chiều điểm số (không đảo dấu `decision_function`) khiến FAR/FRR/EER baseline bị tính sai hoàn toàn (đảo ngược ý nghĩa) mà không báo lỗi rõ ràng. **Giảm thiểu:** thêm assertion/test nhỏ — trên tập cặp tổng hợp có nhãn rõ ràng, `score_distance` trung bình của cặp `label=1` (genuine) phải thấp hơn `label=0`.

## Security Considerations

- Không phát sinh thêm rủi ro bảo mật/riêng tư (dữ liệu CEDAR nghiên cứu, không phải ảnh người dùng).

## Next Steps

- Phase 5 và 6 dùng `results/baseline/metrics.json` làm mốc so sánh bắt buộc trong báo cáo kết quả của từng cấu hình Siamese.
