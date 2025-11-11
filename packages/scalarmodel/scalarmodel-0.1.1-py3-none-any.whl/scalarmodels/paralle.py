#!pip install -q joblib
import time
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def parallel():
    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    start_time = time.time()
    clf_central = RandomForestClassifier(n_estimators=100, n_jobs=1, random_state=42)
    clf_central.fit(X_train, y_train)
    y_pred_central = clf_central.predict(X_test)
    central_time = time.time() - start_time
    central_accuracy = accuracy_score(y_test, y_pred_central)
    
    start_time = time.time()
    clf_parallel = RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=42)
    clf_parallel.fit(X_train, y_train)
    y_pred_parallel = clf_parallel.predict(X_test)
    parallel_time = time.time() - start_time
    parallel_accuracy = accuracy_score(y_test, y_pred_parallel)
    
    print("Centralized Training:")
    print(f"   Time: {central_time:.4f} seconds")
    print(f"   Accuracy: {central_accuracy:.4f}")
    
    print("\n Parallelized Training (joblib, n_jobs=-1):")
    print(f"   Time: {parallel_time:.4f} seconds")
    print(f"   Accuracy: {parallel_accuracy:.4f}")
    
    print("\n Comparison:")
    speedup = central_time / parallel_time if parallel_time > 0 else float('inf')
    print(f"   Speedup: {speedup:.2f}x faster using parallelism")