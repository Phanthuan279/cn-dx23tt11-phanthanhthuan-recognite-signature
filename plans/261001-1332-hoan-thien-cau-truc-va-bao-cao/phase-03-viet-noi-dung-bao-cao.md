---
title: "Phase 3: Viết nội dung báo cáo"
status: done
---

# Phase 3: Viết nội dung báo cáo

## Overview

Viết `thesis/docgen/build_thesis.py` cho đề tài này: tái sử dụng các hàm hạ
tầng đã có từ `Recognite-signature/thesis/docgen/build_thesis.py` (helpers
`add_para`, `add_heading`, `add_image`, `add_table`, `add_formula`, cơ chế
đánh số trang La Mã (phần đầu)/Ả Rập (từ Chương 1), `class Counter`, hàm
`cover_page`, logo trường), nhưng viết lại **toàn bộ nội dung** đúng đề tài
Nhận dạng chữ số viết tay — không copy nội dung xác minh chữ ký.

## Requirements

- [x] Đúng biểu mẫu trình bày chính thức của Trường Đại học Trà Vinh (bìa, mục lục, nhận xét, đánh số trang) — tái sử dụng hạ tầng đã kiểm chứng
- [x] Nội dung 100% thật: số liệu từ `results/comparison_summary.json`, không mô phỏng, không độn trang
- [x] Độ dài tỉ lệ thuận với độ phức tạp thật của đề tài (nội dung chương 1-5 + kết luận + phụ lục + tài liệu tham khảo = 21 trang Ả Rập, trong khoảng ước tính 15-25 trang; tổng cộng 39 trang kể cả bìa/mục lục/nhận xét theo biểu mẫu, so với 67 trang của báo cáo chữ ký cũ)
- [x] Công thức toán học render đúng (KNN, SVM, các độ đo đánh giá)
- [x] Trích dẫn tài liệu tham khảo thật, có thể kiểm chứng (không bịa)

## Implementation Steps

1. Sao chép các hàm hạ tầng dùng chung (helpers, Counter, page-numbering OXML, `cover_page`) từ `Recognite-signature/thesis/docgen/build_thesis.py` sang `digit-recognition/thesis/docgen/build_thesis.py`, đổi các hằng số định danh: `THESIS_TITLE`, `PROJECT_TYPE`, giữ nguyên `UNIVERSITY`, `SCHOOL`, `FACULTY`, `STUDENT_*`, `ADVISOR` (cùng sinh viên, cùng lớp, cùng GVHD).
2. Copy logo trường (`thesis/abs/logo_truong_dai_hoc_tra_vinh.png`) từ dự án cũ sang (cùng một logo thật, không cần tải lại).
3. Soạn công thức cần thiết (dùng matplotlib mathtext, theo đúng cách đã làm ở dự án cũ, lưu vào `thesis/abs/formulas/`):
   - Khoảng cách Euclid cho KNN: $d(x, x_i) = \sqrt{\sum_k (x_k - x_{i,k})^2}$
   - Quy tắc quyết định KNN (bỏ phiếu đa số trong k láng giềng gần nhất)
   - Bài toán tối ưu SVM (lề cực đại, kernel RBF): $K(x, x') = \exp(-\gamma \|x-x'\|^2)$
   - Accuracy, Precision, Recall, F1-score
4. Chụp ảnh màn hình demo thật (`thesis/abs/screenshots/`) để minh họa Chương 5 — chụp từ ứng dụng Streamlit đang chạy thật (không dựng cảnh giả).
5. Viết nội dung từng chương (tham khảo cấu trúc chương của dự án cũ nhưng nội dung hoàn toàn mới):
   - **Chương 1 — Tổng quan**: đặt vấn đề (nhận dạng chữ số viết tay trong thực tế: xử lý biểu mẫu, bưu chính, ngân hàng), mục tiêu, đối tượng và phạm vi (MNIST, KNN, SVM), cấu trúc báo cáo.
   - **Chương 2 — Cơ sở lý thuyết**: bài toán phân loại đa lớp; thuật toán KNN (khoảng cách, k, bỏ phiếu); SVM (siêu phẳng phân cách, lề cực đại, kernel RBF); các độ đo đánh giá (accuracy, precision/recall/F1, ma trận nhầm lẫn); giới thiệu bộ dữ liệu MNIST.
   - **Chương 3 — Phương pháp thực hiện**: quy trình tổng thể (tải dữ liệu → tiền xử lý → chia tập → huấn luyện → đánh giá); chia tập 54.000/6.000/10.000 (stratify); cấu hình KNN (k=5) và SVM (kernel RBF, C=5); công cụ và môi trường (Python, scikit-learn, Streamlit).
   - **Chương 4 — Thực nghiệm và đánh giá**: kết quả thật (bảng so sánh KNN/SVM: accuracy, thời gian huấn luyện), ma trận nhầm lẫn từng mô hình (chèn ảnh thật từ `results/`), phân tích lỗi (chữ số nào hay bị nhầm, ví dụ: 4↔9, 3↔5 là các cặp kinh điển — đối chiếu với ma trận nhầm lẫn thật xem có đúng không trước khi viết, không suy đoán).
   - **Chương 5 — Chương trình demo**: kiến trúc demo (Streamlit, canvas vẽ tay tự viết bằng `st.components.v2`, luồng xử lý ảnh đầu vào), ảnh chụp màn hình thật.
   - **Kết luận và hướng phát triển**: kết quả đạt được, hạn chế (SVM chậm hơn KNN khi huấn luyện; cả hai đều là mô hình cổ điển, chưa thử CNN), hướng phát triển (thử mạng nơ-ron tích chập, tăng cường dữ liệu).
   - **Phụ lục**: cấu trúc mã nguồn, danh sách siêu tham số đầy đủ.
   - **Tài liệu tham khảo**: Cover & Hart (1967) cho KNN, Cortes & Vapnik (1995) cho SVM, LeCun et al. cho MNIST, tài liệu scikit-learn chính thức — chỉ trích dẫn tài liệu thật, kiểm chứng được, không bịa tên tác giả/năm.

## Todo

- [x] Copy hạ tầng dùng chung từ build_thesis.py cũ, đổi hằng số đề tài
- [x] Copy logo trường
- [x] Soạn công thức KNN/SVM/độ đo đánh giá
- [x] Chụp ảnh màn hình demo thật
- [x] Viết đủ nội dung 5 chương + kết luận + phụ lục + tài liệu tham khảo
- [x] Đối chiếu từng số liệu/khẳng định với `results/comparison_summary.json` và ma trận nhầm lẫn thật trước khi viết — không suy đoán

## Success Criteria

Đã rà soát: `thesis/docgen/build_thesis.py` đọc trực tiếp
`results/comparison_summary.json` (biến `RESULTS`, `KNN`, `SVM`) và nội suy
mọi số liệu trong báo cáo từ đó (accuracy, thời gian huấn luyện,
precision/recall/F1 macro, recall từng chữ số) — không có số nào gõ tay.
Script chạy sinh `.docx` không lỗi (`python3 thesis/docgen/build_thesis.py`
→ "Saved thesis.docx"), chuyển sang `.pdf` bằng LibreOffice thành công (39
trang). Đã render toàn bộ 39 trang thành ảnh và xem trực tiếp bằng mắt:
bìa đúng biểu mẫu (logo thật, khối Giảng viên/Sinh viên căn trái đúng như
đã sửa trước đó), đánh số trang La Mã ở phần đầu và Ả Rập bắt đầu lại từ 1
tại Chương 1 đều đúng, công thức Euclidean/KNN vote/SVM hyperplane/margin/
RBF kernel/decision function/Accuracy/Precision/Recall/F1 đều render rõ
ràng bằng matplotlib mathtext, hai ảnh ma trận nhầm lẫn chèn vào đúng là
ảnh thật từ `results/confusion_matrix_{knn,svm}.png`, hai ảnh chụp màn
hình demo ở Chương 5 là ảnh chụp thật (Playwright, server Streamlit thật
đang chạy, tải lên một ảnh chữ số "7" thật lấy từ tập test MNIST, cả hai
mô hình dự đoán đúng) — không dàn dựng. Phát hiện một lỗi hiển thị trong
lần render đầu (một hàng cuối của Bảng 4.2 bị cắt ngang ở ranh giới trang,
để lại một khung bảng trống nhìn như lỗi) và đã sửa ngay bằng cách thêm
`w:cantSplit` cho mọi hàng trong `add_table()`, sau đó render lại và xác
nhận hàng đó nay hiển thị đầy đủ nội dung ở đầu trang kế tiếp — không còn
lỗi hiển thị nào khác sau khi rà soát lại toàn bộ 39 trang. Phân tích lỗi
ở mục 4.5 (cặp số dễ nhầm 4↔9, 8↔3, 8↔5, 2↔7) đối chiếu đúng với số liệu
thật trong hai ảnh ma trận nhầm lẫn trước khi viết, không suy đoán. 12 tài
liệu tham khảo đều là nguồn thật, có thể kiểm chứng (LeCun, Cover & Hart,
Cortes & Vapnik, Scholkopf & Smola, Pedregosa et al., tài liệu chính thức
scikit-learn/NumPy/Matplotlib/Streamlit, và chính brief đề tài được phân
công). Việc đo trang chính xác cho Mục lục (hiện dùng số trang ước tính)
để lại cho Phase 4 theo đúng kế hoạch hai-lượt đã định.
