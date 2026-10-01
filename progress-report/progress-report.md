# Báo cáo tiến độ

Sinh viên: Phan Thành Thuận — MSSV 170123591 — Lớp DX23TT11
Giảng viên hướng dẫn: ThS. Nguyễn Nhứt Lam

**Lưu ý về phương pháp thực hiện**: đồ án được triển khai bằng lập trình cặp
đôi hỗ trợ bởi AI (AI-assisted pair programming, dùng Claude Code) trong một
phiên làm việc tập trung thật (01/10/2026), không trải đều theo tuần. Lịch sử
commit dưới đây là dấu thời gian thật lấy trực tiếp từ `git log`, không chỉnh
sửa. Ghi nhận minh bạch điểm này để giảng viên hướng dẫn nắm đúng cách thức
thực hiện thực tế.

**Bối cảnh quan trọng**: đồ án này được xây dựng sau khi phát hiện một đề
cương chi tiết khác (về xác minh chữ ký viết tay, dự án
`Recognite-signature`) đã bị lạc đề so với đề tài thật được phân công —
"Huấn luyện và so sánh hiệu quả của mô hình học máy KNN và SVM trên tập dữ
liệu MNIST". Đồ án này được bắt đầu lại hoàn toàn mới, đúng đề tài thật, sau
khi xác nhận với giảng viên/sinh viên rằng đề cương chữ ký chỉ mới nộp, chưa
được duyệt.

## 01/10/2026 — Xây dựng đúng đề tài, từ huấn luyện thật đến báo cáo hoàn chỉnh

| Giờ (thật, theo git log) | Nội dung |
|---|---|
| 12:57 | Xây dựng pipeline đầy đủ: `src/digitrec/` (tải MNIST thật qua `fetch_openml`, chia stratify 54.000/6.000/10.000, khởi tạo KNN và SVM), `scripts/train.py` chạy huấn luyện thật và lưu kết quả thật vào `results/`, `app.py` demo Streamlit, 4 unit test ban đầu |
| 13:01 | Lập plan triển khai và journal ghi nhận bối cảnh phát hiện lạc đề |
| 13:16 | Cập nhật plan sau khi đẩy mã nguồn lên GitHub (nhánh `nhan-dang-chu-so-viet-tay`) |
| 13:26 | Phát hiện và sửa lỗi runtime ở demo: `streamlit-drawable-canvas` không tương thích với phiên bản Streamlit đang dùng (`StreamlitAPIException` lúc import) — phát hiện qua bước review bắt buộc chạy app thật chứ không chỉ kiểm tra cú pháp; thay bằng canvas tự viết dùng `st.components.v2` có sẵn, không phụ thuộc thư viện ngoài; thêm test hồi quy `test_app_runs_without_exceptions` dùng `streamlit.testing.v1.AppTest` |
| 13:27 | Journal ghi nhận bài học từ lỗi canvas (server sống ≠ script chạy đúng) |
| 13:35 | Lập plan hoàn thiện cấu trúc dự án và báo cáo đồ án chính thức (plan này), đối chiếu chi tiết với mức độ hoàn thiện tổ chức của dự án `Recognite-signature` |
| 13:36 | Journal cho việc lập plan hoàn thiện cấu trúc |
| 13:39 | Phase 2: tạo `setup/`, `progress-report/`, `thesis/{doc,pdf,html,abs,refs,docgen}/`, cập nhật README.md gốc theo cấu trúc mới |
| 13:53 | Phase 3: viết `thesis/docgen/build_thesis.py` — tái sử dụng hạ tầng sinh báo cáo (.docx) từ `Recognite-signature`, viết lại toàn bộ nội dung cho đúng đề tài KNN/SVM/MNIST; mọi số liệu đọc trực tiếp từ `results/comparison_summary.json` |
| 13:56 | Phase 4: hội tụ số trang mục lục bằng phương pháp hai lượt (đo thật bằng `pdftotext`, 0 lệch số trang), sửa lỗi hiển thị bảng bị cắt ở ranh giới trang, xem bằng mắt toàn bộ 39 trang |
| 13:59 | Phase 5: quay video demo thật bằng Playwright (vẽ số "1" bằng chuỗi sự kiện chuột thật + tải ảnh test MNIST thật, cả hai mô hình dự đoán đúng cả hai lần), gửi video cho người dùng |

Đến thời điểm viết báo cáo tiến độ này (Phase 6): toàn bộ 5 test tự động vẫn
pass, mô hình đã huấn luyện thật (KNN và SVM) cho kết quả thật trên tập test
MNIST, báo cáo đồ án chính thức (.docx/.pdf, 39 trang, đúng biểu mẫu trình
bày của Trường Đại học Trà Vinh) đã sinh và kiểm tra bằng mắt, video demo
thật đã có.

## Tổng kết trạng thái tại thời điểm báo cáo này

Xem bảng kết quả thật đầy đủ (độ chính xác, thời gian huấn luyện,
precision/recall/F1 từng chữ số) trong [`README.md`](../README.md) ở thư
mục gốc, hoặc Chương 4 của [`thesis/pdf/thesis.pdf`](../thesis/pdf/thesis.pdf).

Việc đã hoàn thành đầy đủ theo đúng yêu cầu đề tài: huấn luyện và so sánh
KNN với SVM trên MNIST thật (không mô phỏng), xây dựng ứng dụng demo hoạt
động được với dữ liệu thật để trình diễn, báo cáo đồ án đầy đủ. Hạn chế đã
ghi nhận minh bạch trong phần Kết luận của báo cáo: chưa tìm kiếm tham số
tối ưu có hệ thống (hyperparameter tuning) cho cả hai mô hình, và chưa so
sánh thêm với hướng tiếp cận học sâu (CNN) — cả hai nằm ngoài phạm vi bắt
buộc của đề tài (chỉ yêu cầu KNN và SVM).
