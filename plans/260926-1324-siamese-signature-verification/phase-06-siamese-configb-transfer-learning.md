---
phase: 6
title: "Phase 6: Mạng Siamese Cấu hình B (Transfer Learning ResNet18/VGG16)"
status: pending
priority: P1
effort: "2.5d"
dependencies: [5]
---

# Phase 6: Mạng Siamese Cấu hình B (Transfer Learning ResNet18/VGG16)

## Context Links

- Phase trước: [Phase 5: Mạng Siamese Cấu hình A (CNN huấn luyện từ đầu)](./phase-05-siamese-configa-scratch-cnn.md)
- Plan overview: [plan.md](./plan.md)

## Overview

- **Priority:** P1
- **Status:** Pending
- Cài đặt nhánh Siamese dùng backbone pretrained (ResNet18 mặc định, VGG16 là lựa chọn thay thế cấu hình được) trên ImageNet, thay lớp cuối bằng lớp embedding 128 chiều, fine-tune 2 giai đoạn (đóng băng → mở dần), so sánh với Config A và baseline.

## Key Insights

- **Ảnh input phải đổi sang 3 kênh + chuẩn hoá ImageNet** (đã có sẵn `mode="imagenet"` trong `pipeline.py` từ Phase 2) và resize `224×224` (`image.size_transfer`), khác hoàn toàn pipeline dữ liệu của Config A (1 kênh, 220×150, `mode="unit"`) — không dùng chung DataLoader giữa 2 cấu hình, chỉ dùng chung `train_siamese.py::train_one_config` (nhận model/loss/optimizer/dataloader làm tham số, không giả định kích thước ảnh).
- **Fine-tune 2 giai đoạn ("fine-tune dần" theo đúng yêu cầu người dùng):**
  1. Giai đoạn 1: đóng băng toàn bộ backbone pretrained, chỉ train lớp embedding mới thêm vào, `lr=1e-4`, vài epoch để lớp mới ổn định trước khi chạm vào trọng số pretrained.
  2. Giai đoạn 2: mở khối cuối cùng của backbone (`layer4` với ResNet18, khối conv cuối với VGG16), tiếp tục train cùng lúc với lớp embedding, `lr` thấp hơn (vd. `1e-5`) cho phần backbone mở ra, `1e-4` cho lớp embedding (dùng param groups riêng trong Adam).
- Cùng contrastive loss, cùng quy trình chọn margin theo `val_eer`, cùng quy tắc đóng băng ngưỡng τ trên val như Phase 5 — không phát minh lại quy trình đánh giá.
- Backbone mặc định là **ResNet18** (nhẹ hơn VGG16, phù hợp fine-tune trên GPU miễn phí Colab/Kaggle với thời gian giới hạn); VGG16 để cấu hình được (`model.transfer_backbone: "resnet18" | "vgg16"`) làm phương án so sánh nếu còn thời gian, không bắt buộc chạy cả hai.

## Requirements

- [x] `src/sigverify/models/siamese_transfer.py`: `class SiameseTransferCNN(nn.Module)` — load `torchvision.models.resnet18(weights=...)` hoặc `vgg16(weights=...)` theo config, thay lớp phân loại cuối bằng `Linear(→128)`, expose `freeze_backbone()`/`unfreeze_last_block()` để phục vụ 2 giai đoạn fine-tune.
- [x] `scripts/train_config_b.py`: CLI train Config B — giai đoạn 1 (đóng băng) rồi giai đoạn 2 (mở khối cuối), lặp qua `train.margins`, chọn margin tốt nhất theo `val_eer`, đánh giá test tách skilled/random forgery, lưu `models_registry/config_b_best.pt` + `models_registry/config_b_threshold.json` + `results/config_b/metrics.json` + `results/config_b/roc.png`.
- [x] `results/comparison_summary.md` (hoặc `.json` kèm bảng) tổng hợp Baseline vs Config A vs Config B: FAR/FRR/EER/Accuracy/AUC theo từng loại forgery, để dùng trực tiếp trong báo cáo đồ án.
- [x] `tests/test_transfer_model.py`: forward pass CPU trên batch giả `torch.randn(2,3,224,224)`, assert output `(2,128)`; assert `freeze_backbone()` đặt `requires_grad=False` cho toàn bộ tham số backbone, `unfreeze_last_block()` chỉ mở đúng khối cuối (kiểm bằng đếm số tham số `requires_grad=True` trước/sau).

## Architecture

```
SiameseTransferCNN:
  backbone = resnet18(weights=IMAGENET1K_V1)   # hoặc vgg16, theo config
  backbone.fc (hoặc classifier cuối) = Linear(in_features, 128)   # lớp embedding thay thế

forward_pair(x1, x2):  # x1, x2: (N,3,224,224), đã normalize ImageNet mean/std
  e1 = backbone(x1); e2 = backbone(x2)
  D = ||e1 - e2||_2

Fine-tune 2 giai đoạn:
  Stage 1: freeze_backbone() → Adam([embedding_params], lr=1e-4) → vài epoch
  Stage 2: unfreeze_last_block() → Adam([{params: last_block, lr=1e-5}, {params: embedding, lr=1e-4}]) → tiếp tục đến khi early-stop theo val_eer

Đánh giá: giống hệt quy trình Phase 5 (margin sweep theo val_eer → đóng băng tau* → test tách skilled/random)
```

## Related Code Files

- Create: `src/sigverify/models/siamese_transfer.py`
- Create: `scripts/train_config_b.py`
- Create: `results/comparison_summary.md` (sinh tự động từ script, không viết tay)
- Create: `tests/test_transfer_model.py`
- Modify: `notebooks/colab_train_siamese.ipynb` — thêm cell gọi `scripts/train_config_b.py` sau cell Config A, thêm cell in `results/comparison_summary.md`.
- Modify: `configs/default.yaml` — thêm `model.transfer_backbone: "resnet18"`, `train.finetune_stage1_epochs: 5`, `train.lr_finetune_head: 0.0001`, `train.lr_finetune_backbone: 0.00001`.

## Implementation Steps

1. Viết `SiameseTransferCNN.__init__`: load backbone theo `model.transfer_backbone`, thay lớp cuối, expose thuộc tính `backbone_last_block` (tham chiếu `layer4` hoặc khối conv cuối VGG16) để `unfreeze_last_block()` dùng.
2. Viết `freeze_backbone()`/`unfreeze_last_block()`, viết `test_transfer_model.py` kiểm chứng ngay (trước khi viết vòng lặp train đầy đủ).
3. Viết `scripts/train_config_b.py::stage1()` gọi `train_one_config` (tái sử dụng từ Phase 5) với backbone đã đóng băng, số epoch giới hạn theo `train.finetune_stage1_epochs`.
4. Viết `scripts/train_config_b.py::stage2()` — mở khối cuối, tạo optimizer với 2 param groups (lr khác nhau), tiếp tục gọi `train_one_config` với early stopping theo `val_eer` cho tới khi hội tụ hoặc hết `max_epochs`.
5. Lặp toàn bộ (stage1+stage2) qua từng margin trong `train.margins`, chọn margin tốt nhất theo `val_eer` của stage2, đánh giá test.
6. Viết hàm sinh `results/comparison_summary.md` — đọc `results/baseline/metrics.json`, `results/config_a/metrics.json`, `results/config_b/metrics.json`, xuất bảng Markdown so sánh FAR/FRR/EER/Accuracy/AUC theo `skilled_forgery`/`random_forgery`, cờ đạt/không đạt so với chỉ tiêu đề xuất (EER ≤5% CEDAR skilled) và so với baseline.
7. Cập nhật `notebooks/colab_train_siamese.ipynb` thêm cell Config B + cell in bảng so sánh.
8. Chạy `pytest tests/test_transfer_model.py` (CPU, batch giả).
9. **[Thực hiện trên Colab/Kaggle]** chạy notebook đã cập nhật với CEDAR thật, tải kết quả về, cập nhật `results/comparison_summary.md` với số liệu thật.

## Todo List

- [x] `SiameseTransferCNN` load đúng backbone, thay lớp cuối, test CPU pass
- [x] `freeze_backbone`/`unfreeze_last_block` hoạt động đúng, có test đếm tham số
- [x] 2 giai đoạn fine-tune chạy nối tiếp, param groups lr khác nhau
- [x] Margin sweep + threshold freeze giống quy trình Phase 5
- [x] `comparison_summary.md` sinh tự động, có đủ Baseline/A/B

## Success Criteria

- `pytest tests/test_transfer_model.py` pass trên CPU.
- `results/config_b/metrics.json` đầy đủ, tách skilled/random forgery.
- `results/comparison_summary.md` tồn tại, so sánh rõ ràng 3 phương pháp, không che số liệu bất lợi.

## Risk Assessment

- **Rủi ro:** mở nhầm quá nhiều lớp backbone ở giai đoạn 2 (fine-tune toàn bộ thay vì chỉ khối cuối) gây overfit trên tập train nhỏ (40 signer). **Giảm thiểu:** `unfreeze_last_block()` chỉ mở đúng 1 khối cuối theo thiết kế, test đếm số tham số `requires_grad=True` để phát hiện sớm nếu code mở nhầm phạm vi.
- **Rủi ro:** thời gian GPU miễn phí trên Colab/Kaggle có hạn, chạy cả ResNet18 và VGG16 × 3 margin × 2 giai đoạn có thể vượt quota. **Giảm thiểu:** mặc định chỉ chạy ResNet18 đầy đủ; VGG16 là nhánh tuỳ chọn rõ ràng đánh dấu P3/stretch trong `plan.md`.

## Security Considerations

- Không có dữ liệu cá nhân người dùng cuối ở phase này.

## Next Steps

- Phase 7 chọn mô hình "chính" (Config A hoặc B, theo `val_eer`/`test_eer` thấp hơn) để chạy ablation và kiểm tra tổng quát trên BHSig260.
