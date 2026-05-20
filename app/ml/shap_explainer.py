import shap
from app.ml.model_loader import model

explainer = shap.TreeExplainer(model)

