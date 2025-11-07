import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Suppose your dataset is:
df = pd.read_csv("numerical_dataset.csv")  # Replace with your dataset

# ---------------- 1. Overview ----------------
print("First 10 rows of dataset:\n", df.head())
print("\nDataset Info:")
print(df.info())
print("\nDataset Shape:", df.shape)
print("\nMissing Values:\n", df.isnull().sum())
print("\nBasic Statistics for Numerical Columns:\n", df.describe())
print("\nValue counts for Categorical Columns:")
for col in df.select_dtypes(include='object').columns:
    print(f"\nColumn: {col}")
    print(df[col].value_counts())

# ---------------- 2. Visualizations ----------------

# Histograms for continuous features
num_cols = df.select_dtypes(include=np.number).columns
df[num_cols].hist(bins=15, figsize=(12, 5))
plt.suptitle("Histograms of Numerical Features")
plt.show()

# Boxplots to check outliers
for col in num_cols:
    plt.figure(figsize=(6, 4))
    sns.boxplot(x=df[col])
    plt.title(f"Boxplot of {col}")
    plt.show()

# Countplots for categorical features
cat_cols = df.select_dtypes(include='object').columns
for col in cat_cols:
    plt.figure(figsize=(6, 4))
    sns.countplot(x=df[col])
    plt.title(f"Countplot of {col}")
    plt.show()

# Correlation heatmap for numerical features
plt.figure(figsize=(8, 6))
sns.heatmap(df[num_cols].corr(), annot=True, cmap='coolwarm')
plt.title("Correlation Heatmap")
plt.show()

# Pairplot to see relationships and target distribution
if 'Score' in df.columns:  # replace with your target column
    sns.pairplot(df, hue='Score', vars=num_cols)
    plt.show()

# Boxplots of numerical features vs target
target_col = 'Score'
for col in num_cols:
    plt.figure(figsize=(6, 4))
    sns.boxplot(x=target_col, y=col, data=df)
    plt.title(f"{col} vs {target_col}")
    plt.show()

# Crosstab / pivot table for categorical features vs target
for col in cat_cols:
    if col != target_col:
        print(f"\nCrosstab of {col} vs {target_col}")
        print(pd.crosstab(df[col], df[target_col]))

# ---------------- 3. Advanced EDA ----------------
# Distribution of numerical features per category
for col in num_cols:
    plt.figure(figsize=(8, 4))
    sns.kdeplot(data=df, x=col, hue=target_col, fill=True)
    plt.title(f"Distribution of {col} by {target_col}")
    plt.show()
