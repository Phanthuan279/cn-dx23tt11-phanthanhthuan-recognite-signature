---
title: "Phase 2: Demo Streamlit"
status: done
---

# Phase 2: Demo Streamlit

## Overview

Xây dựng ứng dụng demo bằng Streamlit (đúng công nghệ gợi ý của đề tài) để
minh họa hai mô hình đã huấn luyện hoạt động thật: người dùng vẽ hoặc tải
lên một ảnh chữ số, ứng dụng hiển thị dự đoán và độ tin cậy của cả KNN và SVM.

## Requirements

- [x] Cho phép vẽ chữ số trực tiếp trên canvas
- [x] Cho phép tải ảnh chữ số lên (PNG/JPG)
- [x] Tiền xử lý ảnh đầu vào về đúng định dạng MNIST (xám, 28×28, chuẩn hóa [0,1], tự động đảo màu nếu ảnh nền sáng/mực tối kiểu ảnh chụp giấy)
- [x] Hiển thị dự đoán + biểu đồ độ tin cậy cho cả hai mô hình song song
- [x] Chạy thật và xác nhận không có lỗi runtime (không chỉ kiểm tra cú pháp)

## Implementation Steps

1. `app.py`: tải mô hình đã huấn luyện (`@st.cache_resource`) từ `models/`.
2. Hàm `preprocess()`: chuyển ảnh về xám, resize 28×28, tự động đảo màu khi ảnh nền sáng, chuẩn hóa về [0,1], làm phẳng thành vector 784 chiều.
3. Hai tab: "Vẽ chữ số" (canvas vẽ tay) và "Tải ảnh lên" (file uploader).
4. Cột KNN: `predict()` + `predict_proba()`. Cột SVM: `predict()` + `decision_function()` qua softmax làm điểm tin cậy ước lượng (xem Phase 1 vì sao SVM không dùng `probability=True`).
5. **Lần cài đặt đầu tiên** dùng thư viện ngoài `streamlit-drawable-canvas` cho canvas vẽ tay. Xác minh lúc đó: `streamlit run app.py` khởi động, `curl` trả `HTTP 200` và `/_stcore/health` trả `ok` — **nhưng đây là xác minh không đủ**: hai kiểm tra đó chỉ xác nhận tiến trình server đang chạy, không xác nhận script `app.py` thực sự thực thi được (Streamlit chỉ thực thi script theo từng phiên trình duyệt kết nối qua WebSocket).
6. **Phát hiện lúc rà soát lại (cook pass)**: gọi `python -c "import app"` trực tiếp thì vỡ ngay ở dòng `from streamlit_drawable_canvas import st_canvas` với lỗi `StreamlitAPIException: ... must be declared in pyproject.toml with asset_dir ...`. Lỗi tái lập y hệt trong một venv hoàn toàn sạch (cài đúng `streamlit==1.64.0` + `streamlit-drawable-canvas==0.13.0`) — xác nhận đây là lỗi không tương thích thật giữa phiên bản Streamlit đang dùng (API `components.v2` mới) và thư viện `streamlit-drawable-canvas` (chỉ hỗ trợ API `components.v1` cũ, chưa có bản cập nhật).
7. **Sửa**: bỏ hẳn `streamlit-drawable-canvas`, tự viết canvas vẽ tay bằng API gốc `st.components.v2.component(html=..., css=..., js=...)` của chính Streamlit (không phụ thuộc thư viện ngoài nào) — một `<canvas>` HTML5 nhận sự kiện chuột/chạm, gửi ảnh vẽ về Python qua `setStateValue('image_data', canvas.toDataURL(...))`. Phù hợp với chính ghi chú công nghệ của đề tài: "có thể thay bằng công nghệ tương đương nếu giải thích được lựa chọn và bảo đảm sản phẩm chạy ổn định".
8. **Xác minh lại đúng cách** sau khi sửa: dùng `streamlit.testing.v1.AppTest` (chạy script thật qua script-runner thật của Streamlit, không phải chỉ kiểm tra server sống) — `at.run()` cho `0` exception, tiêu đề/2 tab/thông báo hiển thị đúng như kỳ vọng. Gọi trực tiếp `preprocess()` + `predict()`/`predict_proba()`/`decision_function()` trên một ảnh MNIST test thật (nhãn thật = 3): cả KNN và SVM dự đoán đúng = 3. Khởi động lại `streamlit run app.py` thật một lần nữa, xác nhận log sạch, không traceback, rồi dừng tiến trình dev server.

## Todo

- [x] Viết `app.py` với 2 tab nhập liệu và 3 cột hiển thị (ảnh đầu vào, KNN, SVM)
- [x] Phát hiện và sửa lỗi không tương thích của `streamlit-drawable-canvas` (xem Implementation Steps 5-7)
- [x] Thay bằng canvas tự viết dùng `st.components.v2` gốc của Streamlit, bỏ thư viện ngoài khỏi `requirements.txt`
- [x] Xác minh thật bằng `AppTest` (chạy script thật, 0 exception) + gọi trực tiếp pipeline dự đoán trên ảnh MNIST test thật
- [x] Dọn dẹp tiến trình dev server sau khi xác nhận (không để tiến trình treo)

## Success Criteria

`streamlit.testing.v1.AppTest` chạy `app.py` cho 0 exception; tiêu đề, 2 tab,
và thông báo hướng dẫn hiển thị đúng. Pipeline `preprocess()` → `predict()` /
`predict_proba()` / `decision_function()` cho kết quả đúng trên ảnh MNIST
test thật (nhãn thật = 3, cả hai mô hình dự đoán = 3). `streamlit run app.py`
khởi động sạch, không traceback trong log. Không còn phụ thuộc thư viện
ngoài nào bị gãy.

## Bài học rút ra

Kiểm tra "server khởi động + health check OK" **không đủ** để xác nhận một
ứng dụng Streamlit chạy đúng, vì Streamlit chỉ thực thi script theo từng
phiên trình duyệt kết nối qua WebSocket — một lỗi crash ở ngay dòng import
đầu tiên vẫn có thể để server tiến trình gốc "sống" bình thường. Cách xác
minh đúng: dùng `streamlit.testing.v1.AppTest` để chạy thật script, hoặc gọi
`import app` trực tiếp để script thực thi và lỗi (nếu có) hiện ra ngay.
