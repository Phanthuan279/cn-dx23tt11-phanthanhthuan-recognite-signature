---
phase: 7
title: "Phase 7: Ablation (tiền xử lý/augmentation/margin) & tổng quát chéo trên BHSig260"
status: pending
priority: P2
effort: "2d"
dependencies: [6]
---

# Phase 7: Ablation (tiền xử lý/augmentation/margin) & tổng quát chéo trên BHSig260

## Context Links

- Phase trước: [Phase 6: Mạng Siamese Cấu hình B (Transfer Learning ResNet18/VGG16)](./phase-06-siamese-configb-transfer-learning.md)
- Plan overview: [plan.md](./plan.md)
- Quyết định người dùng: bộ dữ liệu phụ dùng để kiểm tra tổng quát là **BHSig260** (đã xác nhận qua câu hỏi làm rõ khi lập kế hoạch — xem `## Validation Log` trong [plan.md](./plan.md)).

## Overview

- **Priority:** P2 — quan trọng cho chất lượng khoa học của đồ án nhưng không chặn việc có một hệ thống demo hoạt động (Phase 8/9 có thể chạy song song về mặt kỹ thuật, tuy vẫn giữ thứ tự thực hiện tuần tự theo yêu cầu người dùng).
- **Status:** Pending
- Chạy các thí nghiệm ablation trên mô hình "chính" (Config A hoặc B, chọn theo `test_eer` thấp hơn ở Phase 5/6) để đo ảnh hưởng của tiền xử lý, augmentation, margin; sau đó kiểm tra khả năng tổng quát **zero-shot** (không fine-tune lại) trên BHSig260 để chứng minh tính chất writer-independent.

## Key Insights

- **Zero-shot là bắt buộc về mặt phương pháp luận:** mục tiêu đồ án là "writer-independent... không cần huấn luyện lại khi có người dùng mới" — áp mô hình đã train trên CEDAR thẳng vào BHSig260 mà **không fine-tune** là chính là phép kiểm tra cho tuyên bố này. Nếu fine-tune lại trên BHSig260 trước khi đánh giá, kết quả không còn chứng minh được writer-independence.
- **[UNVERIFIED — xác nhận khi thực thi]** Số signer/số ảnh mỗi phần Bengali/Hindi của BHSig260 có thể khác nhau tuỳ mirror phân phối (thường trích dẫn khoảng 100 signer Bengali + 160 signer Hindi, mỗi signer có cả chữ ký thật và giả kỹ năng cao) — script tải phải tự đếm và ghi số liệu thật vào `results/eda/bhsig260_stats.json`, không hard-code con số vào code.
- BHSig260 cũng chỉ có giả mạo kỹ năng cao (skilled), tương tự CEDAR — "random forgery" trên BHSig260 vẫn được định nghĩa như Phase 3 (cặp thật của 2 signer khác nhau trong BHSig260).
- Ablation phải **cùng writer-disjoint test set của CEDAR** (không đổi split giữa các biến thể ablation) để so sánh công bằng — chỉ thay đổi đúng 1 biến mỗi lần chạy (tiền xử lý, augmentation, hoặc chuẩn hoá embedding), không đổi nhiều biến cùng lúc.
- Ảnh BHSig260 phải chạy qua **đúng cùng pipeline tiền xử lý** (`preprocess_image`) như CEDAR — không viết pipeline tiền xử lý riêng cho bộ dữ liệu phụ, đúng tinh thần "một mô hình, một pipeline dùng chung cho mọi người ký".

## Requirements

- [ ] `scripts/download_bhsig260.py`: cùng mẫu với `download_cedar.py` (Kaggle tự động nếu có config + fallback thủ công), parse cấu trúc thư mục BHSig260 thành cùng interface `(writer_id, sample_id, label, path)` như `datasets.py` của CEDAR (mở rộng `datasets.py` với hàm `list_bhsig260_signatures`, không tạo module riêng trùng lặp).
- [ ] `scripts/run_ablations.py`: chạy lần lượt các biến thể sau trên mô hình chính, mỗi biến thể train lại từ đầu (không phải chỉ đánh giá) vì thay đổi tiền xử lý/augmentation ảnh hưởng đến dữ liệu huấn luyện:
  1. Baseline (cấu hình mặc định đã chọn ở Phase 5/6) — dùng lại kết quả có sẵn, không train lại.
  2. Tắt tight-crop bbox (resize toàn khung ảnh gốc, không crop theo Otsu bbox).
  3. Bật `binarize_output=True` (dùng ảnh nhị phân làm input thay vì grayscale).
  4. Tắt toàn bộ augmentation khi train.
  5. Bật `model.l2_normalize=True` cho embedding.
  - Ghi toàn bộ `val_eer`/`test_eer` mỗi biến thể vào `results/ablations/summary.json` + bảng Markdown.
- [ ] `scripts/run_ablations.py` (phần 2 — cross-dataset): load `models_registry/{config_a|config_b}_best.pt` (mô hình chính, không train lại), chạy `preprocess_image` + inference trên toàn bộ BHSig260, tính FAR/FRR/EER/Accuracy/ROC-AUC bằng **đúng** `src/sigverify/evaluation/metrics.py`, tách skilled/random forgery, dùng **cùng τ* đã đóng băng từ CEDAR** (không chọn ngưỡng mới trên BHSig260 — đây chính là phép thử "writer-independent" nghiêm ngặt) và, để tham khảo thêm, một lần chạy phụ có ghi rõ nhãn với τ chọn lại trên một phần nhỏ BHSig260 validation (nếu người dùng muốn xem "trần" hiệu năng có thể đạt được khi cho phép hiệu chỉnh ngưỡng theo miền dữ liệu mới) — hai con số này **không được gộp lẫn** trong báo cáo.
- [ ] Baseline HOG/LBP+SVM (Phase 4) cũng được chạy zero-shot trên BHSig260 để so sánh công bằng.
- [ ] `results/generalization_bhsig260.md`: báo cáo tổng hợp EER trên BHSig260 (skilled/random), so với chỉ tiêu đề xuất EER ≤20%, so với baseline.

## Architecture

```
Ablation (mỗi biến thể, trên CEDAR, cùng test split):
  configs/ablation_variants/<variant>.yaml  (kế thừa default.yaml, override đúng 1 tham số)
  → build_pairs (nếu biến thể ảnh hưởng tiền xử lý) → train_one_config → evaluate
  → results/ablations/<variant>/metrics.json

Cross-dataset generalization (zero-shot):
  BHSig260 raw → list_bhsig260_signatures() → preprocess_image() [pipeline Phase 2, không đổi]
  → generate_pairs() [logic Phase 3, không đổi, áp lên writer BHSig260]
  → model_frozen.forward_pair() [trọng số CEDAR, KHÔNG cập nhật]
  → evaluate_at_threshold(scores, labels, tau_star_from_cedar_val)   # ngưỡng từ CEDAR, không đổi
  → tách kết quả theo skilled_forgery / random_forgery
```

## Related Code Files

- Modify: `src/sigverify/preprocessing/datasets.py` — thêm `list_bhsig260_signatures(raw_dir) -> DataFrame` (cùng schema cột với `list_cedar_signatures`).
- Create: `scripts/download_bhsig260.py`
- Create: `scripts/run_ablations.py`
- Create: `configs/ablation_variants/no_bbox_crop.yaml`, `binarize_output.yaml`, `no_augmentation.yaml`, `l2_normalize.yaml`
- Create: `results/ablations/summary.json`, `results/generalization_bhsig260.md`

## Implementation Steps

1. Viết `list_bhsig260_signatures`, parse quy ước tên file BHSig260 (khác CEDAR — xác nhận quy ước thật khi tải dữ liệu, ghi chú lại trong docstring của hàm khi biết chính xác).
2. Viết `download_bhsig260.py` theo mẫu `download_cedar.py`.
3. Tạo 4 file config biến thể trong `configs/ablation_variants/`, mỗi file chỉ override đúng 1 khoá so với `default.yaml`.
4. Viết `run_ablations.py::run_variant(config_path)` — tái sử dụng `build_pairs.py` + `train_one_config` + khung đo Phase 3, không viết lại logic.
5. Chạy lần lượt 4 biến thể (khi có CEDAR thật trong môi trường thực thi/Colab), tổng hợp `results/ablations/summary.json`.
6. Viết `run_ablations.py::run_cross_dataset(model_path, threshold_path, bhsig260_raw_dir)` — thực hiện đúng luồng "Cross-dataset generalization" ở Architecture, cả cho Siamese chính và baseline SVM (Phase 4).
7. Viết `results/generalization_bhsig260.md` tự động sinh từ số liệu JSON, nêu rõ đạt/không đạt so với chỉ tiêu EER ≤20% và so với baseline trên cùng BHSig260.
8. Nếu CEDAR/BHSig260 chưa có ở môi trường thực thi hiện tại: viết đầy đủ code, chạy test đơn vị trên dữ liệu tổng hợp cho `list_bhsig260_signatures` (cấu trúc thư mục giả), hoãn phần chạy số liệu thật sang khi thực thi trên Colab/Kaggle với dữ liệu thật.

## Todo List

- [ ] `list_bhsig260_signatures` parse đúng cấu trúc BHSig260 thật (xác nhận khi có dữ liệu)
- [ ] 4 file config ablation, mỗi file đổi đúng 1 biến
- [ ] `run_ablations.py` tái sử dụng toàn bộ hạ tầng Phase 2/3/5, không viết lại
- [ ] Cross-dataset dùng đúng τ* đóng băng từ CEDAR, không tự chọn ngưỡng mới làm số liệu chính
- [ ] Baseline SVM cũng chạy zero-shot BHSig260 để so sánh công bằng
- [ ] `results/generalization_bhsig260.md` nêu rõ đạt/không đạt EER ≤20%

## Success Criteria

- 4 biến thể ablation có kết quả trong `results/ablations/summary.json`, so sánh được với cấu hình mặc định.
- `results/generalization_bhsig260.md` có FAR/FRR/EER/Accuracy/AUC trên BHSig260, tách skilled/random forgery, dùng ngưỡng đóng băng từ CEDAR làm số liệu chính.
- Không có đoạn code nào chọn lại ngưỡng τ trên BHSig260 rồi báo cáo nó như kết quả "writer-independent" chính — nếu có chạy thêm biến thể "hiệu chỉnh ngưỡng theo miền mới" thì phải gắn nhãn rõ ràng khác biệt trong báo cáo.

## Risk Assessment

- **Rủi ro cao:** hiệu năng zero-shot trên BHSig260 kém hơn nhiều so với CEDAR (khác biệt phông chữ/nét viết Bengali-Hindi so với Latin) khiến EER vượt xa 20%. **Giảm thiểu:** đây là kết quả khoa học hợp lệ cần báo cáo trung thực (không phải lỗi cần "sửa" bằng cách hiệu chỉnh ngưỡng ngầm); đưa vào Phase 8 (phân tích lỗi) để lý giải nguyên nhân.
- **Rủi ro:** chạy 4 biến thể ablation × train lại từ đầu tốn nhiều thời gian GPU. **Giảm thiểu:** ưu tiên chạy ablation trên Config A (rẻ hơn Config B) trừ khi Config B là mô hình chính; giảm `max_epochs`/mở rộng `patience` sớm hơn cho các lần chạy ablation nếu ngân sách thời gian hạn chế, ghi rõ khác biệt so với lần train chính thức.

## Security Considerations

- BHSig260 là bộ dữ liệu nghiên cứu công khai/xin phép giống CEDAR, không phải dữ liệu người dùng cuối.

## Next Steps

- Phase 8 dùng kết quả CEDAR test + BHSig260 zero-shot của phase này làm nguồn để chọn các cặp bị nhận sai và phân tích nguyên nhân.
