# Phân tích lỗi định tính

Dựa trên `results/config_a/predictions_test.csv` (CEDAR test, mô hình Config A
huấn luyện **đầy đủ 3 margin** {0.5, 1.0, 2.0} với `patience=10`,
`max_epochs=100` — mỗi margin tự dừng sớm ở epoch 14–21; margin thắng=1.0,
val EER=9.75% — xem `results/config_a/metrics.json` và
`results/config_a/margin_sweep.json`) và
`results/config_a/predictions_bhsig260.csv` (BHSig260 zero-shot — xem
`results/generalization_bhsig260.md`). Ảnh minh hoạ trong
`results/error_analysis/{cedar_test,bhsig260}/`.

**Lưu ý phương pháp luận:** ở lần chạy full-sweep này, seed chỉ được gieo một
lần ở đầu script, không gieo lại cho từng margin — nên margin 1.0 và 2.0 kế
thừa trạng thái ngẫu nhiên (augmentation, một phần thứ tự khởi tạo) còn lại từ
margin trước, khiến so sánh giữa 3 margin không hoàn toàn kiểm soát được. Đã
sửa trong `scripts/train_config_a.py`/`train_config_b.py` (gieo lại seed
trước mỗi margin) cho các lần chạy sau; số liệu ở đây vẫn là kết quả thật hợp
lệ, chỉ nên đọc so sánh giữa các margin với mức thận trọng vừa phải.

## CEDAR test (cùng miền dữ liệu huấn luyện)

**Random forgery — chấp nhận nhầm (false accept), ví dụ
`random_forgery_false_accept_006.png` và `..._007.png`:** cả hai ví dụ đều là
cặp chữ ký của hai người hoàn toàn khác nhau (nội dung tên khác nhau: "Melissa
N. Dumble" vs "Rrand R. Co") nhưng có D rất nhỏ, thấp hơn nhiều so với
τ=0.247. Cả hai chữ ký trong mỗi cặp đều có nét gạch ngang/uốn lượn kéo dài
đặc trưng phía trên chữ và độ nghiêng cursive tương tự. Cách đọc hợp lý nhất:
mô hình học mạnh các đặc trưng hình dạng tổng thể (độ nghiêng, mật độ nét, tỉ
lệ khung) hơn là chi tiết nhận dạng nét chữ riêng của từng người — hai người
có "gestalt" chữ ký tương tự bị nhầm là cùng một người. Với margin thắng cuộc
là 1.0, random forgery vẫn là điểm yếu rõ rệt nhất: FAR=39,5% trên test set.

**Genuine-genuine — từ chối nhầm (false reject), ví dụ
`genuine_genuine_false_reject_000.png`:** hai chữ ký của cùng một người nhưng
D cao hơn τ. Hai ảnh khác biệt rõ về hình dạng tổng thể (một chụm tròn hơn,
một dàn trải nghiêng hơn) — đây là biến thiên tự nhiên trong cách ký của
chính người đó giữa các lần ký khác nhau, mà mô hình (dừng sớm ở epoch 18)
chưa học đủ để dung nạp.

**Skilled forgery — chấp nhận nhầm, ví dụ
`skilled_forgery_false_accept_012.png`:** một cặp chữ ký giả kỹ năng cao với
D=0.1938, sát dưới τ=0.2471. Cả hai đều có nét nghiêng chéo và các vòng loop
lặp lại theo cùng một hướng — hoạ tiết hình học tổng thể giống nhau đủ để
"đánh lừa" mô hình dù đây là bản giả.

**Điểm đáng chú ý:** skilled forgery vẫn được phân tách gần như hoàn hảo trên
CEDAR test (AUC=0.997, FAR chỉ 1%) trong khi random forgery khó hơn hẳn
(AUC=0.834, FAR 39,5%). Đây là kết quả ngược với trực giác thông thường
(thường skilled forgery khó phân biệt hơn), phù hợp với cách đọc ở trên: các
cặp forged CEDAR có nét bút "cứng"/thiếu tự nhiên rất đặc trưng dễ phân biệt
với nét bút thật ở mức thô, trong khi hai người viết thật với gestalt tương tự
nhau lại dễ gây nhầm hơn — và mẫu này vẫn nhất quán qua cả lần chạy rút gọn
lẫn lần chạy full-sweep, nên đáng tin hơn là ngẫu nhiên.

## BHSig260 (zero-shot, khác miền dữ liệu — Bengali/Hindi)

**Genuine-genuine — từ chối nhầm nghiêm trọng, ví dụ
`genuine_genuine_false_reject_000.png` (BHSig260):** hai chữ ký "sandeep"
(chữ Devanagari) của cùng một người, nhìn ảnh gốc khá giống nhau, nhưng
D=2.6044 — cao gấp hơn 10 lần τ=0.243 lấy từ CEDAR. Quan sát ảnh "Đã xử lý":
ảnh A hiện ra đậm/dày nét hẳn so với ảnh B mảnh/nhạt, dù ảnh gốc trông tương
đồng về độ đậm. Đây là dấu hiệu **lệch miền (domain shift) ở khâu tiền xử
lý**: tham số khử nhiễu/ngưỡng Otsu được ngầm phù hợp với đặc điểm ảnh scan
CEDAR (độ phân giải, độ tương phản riêng), không chuyển đổi tốt sang ảnh
BHSig260 (định dạng .tif, độ phân giải/độ tương phản khác) — làm hai ảnh vốn
giống nhau trở nên khác biệt rõ rệt sau tiền xử lý, đẩy embedding ra xa nhau.
Đây là nguyên nhân chính khả dĩ cho FRR rất cao (53,2%) khi test zero-shot
trên BHSig260, dùng ngưỡng đóng băng từ CEDAR.

**Skilled forgery — chấp nhận nhầm, ví dụ
`skilled_forgery_false_accept_008.png`:** cặp chữ ký Bengali với D=0.0233, rất
gần 0. Cả hai đều là các đường cong lặp lại (loop) dày đặc, phong cách viết
script rất giống nhau về mặt hình học tổng thể — củng cố thêm giả thuyết ở
trên: mô hình nhạy với hình dạng/mật độ nét thô hơn là danh tính chi tiết,
càng rõ hơn khi chuyển miền dữ liệu (chữ Devanagari/Bengali có mật độ nét và
kiểu loop rất khác chữ Latin của CEDAR).

## Hàm ý cho các bước tiếp theo

1. **Chuẩn hoá tiền xử lý bất biến hơn với độ phân giải nguồn** (ví dụ: chuẩn
   hoá độ tương phản thích ứng thay vì kernel khử nhiễu cố định) có thể giảm
   phần domain-shift quan sát được ở BHSig260.
2. **Không thể tái hiệu chỉnh ngưỡng τ theo BHSig260** làm số liệu chính (vi
   phạm tính "writer-independent"/zero-shot) — nhưng chạy thêm huấn luyện đầy
   đủ (100 epoch, 3 margin, trên GPU) nhiều khả năng thu hẹp khoảng cách vì
   mô hình rút gọn ở đây mới học 12-15 epoch.
3. Kết quả CEDAR test AUC=0.939 > baseline AUC=0.887 dù chỉ huấn luyện rút
   gọn — có cơ sở tốt để kỳ vọng huấn luyện đầy đủ trên GPU sẽ đạt hoặc vượt
   chỉ tiêu EER≤5% (skilled forgery CEDAR) đề ra trong `plan.md`.
