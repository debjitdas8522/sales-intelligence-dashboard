import pandas as pd
from sqlalchemy import create_engine

# Load CSV file
df = pd.read_csv("data/superstore.csv", encoding="latin1")

# Create SQLite database
engine = create_engine("sqlite:///database/sales.db")

# Save data into SQL table
df.to_sql("sales_data", engine, if_exists="replace", index=False)

print("Database created successfully!")
