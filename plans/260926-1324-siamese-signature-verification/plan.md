---
title: "Xác minh chữ ký viết tay offline bằng mạng Siamese (Writer-Independent)"
description: "Hệ thống xác minh chữ ký viết tay offline (verification, không phải identification) dùng mạng Siamese writer-independent, huấn luyện/đánh giá trên CEDAR với kiểm tra tổng quát chéo trên BHSig260, kèm baseline HOG/LBP+SVM và demo Streamlit — đồ án tốt nghiệp."
status: pending
priority: P1
effort: "16.5d"
branch: claude/dreamy-carson-nkwqfa
tags: [ml, computer-vision, pytorch, signature-verification, siamese-network, thesis]
blockedBy: []
blocks: []
created: 2026-09-26
---

# Xác minh chữ ký viết tay offline bằng mạng Siamese (Writer-Independent)

## Overview

Xây dựng một hệ thống xác minh chữ ký viết tay offline: nhận 2 ảnh chữ ký (1 ảnh mẫu đã biết là thật, 1 ảnh cần kiểm tra), trả về "thật"/"giả" kèm khoảng cách D, theo hướng **writer-independent** — một mô hình dùng chung cho mọi người, không huấn luyện lại khi có người dùng mới. Bài toán là **verification** (không phải identification). Dữ liệu chính là **CEDAR** (55 người ký, 24 thật + 24 giả kỹ năng cao/người); dữ liệu phụ để kiểm tra tổng quát là **BHSig260** (đã chốt qua bước làm rõ với người dùng, xem `## Validation Log`). Kết quả phải báo cáo tách riêng **random forgery** (chữ ký thật của người khác) và **skilled forgery** (giả kỹ năng cao cùng người), bằng đủ 4 độ đo bắt buộc: FAR, FRR, EER, Accuracy, ROC/AUC. Sản phẩm bàn giao bắt buộc gồm: baseline HOG/LBP+SVM, 2 cấu hình Siamese (CNN từ đầu / transfer learning ResNet18-VGG16), thí nghiệm ablation + tổng quát chéo, phân tích lỗi, và một ứng dụng demo Streamlit chạy được thật, không lưu ảnh người dùng.

## Goals

| # | Goal | Priority |
|---|------|----------|
| 1 | Pipeline tiền xử lý ảnh 5 bước (grayscale → khử nhiễu → Otsu → crop bbox → resize/pad → chuẩn hoá) dùng chung cho mọi mô hình và demo | P1 |
| 2 | Chia tập writer-disjoint (40/5/10) + sinh 3 loại cặp (dương/âm-khó/âm-dễ) + khung đo FAR/FRR/EER/ROC-AUC tách theo random/skilled forgery, chống rò rỉ ngưỡng | P1 |
| 3 | Baseline HOG hoặc LBP + SVM (RBF) trên vector chênh lệch tuyệt đối, làm mốc so sánh bắt buộc | P1 |
| 4 | Siamese Cấu hình A: CNN 4-5 khối Conv+BN+ReLU+MaxPool huấn luyện từ đầu, contrastive loss, sweep margin {0.5, 1.0, 2.0} | P1 |
| 5 | Siamese Cấu hình B: transfer learning ResNet18 (VGG16 tuỳ chọn), fine-tune 2 giai đoạn, so sánh với Cấu hình A và baseline | P1 |
| 6 | Ablation (tiền xử lý/augmentation/chuẩn hoá embedding) + kiểm tra tổng quát zero-shot trên BHSig260, tách random/skilled forgery | P2 |
| 7 | Phân tích lỗi định tính trên các cặp bị nhận sai (CEDAR test + BHSig260) | P2 |
| 8 | Demo Streamlit: upload 2 ảnh, hiển thị gốc+đã xử lý, kết quả thật/giả + D, thanh trượt τ ảnh hưởng FAR/FRR, xử lý hoàn toàn trong bộ nhớ | P1 |

## Chỉ tiêu đánh giá (đề xuất, ghi nhận đạt/không đạt trung thực — không phải điều kiện chặn tiến độ)

- EER ≤ 5% trên CEDAR (giả mạo chuyên nghiệp/skilled forgery).
- EER ≤ 20% trên BHSig260 (zero-shot, giả mạo chuyên nghiệp).
- EER của Siamese (Cấu hình A và/hoặc B) phải thấp hơn baseline HOG/LBP+SVM, trên cả CEDAR và BHSig260.

## Phases

| # | Phase | Status |
|---|-------|--------|
| 1 | [Khởi tạo cấu trúc dự án & môi trường](./phase-01-start.md) | Pending |
| 2 | [Tải/khảo sát CEDAR & pipeline tiền xử lý ảnh](./phase-02-data-acquisition-preprocessing.md) | Pending |
| 3 | [Sinh cặp huấn luyện, chia tập theo người ký & khung đo FAR/FRR/EER/ROC](./phase-03-pairs-split-metrics-framework.md) | Pending |
| 4 | [Baseline HOG/LBP + SVM](./phase-04-baseline-hog-lbp-svm.md) | Pending |
| 5 | [Mạng Siamese Cấu hình A (CNN huấn luyện từ đầu)](./phase-05-siamese-configa-scratch-cnn.md) | Pending |
| 6 | [Mạng Siamese Cấu hình B (Transfer Learning ResNet18/VGG16)](./phase-06-siamese-configb-transfer-learning.md) | Pending |
| 7 | [Ablation & tổng quát chéo trên BHSig260](./phase-07-ablations-cross-dataset-generalization.md) | Pending |
| 8 | [Phân tích lỗi](./phase-08-error-analysis.md) | Pending |
| 9 | [Chương trình demo Streamlit & đóng gói](./phase-09-demo-app-packaging.md) | Pending |

Phases tuân theo đúng thứ tự tuần tự người dùng yêu cầu ("đừng nhảy cóc"): 1→2→3→4→5→6→7→8→9. Phụ thuộc kỹ thuật thật sự của Phase 9 chỉ là Phase 5 (có một mô hình đã train) — ghi rõ trong `phase-09` để người thực hiện biết có thể triển khai demo sớm hơn về mặt kỹ thuật nếu cần, nhưng thứ tự thực hiện mặc định vẫn giữ tuần tự theo yêu cầu.

## Kiến trúc mô hình (tóm tắt — chi tiết đầy đủ trong từng phase)

```
Ảnh chữ ký 1 ──┐                                    ┌── Ảnh chữ ký 2
               ▼                                    ▼
     preprocess_image() [chung, Phase 2]  preprocess_image() [chung, Phase 2]
               │                                    │
               ▼                                    ▼
        CNN chia sẻ trọng số (Siamese)      CNN chia sẻ trọng số (Siamese)
        [Cấu hình A: scratch CNN            [cùng 1 instance model —
         hoặc Cấu hình B: ResNet18/VGG16]    gọi 2 lần trên 2 ảnh]
               │                                    │
               ▼                                    ▼
          embedding f(x1) 128-d             embedding f(x2) 128-d
               └──────────────┬─────────────────────┘
                               ▼
                    D = ||f(x1) - f(x2)||_2
                               │
                               ▼
                    So sánh D với ngưỡng τ (đóng băng từ validation)
                               │
                     D < τ ──► "Thật"      D ≥ τ ──► "Giả"
```

## Dependencies

- Không có plan khác trong hệ thống mà plan này phụ thuộc hoặc bị phụ thuộc (dự án greenfield, repo `Recognite-signature` trống trước plan này).
- Phụ thuộc bên ngoài chưa xác minh được tại thời điểm lập kế hoạch (đánh dấu `[UNVERIFIED]` trong các phase liên quan): nguồn tải CEDAR và BHSig260 (mirror Kaggle cụ thể), GPU miễn phí Colab/Kaggle còn khả dụng trong thời gian thực hiện.

## Validation Log

### Phiên làm rõ với người dùng — 2026-09-26

**Câu hỏi:** Bộ dữ liệu phụ (kiểm tra khả năng tổng quát ngoài CEDAR) nên dùng BHSig260 hay GPDS Synthetic? (Người dùng chủ động yêu cầu được hỏi về quyết định này.)

**Trả lời:** BHSig260.

**Tác động lên plan:** Phase 7 dùng BHSig260 làm bộ dữ liệu tổng quát chéo bắt buộc; mọi tham chiếu "bộ dữ liệu thứ hai"/"bộ dữ liệu phụ" trong các phase đã được viết thống nhất là BHSig260 (không còn nhắc GPDS Synthetic ở bất kỳ đâu trong plan này).

### Các quyết định phương pháp luận tự chốt trong khi soạn plan (ghi nhận công khai, không phỏng vấn thêm vì đều là lựa chọn kỹ thuật tiêu chuẩn có căn cứ rõ ràng, nằm trong phạm vi/khoảng giá trị người dùng đã tự cho phép)

| Quyết định | Lựa chọn | Căn cứ |
|---|---|---|
| Ảnh input cuối cho mô hình là gì | Grayscale đã crop theo bbox (Otsu chỉ dùng để định vị bbox) | Nhị phân hoá làm mất thông tin độ đậm nét bút — đặc trưng phân biệt forgery có giá trị. `binarize_output` vẫn cấu hình được, thử lại ở Phase 7 ablation. |
| L2-normalize embedding | Tắt mặc định | Nếu bật, khoảng cách Euclid tối đa = 2, khiến margin=2.0 (một trong 3 giá trị người dùng yêu cầu thử) mất ý nghĩa. Bật làm biến thể ablation ở Phase 7. |
| Chọn ngưỡng τ: theo EER hay Accuracy cao nhất | EER làm mặc định chính, Accuracy cao nhất tính thêm để tham khảo | Người dùng cho phép cả 2 ("tại EER hoặc Accuracy cao nhất"); EER là chuẩn phổ biến hơn trong nghiên cứu sinh trắc học nên chọn làm số liệu chính. |
| Tỉ lệ âm-khó : âm-dễ trong nửa "âm" của batch | 1:1 (tổng thể dương:âm-khó:âm-dễ ≈ 2:1:1) | Người dùng chỉ định dương:âm ≈1:1, không chỉ định tỉ lệ nội bộ 2 loại âm — chọn 1:1 làm mặc định hợp lý, tham số hoá để ablate. |
| Streamlit hay Gradio | Streamlit | Người dùng cho phép cả 2; Streamlit có bố cục cột (`st.columns`) thuận tiện hơn cho yêu cầu hiển thị ảnh gốc/đã xử lý cạnh nhau. `app/inference.py` tách biệt logic khỏi UI để đổi sang Gradio không tốn công nếu cần. |
| Backbone transfer learning mặc định | ResNet18 | Người dùng cho phép ResNet18 hoặc VGG16; ResNet18 nhẹ hơn, phù hợp ngân sách GPU miễn phí có hạn của Colab/Kaggle. VGG16 giữ làm nhánh tuỳ chọn cấu hình được. |

### Câu hỏi còn để ngỏ (không chặn việc bắt đầu thực hiện Phase 1)

- Slug/nguồn tải chính xác cho CEDAR và BHSig260 trên Kaggle (hoặc nguồn khác) chưa được xác minh trong phiên lập kế hoạch này — cần xác nhận khi thực thi Phase 2/7 (đã thiết kế script tải có fallback thủ công để không chặn tiến độ).
- Có dùng VGG16 làm phương án so sánh thứ hai ở Phase 6 hay chỉ dừng ở ResNet18, tuỳ vào thời gian/ngân sách GPU thực tế còn lại khi đến Phase 6 — quyết định khi đó, không cần chốt trước.

## Red Team Review (tự đánh giá đối kháng khi soạn plan)

Dự án là greenfield (không có code cũ để đối chiếu bằng chứng `file:line`), nên vòng đối kháng ở đây được thực hiện trực tiếp bởi người soạn plan theo 4 góc nhìn tiêu chuẩn, tập trung vào rủi ro phương pháp luận thay vì rủi ro mã nguồn hiện có:

- **Giả định (Assumption Destroyer):** giả định lớn nhất là CEDAR/BHSig260 tải được trong thời gian thực hiện. Đã giảm thiểu bằng thiết kế script tải 2 đường (tự động + fallback thủ công) và mọi test đơn vị chạy được trên dữ liệu tổng hợp, không chặn cứng vào việc có dữ liệu thật.
- **Thất bại (Failure Mode Analyst):** rủi ro rò rỉ dữ liệu (writer trùng giữa các tập, ngưỡng τ chọn trên test) là nguy cơ lớn nhất làm sai toàn bộ kết quả một cách âm thầm — đã chặn bằng thiết kế chữ ký hàm tách biệt (`select_threshold` chỉ nhận val, `evaluate_at_threshold` không nhận val) và test tự động ở Phase 3, không chỉ dựa vào quy ước tài liệu.
- **Phạm vi (Scope & Complexity Critic):** 9 phase cho một đồ án tốt nghiệp có 8 mốc công việc người dùng liệt kê + 1 phase setup là hợp lý, không phình to; đã cân nhắc gộp Phase 7/8 nhưng giữ tách vì mục tiêu khác nhau rõ rệt (ablation định lượng vs phân tích lỗi định tính) và cả hai đều được người dùng liệt kê là bước riêng.
- **Bảo mật (Security Adversary):** rủi ro riêng tư duy nhất thực sự tồn tại là ảnh chữ ký người dùng upload ở demo (Phase 9) — đã thiết kế ràng buộc "không ghi đĩa" là yêu cầu kiến trúc từ đầu (tham số hàm chỉ nhận bytes trong bộ nhớ), không phải việc thêm sau; không có surface tấn công nào khác đáng kể vì đây là app demo cục bộ, không có xác thực/API công khai trong phạm vi yêu cầu.

**Không phát hiện mâu thuẫn chưa giải quyết giữa các phase** (thuật ngữ, quy ước nhãn `label=1/0`, quy ước chiều `score`=khoảng cách, tên file `far_frr_curve.json`/`predictions_*.csv` được dùng nhất quán xuyên suốt Phase 3→9).

## Success Criteria

- [ ] `pip install -e .` + toàn bộ test đơn vị của Phase 1-9 pass trên CPU với dữ liệu tổng hợp (không cần CEDAR/BHSig260/GPU thật để CI/local pass).
- [ ] CEDAR được tải, tiền xử lý, chia writer-disjoint 40/5/10, sinh cặp đúng 3 loại theo tỉ lệ cấu hình.
- [ ] Baseline HOG/LBP+SVM có kết quả FAR/FRR/EER/Accuracy/AUC tách skilled/random forgery, lưu ở `results/baseline/`.
- [ ] Siamese Cấu hình A và B huấn luyện xong trên Colab/Kaggle, kết quả so sánh với baseline ghi rõ đạt/không đạt chỉ tiêu đề xuất, không che số liệu bất lợi.
- [ ] Ablation (4 biến thể) + tổng quát zero-shot trên BHSig260 hoàn tất, kết quả ghi ở `results/ablations/` và `results/generalization_bhsig260.md`.
- [ ] Phân tích lỗi có ảnh minh hoạ + diễn giải định tính ở `results/error_analysis/findings.md`.
- [ ] Demo Streamlit chạy được thật, đủ 5 yêu cầu UI, xác nhận bằng review code không có lệnh ghi file nào trên ảnh người dùng upload.

## Next Steps

- Xem mục "Post-Implementation Handoff" bên dưới để biết lệnh chạy tiếp theo.
