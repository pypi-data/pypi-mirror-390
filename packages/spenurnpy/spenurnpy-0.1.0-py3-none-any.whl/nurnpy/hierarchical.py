# HIERARCHICAL CLUSTERING COMPARISON SCRIPT

# (Agglomerative vs Divisive)

# ===========================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import AgglomerativeClustering, KMeans
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.preprocessing import StandardScaler
from tkinter import Tk, filedialog  # for file dialog

# -------------------------------------------

# 1️⃣ Load Dataset (any CSV file)

# -------------------------------------------

print("Select your dataset CSV file...")
Tk().withdraw()  # hide root window
file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
if not file_path:
    raise ValueError("No file selected!")

df = pd.read_csv(file_path)
print("\nDataset Loaded Successfully ✅\n")
print(df.head(), "\n")

# -------------------------------------------

# 2️⃣ Preprocessing — Select Numeric Columns

# -------------------------------------------

numeric_df = df.select_dtypes(include=[np.number])

if numeric_df.shape[1] < 2:
    raise ValueError("Dataset must contain at least 2 numeric columns for clustering.")

scaler = StandardScaler()
X = scaler.fit_transform(numeric_df)

print("Numeric columns used for clustering:", list(numeric_df.columns))

# -------------------------------------------

# 3️⃣ Agglomerative Clustering

# -------------------------------------------

agg_model = AgglomerativeClustering(n_clusters=3)
agg_labels = agg_model.fit_predict(X)

# For dendrogram (distance_threshold=0 disables pre-cut)

agg_full = AgglomerativeClustering(distance_threshold=0, n_clusters=None)
agg_full.fit(X)

# Function to plot dendrogram from model

def plot_dendrogram(model, **kwargs):
counts = np.zeros(model.children_.shape[0])
n_samples = len(model.labels_)
for i, merge in enumerate(model.children_):
current_count = 0
for child_idx in merge:
if child_idx < n_samples:
current_count += 1
else:
current_count += counts[child_idx - n_samples]
counts[i] = current_count
linkage_matrix = np.column_stack(
[model.children_, model.distances_, counts]).astype(float)
dendrogram(linkage_matrix, **kwargs)

# -------------------------------------------

# 4️⃣ Divisive Clustering (using recursive KMeans)

# -------------------------------------------

def divisive_clustering(data, max_clusters=3):
clusters = [data]
while len(clusters) < max_clusters:
cluster_to_split = max(clusters, key=lambda x: len(x))
clusters.remove(cluster_to_split)

```
    kmeans = KMeans(n_clusters=2, random_state=42).fit(cluster_to_split)
    c1 = cluster_to_split[kmeans.labels_ == 0]
    c2 = cluster_to_split[kmeans.labels_ == 1]

    clusters.extend([c1, c2])
return clusters
```

div_clusters = divisive_clustering(X, max_clusters=3)

# -------------------------------------------

# 5️⃣ Visualization — Comparison

# -------------------------------------------

plt.figure(figsize=(14, 6))

# (a) Agglomerative Scatter

plt.subplot(1, 2, 1)
plt.scatter(X[:, 0], X[:, 1], c=agg_labels, cmap='viridis', s=70)
plt.title("Agglomerative Clustering Result")
plt.xlabel("Feature 1")
plt.ylabel("Feature 2")

# (b) Divisive Scatter

plt.figure(figsize=(14, 6))
colors = ['r', 'g', 'b', 'c', 'm', 'y']
plt.subplot(1, 2, 1)
for i, cluster in enumerate(div_clusters):
plt.scatter(cluster[:, 0], cluster[:, 1], s=50,
c=colors[i], label=f'Cluster {i+1}')
plt.title('Divisive Clustering Result')
plt.legend()

# (c) Dendrogram (Agglomerative)

plt.subplot(1, 2, 2)
plot_dendrogram(agg_full, truncate_mode='level', p=5)
plt.title("Hierarchical Dendrogram (Agglomerative)")
plt.xlabel("Sample index")
plt.ylabel("Distance")

plt.tight_layout()
plt.show()
