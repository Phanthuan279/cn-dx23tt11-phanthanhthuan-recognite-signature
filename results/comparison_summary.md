# So sánh Baseline vs. Config A vs. Config B (CEDAR test set)

Sinh tự động bởi `scripts/generate_comparison_summary.py` từ các file `results/{baseline,config_a,config_b}/metrics.json`. Không chỉnh sửa file này bằng tay.

| Mô hình | Accuracy | FAR/FRR (skilled) | AUC (skilled) | FAR/FRR (random) | AUC (random) | Đạt EER≤5% skilled? |
|---|---|---|---|---|---|---|
| Baseline (HOG/LBP+SVM) | 0.7850 | 0.3050 / 0.1950 | 0.8625 | 0.1650 / 0.1950 | 0.9106 | CHƯA ĐẠT |
| Config A (CNN từ đầu) | 0.8788 | 0.0000 / 0.1075 | 1.0000 | 0.2700 / 0.1075 | 0.8773 | CHƯA ĐẠT |
| Config B (Transfer learning) | - | - | - | - | - | - |

EER ước lượng ở trên là (FAR+FRR)/2 tại ngưỡng τ đã đóng băng — không phải EER chính xác (điểm FAR=FRR); xem `results/{model}/metrics.json` để có giá trị EER chính xác trên validation.
