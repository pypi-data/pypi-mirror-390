import pandas as pd
from datacleanerpro import DataCleaner

# Create a sample CSV for testing
data = {
    "Name": ["Alice", "Bob", "Alice", "David"],
    "Age": [25, None, 25, 30],
    "Score": [85, 90, 85, None]
}
df = pd.DataFrame(data)
df.to_csv("test.csv", index=False)

# Initialize cleaner
cleaner = DataCleaner("test.csv")
cleaner.remove_duplicates()
cleaner.fill_missing("mean")
cleaner.drop_columns(["Score"])
cleaner.save_cleaned_data("output.csv")

print("Data cleaning complete!")
