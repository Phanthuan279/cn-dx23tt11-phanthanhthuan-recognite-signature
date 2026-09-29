# Cài đặt và tái tạo hệ thống

Thư mục này hướng dẫn cài đặt môi trường và tái tạo lại toàn bộ pipeline, kể
cả các thành phần KHÔNG được commit vào repository (dữ liệu gốc CEDAR/BHSig260
và trọng số mô hình đã huấn luyện), vì lý do dung lượng và bản quyền dữ liệu.

## 1. Cài đặt môi trường

```bash
python3 -m venv .venv && source .venv/bin/activate   # tùy chọn nhưng khuyến khích
pip install -r ../requirements.txt
pip install -e ..
pytest ../tests/    # chạy toàn bộ test trên dữ liệu tổng hợp, không cần GPU/dữ liệu thật
```

Yêu cầu: Python 3.10+. Không cần GPU để chạy test hoặc demo; huấn luyện lại từ
đầu có thể chạy trên CPU (đã thực hiện thật trong đồ án này) nhưng chậm hơn
nhiều so với GPU — xem thời gian thực tế ở mục 3.

## 2. Dữ liệu thử tương ứng với kết quả đã báo cáo

Không cần tải lại dữ liệu gốc để KIỂM TRA kết quả đã báo cáo trong đồ án — các
tệp sau đã được commit thật vào repository:

- `data/splits/cedar_writer_split.json`, `train_pairs.csv`, `val_pairs.csv`,
  `test_pairs.csv` — writer-disjoint split và toàn bộ cặp ảnh (theo đường dẫn
  tương đối) dùng để huấn luyện/đánh giá, giống hệt lần chạy thật đã báo cáo.
- `results/` — `metrics.json`, `margin_sweep.json`, `predictions_test.csv`,
  `roc.png`, ảnh các ca lỗi (`results/error_analysis/`) của cả baseline, Cấu
  hình A, Cấu hình B, và kết quả zero-shot BHSig260 — đây là SỐ LIỆU THẬT thu
  được từ các lần chạy huấn luyện thật, không phải số liệu mẫu.

Ảnh chữ ký gốc (CEDAR/BHSig260) và trọng số mô hình (`models_registry/`) KHÔNG
được commit (dung lượng lớn, CEDAR/BHSig260 có điều khoản sử dụng riêng) — xem
mục 3 để tải/tái tạo khi cần chạy lại từ đầu.

## 3. Tải dữ liệu gốc và huấn luyện lại từ đầu (tùy chọn)

Chỉ cần thiết nếu muốn huấn luyện lại mô hình từ đầu (không cần cho việc đọc
kết quả đã có hoặc chạy demo với mô hình mẫu, nếu có):

```bash
# 1. Tải CEDAR và BHSig260 (cần tài khoản Kaggle, xem hướng dẫn trong script)
python scripts/download_cedar.py
python scripts/download_bhsig260.py

# 2. Tiền xử lý + sinh cặp (đã có sẵn kết quả trong data/splits/, bước này
#    dùng khi cần tái tạo lại từ ảnh gốc)
python scripts/run_preprocessing.py
python scripts/build_pairs.py

# 3. Huấn luyện (chạy tuần tự, không chạy song song hai lệnh dưới nếu chỉ có 1 CPU)
python scripts/train_config_a.py    # ~3,3 giờ trên CPU, cả 3 mức margin
python scripts/train_config_b.py    # lâu hơn đáng kể trên CPU (margin=1.0 riêng cần 47 epoch)

# 4. Đánh giá / tái tạo kết quả
python scripts/run_baseline.py
python scripts/run_ablations.py     # bao gồm zero-shot BHSig260
python scripts/error_analysis.py
```

Thời gian thực tế đo được trong đồ án (môi trường CPU, không có GPU): mỗi
epoch mất khoảng 3,3–5,6 phút tuỳ cấu hình; toàn bộ 3 mức margin của Cấu hình
A mất khoảng 3,3 giờ. Nếu có GPU (Google Colab/Kaggle), thời gian sẽ ngắn hơn
nhiều — xem `notebooks/colab_train_siamese.ipynb` để chạy trên GPU.

**Sơ đồ triển khai**: `raw CEDAR/BHSig260 ảnh gốc → tiền xử lý (pipeline.py)
→ sinh cặp writer-disjoint (pairs/) → huấn luyện (training/) → mô hình +
ngưỡng τ trong models_registry/ → app/demo_app.py load model để suy luận`.

## 4. Chạy demo

```bash
streamlit run app/demo_app.py
```

Cần có mô hình đã huấn luyện trong `models_registry/` (tái tạo theo mục 3, hoặc
dùng file mô hình nếu được chia sẻ riêng ngoài git do dung lượng).
