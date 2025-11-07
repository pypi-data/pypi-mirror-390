import pandas as pd
import numpy as np

# Generate a big numerical dataset (10,000 rows)
big_data = pd.DataFrame({
    'Age': np.random.normal(20, 60, 1000),
    'Salary': np.random.normal(40000, 120000, 1000),
    'Experience': np.random.normal(0, 35, 1000),
    'Score': np.random.normal(50, 100, 1000)
})

# Save to CSV
big_data.to_csv('numerical_dataset_2.csv', index=False)

print("CSV file 'numerical_dataset_2.csv' created with 10,000 rows.")
