---
phase: 1
title: "Phase 1: Khởi tạo cấu trúc dự án & môi trường"
status: pending
priority: P1
effort: "0.5d"
dependencies: []
---

# Phase 1: Khởi tạo cấu trúc dự án & môi trường

## Context Links

- Plan overview: [plan.md](./plan.md)
- Không có báo cáo research/scout riêng — dự án greenfield (repo trống), không có code cũ để đối chiếu.

## Overview

- **Priority:** P1 (chặn mọi phase sau)
- **Status:** Pending
- Dựng khung thư mục Python cho toàn bộ đồ án, cấu hình môi trường (`requirements.txt`), package hoá `src/sigverify` để dùng lại được cả ở local (CPU) lẫn trên Colab/Kaggle (GPU), và ghi README mô tả cách chạy từng bước. Không có bước nào ở phase này train mô hình — chỉ dựng khung.

## Key Insights

- Container thực thi hiện tại (nơi cook chạy) nhiều khả năng **không có GPU** — huấn luyện thật (Phase 5, 6) phải chạy trên Google Colab/Kaggle theo đúng yêu cầu người dùng. Do đó repo phải **pip-installable** (`pyproject.toml`, package `sigverify`) để một notebook Colab có thể `pip install -e .` sau khi `git clone`, tái sử dụng đúng code trong `src/`.
- Vì không có GPU tại chỗ, mọi test cục bộ ở các phase sau phải chạy được trên CPU với dữ liệu tổng hợp nhỏ (fixtures), không phụ thuộc bộ CEDAR/BHSig260 thật.
- `data/`, `models_registry/`, `results/` chứa dữ liệu lớn hoặc ảnh chữ ký thật của người khác → phải nằm trong `.gitignore`, không commit vào git.

## Requirements

- [ ] Thư mục dự án đầy đủ theo cấu trúc bên dưới, mỗi package Python có `__init__.py`.
- [ ] `requirements.txt` liệt kê đầy đủ thư viện: `torch`, `torchvision`, `opencv-python`, `scikit-image`, `scikit-learn`, `numpy`, `matplotlib`, `pandas`, `pyyaml`, `tqdm`, `streamlit`, `pytest`. Gradio ghi chú là lựa chọn thay thế Streamlit, không cài mặc định để tránh phình môi trường.
- [ ] `pyproject.toml` (hoặc `setup.py`) khai báo package `sigverify` (`src/` layout) cài được bằng `pip install -e .`.
- [ ] `configs/default.yaml` chứa toàn bộ tham số mặc định dùng xuyên suốt các phase sau (đường dẫn dữ liệu, kích thước ảnh theo từng cấu hình, seed, batch size, margin mặc định, epoch tối đa, tỉ lệ chia writer-disjoint).
- [ ] `.gitignore` loại trừ `data/raw/`, `data/processed/`, `models_registry/`, `results/` (trừ các file tổng hợp nhỏ như bảng metrics), `__pycache__/`, `.ipynb_checkpoints/`, môi trường ảo.
- [ ] `README.md` mô tả mục tiêu đồ án, cấu trúc thư mục, cách cài đặt, và trỏ tới lệnh chạy cho từng phase (sẽ được các phase sau bổ sung thêm lệnh cụ thể).
- [ ] `tests/` có ít nhất một test smoke (`test_setup.py`) xác nhận `import sigverify` thành công và đọc được `configs/default.yaml`.

## Architecture

Cấu trúc thư mục gốc của repo (toàn bộ đồ án, không chỉ phase này):

```
Recognite-signature/
├── README.md
├── pyproject.toml
├── requirements.txt
├── .gitignore
├── Dockerfile                      # tạo ở Phase 9, để trống/không tồn tại ở Phase 1
├── configs/
│   └── default.yaml
├── data/
│   ├── raw/                        # gitignored — CEDAR/BHSig260 gốc tải về
│   ├── processed/                  # gitignored — ảnh sau tiền xử lý
│   └── splits/                     # writer-disjoint split, CÓ commit (JSON/CSV nhỏ)
├── src/sigverify/
│   ├── __init__.py
│   ├── preprocessing/{__init__.py, pipeline.py, datasets.py}
│   ├── pairs/{__init__.py, generator.py, splits.py}
│   ├── features/{__init__.py, handcrafted.py}
│   ├── models/{__init__.py, siamese_scratch.py, siamese_transfer.py, losses.py}
│   ├── training/{__init__.py, train_baseline.py, train_siamese.py, augment.py}
│   ├── evaluation/{__init__.py, metrics.py}
│   └── utils/{__init__.py, seed.py, config.py}
├── scripts/                        # entrypoint CLI mỏng, gọi vào src/sigverify
├── notebooks/
│   └── colab_train_siamese.ipynb   # tạo ở Phase 5
├── app/
│   ├── demo_app.py                 # Phase 9
│   └── inference.py                # Phase 9
├── models_registry/                # gitignored — trọng số .pt + threshold.json
├── results/                        # gitignored phần lớn — bảng metrics/ROC theo phase
└── tests/
```

Chỉ tạo file thật (không phải thư mục rỗng vô nghĩa với git) ở phase này cho: `README.md`, `pyproject.toml`, `requirements.txt`, `.gitignore`, `configs/default.yaml`, mọi `__init__.py`, `src/sigverify/utils/seed.py`, `src/sigverify/utils/config.py`, `tests/test_setup.py`. Các module còn lại (`pipeline.py`, `generator.py`, ...) được tạo với nội dung thật ở đúng phase sở hữu chúng (Phase 2–9) — không tạo file rỗng trước để tránh review sai lệch nội dung "đã có" khi thực ra chưa cài đặt.

## Related Code Files

- Create: `pyproject.toml`, `requirements.txt`, `.gitignore`, `README.md`
- Create: `configs/default.yaml`
- Create: `src/sigverify/__init__.py` và toàn bộ `__init__.py` con của các package liệt kê ở Architecture
- Create: `src/sigverify/utils/seed.py` (hàm `set_seed(seed: int)` cố định `random`, `numpy`, `torch`)
- Create: `src/sigverify/utils/config.py` (hàm `load_config(path) -> dict` đọc YAML)
- Create: `tests/test_setup.py`

## Implementation Steps

1. Tạo toàn bộ cây thư mục ở mục Architecture (chỉ các file thật liệt kê ở "Related Code Files"; các thư mục còn rỗng vẫn tạo `__init__.py` để package hoá).
2. Viết `pyproject.toml` với `[project] name = "sigverify"`, `dependencies` tham chiếu `requirements.txt` hoặc liệt kê trực tiếp, `[tool.setuptools.packages.find] where = ["src"]`.
3. Viết `requirements.txt` với version pin dạng `>=` an toàn (không cần pin tuyệt đối vì Colab/Kaggle tự quản lý CUDA build của torch).
4. Viết `configs/default.yaml` với các khoá tối thiểu: `seed`, `data.raw_dir`, `data.processed_dir`, `data.splits_dir`, `image.size_scratch: [220, 150]`, `image.size_transfer: [224, 224]`, `pairs.ratio_pos_hardneg_easyneg: [2, 1, 1]`, `split.train_writers: 40`, `split.val_writers: 5`, `split.test_writers: 10`, `train.batch_size: 64`, `train.max_epochs: 100`, `train.early_stop_patience: 10`, `train.margins: [0.5, 1.0, 2.0]`, `train.lr_scratch: 0.001`, `train.lr_finetune: 0.0001`.
5. Viết `.gitignore` theo Requirements.
6. Viết `src/sigverify/utils/seed.py` và `config.py`.
7. Viết `README.md`: mục tiêu, kiến trúc thư mục, hướng dẫn cài đặt (`pip install -r requirements.txt && pip install -e .`), placeholder mục "Cách chạy" sẽ được các phase sau nối thêm lệnh.
8. Viết `tests/test_setup.py`: assert `import sigverify` không lỗi, assert `load_config("configs/default.yaml")` trả về dict có khoá `seed`.
9. Chạy `pip install -e .` cục bộ (CPU) và `pytest tests/test_setup.py` để xác nhận môi trường dựng đúng.
10. Commit lên nhánh làm việc hiện tại của repo.

## Todo List

- [ ] Cây thư mục + toàn bộ `__init__.py`
- [ ] `pyproject.toml` + `requirements.txt`
- [ ] `.gitignore`
- [ ] `configs/default.yaml`
- [ ] `src/sigverify/utils/seed.py`, `config.py`
- [ ] `README.md`
- [ ] `tests/test_setup.py` xanh
- [ ] `pip install -e .` chạy sạch trên máy hiện tại (CPU-only)

## Success Criteria

- `pip install -e .` cài thành công không lỗi trên môi trường CPU hiện tại.
- `pytest tests/test_setup.py` pass.
- Cấu trúc thư mục khớp đúng mục Architecture, sẵn sàng để Phase 2 điền `preprocessing/pipeline.py` và `preprocessing/datasets.py`.
- `git status` sạch (không có file dữ liệu/trọng số lớn bị lỡ add) sau khi commit.

## Risk Assessment

- **Rủi ro:** Container thực thi không có `pip`/mạng để cài `torch` bản CPU nặng. **Giảm thiểu:** dùng bản `torch` CPU-only mặc định của PyPI (không cần chỉ định index CUDA), ghi rõ trong README rằng bản GPU sẽ được cài lại trên Colab/Kaggle.
- **Rủi ro:** Quên thêm thư mục dữ liệu/trọng số vào `.gitignore`, vô tình commit ảnh chữ ký thật hoặc file nặng. **Giảm thiểu:** review `git status` trước khi commit; test setup không tạo dữ liệu mẫu trong `data/raw`.

## Security Considerations

- Không có thông tin nhạy cảm ở phase này. Từ Phase 9 trở đi, ảnh chữ ký người dùng upload là dữ liệu cá nhân — quy tắc "không lưu ổ đĩa" phải được thiết kế xuyên suốt từ `app/inference.py` (xem Phase 9), không phải thêm vá sau.

## Next Steps

- Phase 2 phụ thuộc trực tiếp vào cấu trúc và `configs/default.yaml` của phase này.
