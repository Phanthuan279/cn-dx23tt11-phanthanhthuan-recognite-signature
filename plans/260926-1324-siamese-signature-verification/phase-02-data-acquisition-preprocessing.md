---
phase: 2
title: "Phase 2: Tải/khảo sát CEDAR & pipeline tiền xử lý ảnh"
status: pending
priority: P1
effort: "1.5d"
dependencies: [1]
---

# Phase 2: Tải/khảo sát CEDAR & pipeline tiền xử lý ảnh

## Context Links

- Phase trước: [Phase 1: Khởi tạo cấu trúc dự án & môi trường](./phase-01-start.md)
- Plan overview: [plan.md](./plan.md)

## Overview

- **Priority:** P1
- **Status:** Pending
- Viết script tải/khảo sát bộ CEDAR, và cài đặt pipeline tiền xử lý ảnh 5 bước (grayscale → khử nhiễu → Otsu → crop bbox → resize+pad → chuẩn hoá pixel) thành module tái sử dụng cho baseline, Config A, Config B và demo app.

## Key Insights

- **Cấu trúc CEDAR:** 55 người ký, mỗi người 24 chữ ký thật (`full_org/`) + 24 chữ ký giả kỹ năng cao/skilled forgery (`full_forg/`), quy ước tên file phổ biến `original_{writer}_{sample}.png` / `forgeries_{writer}_{sample}.png`. CEDAR **không có** danh mục "random forgery" riêng — "giả mạo ngẫu nhiên" trong đồ án này được định nghĩa là cặp chữ ký thật của **hai người ký khác nhau** (xem Phase 3), không phải một thư mục dữ liệu riêng.
- **[UNVERIFIED — cần xác nhận khi thực thi]** Nguồn tải: trang chính thức CEDAR (cedar.buffalo.edu) yêu cầu điền form xin quyền truy cập, thời gian phản hồi không ổn định. `scripts/download_cedar.py` phải hỗ trợ **2 đường**: (a) `kaggle datasets download` nếu có `~/.kaggle/kaggle.json` và biết chính xác slug bộ dữ liệu Kaggle mirror; (b) fallback thủ công — người dùng tự tải zip và đặt vào `data/raw/cedar/`, script chỉ giải nén + xác thực cấu trúc. Không hard-code một slug Kaggle cụ thể vì chưa xác minh được tại thời điểm lập kế hoạch này; script log rõ ràng nếu tải tự động thất bại và hướng dẫn fallback thủ công.
- **Quyết định thiết kế quan trọng — ảnh nhị phân chỉ dùng để định vị bbox, KHÔNG dùng làm ảnh input cuối cùng cho mô hình:** nhị phân hoá Otsu dùng để tìm vùng chữ ký (bounding box), nhưng ảnh cuối cùng đưa vào mô hình là ảnh **grayscale đã khử nhiễu, crop theo bbox đó**, không phải ảnh nhị phân phẳng. Lý do: ảnh nhị phân làm mất thông tin độ đậm nhạt nét bút (áp lực/mực), vốn là đặc trưng phân biệt giả mạo có giá trị. Tham số `binarize_output: bool` (mặc định `false`) trong config cho phép bật lại nếu Phase 7 (ablation) cho thấy nhị phân hoá tốt hơn.
- Ảnh nền chữ ký thường là nền trắng, mực tối — pipeline giả định điều này; nếu ảnh nguồn bị đảo màu (nền tối) cần phát hiện và đảo lại trước Otsu (kiểm tra tỉ lệ pixel sáng/tối ở viền ảnh).

## Requirements

- [ ] `scripts/download_cedar.py`: tải hoặc xác thực CEDAR đã có sẵn tại `data/raw/cedar/`, in thống kê (số signer, số ảnh thật/giả mỗi signer, phát hiện thiếu file).
- [ ] `src/sigverify/preprocessing/datasets.py`: hàm liệt kê toàn bộ ảnh CEDAR theo `(writer_id, sample_id, label∈{genuine, forged}, path)`, trả về `pandas.DataFrame` hoặc list dataclass — dùng chung cho Phase 3 sinh cặp và Phase 7 (BHSig260 loader theo cùng interface).
- [ ] `src/sigverify/preprocessing/pipeline.py`: hàm `preprocess_image(path_or_array, target_size, binarize_output=False) -> np.ndarray` thực hiện đủ 5 bước theo đúng thứ tự nêu trong Overview, trả về ảnh float32 chuẩn hoá.
- [ ] Chuẩn hoá pixel hỗ trợ 2 chế độ: `mode="unit"` → về `[0,1]` (dùng cho Config A train from scratch), `mode="imagenet"` → trừ mean/chia std ImageNet trên ảnh 3 kênh (dùng cho Config B) — chọn qua tham số, không hard-code.
- [ ] Script khảo sát `scripts/run_preprocessing.py` chạy pipeline trên một mẫu ảnh, lưu ảnh gốc + ảnh sau xử lý cạnh nhau vào `results/eda/` để kiểm tra trực quan.
- [ ] `tests/test_preprocessing.py` chạy trên ảnh tổng hợp (vẽ vài nét bằng PIL, không cần CEDAR thật) — không phụ thuộc dữ liệu thật để chạy CI/local.

## Architecture

```
preprocess_image(img)
  1. to_grayscale(img)                         # cv2.cvtColor hoặc đọc trực tiếp ở mode "L"
  2. denoise(img)                               # Gaussian hoặc median blur, kernel nhỏ (3x3/5x5)
  3. mask = otsu_threshold(denoise(img))        # CHỈ để tìm bbox, không dùng làm ảnh cuối
  4. bbox = tight_bbox(mask)                    # bounding box vùng mực (pixel tối trên mask)
  5. cropped = grayscale_denoised[bbox]         # crop ẢNH GRAYSCALE gốc theo bbox, không crop mask
  6. centered_padded = center_pad_resize(cropped, target_size)  # giữ tỉ lệ khung hình, pad viền trắng
  7. normalized = normalize(centered_padded, mode)  # "unit" hoặc "imagenet"
```

`target_size` truyền từ `configs/default.yaml`: `[220, 150]` cho pipeline dùng bởi Config A/baseline, `[224, 224]` cho Config B — hàm không tự chọn, caller (Phase 4/5/6) truyền đúng size theo cấu hình đang chạy.

## Related Code Files

- Create: `scripts/download_cedar.py`
- Create: `src/sigverify/preprocessing/datasets.py`
- Create: `src/sigverify/preprocessing/pipeline.py`
- Create: `scripts/run_preprocessing.py`
- Create: `tests/test_preprocessing.py`
- Modify: `configs/default.yaml` (đã có khoá `image.size_scratch`/`image.size_transfer` từ Phase 1; thêm `preprocessing.binarize_output: false`, `preprocessing.denoise: "gaussian"`)

## Implementation Steps

1. Viết `datasets.py::list_cedar_signatures(raw_dir) -> DataFrame[writer_id, sample_id, label, path]`, parse tên file theo quy ước CEDAR, raise lỗi rõ ràng nếu cấu trúc thư mục không khớp kỳ vọng (giúp phát hiện sớm nếu mirror Kaggle có cấu trúc khác).
2. Viết `download_cedar.py`: thử `kaggle datasets download` nếu có config; nếu không, kiểm tra `data/raw/cedar/` đã tồn tại đúng cấu trúc chưa (gọi `list_cedar_signatures`), in hướng dẫn thủ công nếu thiếu.
3. Viết từng hàm con của `pipeline.py` theo đúng 5 bước ở Architecture, mỗi hàm nhỏ, test được độc lập.
4. Viết `center_pad_resize`: resize giữ tỉ lệ khung hình (scale theo cạnh dài hơn so với target), sau đó pad viền trắng (giá trị pixel = nền trắng, tương ứng 255 trước chuẩn hoá) để đạt đúng `target_size`, ảnh được căn giữa.
5. Viết `normalize(img, mode)`: `mode="unit"` chia 255; `mode="imagenet"` convert 1 kênh → 3 kênh (repeat), trừ mean `[0.485,0.456,0.406]`, chia std `[0.229,0.224,0.225]`.
6. Viết `run_preprocessing.py`: đọc N ảnh mẫu ngẫu nhiên (seed cố định), lưu lưới ảnh gốc/đã xử lý bằng matplotlib vào `results/eda/preprocessing_samples.png`, in thống kê phân phối kích thước ảnh gốc trong CEDAR.
7. Viết `test_preprocessing.py`: tạo ảnh tổng hợp bằng PIL (vẽ vài đường nét đen trên nền trắng ở một góc ảnh lớn), assert: (a) output đúng `target_size`; (b) bbox crop loại bỏ được phần lớn viền trắng thừa; (c) `mode="unit"` output nằm trong `[0,1]`; (d) `mode="imagenet"` output có 3 kênh.
8. Chạy `pytest tests/test_preprocessing.py`.
9. Nếu CEDAR đã tải được trong môi trường thực thi: chạy `run_preprocessing.py` thật và xem lại `results/eda/preprocessing_samples.png` để kiểm tra bằng mắt (không có bước này thì đánh dấu "chưa xác minh trên dữ liệu thật" trong báo cáo phase).

## Todo List

- [ ] `list_cedar_signatures` parse đúng cấu trúc CEDAR
- [ ] `download_cedar.py` có cả đường tự động (Kaggle) và fallback thủ công
- [ ] `pipeline.py` đủ 5 bước, tách hàm nhỏ
- [ ] Hỗ trợ 2 chế độ chuẩn hoá `unit`/`imagenet`
- [ ] `binarize_output` chỉ ảnh hưởng bước cuối, mặc định tắt
- [ ] `test_preprocessing.py` xanh trên ảnh tổng hợp
- [ ] EDA script sinh ảnh trực quan gốc vs. đã xử lý

## Success Criteria

- `pytest tests/test_preprocessing.py` pass mà không cần CEDAR thật.
- `preprocess_image` trả về đúng shape `target_size` cho cả hai chế độ chuẩn hoá.
- Nếu CEDAR có sẵn trong môi trường thực thi: `list_cedar_signatures` liệt kê đủ 55 signer × (24 thật + 24 giả) = 2640 ảnh (hoặc số thực tế nếu mirror Kaggle khác biệt — ghi lại số liệu thật vào `results/eda/cedar_stats.json`).

## Risk Assessment

- **Rủi ro cao:** không tải được CEDAR do gating truy cập/mirror Kaggle không tồn tại đúng slug. **Giảm thiểu:** thiết kế toàn bộ Phase 2 để test được bằng ảnh tổng hợp, không chặn tiến độ các phase sau miễn có một bộ dữ liệu thật trước khi Phase 3 sinh cặp thật.
- **Rủi ro:** ảnh CEDAR có nền/độ tương phản không đồng nhất khiến Otsu bắt bbox sai (quá rộng hoặc cắt mất nét). **Giảm thiểu:** thêm bước kiểm tra sanity — nếu bbox chiếm >95% hoặc <5% diện tích ảnh gốc, log cảnh báo thay vì âm thầm dùng kết quả sai.

## Security Considerations

- Không có dữ liệu cá nhân người dùng ở phase này (CEDAR là bộ dữ liệu nghiên cứu công khai/xin phép, không phải chữ ký người dùng thật của đồ án).

## Next Steps

- Phase 3 dùng trực tiếp `list_cedar_signatures` và `preprocess_image` để sinh cặp và chia tập.
