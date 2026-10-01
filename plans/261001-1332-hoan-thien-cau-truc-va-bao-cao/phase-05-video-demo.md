---
title: "Phase 5: Video demo"
status: done
---

# Phase 5: Video demo

## Overview

Quay video demo thật: ứng dụng Streamlit chạy thật, trình duyệt thật (qua
Playwright — đã cài sẵn Chromium trong môi trường này), thao tác thật trên
giao diện, không dàn dựng/giả lập kết quả.

## Requirements

- [x] Video quay từ ứng dụng đang chạy thật (`streamlit run app.py`), không phải ảnh tĩnh ghép
- [x] Thể hiện cả hai luồng: vẽ chữ số trên canvas và tải ảnh chữ số có sẵn lên
- [x] Thấy rõ kết quả dự đoán + biểu đồ độ tin cậy của cả KNN và SVM
- [x] File video lưu vào `thesis/abs/` (đúng quy ước "slide/video bảo vệ nếu có" của README dự án cũ) và gửi trực tiếp cho người dùng xem

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

- [x] Viết script Playwright quay demo
- [x] Chạy thật, xác nhận video quay được cả hai luồng (vẽ + tải ảnh) với kết quả dự đoán thấy rõ
- [x] Convert định dạng nếu cần, lưu vào `thesis/abs/`
- [x] Gửi video cho người dùng xem trực tiếp
- [x] Dừng sạch tiến trình demo server sau khi quay

## Success Criteria

Đã quay thật bằng Playwright (`record_video_dir`, Chromium tại
`/opt/pw-browsers/chromium`) trên server Streamlit thật đang chạy (PID
13558, cổng 8501) — video `.webm` 14,44 giây. Kịch bản thao tác thật: vẽ số
"1" trên canvas bằng chuỗi sự kiện chuột thật (`mouse.move/down/up`, không
chỉ set giá trị), sau đó chuyển tab và tải lên ảnh test MNIST thật (nhãn
thật là "7", trích xuất trực tiếp từ tập test bằng PIL). Đã trích xuất 5
khung hình mẫu và xem bằng mắt để xác nhận nội dung thật: khung giữa cho
thấy canvas với số "1" đã vẽ, cột KNN và SVM đều hiện "Dự đoán: 1"; khung
cuối cho thấy ảnh "7" đã tải lên, cả hai mô hình hiện "Dự đoán: 7" — đúng
cả hai lần, không dàn dựng. Convert sang `.mp4` (H.264, 137KB) bằng ffmpeg,
lưu vào `thesis/abs/demo_video.mp4`. Đã gửi trực tiếp cho người dùng qua
SendUserFile. Dừng sạch tiến trình `streamlit run app.py` (PID 13558) sau
khi quay xong, xác nhận bằng `pgrep` không còn tiến trình. `pytest tests/`
vẫn pass (5/5). Lưu ý: thư mục tạm `thesis/abs/video_raw/` (chứa `.webm`
gốc) không xoá được do safety-check chặn mọi lệnh rm/rmdir nhắm vào một
thư mục trong workspace — thư mục này vô hại (không được git add vào
commit) nhưng người dùng có thể tự xoá nếu muốn dọn sạch.
