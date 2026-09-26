"""Streamlit demo: upload a known-genuine reference signature and a query
signature, see both before/after preprocessing, get a Thật/Giả verdict with
the distance D, and drag a threshold slider to see its effect on FAR/FRR.

PRIVACY: uploaded images are processed entirely in memory via
app/inference.py and are never written to disk or logged. Run with:
    streamlit run app/demo_app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

from inference import ModelNotReadyError, compare, decision, load_model, lookup_far_frr, preprocess_and_embed
from sigverify.utils.config import load_config

st.set_page_config(page_title="Xác minh chữ ký viết tay (Siamese)", layout="wide")
st.title("Xác minh chữ ký viết tay offline bằng mạng Siamese")
st.caption(
    "Ảnh tải lên chỉ được xử lý trong bộ nhớ của phiên làm việc này và không bao giờ được lưu xuống đĩa."
)

CONFIG = load_config("configs/default.yaml")

model_choice = st.sidebar.selectbox("Mô hình", ["config_a", "config_b"], format_func=lambda x: {
    "config_a": "Config A (CNN từ đầu)",
    "config_b": "Config B (Transfer learning)",
}[x])

try:
    model, threshold_info, far_frr_curve = load_model(model_choice)
except ModelNotReadyError as e:
    st.error(str(e))
    st.stop()

if model_choice == "config_a":
    target_size = tuple(CONFIG["image"]["size_scratch"])
    mode = "unit"
else:
    target_size = tuple(CONFIG["image"]["size_transfer"])
    mode = "imagenet"

thresholds = far_frr_curve["thresholds"]
tau = st.sidebar.slider(
    "Ngưỡng τ (khoảng cách)",
    min_value=float(min(thresholds)),
    max_value=float(max(thresholds)),
    value=float(threshold_info["tau"]),
    step=(float(max(thresholds)) - float(min(thresholds))) / 200,
)
far_at_tau, frr_at_tau = lookup_far_frr(tau, far_frr_curve)
st.sidebar.metric("FAR tại τ hiện tại", f"{far_at_tau:.2%}")
st.sidebar.metric("FRR tại τ hiện tại", f"{frr_at_tau:.2%}")
st.sidebar.caption(f"τ mặc định (chọn tại EER trên validation): {threshold_info['tau']:.4f}")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Ảnh mẫu (đã biết là thật)")
    reference_file = st.file_uploader("Tải lên chữ ký mẫu", type=["png", "jpg", "jpeg"], key="reference")
with col2:
    st.subheader("Ảnh cần kiểm tra")
    query_file = st.file_uploader("Tải lên chữ ký cần kiểm tra", type=["png", "jpg", "jpeg"], key="query")

if reference_file and query_file:
    reference_bytes = reference_file.getvalue()
    query_bytes = query_file.getvalue()

    denoise_method = CONFIG["preprocessing"]["denoise"]
    binarize_output = CONFIG["preprocessing"]["binarize_output"]
    crop_to_bbox = CONFIG["preprocessing"]["crop_to_bbox"]

    ref_processed, ref_embedding = preprocess_and_embed(
        model, reference_bytes, target_size, mode, denoise_method, binarize_output, crop_to_bbox
    )
    query_processed, query_embedding = preprocess_and_embed(
        model, query_bytes, target_size, mode, denoise_method, binarize_output, crop_to_bbox
    )

    st.divider()
    img_col1, img_col2, img_col3, img_col4 = st.columns(4)
    with img_col1:
        st.image(reference_bytes, caption="Ảnh mẫu (gốc)", use_container_width=True)
    with img_col2:
        st.image(ref_processed, caption="Ảnh mẫu (đã xử lý)", use_container_width=True, clamp=True)
    with img_col3:
        st.image(query_bytes, caption="Ảnh kiểm tra (gốc)", use_container_width=True)
    with img_col4:
        st.image(query_processed, caption="Ảnh kiểm tra (đã xử lý)", use_container_width=True, clamp=True)

    distance = compare(ref_embedding, query_embedding)
    verdict = decision(distance, tau)

    st.divider()
    result_col1, result_col2 = st.columns(2)
    with result_col1:
        if verdict == "Thật":
            st.success(f"Kết quả: {verdict}")
        else:
            st.error(f"Kết quả: {verdict}")
    with result_col2:
        st.metric("Khoảng cách D", f"{distance:.4f}", delta=f"τ = {tau:.4f}")
else:
    st.info("Tải lên cả hai ảnh (mẫu và cần kiểm tra) để xem kết quả.")
