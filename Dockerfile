# CPU-only demo image. Trained weights (models_registry/) and evaluation
# artefacts (results/*/far_frr_curve.json) must already exist -- produced by
# running scripts/train_config_a.py (and optionally train_config_b.py) on
# Colab/Kaggle first, then copied in (they are gitignored, not baked in here).
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY app/ app/
COPY configs/ configs/
RUN pip install --no-cache-dir -e .

EXPOSE 8501

CMD ["streamlit", "run", "app/demo_app.py", "--server.address=0.0.0.0"]
