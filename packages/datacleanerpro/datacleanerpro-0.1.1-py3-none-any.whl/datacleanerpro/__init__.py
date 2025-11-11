"""
DataCleanerPro: A simple and efficient data cleaning library for CSV files.
"""

import pandas as pd

class DataCleaner:
    def __init__(self, file_path):
        """Initialize with a CSV file path."""
        self.file_path = file_path
        self.df = pd.read_csv(file_path)

    def remove_duplicates(self):
        """Remove duplicate rows from the dataset."""
        before = len(self.df)
        self.df.drop_duplicates(inplace=True)
        after = len(self.df)
        print(f"Removed {before - after} duplicates.")
        return self.df

    def fill_missing(self, strategy="mean"):
        """
        Fill missing values using the specified strategy: mean, median, mode, or zero.
        """
        for column in self.df.select_dtypes(include=["float64", "int64"]).columns:
            if self.df[column].isnull().any():
                if strategy == "mean":
                    self.df[column].fillna(self.df[column].mean(), inplace=True)
                elif strategy == "median":
                    self.df[column].fillna(self.df[column].median(), inplace=True)
                elif strategy == "mode":
                    self.df[column].fillna(self.df[column].mode()[0], inplace=True)
                elif strategy == "zero":
                    self.df[column].fillna(0, inplace=True)
        print(f"Missing values filled using '{strategy}' strategy.")
        return self.df

    def drop_columns(self, columns):
        """Drop specified columns from the dataset."""
        self.df.drop(columns=columns, inplace=True, errors="ignore")
        print(f"Dropped columns: {columns}")
        return self.df

    def save_cleaned_data(self, output_path="cleaned_data.csv"):
        """Save the cleaned data to a new CSV file."""
        self.df.to_csv(output_path, index=False)
        print(f"Cleaned data saved to {output_path}")
        return output_path
