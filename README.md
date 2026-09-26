# Recognite-signature

Xác minh chữ ký viết tay offline (verification, không phải identification) bằng
mạng Siamese **writer-independent**: một mô hình dùng chung cho mọi người ký,
không huấn luyện lại khi có người dùng mới.

Đồ án tốt nghiệp. Kế hoạch triển khai đầy đủ nằm ở
[`plans/260926-1324-siamese-signature-verification/plan.md`](plans/260926-1324-siamese-signature-verification/plan.md).

## Cấu trúc dự án

```
├── configs/                # default.yaml + các biến thể ablation
├── data/
│   ├── raw/                # CEDAR/BHSig260 gốc (gitignored, tự tải)
│   ├── processed/          # ảnh sau tiền xử lý (gitignored)
│   └── splits/             # writer-disjoint split + cặp huấn luyện (commit)
├── src/sigverify/          # package chính
│   ├── preprocessing/      # tiền xử lý ảnh + đọc dataset
│   ├── pairs/              # chia tập + sinh cặp huấn luyện
│   ├── features/           # đặc trưng thủ công (HOG/LBP) cho baseline
│   ├── models/              # kiến trúc Siamese (scratch CNN, transfer learning) + loss
│   ├── training/           # vòng lặp huấn luyện + augmentation
│   ├── evaluation/         # FAR/FRR/EER/ROC-AUC
│   └── utils/               # seed, config
├── scripts/                # CLI mỏng gọi vào src/sigverify
├── notebooks/              # notebook chạy trên Google Colab/Kaggle (GPU)
├── app/                    # demo Streamlit (suy luận trong bộ nhớ, không lưu ảnh)
├── models_registry/        # trọng số đã train + ngưỡng τ (gitignored)
├── results/                # bảng metrics, ROC, phân tích lỗi (gitignored phần lớn)
└── tests/                  # test đơn vị, chạy được trên CPU với dữ liệu tổng hợp
```

## Cài đặt

```bash
pip install -r requirements.txt
pip install -e .
pytest tests/
```

Môi trường phát triển/test cục bộ chỉ cần CPU (mọi test dùng dữ liệu tổng hợp).
Huấn luyện thật trên CEDAR/BHSig260 chạy trên Google Colab hoặc Kaggle (GPU
miễn phí) qua `notebooks/colab_train_siamese.ipynb`.

## Cách chạy (cập nhật dần theo từng phase)

- Cài đặt môi trường: xem trên.
- Tải/khảo sát CEDAR và tiền xử lý: `python scripts/download_cedar.py`,
  `python scripts/run_preprocessing.py`.
- Sinh cặp + chia tập: `python scripts/build_pairs.py`.
- Baseline HOG/LBP+SVM: `python scripts/run_baseline.py`.
- Huấn luyện Siamese: xem `notebooks/colab_train_siamese.ipynb` (chạy trên
  Colab/Kaggle, gọi `scripts/train_config_a.py` / `scripts/train_config_b.py`).
- Ablation & tổng quát chéo BHSig260: `python scripts/run_ablations.py`.
- Phân tích lỗi: `python scripts/error_analysis.py`.
- Demo: `streamlit run app/demo_app.py`.

## Riêng tư

Ảnh chữ ký người dùng tải lên trong demo (`app/`) chỉ được xử lý trong bộ nhớ
và không bao giờ được ghi xuống đĩa hay ghi log.
