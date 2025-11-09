import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, r2_score, mean_squared_error, mean_absolute_error,
    confusion_matrix, classification_report
)
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.svm import SVC, SVR
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor

# Optional XGBoost
try:
    from xgboost import XGBClassifier, XGBRegressor
    xgb_available = True
except ImportError:
    xgb_available = False


def auto_train(X, y, model_name='rf', test_size=0.2, random_state=42, problem_type='auto'):
    """
    Automatically trains and evaluates a model.
    
    Parameters:
        X (pd.DataFrame or np.array): Features
        y (pd.Series or np.array): Target
        model_name (str): Model short code (e.g. 'rf', 'lr', 'svm', 'dt', 'knn', 'xgb', etc.)
        problem_type (str): 'classification', 'regression', or 'auto'
    """

    # Step 1: Auto-detect problem type
    if problem_type == 'auto':
        problem_type = 'classification' if len(pd.Series(y).unique()) < 20 else 'regression'

    print(f"🔍 Problem type detected: {problem_type.title()}")

    # Step 2: Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    # Step 3: Model dictionary
    classifiers = {
        'rf': RandomForestClassifier(random_state=random_state),
        'lr': LogisticRegression(max_iter=1000),
        'svm': SVC(),
        'dt': DecisionTreeClassifier(random_state=random_state),
        'knn': KNeighborsClassifier(),
        'nb': GaussianNB(),
        'gb': GradientBoostingClassifier(random_state=random_state),
    }

    regressors = {
        'rfr': RandomForestRegressor(random_state=random_state),
        'lr': LinearRegression(),
        'svr': SVR(),
        'dtr': DecisionTreeRegressor(random_state=random_state),
        'knnr': KNeighborsRegressor(),
        'gbr': GradientBoostingRegressor(random_state=random_state),
    }

    if xgb_available:
        classifiers['xgb'] = XGBClassifier(eval_metric='mlogloss', random_state=random_state)
        regressors['xgbr'] = XGBRegressor(random_state=random_state)

    # Step 4: Model selection
    model_dict = classifiers if problem_type == 'classification' else regressors
    if model_name not in model_dict:
        raise ValueError(f"❌ Invalid model name '{model_name}'. Available: {list(model_dict.keys())}")

    model = model_dict[model_name]

    # Step 5: Train
    print(f"🚀 Training model: {model.__class__.__name__}")
    model.fit(X_train, y_train)

    # Step 6: Predict
    y_pred = model.predict(X_test)

    print("✅ Model trained successfully!\n")

    # Step 7: Evaluation
    if problem_type == 'classification':
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        cm = confusion_matrix(y_test, y_pred)

        print("--- 📊 Classification Metrics ---")
        print(f"Accuracy : {acc:.3f}")
        print(f"Precision: {prec:.3f}")
        print(f"Recall   : {rec:.3f}")
        print(f"F1 Score : {f1:.3f}\n")
        print("--- 🧾 Classification Report ---")
        print(classification_report(y_test, y_pred, zero_division=0))
        print("--- 🔢 Confusion Matrix ---")
        print(pd.DataFrame(cm))

    else:
        r2 = r2_score(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)

        print("--- 📈 Regression Metrics ---")
        print(f"R² Score        : {r2:.3f}")
        print(f"Mean Squared Err: {mse:.3f}")
        print(f"Mean Abs Error  : {mae:.3f}")

    return model
