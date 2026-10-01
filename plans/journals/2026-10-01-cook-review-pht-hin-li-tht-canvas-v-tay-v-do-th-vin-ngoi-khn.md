---
title: "Cook review phát hiện lỗi thật: canvas vẽ tay vỡ do thư viện ngoài không tương thích"
date: 2026-10-01
summary: "Rà soát trước khi nộp bài phát hiện streamlit-drawable-canvas vỡ ngay lúc import; đã thay bằng canvas tự viết dùng API gốc Streamlit, thêm test hồi quy."
---

# Cook review phát hiện lỗi thật: canvas vẽ tay vỡ do thư viện ngoài không tương thích

## What happened

Chạy `/ak:cook` để rà soát dự án "Nhận dạng chữ số viết tay" trước khi nộp
bài (theo yêu cầu của người dùng). Kiểm tra ban đầu ở phiên trước (HTTP 200
+ `/_stcore/health` trả `ok` khi chạy `streamlit run app.py`) đã bị coi là
đủ để xác nhận demo hoạt động -- **đây là xác minh sai/không đủ**.

Khi rà soát lại lần này, thử `python -c "import app"` trực tiếp thì vỡ ngay
ở dòng `from streamlit_drawable_canvas import st_canvas`:

```
StreamlitAPIException: Component 'streamlit-drawable-canvas.streamlit_drawable_canvas'
must be declared in pyproject.toml with asset_dir to use file-backed css.
```

Tái lập y hệt trong một venv hoàn toàn sạch (`streamlit==1.64.0` +
`streamlit-drawable-canvas==0.13.0`, phiên bản mới nhất của cả hai) --
xác nhận đây là lỗi không tương thích thật giữa API `components.v2` mới
của Streamlit và thư viện `streamlit-drawable-canvas` (chỉ hỗ trợ API
`components.v1` cũ, không có bản cập nhật).

Gốc rễ của việc bỏ sót: Streamlit chỉ thực thi script ứng dụng theo từng
phiên trình duyệt kết nối qua WebSocket. Tiến trình server gốc khởi động
và lắng nghe bình thường ngay cả khi script sẽ crash ngay lúc một trình
duyệt thật kết nối -- `curl` vào `/` và `/_stcore/health` chỉ xác nhận
tiến trình sống, không xác nhận script chạy được.

## Decision

- Bỏ hẳn `streamlit-drawable-canvas` khỏi `requirements.txt`.
- Tự viết canvas vẽ tay bằng `st.components.v2.component(html=, css=, js=)`
  -- API gốc, có sẵn trong Streamlit, không phụ thuộc thư viện ngoài nào.
  Đúng tinh thần công nghệ gợi ý của đề tài: "có thể thay bằng công nghệ
  tương đương nếu giải thích được lựa chọn và bảo đảm sản phẩm chạy ổn định".
- Xác minh lại bằng `streamlit.testing.v1.AppTest` (chạy script thật qua
  script-runner thật, không phải chỉ kiểm tra server sống): 0 exception,
  tiêu đề/tab/thông báo đúng như kỳ vọng.
- Gọi trực tiếp pipeline `preprocess()` → `predict()`/`predict_proba()`/
  `decision_function()` trên một ảnh MNIST test thật (nhãn thật = 3): cả
  KNN và SVM dự đoán đúng = 3.
- Thêm `test_app_runs_without_exceptions` (dùng `AppTest`) vào bộ test để
  lỗi tương tự trong tương lai bị bắt tự động, không cần nhớ phải kiểm tra
  thủ công theo đúng cách.
- Cập nhật README, requirements.txt, và plan phase-02 cho khớp với giải
  pháp thật đã dùng.

## Next steps

Không còn việc gì bắt buộc. Plan đã 100% hoàn thành (3/3 phase, giờ với
nội dung chính xác). Mã nguồn đã đẩy lên nhánh
`nhan-dang-chu-so-viet-tay` trên
https://github.com/Phanthuan279/cn-dx23tt11-phanthanhthuan-recognite-signature,
commit mới nhất `59b5093`.

> Historical work record — not durable authority. Prefer docs/specs/ADRs for current decisions.
