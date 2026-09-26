---
phase: 9
title: "Phase 9: Chương trình demo Streamlit & đóng gói"
status: pending
priority: P1
effort: "1.5d"
dependencies: [5]
---

# Phase 9: Chương trình demo Streamlit & đóng gói

## Context Links

- Phase trước liền kề theo thứ tự thực hiện: [Phase 8: Phân tích lỗi](./phase-08-error-analysis.md)
- Phụ thuộc kỹ thuật thật sự: chỉ cần một mô hình đã train xong (Phase 5 tối thiểu; Phase 6 nếu Config B là mô hình tốt hơn) — không phụ thuộc Phase 7/8.
- Plan overview: [plan.md](./plan.md)

## Overview

- **Priority:** P1 — đây là hạng mục "bắt buộc phải làm" theo yêu cầu người dùng.
- **Status:** Pending
- Xây dựng ứng dụng web nhỏ bằng Streamlit (mặc định — Gradio là lựa chọn thay thế dễ hoán đổi vì `app/inference.py` tách biệt logic suy luận khỏi UI framework): tải lên 2 ảnh, hiển thị ảnh gốc + đã tiền xử lý, trả kết quả thật/giả kèm khoảng cách D, thanh trượt ngưỡng τ hiển thị ảnh hưởng lên FAR/FRR, không lưu ảnh người dùng xuống đĩa. Đóng gói `requirements.txt` (đã có từ Phase 1, chốt lại phiên bản cuối) và `Dockerfile` CPU tuỳ chọn.

## Key Insights

- **Ràng buộc riêng tư là yêu cầu thiết kế cứng, không phải tính năng phụ:** toàn bộ luồng xử lý ảnh người dùng upload phải nằm trong bộ nhớ (`io.BytesIO` → `PIL.Image` → `numpy.ndarray`), không có bất kỳ lệnh ghi file nào (`cv2.imwrite`, `Image.save`, `open(..., "wb")`) trên đường đi từ upload đến kết quả hiển thị. Đây phải là một mục kiểm tra rõ ràng trong Success Criteria, không chỉ ghi chú.
- **Đường cong FAR(τ)/FRR(τ) hiển thị trên thanh trượt phải lấy từ dữ liệu **validation** đã tính sẵn ở Phase 5/6/7 (`compute_far_frr` lưu ra file), không tính lại từ dữ liệu CEDAR gốc trong lúc chạy app** — vừa nhanh hơn, vừa tránh việc app phải đóng gói/bundle theo ảnh CEDAR thật (không cần thiết cho một app demo suy luận, và tránh rủi ro vô tình phân phối lại dữ liệu nghiên cứu có điều kiện truy cập).
- App load mô hình đã train (`models_registry/{config}_best.pt`) và đường cong FAR/FRR đã tính sẵn (`results/{config}/far_frr_curve.json`, sinh mới ở phase này) khi khởi động — nếu chưa có file này (vd. Phase 5/6 chưa chạy trên Colab/Kaggle), app phải báo lỗi khởi động rõ ràng, không được chạy với mô hình giả/ngẫu nhiên.
- Theo quy tắc quản lý tiến trình dài hạn: khi chạy `streamlit run` để kiểm thử thủ công, phải kiểm tra cổng 8501 trống trước khi chạy, theo dõi tiến trình đã khởi chạy, và dừng nó khi kết thúc kiểm thử — không để tiến trình Streamlit orphan lại trong môi trường thực thi.

## Requirements

- [x] `app/inference.py`: hàm thuần suy luận, không phụ thuộc Streamlit — `load_model(config_name) -> (model, tau_default, far_frr_curve)`, `preprocess_and_embed(image_bytes) -> (preprocessed_np_array, embedding)`, `compare(embedding_a, embedding_b) -> distance`, `decision(distance, tau) -> "Thật"|"Giả"`, `lookup_far_frr(tau, far_frr_curve) -> (far, frr)`.
- [x] `app/demo_app.py` (Streamlit): 2 ô upload ảnh (`st.file_uploader`, giới hạn định dạng ảnh phổ biến), hiển thị ảnh gốc và ảnh sau tiền xử lý cạnh nhau cho cả 2 ảnh (dùng `preprocess_image` từ Phase 2, không viết lại), nút/tự động chạy suy luận, hiển thị kết quả "Thật"/"Giả" + giá trị D, thanh trượt τ (`st.slider`, khoảng giá trị lấy từ `far_frr_curve` đã tính sẵn) cập nhật FAR/FRR hiển thị theo thời gian thực khi kéo, và cập nhật lại kết quả thật/giả theo τ hiện tại của thanh trượt (không chỉ hiển thị τ mặc định cố định).
- [x] Toàn bộ xử lý ảnh upload chỉ trong bộ nhớ — không có lệnh ghi file nào trên đường dẫn xử lý ảnh người dùng; xác nhận bằng review code + 1 test tĩnh đơn giản (rà `inference.py` và phần xử lý ảnh của `demo_app.py` không gọi API ghi file ảnh).
- [x] Sinh `results/{config}/far_frr_curve.json` (từ `compute_far_frr` trên val, Phase 3) — bổ sung bước lưu file này vào script train Phase 5/6 nếu chưa có (mở rộng nhỏ ngược lại `scripts/train_config_a.py`/`train_config_b.py`, tương tự cách Phase 8 mở rộng `evaluate_at_threshold`).
- [x] `requirements.txt` chốt phiên bản cuối cùng, bao gồm `streamlit`.
- [x] `Dockerfile` (P3 — làm nếu còn thời gian, nhưng đặc tả đầy đủ ngay trong phase này để không phải quay lại thiết kế): base `python:3.11-slim`, cài `requirements.txt`, `EXPOSE 8501`, `CMD ["streamlit", "run", "app/demo_app.py", "--server.address=0.0.0.0"]`, chạy CPU-only (không cài CUDA).
- [x] `tests/test_inference.py`: test `preprocess_and_embed`/`compare`/`decision`/`lookup_far_frr` bằng model giả nhỏ hoặc mock, không cần chạy Streamlit UI thật.

## Architecture

```
User upload (2 ảnh, qua Streamlit) → bytes trong bộ nhớ
  → preprocess_and_embed(bytes_a) → (img_a_pre, emb_a)   [không ghi đĩa]
  → preprocess_and_embed(bytes_b) → (img_b_pre, emb_b)
  → D = compare(emb_a, emb_b)
  → UI hiển thị: [ảnh gốc A | ảnh gốc B]
                 [ảnh đã xử lý A | ảnh đã xử lý B]
                 D = ...
  → tau = st.slider(...)  # khoảng giá trị từ far_frr_curve["thresholds"]
  → decision(D, tau) → "Thật"/"Giả"
  → far, frr = lookup_far_frr(tau, far_frr_curve)  → hiển thị "Tại τ này: FAR=…, FRR=…"
```

## Related Code Files

- Create: `app/inference.py`
- Create: `app/demo_app.py`
- Create: `Dockerfile`
- Create: `tests/test_inference.py`
- Modify: `scripts/train_config_a.py`, `scripts/train_config_b.py` — thêm bước lưu `results/{config}/far_frr_curve.json` từ `compute_far_frr` trên tập val (tái sử dụng, không tính lại bằng logic khác).
- Modify: `requirements.txt` — xác nhận `streamlit` có mặt với version tối thiểu hợp lý.

## Implementation Steps

1. Bổ sung bước lưu `far_frr_curve.json` vào `train_config_a.py`/`train_config_b.py` (mảng `thresholds`, `far`, `frr` từ `compute_far_frr` trên val).
2. Viết `app/inference.py::load_model(config_name)` — đọc `models_registry/{config}_best.pt`, `models_registry/{config}_threshold.json` (τ mặc định gợi ý), `results/{config}/far_frr_curve.json`; nếu thiếu file nào, raise lỗi rõ ràng kèm hướng dẫn chạy phase nào để tạo ra nó.
3. Viết `preprocess_and_embed`, `compare`, `decision`, `lookup_far_frr` (nội suy tuyến tính τ gần nhất trong `far_frr_curve`).
4. Viết `tests/test_inference.py` với một model giả siêu nhỏ (khởi tạo `SiameseScratchCNN` với trọng số ngẫu nhiên, không cần file `.pt` thật) để test luồng hàm mà không phụ thuộc Phase 5 đã chạy xong trên Colab.
5. Viết `app/demo_app.py` theo Architecture — dùng `st.columns` cho bố cục 2 ảnh cạnh nhau, `st.file_uploader(type=["png","jpg","jpeg"])`, `st.slider` cho τ, `st.metric`/`st.success`/`st.error` để hiển thị kết quả nổi bật (Thật = success màu xanh, Giả = error màu đỏ).
6. Rà lại toàn bộ `inference.py` và `demo_app.py`: xác nhận không có `cv2.imwrite`, `.save(`, `open(*, "wb"` nào áp dụng lên dữ liệu ảnh người dùng upload.
7. Viết `Dockerfile` theo đặc tả ở Requirements.
8. Chốt `requirements.txt`.
9. Chạy `pytest tests/test_inference.py`.
10. Kiểm thử thủ công cục bộ: kiểm tra cổng 8501 trống (`lsof -i :8501` hoặc tương đương), chạy `streamlit run app/demo_app.py` ở chế độ theo dõi được (background có ghi PID), thử tải 2 ảnh mẫu (không dùng CEDAR thật của người khác nếu có ràng buộc chia sẻ — dùng ảnh chữ ký tự vẽ hoặc ảnh mẫu công khai không nhạy cảm), kéo thanh trượt τ xác nhận FAR/FRR/kết quả cập nhật đúng, sau đó **dừng tiến trình Streamlit đã khởi chạy** trước khi kết thúc kiểm thử.

## Todo List

- [x] `far_frr_curve.json` được sinh từ Phase 5/6
- [x] `app/inference.py` xử lý hoàn toàn trong bộ nhớ, có test
- [x] `app/demo_app.py` đủ 5 yêu cầu UI: upload 2 ảnh, hiển thị gốc+đã xử lý, kết quả+D, thanh trượt τ, FAR/FRR theo τ
- [x] Xác nhận không có lệnh ghi file nào trên đường xử lý ảnh người dùng
- [x] `Dockerfile` CPU-only đặc tả đầy đủ (P3, làm nếu còn thời gian)
- [x] `requirements.txt` chốt bản cuối
- [x] Kiểm thử thủ công app chạy đúng, tiến trình được dừng sạch sau khi test

## Success Criteria

- `pytest tests/test_inference.py` pass.
- Chạy thử `streamlit run app/demo_app.py` thành công cục bộ, luồng upload → hiển thị → kết quả → thanh trượt hoạt động đúng như mô tả.
- Review code xác nhận: không có bất kỳ lệnh ghi file nào tác động lên dữ liệu ảnh người dùng upload trong toàn bộ `app/`.
- Không còn tiến trình Streamlit nào chạy nền sau khi hoàn tất kiểm thử phase này (`ps`/`lsof :8501` sạch).

## Risk Assessment

- **Rủi ro:** thanh trượt τ dùng khoảng giá trị không khớp thực tế phân phối D của mô hình (quá rộng hoặc quá hẹp), làm phần lớn giá trị trượt không thay đổi kết quả. **Giảm thiểu:** lấy `min`/`max` của khoảng τ trực tiếp từ `far_frr_curve["thresholds"]` (đã được `compute_far_frr` quét trên đúng dải giá trị D quan sát được ở Phase 3), không tự đặt khoảng cố định tuỳ ý.
- **Rủi ro riêng tư:** vô tình cache ảnh qua cơ chế nội bộ của Streamlit (`st.file_uploader` giữ buffer trong session state) khiến ảnh tồn tại lâu hơn cần thiết dù không ghi đĩa. **Giảm thiểu:** không chủ động lưu ảnh vào `st.session_state` lâu dài; xử lý xong một lượt upload thì không giữ tham chiếu ảnh cũ ngoài phạm vi cần thiết cho lần render hiện tại.
- **Rủi ro tiến trình:** quên dừng `streamlit run` sau kiểm thử thủ công, để lại tiến trình nền chiếm cổng 8501 cho lần chạy sau. **Giảm thiểu:** tuân thủ bước 10 ở Implementation Steps — luôn dừng tiến trình đã khởi chạy trước khi coi phase hoàn tất.

## Security Considerations

- **Riêng tư dữ liệu người dùng là yêu cầu bảo mật chính của phase này:** ảnh chữ ký là dữ liệu cá nhân/sinh trắc học — không lưu, không log đường dẫn/nội dung ảnh, không gửi ảnh ra ngoài (không có lệnh gọi mạng nào trong `app/` ngoài chính Streamlit server cục bộ).
- Không cần xác thực người dùng cho bản demo cục bộ này (ngoài phạm vi yêu cầu người dùng); nếu sau này triển khai công khai trên Internet, cần đánh giá bổ sung (giới hạn kích thước upload, rate limiting) — ghi nhận là ngoài phạm vi hiện tại, không tự ý mở rộng.

## Next Steps

- Đây là phase cuối cùng theo thứ tự yêu cầu của người dùng. Sau khi hoàn tất, xem lại `plan.md` mục tiêu/chỉ tiêu để tổng kết đồ án so với chỉ tiêu đề xuất ban đầu.
