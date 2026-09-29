# Xây dựng hệ thống xác minh chữ ký viết tay offline sử dụng mạng nơ-ron Siamese

Đồ án thực tập chuyên ngành — Trường Đại học Trà Vinh, Trường Kỹ thuật và Công nghệ, Khoa Công nghệ thông tin.

Xác minh chữ ký viết tay offline (verification, không phải identification) bằng
mạng Siamese **writer-independent**: một mô hình dùng chung cho mọi người ký,
không cần huấn luyện lại khi có người ký mới.

| | |
|---|---|
| Sinh viên thực hiện | Phan Thành Thuận — MSSV 170123591 — Lớp DX23TT11 |
| Giảng viên hướng dẫn | ThS. Nguyễn Nhứt Lam |
| Đề cương chi tiết đã duyệt | `plans/260926-1324-siamese-signature-verification/plan.md` |
| Báo cáo đồ án đầy đủ | [`thesis/doc/thesis.docx`](thesis/doc/thesis.docx) · [`thesis/pdf/thesis.pdf`](thesis/pdf/thesis.pdf) |

## Trạng thái hiện tại (số liệu thật, không mô phỏng)

Đối chiếu với 8 thí nghiệm (T1–T8) đề ra trong đề cương chi tiết:

| Mã | Nội dung | Trạng thái |
|---|---|---|
| T1 | Baseline HOG + SVM trên CEDAR | ✅ Hoàn thành |
| T2 | Cấu hình A (Siamese CNN từ đầu) | ✅ Hoàn thành (cả 3 mức margin) |
| T3 | Cấu hình B (Siamese ResNet18) | ⚠️ Hoàn thành 2/3 margin — mất margin=2,0 do container tính toán khởi động lại giữa chừng |
| T4 | Ảnh hưởng tiền xử lý (nhị phân hoá, kích thước ảnh) | ❌ Chưa thực hiện — thiếu thời gian (huấn luyện trên CPU) |
| T5 | Ảnh hưởng huấn luyện (augmentation, margin) | ⚠️ Một phần — đã khảo sát margin, chưa augmentation on/off |
| T6 | So sánh contrastive vs triplet loss | ❌ Chưa thực hiện (tùy chọn theo đề cương) |
| T7 | Tổng quát chéo CEDAR → BHSig260 (zero-shot) | ✅ Hoàn thành |
| T8 | Mẫu chữ ký tự thu thập | ❌ Chưa thực hiện (tùy chọn theo đề cương) |

Kết quả tổng thể trên tập test CEDAR (800 cặp, 10 người ký chưa từng xuất hiện lúc huấn luyện):

| Mô hình | AUC | EER (validation) | FAR random forgery |
|---|---|---|---|
| Baseline HOG + SVM | 0,887 | — | 16,5% |
| Cấu hình A (CNN từ đầu) | 0,915 | 9,75% | 39,5% |
| **Cấu hình B (ResNet18, transfer learning)** | **0,955** | **5,50%** | **13,0%** |

Chi tiết đầy đủ, phân tích lỗi định tính, và kết quả zero-shot trên BHSig260: xem
`results/` (số liệu thật) hoặc chương 4 của báo cáo (`thesis/pdf/thesis.pdf`).

## Cấu trúc dự án

```
├── setup/                  # hướng dẫn cài đặt & tái tạo hệ thống từ đầu
├── src/sigverify/          # package chính
│   ├── preprocessing/      # tiền xử lý ảnh + đọc dataset
│   ├── pairs/              # chia tập writer-disjoint + sinh cặp huấn luyện
│   ├── features/           # đặc trưng thủ công (HOG/LBP) cho baseline
│   ├── models/             # kiến trúc Siamese (scratch CNN, transfer learning) + loss
│   ├── training/           # vòng lặp huấn luyện + augmentation
│   ├── evaluation/         # FAR/FRR/EER/ROC-AUC
│   └── utils/              # seed, config
├── scripts/                # CLI mỏng gọi vào src/sigverify (huấn luyện, đánh giá, ablation)
├── configs/                # default.yaml + các biến thể ablation
├── notebooks/              # notebook tham khảo để chạy trên Google Colab/Kaggle (GPU)
├── app/                    # demo Streamlit (suy luận trong bộ nhớ, không lưu ảnh)
├── data/
│   ├── raw/                # CEDAR/BHSig260 gốc (gitignored — có bản quyền/dung lượng lớn, tự tải theo setup/)
│   ├── processed/          # ảnh sau tiền xử lý (gitignored, tái tạo được)
│   └── splits/             # writer-disjoint split + cặp huấn luyện/test (đã commit — dữ liệu thử thật)
├── models_registry/        # trọng số đã huấn luyện + ngưỡng τ (gitignored — xem setup/ để tái tạo)
├── results/                # metrics, ROC, dự đoán từng cặp, phân tích lỗi — SỐ LIỆU THẬT (đã commit)
├── progress-report/        # nhật ký tiến độ thực hiện đồ án
├── thesis/                 # tài liệu báo cáo đồ án
│   ├── doc/                # báo cáo dạng .docx
│   ├── pdf/                # báo cáo dạng .pdf
│   ├── html/                # (dự phòng) bản web của báo cáo
│   ├── abs/                # hình/công thức/ảnh chụp màn hình dùng trong báo cáo; slide/video bảo vệ (nếu có) đặt tại đây
│   ├── refs/                # tài liệu tham khảo dùng khi làm đồ án
│   └── docgen/             # script sinh báo cáo .docx tự động (build_thesis.py, dùng python-docx)
├── plans/                  # đề cương chi tiết + kế hoạch triển khai từng phase
├── Dockerfile              # đóng gói demo chạy CPU
└── tests/                  # test đơn vị, chạy được trên CPU với dữ liệu tổng hợp
```

## Cài đặt nhanh

Hướng dẫn cài đặt đầy đủ (bao gồm cách tải dữ liệu thật và tái tạo mô hình đã
huấn luyện, vì các tệp này không được commit do dung lượng/bản quyền): xem
[`setup/README.md`](setup/README.md).

```bash
pip install -r requirements.txt
pip install -e .
pytest tests/
```

Môi trường phát triển/test cục bộ chỉ cần CPU (mọi test dùng dữ liệu tổng hợp).
Huấn luyện thật trên CEDAR/BHSig260 trong đồ án này chạy hoàn toàn trên CPU
(không có GPU khả dụng trong môi trường thực thi) — xem `setup/README.md` để
biết thời gian thực tế.

## Cách chạy lại từng bước

- Cài đặt môi trường: xem `setup/README.md`.
- Tải/khảo sát CEDAR và tiền xử lý: `python scripts/download_cedar.py`,
  `python scripts/run_preprocessing.py`.
- Sinh cặp + chia tập: `python scripts/build_pairs.py`.
- Baseline HOG/LBP+SVM: `python scripts/run_baseline.py`.
- Huấn luyện Siamese (Cấu hình A/B): `python scripts/train_config_a.py`,
  `python scripts/train_config_b.py` (tham khảo thêm
  `notebooks/colab_train_siamese.ipynb` nếu chạy trên GPU Colab/Kaggle).
- Ablation & tổng quát chéo BHSig260: `python scripts/run_ablations.py`.
- Phân tích lỗi: `python scripts/error_analysis.py`.
- Sinh lại báo cáo đồ án (.docx/.pdf): `python thesis/docgen/build_thesis.py`.
- Demo: `streamlit run app/demo_app.py`.

## Riêng tư

Ảnh chữ ký người dùng tải lên trong demo (`app/`) chỉ được xử lý trong bộ nhớ
và không bao giờ được ghi xuống đĩa hay ghi log.
