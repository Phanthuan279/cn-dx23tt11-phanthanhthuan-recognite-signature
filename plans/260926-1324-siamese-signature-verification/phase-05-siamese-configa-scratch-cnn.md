---
phase: 5
title: "Phase 5: Mạng Siamese Cấu hình A (CNN huấn luyện từ đầu)"
status: pending
priority: P1
effort: "3d"
dependencies: [3, 4]
---

# Phase 5: Mạng Siamese Cấu hình A (CNN huấn luyện từ đầu)

## Context Links

- Phase trước: [Phase 4: Baseline HOG/LBP + SVM](./phase-04-baseline-hog-lbp-svm.md)
- Plan overview: [plan.md](./plan.md)

## Overview

- **Priority:** P1
- **Status:** Pending
- Cài đặt mạng Siamese CNN huấn luyện từ đầu (Cấu hình A), contrastive loss với sweep margin {0.5, 1.0, 2.0}, augmentation không lật ngang, huấn luyện thật chạy trên Colab/Kaggle (GPU), đánh giá bằng khung Phase 3, so sánh bắt buộc với baseline Phase 4.

## Key Insights

- **Không L2-normalize embedding theo mặc định.** Nếu chuẩn hoá về vector đơn vị, khoảng cách Euclid tối đa giữa 2 vector là 2 — margin 2.0 mà người dùng yêu cầu thử sẽ gần như luôn bị "chạm trần", làm sai lệch ý nghĩa của việc sweep 3 giá trị margin. Giữ embedding thô (không chuẩn hoá) làm mặc định để 3 margin {0.5, 1.0, 2.0} đều có ý nghĩa thực sự trên một dải khoảng cách rộng hơn; L2-normalize được đưa vào Phase 7 như một biến thể ablation, không phải mặc định ở đây.
- **Không có GPU tại chỗ.** Phase này viết code training/eval đầy đủ và test được trên CPU với dữ liệu tổng hợp nhỏ (vài chục cặp), nhưng **huấn luyện thật với CEDAR đầy đủ chạy trên Colab/Kaggle** — cần một notebook (`notebooks/colab_train_siamese.ipynb`) `git clone` repo, `pip install -e .`, rồi gọi đúng hàm/CLI trong `src/sigverify` và `scripts/train_config_a.py`, không viết lại logic training trong notebook.
- **KHÔNG lật ngang (horizontal flip)** — đây là ràng buộc miền bài toán cứng (chữ ký có hướng viết cố định), phải được kiểm tra bằng test tĩnh (rà `augment.py` không gọi bất kỳ hàm flip ngang nào), không chỉ ghi chú bằng lời.
- Augmentation chỉ áp dụng cho **cặp huấn luyện** (train), không áp dụng cho val/test — val/test phải đánh giá trên ảnh đã tiền xử lý gốc, cố định, để kết quả tái lập được giữa các lần chạy.
- Chọn margin tốt nhất bằng **EER trên validation**, không phải loss huấn luyện, và không phải test — 3 lần train (1 mỗi margin) đều dùng chung early stopping theo `val_eer`, chọn model+margin có `val_eer` thấp nhất trước khi chạm vào test lần đầu và duy nhất.

## Requirements

- [ ] `src/sigverify/models/siamese_scratch.py`: `class SiameseScratchCNN(nn.Module)` — 4-5 khối `Conv2d+BatchNorm2d+ReLU+MaxPool2d`, kênh tăng dần (vd. 32→64→128→256), theo sau 1-2 `Linear` cho ra embedding 128 chiều; input 1 kênh (grayscale), kích thước `image.size_scratch` (220×150).
- [ ] `src/sigverify/models/losses.py`: `class ContrastiveLoss(nn.Module)` implement đúng `L(y,D) = y·D² + (1-y)·max(0, m-D)²` với `y=1` nghĩa là cặp cùng người (genuine-genuine) — **thống nhất quy ước nhãn** với `y_pair` dùng trong Phase 3 (label=1 same/genuine, label=0 different) để không lệch dấu so với `metrics.py`.
- [ ] `src/sigverify/training/augment.py`: augmentation train-only — xoay ±5°, dịch chuyển/co giãn nhẹ, nhiễu Gaussian nhẹ; **không có** hàm lật ngang/dọc nào trong module này.
- [ ] `src/sigverify/training/train_siamese.py`: vòng lặp huấn luyện tổng quát dùng chung cho Config A và B (nhận model, loss, optimizer, dataloader làm tham số) — Adam, early stopping theo `val_eer` (patience từ config), lưu checkpoint tốt nhất theo `val_eer`.
- [ ] `scripts/train_config_a.py`: CLI train Config A, lặp qua `train.margins` từ config, mỗi margin một lần train đầy đủ, chọn margin tốt nhất theo `val_eer`, đánh giá model tốt nhất trên test (skilled + random forgery tách riêng), lưu `models_registry/config_a_best.pt` + `models_registry/config_a_threshold.json` (chứa `tau*` đã đóng băng) + `results/config_a/metrics.json` + `results/config_a/roc.png` + `results/config_a/margin_sweep.json` (val_eer mỗi margin, để đưa vào báo cáo).
- [ ] `notebooks/colab_train_siamese.ipynb`: notebook tối giản — cell 1 clone repo + cài đặt, cell 2 tải CEDAR (gọi `scripts/download_cedar.py`), cell 3 gọi `scripts/build_pairs.py`, cell 4 gọi `scripts/train_config_a.py`, cell 5 in bảng kết quả từ `results/config_a/metrics.json`. Không định nghĩa lớp mô hình/loss trực tiếp trong notebook.
- [ ] `tests/test_siamese_model.py`: forward pass CPU trên batch giả (vd. `torch.randn(4,1,150,220)`), assert output shape `(4,128)`; `ContrastiveLoss` trên vài giá trị D/y biết trước đáp án (vd. `y=1,D=0` → loss=0; `y=0,D=0,margin=1` → loss=1).
- [ ] `tests/test_augment.py`: assert module `augment.py` không import/gọi bất kỳ API lật ảnh ngang nào (kiểm tra tĩnh bằng cách rà tên hàm được gọi, hoặc property-based: áp augmentation nhiều lần lên ảnh có nội dung bất đối xứng rõ ràng và assert không có lần nào bị lật theo trục ngang).

## Architecture

```
SiameseScratchCNN (dùng chung 2 nhánh, shared weights — 1 instance, gọi 2 lần):
  Input (1, 220, 150)
  → [Conv(32,3x3)+BN+ReLU+MaxPool(2)] → [Conv(64)+BN+ReLU+MaxPool(2)]
  → [Conv(128)+BN+ReLU+MaxPool(2)] → [Conv(256)+BN+ReLU+MaxPool(2)]
  → [Conv(256)+BN+ReLU+MaxPool(2)]   # khối thứ 5, tuỳ theo kích thước còn lại sau 4 khối đầu
  → Flatten → Linear(→512) → ReLU → Dropout → Linear(→128)   # embedding, KHÔNG L2-normalize mặc định

forward_pair(x1, x2):
  e1 = model(x1); e2 = model(x2)
  D = ||e1 - e2||_2

Huấn luyện (mỗi margin m ∈ {0.5, 1.0, 2.0}):
  Adam(lr=1e-3) → ContrastiveLoss(margin=m) → early stop theo val_eer (patience cấu hình)
  → chọn margin* = argmin(val_eer qua 3 lần train)
  → evaluate_at_threshold trên test với tau* chọn từ val của margin* (theo đúng quy trình Phase 3)
```

## Related Code Files

- Create: `src/sigverify/models/siamese_scratch.py`
- Create: `src/sigverify/models/losses.py`
- Create: `src/sigverify/training/augment.py`
- Create: `src/sigverify/training/train_siamese.py`
- Create: `scripts/train_config_a.py`
- Create: `notebooks/colab_train_siamese.ipynb`
- Create: `tests/test_siamese_model.py`
- Create: `tests/test_augment.py`
- Modify: `configs/default.yaml` — xác nhận `train.margins`, `train.lr_scratch`, `train.batch_size`, `train.max_epochs`, `train.early_stop_patience` (đã thêm ở Phase 1) đủ dùng; thêm `model.embedding_dim: 128`, `model.l2_normalize: false`.

## Implementation Steps

1. Viết `SiameseScratchCNN`, tính toán số chiều Flatten dựa trên `image.size_scratch` (dùng `nn.AdaptiveAvgPool2d` hoặc tính tay kích thước sau 5 lần MaxPool(2) để tránh lỗi shape mismatch khi đổi `target_size`).
2. Viết `ContrastiveLoss` đúng công thức, đơn vị hoá theo batch (`mean` qua batch).
3. Viết `test_siamese_model.py` và `test_augment.py` **trước** khi viết `train_siamese.py` đầy đủ, chạy trên CPU với dữ liệu giả để bắt lỗi shape/dấu sớm.
4. Viết `augment.py`: các hàm `random_rotation(img, max_deg=5)`, `random_affine_jitter(img, translate=..., scale=...)`, `add_gaussian_noise(img, std=...)`, hợp thành 1 pipeline augmentation áp dụng ngẫu nhiên (không phải luôn cả 3) cho ảnh train.
5. Viết `train_siamese.py::train_one_config(model, train_loader, val_loader, margin, lr, max_epochs, patience) -> (best_state_dict, history)` — vòng lặp epoch, mỗi epoch: train (có augment), eval trên val (không augment) → tính `val_eer` bằng khung Phase 3 → early stop nếu không cải thiện sau `patience` epoch.
6. Viết `scripts/train_config_a.py`: lặp `for margin in config.train.margins`, gọi `train_one_config`, log `val_eer` mỗi margin vào `results/config_a/margin_sweep.json`, chọn tốt nhất, load lại best checkpoint, đánh giá trên test (skilled + random tách riêng), lưu toàn bộ artefact nêu ở Requirements.
7. Viết `notebooks/colab_train_siamese.ipynb` theo cấu trúc nêu ở Requirements — notebook chỉ là lớp điều phối mỏng.
8. Chạy `pytest tests/test_siamese_model.py tests/test_augment.py` (CPU, dữ liệu giả — phải xanh trong môi trường thực thi hiện tại không có GPU/không có CEDAR).
9. **[Thực hiện trên Colab/Kaggle, ngoài môi trường code hiện tại]** chạy `notebooks/colab_train_siamese.ipynb` với CEDAR thật, tải `models_registry/config_a_best.pt` + `results/config_a/*` về, so sánh `results/config_a/metrics.json` với `results/baseline/metrics.json` — xác nhận EER Siamese thấp hơn baseline theo yêu cầu người dùng; nếu không, ghi rõ trong `results/config_a/metrics.json` (trường `beats_baseline: false`) thay vì che giấu.

## Todo List

- [ ] `SiameseScratchCNN` forward pass đúng shape, test CPU pass
- [ ] `ContrastiveLoss` đúng công thức, test biết trước đáp án pass
- [ ] `augment.py` không có lật ngang, có test tĩnh xác nhận
- [ ] Vòng lặp train chung dùng lại được cho Config B (Phase 6)
- [ ] Margin sweep {0.5, 1.0, 2.0} chạy đủ 3 lần, chọn theo `val_eer`
- [ ] Threshold đóng băng đúng quy trình Phase 3 (không rò rỉ test)
- [ ] So sánh kết quả với `results/baseline/metrics.json`, ghi rõ đạt/không đạt

## Success Criteria

- `pytest tests/test_siamese_model.py tests/test_augment.py` pass trên CPU, không cần CEDAR/GPU.
- `notebooks/colab_train_siamese.ipynb` chạy hết không lỗi trên Colab/Kaggle (xác minh khi thực thi thật, ngoài phạm vi môi trường code hiện tại).
- `results/config_a/metrics.json` có EER tách riêng skilled/random forgery, kèm cờ `beats_baseline` so với Phase 4.
- Chỉ tiêu đề xuất của người dùng (EER ≤ 5% skilled forgery trên CEDAR) được ghi nhận đạt/không đạt minh bạch, không làm tròn/che số liệu nếu không đạt.

## Risk Assessment

- **Rủi ro cao:** không đạt chỉ tiêu EER ≤5% ngay ở cấu hình A. **Giảm thiểu:** đây là kỳ vọng đã được người dùng gắn nhãn "chỉ tiêu đề xuất", không phải điều kiện chặn tiến độ — Phase 6 (transfer learning) và Phase 7 (ablation) là các đòn bẩy cải thiện tiếp theo; báo cáo trung thực số liệu Config A dù đạt hay chưa.
- **Rủi ro:** early stopping theo `val_eer` không ổn định ở vài epoch đầu (EER dao động mạnh khi model chưa hội tụ) gây dừng sớm sai. **Giảm thiểu:** thêm "warm-up" tối thiểu (vd. không cho early-stop trước epoch thứ 5-10) trong `train_one_config`.
- **Rủi ro:** notebook Colab lệch phiên bản thư viện so với `requirements.txt`. **Giảm thiểu:** notebook luôn `pip install -e .` từ đúng commit của repo thay vì cài thủ công từng thư viện.

## Security Considerations

- Không có dữ liệu cá nhân người dùng cuối ở phase này.

## Next Steps

- Phase 6 tái sử dụng `train_siamese.py::train_one_config` và toàn bộ khung Phase 3, chỉ thay `model` bằng kiến trúc transfer learning và đổi `lr`/kích thước ảnh/chuẩn hoá.
