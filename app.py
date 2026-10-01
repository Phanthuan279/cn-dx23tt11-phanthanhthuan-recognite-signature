"""Streamlit demo: draw or upload a handwritten digit, see KNN vs SVM
predictions side by side with confidence scores.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import joblib
import numpy as np
import streamlit as st
from PIL import Image
from scipy.special import softmax
from streamlit_drawable_canvas import st_canvas

BASE = Path(__file__).resolve().parent
MODELS_DIR = BASE / "models"


@st.cache_resource
def load_models():
    knn_path = MODELS_DIR / "knn_mnist.joblib"
    svm_path = MODELS_DIR / "svm_mnist.joblib"
    if not knn_path.exists() or not svm_path.exists():
        return None, None
    return joblib.load(knn_path), joblib.load(svm_path)


def preprocess(image: Image.Image) -> np.ndarray:
    """Grayscale, invert if needed (MNIST is white digit on black), resize to
    28x28, normalize to [0, 1], flatten to the 784-d vector the models expect.
    """
    img = image.convert("L").resize((28, 28), Image.LANCZOS)
    arr = np.array(img).astype("float32")
    # MNIST convention: digit is bright (high value) on a dark background.
    # A typical uploaded photo is the opposite (dark ink on white paper), so
    # auto-invert when the image looks "mostly bright" (paper-like).
    if arr.mean() > 127:
        arr = 255.0 - arr
    arr = arr / 255.0
    return arr.reshape(1, -1)


def main() -> None:
    st.set_page_config(page_title="Nhận dạng chữ số viết tay", page_icon="🔢")
    st.title("Nhận dạng chữ số viết tay — KNN vs SVM")
    st.caption(
        "Đồ án thực tập chuyên ngành — so sánh hiệu quả KNN và SVM trên MNIST. "
        "Vẽ hoặc tải lên một chữ số (0-9) để xem hai mô hình dự đoán."
    )

    knn, svm = load_models()
    if knn is None or svm is None:
        st.error(
            "Chưa tìm thấy mô hình đã huấn luyện trong models/. "
            "Chạy `python scripts/train.py` trước khi mở demo này."
        )
        return

    tab_draw, tab_upload = st.tabs(["Vẽ chữ số", "Tải ảnh lên"])
    image = None

    with tab_draw:
        canvas = st_canvas(
            fill_color="black",
            stroke_width=18,
            stroke_color="white",
            background_color="black",
            width=280,
            height=280,
            drawing_mode="freedraw",
            key="canvas",
        )
        if canvas.image_data is not None and canvas.image_data[:, :, :3].sum() > 0:
            image = Image.fromarray(canvas.image_data.astype("uint8")).convert("RGB")

    with tab_upload:
        uploaded = st.file_uploader("Ảnh chữ số (PNG/JPG)", type=["png", "jpg", "jpeg"])
        if uploaded is not None:
            image = Image.open(uploaded)

    if image is None:
        st.info("Vẽ một chữ số hoặc tải ảnh lên để xem kết quả.")
        return

    x = preprocess(image)

    col_img, col_knn, col_svm = st.columns(3)
    with col_img:
        st.subheader("Ảnh đầu vào (28×28)")
        st.image(Image.fromarray((x.reshape(28, 28) * 255).astype("uint8")), width=140)

    with col_knn:
        st.subheader("KNN")
        pred = knn.predict(x)[0]
        proba = knn.predict_proba(x)[0]
        st.metric("Dự đoán", pred)
        st.bar_chart({"xác suất": proba}, x_label="chữ số")

    with col_svm:
        st.subheader("SVM")
        pred = svm.predict(x)[0]
        # SVC without probability=True (see src/digitrec/models.py) -- use the
        # one-vs-rest decision margins, softmax-normalized, as a confidence
        # proxy instead of calibrated probabilities.
        scores = svm.decision_function(x)[0]
        confidence = softmax(scores)
        st.metric("Dự đoán", pred)
        st.bar_chart({"điểm tin cậy (ước lượng)": confidence}, x_label="chữ số")

    st.divider()
    st.caption(
        "Lưu ý: điểm tin cậy của SVM là ước lượng từ decision_function (softmax), "
        "không phải xác suất đã hiệu chỉnh như KNN."
    )


if __name__ == "__main__":
    main()
