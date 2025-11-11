
from typing import Dict, List

def mini_code() -> str:
    return """
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import r2_score, mean_squared_error

def load_data(path):
    data = pd.read_csv(path)
    X = data[['GRE Score', 'TOEFL Score', 'University Rating', 'SOP', 'LOR', 'CGPA', 'Research']]
    y = data['Chance of Admit']
    return X, y

def build_pipeline(model):
    return Pipeline([
        ('scaler', StandardScaler()),
        ('model', model)
    ])

def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    return r2, rmse

def main():
    X, y = load_data("Synthetic_Graduate_Admissions.csv")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    models = {
        "Linear Regression": LinearRegression(),
        "Decision Tree": DecisionTreeRegressor(random_state=42),
        "Random Forest": RandomForestRegressor(random_state=42),
        "Support Vector Regressor": SVR(kernel='rbf'),
        "KNN Regressor": KNeighborsRegressor(n_neighbors=5)
    }

    results = []
    for name, model in models.items():
        pipe = build_pipeline(model)
        pipe.fit(X_train, y_train)
        r2, rmse = evaluate_model(pipe, X_test, y_test)
        results.append({"Model": name, "R2 Score": round(r2, 3), "RMSE": round(rmse, 3)})

    results_df = pd.DataFrame(results)
    print("\\nModel Performance Summary:")
    print(results_df.to_string(index=False))

    sample = pd.DataFrame([[320, 110, 4, 4.5, 4.0, 9.0, 1]],
                          columns=['GRE Score', 'TOEFL Score', 'University Rating', 'SOP', 'LOR', 'CGPA', 'Research'])
    best_model = build_pipeline(RandomForestRegressor(random_state=42))
    best_model.fit(X, y)
    pred = best_model.predict(sample)
    print(f"\\nPredicted Chance of Admission: {pred[0]*100:.2f}%")

if __name__ == "__main__":
    main()
"""

def forestfire_code() -> str:
    return """
from multiprocessing import Pool
import pandas as pd
import sqlite3


def mapper(row):
    return (row["Month"], row["Temperature_Celsius"])


def reducer(mapped_data):
    result = {}
    for month, temp in mapped_data:
        result.setdefault(month, []).append(temp)
    return {m: sum(v) / len(v) for m, v in result.items()}


def run_mapreduce(df):
    with Pool() as p:
        mapped = p.map(mapper, [row for _, row in df.iterrows()])
    reduced = reducer(mapped)

    print("\\nAverage Temperature per Month:")
    for m, t in reduced.items():
        print(f"{m}: {t:.2f}")
    return reduced


def top_fire_months(df, top_n=5):
    top = df.groupby("Month")["Burned_Area_hectares"].mean().sort_values(ascending=False).head(top_n)
    print(f"\\nTop {top_n} Months with Largest Fire Area:\\n{top}\\n")
    return top


def temperature_area_correlation(df):
    corr = df["Temperature_Celsius"].corr(df["Burned_Area_hectares"])
    print(f"Correlation between Temperature and Fire Area: {corr:.2f}")
    return corr


def query_avg_area_by_month(conn):
    query = '''
        SELECT Month, AVG(Burned_Area_hectares) AS avg_area
        FROM forestfires
        GROUP BY Month
        ORDER BY avg_area DESC;
    '''
    result = pd.read_sql_query(query, conn)
    print("\\nAverage Burned Area by Month (from SQL):")
    print(result)
    return result


def run_pipeline():
    print("=== Forest Fire Analysis Pipeline Started ===\\n")

    df = pd.read_csv("forestfires.csv")
    print(f"Loaded dataset with {len(df)} rows and {len(df.columns)} columns.")

    conn = sqlite3.connect("forestfires.db")
    df.to_sql("forestfires", conn, if_exists="replace", index=False)
    print("Data saved to SQLite database.\\n")

    run_mapreduce(df)
    top_fire_months(df)
    temperature_area_correlation(df)
    query_avg_area_by_month(conn)

    print("\\n=== Pipeline Completed Successfully ===")


if __name__ == "__main__":
    run_pipeline()
"""

def placeholder_code() -> str:
    return "# Add your next practical code here..."

def get_code_map() -> Dict[str, str]:
    return {
        "mini": mini_code(),
        "forestfire": forestfire_code(),
        "placeholder": placeholder_code(),
    }

def get_code(name: str) -> str:
    """
    Retrieve a stored code snippet by name.
    Available names: see list_codes().
    """
    key = (name or "").strip().lower()
    mapping = get_code_map()
    if key not in mapping:
        available = ", ".join(sorted(mapping.keys()))
        raise KeyError(f"Code '{name}' not found. Try one of: {available}")
    return mapping[key]

def list_codes() -> List[str]:
    \"Return a list of available code names.\"
    return sorted(get_code_map().keys())
