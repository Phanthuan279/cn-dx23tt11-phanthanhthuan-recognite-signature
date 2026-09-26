---
phase: 8
title: "Phase 8: Phân tích lỗi"
status: pending
priority: P2
effort: "1d"
dependencies: [7]
---

# Phase 8: Phân tích lỗi

## Context Links

- Phase trước: [Phase 7: Ablation & tổng quát chéo trên BHSig260](./phase-07-ablations-cross-dataset-generalization.md)
- Plan overview: [plan.md](./plan.md)

## Overview

- **Priority:** P2
- **Status:** Pending
- Trích xuất và trực quan hoá các cặp chữ ký bị mô hình chính nhận sai (chấp nhận nhầm giả / từ chối nhầm thật) trên tập test CEDAR và trên BHSig260 (zero-shot), phân loại nguyên nhân định tính để đưa vào báo cáo đồ án.

## Key Insights

- Phân tích lỗi phải tách theo **cả 2 chiều**: (a) loại lỗi — chấp nhận nhầm (false accept, FA) vs từ chối nhầm (false reject, FR); (b) loại forgery — skilled vs random. 4 tổ hợp này thường có nguyên nhân khác nhau (vd. FA trên random forgery thường do 2 người có nét chữ tự nhiên giống nhau; FR trên genuine thường do biến thiên tự nhiên lớn trong chữ ký thật của cùng một người, hoặc lỗi tiền xử lý cắt mất 1 phần chữ ký).
- Dùng đúng `tau*` đã đóng băng từ Phase 5/6/7 để xác định "sai" — không tự chọn ngưỡng khác cho phân tích lỗi.
- Kết quả phase này là tài liệu tham khảo cho báo cáo đồ án, lưu trong `results/error_analysis/` của chính repo — không tạo file ngoài cấu trúc `results/` đã định nghĩa ở Phase 1.

## Requirements

- [ ] `scripts/error_analysis.py`: với mỗi tập đánh giá (CEDAR test, BHSig260 zero-shot), lọc ra các cặp có dự đoán sai tại `tau*`, sắp xếp theo mức độ sai lệch (`|D - tau*|` lớn nhất trước — đây là các ca sai "rõ ràng" nhất, đáng chú ý nhất).
- [ ] Với mỗi ca sai được chọn (giới hạn số lượng hiển thị, vd. top 20 mỗi tổ hợp FA/FR × skilled/random), lưu ảnh gốc + ảnh sau tiền xử lý của cả 2 ảnh trong cặp, cùng giá trị `D`, `tau*`, nhãn thật, dự đoán, vào `results/error_analysis/{dataset}/{case_id}.png` (lưới 2×2: gốc A, gốc B, đã xử lý A, đã xử lý B).
- [ ] `results/error_analysis/findings.md`: tổng hợp định tính — với mỗi tổ hợp (FA/FR × skilled/random × CEDAR/BHSig260), liệt kê 2-3 nguyên nhân khả dĩ quan sát được từ các ca cụ thể (tham chiếu ảnh đã lưu), không suy đoán chung chung không có bằng chứng ảnh minh hoạ.
- [ ] `tests/test_error_analysis.py`: assert hàm lọc ca sai trả về đúng tập con (dùng dữ liệu tổng hợp có nhãn/dự đoán biết trước).

## Architecture

```
Với mỗi dataset ∈ {cedar_test, bhsig260}:
  load predictions.csv  # (pair_id, D, label, forgery_type, tau_used)  — sinh sẵn từ Phase 5/6/7 khi evaluate_at_threshold chạy
  errors = predictions[ (label==1 & D>=tau_used) | (label==0 & D<tau_used) ]
  errors["severity"] = abs(errors.D - errors.tau_used)
  top_errors = errors.groupby(["forgery_type", error_type]).apply(lambda g: g.nlargest(20, "severity"))
  → với mỗi ca trong top_errors: load ảnh gốc + preprocess_image() → lưới 2x2 → lưu PNG
  → findings.md tổng hợp quan sát định tính theo từng nhóm
```

**Yêu cầu ngược đối với Phase 3/5/6/7:** hàm `evaluate_at_threshold` (Phase 3) cần được mở rộng để, khi gọi với cờ `return_per_pair=True`, trả về thêm DataFrame chi tiết từng cặp (`pair_id, D, label, forgery_type, prediction`) thay vì chỉ số liệu tổng hợp — bổ sung tham số này ở Phase 3 (không phá vỡ chữ ký gọi mặc định hiện có, giữ tương thích ngược cho các phase trước), rồi Phase 5/6/7 truyền `return_per_pair=True` khi lưu `predictions.csv` phục vụ phase này.

## Related Code Files

- Modify: `src/sigverify/evaluation/metrics.py` — thêm tham số tuỳ chọn `return_per_pair: bool = False` cho `evaluate_at_threshold`, mặc định `False` để không đổi hành vi đã dùng ở các phase trước.
- Modify: `scripts/train_config_a.py`, `scripts/train_config_b.py`, `scripts/run_ablations.py` — thêm dòng lưu `results/{config}/predictions_test.csv` và `results/{config}/predictions_bhsig260.csv` bằng `return_per_pair=True`.
- Create: `scripts/error_analysis.py`
- Create: `tests/test_error_analysis.py`
- Create: `results/error_analysis/findings.md` (sinh có hỗ trợ thủ công — script tạo khung + số liệu, phần diễn giải định tính do người thực hiện bổ sung dựa trên ảnh quan sát được)

## Implementation Steps

1. Mở rộng `evaluate_at_threshold` với `return_per_pair` — viết test hồi quy xác nhận hành vi mặc định (`return_per_pair=False`) không đổi so với Phase 3.
2. Cập nhật các script Phase 5/6/7 để lưu `predictions_*.csv`.
3. Viết `error_analysis.py::find_top_errors(predictions_df, top_k=20) -> DataFrame`.
4. Viết `test_error_analysis.py` với `predictions_df` tổng hợp có nhãn/dự đoán biết trước, assert lọc đúng và sắp xếp đúng theo `severity`.
5. Viết `error_analysis.py::render_case(case_row, out_path)` — load 2 ảnh gốc, chạy `preprocess_image`, ghép lưới 2×2 bằng matplotlib, ghi chú `D`, `tau*`, nhãn/dự đoán lên hình.
6. Chạy `error_analysis.py` cho CEDAR test và BHSig260 (khi đã có `predictions_*.csv` thật từ Phase 5-7 chạy trên Colab/Kaggle).
7. Xem trực quan các ảnh sinh ra, viết `findings.md` theo khung ở Requirements — đây là bước cần đánh giá của người trực tiếp xem ảnh, không tự động hoá hoàn toàn phần diễn giải.

## Todo List

- [ ] `evaluate_at_threshold` mở rộng không phá vỡ hành vi cũ
- [ ] `predictions_*.csv` được lưu ở Phase 5/6/7
- [ ] `find_top_errors` có test, lọc đúng 4 tổ hợp FA/FR × skilled/random
- [ ] Ảnh minh hoạ 2×2 cho các ca sai tiêu biểu
- [ ] `findings.md` có nguyên nhân định tính kèm tham chiếu ảnh cụ thể

## Success Criteria

- `pytest tests/test_error_analysis.py` pass.
- `results/error_analysis/{cedar_test,bhsig260}/` chứa ảnh minh hoạ cho từng tổ hợp FA/FR × skilled/random (khi có dữ liệu thật).
- `findings.md` không chứa nhận định không có bằng chứng ảnh minh hoạ đi kèm.

## Risk Assessment

- **Rủi ro:** nếu mô hình chính đạt EER quá thấp trên CEDAR test, số lượng ca sai thật sự quá ít để phân tích có ý nghĩa thống kê. **Giảm thiểu:** vẫn phân tích toàn bộ ca sai hiện có (dù ít), bổ sung phân tích trên BHSig260 (nơi tỉ lệ lỗi dự kiến cao hơn) để có đủ dữ liệu định tính cho báo cáo.

## Security Considerations

- Ảnh dùng ở phase này là CEDAR/BHSig260 (dữ liệu nghiên cứu), không phải ảnh người dùng cuối — không áp dụng ràng buộc "không lưu" của Phase 9.

## Next Steps

- Phase 9 (demo) không phụ thuộc kỹ thuật vào phase này, nhưng nên tham khảo `findings.md` để đặt kỳ vọng đúng cho người dùng demo (vd. cảnh báo trong UI nếu ảnh chất lượng thấp dễ rơi vào nhóm lỗi đã quan sát).
