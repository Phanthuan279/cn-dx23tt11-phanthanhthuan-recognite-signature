"""Generate results/comparison_summary.md from the baseline, Config A and
Config B metrics.json files, so the ready-to-cite comparison table used in
the thesis report is always derived from the actual run artefacts, never
hand-typed.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

EER_TARGET_CEDAR_SKILLED = 0.05


def _load(path: Path) -> dict | None:
    return json.loads(path.read_text()) if path.exists() else None


def _row(name: str, metrics: dict | None) -> str:
    if metrics is None:
        return f"| {name} | - | - | - | - | - | - |"
    overall = metrics.get("overall", {})
    skilled = metrics.get("by_forgery_type", {}).get("skilled_forgery", {})
    random_ = metrics.get("by_forgery_type", {}).get("random_forgery", {})
    return (
        f"| {name} "
        f"| {overall.get('accuracy', float('nan')):.4f} "
        f"| {skilled.get('far', float('nan')):.4f} / {skilled.get('frr', float('nan')):.4f} "
        f"| {skilled.get('auc', float('nan')):.4f} "
        f"| {random_.get('far', float('nan')):.4f} / {random_.get('frr', float('nan')):.4f} "
        f"| {random_.get('auc', float('nan')):.4f} "
        f"| {'ĐẠT' if skilled.get('far') is not None and (skilled['far'] + skilled['frr']) / 2 <= EER_TARGET_CEDAR_SKILLED else 'CHƯA ĐẠT'} |"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", default="results/baseline/metrics.json")
    parser.add_argument("--config-a", default="results/config_a/metrics.json")
    parser.add_argument("--config-b", default="results/config_b/metrics.json")
    parser.add_argument("--out", default="results/comparison_summary.md")
    args = parser.parse_args()

    baseline = _load(Path(args.baseline))
    config_a = _load(Path(args.config_a))
    config_b = _load(Path(args.config_b))

    lines = [
        "# So sánh Baseline vs. Config A vs. Config B (CEDAR test set)",
        "",
        "Sinh tự động bởi `scripts/generate_comparison_summary.py` từ các file "
        "`results/{baseline,config_a,config_b}/metrics.json`. Không chỉnh sửa file này bằng tay.",
        "",
        "| Mô hình | Accuracy | FAR/FRR (skilled) | AUC (skilled) | FAR/FRR (random) | AUC (random) | Đạt EER≤5% skilled? |",
        "|---|---|---|---|---|---|---|",
        _row("Baseline (HOG/LBP+SVM)", baseline),
        _row("Config A (CNN từ đầu)", config_a),
        _row("Config B (Transfer learning)", config_b),
        "",
        "EER ước lượng ở trên là (FAR+FRR)/2 tại ngưỡng τ đã đóng băng — không phải EER chính xác "
        "(điểm FAR=FRR); xem `results/{model}/metrics.json` để có giá trị EER chính xác trên validation.",
    ]

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n")
    print(f"[generate_comparison_summary] Written to {out_path}")

    for name, metrics in (("baseline", baseline), ("config_a", config_a), ("config_b", config_b)):
        if metrics is None:
            print(f"[generate_comparison_summary] WARNING: {name} metrics not found yet -- run its script first.")


if __name__ == "__main__":
    main()
