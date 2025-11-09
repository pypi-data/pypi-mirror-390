from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    r2_score, mean_squared_error, mean_absolute_error, classification_report
)
import pandas as pd


def classification_metrics(y_true, y_pred):
    """
    Prints classification metrics.
    """
    print("📊 Classification Metrics:")
    print(f"Accuracy : {accuracy_score(y_true, y_pred):.3f}")
    print(f"Precision: {precision_score(y_true, y_pred, average='weighted'):.3f}")
    print(f"Recall   : {recall_score(y_true, y_pred, average='weighted'):.3f}")
    print(f"F1 Score : {f1_score(y_true, y_pred, average='weighted'):.3f}")
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred))


def regression_metrics(y_true, y_pred):
    """
    Prints regression metrics.
    """
    print("📈 Regression Metrics:")
    print(f"R² Score       : {r2_score(y_true, y_pred):.3f}")
    print(f"Mean Abs Error : {mean_absolute_error(y_true, y_pred):.3f}")
    print(f"Mean Sq Error  : {mean_squared_error(y_true, y_pred):.3f}")
