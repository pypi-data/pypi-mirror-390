import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder, StandardScaler

# ---------------- Load dataset ----------------
# Replace 'numerical_dataset.csv' with your dataset path
df = pd.read_csv('numerical_dataset_2.csv')

# Specify identity column(s) to ignore
identity_columns = ['ID']  # if you have ID column
df_analysis = df.drop(columns=[col for col in identity_columns if col in df.columns])

# ---------------- Data Preprocessing ----------------

# 1. Handle missing values
for col in df_analysis.columns:
    if df_analysis[col].dtype in ['float64', 'int64']:
        df_analysis[col].fillna(df_analysis[col].median(), inplace=True)
    else:
        df_analysis[col].fillna(df_analysis[col].mode()[0], inplace=True)

# 2. Encode categorical columns
categorical_cols = df_analysis.select_dtypes(include='object').columns
le = LabelEncoder()
for col in categorical_cols:
    df_analysis[col] = le.fit_transform(df_analysis[col])

# 3. Scale numerical columns
numerical_cols = df_analysis.select_dtypes(include=['int64','float64']).columns
scaler = StandardScaler()
df_analysis[numerical_cols] = scaler.fit_transform(df_analysis[numerical_cols])

# ---------------- Exploratory Data Analysis ----------------

# 1. Univariate Analysis
print("---- Univariate Analysis ----")
for col in df_analysis.columns:
    print(f"\nColumn: {col}")
    print(df_analysis[col].describe())
    plt.figure(figsize=(6,4))
    sns.histplot(df_analysis[col], kde=True, bins=30)
    plt.title(f'Distribution of {col}')
    plt.show()

# 2. Bivariate Analysis
print("---- Bivariate Analysis ----")
for col1 in df_analysis.columns:
    for col2 in df_analysis.columns:
        if col1 != col2:
            plt.figure(figsize=(6,4))
            sns.scatterplot(x=df_analysis[col1], y=df_analysis[col2])
            plt.title(f'{col1} vs {col2}')
            plt.show()

# 3. Multivariate Analysis
print("---- Multivariate Analysis (Correlation Heatmap) ----")
plt.figure(figsize=(10,8))
sns.heatmap(df_analysis.corr(), annot=True, cmap='coolwarm')
plt.title('Correlation Heatmap')
plt.show()

# 4. Column-wise Distribution
print("---- Column-wise Distribution ----")
for col in df_analysis.columns:
    counts = df_analysis[col].value_counts()
    print(f"\nDistribution for {col}:\n{counts.head(10)}")  # top 10 unique values

# ---------------- Outlier Analysis ----------------
print("---- Outlier Analysis ----")
for col in numerical_cols:
    Q1 = df_analysis[col].quantile(0.25)
    Q3 = df_analysis[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = df_analysis[(df_analysis[col] < lower_bound) | (df_analysis[col] > upper_bound)]
    print(f"{col} - Number of outliers: {outliers.shape[0]}")
    
    # Boxplot
    plt.figure(figsize=(6,4))
    sns.boxplot(x=df_analysis[col])
    plt.title(f'Boxplot for {col}')
    plt.show()

# ---------------- Noise Analysis ----------------
print("---- Noise Analysis ----")
# Define noise as points beyond 3 standard deviations
for col in numerical_cols:
    mean = df_analysis[col].mean()
    std = df_analysis[col].std()
    noise = df_analysis[(df_analysis[col] < mean - 3*std) | (df_analysis[col] > mean + 3*std)]
    print(f"{col} - Number of noisy points: {noise.shape[0]}")
    
    plt.figure(figsize=(6,4))
    sns.histplot(df_analysis[col], bins=30, kde=True)
    plt.axvline(mean - 3*std, color='r', linestyle='--', label='Lower Noise Threshold')
    plt.axvline(mean + 3*std, color='g', linestyle='--', label='Upper Noise Threshold')
    plt.title(f'Noise Detection for {col}')
    plt.legend()
    plt.show()
