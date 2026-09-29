# Báo cáo tiến độ

Sinh viên: Phan Thành Thuận — MSSV 170123591 — Lớp DX23TT11
Giảng viên hướng dẫn: ThS. Nguyễn Nhứt Lam

**Lưu ý về phương pháp thực hiện**: đồ án được triển khai bằng lập trình cặp
đôi hỗ trợ bởi AI (AI-assisted pair programming, dùng Claude Code) trong hai
phiên làm việc tập trung thật (26/09/2026 và 27/09/2026), thay vì trải đều
theo nhịp 8 tuần như đề cương nêu ban đầu. Lịch sử commit dưới đây là dấu thời
gian thật lấy trực tiếp từ `git log`, không chỉnh sửa. Ghi nhận minh bạch điểm
này để giảng viên hướng dẫn nắm đúng cách thức thực hiện thực tế.

## 26/09/2026 — Xây dựng toàn bộ pipeline trên dữ liệu tổng hợp

| Giờ (thật, theo git log) | Nội dung |
|---|---|
| 13:37 | Lập đề cương triển khai chi tiết (`plans/`), chia 9 phase |
| 13:44 | Khởi tạo cấu trúc package `sigverify`, cấu hình `default.yaml` |
| 13:45 | Bộ đọc CEDAR + pipeline tiền xử lý ảnh 5 bước |
| 13:48 | Chia writer-disjoint, sinh cặp huấn luyện, khung đo FAR/FRR/EER/ROC |
| 13:50 | Baseline HOG/LBP + SVM (RBF) |
| 13:55 | Cấu hình A: Siamese CNN huấn luyện từ đầu + contrastive loss |
| 13:58 | Cấu hình B: Siamese transfer learning (ResNet18/VGG16), tinh chỉnh 2 giai đoạn |
| 14:03 | Ablation sweep + tổng quát hoá zero-shot BHSig260 |
| 14:07 | Trích xuất và render các ca lỗi phân loại sai nghiêm trọng nhất |
| 14:15 | Demo Streamlit + Dockerfile chạy CPU |
| 14:27 | Sửa loader cho đúng cấu trúc thư mục thật của CEDAR/BHSig260 trên Kaggle |
| 15:21–18:59 | Chạy huấn luyện THẬT trên CEDAR (baseline, Cấu hình A đủ 3 mức margin), chạy zero-shot BHSig260 thật, sửa lỗi reseed theo từng margin |

Đến cuối ngày 26/09: toàn bộ mã nguồn đã có 55 unit test chạy trên dữ liệu
tổng hợp trước khi chạm vào dữ liệu thật; Baseline và Cấu hình A đã có kết quả
thật đầy đủ trên CEDAR.

## 27/09/2026 — Hoàn thành Cấu hình B, viết báo cáo

| Giờ (thật) | Nội dung |
|---|---|
| 02:19–02:21 | Khôi phục kết quả Cấu hình B từ checkpoint sau sự cố container khởi động lại giữa chừng (mất margin=2,0, không phục hồi được); có kết quả thật Cấu hình B (2/3 margin), vượt Cấu hình A |
| 06:52–14:48 | Viết báo cáo đồ án đầy đủ (`thesis/docgen/build_thesis.py`, sinh `.docx`/`.pdf` bằng python-docx): theo cấu trúc đề cương đã duyệt, sau đó chỉnh theo đúng biểu mẫu trình bày chính thức của Trường Đại học Trà Vinh, và mở rộng nội dung lý thuyết/thực nghiệm lên khoảng 45 trang nội dung chính |

## Tổng kết trạng thái tại thời điểm báo cáo này

Xem bảng đối chiếu T1–T8 đầy đủ và số liệu kết quả thật trong
[`README.md`](../README.md) ở thư mục gốc, hoặc Chương 4 của
[`thesis/pdf/thesis.pdf`](../thesis/pdf/thesis.pdf).

Việc còn lại (đã ghi nhận trung thực, không che giấu): T4 (ảnh hưởng tiền xử
lý) chưa chạy do giới hạn thời gian trên CPU; T5 mới khảo sát margin, chưa
khảo sát augmentation on/off; T6 (triplet loss) và T8 (mẫu tự thu thập) là hai
thí nghiệm tùy chọn theo đề cương, chưa thực hiện; Cấu hình B thiếu kết quả
margin=2,0 do sự cố hạ tầng ngoài kiểm soát.
