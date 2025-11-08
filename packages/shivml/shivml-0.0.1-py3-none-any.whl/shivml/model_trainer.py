# shivml/model_trainer.py
import os
from typing import Union
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, mean_squared_error, r2_score)

from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.svm import SVC, SVR

from .utils import load_data
from .preprocessing import basic_preprocess

CLASSIFIERS = {
    "LogisticRegression": LogisticRegression,
    "RandomForest": RandomForestClassifier,
    "SVC": SVC
}

REGRESSORS = {
    "LinearRegression": LinearRegression,
    "RandomForestRegressor": RandomForestRegressor,
    "SVR": SVR
}

def _detect_problem_type(y: pd.Series, problem_type: Union[str, None]):
    if problem_type:
        return problem_type.lower()
    # If target has <= 20 unique values and is integer-like -> classification
    if y.dtype.kind in 'ifu' and pd.api.types.is_integer_dtype(y) and y.nunique() <= 20:
        return 'classification'
    # If non-numeric -> classification
    if y.dtype == object or pd.api.types.is_categorical_dtype(y):
        return 'classification'
    # otherwise regression
    return 'regression'

def train_model(data: Union[str, pd.DataFrame],
                target: str,
                model: str = None,
                problem_type: str = None,
                test_size: float = 0.2,
                random_state: int = 42,
                save_model: bool = True):
    """
    Main function to train a model.
    data: csv path or DataFrame
    target: target column name
    model: model name string (optional, will use default if None)
    problem_type: 'classification' or 'regression' (optional)
    """
    df = load_data(data)
    if target not in df.columns:
        raise ValueError(f"Target column '{target}' not found in data")

    X = df.drop(columns=[target])
    y = df[target]

    problem = _detect_problem_type(y, problem_type)
    print(f"Detected problem type: {problem}")

    # Preprocess features
    X_proc, encoders = basic_preprocess(X)

    # Scale numeric columns
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_proc)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=test_size, random_state=random_state
    )

    # Choose default model if not provided
    if model is None:
        model = "RandomForest" if problem == 'classification' else "LinearRegression"

    # Instantiate chosen model class
    if problem == 'classification':
        model_map = CLASSIFIERS
    else:
        model_map = REGRESSORS

    if model not in model_map:
        raise ValueError(f"Model '{model}' unknown. Choose from: {list(model_map.keys())}")

    ModelClass = model_map[model]
    clf = ModelClass()
    print(f"Training {model} ...")
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)

    # Metrics
    print("\nModel evaluation:")
    if problem == 'classification':
        print("Accuracy:", accuracy_score(y_test, y_pred))
        print("Precision (weighted):", precision_score(y_test, y_pred, average='weighted', zero_division=0))
        print("Recall (weighted):", recall_score(y_test, y_pred, average='weighted', zero_division=0))
        print("F1 (weighted):", f1_score(y_test, y_pred, average='weighted', zero_division=0))
    else:
        print("MSE:", mean_squared_error(y_test, y_pred))
        print("RMSE:", mean_squared_error(y_test, y_pred, squared=False))
        print("R2:", r2_score(y_test, y_pred))

    # Save model & artifacts
    if save_model:
        os.makedirs("models", exist_ok=True)
        model_path = os.path.join("models", f"{model}.pkl")
        joblib.dump({
            'model': clf,
            'scaler': scaler,
            'encoders': encoders
        }, model_path)
        print(f"Saved model to: {model_path}")

    return {'model': clf, 'scaler': scaler, 'encoders': encoders}
