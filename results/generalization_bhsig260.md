# Kiểm tra tổng quát zero-shot trên BHSig260

Mô hình Config A huấn luyện trên CEDAR được áp thẳng lên BHSig260 **không fine-tune lại**, dùng đúng ngưỡng τ đã đóng băng từ CEDAR validation. Đây là phép thử trực tiếp cho tuyên bố writer-independent của đồ án.

## Siamese (Config A)
- Skilled forgery: FAR=0.1623, FRR=0.5315, AUC=0.7336 -> CHƯA ĐẠT (mục tiêu EER≤20%)
- Random forgery: FAR=0.0738, FRR=0.5315, AUC=0.8463

## Baseline (HOG/LBP + SVM)
- Skilled forgery: FAR=0.4185, FRR=0.2165, AUC=0.7672 -> CHƯA ĐẠT (mục tiêu EER≤20%)
- Random forgery: FAR=0.0569, FRR=0.2165, AUC=0.9230
