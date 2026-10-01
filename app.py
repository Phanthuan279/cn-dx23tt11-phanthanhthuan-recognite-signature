"""Streamlit demo: draw or upload a handwritten digit, see KNN vs SVM
predictions side by side with confidence scores.

Drawing uses Streamlit's own built-in `st.components.v2` inline-component API
(a plain HTML5 canvas) rather than the third-party `streamlit-drawable-canvas`
package: that package's component registration call is incompatible with this
streamlit version (raises `StreamlitAPIException: ... must be declared in
pyproject.toml with asset_dir ...` on import), and upstream has not published
a fix. Per the đề tài's own technology note ("có thể thay bằng công nghệ
tương đương nếu giải thích được lựa chọn và bảo đảm sản phẩm chạy ổn định"),
this substitutes a first-party, dependency-free equivalent instead.
"""

from __future__ import annotations

import base64
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import joblib
import numpy as np
import streamlit as st
from PIL import Image
from scipy.special import softmax

BASE = Path(__file__).resolve().parent
MODELS_DIR = BASE / "models"

_CANVAS_HTML = """
<div>
  <canvas id="draw-canvas" width="280" height="280"></canvas>
  <div style="margin-top: 8px;">
    <button id="clear-btn" type="button">Xóa</button>
  </div>
</div>
"""

_CANVAS_CSS = """
#draw-canvas {
  border: 1px solid #888;
  touch-action: none;
  cursor: crosshair;
  background: black;
}
#clear-btn {
  padding: 4px 14px;
}
"""

_CANVAS_JS = """
export default function(component) {
    const { setStateValue, parentElement } = component;
    const canvas = parentElement.querySelector('#draw-canvas');
    const ctx = canvas.getContext('2d');

    function clear() {
        ctx.fillStyle = 'black';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }
    clear();
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 18;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    let drawing = false;
    let lastX = 0;
    let lastY = 0;

    function getPos(e) {
        const rect = canvas.getBoundingClientRect();
        const point = e.touches ? e.touches[0] : e;
        return [point.clientX - rect.left, point.clientY - rect.top];
    }

    function start(e) {
        drawing = true;
        [lastX, lastY] = getPos(e);
    }

    function move(e) {
        if (!drawing) return;
        const [x, y] = getPos(e);
        ctx.beginPath();
        ctx.moveTo(lastX, lastY);
        ctx.lineTo(x, y);
        ctx.stroke();
        [lastX, lastY] = [x, y];
        e.preventDefault();
    }

    function end() {
        if (!drawing) return;
        drawing = false;
        setStateValue('image_data', canvas.toDataURL('image/png'));
    }

    canvas.addEventListener('mousedown', start);
    canvas.addEventListener('mousemove', move);
    window.addEventListener('mouseup', end);
    canvas.addEventListener('touchstart', start);
    canvas.addEventListener('touchmove', move);
    canvas.addEventListener('touchend', end);

    parentElement.querySelector('#clear-btn').addEventListener('click', () => {
        clear();
        setStateValue('image_data', null);
    });

    setStateValue('image_data', null);
}
"""

_draw_canvas = st.components.v2.component("digit_draw_canvas", html=_CANVAS_HTML, css=_CANVAS_CSS, js=_CANVAS_JS)


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


def _decode_data_url(data_url: str) -> Image.Image:
    _, b64data = data_url.split(",", 1)
    return Image.open(io.BytesIO(base64.b64decode(b64data))).convert("RGB")


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
        result = _draw_canvas(on_image_data_change=lambda: None, key="canvas")
        if result.image_data:
            image = _decode_data_url(result.image_data)

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
