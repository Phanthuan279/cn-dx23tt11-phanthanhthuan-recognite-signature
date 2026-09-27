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

## Config B (transfer learning ResNet18) — so sánh với Config A

Huấn luyện đầy đủ trên GPU không khả dụng trong môi trường này; đã hoàn thành
thật 2/3 margin ({0.5: val_eer=14,3%}, {1.0: val_eer=5,5%}) trước khi container
bị khởi động lại giữa chừng margin=2.0 (mất, không phục hồi được — xem
`scripts/finalize_config_b_from_checkpoint.py`). Margin=1.0 được chọn làm kết
quả cuối cùng.

**Config B vượt Config A rõ rệt, đặc biệt ở đúng điểm yếu của Config A:**

| | Config A (margin=1.0) | Config B (margin=1.0) |
|---|---|---|
| AUC tổng thể | 0,915 | **0,955** |
| FAR random forgery | 39,5% | **13,0%** |
| AUC random forgery | 0,834 | 0,927 |
| FAR skilled forgery | 1,0% | 2,5% |
| AUC skilled forgery | 0,997 | 0,984 |
| Val EER | 9,75% | **5,50%** (rất sát mục tiêu 5%) |

Ví dụ `random_forgery_false_accept_004.png` (Config B) vẫn cho thấy đúng mẫu
lỗi đã quan sát ở Config A — hai người khác nhau ("Glorimar Vicente" vs
"Melissa N. Dumble") với nét nghiêng cursive tương tự bị nhầm — nhưng D=0,3247
gần τ=0,4763 hơn (tỉ lệ D/τ ≈ 0,68) so với các ca tương ứng ở Config A (tỉ lệ
D/τ ≈ 0,05–0,08, tức gần như bằng 0). Nói cách khác, Config B vẫn mắc cùng
loại lỗi nhưng "tự tin sai" ít hơn nhiều — đặc trưng pretrained ImageNet của
ResNet18 tổng quát hoá tốt hơn CNN train-from-scratch trên tập chỉ 40 người
ký, dù cả hai vẫn chia sẻ cùng một xu hướng học hình dạng thô trước chi tiết
danh tính.

## BHSig260 (zero-shot, khác miền dữ liệu — Bengali/Hindi)

Kết quả zero-shot (mô hình Config A full-sweep, τ đóng băng từ CEDAR — xem
`results/generalization_bhsig260.md`): skilled forgery FAR=19,8%/FRR=44,3%/
AUC=0,752; random forgery FAR=9,7%/FRR=44,3%/AUC=0,852. Chưa đạt mục tiêu
EER≤20%, nhưng AUC vẫn >0,75 cho thấy embedding còn giữ được tín hiệu phân
biệt nhất định dù khác ngôn ngữ/hệ chữ hoàn toàn.

**Genuine-genuine — từ chối nhầm nghiêm trọng, ví dụ
`genuine_genuine_false_reject_000.png` (BHSig260):** hai chữ ký "sandeep"
(chữ Devanagari) của cùng một người, nhìn ảnh gốc khá giống nhau, nhưng
D=1.9224 — cao gấp gần 8 lần τ=0.2471 lấy từ CEDAR. Quan sát ảnh "Đã xử lý":
ảnh A hiện ra đậm/dày nét hẳn so với ảnh B mảnh/nhạt, dù ảnh gốc trông tương
đồng về độ đậm. Đây là dấu hiệu **lệch miền (domain shift) ở khâu tiền xử
lý**: tham số khử nhiễu/ngưỡng Otsu được ngầm phù hợp với đặc điểm ảnh scan
CEDAR (độ phân giải, độ tương phản riêng), không chuyển đổi tốt sang ảnh
BHSig260 (định dạng .tif, độ phân giải/độ tương phản khác) — làm hai ảnh vốn
giống nhau trở nên khác biệt rõ rệt sau tiền xử lý, đẩy embedding ra xa nhau.
Ca này xuất hiện ở cả hai lần chạy (model rút gọn lẫn model full-sweep), nên
đây là nguyên nhân chính khả dĩ, nhất quán, cho FRR rất cao (44,3%) khi test
zero-shot trên BHSig260.

**Skilled forgery — chấp nhận nhầm, ví dụ
`skilled_forgery_false_accept_008.png`:** cặp chữ ký Hindi "ravindra kaur"
(thật vs giả) với D=0.0176, rất gần 0 — nội dung chữ và phong cách nét gần
như giống hệt nhau bằng mắt thường. Củng cố thêm giả thuyết ở trên: mô hình
nhạy với hình dạng/mật độ nét thô hơn là danh tính chi tiết, càng rõ hơn khi
chuyển miền dữ liệu (chữ Devanagari có mật độ nét và kiểu nối chữ rất khác
chữ Latin của CEDAR).

## Hàm ý cho các bước tiếp theo

1. **Config B (transfer learning) là lựa chọn nên ưu tiên** cho bản cuối của
   đồ án: val EER 5,5% đã rất sát chỉ tiêu 5%, và cải thiện mạnh nhất đúng vào
   điểm yếu của Config A (random forgery). Hoàn thành nốt margin=2.0 (và lý
   tưởng là chạy lại cả 3 margin với seed sạch mỗi margin, trên GPU) nhiều khả
   năng đạt hoặc vượt chỉ tiêu EER≤5%.
2. **Chuẩn hoá tiền xử lý bất biến hơn với độ phân giải nguồn** (ví dụ: chuẩn
   hoá độ tương phản thích ứng thay vì kernel khử nhiễu cố định) có thể giảm
   phần domain-shift quan sát được ở BHSig260.
3. **Không thể tái hiệu chỉnh ngưỡng τ theo BHSig260** làm số liệu chính (vi
   phạm tính "writer-independent"/zero-shot) — nên đo lại BHSig260 zero-shot
   với Config B (chưa thực hiện trong lần chạy này) để xem cải thiện tương tự
   CEDAR có chuyển sang miền dữ liệu khác hay không.
4. Cả Config A và Config B đều chia sẻ cùng một xu hướng lỗi định tính (học
   hình dạng/độ nghiêng tổng thể trước chi tiết danh tính) — đây có thể là do
   đặc điểm chung của contrastive loss + kiến trúc CNN ở quy mô dữ liệu này
   (chỉ 40 người ký huấn luyện), không riêng một kiến trúc nào; đáng thử thêm
   triplet loss hoặc tăng cường dữ liệu mạnh hơn nếu muốn giải quyết triệt để.
