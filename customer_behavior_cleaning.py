"""
Customer Behavior Analytics - data cleaning and loading to MySQL.

Steps: read CSV -> clean and create new columns -> load into MySQL table `customers`.
Before running: put the CSV in the same folder and set your own MySQL details below.
"""
import pandas as pd
from sqlalchemy import create_engine

df = pd.read_csv("customer_shopping_behavior.csv")
print(df.head())
print(df.columns)
print(df.describe(include='all'))
print(df.info())

# --- Clean column names ---
df.columns = df.columns.str.replace(' ', '_')
df.columns = df.columns.str.lower()
df = df.rename(columns={'purchase_amount_(usd)': 'purchase_amount'})
print(df.columns)

# --- Missing values: fill review rating with the median of its category ---
print(df.isnull().sum())
df["review_rating"] = df.groupby("category")["review_rating"].transform(lambda x: x.fillna(x.median()))
print(df["review_rating"])
print(df.isnull().sum())

# --- Create age_group column (4 equal-sized groups) ---
labels = ["young_adult", "adult", "mid_age", "senior"]
df["age_group"] = pd.qcut(df["age"], q=4, labels=labels)
print(df[["age", "age_group"]].head(10))

# --- Convert purchase frequency to days ---
frequency_mapping = {"Fortnightly": 14,
                     "Weekly": 7,
                     "Monthly": 30,
                     "Quarterly": 90,
                     "Bi-Weekly": 14,
                     "Annually": 365,
                     "Every 3 Months": 90}

df["purchases_frequency_days"] = df["frequency_of_purchases"].map(frequency_mapping)
print(df[["purchases_frequency_days", "frequency_of_purchases"]].head(10))

# --- Check and drop the duplicate column ---
print((df["discount_applied"] == df["promo_code_used"]).all())
df = df.drop("promo_code_used", axis=1)

# --- Connect to MySQL (replace with your own details) ---
username = "root"
password = "YOUR_PASSWORD"   # never upload your real password
host = "localhost"
port = "3306"
database = "customer_behaviour"

connection_url = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
engine = create_engine(connection_url)

table_name = "customers"
df.to_sql(table_name, engine, if_exists="replace", index=False)

print(f"data successfully imported into sql table {table_name} and database {database}")
