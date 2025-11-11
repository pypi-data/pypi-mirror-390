# Random Forest vs Traditional Algorithms (Logistic Regression, Decision Tree) on California Housing
import pandas as pd
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report

def comp():
    california = fetch_california_housing(as_frame=True)
    df = california.frame
    
    median_target = df['MedHouseVal'].median()
    df['target'] = (df['MedHouseVal'] > median_target).astype(int)
    X = df.drop(columns=['MedHouseVal', 'target'])
    y = df['target']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test  = scaler.transform(X_test)
    
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    dt = DecisionTreeClassifier(random_state=42)
    lr = LogisticRegression(max_iter=1000, random_state=42)
    
    rf.fit(X_train, y_train)
    dt.fit(X_train, y_train)
    lr.fit(X_train, y_train)
    
    models = {'Random Forest': rf, 'Decision Tree': dt, 'Logistic Regression': lr}
    
    for name, model in models.items():
        y_pred = model.predict(X_test)
        print(f"\n{name} Accuracy: {accuracy_score(y_test, y_pred):.4f}")
        print(classification_report(y_test, y_pred, zero_division=0))
    