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

- [x] Cho phép vẽ chữ số trực tiếp trên canvas (dùng `streamlit-drawable-canvas`)
- [x] Cho phép tải ảnh chữ số lên (PNG/JPG)
- [x] Tiền xử lý ảnh đầu vào về đúng định dạng MNIST (xám, 28×28, chuẩn hóa [0,1], tự động đảo màu nếu ảnh nền sáng/mực tối kiểu ảnh chụp giấy)
- [x] Hiển thị dự đoán + biểu đồ độ tin cậy cho cả hai mô hình song song
- [x] Chạy thật và xác nhận không có lỗi runtime (không chỉ kiểm tra cú pháp)

## Implementation Steps

1. `app.py`: tải mô hình đã huấn luyện (`@st.cache_resource`) từ `models/`.
2. Hàm `preprocess()`: chuyển ảnh về xám, resize 28×28, tự động đảo màu khi ảnh nền sáng (ảnh chụp giấy thường là mực tối trên nền sáng, ngược với quy ước MNIST là chữ số sáng trên nền tối), chuẩn hóa về [0,1], làm phẳng thành vector 784 chiều.
3. Hai tab: "Vẽ chữ số" (canvas vẽ tay) và "Tải ảnh lên" (file uploader).
4. Cột KNN: `predict()` + `predict_proba()` (KNN hỗ trợ xác suất hiệu chỉnh tự nhiên, không tốn thêm chi phí huấn luyện).
5. Cột SVM: `predict()` + `decision_function()` chuyển qua softmax làm điểm tin cậy ước lượng (SVM không bật `probability=True` để tránh huấn luyện chậm hơn ~5 lần — xem Phase 1).
6. Đã khởi chạy thật `streamlit run app.py` ở chế độ headless, xác nhận HTTP 200 và health check `ok`, không có traceback trong log server; đã dừng tiến trình dev server sau khi xác nhận.

## Todo

- [x] Cài `streamlit-drawable-canvas` (không có sẵn, đã `pip install` thành công)
- [x] Viết `app.py` với 2 tab nhập liệu và 3 cột hiển thị (ảnh đầu vào, KNN, SVM)
- [x] Chạy thử thật, xác nhận server khởi động không lỗi
- [x] Dọn dẹp tiến trình dev server sau khi xác nhận (không để tiến trình treo)

## Success Criteria

Ứng dụng khởi động thành công (`HTTP 200`, `/_stcore/health` trả `ok`),
không có exception trong log server. Mã nguồn tại `app.py`, đã verify thủ
công bằng cách curl trực tiếp vào server đang chạy thật, không chỉ dựa vào
kiểm tra cú pháp tĩnh.
