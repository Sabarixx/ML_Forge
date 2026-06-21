import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score


def train_all_models(df: pd.DataFrame, target_column: str):
    # Drop rows where the target itself is missing — can't learn from unknown answers
    df = df.dropna(subset=[target_column])

    # Drop any remaining rows with missing values in features (simple, safe default)
    df = df.dropna()

    if len(df) < 5:
        raise ValueError("Not enough clean rows left to train (need at least 5).")

    X = df.drop(columns=[target_column]).copy()
    y = df[target_column].copy()

    # Encode any text columns in X to numbers (models can't read raw text)

    for col in X.select_dtypes(include="object").columns:
        X[col] = LabelEncoder().fit_transform(X[col].astype(str))

    # Encode the target too, in case it's text (e.g. "Mumbai", "Delhi")
    y = LabelEncoder().fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "Decision Tree": DecisionTreeClassifier(),
        "Random Forest": RandomForestClassifier(),
        "KNN": KNeighborsClassifier(),
    }

    results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        results[name] = {
            "accuracy": round(accuracy_score(y_test, preds), 4),
            "precision": round(precision_score(y_test, preds, average="weighted", zero_division=0), 4),
            "recall": round(recall_score(y_test, preds, average="weighted", zero_division=0), 4),
        }

    return results