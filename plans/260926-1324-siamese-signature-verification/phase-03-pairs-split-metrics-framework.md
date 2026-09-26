---
phase: 3
title: "Phase 3: Sinh cặp huấn luyện, chia tập theo người ký & khung đo FAR/FRR/EER/ROC"
status: pending
priority: P1
effort: "2d"
dependencies: [2]
---

# Phase 3: Sinh cặp huấn luyện, chia tập theo người ký & khung đo FAR/FRR/EER/ROC

## Context Links

- Phase trước: [Phase 2: Tải/khảo sát CEDAR & pipeline tiền xử lý ảnh](./phase-02-data-acquisition-preprocessing.md)
- Plan overview: [plan.md](./plan.md)

## Overview

- **Priority:** P1 — đây là phần hạ tầng dùng chung cho mọi mô hình (baseline, Config A, Config B), sai ở đây thì mọi kết quả sau đều sai.
- **Status:** Pending
- Cài đặt: (1) chia 55 signer CEDAR thành train/val/test writer-disjoint; (2) sinh 3 loại cặp (dương, âm khó, âm dễ) theo tỉ lệ cấu hình được; (3) khung tính FAR/FRR/EER/Accuracy/ROC-AUC dùng chung cho mọi mô hình, với quy tắc chọn ngưỡng τ chỉ trên validation rồi đóng băng khi test.

## Key Insights

- **Chống rò rỉ dữ liệu (data leakage) là ưu tiên số 1 của phase này** — hai loại rò rỉ phải được chặn bằng code + test, không chỉ bằng quy ước tài liệu:
  1. **Rò rỉ người ký:** một `writer_id` không được xuất hiện ở nhiều hơn một tập trong {train, val, test}.
  2. **Rò rỉ ngưỡng:** hàm chọn ngưỡng τ chỉ được nhận điểm số/nhãn của **validation**; hàm đánh giá test nhận τ đã cố định làm tham số đầu vào, không được tự tính lại τ từ dữ liệu test.
- **Bùng nổ tổ hợp cặp:** với 24 ảnh thật/người, cặp dương tối đa `C(24,2)=276`/người; cặp âm khó (thật×giả) tối đa `24×24=576`/người. Không vật liệu hoá toàn bộ tổ hợp — lấy mẫu ngẫu nhiên có seed mỗi epoch (hoặc một lần với số lượng giới hạn per signer, cấu hình được) để giữ kích thước dataset hợp lý.
- **Tỉ lệ 3 loại cặp:** giữ dương:âm ≈ 1:1 mỗi batch theo yêu cầu người dùng; trong nửa "âm", chia mặc định 1:1 giữa âm khó (giả kỹ năng cao) và âm dễ (người khác) → tỉ lệ tổng thể mặc định dương:âm-khó:âm-dễ = 2:1:1, tham số hoá qua `pairs.ratio_pos_hardneg_easyneg` (đã có trong `configs/default.yaml` từ Phase 1) để Phase 7 ablate được.
- **"Giả mạo ngẫu nhiên" vs "giả mạo chuyên nghiệp" trong báo cáo:** ánh xạ trực tiếp — cặp âm dễ (khác người ký) = random forgery; cặp âm khó (giả CEDAR cùng người) = skilled forgery. Khung đo phải tính FAR/FRR/EER **tách riêng cho từng loại**, không gộp chung.
- **Chọn điểm EER khi không có giao điểm chính xác:** vì τ được quét trên lưới rời rạc, FAR(τ) và FRR(τ) hiếm khi bằng nhau tuyệt đối — dùng nội suy tuyến tính giữa hai điểm quét gần nhất nơi FAR-FRR đổi dấu để lấy EER và τ* tương ứng.

## Requirements

- [ ] `src/sigverify/pairs/splits.py`: hàm `writer_disjoint_split(writer_ids, n_train=40, n_val=5, n_test=10, seed) -> dict` trả về 3 danh sách `writer_id` rời nhau, lưu kết quả ra `data/splits/cedar_writer_split.json` (file này **được commit**, đảm bảo mọi lần chạy lại dùng đúng 1 split).
- [ ] `src/sigverify/pairs/generator.py`: hàm `generate_pairs(df_signatures, writer_ids, ratio, pairs_per_writer, seed) -> list[(path_a, path_b, label, forgery_type)]` với `forgery_type ∈ {"genuine_genuine", "skilled_forgery", "random_forgery"}`.
- [ ] `src/sigverify/evaluation/metrics.py`: hàm `compute_far_frr(scores, labels) -> (far_array, frr_array, thresholds)`, `find_eer(far_array, frr_array, thresholds) -> (eer, tau_star)`, `select_threshold(val_scores, val_labels, method="eer") -> tau`, `evaluate_at_threshold(test_scores, test_labels, tau) -> dict{accuracy, far, frr}`, `roc_auc(scores, labels) -> (fpr, tpr, auc)`. Tất cả hàm nhận `scores` là **khoảng cách D** (thấp = giống thật) — quy ước thống nhất chiều số cho mọi mô hình (Siamese, baseline SVM) dùng chung khung này.
- [ ] Test bắt buộc chứng minh chống rò rỉ: `tests/test_pairs.py::test_no_writer_overlap_across_splits` và `tests/test_pairs.py::test_threshold_not_fit_on_test` (kiểm tra bằng cách mock/assert chữ ký hàm, không cho `evaluate_at_threshold` nhận `val_scores`).
- [ ] `tests/test_metrics.py` với ca biết trước đáp án: điểm số phân tách hoàn hảo → EER ≈ 0; điểm số ngẫu nhiên hoàn toàn chồng lấp (cùng phân phối cho cả 2 lớp) → EER ≈ 0.5.

## Architecture

```
writer_ids (55)
  └── writer_disjoint_split() ──► {train: 40, val: 5, test: 10} writer_id, lưu data/splits/cedar_writer_split.json

Với mỗi tập con (train/val/test):
  generate_pairs(df, writer_ids_of_this_split, ratio, pairs_per_writer, seed)
    ├── genuine_genuine: 2 ảnh thật cùng người, label=1 (same)
    ├── skilled_forgery: 1 thật + 1 giả CEDAR cùng người, label=0 (different), forgery_type="skilled_forgery"
    └── random_forgery : 1 thật của người X + 1 thật của người Y≠X, label=0, forgery_type="random_forgery"

Quy trình đánh giá (dùng chung mọi mô hình):
  val_scores, val_labels   → select_threshold(method="eer") → tau*      [CHỈ trên val]
  test_scores, test_labels, tau* → evaluate_at_threshold()              [tau* đã đóng băng]
  Báo cáo FAR/FRR/EER/Accuracy tách riêng theo forgery_type ∈ {skilled_forgery, random_forgery}
  roc_auc() cho ROC/AUC tổng và theo từng forgery_type
```

## Related Code Files

- Create: `src/sigverify/pairs/splits.py`
- Create: `src/sigverify/pairs/generator.py`
- Create: `src/sigverify/evaluation/metrics.py`
- Create: `scripts/build_pairs.py` (CLI mỏng: đọc config → gọi split + generate_pairs → lưu `data/splits/{train,val,test}_pairs.csv`)
- Create: `tests/test_pairs.py`
- Create: `tests/test_metrics.py`

## Implementation Steps

1. Viết `writer_disjoint_split`: shuffle `writer_ids` với seed cố định, cắt theo `n_train/n_val/n_test` (mặc định 40/5/10, phải bằng tổng số signer thật của CEDAR đã tải ở Phase 2 — nếu tổng khác 55, log cảnh báo và giữ tỉ lệ tương đối).
2. Viết `generate_pairs` — với mỗi writer trong tập, lấy mẫu ngẫu nhiên (không lặp lại trong cùng lần gọi) số lượng cặp mỗi loại theo `ratio` và `pairs_per_writer`; với `random_forgery`, chọn writer khác ngẫu nhiên trong **cùng tập split** (không bao giờ trộn writer khác split vào, kể cả để làm "người khác").
3. Viết `metrics.py::compute_far_frr` — quét τ trên dải giá trị `scores` quan sát được (ví dụ 200 điểm chia đều min–max), với mỗi τ: `FAR = mean(scores[labels==0] < τ)`, `FRR = mean(scores[labels==1] >= τ)`.
4. Viết `find_eer` — tìm chỉ số nơi `FAR - FRR` đổi dấu, nội suy tuyến tính giữa 2 điểm lân cận để ra `(eer, tau_star)`.
5. Viết `select_threshold(val_scores, val_labels, method)` — `method="eer"` gọi `find_eer` trên val; `method="max_accuracy"` quét τ tìm accuracy cao nhất trên val. Trả về **chỉ** `tau`, không trả về cấu trúc nào chứa dữ liệu test.
6. Viết `evaluate_at_threshold(test_scores, test_labels, tau)` — chữ ký hàm **không nhận** `val_scores`/`val_labels`, chỉ nhận `tau` đã tính sẵn — đây là ràng buộc kiểm chứng được bằng test.
7. Viết `roc_auc` dùng `sklearn.metrics.roc_curve`/`roc_auc_score` với `y_score = -scores` (đảo dấu vì AUC quy ước điểm cao = positive, còn khoảng cách thấp = genuine).
8. Viết `build_pairs.py`: chạy toàn bộ pipeline trên CEDAR thật (nếu có ở môi trường thực thi) hoặc báo rõ "cần Phase 2 hoàn tất với dữ liệu thật" nếu chưa có.
9. Viết `test_pairs.py`: dựng `writer_ids` giả (vd. 1..55), gọi `writer_disjoint_split`, assert 3 tập rời nhau và hợp đủ toàn bộ; gọi `generate_pairs` trên DataFrame tổng hợp nhỏ, assert đúng tỉ lệ ±dung sai và không có cặp `random_forgery` xuyên writer khác split.
10. Viết `test_metrics.py` với 2 ca biết trước đáp án nêu ở Requirements, cộng thêm 1 ca kiểm tra `evaluate_at_threshold` không truy cập biến val (dùng kỹ thuật đơn giản: gọi hàm chỉ với 3 tham số `test_scores, test_labels, tau` — nếu chữ ký hàm khác đi test này tự fail).
11. `pytest tests/test_pairs.py tests/test_metrics.py`.

## Todo List

- [ ] `writer_disjoint_split` + file split được commit
- [ ] `generate_pairs` đúng 3 loại, đúng tỉ lệ cấu hình được
- [ ] `metrics.py` đầy đủ FAR/FRR/EER/Accuracy/ROC-AUC, tách theo forgery_type
- [ ] Test chống rò rỉ writer pass
- [ ] Test chống rò rỉ ngưỡng pass
- [ ] Test EER trên ca biết trước đáp án pass

## Success Criteria

- `pytest tests/test_pairs.py tests/test_metrics.py` pass toàn bộ.
- `data/splits/cedar_writer_split.json` tồn tại, 3 danh sách writer rời nhau, tổng đúng số signer thật.
- Không có bất kỳ đường gọi code nào trong `src/sigverify/evaluation/metrics.py` cho phép `evaluate_at_threshold` nhận dữ liệu val.

## Risk Assessment

- **Rủi ro:** lấy mẫu cặp ngẫu nhiên không seed cố định → kết quả không tái lập giữa các lần chạy/so sánh Config A vs B không công bằng. **Giảm thiểu:** mọi hàm sinh cặp nhận `seed` bắt buộc, log seed dùng vào file cấu hình đi kèm mỗi lần chạy.
- **Rủi ro:** với 5 signer ở validation, cặp âm dễ (random forgery) có không gian tổ hợp nhỏ → dễ lặp lại cặp giống nhau giữa các epoch nếu sinh động. **Giảm thiểu:** với tập val/test, sinh cặp **một lần, cố định** (không sinh lại mỗi epoch) và lưu ra CSV; chỉ tập train mới sinh động mỗi epoch để tăng đa dạng.

## Security Considerations

- Không phát sinh thêm rủi ro bảo mật/riêng tư ở phase này (vẫn là dữ liệu CEDAR nghiên cứu).

## Next Steps

- Phase 4 (baseline) và Phase 5/6 (Siamese) đều tiêu thụ `data/splits/{train,val,test}_pairs.csv` và `src/sigverify/evaluation/metrics.py` từ phase này — không phase nào được tự viết lại logic chia tập hay tính FAR/FRR/EER riêng.
