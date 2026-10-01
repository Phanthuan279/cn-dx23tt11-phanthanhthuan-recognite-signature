# Cài đặt và tái tạo hệ thống

Thư mục này hướng dẫn cài đặt môi trường và tái tạo lại toàn bộ pipeline,
kể cả các thành phần KHÔNG được commit vào repository (mô hình đã huấn
luyện), vì lý do dung lượng.

## 1. Cài đặt môi trường

```bash
python3 -m venv .venv && source .venv/bin/activate   # tùy chọn nhưng khuyến khích
pip install -r ../requirements.txt
pytest ../tests/    # chạy toàn bộ test, không cần tải MNIST (dùng dữ liệu tổng hợp)
```

Yêu cầu: Python 3.10+. Không cần GPU — KNN và SVM huấn luyện được trên
CPU thường trong vài phút (xem thời gian thực tế ở mục 3).

## 2. Dữ liệu thử tương ứng với kết quả đã báo cáo

Không cần tải lại MNIST để KIỂM TRA kết quả đã báo cáo — các tệp sau đã
được commit thật vào repository:

- `results/comparison_summary.json`, `results/{knn,svm}_metrics.json` —
  độ chính xác, classification report, thời gian huấn luyện — SỐ LIỆU
  THẬT từ lần huấn luyện thật.
- `results/confusion_matrix_{knn,svm}.png` — ma trận nhầm lẫn thật trên
  tập test.

Mô hình đã huấn luyện (`models/*.joblib`) KHÔNG được commit (dung lượng
lớn — file KNN chứa toàn bộ tập huấn luyện, ~170 MB) — xem mục 3 để tái
tạo khi cần chạy demo.

## 3. Tải dữ liệu gốc và huấn luyện lại từ đầu (tùy chọn)

Chỉ cần thiết nếu muốn huấn luyện lại mô hình từ đầu hoặc chạy demo (demo
cần có file mô hình trong `models/`):

```bash
python scripts/train.py
```

Lần chạy đầu tiên tự động tải MNIST thật (70.000 ảnh) qua
`sklearn.datasets.fetch_openml`, cache vào `data/` (do sklearn tự quản
lý, không cần tài khoản/API key nào). Những lần sau dùng lại bản đã tải.

Thời gian thực tế đo được trong đồ án (môi trường CPU, không có GPU):
KNN gần như tức thời (`fit()` của KNN chỉ lưu dữ liệu, không có bước tối
ưu — toàn bộ chi phí tính toán dồn vào lúc dự đoán); SVM (kernel RBF)
mất khoảng 235 giây (~4 phút) để huấn luyện trên 54.000 mẫu.

**Sơ đồ triển khai**: `MNIST thật (fetch_openml) → chia stratify
54000/6000/10000 train/val/test → huấn luyện KNN và SVM (src/digitrec/) →
lưu mô hình vào models/ + số liệu thật vào results/ → app.py load mô
hình để suy luận`.

## 4. Chạy demo

```bash
streamlit run app.py
```

Cần có mô hình đã huấn luyện trong `models/` (tái tạo theo mục 3). Demo
có hai luồng nhập liệu: vẽ chữ số trực tiếp (canvas tự viết bằng
`st.components.v2` của Streamlit, không phụ thuộc thư viện ngoài), hoặc
tải ảnh chữ số có sẵn lên.
