# shivml/preprocessing.py
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer

def basic_preprocess(X: pd.DataFrame):
    """Encode categorical columns, fill missing values. Returns transformed X and encoders/dict."""
    X = X.copy()
    encoders = {}
    # Fill missing values: numeric -> mean, object -> 'missing'
    num_cols = X.select_dtypes(include=['number']).columns.tolist()
    cat_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()

    if num_cols:
        imputer_num = SimpleImputer(strategy='mean')
        X[num_cols] = imputer_num.fit_transform(X[num_cols])

    if cat_cols:
        imputer_cat = SimpleImputer(strategy='constant', fill_value='__missing__')
        X[cat_cols] = imputer_cat.fit_transform(X[cat_cols])
        for col in cat_cols:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            encoders[col] = le

    return X, encoders
