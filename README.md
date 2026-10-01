# Nhận dạng chữ số viết tay — So sánh KNN và SVM trên MNIST

Đồ án thực tập chuyên ngành — Trường Đại học Trà Vinh.

| | |
|---|---|
| Sinh viên thực hiện | Phan Thành Thuận — MSSV 170123591 — Lớp DX23TT11 |
| Giảng viên hướng dẫn | ThS. Nguyễn Nhứt Lam |
| Báo cáo đồ án đầy đủ | [`thesis/doc/thesis.docx`](thesis/doc/thesis.docx) · [`thesis/pdf/thesis.pdf`](thesis/pdf/thesis.pdf) |

## Đề tài

Huấn luyện và so sánh hiệu quả của hai mô hình học máy — **K-Nearest
Neighbors (KNN)** và **Support Vector Machine (SVM)** — trên tập dữ liệu
**MNIST** (ảnh chữ số viết tay 0-9), kèm một chương trình demo cho phép
người dùng vẽ hoặc tải ảnh một chữ số lên và xem cả hai mô hình dự đoán.

## Kết quả thật (không mô phỏng)

Huấn luyện trên dữ liệu MNIST thật (lấy qua `sklearn.datasets.fetch_openml`,
70.000 ảnh), chia theo tỉ lệ chuẩn 60.000/10.000, trong đó 54.000 dùng để
huấn luyện và 6.000 dùng để kiểm định (validation), 10.000 ảnh còn lại dùng
làm tập kiểm thử (test) hoàn toàn tách biệt:

| Mô hình | Độ chính xác (test) | Thời gian huấn luyện |
|---|---|---|
| KNN (k=5) | **97,08%** | 0,07 giây |
| SVM (kernel RBF, C=5) | **98,35%** | 235 giây (~3,9 phút) |

Chi tiết đầy đủ (precision/recall/F1 theo từng chữ số, ma trận nhầm lẫn):
xem `results/comparison_summary.json`, `results/confusion_matrix_knn.png`,
`results/confusion_matrix_svm.png`.

**Nhận xét**: SVM cho độ chính xác cao hơn KNN khoảng 1,3 điểm phần trăm,
nhưng đổi lại thời gian huấn luyện lâu hơn đáng kể (KNN gần như tức thời vì
là "lazy learner" — chỉ lưu lại dữ liệu huấn luyện, toàn bộ việc tính toán
dồn vào lúc dự đoán; SVM phải giải một bài toán tối ưu trong lúc huấn
luyện). Với tập dữ liệu nhỏ như MNIST, cả hai đều đạt độ chính xác cao,
phù hợp để so sánh đánh đổi giữa chất lượng và chi phí tính toán.

## Cấu trúc dự án

```
├── setup/                  # hướng dẫn cài đặt & tái tạo hệ thống từ đầu
├── src/digitrec/           # package chính: tải dữ liệu, mô hình, đánh giá
│   ├── data.py             # tải MNIST thật + chia tập train/val/test
│   ├── models.py           # khởi tạo KNN và SVM
│   └── evaluate.py         # tính accuracy, classification report, ma trận nhầm lẫn
├── scripts/
│   └── train.py            # huấn luyện cả hai mô hình, lưu kết quả thật vào results/
├── app.py                  # demo Streamlit: vẽ/tải ảnh chữ số, xem dự đoán
├── data/                    # cache MNIST do sklearn tự quản lý (gitignored, tái tạo bằng scripts/train.py)
├── models/                  # trọng số mô hình đã huấn luyện (gitignored, tái tạo bằng scripts/train.py)
├── results/                 # kết quả thật đã commit: metrics, ma trận nhầm lẫn
├── progress-report/         # nhật ký tiến độ thực hiện đồ án
├── thesis/                  # tài liệu báo cáo đồ án
│   ├── doc/                 # báo cáo dạng .docx
│   ├── pdf/                 # báo cáo dạng .pdf
│   ├── html/                # (dự phòng) bản web của báo cáo
│   ├── abs/                 # hình/công thức/ảnh chụp màn hình dùng trong báo cáo; video demo đặt tại đây
│   ├── refs/                # tài liệu tham khảo dùng khi làm đồ án
│   └── docgen/               # script sinh báo cáo .docx tự động (build_thesis.py, dùng python-docx)
├── plans/                   # đề cương triển khai + kế hoạch từng phase
└── tests/                   # unit test trên dữ liệu tổng hợp, không cần tải MNIST
```

## Cài đặt nhanh

Hướng dẫn cài đặt đầy đủ (bao gồm cách tải MNIST và tái tạo mô hình đã
huấn luyện, vì mô hình không được commit do dung lượng): xem
[`setup/README.md`](setup/README.md).

```bash
pip install -r requirements.txt
pytest tests/
```

## Huấn luyện lại từ đầu

```bash
python scripts/train.py
```

Lần chạy đầu tiên sẽ tải MNIST thật (~70.000 ảnh) qua `fetch_openml`, mất
khoảng 20-30 giây tùy đường truyền; những lần sau dùng lại bản đã tải (cache
trong thư mục `data/`, do sklearn tự quản lý). Huấn luyện KNN gần như tức
thời; SVM mất khoảng 4 phút trên CPU thường.

## Chạy demo

```bash
streamlit run app.py
```

Mở trình duyệt, chọn tab "Vẽ chữ số" để vẽ trực tiếp hoặc "Tải ảnh lên" để
dùng ảnh có sẵn. Cần đã chạy `scripts/train.py` trước để có mô hình trong
`models/`.

## Công nghệ sử dụng

Python, scikit-learn (KNN, SVM), NumPy/Pandas, Matplotlib (ma trận nhầm
lẫn), Streamlit (demo — bảng vẽ chữ số dùng `st.components.v2` có sẵn của
Streamlit, không phụ thuộc thư viện ngoài, vì `streamlit-drawable-canvas`
không tương thích với phiên bản Streamlit đang dùng).
