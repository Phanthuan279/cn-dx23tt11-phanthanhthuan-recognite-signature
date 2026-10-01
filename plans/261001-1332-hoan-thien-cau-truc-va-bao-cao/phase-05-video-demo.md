---
title: "Phase 5: Video demo"
status: todo
---

# Phase 5: Video demo

## Overview

Quay video demo thật: ứng dụng Streamlit chạy thật, trình duyệt thật (qua
Playwright — đã cài sẵn Chromium trong môi trường này), thao tác thật trên
giao diện, không dàn dựng/giả lập kết quả.

## Requirements

- [ ] Video quay từ ứng dụng đang chạy thật (`streamlit run app.py`), không phải ảnh tĩnh ghép
- [ ] Thể hiện cả hai luồng: vẽ chữ số trên canvas và tải ảnh chữ số có sẵn lên
- [ ] Thấy rõ kết quả dự đoán + biểu đồ độ tin cậy của cả KNN và SVM
- [ ] File video lưu vào `thesis/abs/` (đúng quy ước "slide/video bảo vệ nếu có" của README dự án cũ) và gửi trực tiếp cho người dùng xem

## Implementation Steps

1. Khởi động `streamlit run app.py` (chạy nền, theo đúng cách quản lý tiến trình đã dùng xuyên suốt phiên này — tách biệt khỏi theo dõi của harness nếu cần chạy lâu, dọn dẹp sau khi quay xong).
2. Dùng Playwright (`sync_playwright`, `executablePath: '/opt/pw-browsers/chromium'` theo đúng cấu hình môi trường) mở trình duyệt với `record_video_dir` để quay lại toàn bộ phiên.
3. Kịch bản thao tác thật:
   - Mở trang demo, chờ tải xong.
   - Tab "Tải ảnh lên": tải một ảnh chữ số thật lấy từ `results/` hoặc trích xuất trực tiếp một ảnh test MNIST thật (ghi ra file tạm bằng PIL), xem kết quả dự đoán của cả hai mô hình hiện ra.
   - Tab "Vẽ chữ số": mô phỏng vẽ bằng chuỗi sự kiện chuột thật (`mouse.move/down/up`) phác một nét chữ số đơn giản (ví dụ số 1 hoặc số 7 — dễ vẽ bằng vài đường thẳng), xem kết quả dự đoán cập nhật.
   - Dừng lại vài giây ở mỗi kết quả để video dễ xem.
4. Đóng browser context để Playwright ghi file video hoàn chỉnh (`.webm`), chuyển đổi sang `.mp4` bằng `ffmpeg` nếu cần định dạng phổ biến hơn.
5. Lưu video vào `thesis/abs/demo_video.mp4` (hoặc `.webm` nếu giữ nguyên), và gửi trực tiếp cho người dùng qua kênh gửi file.
6. Dừng tiến trình `streamlit run app.py` sau khi quay xong (không để tiến trình treo).

## Todo

- [ ] Viết script Playwright quay demo
- [ ] Chạy thật, xác nhận video quay được cả hai luồng (vẽ + tải ảnh) với kết quả dự đoán thấy rõ
- [ ] Convert định dạng nếu cần, lưu vào `thesis/abs/`
- [ ] Gửi video cho người dùng xem trực tiếp
- [ ] Dừng sạch tiến trình demo server sau khi quay

## Success Criteria

Có một file video thật (không phải ảnh tĩnh, không dàn dựng) cho thấy ứng
dụng hoạt động đúng với cả hai luồng nhập liệu và kết quả dự đoán thật của
cả hai mô hình. Video được lưu trong repo và đã gửi cho người dùng xem.
