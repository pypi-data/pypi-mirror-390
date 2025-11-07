# import pandas as pd
# 
# # Load dataset
# df = pd.read_csv("students.csv")
# 
# # View the first few rows
# print(df.head())
# 
# # Basic info and summary
# print(df.info())
# print(df.describe())
# 
# df = pd.read_csv('employees.csv')
# print(df.head())       # first 5 rows
# print(df.tail(3))      # last 3 rows
# print(df.shape)        # (rows, columns)
# print(df.info())       # datatypes + missing values
# print(df.describe())   # stats for numeric columns



#Frequency of a Column
# print(df.columns)         # all column names
# print(df.dtypes)          # data types
# print(df.nunique())       # unique values count
# print(df['Gender'].value_counts())  # frequency of a column








# # Check for missing values
# # print(df.isnull().sum())
# #quick Visuals to check Missing Data
# sns.heatmap(df.isnull(), cbar=False, cmap='coolwarm')
# plt.title("Missing Values Heatmap")
# plt.show()


# DATA Clean


# import pandas as pd
# import numpy as np
# 
# data = {
#     "Name": [" Alice ", "Bob", "Charlie", "Alice "],
#     "Age": [25, np.nan, 30, 25],
#     "City": ["New York", "Paris", "Paris", "New York"]
# }
# 
# df = pd.DataFrame(data)
# 
# # 1. Remove whitespace from names
# df["Name"] = df["Name"].str.strip()
# 
# # 2. Fill missing age with mean
# df["Age"].fillna(df["Age"].mean(), inplace=True)
# 
# # 3. Drop duplicate rows
# df.drop_duplicates(inplace=True)
# 
# # 4. Replace a city name
# df["City"].replace("Paris", "FR-Paris", inplace=True)
# 
# print(df)


# rename and reorder
# df.rename(columns={'Emp ID': 'Employee_ID', 'Dept': 'Department'}, inplace=True)
# df = df[['Employee_ID', 'Name', 'Department', 'Salary']]

#remove dupicates
# before = df.shape[0]
# df.drop_duplicates(inplace=True)
# print(f"{before - df.shape[0]} duplicates removed.")

#Handling White space and Csing
# df['Name'] = df['Name'].str.strip().str.title()
# df['Department'] = df['Department'].str.lower()

# #replace and map
# df['Department'].replace({'hr': 'Human Resources', 'it': 'Information Tech'}, inplace=True)
# df['Gender'] = df['Gender'].map({'Male': 1, 'Female': 0})
#
# 
# Removing Unwanted Characters with Regex
# import re
# df['Name'] = df['Name'].apply(lambda x: re.sub('[^A-Za-z ]+', '', x))
# 
# Fixing Datatypes
# df['Salary'] = df['Salary'].astype(float)
# df['JoinDate'] = pd.to_datetime(df['JoinDate'])

#Creating Derived Features
# df['Experience'] = 2025 - df['JoinYear']
# df['Salary_per_Year'] = df['Salary'] / df['Experience']
# Combining Columns
# df['FullName'] = df['FirstName'] + ' ' + df['LastName']
# Discretization / Binning
# df['Age_Group'] = pd.cut(df['Age'], bins=[0, 18, 30, 50, 100],
#                          labels=['Teen', 'Young', 'Adult', 'Senior'])
# Mathematical Transformations - Log/sqrt helps reduce skewness and stabilize variance for ML algorithms.
# import numpy as np
# df['Log_Income'] = np.log(df['Income'] + 1)
# df['Income_Sqrt'] = np.sqrt(df['Income'])
# 
# Encoding Boolean Features
# df['Has_Bonus'] = df['Bonus'].notnull().astype(int)







# -------------------------------------------------------------------------
# import pandas as pd
# import numpy as np
# 
# df = pd.DataFrame({
#     "Height(cm)": [160, 170, 180, 190],
#     "Weight(kg)": [55, 65, 80, 90]
# })
# 
# # 1. Create BMI column
# df["BMI"] = df["Weight(kg)"] / ((df["Height(cm)"]/100) ** 2)
# 
# # 2. Log transformation to reduce skewness
# df["Log_Weight"] = np.log(df["Weight(kg)"])
# 
# # 3. Discretize BMI into categories
# df["BMI_Category"] = pd.cut(
#     df["BMI"],
#     bins=[0, 18.5, 25, 30, np.inf],
#     labels=["Underweight", "Normal", "Overweight", "Obese"]
# )
# 
# print(df)
# ----------------------------------------------------------------------
# from sklearn.preprocessing import MinMaxScaler
# import pandas as pd
# 
# df = pd.DataFrame({
#     'Age': [18, 22, 30, 40, 60],
#     'Income': [20000, 35000, 50000, 80000, 120000]
# })
# 
# scaler = MinMaxScaler()
# df_scaled = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)
# print(df_scaled)
# 
# #zscore
# from sklearn.preprocessing import StandardScaler
# 
# scaler = StandardScaler()
# df_standardized = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)
# print(df_standardized)
# 
# #robust-resistant to outliers
# from sklearn.preprocessing import RobustScaler
# 
# scaler = RobustScaler()
# df_robust = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)
# print(df_robust)
# 
# #Normalization - txt and sparse
# from sklearn.preprocessing import Normalizer
# import numpy as np
# 
# X = np.array([[3, 4], [1, 2], [2, 2]])
# 
# normalizer = Normalizer(norm='l2')
# print(normalizer.fit_transform(X))
# 
# #Label Encoding
# from sklearn.preprocessing import LabelEncoder
# import pandas as pd
# 
# df = pd.DataFrame({'City': ['Paris', 'London', 'New York', 'Paris']})
# encoder = LabelEncoder()
# df['City_Code'] = encoder.fit_transform(df['City'])
# print(df)
# 
# #ordinal Encoding
# from sklearn.preprocessing import OrdinalEncoder
# 
# data = [['Low'], ['Medium'], ['High'], ['Medium']]
# encoder = OrdinalEncoder(categories=[['Low', 'Medium', 'High']])
# encoded = encoder.fit_transform(data)
# print(encoded)
# 
# #binry - category coders
# !pip install category_encoders
# import category_encoders as ce
# import pandas as pd
# 
# df = pd.DataFrame({'City': ['Paris', 'London', 'New York', 'Berlin']})
# encoder = ce.BinaryEncoder(cols=['City'])
# df_encoded = encoder.fit_transform(df)
# print(df_encoded)
# 
# Frequency Encoding
# freq = df['City'].value_counts().to_dict()
# df['City_freq'] = df['City'].map(freq)
# 
# ----------------------------------------------------------------------
# #Missing Values handling:
# df['A'].fillna(df['A'].mean(), inplace=True)
# df['B'].fillna(df['B'].mode()[0], inplace=True)
# print(df)
# 
# # drop
# df = df.dropna()        # drop rows with NaN
# # df = df.dropna(axis=1) # drop columns with NaN
# 
# #impute:
# from sklearn.impute import SimpleImputer
# import numpy as np
# 
# data = [[1, 2], [np.nan, 3], [7, 6]]
# imputer = SimpleImputer(strategy='mean')
# print(imputer.fit_transform(data))
# 
# ___________________________________________________________________________________________
# 
# #Outlier Detection:
# import pandas as pd
# 
# df = pd.DataFrame({'Salary': [20, 22, 25, 28, 30, 120]})
# Q1 = df['Salary'].quantile(0.25)
# Q3 = df['Salary'].quantile(0.75)
# IQR = Q3 - Q1
# 
# lower = Q1 - 1.5 * IQR
# upper = Q3 + 1.5 * IQR
# 
# outliers = df[(df['Salary'] < lower) | (df['Salary'] > upper)]
# print(outliers)
# 
# #Replace extreme outliers with boundary values instead of removing them.
# df['Salary'] = df['Salary'].clip(lower, upper)
# print(df)
# 
# # Detecting Outliers via Z-Score]
# from scipy import stats
# import numpy as np
# 
# z = np.abs(stats.zscore(df['Salary']))
# df = df[z < 3]
# 
# --------------------------------------------------------------------------------------------------------------------------

# TEXT PREPROCESSING (NLP)
# import pandas as pd
# 
# data = {
#     'Review': [
#         "I LOVED this product! It’s amazing!!! 😍",
#         "Terrible quality... broke in 2 days.",
#         "Average, not great but okay.",
#         "Would buy again :)",
#         "Too costly & not worth it!!!"
#     ]
# }
# df = pd.DataFrame(data)
# print(df)
# 
#Lowercasing=> df['clean'] = df['Review'].str.lower()
#import string
# Remove Punctuation and Special Characters=> df['clean'] = df['clean'].str.replace(f"[{string.punctuation}]", "", regex=True)
# Remove Digits,etc import re
# df['clean'] = df['clean'].apply(lambda x: re.sub(r'[^a-zA-Z\s]', '', x))
# df['clean'] = df['clean'].str.replace('\s+', ' ', regex=True).str.strip()

#Tokrnization => "this product is good" → ["this", "product", "is", "good"].
# from nltk.tokenize import word_tokenize
# import nltk
# nltk.download('punkt')
# 
# df['tokens'] = df['clean'].apply(word_tokenize)

#Removes Stopwords => Removes common words like is, the, and, in which don’t add meaning.
# from nltk.corpus import stopwords
# nltk.download('stopwords')
# 
# stop_words = set(stopwords.words('english'))
# df['tokens'] = df['tokens'].apply(lambda x: [w for w in x if w not in stop_words])

#=======================================================================================
#DateTime Processing
#1) Converting to Datetime
# df = pd.DataFrame({'date': ['2023-01-15', '15-02-2024', '2025/03/01']})
# df['date'] = pd.to_datetime(df['date'], errors='coerce', dayfirst=True)

#2) Extracting Date Components
# df['year'] = df['date'].dt.year
# df['month'] = df['date'].dt.month
# df['day'] = df['date'].dt.day
# df['weekday'] = df['date'].dt.day_name()
# print(df)
#3) Time Differences
# df['next_date'] = df['date'] + pd.Timedelta(days=7)
# df['days_between'] = (df['next_date'] - df['date']).dt.days

#4) Resampling Time-Series
# date_rng = pd.date_range(start='2023-01-01', end='2023-01-10', freq='D')
# sales = [10, 12, 9, 14, 15, 16, 20, 18, 22, 25]
# df = pd.DataFrame({'date': date_rng, 'sales': sales})
# df.set_index('date', inplace=True)
# 
# # Convert daily data to weekly average
# weekly_sales = df.resample('W').mean()
# print(weekly_sales)

#5) Creating Temporal Features
# df['is_weekend'] = df['date'].dt.weekday >= 5
# df['quarter'] = df['date'].dt.quarter

#6_) SelectKBest (Chi-Squared)
# from sklearn.datasets import load_iris
# from sklearn.feature_selection import SelectKBest, chi2
# 
# X, y = load_iris(return_X_y=True)
# selector = SelectKBest(chi2, k=2)
# X_new = selector.fit_transform(X, y)
# print("Selected Features Shape:", X_new.shape)

#7) Variance TRhreshold - Removes features with zero or low variance (constant columns).

# from sklearn.feature_selection import VarianceThreshold
# import numpy as np
# 
# X = np.array([[1, 0, 2],
#               [1, 0, 3],
#               [1, 0, 4]])
# 
# selector = VarianceThreshold(threshold=0.0)
# X_new = selector.fit_transform(X)
# print(X_new)












